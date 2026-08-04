from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.enums import TariffCategory
from src.database.models.subscription import Subscription
from src.database.models.user import User


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_subscription(
        self,
        user_id: int,
        tariff_id: int,
        sub_url: str,
        remnawave_user_id: int,
        expired_at: datetime,
        tariff_category: TariffCategory,
        squad_uuids: list[UUID],
    ) -> Subscription:

        subscription = Subscription(
            user_id=user_id,
            tariff_id=tariff_id,
            tariff_category=tariff_category,
            remnawave_user_id=remnawave_user_id,
            sub_url=sub_url,
            expired_at=expired_at,
            squad_uuids=squad_uuids,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def delete_subscription(self, sub_id: int) -> bool:
        stmt = delete(Subscription).where(Subscription.id == sub_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def update_expired_at_subscription(
        self, sub_id: int, new_expired_at: datetime, **kwargs
    ) -> Subscription:
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(expired_at=new_expired_at, **kwargs)
            .returning(Subscription)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_subscriptions_by_user(
        self,
        user_id: int,
        load_user: bool = False,
        load_tariff: bool = False,
    ) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)

        if load_tariff:
            stmt = stmt.options(joinedload(Subscription.tariff))

        if load_user:
            stmt = stmt.options(joinedload(Subscription.user))

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_subscriptions_by_tg_id(self, telegram_id: int) -> list[Subscription]:
        stmt = select(Subscription).join(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_subscription_by_id(self, sub_id: int):
        stmt = select(Subscription).where(Subscription.id == sub_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_subscription(self, sub_id: int) -> bool:
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore
