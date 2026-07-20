import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.core.config import settings
from src.bot.middlewares.middlewares import DbSessionMiddleware, InlineKeyboardsMiddleware
from src.database.connection import session_factory
from src.bot.handlers import handlers_router
from src.bot.keyboards.main_kb import keyboards
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

async def main():
    proxy_session = None
    if settings.PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        proxy_session = AiohttpSession(proxy=settings.PROXY_URL) 

    bot = Bot(
        token=settings.BOT_TOKEN, 
        session=proxy_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    redis_client = Redis(
        host="localhost", 
        port=6379,
        password=settings.REDIS_PASSWORD, 
        decode_responses=True
    )
    storage = RedisStorage(redis_client)

    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.message.middleware.register(InlineKeyboardsMiddleware(keyboards))
    dp.callback_query.middleware.register(InlineKeyboardsMiddleware(keyboards))
    dp.include_router(handlers_router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
