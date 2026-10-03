from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from src.core.enums import StageNotification, TariffCategory
from src.database.models.subscription import Subscription
from src.database.models.subscription_notifications import SubscriptionNotification
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
        daily_rate: Decimal,
        tariff_category: TariffCategory,
    ) -> Subscription:

        subscription = Subscription(
            user_id=user_id,
            tariff_id=tariff_id,
            tariff_category=tariff_category,
            remnawave_user_id=remnawave_user_id,
            sub_url=sub_url,
            expired_at=expired_at,
            daily_rate=daily_rate,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def delete_subscription(self, sub_id: int) -> bool:
        stmt = delete(Subscription).where(Subscription.id == sub_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def update_subscription(self, sub_id: int, **kwargs) -> Subscription:
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(**kwargs)
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

    async def get_by_tg_id_with_relations(
        self, telegram_id: int
    ) -> Subscription | None:
        stmt = (
            select(Subscription)
            .join(User)
            .where(User.telegram_id == telegram_id)
            .options(
                contains_eager(Subscription.user), selectinload(Subscription.tariff)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tg_id(self, telegram_id: int) -> Subscription | None:
        stmt = select(Subscription).join(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

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

    async def find_pending_notification_subscriptions_with_user_relation(
        self,
        stage: StageNotification,
        lower_limit: datetime,
        upper_limit: datetime,
    ) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .outerjoin(
                SubscriptionNotification,
                (SubscriptionNotification.subscription_id == Subscription.id)
                & (SubscriptionNotification.stage == stage)
                & (SubscriptionNotification.expired_at == Subscription.expired_at),
            )
            .where(
                SubscriptionNotification.id.is_(None),
                Subscription.expired_at > lower_limit,
                Subscription.expired_at <= upper_limit,
            )
            .options(selectinload(Subscription.user))
            .order_by(Subscription.expired_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
