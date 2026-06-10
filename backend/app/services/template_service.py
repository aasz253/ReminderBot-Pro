import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.reminder import Reminder, Priority, NotificationChannel, RepeatType


class ReminderTemplate:
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        title: str = "",
        description: Optional[str] = None,
        priority: str = "medium",
        notification_type: str = "email",
        repeat_type: str = "none",
        repeat_interval: Optional[int] = None,
        category: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        is_public: bool = True,
        usage_count: int = 0,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or uuid.uuid4()
        self.title = title
        self.description = description
        self.priority = priority
        self.notification_type = notification_type
        self.repeat_type = repeat_type
        self.repeat_interval = repeat_interval
        self.category = category
        self.user_id = user_id
        self.is_public = is_public
        self.usage_count = usage_count
        self.created_at = created_at or datetime.now(timezone.utc)


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._templates: dict[uuid.UUID, ReminderTemplate] = {}
        self._init_default_templates()

    def _init_default_templates(self) -> None:
        defaults = [
            ReminderTemplate(
                title="Morning Standup",
                description="Daily team standup meeting reminder",
                priority="high",
                notification_type="telegram",
                repeat_type="daily",
                category="work",
                is_public=True,
            ),
            ReminderTemplate(
                title="Drink Water",
                description="Stay hydrated! Drink a glass of water.",
                priority="low",
                notification_type="push",
                repeat_type="hourly",
                repeat_interval=2,
                category="health",
                is_public=True,
            ),
            ReminderTemplate(
                title="Take Medication",
                description="Time to take your medication",
                priority="high",
                notification_type="all",
                repeat_type="daily",
                category="health",
                is_public=True,
            ),
            ReminderTemplate(
                title="Pay Bills",
                description="Monthly bill payment reminder",
                priority="urgent",
                notification_type="email",
                repeat_type="monthly",
                category="finance",
                is_public=True,
            ),
            ReminderTemplate(
                title="Weekly Review",
                description="Review weekly goals and accomplishments",
                priority="medium",
                notification_type="email",
                repeat_type="weekly",
                category="work",
                is_public=True,
            ),
            ReminderTemplate(
                title="Exercise",
                description="Time for your workout session",
                priority="medium",
                notification_type="push",
                repeat_type="daily",
                category="health",
                is_public=True,
            ),
            ReminderTemplate(
                title="Read Books",
                description="Daily reading session for personal development",
                priority="low",
                notification_type="push",
                repeat_type="daily",
                category="personal",
                is_public=True,
            ),
            ReminderTemplate(
                title="Birthday Reminder",
                description="Don't forget to wish them a happy birthday!",
                priority="medium",
                notification_type="email",
                repeat_type="yearly",
                category="social",
                is_public=True,
            ),
            ReminderTemplate(
                title="Study Session",
                description="Focused study time",
                priority="high",
                notification_type="all",
                repeat_type="daily",
                category="study",
                is_public=True,
            ),
            ReminderTemplate(
                title="Meditation",
                description="Take 10 minutes to meditate and relax",
                priority="low",
                notification_type="push",
                repeat_type="daily",
                category="personal",
                is_public=True,
            ),
        ]

        for tpl in defaults:
            self._templates[tpl.id] = tpl

    def create_template(self, user_id: UUID, reminder: Reminder, is_public: bool = False) -> ReminderTemplate:
        tpl = ReminderTemplate(
            title=reminder.title,
            description=reminder.description,
            priority=reminder.priority.value,
            notification_type=reminder.notification_type.value,
            repeat_type=reminder.repeat_type.value,
            repeat_interval=reminder.repeat_interval,
            user_id=user_id,
            is_public=is_public,
        )
        self._templates[tpl.id] = tpl
        return tpl

    def get_templates(
        self, skip: int = 0, limit: int = 50, search: Optional[str] = None, category: Optional[str] = None
    ) -> Tuple[List[ReminderTemplate], int]:
        templates = list(self._templates.values())
        public_templates = [t for t in templates if t.is_public]

        if search:
            search_lower = search.lower()
            public_templates = [
                t for t in public_templates
                if search_lower in t.title.lower()
                or (t.description and search_lower in t.description.lower())
            ]

        if category:
            public_templates = [
                t for t in public_templates
                if t.category and t.category.lower() == category.lower()
            ]

        total = len(public_templates)
        paginated = public_templates[skip:skip + limit]

        return paginated, total

    def get_template_by_id(self, template_id: UUID) -> ReminderTemplate:
        tpl = self._templates.get(uuid.UUID(str(template_id)))
        if not tpl or not tpl.is_public:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        return tpl

    async def use_template(
        self, template_id: UUID, user_id: UUID, reminder_time: datetime, timezone: str = "UTC"
    ) -> Reminder:
        tpl = self.get_template_by_id(template_id)

        reminder = Reminder(
            user_id=user_id,
            title=tpl.title,
            description=tpl.description,
            reminder_time=reminder_time,
            timezone=timezone,
            priority=Priority(tpl.priority),
            notification_type=NotificationChannel(tpl.notification_type),
            repeat_type=RepeatType(tpl.repeat_type if tpl.repeat_type != "hourly" else "custom"),
            repeat_interval=tpl.repeat_interval,
        )
        self.db.add(reminder)
        await self.db.flush()

        tpl.usage_count += 1
        return reminder

    def search_templates(self, query: str) -> List[ReminderTemplate]:
        query_lower = query.lower()
        results = []
        for tpl in self._templates.values():
            if not tpl.is_public:
                continue
            if query_lower in tpl.title.lower() or query_lower in (tpl.description or "").lower():
                results.append(tpl)
        return results
