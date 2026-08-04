from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.enums import PaymentStatus
from src.database.models.invoice import Invoice
from src.scheams.tariff import CreateInvoiceDTO


class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_invoice(self, invoice_dto: CreateInvoiceDTO) -> Invoice:
        query = insert(Invoice).values(**invoice_dto.model_dump()).returning(Invoice)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def mark_as_paid_if_pending(self, provider_payment_id: str) -> Invoice | None:
        stmt = (
            update(Invoice)
            .where(
                Invoice.provider_payment_id == provider_payment_id,
                Invoice.status == PaymentStatus.PENDING,
            )
            .values(status=PaymentStatus.PAID)
            .returning(Invoice)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_subscription_id(self, invoice_id: int, sub_id: int) -> None:
        stmt = (
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(subscription_id=sub_id)
        )
        await self.session.execute(stmt)

    async def get_with_relations(self, invoice_id: int) -> Invoice:
        query = (
            select(Invoice)
            .where(Invoice.id == invoice_id)
            .options(joinedload(Invoice.tariff))
            .options(joinedload(Invoice.user))
            .options(joinedload(Invoice.subscription))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one()
