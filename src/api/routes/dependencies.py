from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.enums import PaymentProvider
from src.database.connection import get_session
from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.services.payment.base import BasePaymentProvider
from src.services.payment.payment import PaymentService
from src.services.payment.providers import get_payment_providers
from src.services.payment.yookassa import YooKassaProvider
from src.services.vpn.client import RemnawaveClient
from src.services.vpn.subscription import SubscriptionService


def get_yookassa_provider() -> YooKassaProvider:
    return YooKassaProvider(
        shop_id=settings.YOOKASSA_SHOP_ID, secret_key=settings.YOOKASSA_SECRET_KEY
    )


def get_payment_service(
    session: AsyncSession = Depends(get_session),
    providers: dict[PaymentProvider, BasePaymentProvider] = Depends(
        get_payment_providers
    ),
):
    return PaymentService(
        invoice_repo=InvoiceRepository(session=session), providers=providers
    )


def get_vpn_client(request: Request) -> RemnawaveClient:
    """Достаёт RemnawaveClient из app.state текущего приложения."""
    return request.app.state.vpn_client


def get_subscription_service(
    session: AsyncSession = Depends(get_session),
    vpn_client: RemnawaveClient = Depends(get_vpn_client),
):
    return SubscriptionService(
        vpn_client=vpn_client,
        sub_repo=SubscriptionRepository(session),
        invoice_repo=InvoiceRepository(session),
    )
