from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class TariffChangeResult:
    expire_at: datetime
    converted_days: int
    daily_rate: Decimal


class SubscriptionCalculator:
    @staticmethod
    def calculate_change_tariff(
        current_expire_at: datetime,
        duration_days: int,
        price: Decimal,
        daily_rate: Decimal,
        now: datetime,
    ) -> TariffChangeResult:
        if duration_days <= 0:
            raise ValueError("duration_days должно быть положительным")

        new_rate = price / duration_days
        seconds_left = int((current_expire_at - now).total_seconds())
        remaining_days = Decimal(seconds_left) / Decimal(86400)

        converted = 0
        if new_rate > 0 and remaining_days >= 0:
            credit = remaining_days * daily_rate
            converted = int(credit / new_rate)

        total_days = duration_days + converted
        return TariffChangeResult(
            expire_at=now + timedelta(days=total_days),
            converted_days=converted,
            daily_rate=new_rate,
        )
