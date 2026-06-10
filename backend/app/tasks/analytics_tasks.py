import asyncio
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, delete

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.reminder import Reminder
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


def get_session():
    return SessionLocal()


@celery_app.task
def generate_daily_analytics():
    async def _generate():
        async with get_session() as db:
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = list(result.scalars().all())

            service = AnalyticsService(db)
            generated = 0
            for user in users:
                try:
                    stats = await service.get_user_stats(user.id)
                    productivity = await service.get_productivity_score(user.id)

                    log = ActivityLog(
                        user_id=user.id,
                        action="analytics.daily",
                        resource_type="analytics",
                        details={
                            "stats": stats,
                            "productivity": productivity,
                        },
                    )
                    db.add(log)
                    generated += 1
                except Exception as e:
                    logger.error(f"Failed to generate analytics for user {user.id}: {e}")

            await db.flush()
            logger.info(f"Generated daily analytics for {generated} users")
            return generated

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_generate())


@celery_app.task
def calculate_productivity_scores():
    async def _calculate():
        async with get_session() as db:
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = list(result.scalars().all())

            service = AnalyticsService(db)
            calculated = 0
            for user in users:
                try:
                    score = await service.get_productivity_score(user.id)
                    log = ActivityLog(
                        user_id=user.id,
                        action="productivity.score",
                        resource_type="analytics",
                        details={"score": score},
                    )
                    db.add(log)
                    calculated += 1
                except Exception as e:
                    logger.error(f"Failed to calculate productivity for user {user.id}: {e}")

            await db.flush()
            logger.info(f"Calculated productivity scores for {calculated} users")
            return calculated

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_calculate())


@celery_app.task
def cleanup_old_logs():
    async def _cleanup():
        async with get_session() as db:
            ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)

            stmt = delete(ActivityLog).where(
                ActivityLog.created_at < ninety_days_ago
            )
            result = await db.execute(stmt)
            await db.flush()
            logger.info(f"Cleaned up {result.rowcount} old activity logs")
            return result.rowcount

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_cleanup())
