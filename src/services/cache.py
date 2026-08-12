from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.database.repositories.user import UserRepository


async def warm_up_banned_users_cache(
    redis_client: Redis, session_factory: async_sessionmaker
):
    try:
        async with session_factory() as session:
            banned_users = await UserRepository(session).get_banned_tg_user_ids()
        await redis_client.delete("banned_users")
        if banned_users:
            await redis_client.sadd("banned_users", *banned_users)

    except Exception:
        logger.error("Не удалось получить забаненых пользователей из базы данных.")
