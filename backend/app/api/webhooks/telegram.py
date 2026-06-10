import json
import logging

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["Webhooks"])


@router.post("/webhook")
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot not configured",
        )

    body = await request.json()
    logger.debug(f"Telegram webhook received: {json.dumps(body)}")

    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id or not text:
        return {"ok": True}

    try:
        from telegram import Bot
        from telegram.constants import ParseMode

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        if text == "/start":
            args = text.split()
            if len(args) > 1:
                token = args[1]
                result = await db.execute(
                    select(User).where(User.email_verification_token == token)
                )
                user = result.scalar_one_or_none()
                if user:
                    user.telegram_id = str(chat_id)
                    await db.flush()
                    await bot.send_message(
                        chat_id=chat_id,
                        text="Welcome! Your Telegram is now linked to your ReminderBot account.",
                    )
                else:
                    await bot.send_message(
                        chat_id=chat_id,
                        text="Invalid token. Please try linking from the web app.",
                    )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "Welcome to ReminderBot! 🤖\n\n"
                        "I will send you reminders here.\n"
                        "Link your account from the web app to get started."
                    ),
                )
        elif text == "/help":
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "Available commands:\n"
                    "/start - Start the bot\n"
                    "/help - Show this help\n"
                    "/myreminders - List your reminders\n"
                    "/link - Get linking instructions"
                ),
            )
        elif text == "/myreminders":
            result = await db.execute(
                select(User).where(User.telegram_id == str(chat_id))
            )
            user = result.scalar_one_or_none()
            if user:
                from app.models.reminder import Reminder
                reminders_result = await db.execute(
                    select(Reminder).where(
                        Reminder.user_id == user.id,
                        Reminder.is_active == True,
                        Reminder.is_completed == False,
                    ).limit(5)
                )
                reminders = list(reminders_result.scalars().all())
                if reminders:
                    msg = "Your upcoming reminders:\n\n"
                    for r in reminders:
                        msg += f"• {r.title} - {r.reminder_time.strftime('%b %d, %I:%M %p')}\n"
                    await bot.send_message(chat_id=chat_id, text=msg)
                else:
                    await bot.send_message(chat_id=chat_id, text="No upcoming reminders.")
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Account not linked. Use /start from the web app.",
                )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text="I'll notify you when you have reminders set! Use /help for commands.",
            )

    except Exception as e:
        logger.error(f"Telegram webhook handler error: {e}")

    return {"ok": True}


@router.post("/set-webhook")
async def set_telegram_webhook():
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_BOT_WEBHOOK_URL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram webhook URL not configured",
        )

    try:
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        webhook_url = f"{settings.TELEGRAM_BOT_WEBHOOK_URL}/api/webhooks/telegram/webhook"
        await bot.set_webhook(url=webhook_url)
        return {"message": f"Webhook set to {webhook_url}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set webhook: {str(e)}",
        )
