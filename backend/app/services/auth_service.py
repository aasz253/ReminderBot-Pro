import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import httpx
from jose import jwt
from authlib.integrations.base_client import OAuthError

from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp_secret,
    verify_otp,
    get_totp_uri,
    generate_qr_code_base64,
)
from app.models.user import User
from app.models.activity_log import ActivityLog


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(
        self, email: str, password: str, username: str, full_name: Optional[str] = None, phone: Optional[str] = None
    ) -> User:
        existing = await self.db.execute(
            select(User).where(or_(User.email == email, User.username == username))
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists",
            )

        verification_token = secrets.token_urlsafe(32)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            hashed_password=get_password_hash(password),
            email_verification_token=verification_token,
        )
        self.db.add(user)
        await self.db.flush()

        await self._log_activity(user.id, "user.register", "user", str(user.id))

        return user

    async def authenticate_user(self, email: str, password: str, otp_token: Optional[str] = None) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        if user.is_2fa_enabled:
            if not otp_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="OTP token required",
                    headers={"X-2FA-Required": "true"},
                )
            if not verify_otp(user.otp_secret, otp_token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid OTP token",
                )

        await self._log_activity(user.id, "user.login", "user", str(user.id))
        return user

    async def create_tokens(self, user: User) -> dict:
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        result = await self.db.execute(
            select(User).where(User.id == uid, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return await self.create_tokens(user)

    async def verify_email(self, token: str) -> User:
        result = await self.db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user.is_verified = True
        user.email_verification_token = None
        await self.db.flush()

        await self._log_activity(user.id, "user.verify_email", "user", str(user.id))
        return user

    async def forgot_password(self, email: str) -> None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return

        reset_token = secrets.token_urlsafe(32)
        user.reset_password_token = reset_token
        user.reset_password_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.db.flush()

        await self._log_activity(user.id, "user.forgot_password", "user", str(user.id))

    async def reset_password(self, token: str, new_password: str) -> User:
        result = await self.db.execute(
            select(User).where(
                User.reset_password_token == token,
                User.reset_password_token_expires > datetime.now(timezone.utc),
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user.hashed_password = get_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_token_expires = None
        await self.db.flush()

        await self._log_activity(user.id, "user.reset_password", "user", str(user.id))
        return user

    async def enable_2fa(self, user: User) -> dict:
        if user.is_2fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled",
            )

        secret = generate_otp_secret()
        user.otp_secret = secret
        await self.db.flush()

        uri = get_totp_uri(secret, user.email)
        qr_code = generate_qr_code_base64(uri)

        return {
            "secret": secret,
            "qr_code": qr_code,
            "uri": uri,
        }

    async def verify_2fa_setup(self, user: User, token: str) -> User:
        if not user.otp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA not initialized. Call enable_2fa first.",
            )

        if not verify_otp(user.otp_secret, token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP token",
            )

        user.is_2fa_enabled = True
        await self.db.flush()

        await self._log_activity(user.id, "user.enable_2fa", "user", str(user.id))
        return user

    async def disable_2fa(self, user: User, password: str) -> User:
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )

        user.is_2fa_enabled = False
        user.otp_secret = None
        await self.db.flush()

        await self._log_activity(user.id, "user.disable_2fa", "user", str(user.id))
        return user

    async def oauth_login(self, provider: str, code: str, redirect_uri: str) -> dict:
        if provider == "google":
            user_data = await self.get_google_user(code, redirect_uri)
        elif provider == "github":
            user_data = await self.get_github_user(code)
        elif provider == "telegram":
            user_data = await self.validate_telegram_login(code)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}",
            )

        email = user_data.get("email")
        provider_id = user_data.get("provider_id")
        name = user_data.get("name", "")
        avatar = user_data.get("avatar")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider",
            )

        filter_cond = User.email == email
        if provider == "google":
            filter_cond = or_(User.email == email, User.google_id == provider_id)
        elif provider == "github":
            filter_cond = or_(User.email == email, User.github_id == provider_id)

        result = await self.db.execute(select(User).where(filter_cond))
        user = result.scalar_one_or_none()

        if user:
            if provider == "google" and not user.google_id:
                user.google_id = provider_id
            if provider == "github" and not user.github_id:
                user.github_id = provider_id
            if avatar and not user.avatar_url:
                user.avatar_url = avatar
        else:
            username_base = email.split("@")[0]
            username = username_base
            counter = 1
            while True:
                existing = await self.db.execute(
                    select(User).where(User.username == username)
                )
                if not existing.scalar_one_or_none():
                    break
                username = f"{username_base}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=name,
                google_id=provider_id if provider == "google" else None,
                github_id=provider_id if provider == "github" else None,
                is_verified=True,
                avatar_url=avatar,
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            )
            self.db.add(user)
            await self.db.flush()

        return await self.create_tokens(user)

    async def get_google_user(self, code: str, redirect_uri: str) -> dict:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange Google OAuth code",
                )

            tokens = token_response.json()
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch Google user info",
                )

            user_info = user_response.json()
            return {
                "email": user_info.get("email"),
                "provider_id": user_info.get("id"),
                "name": user_info.get("name"),
                "avatar": user_info.get("picture"),
            }

    async def get_github_user(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange GitHub OAuth code",
                )

            tokens = token_response.json()
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "Accept": "application/json",
                },
            )
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch GitHub user info",
                )

            user_info = user_response.json()

            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "Accept": "application/json",
                },
            )
            primary_email = ""
            if email_response.status_code == 200:
                emails = email_response.json()
                for e in emails:
                    if e.get("primary"):
                        primary_email = e.get("email")
                        break
                if not primary_email and emails:
                    primary_email = emails[0].get("email", "")

            return {
                "email": primary_email or user_info.get("email"),
                "provider_id": str(user_info.get("id")),
                "name": user_info.get("name") or user_info.get("login"),
                "avatar": user_info.get("avatar_url"),
            }

    async def validate_telegram_login(self, data: str) -> dict:
        from urllib.parse import parse_qs

        parsed = parse_qs(data)
        auth_data = {k: v[0] for k, v in parsed.items()}

        if not settings.TELEGRAM_BOT_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram login not configured",
            )

        check_hash = auth_data.pop("hash", None)
        if not check_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Telegram login hash",
            )

        import hashlib
        import hmac

        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(auth_data.items())
        )
        computed_hash = hmac.new(
            secret_key, check_string.encode(), hashlib.sha256
        ).hexdigest()

        if computed_hash != check_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Telegram login data",
            )

        return {
            "email": f"{auth_data.get('id')}@telegram.user",
            "provider_id": auth_data.get("id"),
            "name": auth_data.get("first_name", ""),
            "avatar": auth_data.get("photo_url"),
        }

    async def update_user(self, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        await self._log_activity(user.id, "user.update", "user", str(user.id))
        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _log_activity(
        self, user_id: UUID, action: str, resource_type: str, resource_id: str
    ) -> None:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        self.db.add(log)
