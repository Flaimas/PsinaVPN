from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from types import MappingProxyType

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import StageNotification
from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.subscription_notifications import (
    SubscriptionNotificationsRepository,
)


class ExpiryDetectorWorker:
    PERIODS: MappingProxyType[
        StageNotification, Callable[[datetime], tuple[datetime, datetime]]
    ] = MappingProxyType(
        {
            StageNotification.EXPIRING_3D: lambda now: (
                now + timedelta(days=2),
                now + timedelta(days=3),
            ),
            StageNotification.EXPIRING_2D: lambda now: (
                now + timedelta(days=1),
                now + timedelta(days=2),
            ),
            StageNotification.EXPIRING_1D: lambda now: (
                now,
                now + timedelta(days=1),
            ),
        }
    )

    def __init__(
        self,
        session: AsyncSession,
        subscription_repo: SubscriptionRepository,
        subscription_notifications_repo: SubscriptionNotificationsRepository,
    ) -> None:
        self.session: AsyncSession = session
        self.subscription_repo: SubscriptionRepository = subscription_repo
        self.subscription_notifications_repo: SubscriptionNotificationsRepository = (
            subscription_notifications_repo
        )

    async def run(self):
        now = datetime.now(UTC)
        for stage, limits_fn in self.PERIODS.items():
            lower_limit, upper_limit = limits_fn(now)
            subs = await self.subscription_repo.find_pending_notification_subscriptions_with_user_relation(
                stage=stage, lower_limit=lower_limit, upper_limit=upper_limit
            )
            if not subs:
                continue
            sending_subs = await self.subscription_notifications_repo.enqueue_many(
                subscriptions_with_user=subs, stage=stage
            )
            if not sending_subs:
                continue
            logger.info(
                f"Очередь: {len(sending_subs)}/{len(subs)}, notifications stage={stage}"
            )
