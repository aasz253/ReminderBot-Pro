import json
import logging
from decimal import Decimal

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.payment import Payment, PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mpesa", tags=["Webhooks"])


@router.post("/callback")
async def mpesa_callback(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.info(f"M-Pesa callback received: {json.dumps(body)}")

    stk_callback = body.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")
    checkout_request_id = stk_callback.get("CheckoutRequestID")

    if result_code == 0:
        metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        callback_data = {}
        for item in metadata:
            callback_data[item.get("Name")] = item.get("Value")

        payment = Payment(
            amount=Decimal(str(callback_data.get("Amount", 0))),
            currency="KES",
            provider=PaymentProvider.MPESA,
            provider_reference=callback_data.get("MpesaReceiptNumber", checkout_request_id),
            status=PaymentStatus.COMPLETED,
            payment_method="M-Pesa",
            metadata=json.dumps({
                "phone": callback_data.get("PhoneNumber"),
                "transaction_date": callback_data.get("TransactionDate"),
                "checkout_request_id": checkout_request_id,
            }),
        )
        db.add(payment)
        await db.flush()
        logger.info(f"M-Pesa payment completed: {callback_data.get('MpesaReceiptNumber')}")
    else:
        logger.warning(f"M-Pesa payment failed: {result_desc}")
        payment = Payment(
            amount=Decimal("0"),
            currency="KES",
            provider=PaymentProvider.MPESA,
            provider_reference=checkout_request_id or "failed",
            status=PaymentStatus.FAILED,
            metadata=json.dumps({"error": result_desc}),
        )
        db.add(payment)
        await db.flush()

    return {"ResultCode": 0, "ResultDesc": "Success"}


@router.post("/confirmation")
async def mpesa_confirmation(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.info(f"M-Pesa confirmation received")
    return {"ResultCode": 0, "ResultDesc": "Success"}


@router.post("/validation")
async def mpesa_validation(request: Request):
    return {"ResultCode": 0, "ResultDesc": "Success"}
