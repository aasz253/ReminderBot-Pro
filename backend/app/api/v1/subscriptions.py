from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, PlanType
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionUpgrade, PlanInfo, PlanLimits,
)
from app.services.subscription_service import SubscriptionService, PLAN_LIMITS

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=list[PlanInfo])
async def get_plans():
    plans = []
    for plan_type, limits in PLAN_LIMITS.items():
        plans.append(PlanInfo(
            name=plan_type.value.title(),
            code=plan_type.value,
            price_monthly=limits["price_monthly"],
            price_yearly=limits["price_yearly"],
            max_reminders=limits["max_reminders"],
            max_teams=limits["max_teams"],
            max_team_members=limits["max_team_members"],
            features=[
                f"Up to {limits['max_reminders']} reminders",
                "Analytics" if limits["analytics_enabled"] else "No analytics",
                "AI Features" if limits["ai_features"] else "No AI features",
                "API Access" if limits["api_access"] else "No API access",
                "Webhooks" if limits["webhooks"] else "No webhooks",
                "Collaboration" if limits["collaboration"] else "No collaboration",
                "Priority Support" if limits["priority_support"] else "Standard support",
            ],
        ))
    return plans


@router.get("/my", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.get_user_subscription(current_user.id)
    if not subscription:
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
            .order_by(Subscription.created_at.desc())
        )
        subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found",
        )
    return SubscriptionResponse.model_validate(subscription)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.create_subscription(
        user=current_user,
        plan=PlanType(data.plan),
        payment_provider=data.payment_provider,
        payment_reference=data.payment_reference,
    )
    return SubscriptionResponse.model_validate(subscription)


@router.post("/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    data: SubscriptionUpgrade,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.upgrade_subscription(
        user_id=current_user.id,
        new_plan=PlanType(data.plan),
        payment_provider=data.payment_provider,
        payment_reference=data.payment_reference,
    )
    return SubscriptionResponse.model_validate(subscription)


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.cancel_subscription(current_user.id)
    return SubscriptionResponse.model_validate(subscription)


@router.get("/limits", response_model=PlanLimits)
async def get_limits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.get_user_subscription(current_user.id)
    plan = subscription.plan if subscription else PlanType.FREE
    limits = service.get_plan_details(plan)
    return PlanLimits(
        max_reminders=limits["max_reminders"],
        max_categories=limits["max_categories"],
        max_teams=limits["max_teams"],
        max_team_members=limits["max_team_members"],
        analytics_enabled=limits["analytics_enabled"],
        ai_features=limits["ai_features"],
        priority_support=limits["priority_support"],
        api_access=limits["api_access"],
        webhooks=limits["webhooks"],
        collaboration=limits["collaboration"],
    )
