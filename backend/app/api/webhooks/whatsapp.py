import json
import logging

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["Webhooks"])


@router.get("/webhook")
async def whatsapp_verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    verify_token = settings.WHATSAPP_API_TOKEN or "reminderbot_verify_token"

    if mode == "subscribe" and token == verify_token:
        logger.info("WhatsApp webhook verified")
        return int(challenge) if challenge else 200
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification failed",
        )


@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.debug(f"WhatsApp webhook received: {json.dumps(body)}")

    entries = body.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                from_number = message.get("from")
                msg_type = message.get("type")
                if msg_type == "text":
                    text = message.get("text", {}).get("body", "")
                    logger.info(f"WhatsApp message from {from_number}: {text}")

                    if text.lower() in ["hi", "hello", "start"]:
                        try:
                            async with __import__("httpx").AsyncClient() as client:
                                await client.post(
                                    f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
                                    headers={
                                        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                                        "Content-Type": "application/json",
                                    },
                                    json={
                                        "messaging_product": "whatsapp",
                                        "to": from_number,
                                        "type": "text",
                                        "text": {
                                            "body": "Welcome to ReminderBot! You will receive reminders here. Link your account from the web app."
                                        },
                                    },
                                )
                        except Exception as e:
                            logger.error(f"Failed to reply via WhatsApp: {e}")

    return {"status": "ok"}
