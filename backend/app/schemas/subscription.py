from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class PlanInfo(BaseModel):
    name: str
    code: str
    price_monthly: Decimal
    price_yearly: Decimal
    max_reminders: int
    max_teams: int
    max_team_members: int
    features: list[str]


class SubscriptionCreate(BaseModel):
    plan: str = Field(..., pattern=r"^(free|premium|business)$")
    payment_provider: str = Field(..., pattern=r"^(stripe|paypal|mpesa)$")
    payment_reference: str


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    status: str
    stripe_subscription_id: Optional[str]
    paypal_agreement_id: Optional[str]
    mpesa_reference: Optional[str]
    started_at: Optional[datetime]
    expires_at: Optional[datetime]
    trial_ends_at: Optional[datetime]
    auto_renew: bool
    price: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpgrade(BaseModel):
    plan: str = Field(..., pattern=r"^(premium|business)$")
    payment_provider: str = Field(..., pattern=r"^(stripe|paypal|mpesa)$")
    payment_reference: str


class PlanLimits(BaseModel):
    max_reminders: int = 5
    max_categories: int = 10
    max_teams: int = 0
    max_team_members: int = 0
    analytics_enabled: bool = False
    ai_features: bool = False
    priority_support: bool = False
    api_access: bool = False
    webhooks: bool = False
    collaboration: bool = False
