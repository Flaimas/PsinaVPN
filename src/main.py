import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.core.config import settings
from src.bot.middlewares.middlewares import DbSessionMiddleware, InlineKeyboardsMiddleware, ShadowBanMiddleware
from src.database.connection import session_factory
from src.database.repositories.user import UserRepository
from src.bot.handlers import handlers_router
from src.bot.keyboards.main_kb import keyboards
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from src.core.logger import setup_logging
from loguru import logger



async def main():
    setup_logging() #logger

    proxy_session = None
    if settings.PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        proxy_session = AiohttpSession(proxy=settings.PROXY_URL)
        logger.info("Бот запущен с использованием прокси.") 

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
    redis_storage = RedisStorage(redis_client)

    try:
        async with session_factory() as session:
            banned_users = await UserRepository(session).get_banned_tg_user_ids()
        
        if banned_users:
            await redis_storage.delete("banned_users")
            await redis_storage.sadd("banned_users", *banned_users)
    except Exception as e:
        logger.error("Не удалось получить забаненых пользователей из базы данных.")

    dp = Dispatcher(storage=redis_storage)
    dp.update.outer_middleware(ShadowBanMiddleware(redis=redis_client))
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.message.middleware.register(InlineKeyboardsMiddleware(keyboards))
    dp.callback_query.middleware.register(InlineKeyboardsMiddleware(keyboards))
    dp.include_router(handlers_router)
    
    try:
        logger.info("Бот запущен в режиме Polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await redis_storage.close()
        logger.info("Сессия bot и redis закрыта")


if __name__ == "__main__":
    asyncio.run(main())
