import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_subscription(
        self,
        user_id: int,
        tariff_id: int,
        sub_url: str,
        sub_uuid: uuid.UUID,
        expired_at: datetime,
        is_active: bool = True,
    ) -> Subscription:

        subscription = Subscription(
            user_id=user_id,
            tariff_id=tariff_id,
            sub_uuid=sub_uuid,
            sub_url=sub_url,
            is_active=is_active,
            expired_at=expired_at,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def delete_subscription(self, sub_id: int) -> bool:
        stmt = delete(Subscription).where(Subscription.id == sub_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def update_subscription(self, sub_id: int, **kwargs):
        stmt = update(Subscription).where(Subscription.id == sub_id).values(**kwargs)
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def get_subscriptions_by_user(
        self,
        user_id: int,
        is_active: bool | None = None,
        load_user: bool = False,
        load_tariff: bool = False,
    ) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)

        if is_active is not None:
            stmt = stmt.where(Subscription.is_active == is_active)

        if load_tariff:
            stmt = stmt.options(joinedload(Subscription.tariff))

        if load_user:
            stmt = stmt.options(joinedload(Subscription.user))

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def deactivate_subscription(self, sub_id: int) -> bool:
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore
