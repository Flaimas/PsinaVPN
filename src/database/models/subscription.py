from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sub_url: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

    user: Mapped["User"] = relationship(back_populates="subscriptions")