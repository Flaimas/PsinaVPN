from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import InvoiceOperation, PaymentProvider, PaymentStatus


class StrictDTO(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class CreateInvoiceDTO(StrictDTO):
    user_id: int
    tariff_id: int
    provider: PaymentProvider
    provider_payment_id: str
    amount: float
    duration_days: int
    operation: InvoiceOperation
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    paid_at: datetime | None = None
    subscription_id: int | None
