import logging
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(
    jobstores={"default": MemoryJobStore()},
    executors={"default": AsyncIOExecutor()},
    job_defaults={
        "coalesce": True,
        "max_instances": 3,
        "misfire_grace_time": 300,
    },
    timezone="UTC",
)


def add_reminder_job(reminder_id: UUID, run_date: datetime, timezone_str: str = "UTC") -> Optional[str]:
    job_id = f"reminder_{reminder_id}"
    try:
        from app.tasks.reminder_tasks import process_reminder

        trigger = DateTrigger(run_date=run_date, timezone=timezone_str)
        scheduler.add_job(
            func=process_reminder,
            trigger=trigger,
            args=[str(reminder_id)],
            id=job_id,
            name=f"Reminder {reminder_id}",
            replace_existing=True,
        )
        logger.info(f"Scheduled reminder job {job_id} for {run_date}")
        return job_id
    except Exception as e:
        logger.error(f"Failed to schedule reminder job: {e}")
        return None


def add_recurring_job(reminder_id: UUID, cron_expression: str, timezone_str: str = "UTC") -> Optional[str]:
    job_id = f"recurring_reminder_{reminder_id}"
    try:
        from app.tasks.reminder_tasks import process_reminder

        trigger = CronTrigger.from_crontab(cron_expression, timezone=timezone_str)
        scheduler.add_job(
            func=process_reminder,
            trigger=trigger,
            args=[str(reminder_id)],
            id=job_id,
            name=f"Recurring Reminder {reminder_id}",
            replace_existing=True,
        )
        logger.info(f"Scheduled recurring job {job_id} with cron {cron_expression}")
        return job_id
    except Exception as e:
        logger.error(f"Failed to schedule recurring job: {e}")
        return None


def remove_job(job_id: str) -> bool:
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Removed job {job_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to remove job {job_id}: {e}")
        return False


def pause_job(job_id: str) -> bool:
    try:
        scheduler.pause_job(job_id)
        logger.info(f"Paused job {job_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to pause job {job_id}: {e}")
        return False


def resume_job(job_id: str) -> bool:
    try:
        scheduler.resume_job(job_id)
        logger.info(f"Resumed job {job_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to resume job {job_id}: {e}")
        return False


def get_jobs() -> List[dict]:
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return jobs


def init_scheduler():
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
