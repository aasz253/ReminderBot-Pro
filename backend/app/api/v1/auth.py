from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_rate_limiter
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh,
    ForgotPassword, ResetPassword, VerifyEmail, Enable2FAResponse,
    Verify2FA, Disable2FA, UserUpdate, OAuthLogin, ChangePassword,
)
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.rate_limiter import RateLimiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    if await rate_limiter.is_rate_limited(f"register:{data.email}", 5, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts",
        )
    auth_service = AuthService(db)
    user = await auth_service.register_user(
        email=data.email,
        password=data.password,
        username=data.username,
        full_name=data.full_name,
        phone=data.phone,
    )
    return await auth_service.create_tokens(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    if await rate_limiter.is_rate_limited(f"login:{data.email}", 10, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
        )
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        email=data.email,
        password=data.password,
        otp_token=data.otp_token,
    )
    return await auth_service.create_tokens(user)


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(data.refresh_token)


@router.post("/verify-email", response_model=dict)
async def verify_email(
    data: VerifyEmail,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.verify_email(data.token)
    return {"message": "Email verified successfully"}


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    data: ForgotPassword,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.forgot_password(data.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", response_model=dict)
async def reset_password(
    data: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.reset_password(data.token, data.new_password)
    return {"message": "Password reset successfully"}


@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    return await auth_service.enable_2fa(current_user)


@router.post("/2fa/verify", response_model=dict)
async def verify_2fa_setup(
    data: Verify2FA,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.verify_2fa_setup(current_user, data.token)
    return {"message": "2FA enabled successfully"}


@router.post("/2fa/disable", response_model=dict)
async def disable_2fa(
    data: Disable2FA,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.disable_2fa(current_user, data.password)
    return {"message": "2FA disabled successfully"}


@router.get("/oauth/{provider}")
async def oauth_authorize(provider: str):
    from app.core.config import settings

    if provider == "google":
        redirect_uri = f"{settings.BACKEND_URL}/api/v1/auth/oauth/google/callback"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=email%20profile"
        )
        return {"auth_url": auth_url}
    elif provider == "github":
        redirect_uri = f"{settings.BACKEND_URL}/api/v1/auth/oauth/github/callback"
        auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.GITHUB_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=user:email"
        )
        return {"auth_url": auth_url}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )


@router.post("/oauth/{provider}/callback", response_model=TokenResponse)
async def oauth_callback(
    provider: str,
    data: OAuthLogin,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    return await auth_service.oauth_login(provider, data.code, data.redirect_uri)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    return await auth_service.update_user(
        current_user, data.model_dump(exclude_unset=True)
    )


@router.post("/change-password", response_model=dict)
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import verify_password, get_password_hash

    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.flush()
    return {"message": "Password changed successfully"}
