from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import NotificationStatus, StageNotification
from src.database.models.subscription import Subscription
from src.database.models.subscription_notifications import SubscriptionNotification


class SubscriptionNotificationsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def enqueue_many(
        self, subscriptions_with_user: list[Subscription], stage: StageNotification
    ) -> list[SubscriptionNotification]:
        if not subscriptions_with_user:
            return []
        stmt = (
            pg_insert(SubscriptionNotification)
            .values(
                [
                    {
                        "telegram_id": sub.user.telegram_id,
                        "subscription_id": sub.id,
                        "stage": stage,
                        "expired_at": sub.expired_at,
                    }
                    for sub in subscriptions_with_user
                ]
            )
            .on_conflict_do_nothing()
        ).returning(SubscriptionNotification)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_notifications(
        self, limit: int
    ) -> list[SubscriptionNotification]:
        subquery = (
            select(SubscriptionNotification.id)
            .where(SubscriptionNotification.status == NotificationStatus.PENDING)
            .order_by(SubscriptionNotification.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        ).scalar_subquery()

        stmt = (
            update(SubscriptionNotification)
            .where(SubscriptionNotification.id.in_(subquery))
            .values(status=NotificationStatus.SENDING)
            .returning(SubscriptionNotification)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_notify_many(
        self,
        ids: list[int],
        status: NotificationStatus,
        attempts_inc: bool = False,
        sent_at: datetime | None = None,
    ) -> None:
        stmt = (
            update(SubscriptionNotification)
            .where(SubscriptionNotification.id.in_(ids))
            .values(
                status=status,
                attempts=(
                    SubscriptionNotification.attempts + 1
                    if attempts_inc
                    else SubscriptionNotification.attempts
                ),
                sent_at=sent_at,
            )
        )
        await self.session.execute(stmt)
