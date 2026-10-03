from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import NotificationStatus, StageNotification

from .base import Base


class SubscriptionNotification(Base):
    __tablename__ = "subscription_notifications"
    __table_args__ = (UniqueConstraint("subscription_id", "stage", "expired_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False
    )
    stage: Mapped[StageNotification] = mapped_column(String(20), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        String(20),
        default=NotificationStatus.PENDING,
        server_default=NotificationStatus.PENDING.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attempts: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
