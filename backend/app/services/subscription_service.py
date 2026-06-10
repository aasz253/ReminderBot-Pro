from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.models.user import User
from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.models.reminder import Reminder


PLAN_LIMITS = {
    PlanType.FREE: {
        "max_reminders": 5,
        "max_categories": 10,
        "max_teams": 0,
        "max_team_members": 0,
        "analytics_enabled": False,
        "ai_features": False,
        "priority_support": False,
        "api_access": False,
        "webhooks": False,
        "collaboration": False,
        "price_monthly": Decimal("0.00"),
        "price_yearly": Decimal("0.00"),
    },
    PlanType.PREMIUM: {
        "max_reminders": 100,
        "max_categories": 50,
        "max_teams": 3,
        "max_team_members": 10,
        "analytics_enabled": True,
        "ai_features": True,
        "priority_support": False,
        "api_access": True,
        "webhooks": True,
        "collaboration": True,
        "price_monthly": Decimal("9.99"),
        "price_yearly": Decimal("99.99"),
    },
    PlanType.BUSINESS: {
        "max_reminders": 10000,
        "max_categories": 200,
        "max_teams": 50,
        "max_team_members": 500,
        "analytics_enabled": True,
        "ai_features": True,
        "priority_support": True,
        "api_access": True,
        "webhooks": True,
        "collaboration": True,
        "price_monthly": Decimal("29.99"),
        "price_yearly": Decimal("299.99"),
    },
}


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def get_plan_details(self, plan: PlanType) -> dict:
        return PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.FREE])

    async def check_reminder_quota(self, user: User) -> bool:
        subscription = await self.get_user_subscription(user.id)
        plan = subscription.plan if subscription else PlanType.FREE
        limits = self.get_plan_details(plan)

        query = select(func.count()).where(
            Reminder.user_id == user.id,
            Reminder.is_active == True,
            Reminder.is_completed == False,
        )
        result = await self.db.execute(query)
        active_count = result.scalar() or 0

        return active_count < limits["max_reminders"]

    async def get_user_subscription(self, user_id: UUID) -> Optional[Subscription]:
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status.in_([
                    SubscriptionStatus.ACTIVE,
                    SubscriptionStatus.TRIAL,
                ]),
            ).order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def create_subscription(
        self,
        user: User,
        plan: PlanType,
        payment_provider: str,
        payment_reference: str,
    ) -> Subscription:
        existing = await self.get_user_subscription(user.id)
        if existing and existing.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has an active subscription",
            )

        now = datetime.now(timezone.utc)
        trial_days = 14 if plan == PlanType.PREMIUM else 7

        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            started_at=now,
            expires_at=now + timedelta(days=30),
            trial_ends_at=now + timedelta(days=trial_days),
            auto_renew=True,
            price=PLAN_LIMITS[plan]["price_monthly"],
        )

        if payment_provider == "stripe":
            subscription.stripe_subscription_id = payment_reference
        elif payment_provider == "paypal":
            subscription.paypal_agreement_id = payment_reference
        elif payment_provider == "mpesa":
            subscription.mpesa_reference = payment_reference
            subscription.status = SubscriptionStatus.TRIAL

        self.db.add(subscription)
        await self.db.flush()

        return subscription

    async def cancel_subscription(self, user_id: UUID) -> Subscription:
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )

        subscription.status = SubscriptionStatus.CANCELLED
        subscription.auto_renew = False
        await self.db.flush()

        return subscription

    async def upgrade_subscription(
        self,
        user_id: UUID,
        new_plan: PlanType,
        payment_provider: str,
        payment_reference: str,
    ) -> Subscription:
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return await self.create_subscription(
                await self.db.get(User, user_id),
                new_plan,
                payment_provider,
                payment_reference,
            )

        plan_order = {PlanType.FREE: 0, PlanType.PREMIUM: 1, PlanType.BUSINESS: 2}
        if plan_order.get(new_plan, 0) <= plan_order.get(subscription.plan, 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New plan must be higher tier than current plan",
            )

        subscription.plan = new_plan
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.stripe_subscription_id = payment_reference if payment_provider == "stripe" else subscription.stripe_subscription_id
        subscription.paypal_agreement_id = payment_reference if payment_provider == "paypal" else subscription.paypal_agreement_id
        subscription.mpesa_reference = payment_reference if payment_provider == "mpesa" else subscription.mpesa_reference
        subscription.price = PLAN_LIMITS[new_plan]["price_monthly"]
        subscription.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        await self.db.flush()

        return subscription

    async def renew_subscription(self, subscription: Subscription) -> Subscription:
        if not subscription.auto_renew:
            return subscription

        now = datetime.now(timezone.utc)
        subscription.started_at = now
        subscription.expires_at = now + timedelta(days=30)
        subscription.status = SubscriptionStatus.ACTIVE
        await self.db.flush()

        return subscription

    async def handle_expired_subscriptions(self) -> int:
        now = datetime.now(timezone.utc)
        query = select(Subscription).where(
            Subscription.expires_at <= now,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        result = await self.db.execute(query)
        expired = list(result.scalars().all())

        count = 0
        for sub in expired:
            if sub.auto_renew:
                await self.renew_subscription(sub)
            else:
                sub.status = SubscriptionStatus.EXPIRED
                count += 1
        await self.db.flush()
        return count

    async def get_feature_access(self, user_id: UUID, feature: str) -> bool:
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        limits = self.get_plan_details(subscription.plan)
        return limits.get(feature, False)
