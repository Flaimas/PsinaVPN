from src.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    balance: Mapped[int]