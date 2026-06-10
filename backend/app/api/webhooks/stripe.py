import json
import logging

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.models.subscription import Subscription, PlanType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stripe", tags=["Webhooks"])


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook not configured",
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        payment_intent_id = data.get("id")
        payment = Payment(
            amount=0,
            currency=data.get("currency", "usd").upper(),
            provider=PaymentProvider.STRIPE,
            provider_reference=payment_intent_id,
            status=PaymentStatus.COMPLETED,
        )
        db.add(payment)
        await db.flush()
        logger.info(f"Stripe payment succeeded: {payment_intent_id}")

    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = data.get("id")
        logger.warning(f"Stripe payment failed: {payment_intent_id}")

    elif event_type == "invoice.paid":
        subscription_id = data.get("subscription")
        if subscription_id:
            result = await db.execute(
                __import__("sqlalchemy").select(Subscription)
                .where(Subscription.stripe_subscription_id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                from datetime import datetime, timezone, timedelta
                subscription.status = "active"
                subscription.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
                await db.flush()

    elif event_type == "customer.subscription.deleted":
        subscription_id = data.get("id")
        result = await db.execute(
            __import__("sqlalchemy").select(Subscription)
            .where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.status = "cancelled"
            subscription.auto_renew = False
            await db.flush()

    return {"status": "ok"}
