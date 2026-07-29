from datetime import UTC, datetime, timedelta

from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository

from .client import RemnawaveClient
from .models import RemnawaveCreateUserRequest, TrafficLimitStrategy


class SubscriptionService:
    def __init__(
        self,
        vpn_client: RemnawaveClient,
        sub_repo: SubscriptionRepository,
        invoice_repo: InvoiceRepository,
    ) -> None:
        self.vpn_client = vpn_client
        self.sub_repo = sub_repo
        self.invoice_repo = invoice_repo

    async def issue_subscription(self, invoice_id: int) -> bool:
        user_invoice = await self.invoice_repo.get_with_relations(invoice_id=invoice_id)

        if not user_invoice:
            raise ValueError(f"Инвойса с id={invoice_id} нет в базе данных.")

        expire_at = datetime.now(UTC) + timedelta(days=user_invoice.duration_days)
        username = (
            user_invoice.user.username
            if user_invoice.user.username
            else f"user_id:{user_invoice.user.id}"
        )
        payload = RemnawaveCreateUserRequest(
            username=username,
            telegram_id=user_invoice.user.telegram_id,
            expire_at=expire_at,
            traffic_limit_bytes=90000,
            traffic_limit_strategy=TrafficLimitStrategy.MONTH_ROLLING,
        )
        panel_response = await self.vpn_client.create_user(payload)
        result = await self.sub_repo.add_subscription(
            user_id=user_invoice.user.id,
            tariff_id=user_invoice.tariff_id,
            sub_url=panel_response.subscription_url,
            sub_uuid=panel_response.uuid,
            expired_at=panel_response.expire_at,
        )
        return bool(result)
