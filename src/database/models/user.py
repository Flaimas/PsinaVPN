from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, DateTime, BigInteger
from datetime import datetime
from src.core.config import settings

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone('utc', func.now())
    )
    balance: Mapped[float] = mapped_column(
        default=settings.START_BALANCE, 
        server_default="0.0",
        nullable=False
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")