import smtplib
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from jinja2 import Template

from app.core.config import settings
from app.models.user import User
from app.models.reminder import Reminder
from app.models.notification import Notification, NotificationStatus
from app.services.content_generator import ContentGenerator

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.content_generator = ContentGenerator()

    async def send_notification(
        self, user: User, reminder: Reminder, channels: Optional[List[str]] = None
    ) -> List[Notification]:
        if channels is None:
            if reminder.notification_type.value == "all":
                channels = ["email", "telegram", "whatsapp", "sms", "push"]
            else:
                channels = [reminder.notification_type.value]

        notifications = []
        for channel in channels:
            notification = Notification(
                reminder_id=reminder.id,
                user_id=user.id,
                channel=channel,
                status=NotificationStatus.PENDING,
            )
            self.db.add(notification)
            notifications.append(notification)

        await self.db.flush()

        for notification in notifications:
            try:
                if notification.channel == "telegram":
                    await self.send_telegram_notification(user, reminder, notification)
                elif notification.channel == "whatsapp":
                    await self.send_whatsapp_notification(user, reminder, notification)
                elif notification.channel == "email":
                    await self.send_email_notification(user, reminder, notification)
                elif notification.channel == "sms":
                    await self.send_sms_notification(user, reminder, notification)
                elif notification.channel == "push":
                    await self.send_push_notification(user, reminder, notification)

                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(timezone.utc)

            except Exception as e:
                notification.status = NotificationStatus.FAILED
                notification.error_message = str(e)
                logger.error(f"Failed to send {notification.channel} notification: {e}")

        await self.db.flush()
        return notifications

    async def send_telegram_notification(
        self, user: User, reminder: Reminder, notification: Notification
    ) -> None:
        if not settings.TELEGRAM_BOT_TOKEN or not user.telegram_id:
            raise ValueError("Telegram not configured or user has no Telegram ID")

        try:
            from telegram import Bot
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

            message = (
                f"⏰ *Reminder: {reminder.title}*\n\n"
                f"{reminder.description or ''}\n\n"
                f"Priority: {reminder.priority.value}\n"
                f"Time: {reminder.reminder_time.strftime('%Y-%m-%d %H:%M %Z')}"
            )

            await bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode="Markdown",
            )

        except Exception as e:
            raise RuntimeError(f"Telegram send failed: {str(e)}")

    async def send_whatsapp_notification(
        self, user: User, reminder: Reminder, notification: Notification
    ) -> None:
        if not settings.WHATSAPP_API_TOKEN or not user.phone:
            raise ValueError("WhatsApp not configured or user has no phone")

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
                    headers={
                        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "messaging_product": "whatsapp",
                        "to": user.phone,
                        "type": "template",
                        "template": {
                            "name": "reminder_notification",
                            "language": {"code": "en"},
                            "components": [{
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "text": reminder.title},
                                    {"type": "text", "text": reminder.reminder_time.strftime("%Y-%m-%d %H:%M")},
                                ],
                            }],
                        },
                    },
                )
                if response.status_code != 200:
                    raise RuntimeError(f"WhatsApp API error: {response.text}")

        except Exception as e:
            raise RuntimeError(f"WhatsApp send failed: {str(e)}")

    async def send_email_notification(
        self, user: User, reminder: Reminder, notification: Notification
    ) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            raise ValueError("SMTP not configured")

        html_content = self.content_generator.reminder_notification_email(reminder)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Reminder: {reminder.title}"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = user.email

        text_part = MIMEText(
            f"Reminder: {reminder.title}\n\n{reminder.description or ''}\n\nTime: {reminder.reminder_time}",
            "plain",
        )
        html_part = MIMEText(html_content, "html")
        msg.attach(text_part)
        msg.attach(html_part)

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            raise RuntimeError(f"Email send failed: {str(e)}")

    async def send_sms_notification(
        self, user: User, reminder: Reminder, notification: Notification
    ) -> None:
        if not settings.AFRICAS_TALKING_API_KEY or not user.phone:
            raise ValueError("SMS not configured or user has no phone")

        try:
            import africastalking
            africastalking.initialize(
                username=settings.AFRICAS_TALKING_USERNAME or "sandbox",
                api_key=settings.AFRICAS_TALKING_API_KEY,
            )
            sms = africastalking.SMS

            message = (
                f"ReminderBot: {reminder.title} - "
                f"{reminder.reminder_time.strftime('%Y-%m-%d %H:%M')}"
            )

            response = sms.send(message, [user.phone])
            if isinstance(response, dict) and response.get("SMSMessageData", {}).get("Message") == "Sent":
                pass
            else:
                logger.warning(f"SMS response: {response}")

        except Exception as e:
            raise RuntimeError(f"SMS send failed: {str(e)}")

    async def send_push_notification(
        self, user: User, reminder: Reminder, notification: Notification
    ) -> None:
        if not settings.VAPID_PRIVATE_KEY:
            raise ValueError("Web Push not configured")

        try:
            from pywebpush import webpush, WebPushException

            payload = {
                "title": reminder.title,
                "body": reminder.description or f"Priority: {reminder.priority.value}",
                "icon": "/static/icon.png",
                "badge": "/static/badge.png",
                "data": {
                    "reminder_id": str(reminder.id),
                    "url": f"{settings.FRONTEND_URL}/reminders/{reminder.id}",
                },
            }

            import json
            # In production, you'd store push subscriptions per user
            # This is a simplified version
            logger.info(f"Push notification payload: {json.dumps(payload)}")

        except Exception as e:
            raise RuntimeError(f"Push notification failed: {str(e)}")

    async def process_failed_notifications(self, max_retries: int = 3) -> int:
        query = select(Notification).where(
            Notification.status == NotificationStatus.FAILED,
            Notification.retry_count < max_retries,
        )
        result = await self.db.execute(query)
        failed = list(result.scalars().all())

        retried = 0
        for notification in failed:
            try:
                notification.retry_count += 1
                reminder_result = await self.db.execute(
                    select(Reminder).where(Reminder.id == notification.reminder_id)
                )
                reminder = reminder_result.scalar_one_or_none()
                user_result = await self.db.execute(
                    select(User).where(User.id == notification.user_id)
                )
                user = user_result.scalar_one_or_none()

                if not reminder or not user:
                    continue

                if notification.channel == "telegram":
                    await self.send_telegram_notification(user, reminder, notification)
                elif notification.channel == "email":
                    await self.send_email_notification(user, reminder, notification)

                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(timezone.utc)
                notification.error_message = None
                retried += 1

            except Exception as e:
                notification.error_message = str(e)
                logger.error(f"Retry failed for notification {notification.id}: {e}")

        await self.db.flush()
        return retried

    async def get_notification_history(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        status_filter: Optional[str] = None,
    ) -> Tuple[List[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count()).where(Notification.user_id == user_id)

        if status_filter:
            query = query.where(Notification.status == NotificationStatus(status_filter))
            count_query = count_query.where(Notification.status == NotificationStatus(status_filter))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total
