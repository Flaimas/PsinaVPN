from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import InvoiceOperation, PaymentProvider, PaymentStatus

from .base import Base

if TYPE_CHECKING:
    from .subscription import Subscription
    from .tariff import Tariff
    from .user import User


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    tariff_id: Mapped[int | None] = mapped_column(ForeignKey("tariffs.id"))
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[PaymentProvider] = mapped_column(
        SQLEnum(PaymentProvider, native_enum=False), nullable=False
    )
    provider_payment_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float)
    duration_days: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        String(20),
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.timezone("utc", func.now())
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    operation: Mapped[InvoiceOperation] = mapped_column(
        String(10),
        default=InvoiceOperation.BUY,
        server_default=InvoiceOperation.BUY.value,
    )
    user: Mapped[User | None] = relationship(back_populates="invoices")
    tariff: Mapped[Tariff | None] = relationship(back_populates="invoices")
    subscription: Mapped[Subscription | None] = relationship(back_populates="invoices")
