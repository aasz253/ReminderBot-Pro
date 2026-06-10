from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.subscription import Subscription, PlanType
from app.models.payment import Payment, PaymentStatus
from app.models.reminder import Reminder
from app.models.support_ticket import SupportTicket, TicketStatus
from app.models.activity_log import ActivityLog
from app.schemas.user import UserResponse
from app.schemas.subscription import SubscriptionResponse
from app.schemas.payment import PaymentResponse
from app.schemas.reminder import ReminderResponse
from app.schemas.analytics import AdminStats
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_term)) |
            (User.username.ilike(search_term)) |
            (User.full_name.ilike(search_term))
        )
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    users = list(result.scalars().all())

    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if is_active is not None:
        user.is_active = is_active
    if is_superuser is not None:
        user.is_superuser = is_superuser
    if is_verified is not None:
        user.is_verified = is_verified
    await db.flush()
    return UserResponse.model_validate(user)


@router.get("/subscriptions", response_model=dict)
async def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    plan: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Subscription)
    if plan:
        query = query.where(Subscription.plan == PlanType(plan))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Subscription.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    subscriptions = list(result.scalars().all())

    return {
        "items": [SubscriptionResponse.model_validate(s) for s in subscriptions],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/payments", response_model=dict)
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    count_query = select(func.count()).select_from(Payment)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    result = await db.execute(query)
    payments = list(result.scalars().all())
    return {
        "items": [PaymentResponse.model_validate(p) for p in payments],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/analytics", response_model=AdminStats)
async def admin_analytics(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    stats = await service.get_admin_stats()
    return AdminStats(**stats)


@router.get("/reminders", response_model=dict)
async def list_all_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Reminder)
    if is_active is not None:
        query = query.where(Reminder.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Reminder.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reminders = list(result.scalars().all())
    return {
        "items": [ReminderResponse.model_validate(r) for r in reminders],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/tickets", response_model=dict)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SupportTicket)
    if status_filter:
        query = query.where(SupportTicket.status == TicketStatus(status_filter))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    tickets = list(result.scalars().all())
    return {
        "items": [{
            "id": str(t.id),
            "user_id": str(t.user_id),
            "subject": t.subject,
            "status": t.status.value,
            "priority": t.priority.value,
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
        } for t in tickets],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: UUID,
    status: str = Query(..., regex=r"^(open|in_progress|resolved|closed)$"),
    assigned_to: Optional[UUID] = None,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    ticket.status = TicketStatus(status)
    if assigned_to:
        ticket.assigned_to = assigned_to
    await db.flush()
    return {"message": "Ticket updated", "status": ticket.status.value}


@router.get("/logs", response_model=dict)
async def list_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ActivityLog).order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
    count_query = select(func.count()).select_from(ActivityLog)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    result = await db.execute(query)
    logs = list(result.scalars().all())
    return {
        "items": [{
            "id": str(log.id),
            "user_id": str(log.user_id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        } for log in logs],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
