from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    price: Mapped[float] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true")

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="tariff")