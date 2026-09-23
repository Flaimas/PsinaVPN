from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
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
    referrer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    balance: Mapped[float] = mapped_column(
        default=settings.START_BALANCE, server_default="0.0", nullable=False
    )
    is_banned: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default="false"
    )
    is_test_used: Mapped[bool] = mapped_column(default=False, server_default="false")

    referrer: Mapped[User | None] = relationship(
        remote_side=[id], back_populates="referrals"
    )
    referrals: Mapped[list[User]] = relationship(back_populates="referrer")
    subscription: Mapped[Subscription | None] = relationship(
        back_populates="user", uselist=False
    )
    invoices: Mapped[list[Invoice]] = relationship(back_populates="user")
