from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import SubscriptionStatus, TariffCategory
from src.database.models.invoice import Invoice

from .base import Base

if TYPE_CHECKING:
    from src.database.models.tariff import Tariff
    from src.database.models.user import User


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    tariff_category: Mapped[TariffCategory] = mapped_column(String(20), nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), nullable=False, server_default="0"
    )
    sub_url: Mapped[str]
    remnawave_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(20),
        default=SubscriptionStatus.ACTIVE,
        server_default=SubscriptionStatus.ACTIVE.value,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.timezone("utc", func.now())
    )
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="subscription")
    tariff: Mapped[Tariff] = relationship(back_populates="subscriptions")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="subscription")
