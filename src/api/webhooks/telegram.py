from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, Header, HTTPException, Request, status

from src.core.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    secret_token: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
):
    if secret_token != settings.TELEGRAM_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invallid telegram token"
        )

    bot: Bot = request.app.state.bot
    dp: Dispatcher = request.app.state.dp
    json_data = await request.json()
    update = Update.model_validate(json_data, context={"bot": bot})

    await dp.feed_update(bot=bot, update=update)
    return HTTPException(status_code=status.HTTP_200_OK)
