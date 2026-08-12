from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.database.connection import get_session
from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.services.notification import NotificationService
from src.services.payment.yookassa import YooKassaProvider
from src.services.payment_processor import ProcessPaymentUseCase
from src.services.subscription import SubscriptionService
from src.services.vpn.client import RemnawaveClient


def get_yookassa_provider() -> YooKassaProvider:
    return YooKassaProvider(
        shop_id=settings.YOOKASSA_SHOP_ID, secret_key=settings.YOOKASSA_SECRET_KEY
    )


def get_vpn_client(request: Request) -> RemnawaveClient:
    """Достаёт RemnawaveClient из app.state текущего приложения."""
    return request.app.state.vpn_client


def get_notifier(request: Request):
    bot = request.app.state.bot
    dp = request.app.state.dp
    return NotificationService(bot=bot, dp=dp)


def get_payment_process(
    session: AsyncSession = Depends(get_session),
    vpn_client: RemnawaveClient = Depends(get_vpn_client),
    notifier: NotificationService = Depends(get_notifier),
) -> ProcessPaymentUseCase:
    sub_repo = SubscriptionRepository(session=session)
    invoice_repo = InvoiceRepository(session=session)

    subscription_service = SubscriptionService(
        vpn_client=vpn_client,
        sub_repo=sub_repo,
    )

    return ProcessPaymentUseCase(
        session=session,
        invoice_repo=invoice_repo,
        subscription_service=subscription_service,
        notifier=notifier,
    )
