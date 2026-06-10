from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    reminder_time: datetime
    timezone: str = "UTC"
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|urgent)$")
    category_id: Optional[UUID] = None
    notification_type: str = Field(default="email", pattern=r"^(telegram|whatsapp|email|sms|push|all)$")
    repeat_type: str = Field(default="none", pattern=r"^(none|daily|weekly|monthly|yearly|custom)$")
    repeat_interval: Optional[int] = Field(None, ge=1)
    repeat_end_date: Optional[datetime] = None
    cron_expression: Optional[str] = None

    @field_validator("reminder_time")
    @classmethod
    def validate_reminder_time(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("reminder_time must be timezone-aware")
        return v


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    reminder_time: Optional[datetime] = None
    timezone: Optional[str] = None
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    category_id: Optional[UUID] = None
    notification_type: Optional[str] = Field(None, pattern=r"^(telegram|whatsapp|email|sms|push|all)$")
    repeat_type: Optional[str] = Field(None, pattern=r"^(none|daily|weekly|monthly|yearly|custom)$")
    repeat_interval: Optional[int] = Field(None, ge=1)
    repeat_end_date: Optional[datetime] = None
    cron_expression: Optional[str] = None


class ReminderResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    reminder_time: datetime
    timezone: str
    priority: str
    category_id: Optional[UUID]
    notification_type: str
    repeat_type: str
    repeat_interval: Optional[int]
    repeat_end_date: Optional[datetime]
    cron_expression: Optional[str]
    is_recurring: bool
    is_active: bool
    is_paused: bool
    is_completed: bool
    job_id: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    next_run: Optional[datetime] = None

    class Config:
        from_attributes = True


class NaturalLanguageReminder(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


class ParsedReminderResponse(BaseModel):
    title: str
    reminder_time: datetime
    timezone: str = "UTC"
    priority: str = "medium"
    description: Optional[str] = None


class ReminderBulkAction(BaseModel):
    reminder_ids: List[UUID]
    action: str = Field(..., pattern=r"^(delete|pause|resume|complete)$")


class ReminderListResponse(BaseModel):
    items: List[ReminderResponse]
    total: int
    skip: int
    limit: int


class DailySummary(BaseModel):
    date: str
    total: int
    completed: int
    pending: int
    reminders: List[ReminderResponse]
