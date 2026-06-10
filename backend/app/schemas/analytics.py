from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class UserStats(BaseModel):
    total_reminders: int
    active_reminders: int
    completed_reminders: int
    missed_reminders: int
    paused_reminders: int
    upcoming_reminders: int
    completion_rate: float
    current_streak: int
    longest_streak: int


class ReminderTrend(BaseModel):
    date: str
    created: int
    completed: int
    missed: int


class ProductivityScore(BaseModel):
    overall_score: float
    completion_rate_score: float
    consistency_score: float
    timeliness_score: float
    streak_score: float
    total_reminders: int
    completed_reminders: int
    missed_reminders: int
    current_streak: int
    longest_streak: int
    score_breakdown: dict


class CategoryBreakdown(BaseModel):
    category_id: UUID
    category_name: str
    color: str
    total: int
    completed: int
    percentage: float


class TeamAnalytics(BaseModel):
    team_id: UUID
    team_name: str
    total_members: int
    total_reminders: int
    completed_reminders: int
    missed_reminders: int
    completion_rate: float
    member_productivity: List[dict]


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_subscriptions: int
    premium_subscriptions: int
    business_subscriptions: int
    total_revenue: float
    revenue_this_month: float
    total_reminders: int
    notification_delivery_rate: float
    registration_trend: List[dict]
    revenue_trend: List[dict]


class AnalyticsResponse(BaseModel):
    stats: UserStats
    trends: List[ReminderTrend]
    productivity: ProductivityScore
    category_breakdown: List[CategoryBreakdown]
