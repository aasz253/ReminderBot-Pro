from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "reminderbot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.reminder_tasks",
        "app.tasks.subscription_tasks",
        "app.tasks.analytics_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "check-expired-subscriptions": {
            "task": "app.tasks.subscription_tasks.check_expired_subscriptions",
            "schedule": 3600.0,
        },
        "retry-failed-notifications": {
            "task": "app.tasks.reminder_tasks.retry_failed_notifications",
            "schedule": 300.0,
        },
        "cleanup-expired-reminders": {
            "task": "app.tasks.reminder_tasks.cleanup_expired_reminders",
            "schedule": 86400.0,
        },
        "send-daily-summary": {
            "task": "app.tasks.reminder_tasks.send_daily_summary",
            "schedule": 86400.0,
        },
        "generate-daily-analytics": {
            "task": "app.tasks.analytics_tasks.generate_daily_analytics",
            "schedule": 86400.0,
        },
        "calculate-productivity-scores": {
            "task": "app.tasks.analytics_tasks.calculate_productivity_scores",
            "schedule": 3600.0,
        },
        "cleanup-old-logs": {
            "task": "app.tasks.analytics_tasks.cleanup_old_logs",
            "schedule": 86400.0,
        },
        "send-renewal-reminders": {
            "task": "app.tasks.subscription_tasks.send_renewal_reminders",
            "schedule": 43200.0,
        },
    },
)
