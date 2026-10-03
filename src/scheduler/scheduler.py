from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.subscription_notifications import (
    SubscriptionNotificationsRepository,
)
from src.services.notification import NotificationService

from .workers.expiry_detector import ExpiryDetectorWorker
from .workers.expiry_notifier import ExpiryNotifierWorker


class Scheduler:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        dp: Dispatcher,
        bot: Bot,
    ) -> None:
        self._session_factory: async_sessionmaker = session_factory
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._dp: Dispatcher = dp
        self._bot: Bot = bot

    @asynccontextmanager
    async def _session(self):
        async with self._session_factory() as session:
            yield session
            await session.commit()

    async def _run_detector(self) -> None:
        async with self._session() as session:
            worker = ExpiryDetectorWorker(
                session=session,
                subscription_repo=SubscriptionRepository(session),
                subscription_notifications_repo=SubscriptionNotificationsRepository(
                    session
                ),
            )
            await worker.run()

    async def _run_notify(self) -> None:
        async with self._session() as session:
            worker = ExpiryNotifierWorker(
                session=session,
                subscription_notifications_repo=SubscriptionNotificationsRepository(
                    session
                ),
                notification_service=NotificationService(bot=self._bot, dp=self._dp),
            )
            await worker.run(limit_notifications=50)

    def setup(self) -> None:
        self._scheduler.add_job(
            self._run_detector,
            "interval",
            minutes=1,
            id="expiry_detector",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        self._scheduler.add_job(
            self._run_notify,
            "interval",
            id="expiry_notifier",
            seconds=15,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )

    def start(self) -> None:
        self.setup()
        self._scheduler.start()

    def shutdown(self) -> None:
        self._scheduler.shutdown()
