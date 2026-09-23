from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.tariff import Tariff, TariffOption


class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_tariffs(self) -> list[Tariff]:
        stmt = (
            select(Tariff)
            .where(Tariff.is_active.is_(True))
            .order_by(Tariff.traffic_limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_active_tariff_by_id(self, tariff_id: int) -> Tariff | None:
        stmt = (
            select(Tariff)
            .where(Tariff.is_active, Tariff.id == tariff_id)
            .options(selectinload(Tariff.options))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_tariff_option_by_id(
        self, tariff_option_id: int
    ) -> TariffOption | None:
        stmt = select(TariffOption).where(TariffOption.id == tariff_option_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
