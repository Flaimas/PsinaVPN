import asyncio
import uuid

from loguru import logger
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError
from yookassa.domain.response import PaymentResponse as YooKassaResponse

from src.services.payment.exceptions import PaymentServiceError

from .base import BasePaymentProvider, PaymentInvoiceResult


class YooKassaProvider(BasePaymentProvider):
    def __init__(self, shop_id: str, secret_key: str) -> None:
        Configuration.configure(shop_id, secret_key)
        self.return_url = "https://www.example.com/return_url"

    async def create_payment(
        self, amount: float, description: str, user_id: int, **kwargs
    ):
        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": self.return_url},
            "capture": True,
            "description": f"{description}",
            "metadata": {"user_id": f"{user_id}"},
        }

        try:
            payment: YooKassaResponse = await asyncio.to_thread(
                Payment.create, payload, uuid.uuid4()
            )
        except ApiError as e:
            logger.error(
                "[YooKassa] Ошибка API при создании платежа для user_id:{}: {}",
                user_id,
                e,
            )
            raise PaymentServiceError(
                "Ошибка на стороне платежной системы YooKassa"
            ) from e
        except (OSError, TimeoutError) as e:
            logger.error("[YooKass] Непредвиденная ошибка сети/сервера:{}", e)
            raise PaymentServiceError("Сервис оплаты веременно недоступен") from e

        return PaymentInvoiceResult(
            invoice_id=payment.id,  # type: ignore
            pay_url=payment.confirmation.confirmation_url,  # type: ignore
        )

    async def check_payment(self, payment_id: str) -> bool:
        payment_info = await asyncio.to_thread(Payment.find_one, payment_id)
        return payment_info.status == "succeeded"
