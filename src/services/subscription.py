from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.core.enums import InvoiceOperation
from src.database.models.invoice import Invoice
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff
from src.database.models.user import User
from src.database.repositories.subscription import SubscriptionRepository

from .subscription_calculator import SubscriptionCalculator
from .vpn.client import RemnawaveClient
from .vpn.models import (
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    RemnawaveUserResponse,
    TrafficLimitStrategy,
)


@dataclass(frozen=True)
class GrantResult:
    subscription: Subscription
    converted_days: int = 0


class SubscriptionService:
    def __init__(
        self,
        vpn_client: RemnawaveClient,
        sub_repo: SubscriptionRepository,
    ) -> None:
        self.vpn_client: RemnawaveClient = vpn_client
        self.sub_repo: SubscriptionRepository = sub_repo

    async def grant_subscription_for_invoice(self, invoice: Invoice) -> GrantResult:
        if not invoice.user:
            raise ValueError(f"У инвойса {invoice.id} отсутствует пользователь")
        if not invoice.tariff:
            raise ValueError(f"У инвойса {invoice.id} отсутствует тариф")

        daily_rate = Decimal(str(invoice.amount)) / invoice.duration_days

        if invoice.operation == InvoiceOperation.BUY:
            result = await self._create_subscription(
                duration_days=invoice.duration_days,
                user=invoice.user,
                tariff=invoice.tariff,
                daily_rate=daily_rate,
            )

        elif invoice.operation == InvoiceOperation.EXTEND:
            if not invoice.subscription:
                raise ValueError(
                    f"У инвойса {invoice.id} отсутствует subscription для продления"
                )

            result = await self._extend_subscription(
                user_subscription=invoice.subscription,
                duration_days=invoice.duration_days,
                daily_rate=daily_rate,
            )

        elif invoice.operation == InvoiceOperation.CHANGE:
            if not invoice.subscription:
                raise ValueError(
                    f"У инвойса {invoice.id} отсутствует subscription для смены"
                )
            result = await self._change_tariff(
                invoice=invoice,
                user_subscription=invoice.subscription,
                duration_days=invoice.duration_days,
                new_tariff=invoice.tariff,
            )

        else:
            raise ValueError(f"Неизвестный тип операции: {invoice.operation}")

        return result

    async def _create_subscription(
        self, duration_days: int, user: User, tariff: Tariff, daily_rate: Decimal
    ) -> GrantResult:
        expire_at: datetime = datetime.now(UTC) + timedelta(days=duration_days)
        username: str = f"{user.telegram_id}_{tariff.category}"

        payload = RemnawaveCreateUserRequest(
            username=username,
            telegram_id=user.telegram_id,
            expire_at=expire_at,
            traffic_limit_bytes=(tariff.traffic_limit) * 1024**3,
            hwid_device_limit=tariff.device_limit,
            traffic_limit_strategy=TrafficLimitStrategy.MONTH,
            active_internal_squads=tariff.internal_squad_uuids,
            external_squad_uuid=tariff.external_squad_uuid,
        )
        panel_response: RemnawaveUserResponse = await self.vpn_client.create_user(
            payload
        )

        subscription = await self.sub_repo.add_subscription(
            user_id=user.id,
            tariff_id=tariff.id,
            tariff_category=tariff.category,
            sub_url=panel_response.subscription_url,
            remnawave_user_id=panel_response.id,
            expired_at=panel_response.expire_at,
            daily_rate=daily_rate,
        )
        return GrantResult(subscription=subscription)

    async def _extend_subscription(
        self, user_subscription: Subscription, duration_days: int, daily_rate: Decimal
    ) -> GrantResult:
        panel_response: RemnawaveUserResponse = (
            await self.vpn_client.extend_user_expiration_date(
                user_remnawave_id=user_subscription.remnawave_user_id,
                days=duration_days,
            )
        )

        subscription = await self.sub_repo.update_subscription(
            sub_id=user_subscription.id,
            expired_at=panel_response.expire_at,
            daily_rate=daily_rate,
        )
        return GrantResult(subscription=subscription)

    async def _change_tariff(
        self,
        invoice: Invoice,
        user_subscription: Subscription,
        duration_days: int,
        new_tariff: Tariff,
    ) -> GrantResult:
        result = SubscriptionCalculator.calculate_change_tariff(
            current_expire_at=user_subscription.expired_at,
            duration_days=duration_days,
            price=Decimal(invoice.amount),
            daily_rate=Decimal(user_subscription.daily_rate),
            now=datetime.now(UTC),
        )
        payload = RemnawaveUpdateUser(
            id=user_subscription.remnawave_user_id,
            expire_at=result.expire_at,
            hwid_device_limit=new_tariff.device_limit,
            active_internal_squads=new_tariff.internal_squad_uuids,
            external_squad_uuid=new_tariff.external_squad_uuid,
            traffic_limit_bytes=new_tariff.traffic_limit * 1024**3,
        )
        panel_response: RemnawaveUserResponse = await self.vpn_client.update_user(
            payload=payload
        )

        subscription = await self.sub_repo.update_subscription(
            sub_id=user_subscription.id,
            expired_at=panel_response.expire_at,
            tariff_id=new_tariff.id,
            daily_rate=result.daily_rate,
        )
        return GrantResult(
            subscription=subscription, converted_days=result.converted_days
        )
