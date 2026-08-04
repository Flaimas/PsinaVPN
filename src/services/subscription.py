from datetime import UTC, datetime, timedelta

from src.core.enums import InvoiceOperation
from src.database.models.invoice import Invoice
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff
from src.database.models.user import User
from src.database.repositories.subscription import SubscriptionRepository

from .vpn.client import RemnawaveClient
from .vpn.models import (
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    TrafficLimitStrategy,
)


class SubscriptionService:
    def __init__(
        self,
        vpn_client: RemnawaveClient,
        sub_repo: SubscriptionRepository,
    ) -> None:
        self.vpn_client = vpn_client
        self.sub_repo = sub_repo

    async def grant_subscription_for_invoice(self, invoice: Invoice) -> Subscription:
        if not invoice.user:
            raise ValueError(f"У инвойса {invoice.id} отсутствует пользователь")
        if not invoice.tariff:
            raise ValueError(f"У инвойса {invoice.id} отсутствует тариф")

        if invoice.operation == InvoiceOperation.BUY:
            return await self._create_subscription(
                duration_days=invoice.duration_days,
                user=invoice.user,
                tariff=invoice.tariff,
            )

        elif invoice.operation == InvoiceOperation.EXTEND:
            if not invoice.subscription:
                raise ValueError(
                    f"У инвойса {invoice.id} отсутствует subscription для продления"
                )

            return await self._extend_subscription(
                user_subscription=invoice.subscription,
                duration_days=invoice.duration_days,
                tariff=invoice.tariff,
            )

        elif invoice.operation == InvoiceOperation.CHANGE:
            if not invoice.subscription:
                raise ValueError(
                    f"У инвойса {invoice.id} отсутствует subscription для смены"
                )
            return await self._change_tariff(
                user_subscription=invoice.subscription,
                duration_days=invoice.duration_days,
                new_tariff=invoice.tariff,
            )

        else:
            raise ValueError(f"Неизвестный тип операции: {invoice.operation}")

    async def _create_subscription(
        self, duration_days: int, user: User, tariff: Tariff
    ) -> Subscription:
        expire_at = datetime.now(UTC) + timedelta(days=duration_days)
        username = f"{user.telegram_id}_{tariff.category}"

        payload = RemnawaveCreateUserRequest(
            username=username,
            telegram_id=user.telegram_id,
            expire_at=expire_at,
            traffic_limit_bytes=tariff.traffic_limit,
            traffic_limit_strategy=TrafficLimitStrategy.MONTH,
            active_internal_squads=tariff.squad_uuids,
        )
        panel_response = await self.vpn_client.create_user(payload)

        return await self.sub_repo.add_subscription(
            user_id=user.id,
            tariff_id=tariff.id,
            tariff_category=tariff.category,
            sub_url=panel_response.subscription_url,
            remnawave_user_id=panel_response.id,
            expired_at=panel_response.expire_at,
            squad_uuids=tariff.squad_uuids,
        )

    async def _extend_subscription(
        self, user_subscription: Subscription, duration_days: int, tariff: Tariff
    ) -> Subscription:
        now = datetime.now(UTC)
        base_date = max(now, user_subscription.expired_at)
        expired_at = base_date + timedelta(days=duration_days)

        payload = RemnawaveUpdateUser(
            id=user_subscription.remnawave_user_id,
            expire_at=expired_at,
            traffic_limit_bytes=tariff.traffic_limit,
        )
        panel_response = await self.vpn_client.update_user(payload=payload)

        return await self.sub_repo.update_expired_at_subscription(
            sub_id=user_subscription.id, new_expired_at=panel_response.expire_at
        )

    async def _change_tariff(
        self, user_subscription: Subscription, duration_days: int, new_tariff: Tariff
    ):
        expired_at = datetime.now(UTC) + timedelta(days=duration_days)
        payload = RemnawaveUpdateUser(
            id=user_subscription.remnawave_user_id,
            expire_at=expired_at,
            active_internal_squads=new_tariff.squad_uuids,
            traffic_limit_bytes=new_tariff.traffic_limit,
        )
        panel_response = await self.vpn_client.update_user(payload=payload)
        return await self.sub_repo.update_expired_at_subscription(
            sub_id=user_subscription.id,
            new_expired_at=panel_response.expire_at,
            tariff_id=new_tariff.id,
            squad_uuids=new_tariff.squad_uuids,
        )
