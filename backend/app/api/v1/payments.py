from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import (
    PaymentResponse, PaymentListResponse, MpesaSTKPushRequest,
    StripePaymentIntent, PaypalPaymentRequest, PaypalExecutePayment,
    InvoiceResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    count_query = select(func.count()).where(Payment.user_id == current_user.id)

    result = await db.execute(query)
    payments = list(result.scalars().all())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return PaymentListResponse(
        items=[PaymentResponse.model_validate(p) for p in payments],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    result = await db.execute(
        select(Payment).where(
            Payment.id == UUID(payment_id),
            Payment.user_id == current_user.id,
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return PaymentResponse.model_validate(payment)


@router.post("/stripe", response_model=PaymentResponse)
async def create_stripe_payment(
    data: StripePaymentIntent,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    payment = await service.process_stripe_payment(
        amount=data.amount,
        currency=data.currency,
        payment_method_id=data.payment_method_id,
        user=current_user,
    )
    return PaymentResponse.model_validate(payment)


@router.post("/paypal/create")
async def create_paypal_payment(
    data: PaypalPaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    result = await service.process_paypal_payment(
        amount=data.amount,
        currency=data.currency,
        return_url=data.return_url,
        cancel_url=data.cancel_url,
    )
    return result


@router.post("/paypal/execute", response_model=PaymentResponse)
async def execute_paypal_payment(
    data: PaypalExecutePayment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    payment = await service.execute_paypal_payment(data.payment_id, data.payer_id)
    payment.user_id = current_user.id
    db.add(payment)
    await db.flush()
    return PaymentResponse.model_validate(payment)


@router.post("/mpesa/stk-push")
async def mpesa_stk_push(
    data: MpesaSTKPushRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    result = await service.process_mpesa_stk_push(
        phone=data.phone,
        amount=data.amount,
        account_reference=data.account_reference,
    )
    return result


@router.post("/mpesa/callback")
async def mpesa_callback(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    payment = await service.verify_mpesa_callback(data)
    return {"ResultCode": 0, "ResultDesc": "Success"}


@router.post("/{payment_id}/invoice", response_model=InvoiceResponse)
async def generate_invoice(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    result = await db.execute(
        select(Payment).where(
            Payment.id == UUID(payment_id),
            Payment.user_id == current_user.id,
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    service = PaymentService(db)
    invoice_url = await service.generate_invoice(payment)
    return InvoiceResponse(
        invoice_url=invoice_url,
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        created_at=payment.created_at,
    )
