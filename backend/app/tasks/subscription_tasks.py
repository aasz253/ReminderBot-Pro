import asyncio
import logging
from datetime import datetime, timezone, timedelta

from celery import current_task
from sqlalchemy import select, func

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.subscription import Subscription, SubscriptionStatus, PlanType
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


def get_session():
    return SessionLocal()


@celery_app.task
def check_expired_subscriptions():
    async def _check():
        async with get_session() as db:
            service = SubscriptionService(db)
            count = await service.handle_expired_subscriptions()
            logger.info(f"Handled {count} expired subscriptions")
            return count

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_check())


@celery_app.task
def renew_subscriptions():
    async def _renew():
        async with get_session() as db:
            now = datetime.now(timezone.utc)
            query = select(Subscription).where(
                Subscription.expires_at <= now + timedelta(days=1),
                Subscription.expires_at > now,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.auto_renew == True,
            )
            result = await db.execute(query)
            subscriptions = list(result.scalars().all())

            renewed = 0
            for sub in subscriptions:
                try:
                    sub.started_at = now
                    sub.expires_at = now + timedelta(days=30)
                    await db.flush()

                    log = ActivityLog(
                        user_id=sub.user_id,
                        action="subscription.renewed",
                        resource_type="subscription",
                        resource_id=str(sub.id),
                        details={"plan": sub.plan.value},
                    )
                    db.add(log)
                    renewed += 1
                except Exception as e:
                    logger.error(f"Failed to renew subscription {sub.id}: {e}")

            await db.flush()
            logger.info(f"Renewed {renewed} subscriptions")
            return renewed

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_renew())


@celery_app.task
def send_renewal_reminders():
    async def _send():
        async with get_session() as db:
            now = datetime.now(timezone.utc)
            query = select(Subscription).where(
                Subscription.expires_at <= now + timedelta(days=7),
                Subscription.expires_at > now,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.auto_renew == True,
            )
            result = await db.execute(query)
            subscriptions = list(result.scalars().all())

            reminded = 0
            for sub in subscriptions:
                try:
                    log = ActivityLog(
                        user_id=sub.user_id,
                        action="subscription.renewal_reminder",
                        resource_type="subscription",
                        resource_id=str(sub.id),
                        details={
                            "plan": sub.plan.value,
                            "expires_at": sub.expires_at.isoformat(),
                        },
                    )
                    db.add(log)
                    reminded += 1
                except Exception as e:
                    logger.error(f"Failed to send renewal reminder for {sub.id}: {e}")

            await db.flush()
            logger.info(f"Sent {reminded} renewal reminders")
            return reminded

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())
