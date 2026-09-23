from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.services.subscription_calculator import (
    SubscriptionCalculator,
)

NOW = datetime(2026, 10, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    "days_left, old_rate, price, duration_days, converted, total_days",
    [
        pytest.param(10, "5", 300, 30, 5, 35, id="basic-conversion"),
        pytest.param(10, "4", 900, 30, 1, 31, id="remainder-is-dropped"),
        pytest.param(10, "3", 900, 30, 1, 31, id="credit-equals-new-rate-exactly"),
        pytest.param(10, "2.9", 900, 30, 0, 30, id="credit-just-below-new-rate"),
        pytest.param(-3, "5", 300, 30, 0, 30, id="already-expired"),
        pytest.param(0, "5", 300, 30, 0, 30, id="expires-right-now"),
        pytest.param(10, "5", 0, 30, 0, 30, id="free-tariff"),
        pytest.param(10, "0", 300, 30, 0, 30, id="switching-to-a-paid-tariff"),
        pytest.param(
            10, "5", 100, 30, 15, 45, id="fractional-daily-rate-exact-boundary"
        ),
    ],
)
def test_calculate_change_tariff(
    days_left, old_rate, price, duration_days, converted, total_days
):
    result = SubscriptionCalculator.calculate_change_tariff(
        current_expire_at=NOW + timedelta(days=days_left),
        duration_days=duration_days,
        price=Decimal(price),
        daily_rate=Decimal(old_rate),
        now=NOW,
    )

    assert result.expire_at == NOW + timedelta(days=total_days)
    assert result.converted_days == converted
    assert result.daily_rate == pytest.approx(Decimal(price) / duration_days)


@pytest.mark.parametrize("bad_duration", [0, -1, -30])
def test_raises_if_duration_is_not_positive(bad_duration):
    with pytest.raises(ValueError, match="должно быть положительным"):
        SubscriptionCalculator.calculate_change_tariff(
            current_expire_at=NOW,
            duration_days=bad_duration,
            price=Decimal(100),
            daily_rate=Decimal(10),
            now=NOW,
        )
