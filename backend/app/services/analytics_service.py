from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, case

from app.models.user import User
from app.models.reminder import Reminder, Priority
from app.models.notification import Notification, NotificationStatus
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.models.payment import Payment, PaymentStatus
from app.models.team import Team, TeamMember, TeamReminder, TeamReminderStatus
from app.models.category import Category
from app.models.activity_log import ActivityLog


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_stats(self, user_id: UUID) -> dict:
        total_query = select(func.count()).where(Reminder.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        active_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.is_completed == False,
        )
        active_result = await self.db.execute(active_query)
        active = active_result.scalar() or 0

        completed_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == True,
        )
        completed_result = await self.db.execute(completed_query)
        completed = completed_result.scalar() or 0

        missed_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_completed == False,
            Reminder.is_active == True,
            Reminder.reminder_time < datetime.now(timezone.utc),
        )
        missed_result = await self.db.execute(missed_query)
        missed = missed_result.scalar() or 0

        paused_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_paused == True,
        )
        paused_result = await self.db.execute(paused_query)
        paused = paused_result.scalar() or 0

        upcoming_query = select(func.count()).where(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.is_paused == False,
            Reminder.is_completed == False,
            Reminder.reminder_time > datetime.now(timezone.utc),
        )
        upcoming_result = await self.db.execute(upcoming_query)
        upcoming = upcoming_result.scalar() or 0

        completion_rate = (completed / total * 100) if total > 0 else 0

        streaks = await self._calculate_streaks(user_id)

        return {
            "total_reminders": total,
            "active_reminders": active,
            "completed_reminders": completed,
            "missed_reminders": missed,
            "paused_reminders": paused,
            "upcoming_reminders": upcoming,
            "completion_rate": round(completion_rate, 2),
            "current_streak": streaks["current"],
            "longest_streak": streaks["longest"],
        }

    async def get_reminder_trends(self, user_id: UUID, period: str = "weekly") -> List[dict]:
        now = datetime.now(timezone.utc)
        if period == "daily":
            start = now - timedelta(days=30)
            date_trunc = func.date(Reminder.created_at)
        elif period == "weekly":
            start = now - timedelta(weeks=12)
            date_trunc = func.date_trunc("week", Reminder.created_at)
        else:
            start = now - timedelta(days=365)
            date_trunc = func.date_trunc("month", Reminder.created_at)

        created_query = (
            select(
                date_trunc.label("date"),
                func.count().label("count"),
            )
            .where(
                Reminder.user_id == user_id,
                Reminder.created_at >= start,
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        created_result = await self.db.execute(created_query)
        created_data = {row.date: row.count for row in created_result.all()}

        completed_query = (
            select(
                date_trunc.label("date"),
                func.count().label("count"),
            )
            .where(
                Reminder.user_id == user_id,
                Reminder.completed_at >= start,
                Reminder.is_completed == True,
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        completed_result = await self.db.execute(completed_query)
        completed_data = {row.date: row.count for row in completed_result.all()}

        all_dates = sorted(set(list(created_data.keys()) + list(completed_data.keys())))
        trends = []
        for date in all_dates:
            trends.append({
                "date": date.isoformat() if hasattr(date, "isoformat") else str(date),
                "created": created_data.get(date, 0),
                "completed": completed_data.get(date, 0),
                "missed": 0,
            })

        return trends

    async def get_productivity_score(self, user_id: UUID) -> dict:
        stats = await self.get_user_stats(user_id)

        completion_rate = stats["completion_rate"]
        completion_score = completion_rate * 0.35

        consistency = stats["current_streak"]
        consistency_score = min(consistency * 5, 25)

        completed = stats["completed_reminders"]
        missed = stats["missed_reminders"]
        total_attempted = completed + missed
        timeliness = (completed / total_attempted * 100) if total_attempted > 0 else 0
        timeliness_score = timeliness * 0.25

        streak_score = min(stats["longest_streak"] * 3, 15)

        overall = min(completion_score + consistency_score + timeliness_score + streak_score, 100)

        return {
            "overall_score": round(overall, 2),
            "completion_rate_score": round(completion_score, 2),
            "consistency_score": round(consistency_score, 2),
            "timeliness_score": round(timeliness_score, 2),
            "streak_score": round(streak_score, 2),
            "total_reminders": stats["total_reminders"],
            "completed_reminders": stats["completed_reminders"],
            "missed_reminders": stats["missed_reminders"],
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "score_breakdown": {
                "completion_rate": round(completion_rate, 2),
                "consistency_days": consistency,
                "timeliness_rate": round(timeliness, 2),
                "longest_streak": stats["longest_streak"],
            },
        }

    async def get_category_breakdown(self, user_id: UUID) -> List[dict]:
        query = (
            select(
                Category.id,
                Category.name,
                Category.color,
                func.count(Reminder.id).label("total"),
                func.count().filter(Reminder.is_completed == True).label("completed"),
            )
            .join(Reminder, Reminder.category_id == Category.id, isouter=True)
            .where(Category.user_id == user_id)
            .group_by(Category.id, Category.name, Category.color)
        )
        result = await self.db.execute(query)
        total_all = sum((row.total or 0) for row in result.all())

        result = await self.db.execute(query)
        breakdown = []
        for row in result.all():
            total = row.total or 0
            breakdown.append({
                "category_id": str(row.id),
                "category_name": row.name,
                "color": row.color,
                "total": total,
                "completed": row.completed or 0,
                "percentage": round((total / total_all * 100), 2) if total_all > 0 else 0,
            })

        return breakdown

    async def get_team_analytics(self, team_id: UUID) -> dict:
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

        return {
            "total_members": total_members,
            "total_reminders": total_reminders,
            "completed_reminders": completed,
            "missed_reminders": missed,
            "completion_rate": round(completion_rate, 2),
        }

    async def get_admin_stats(self) -> dict:
        total_users_query = select(func.count()).select_from(User)
        total_users_result = await self.db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0

        active_users_query = select(func.count()).where(
            User.is_active == True,
            User.is_verified == True,
        )
        active_users_result = await self.db.execute(active_users_query)
        active_users = active_users_result.scalar() or 0

        total_subs_query = select(func.count()).select_from(Subscription)
        total_subs_result = await self.db.execute(total_subs_query)
        total_subs = total_subs_result.scalar() or 0

        premium_query = select(func.count()).where(Subscription.plan == PlanType.PREMIUM)
        premium_result = await self.db.execute(premium_query)
        premium = premium_result.scalar() or 0

        business_query = select(func.count()).where(Subscription.plan == PlanType.BUSINESS)
        business_result = await self.db.execute(business_query)
        business = business_result.scalar() or 0

        revenue_query = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.COMPLETED,
        )
        revenue_result = await self.db.execute(revenue_query)
        total_revenue = float(revenue_result.scalar() or 0)

        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_revenue_query = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at >= month_start,
        )
        month_revenue_result = await self.db.execute(month_revenue_query)
        month_revenue = float(month_revenue_result.scalar() or 0)

        total_reminders_query = select(func.count()).select_from(Reminder)
        total_reminders_result = await self.db.execute(total_reminders_query)
        total_reminders = total_reminders_result.scalar() or 0

        delivered_query = select(func.count()).where(
            Notification.status == NotificationStatus.DELIVERED,
        )
        delivered_result = await self.db.execute(delivered_query)
        delivered = delivered_result.scalar() or 0

        total_notif_query = select(func.count()).select_from(Notification)
        total_notif_result = await self.db.execute(total_notif_query)
        total_notif = total_notif_result.scalar() or 0
        delivery_rate = (delivered / total_notif * 100) if total_notif > 0 else 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_subscriptions": total_subs,
            "premium_subscriptions": premium,
            "business_subscriptions": business,
            "total_revenue": round(total_revenue, 2),
            "revenue_this_month": round(month_revenue, 2),
            "total_reminders": total_reminders,
            "notification_delivery_rate": round(delivery_rate, 2),
        }

    async def _calculate_streaks(self, user_id: UUID) -> dict:
        today = datetime.now(timezone.utc).date()
        query = (
            select(func.date(Reminder.completed_at))
            .where(
                Reminder.user_id == user_id,
                Reminder.is_completed == True,
                Reminder.completed_at.isnot(None),
            )
            .order_by(Reminder.completed_at.desc())
            .distinct()
        )
        result = await self.db.execute(query)
        completion_dates = sorted(set(row[0] for row in result.all()), reverse=True)

        if not completion_dates:
            return {"current": 0, "longest": 0}

        current = 0
        longest = 0
        streak = 0
        check_date = today

        for date in completion_dates:
            if date == check_date or date == check_date - timedelta(days=1):
                if date == check_date - timedelta(days=1):
                    streak = 1 if current == 0 else streak
                if date == check_date:
                    current += 1
                    streak += 1
                else:
                    streak += 1
                check_date = date
            elif date < check_date - timedelta(days=1):
                longest = max(longest, streak)
                streak = 1
                check_date = date
            longest = max(longest, streak)

        if completion_dates and completion_dates[0] >= today - timedelta(days=1):
            current = streak
        else:
            current = 0

        return {"current": current, "longest": longest}
