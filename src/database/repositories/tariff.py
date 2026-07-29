from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.tariff import Tariff


class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tariffs(self, is_active: bool | None = True) -> list[Tariff]:
        stmt = select(Tariff)

        if is_active is not None:
            stmt = stmt.where(Tariff.is_active == is_active)
        stmt = stmt.order_by(Tariff.price)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_tariff_by_slug(self, slug: str, is_active: bool = True) -> Tariff:
        stmt = select(Tariff).where(Tariff.is_active == is_active, Tariff.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one()
