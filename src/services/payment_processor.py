from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.invoice import InvoiceRepository
from src.services.notification import NotificationService
from src.services.subscription import SubscriptionService


class ProcessPaymentUseCase:
    def __init__(
        self,
        session: AsyncSession,
        invoice_repo: InvoiceRepository,
        subscription_service: SubscriptionService,
        notifier: NotificationService,
    ) -> None:
        self.session = session
        self.invoice_repo = invoice_repo
        self.subscriprion_service = subscription_service
        self.notifier = notifier

    async def execute(self, provider_payment_id: str) -> bool:
        async with self.session.begin_nested():
            updated_invoice = await self.invoice_repo.mark_as_paid_if_pending(
                provider_payment_id=provider_payment_id
            )
            if not updated_invoice:
                return False

            invoice = await self.invoice_repo.get_with_relations(
                invoice_id=updated_invoice.id
            )
            user_sub = await self.subscriprion_service.grant_subscription_for_invoice(
                invoice=invoice
            )
            invoice.subscription_id = user_sub.id

        await self.notifier.notify_payment_success(
            telegram_id=user_sub.user.telegram_id,
            operation=updated_invoice.operation,
            user_sub=user_sub,
            user_tariff=updated_invoice.tariff,
        )
        return True
