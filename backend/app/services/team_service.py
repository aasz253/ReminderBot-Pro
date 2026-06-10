import secrets
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete

from app.models.team import Team, TeamMember, TeamMemberRole, TeamReminder, TeamReminderStatus
from app.models.user import User
from app.models.reminder import Reminder
from app.models.activity_log import ActivityLog
from app.services.subscription_service import SubscriptionService


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_service = SubscriptionService(db)

    async def create_team(self, name: str, description: Optional[str], owner: User) -> Team:
        team = Team(
            name=name,
            description=description,
            owner_id=owner.id,
        )
        self.db.add(team)
        await self.db.flush()

        member = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamMemberRole.OWNER,
            joined_at=datetime.now(timezone.utc),
        )
        self.db.add(member)
        await self.db.flush()

        log = ActivityLog(
            user_id=owner.id,
            action="team.create",
            resource_type="team",
            resource_id=str(team.id),
        )
        self.db.add(log)
        await self.db.flush()

        return team

    async def get_teams(self, user_id: UUID) -> List[Team]:
        query = (
            select(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .where(TeamMember.user_id == user_id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_team_by_id(self, team_id: UUID, user_id: UUID) -> Team:
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        is_member = await self._is_member(team_id, user_id)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this team",
            )

        return team

    async def update_team(self, team_id: UUID, user_id: UUID, update_data: dict) -> Team:
        team = await self.get_team_by_id(team_id, user_id)
        await self._require_role(team_id, user_id, [TeamMemberRole.OWNER, TeamMemberRole.ADMIN])

        for key, value in update_data.items():
            if value is not None and hasattr(team, key):
                setattr(team, key, value)
        team.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return team

    async def delete_team(self, team_id: UUID, user_id: UUID) -> None:
        team = await self.get_team_by_id(team_id, user_id)
        if team.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the team owner can delete the team",
            )
        await self.db.delete(team)
        await self.db.flush()

    async def invite_member(self, team_id: UUID, email: str, role: str, invited_by: User) -> TeamMember:
        team = await self.get_team_by_id(team_id, invited_by.id)
        await self._require_role(team_id, invited_by.id, [TeamMemberRole.OWNER, TeamMemberRole.ADMIN])

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found",
            )

        existing = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this team",
            )

        member = TeamMember(
            team_id=team_id,
            user_id=user.id,
            role=TeamMemberRole(role),
            invited_by=invited_by.id,
        )
        self.db.add(member)
        await self.db.flush()

        log = ActivityLog(
            user_id=invited_by.id,
            action="team.invite",
            resource_type="team_member",
            resource_id=str(member.id),
            details={"email": email, "role": role},
        )
        self.db.add(log)
        await self.db.flush()

        return member

    async def accept_invite(self, team_id: UUID, user_id: UUID) -> TeamMember:
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.joined_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        member.joined_at = datetime.now(timezone.utc)
        await self.db.flush()
        return member

    async def remove_member(self, team_id: UUID, member_id: UUID, requester_id: UUID) -> None:
        team = await self.get_team_by_id(team_id, requester_id)

        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.id == member_id,
                TeamMember.team_id == team_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        if member.role == TeamMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the team owner",
            )

        await self._require_role(team_id, requester_id, [TeamMemberRole.OWNER, TeamMemberRole.ADMIN])
        await self.db.delete(member)
        await self.db.flush()

    async def update_member_role(self, team_id: UUID, member_id: UUID, new_role: str, requester_id: UUID) -> TeamMember:
        await self._require_role(team_id, requester_id, [TeamMemberRole.OWNER])

        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.id == member_id,
                TeamMember.team_id == team_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        if member.role == TeamMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change the owner's role",
            )

        member.role = TeamMemberRole(new_role)
        await self.db.flush()
        return member

    async def assign_reminder(
        self, team_id: UUID, reminder_id: UUID, assigned_to: Optional[UUID], user_id: UUID
    ) -> TeamReminder:
        await self._require_role(team_id, user_id, [TeamMemberRole.OWNER, TeamMemberRole.ADMIN])

        result = await self.db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found",
            )

        team_reminder = TeamReminder(
            team_id=team_id,
            reminder_id=reminder_id,
            assigned_to=assigned_to,
            status=TeamReminderStatus.PENDING,
        )
        self.db.add(team_reminder)
        await self.db.flush()
        return team_reminder

    async def track_completion(self, team_reminder_id: UUID, user_id: UUID) -> TeamReminder:
        result = await self.db.execute(
            select(TeamReminder).where(TeamReminder.id == team_reminder_id)
        )
        team_reminder = result.scalar_one_or_none()
        if not team_reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team reminder not found",
            )

        is_member = await self._is_member(team_reminder.team_id, user_id)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )

        team_reminder.status = TeamReminderStatus.COMPLETED
        await self.db.flush()
        return team_reminder

    async def get_team_analytics(self, team_id: UUID, user_id: UUID) -> dict:
        await self.get_team_by_id(team_id, user_id)

        total_members_query = select(func.count()).where(TeamMember.team_id == team_id)
        total_members_result = await self.db.execute(total_members_query)
        total_members = total_members_result.scalar() or 0

        total_reminders_query = select(func.count()).where(TeamReminder.team_id == team_id)
        total_reminders_result = await self.db.execute(total_reminders_query)
        total_reminders = total_reminders_result.scalar() or 0

        completed_query = select(func.count()).where(
            TeamReminder.team_id == team_id,
            TeamReminder.status == TeamReminderStatus.COMPLETED,
        )
        completed_result = await self.db.execute(completed_query)
        completed = completed_result.scalar() or 0

        missed_query = select(func.count()).where(
            TeamReminder.team_id == team_id,
            TeamReminder.status == TeamReminderStatus.MISSED,
        )
        missed_result = await self.db.execute(missed_query)
        missed = missed_result.scalar() or 0

        completion_rate = (completed / total_reminders * 100) if total_reminders > 0 else 0

        members_result = await self.db.execute(
            select(
                TeamMember.user_id,
                User.username,
                User.full_name,
                func.count(TeamReminder.id).label("total"),
                func.count().filter(TeamReminder.status == TeamReminderStatus.COMPLETED).label("completed"),
            )
            .select_from(TeamMember)
            .join(User, User.id == TeamMember.user_id)
            .outerjoin(
                TeamReminder,
                and_(
                    TeamReminder.team_id == TeamMember.team_id,
                    TeamReminder.assigned_to == TeamMember.user_id,
                ),
            )
            .where(TeamMember.team_id == team_id)
            .group_by(TeamMember.user_id, User.username, User.full_name)
        )
        member_productivity = []
        for row in members_result.all():
            member_productivity.append({
                "user_id": str(row.user_id),
                "username": row.username,
                "full_name": row.full_name,
                "total_assigned": row.total,
                "completed": row.completed,
            })

        return {
            "team_id": str(team_id),
            "total_members": total_members,
            "total_reminders": total_reminders,
            "completed_reminders": completed,
            "missed_reminders": missed,
            "completion_rate": round(completion_rate, 2),
            "member_productivity": member_productivity,
        }

    async def get_team_productivity(self, team_id: UUID, user_id: UUID) -> dict:
        analytics = await self.get_team_analytics(team_id, user_id)

        score = analytics["completion_rate"] * 0.6
        if analytics["total_members"] > 1:
            score += min(analytics["total_members"] / 10, 20)
        score += max(0, 20 - analytics["missed_reminders"])

        return {
            **analytics,
            "productivity_score": round(min(score, 100), 2),
        }

    async def get_members(self, team_id: UUID, user_id: UUID) -> List[TeamMember]:
        await self.get_team_by_id(team_id, user_id)
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.created_at.asc())
        )
        return list(result.scalars().all())

    async def _is_member(self, team_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def _require_role(
        self, team_id: UUID, user_id: UUID, allowed_roles: List[TeamMemberRole]
    ) -> None:
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member or member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
