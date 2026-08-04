from loguru import logger

from src.core.config import settings
from src.scheams.tariff import TariffOption


class TariffService:
    def __init__(
        self,
        periods: list[int] | None = None,
        discount_for_period: list[int] | None = None,
        max_discount: int | None = None,
    ):
        self.periods = periods or settings.PERIODS_SUBSCRIPTION
        self.discount_for_period = (
            discount_for_period
            or settings.DISCOUNT_FOR_PERIOD
            or [0] * len(self.periods)
        )
        self.max_discount = max_discount or settings.MAX_DISCOUNT

    def calculate_period_price(self, price: float) -> list[TariffOption]:
        if not self.periods:
            raise ValueError("Периоды подписки не были инициализированны!")
        if len(self.periods) != len(self.discount_for_period):
            raise ValueError(
                "Спискок периодов подписки и список размера скидки для каждого периода должны быть одной длинны!"
            )

        if max(self.discount_for_period) > self.max_discount:
            raise ValueError(
                "Размер скидки привышает выставленный порог в {}%", self.max_discount
            )

        prices_for_periods = []
        for period, period_discount in zip(self.periods, self.discount_for_period):
            base_price = (period / 30) * price
            discount_price = round(base_price * (1 - period_discount / 100))
            prices_for_periods.append(
                TariffOption(
                    period_days=period,
                    base_price=round(base_price),
                    discount_price=discount_price,
                    discount_percent=period_discount,
                )
            )
        return prices_for_periods

    def calculate_subscription_price(self, price: float, target_period: int):
        options = self.calculate_period_price(price=price)
        for opt in options:
            if opt.period_days == target_period:
                return opt
        error_msg = (
            f"Период {target_period} дней не найден в доступных опциях {self.periods}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
