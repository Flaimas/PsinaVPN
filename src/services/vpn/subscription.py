from datetime import UTC, datetime, timedelta

from loguru import logger

from src.core.enums import InvoiceOperation
from src.database.models.subscription import Subscription
from src.database.models.user import User
from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository

from .client import RemnawaveClient
from .models import (
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    TrafficLimitStrategy,
)


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

    async def grant_subscription_for_invoice(self, invoice_id: int) -> bool:
        user_invoice = await self.invoice_repo.get_with_relations(invoice_id=invoice_id)

        if not user_invoice:
            logger.error("Инвойса с id={invoice_id} нет в базе данных", invoice_id)
            raise ValueError(f"Инвойса с id={invoice_id} нет в базе данных.")

        if not user_invoice.user:
            logger.error(
                "Приобретена подписка для несуществубщего пользователя! ivoice_id={}",
                invoice_id,
            )
            raise ValueError("Приобретена подписка для несуществубщего пользователя!")

        if not user_invoice.tariff_id:
            logger.error("Инвойс ссылается на несуществующий тариф. (tairff_id)")
            raise ValueError("Инвойс ссылается на несуществующий тариф.")

        if user_invoice.operation == InvoiceOperation.BUY:
            return await self._create_subscription(
                duration_days=user_invoice.duration_days,
                user=user_invoice.user,
                tariff_id=user_invoice.tariff_id,
            )

        if user_invoice.operation == InvoiceOperation.EXTEND:
            if not user_invoice.subscription:
                raise ValueError("У инвойса отсуствует переменная subscription")
            return await self._extend_subscription(
                user_subscription=user_invoice.subscription,
                duration_days=user_invoice.duration_days,
            )

        raise ValueError("Неизвестная ошибка при обработке платежа")

    async def _create_subscription(
        self, duration_days: int, user: User, tariff_id: int
    ):
        expire_at = datetime.now(UTC) + timedelta(days=duration_days)
        username = user.username if user.username else f"user_id:{user.id}"

        payload = RemnawaveCreateUserRequest(
            username=username,
            telegram_id=user.telegram_id,
            expire_at=expire_at,
            traffic_limit_bytes=200000,
            traffic_limit_strategy=TrafficLimitStrategy.MONTH_ROLLING,
        )
        panel_response = await self.vpn_client.create_user(payload)

        subscription_add_db = await self.sub_repo.add_subscription(
            user_id=user.id,
            tariff_id=tariff_id,
            sub_url=panel_response.subscription_url,
            sub_uuid=panel_response.uuid,
            expired_at=panel_response.expire_at,
        )
        return bool(subscription_add_db)

    async def _extend_subscription(
        self, user_subscription: Subscription, duration_days: int
    ):
        now = datetime.now(UTC)
        base_date = max(now, user_subscription.expired_at)
        expired_at = base_date + timedelta(days=duration_days)

        payload = RemnawaveUpdateUser(
            uuid=user_subscription.sub_uuid, expire_at=expired_at
        )
        panel_response = await self.vpn_client.update_user(payload=payload)
        subscription_update_db = await self.sub_repo.update_subscription(
            sub_id=user_subscription.id, expired_at=panel_response.expire_at
        )
        return bool(subscription_update_db)
