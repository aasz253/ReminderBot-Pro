import json
import logging

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notification import Notification, NotificationStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/email", tags=["Webhooks"])


@router.post("/webhook")
async def email_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.debug(f"Email webhook received")

    events = body if isinstance(body, list) else [body]

    for event in events:
        event_type = event.get("event")
        email = event.get("email")
        sg_event_id = event.get("sg_event_id")
        sg_message_id = event.get("sg_message_id")
        timestamp = event.get("timestamp")

        if event_type == "delivered":
            result = await db.execute(
                __import__("sqlalchemy").select(Notification)
                .where(Notification.id.isnot(None))
                .order_by(Notification.created_at.desc())
                .limit(1)
            )
            notification = result.scalar_one_or_none()
            if notification:
                from datetime import datetime, timezone
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.now(timezone.utc)
                await db.flush()
            logger.info(f"Email delivered: {email}")

        elif event_type == "bounce":
            logger.warning(f"Email bounced: {email} - {event.get('reason', 'No reason')}")

        elif event_type == "open":
            logger.info(f"Email opened: {email}")

        elif event_type == "click":
            url = event.get("url", "")
            logger.info(f"Email link clicked: {email} - {url}")

        elif event_type == "dropped":
            reason = event.get("reason", "Unknown")
            logger.warning(f"Email dropped: {email} - {reason}")

        elif event_type == "spamreport":
            logger.warning(f"Spam report: {email}")

    return {"status": "ok"}
