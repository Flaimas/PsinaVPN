from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.invoice import Invoice

from .base import Base

if TYPE_CHECKING:
    from src.database.models.tariff import Tariff
    from src.database.models.user import User


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    sub_url: Mapped[str]
    sub_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.timezone("utc", func.now())
    )
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="subscriptions")
    tariff: Mapped[Tariff] = relationship(back_populates="subscriptions")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="subscription")
