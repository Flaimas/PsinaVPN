from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings

from .base import Base

if TYPE_CHECKING:
    from src.database.models.subscription import Subscription

    from .invoice import Invoice


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.timezone("utc", func.now())
    )
    balance: Mapped[float] = mapped_column(
        default=settings.START_BALANCE, server_default="0.0", nullable=False
    )
    is_banned: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default="false"
    )

    subscriptions: Mapped[list[Subscription]] = relationship(
        back_populates="user", order_by="Subscription.expired_at.asc()"
    )
    invoices: Mapped[list[Invoice]] = relationship(back_populates="user")
