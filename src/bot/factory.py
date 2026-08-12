from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.handlers import handlers_router
from src.bot.middlewares.middlewares import (
    DbSessionMiddleware,
    InlineKeyboardsMiddleware,
    ServicesMiddleware,
    ShadowBanMiddleware,
    ValidMessageMiddleware,
)
from src.core.config import settings


def create_bot() -> Bot:
    proxy_session = None
    if settings.PROXY_URL:
        proxy_session = AiohttpSession(proxy=settings.PROXY_URL)
        logger.info("Бот запущен с использованием прокси.")

    return Bot(
        token=settings.BOT_TOKEN,
        session=proxy_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(
    redis_client: Redis, session_factory: async_sessionmaker
) -> Dispatcher:
    dp = Dispatcher(storage=RedisStorage(redis_client))
    dp.update.outer_middleware(ShadowBanMiddleware(redis=redis_client))
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=session_factory))
    dp.update.outer_middleware(ServicesMiddleware())

    dp.callback_query.outer_middleware(ValidMessageMiddleware())

    dp.message.middleware(InlineKeyboardsMiddleware())
    dp.callback_query.middleware(InlineKeyboardsMiddleware())

    dp.include_router(handlers_router)
    return dp
