from src.core.enums import InvoiceOperation, PaymentProvider
from src.database.models.invoice import Invoice
from src.database.repositories.invoice import InvoiceRepository
from src.scheams.tariff import CreateInvoiceDTO
from src.services.payment.base import BasePaymentProvider
from src.services.payment.exceptions import PaymentProviderUnavailableError


class PaymentService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        providers: dict[PaymentProvider, BasePaymentProvider],
    ):
        self.invoice_repo = invoice_repo
        self._providers = providers

    def _get_provider(self, provider_type: PaymentProvider):
        provider = self._providers.get(provider_type)
        if not provider:
            raise PaymentProviderUnavailableError("Ошибка, провайдер не обслуживается!")
        return provider

    async def create_invoice(
        self,
        provider_type: PaymentProvider,
        amount: float,
        period: int,
        description: str,
        user_id: int,
        tariff_id: int,
        operation: InvoiceOperation,
        subscription_id: int | None = None,
    ) -> tuple[Invoice, str]:

        provider = self._get_provider(provider_type)

        payment_data = await provider.create_payment(
            amount=amount, description=description, user_id=user_id
        )

        invoice_dto = CreateInvoiceDTO(
            user_id=user_id,
            duration_days=period,
            tariff_id=tariff_id,
            provider=provider_type,
            provider_payment_id=str(payment_data.invoice_id),
            amount=amount,
            operation=operation,
            subscription_id=subscription_id,
        )

        return await self.invoice_repo.add_invoice(invoice_dto), payment_data.pay_url
