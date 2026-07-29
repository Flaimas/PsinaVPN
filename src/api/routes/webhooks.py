from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from src.core.config import settings
from src.services.payment.payment import PaymentService
from src.services.payment.yookassa import YooKassaProvider
from src.services.vpn.subscription import SubscriptionService

from .dependencies import (
    get_payment_service,
    get_subscription_service,
    get_yookassa_provider,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    yookassa_provider: YooKassaProvider = Depends(get_yookassa_provider),
    sub_service: SubscriptionService = Depends(get_subscription_service),
):
    body = await request.json()
    payment_id = body.get("object", {}).get("id")
    payment_status = body.get("object", {}).get("status")

    if not payment_id or payment_status != "succeeded":
        return {"status": "ignored"}

    check_payment = await yookassa_provider.check_payment(payment_id)
    if not check_payment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    order = await payment_service.successful_payment_process(payment_id)
    if not order:
        return {"status": "ok"}

    await sub_service.issue_subscription(order.id)


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
