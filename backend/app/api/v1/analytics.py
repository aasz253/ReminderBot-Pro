from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    UserStats, ReminderTrend, ProductivityScore, CategoryBreakdown,
    AnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    period: str = Query("weekly", regex=r"^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    stats = await service.get_user_stats(current_user.id)
    trends = await service.get_reminder_trends(current_user.id, period)
    productivity = await service.get_productivity_score(current_user.id)
    category_breakdown = await service.get_category_breakdown(current_user.id)

    return AnalyticsResponse(
        stats=UserStats(**stats),
        trends=[ReminderTrend(**t) for t in trends],
        productivity=ProductivityScore(**productivity),
        category_breakdown=[CategoryBreakdown(**c) for c in category_breakdown],
    )


@router.get("/stats", response_model=UserStats)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    stats = await service.get_user_stats(current_user.id)
    return UserStats(**stats)


@router.get("/trends", response_model=list[ReminderTrend])
async def get_trends(
    period: str = Query("weekly", regex=r"^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    trends = await service.get_reminder_trends(current_user.id, period)
    return [ReminderTrend(**t) for t in trends]


@router.get("/productivity", response_model=ProductivityScore)
async def get_productivity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    score = await service.get_productivity_score(current_user.id)
    return ProductivityScore(**score)


@router.get("/categories", response_model=list[CategoryBreakdown])
async def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    breakdown = await service.get_category_breakdown(current_user.id)
    return [CategoryBreakdown(**c) for c in breakdown]
