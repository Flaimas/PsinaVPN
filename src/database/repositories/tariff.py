from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import TariffCategory
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff
from src.database.models.user import User


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

    async def get_available_tariffs_for_user(
        self, telegram_id: int, category: TariffCategory | None = None
    ) -> list[Tariff]:
        stmt = (
            select(Tariff)
            .outerjoin(
                Subscription,
                and_(
                    Subscription.tariff_id == Tariff.id,
                    Subscription.user_id
                    == select(User.id)
                    .where(User.telegram_id == telegram_id)
                    .scalar_subquery(),
                ),
            )
            .where(
                Tariff.is_active.is_(True),
                Subscription.id.is_(None),
            )
        )

        if category is not None:
            stmt = stmt.where(Tariff.category == category)

        stmt = stmt.order_by(Tariff.price.asc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_tariff_by_id(self, tariff_id: int) -> Tariff | None:
        stmt = select(Tariff).where(Tariff.is_active, Tariff.id == tariff_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
