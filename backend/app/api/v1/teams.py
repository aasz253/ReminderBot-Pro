from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamListResponse,
    TeamMemberResponse, InviteMember, UpdateMemberRole, AssignReminder,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=TeamListResponse)
async def list_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    teams = await service.get_teams(current_user.id)
    team_responses = []
    for team in teams:
        members = await service.get_members(team.id, current_user.id)
        team_responses.append(TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            owner_id=team.owner_id,
            member_count=len(members),
            created_at=team.created_at,
            updated_at=team.updated_at,
            members=[TeamMemberResponse(
                id=m.id,
                user_id=m.user_id,
                username="",
                email="",
                role=m.role.value,
                joined_at=m.joined_at,
                created_at=m.created_at,
            ) for m in members],
        ))
    return TeamListResponse(items=team_responses, total=len(team_responses))


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    team = await service.create_team(
        name=data.name,
        description=data.description,
        owner=current_user,
    )
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_id=team.owner_id,
        member_count=1,
        created_at=team.created_at,
        updated_at=team.updated_at,
        members=[],
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    team = await service.get_team_by_id(team_id, current_user.id)
    members = await service.get_members(team_id, current_user.id)

    member_responses = []
    for m in members:
        u_result = await db.execute(
            __import__("sqlalchemy").select(User).where(User.id == m.user_id)
        )
        u = u_result.scalar_one_or_none()
        member_responses.append(TeamMemberResponse(
            id=m.id,
            user_id=m.user_id,
            username=u.username if u else "",
            email=u.email if u else "",
            full_name=u.full_name if u else None,
            role=m.role.value,
            joined_at=m.joined_at,
            created_at=m.created_at,
        ))

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_id=team.owner_id,
        member_count=len(member_responses),
        created_at=team.created_at,
        updated_at=team.updated_at,
        members=member_responses,
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    team = await service.update_team(
        team_id, current_user.id, data.model_dump(exclude_unset=True)
    )
    members = await service.get_members(team_id, current_user.id)
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_id=team.owner_id,
        member_count=len(members),
        created_at=team.created_at,
        updated_at=team.updated_at,
        members=[],
    )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    await service.delete_team(team_id, current_user.id)


@router.post("/{team_id}/invite", response_model=TeamMemberResponse)
async def invite_member(
    team_id: UUID,
    data: InviteMember,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    member = await service.invite_member(
        team_id, data.email, data.role, current_user
    )
    u_result = await db.execute(
        __import__("sqlalchemy").select(User).where(User.id == member.user_id)
    )
    u = u_result.scalar_one_or_none()
    return TeamMemberResponse(
        id=member.id,
        user_id=member.user_id,
        username=u.username if u else "",
        email=u.email if u else "",
        full_name=u.full_name if u else None,
        role=member.role.value,
        joined_at=member.joined_at,
        created_at=member.created_at,
    )


@router.post("/{team_id}/accept-invite")
async def accept_invite(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    member = await service.accept_invite(team_id, current_user.id)
    return {"message": "Invite accepted", "team_id": str(team_id)}


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    team_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    await service.remove_member(team_id, member_id, current_user.id)


@router.put("/{team_id}/members/{member_id}/role")
async def update_member_role(
    team_id: UUID,
    member_id: UUID,
    data: UpdateMemberRole,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    member = await service.update_member_role(
        team_id, member_id, data.role, current_user.id
    )
    return {"message": "Role updated", "new_role": member.role.value}


@router.post("/{team_id}/reminders/assign")
async def assign_reminder(
    team_id: UUID,
    data: AssignReminder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    team_reminder = await service.assign_reminder(
        team_id, data.reminder_id, data.assigned_to, current_user.id
    )
    return {"message": "Reminder assigned", "id": str(team_reminder.id)}


@router.get("/{team_id}/analytics")
async def team_analytics(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    return await service.get_team_analytics(team_id, current_user.id)


@router.get("/{team_id}/productivity")
async def team_productivity(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeamService(db)
    return await service.get_team_productivity(team_id, current_user.id)
