from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.keyboards import InlineKB
from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.tariff import TariffRepository
from src.database.repositories.user import UserRepository
from src.services.payment.payment import PaymentService
from src.services.payment.providers import get_payment_providers
from src.services.tariff import TariffService


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            try:
                data["db_session"] = session
                result = await handler(event, data)
                await session.commit()
                return result

            except Exception as e:
                await session.rollback()
                raise e


class ServicesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session = data["db_session"]

        user_repo = UserRepository(session)
        tariff_repo = TariffRepository(session)
        sub_repo = SubscriptionRepository(session)
        ivoice_repo = InvoiceRepository(session)

        tariff_service = TariffService()
        payment_service = PaymentService(
            invoice_repo=ivoice_repo,
            providers=get_payment_providers(),
        )

        data["tariff_service"] = tariff_service
        data["payment_service"] = payment_service
        data["tariff_repo"] = tariff_repo
        data["user_repo"] = user_repo
        data["sub_repo"] = sub_repo

        return await handler(event, data)


class InlineKeyboardsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        data["kb"] = InlineKB()
        return await handler(event, data)


class ShadowBanMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        user: User | None = data.get("event_from_user")
        if user is not None:
            is_banned = await self.redis.sismember("banned_users", str(user.id))
            if is_banned:
                return

        return await handler(event, data)


class ValidMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event.message, Message):
            await event.answer(
                "Сообщение устарело или недоступно.\nПерезагрузите бота командой /start",
                show_alert=True,
            )
            return

        return await handler(event, data)
