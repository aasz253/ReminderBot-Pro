from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.orm import joinedload

from app.models.reminder import Reminder, Priority, NotificationChannel, RepeatType
from app.models.user import User
from app.models.notification import Notification, NotificationStatus
from app.services.subscription_service import SubscriptionService


class ReminderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    async def create_reminder(
        self,
        user: User,
        title: str,
        reminder_time: datetime,
        timezone: str = "UTC",
        description: Optional[str] = None,
        priority: str = "medium",
        category_id: Optional[UUID] = None,
        notification_type: str = "email",
        repeat_type: str = "none",
        repeat_interval: Optional[int] = None,
        repeat_end_date: Optional[datetime] = None,
        cron_expression: Optional[str] = None,
    ) -> Reminder:
        if not await self.subscription_service.check_reminder_quota(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reminder quota exceeded for your plan. Upgrade to create more reminders.",
            )

        is_recurring = repeat_type != "none"

        reminder = Reminder(
            user_id=user.id,
            title=title,
            description=description,
            reminder_time=reminder_time,
            timezone=timezone,
            priority=Priority(priority),
            category_id=category_id,
            notification_type=NotificationChannel(notification_type),
            repeat_type=RepeatType(repeat_type),
            repeat_interval=repeat_interval,
            repeat_end_date=repeat_end_date,
            cron_expression=cron_expression,
            is_recurring=is_recurring,
        )
        self.db.add(reminder)
        await self.db.flush()

        return reminder

    async def get_reminders(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[str] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort_by: str = "reminder_time",
        sort_order: str = "asc",
    ) -> Tuple[List[Reminder], int]:
        query = select(Reminder).where(Reminder.user_id == user_id)

        if is_active is not None:
            query = query.where(Reminder.is_active == is_active)
        if is_completed is not None:
            query = query.where(Reminder.is_completed == is_completed)
        if priority:
            query = query.where(Reminder.priority == Priority(priority))
        if category_id:
            query = query.where(Reminder.category_id == category_id)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Reminder.title.ilike(search_term),
                    Reminder.description.ilike(search_term),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        sort_column = getattr(Reminder, sort_by, Reminder.reminder_time)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        reminders = list(result.scalars().all())

        return reminders, total

    async def get_reminder_by_id(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        result = await self.db.execute(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
            )
        )
        reminder = result.scalar_one_or_none()
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found",
            )
        return reminder

    async def update_reminder(
        self, reminder_id: UUID, user_id: UUID, update_data: dict
    ) -> Reminder:
        reminder = await self.get_reminder_by_id(reminder_id, user_id)

        for key, value in update_data.items():
            if value is not None and hasattr(reminder, key):
                if key == "priority":
                    value = Priority(value)
                elif key == "notification_type":
                    value = NotificationChannel(value)
                elif key == "repeat_type":
                    value = RepeatType(value)
                setattr(reminder, key, value)

        reminder.is_recurring = reminder.repeat_type != RepeatType.NONE
        reminder.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        return reminder

    async def delete_reminder(self, reminder_id: UUID, user_id: UUID) -> None:
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        await self.db.delete(reminder)
        await self.db.flush()

    async def pause_reminder(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        reminder.is_paused = True
        reminder.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return reminder

    async def resume_reminder(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        reminder.is_paused = False
        reminder.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return reminder

    async def mark_complete(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        reminder.is_completed = True
        reminder.completed_at = datetime.now(timezone.utc)
        reminder.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return reminder

    async def parse_natural_language(self, query: str) -> dict:
        from app.services.ai_service import AIService

        ai_service = AIService()
        return await ai_service.parse_natural_language(query)

    async def bulk_action(
        self, reminder_ids: List[UUID], user_id: UUID, action: str
    ) -> int:
        count = 0
        for rid in reminder_ids:
            try:
                if action == "delete":
                    await self.delete_reminder(rid, user_id)
                elif action == "pause":
                    await self.pause_reminder(rid, user_id)
                elif action == "resume":
                    await self.resume_reminder(rid, user_id)
                elif action == "complete":
                    await self.mark_complete(rid, user_id)
                count += 1
            except HTTPException:
                continue
        return count

    async def get_upcoming_reminders(
        self, user_id: UUID, limit: int = 10
    ) -> List[Reminder]:
        now = datetime.now(timezone.utc)
        query = (
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.is_active == True,
                Reminder.is_paused == False,
                Reminder.is_completed == False,
                Reminder.reminder_time >= now,
            )
            .order_by(Reminder.reminder_time.asc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_daily_summary(self, user_id: UUID) -> dict:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        total_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.reminder_time >= start_of_day,
            Reminder.reminder_time <= end_of_day,
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        completed_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.reminder_time >= start_of_day,
            Reminder.reminder_time <= end_of_day,
            Reminder.is_completed == True,
        )
        completed_result = await self.db.execute(completed_query)
        completed = completed_result.scalar() or 0

        reminders_query = (
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.reminder_time >= start_of_day,
                Reminder.reminder_time <= end_of_day,
            )
            .order_by(Reminder.reminder_time.asc())
        )
        reminders_result = await self.db.execute(reminders_query)
        reminders = list(reminders_result.scalars().all())

        return {
            "date": start_of_day.date().isoformat(),
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "reminders": reminders,
        }

    async def get_active_count(self, user_id: UUID) -> int:
        query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.is_completed == False,
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
