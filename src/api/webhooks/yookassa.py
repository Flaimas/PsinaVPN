from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.services.payment.yookassa import YooKassaProvider
from src.services.payment_processor import ProcessPaymentUseCase

from .dependencies import get_payment_process, get_yookassa_provider

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(
    request: Request,
    yookassa_provider: YooKassaProvider = Depends(get_yookassa_provider),
    payment_process: ProcessPaymentUseCase = Depends(get_payment_process),
):
    body = await request.json()
    payment_id = body.get("object", {}).get("id")
    payment_status = body.get("object", {}).get("status")

    if not payment_id or payment_status != "succeeded":
        return {"status": "ignored"}

    check_payment = await yookassa_provider.check_payment(payment_id)
    if not check_payment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await payment_process.execute(provider_payment_id=payment_id)
    return {"status": "ok"}
