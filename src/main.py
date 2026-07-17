import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.core.config import settings
from src.bot.middlewares.middlewares import DbSessionMiddleware
from src.database.connection import session_factory
from src.services.vpn.mock import MockVPNClient
from src.services.vpn.base import BaseVPNClient
from src.database.repositories.user import UserRepository

async def main():
    proxy_session = None
    if settings.PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        proxy_session = AiohttpSession(proxy=settings.PROXY_URL) 

    bot = Bot(token=settings.BOT_TOKEN, session=proxy_session)
    dp = Dispatcher()
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))

    vpn_client: BaseVPNClient = MockVPNClient()

    @dp.message(CommandStart())
    async def cmd_start(message: Message, user_repo: UserRepository):
        user = await user_repo.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )

        vpn_key = await vpn_client.create_user(telegram_id=message.from_user.id)

        await message.answer(
            f"Привет, {user.username or 'друг'}!\n"
            f"Ты успешно зарегистрирован. Твой баланс: {user.balance} руб.\n\n"
            f"Твой тестовый VPN-ключ:\n<code>{vpn_key}</code>",
            parse_mode="HTML"
        )
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
