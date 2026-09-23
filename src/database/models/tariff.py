from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import TariffCategory

from .base import Base

if TYPE_CHECKING:
    from src.database.models.subscription import Subscription

    from .invoice import Invoice


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[TariffCategory] = mapped_column(String(20), nullable=False)
    traffic_limit: Mapped[int] = mapped_column(nullable=False)
    is_promo: Mapped[bool] = mapped_column(default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    internal_squad_uuids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), default=list, nullable=False
    )
    external_squad_uuid: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    device_limit: Mapped[int] = mapped_column(nullable=False)

    options: Mapped[list[TariffOption]] = relationship(
        back_populates="tariff",
        cascade="all, delete-orphan",
        order_by="TariffOption.price.asc()",
    )
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="tariff")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="tariff")


class TariffOption(Base):
    __tablename__ = "tariff_options"
    id: Mapped[int] = mapped_column(primary_key=True)
    tariff_id: Mapped[int] = mapped_column(
        ForeignKey("tariffs.id", ondelete="CASCADE"), nullable=False
    )
    period_days: Mapped[int]
    old_price: Mapped[int | None]
    price: Mapped[int]

    tariff: Mapped[Tariff] = relationship(back_populates="options")
