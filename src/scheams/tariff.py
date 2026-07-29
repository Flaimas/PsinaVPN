from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import PaymentProvider, PaymentStatus


# Базовый конфиг для всех DTO, чтобы они были неизменяемыми (frozen), как датаклассы
class StrictDTO(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class TariffOption(StrictDTO):
    period_days: int
    base_price: int
    discount_price: int
    discount_percent: int


class CreateInvoiceDTO(StrictDTO):
    user_id: int
    tariff_id: int
    provider: PaymentProvider
    provider_payment_id: str
    amount: float
    duration_days: int
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    paid_at: datetime | None = None
