from datetime import UTC, datetime, timedelta

from loguru import logger

from src.core.enums import InvoiceOperation
from src.database.models.subscription import Subscription
from src.database.models.user import User
from src.database.repositories.invoice import InvoiceRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.services.notification import NotificationService

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
        notifier: NotificationService,
    ) -> None:
        self.vpn_client = vpn_client
        self.sub_repo = sub_repo
        self.invoice_repo = invoice_repo
        self.notifier = notifier

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
            user_sub = await self._create_subscription(
                duration_days=user_invoice.duration_days,
                user=user_invoice.user,
                tariff_id=user_invoice.tariff_id,
            )

        elif user_invoice.operation == InvoiceOperation.EXTEND:
            if not user_invoice.subscription:
                raise ValueError("У инвойса отсуствует переменная subscription")

            user_sub = await self._extend_subscription(
                user_subscription=user_invoice.subscription,
                duration_days=user_invoice.duration_days,
            )

        else:
            logger.error(
                f"Неизвестный тип операции с инвойсом: operation={user_invoice.operation}"
            )
            raise ValueError("Неизвестный тип операции.")

        user_taiff = user_invoice.tariff if user_invoice.tariff else None
        await self.notifier.notify_payment_success(
            telegram_id=user_invoice.user.telegram_id,
            operation=user_invoice.operation,
            user_sub=user_sub,
            user_tariff=user_taiff,
        )
        return True

    async def _create_subscription(
        self, duration_days: int, user: User, tariff_id: int
    ) -> Subscription:
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
        return subscription_add_db

    async def _extend_subscription(
        self, user_subscription: Subscription, duration_days: int
    ) -> Subscription:
        now = datetime.now(UTC)
        base_date = max(now, user_subscription.expired_at)
        expired_at = base_date + timedelta(days=duration_days)

        payload = RemnawaveUpdateUser(
            uuid=user_subscription.sub_uuid, expire_at=expired_at
        )
        panel_response = await self.vpn_client.update_user(payload=payload)

        subscription_update_db = await self.sub_repo.update_expired_at_subscription(
            sub_id=user_subscription.id, new_expired_at=panel_response.expire_at
        )
        return subscription_update_db
