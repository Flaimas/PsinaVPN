import asyncio
from datetime import UTC, datetime

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import NotificationStatus
from src.database.repositories.subscription_notifications import (
    SubscriptionNotificationsRepository,
)
from src.services.notification import NotificationService


class ExpiryNotifierWorker:
    def __init__(
        self,
        session: AsyncSession,
        subscription_notifications_repo: SubscriptionNotificationsRepository,
        notification_service: NotificationService,
    ) -> None:
        self.session: AsyncSession = session
        self.subscription_notifications_repo: SubscriptionNotificationsRepository = (
            subscription_notifications_repo
        )
        self.notification_service: NotificationService = notification_service

    async def run(self, limit_notifications: int):
        batch = await self.subscription_notifications_repo.get_pending_notifications(
            limit=limit_notifications
        )
        items = [(n.id, n.telegram_id, n.expired_at) for n in batch]
        await self.session.commit()
        if not items:
            return
        sent: list[int] = []
        failed: list[int] = []
        retry: list[int] = []
        try:
            for id_, telegram_id, expire_at in items:
                try:
                    await self.notification_service.notify_subscription_expire(
                        telegram_id=telegram_id, expire_at=expire_at
                    )
                    sent.append(id_)
                except TelegramRetryAfter as e:
                    retry.append(id_)
                    await asyncio.sleep(e.retry_after)
                except TelegramForbiddenError, TelegramBadRequest:
                    failed.append(id_)
                except Exception:
                    logger.exception(f"notify failed id={id_}")

        finally:
            await asyncio.shield(self._save_result(sent, failed, retry))

    async def _save_result(self, sent: list[int], failed: list[int], retry: list[int]):
        if sent:
            await self.subscription_notifications_repo.mark_notify_many(
                ids=sent, status=NotificationStatus.SENT, sent_at=datetime.now(UTC)
            )
        if failed:
            await self.subscription_notifications_repo.mark_notify_many(
                ids=sent, status=NotificationStatus.FAILED
            )
        if retry:
            await self.subscription_notifications_repo.mark_notify_many(
                ids=sent, status=NotificationStatus.PENDING, attempts_inc=True
            )
        await self.session.commit()
