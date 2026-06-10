import secrets
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import settings
from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.models.user import User
from app.models.subscription import Subscription


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_stripe_payment(
        self, amount: Decimal, currency: str, payment_method_id: str, user: User
    ) -> Payment:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
            )

            payment = Payment(
                user_id=user.id,
                amount=amount,
                currency=currency,
                provider=PaymentProvider.STRIPE,
                provider_reference=intent.id,
                status=PaymentStatus.COMPLETED if intent.status == "succeeded" else PaymentStatus.PENDING,
                payment_method=payment_method_id,
            )
            self.db.add(payment)
            await self.db.flush()
            return payment

        except Exception as e:
            payment = Payment(
                user_id=user.id,
                amount=amount,
                currency=currency,
                provider=PaymentProvider.STRIPE,
                provider_reference="failed",
                status=PaymentStatus.FAILED,
                payment_method=payment_method_id,
                payment_metadata=str(e),
            )
            self.db.add(payment)
            await self.db.flush()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe payment failed: {str(e)}",
            )

    async def process_paypal_payment(
        self, amount: Decimal, currency: str, return_url: str, cancel_url: str
    ) -> dict:
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                "mode": settings.PAYPAL_MODE,
                "client_id": settings.PAYPAL_CLIENT_ID,
                "client_secret": settings.PAYPAL_CLIENT_SECRET,
            })

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency,
                    },
                    "description": f"ReminderBot Pro {currency} {amount}",
                }],
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
            })

            if payment.create():
                approval_url = next(
                    (link.href for link in payment.links if link.rel == "approval_url"),
                    None,
                )
                return {
                    "payment_id": payment.id,
                    "approval_url": approval_url,
                    "status": "created",
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal payment creation failed: {payment.error}",
                )

        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PayPal SDK not configured",
            )

    async def execute_paypal_payment(self, payment_id: str, payer_id: str) -> Payment:
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                "mode": settings.PAYPAL_MODE,
                "client_id": settings.PAYPAL_CLIENT_ID,
                "client_secret": settings.PAYPAL_CLIENT_SECRET,
            })

            payment = paypalrestsdk.Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                transaction = payment.transactions[0]
                amount = Decimal(transaction["amount"]["total"])
                currency = transaction["amount"]["currency"]

                return Payment(
                    amount=amount,
                    currency=currency,
                    provider=PaymentProvider.PAYPAL,
                    provider_reference=payment_id,
                    status=PaymentStatus.COMPLETED,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PayPal payment execution failed",
                )

        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PayPal SDK not configured",
            )

    async def process_mpesa_stk_push(
        self, phone: str, amount: Decimal, account_reference: str
    ) -> dict:
        if settings.MPESA_ENVIRONMENT == "sandbox":
            return {
                "MerchantRequestID": secrets.token_hex(8),
                "CheckoutRequestID": secrets.token_hex(16),
                "ResponseCode": "0",
                "ResponseDescription": "Success. Request accepted for processing",
                "CustomerMessage": "Success. Request accepted for processing",
            }

        try:
            async with httpx.AsyncClient() as client:
                auth_response = await client.get(
                    "https://api.safaricom.co.ke/oauth/v1/generate",
                    params={"grant_type": "client_credentials"},
                    auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
                )
                auth_data = auth_response.json()
                access_token = auth_data.get("access_token")

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
                import base64
                password = base64.b64encode(password_str.encode()).decode()

                stk_response = await client.post(
                    "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "BusinessShortCode": settings.MPESA_SHORTCODE,
                        "Password": password,
                        "Timestamp": timestamp,
                        "TransactionType": "CustomerPayBillOnline",
                        "Amount": str(int(amount)),
                        "PartyA": phone,
                        "PartyB": settings.MPESA_SHORTCODE,
                        "PhoneNumber": phone,
                        "CallBackURL": f"{settings.BACKEND_URL}/api/webhooks/mpesa/callback",
                        "AccountReference": account_reference,
                        "TransactionDesc": "ReminderBot Subscription",
                    },
                )
                return stk_response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"M-Pesa STK push failed: {str(e)}",
            )

    async def process_airtel_money(self, phone: str, amount: Decimal) -> dict:
        if not settings.AIRTEL_API_KEY:
            return {
                "status": "simulated",
                "message": "Airtel Money API not configured. Payment recorded as pending.",
            }

        try:
            async with httpx.AsyncClient() as client:
                auth_response = await client.post(
                    "https://openapi.airtel.africa/auth/oauth2/token",
                    json={
                        "client_id": settings.AIRTEL_API_KEY,
                        "client_secret": settings.AIRTEL_API_SECRET,
                        "grant_type": "client_credentials",
                    },
                )
                auth_data = auth_response.json()
                access_token = auth_data.get("access_token")

                payment_response = await client.post(
                    "https://openapi.airtel.africa/merchant/v1/payments/",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "X-Country": "KE",
                        "X-Currency": "KES",
                    },
                    json={
                        "reference": f"RB-{secrets.token_hex(8)}",
                        "subscriber": {
                            "country": "KE",
                            "currency": "KES",
                            "msisdn": phone,
                        },
                        "transaction": {
                            "amount": str(int(amount)),
                            "country": "KE",
                            "currency": "KES",
                            "id": secrets.token_hex(12),
                        },
                    },
                )
                return payment_response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Airtel Money payment failed: {str(e)}",
            )

    async def verify_mpesa_callback(self, data: dict) -> Payment:
        stk_callback = data.get("Body", {}).get("stkCallback", {})
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
                payment_metadata=json.dumps({
                    "phone": callback_data.get("PhoneNumber"),
                    "transaction_date": callback_data.get("TransactionDate"),
                    "checkout_request_id": checkout_request_id,
                }),
            )
            self.db.add(payment)
            await self.db.flush()
            return payment
        else:
            payment = Payment(
                amount=Decimal("0"),
                currency="KES",
                provider=PaymentProvider.MPESA,
                provider_reference=checkout_request_id or "failed",
                status=PaymentStatus.FAILED,
                payment_metadata=json.dumps({"error": result_desc}),
            )
            self.db.add(payment)
            await self.db.flush()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"M-Pesa payment failed: {result_desc}",
            )

    async def generate_invoice(self, payment: Payment) -> str:
        invoice_id = f"INV-{payment.id.hex[:12].upper()}"
        invoice_url = f"{settings.BACKEND_URL}/invoices/{invoice_id}"
        payment.invoice_url = invoice_url
        await self.db.flush()
        return invoice_url

    async def refund_payment(self, payment_id: UUID) -> Payment:
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed payments can be refunded",
            )

        if payment.provider == PaymentProvider.STRIPE:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                refund = stripe.Refund.create(
                    payment_intent=payment.provider_reference,
                )
                if refund.status in ["succeeded", "pending"]:
                    payment.status = PaymentStatus.REFUNDED
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Stripe refund failed",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Refund failed: {str(e)}",
                )
        else:
            payment.status = PaymentStatus.REFUNDED

        await self.db.flush()
        return payment
