import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis

from src.api.webhooks.telegram import router as telegram_webhook
from src.api.webhooks.yookassa import router as yookassa_webhook
from src.bot.factory import create_bot, create_dispatcher
from src.core.config import settings
from src.core.logger import setup_logging
from src.database.connection import session_factory
from src.services.cache import warm_up_banned_users_cache
from src.services.payment.providers import get_payment_providers
from src.services.vpn.client import RemnawaveClient
from src.tests.services.vpn.client import FakeRemnawaveClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    vpn_client = FakeRemnawaveClient() if settings.DEBUG else RemnawaveClient()
    await vpn_client.open()

    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    bot = create_bot()
    dp = create_dispatcher(redis_client, session_factory)

    await warm_up_banned_users_cache(redis_client, session_factory)

    app.state.vpn_client = vpn_client
    app.state.bot = bot
    app.state.dp = dp
    app.state.providers = get_payment_providers()

    if settings.USE_WEBHOOK:
        await bot.set_webhook(
            url=settings.telegram_web_hook_url,
            secret_token=settings.TELEGRAM_SECRET_TOKEN,
            drop_pending_updates=True,
        )
        logger.info(
            "Вебхук для Telegram успешно установлен на {}",
            settings.telegram_web_hook_url,
        )
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        logger.info("Бот запущен в режиме Long Polling")

    yield

    logger.info("Остановка приложения...")

    if settings.USE_WEBHOOK:
        await bot.delete_webhook()
        logger.info("Вебхук для Telegram удален")
    elif "polling_task" in locals():
        polling_task.cancel()
        logger.info("Long Polling остановлен")

    await bot.session.close()
    logger.info("Сессия бота закрыта")

    await vpn_client.close()
    logger.info("Сессия VPN клиента закрыта")

    await redis_client.aclose()
    logger.info("Сессия redis закрыта")


app = FastAPI(lifespan=lifespan)
app.include_router(yookassa_webhook)

if settings.USE_WEBHOOK:
    app.include_router(telegram_webhook)


def main():
    uvicorn.run(
        "src.main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
