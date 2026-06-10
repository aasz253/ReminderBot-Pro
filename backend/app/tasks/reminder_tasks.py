import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal

from celery import current_task
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.reminder import Reminder
from app.models.user import User
from app.models.notification import Notification, NotificationStatus
from app.services.notification_service import NotificationService
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


def get_session():
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_reminder(self, reminder_id: str):
    from uuid import UUID
    rid = UUID(reminder_id)

    async def _process():
        async with get_session() as db:
            result = await db.execute(
                select(Reminder).where(Reminder.id == rid)
            )
            reminder = result.scalar_one_or_none()
            if not reminder:
                logger.error(f"Reminder {reminder_id} not found")
                return

            if not reminder.is_active or reminder.is_paused or reminder.is_completed:
                logger.info(f"Reminder {reminder_id} is not active, skipping")
                return

            result = await db.execute(
                select(User).where(User.id == reminder.user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"User {reminder.user_id} not found")
                return

            notification_service = NotificationService(db)
            await notification_service.send_notification(user, reminder)

            if reminder.is_recurring:
                from app.utils.date_utils import calculate_repeat_dates
                next_dates = calculate_repeat_dates(
                    reminder.reminder_time,
                    reminder.repeat_type.value,
                    reminder.repeat_interval or 1,
                    reminder.repeat_end_date,
                )
                if next_dates and len(next_dates) > 0:
                    reminder.reminder_time = next_dates[0]
                else:
                    reminder.is_completed = True
                    reminder.completed_at = datetime.now(timezone.utc)
            else:
                reminder.is_completed = True
                reminder.completed_at = datetime.now(timezone.utc)

            await db.flush()
            logger.info(f"Reminder {reminder_id} processed successfully")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_process())
        else:
            loop.run_until_complete(_process())
    except Exception as e:
        logger.error(f"Failed to process reminder {reminder_id}: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def send_notification_task(self, notification_id: str):
    from uuid import UUID
    nid = UUID(notification_id)

    async def _send():
        async with get_session() as db:
            result = await db.execute(
                select(Notification).where(Notification.id == nid)
            )
            notification = result.scalar_one_or_none()
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return

            reminder_result = await db.execute(
                select(Reminder).where(Reminder.id == notification.reminder_id)
            )
            reminder = reminder_result.scalar_one_or_none()
            user_result = await db.execute(
                select(User).where(User.id == notification.user_id)
            )
            user = user_result.scalar_one_or_none()

            if not reminder or not user:
                logger.error(f"Reminder or user not found for notification {notification_id}")
                return

            service = NotificationService(db)
            channel = notification.channel
            try:
                if channel == "telegram":
                    await service.send_telegram_notification(user, reminder, notification)
                elif channel == "whatsapp":
                    await service.send_whatsapp_notification(user, reminder, notification)
                elif channel == "email":
                    await service.send_email_notification(user, reminder, notification)
                elif channel == "sms":
                    await service.send_sms_notification(user, reminder, notification)
                elif channel == "push":
                    await service.send_push_notification(user, reminder, notification)

                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(timezone.utc)
                await db.flush()
                logger.info(f"Notification {notification_id} sent via {channel}")

            except Exception as e:
                notification.status = NotificationStatus.FAILED
                notification.error_message = str(e)
                notification.retry_count += 1
                await db.flush()
                logger.error(f"Failed to send notification {notification_id}: {e}")
                if notification.retry_count < 3:
                    raise self.retry(exc=e)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_send())
        else:
            loop.run_until_complete(_send())
    except Exception as e:
        logger.error(f"send_notification_task failed: {e}")
        raise self.retry(exc=e)


@celery_app.task
def retry_failed_notifications():
    async def _retry():
        async with get_session() as db:
            service = NotificationService(db)
            count = await service.process_failed_notifications()
            logger.info(f"Retried {count} failed notifications")
            return count

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_retry())


@celery_app.task
def cleanup_expired_reminders():
    async def _cleanup():
        async with get_session() as db:
            thirty_days_ago = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            from sqlalchemy import delete
            stmt = delete(Reminder).where(
                Reminder.is_completed == True,
                Reminder.completed_at <= thirty_days_ago,
            )
            result = await db.execute(stmt)
            await db.flush()
            logger.info(f"Cleaned up {result.rowcount} expired reminders")
            return result.rowcount

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_cleanup())


@celery_app.task
def send_daily_summary():
    async def _send():
        async with get_session() as db:
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = list(result.scalars().all())
            count = 0
            for user in users:
                try:
                    service = ReminderService(db)
                    summary = await service.get_daily_summary(user.id)
                    if summary["total"] > 0:
                        notification_service = NotificationService(db)
                        from app.models.activity_log import ActivityLog
                        log = ActivityLog(
                            user_id=user.id,
                            action="daily_summary",
                            resource_type="reminder",
                            details={
                                "total": summary["total"],
                                "completed": summary["completed"],
                                "pending": summary["pending"],
                            },
                        )
                        db.add(log)
                        count += 1
                except Exception as e:
                    logger.error(f"Failed to send daily summary to {user.id}: {e}")
            await db.flush()
            logger.info(f"Sent daily summary to {count} users")
            return count

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())
