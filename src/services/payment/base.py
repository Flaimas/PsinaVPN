from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentInvoiceResult:
    invoice_id: int
    pay_url: str
    payload: dict | None = None


class BasePaymentProvider:
    """Абстрактрый класс для всех платежных провайдеров"""

    @abstractmethod
    async def create_payment(
        self, amount: float, description: str, user_id: int, **kwargs
    ) -> PaymentInvoiceResult:
        """Создать счет и получить ссылку на оплату"""

    async def check_payment(self, payment_id: str):
        """Проверяет подлинность вебхука, статус платежа"""
