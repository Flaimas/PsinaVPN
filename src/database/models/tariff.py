from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from src.database.models.subscription import Subscription

    from .invoice import Invoice


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    price: Mapped[float] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true")

    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="tariff")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="tariff")
