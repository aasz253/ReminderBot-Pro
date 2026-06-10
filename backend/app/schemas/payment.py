from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID]
    amount: Decimal
    currency: str
    provider: str
    provider_reference: str
    status: str
    payment_method: Optional[str]
    invoice_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    skip: int
    limit: int


class MpesaSTKPushRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    amount: Decimal = Field(..., gt=0)
    account_reference: str = Field(..., max_length=12)


class MpesaCallbackData(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    Amount: Optional[float] = None
    MpesaReceiptNumber: Optional[str] = None
    TransactionDate: Optional[str] = None
    PhoneNumber: Optional[str] = None


class StripePaymentIntent(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = "KES"
    payment_method_id: str


class PaypalPaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = "USD"
    return_url: str
    cancel_url: str


class PaypalExecutePayment(BaseModel):
    payment_id: str
    payer_id: str


class InvoiceResponse(BaseModel):
    invoice_url: str
    payment_id: UUID
    amount: Decimal
    currency: str
    created_at: datetime
