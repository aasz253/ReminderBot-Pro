from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.reminder import (
    ReminderCreate, ReminderUpdate, ReminderResponse, ReminderListResponse,
    NaturalLanguageReminder, ParsedReminderResponse, ReminderBulkAction,
    DailySummary,
)
from app.models.user import User
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    is_completed: Optional[bool] = None,
    priority: Optional[str] = None,
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: str = Query("reminder_time", regex=r"^(reminder_time|created_at|priority|title)$"),
    sort_order: str = Query("asc", regex=r"^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminders, total = await service.get_reminders(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_active=is_active,
        is_completed=is_completed,
        priority=priority,
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ReminderListResponse(
        items=[ReminderResponse.model_validate(r) for r in reminders],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.create_reminder(
        user=current_user,
        title=data.title,
        reminder_time=data.reminder_time,
        timezone=data.timezone,
        description=data.description,
        priority=data.priority,
        category_id=data.category_id,
        notification_type=data.notification_type,
        repeat_type=data.repeat_type,
        repeat_interval=data.repeat_interval,
        repeat_end_date=data.repeat_end_date,
        cron_expression=data.cron_expression,
    )
    return ReminderResponse.model_validate(reminder)


@router.get("/upcoming", response_model=list[ReminderResponse])
async def get_upcoming(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminders = await service.get_upcoming_reminders(current_user.id, limit)
    return [ReminderResponse.model_validate(r) for r in reminders]


@router.get("/daily-summary", response_model=DailySummary)
async def daily_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    result = await service.get_daily_summary(current_user.id)
    result["reminders"] = [ReminderResponse.model_validate(r) for r in result["reminders"]]
    return DailySummary(**result)


@router.post("/parse", response_model=ParsedReminderResponse)
async def parse_natural_language(
    data: NaturalLanguageReminder,
    current_user: User = Depends(get_current_user),
):
    service = ReminderService(None)
    result = await service.parse_natural_language(data.query)
    return ParsedReminderResponse(**result)


@router.post("/bulk-action", response_model=dict)
async def bulk_action(
    data: ReminderBulkAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    count = await service.bulk_action(data.reminder_ids, current_user.id, data.action)
    return {"message": f"{count} reminders {data.action}d successfully", "count": count}


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.get_reminder_by_id(reminder_id, current_user.id)
    return ReminderResponse.model_validate(reminder)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.update_reminder(
        reminder_id, current_user.id, data.model_dump(exclude_unset=True)
    )
    return ReminderResponse.model_validate(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    await service.delete_reminder(reminder_id, current_user.id)


@router.post("/{reminder_id}/pause", response_model=ReminderResponse)
async def pause_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.pause_reminder(reminder_id, current_user.id)
    return ReminderResponse.model_validate(reminder)


@router.post("/{reminder_id}/resume", response_model=ReminderResponse)
async def resume_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.resume_reminder(reminder_id, current_user.id)
    return ReminderResponse.model_validate(reminder)


@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReminderService(db)
    reminder = await service.mark_complete(reminder_id, current_user.id)
    return ReminderResponse.model_validate(reminder)
