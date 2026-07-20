from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models.tariff import Tariff

class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def calculate_period_price(self, price: int, period: int) -> tuple[int, int]:
        price_full_period = (period / 30) * int(price)
        if period > 60:
            discount = 0.20
        elif period > 30:
            discount = 0.10
        else:
            discount = 0
        
        return int(price_full_period), int(price_full_period - (discount * price_full_period))

    async def get_tariffs(self, is_active: bool = True) -> list[Tariff]:
        stmt = (
            select(Tariff)
            .where(Tariff.is_active == is_active)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_tariff_by_slug(self, slug: str) -> Tariff:
        stmt = (
            select(Tariff)
            .where(Tariff.is_active == True, Tariff.slug == slug)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()