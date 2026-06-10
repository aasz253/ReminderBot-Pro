from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class TeamMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: str
    joined_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    member_count: int = 0
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    items: List[TeamResponse]
    total: int


class InviteMember(BaseModel):
    email: str
    role: str = Field(default="member", pattern=r"^(admin|member)$")


class AcceptInvite(BaseModel):
    team_id: UUID


class UpdateMemberRole(BaseModel):
    role: str = Field(..., pattern=r"^(admin|member)$")


class AssignReminder(BaseModel):
    reminder_id: UUID
    assigned_to: Optional[UUID] = None
