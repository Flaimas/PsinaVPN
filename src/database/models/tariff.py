from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ARRAY, BigInteger, String
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
    price: Mapped[float] = mapped_column(nullable=False)
    category: Mapped[TariffCategory] = mapped_column(String(20), nullable=False)
    traffic_limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true")
    squad_uuids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), default=list, nullable=False
    )

    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="tariff")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="tariff")
