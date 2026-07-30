from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis

from src.api.routes.webhooks import router as webhooks_router
from src.bot.handlers import handlers_router
from src.bot.middlewares.middlewares import (
    DbSessionMiddleware,
    InlineKeyboardsMiddleware,
    ServicesMiddleware,
    ShadowBanMiddleware,
    ValidMessageMiddleware,
)
from src.core.config import settings
from src.core.logger import setup_logging
from src.database.connection import session_factory
from src.database.repositories.user import UserRepository
from src.services.payment.providers import get_payment_providers
from src.services.vpn.client import RemnawaveClient
from src.tests.services.vpn.client import FakeRemnawaveClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    setup_logging()
    if settings.DEBUG:
        vpn_client = FakeRemnawaveClient()
    else:
        vpn_client = RemnawaveClient()

    await vpn_client.open()

    proxy_session = None
    if settings.PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession

        proxy_session = AiohttpSession(proxy=settings.PROXY_URL)
        logger.info("Бот запущен с использованием прокси.")

    bot = Bot(
        token=settings.BOT_TOKEN,
        session=proxy_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    redis_client = Redis(
        host="localhost",
        port=6379,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )
    redis_storage = RedisStorage(redis_client)

    try:
        async with session_factory() as session:
            banned_users = await UserRepository(session).get_banned_tg_user_ids()
        await redis_client.delete("banned_users")
        if banned_users:
            await redis_client.sadd("banned_users", *banned_users)

    except Exception:
        logger.error("Не удалось получить забаненых пользователей из базы данных.")

    dp = Dispatcher(storage=redis_storage)

    dp.update.outer_middleware(ShadowBanMiddleware(redis=redis_client))
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=session_factory))
    dp.update.outer_middleware(ServicesMiddleware())

    dp.callback_query.outer_middleware(ValidMessageMiddleware())

    dp.message.middleware(InlineKeyboardsMiddleware())
    dp.callback_query.middleware(InlineKeyboardsMiddleware())

    dp.include_router(handlers_router)

    app.state.vpn_client = vpn_client
    app.state.bot = bot
    app.state.dp = dp
    app.state.providers = get_payment_providers()
    telegram_web_hook_url = (
        "https://qtbmx-78-37-145-11.free.pinggy.net/webhooks/telegram"
    )
    await bot.set_webhook(
        url=telegram_web_hook_url,
        secret_token=settings.TELEGRAM_SECRET_TOKEN,
        drop_pending_updates=True,
    )
    logger.info("Вебхук для Telegram успешно установлен на {}", telegram_web_hook_url)

    yield

    logger.info("Остановка приложения...")
    await bot.delete_webhook()

    logger.info("Вебхук для Telegram удален")
    await vpn_client.close()

    await redis_storage.close()
    logger.info("Сессия bot и redis закрыта")


app = FastAPI(lifespan=lifespan)
app.include_router(webhooks_router)
