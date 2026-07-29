from functools import cache

from src.core.config import settings
from src.core.enums import PaymentProvider

from .base import BasePaymentProvider
from .yookassa import YooKassaProvider


@cache
def get_payment_providers() -> dict[PaymentProvider, BasePaymentProvider]:
    return {
        PaymentProvider.YOOKASSA: YooKassaProvider(
            shop_id=settings.YOOKASSA_SHOP_ID, secret_key=settings.YOOKASSA_SECRET_KEY
        ),
    }
