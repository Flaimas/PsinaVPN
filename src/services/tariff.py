from loguru import logger
from src.core.config import settings
from src.scheams.tariff import TariffOption

class TariffService:
    def __init__(
        self,
        months: list | None = None,
        discount_for_month: float | None = None,
        step_discount: float | None = None,
        max_discount: float | None = None
    ):
        self.months = months or settings.MONTHS
        self.discount_for_month = discount_for_month or settings.DISCOUNT_FOR_MONTH
        self.step_discount = step_discount or settings.STEP_DISCOUNT
        self.max_discount = max_discount or settings.MAX_DISCOUNT

    def calculate_period_price(self, price: int) -> list[TariffOption]:
        logger.debug("Расчет списка цен и скидки price={}", price)
        if self.discount_for_month is not None:
            if len(self.months) != len(self.discount_for_month):
                error_msg = (
                    f"Ошибка! Количество месяцев не соответствует длине списка с величиной скидки!"
                    f"months={self.months}, discount_for_month={self.discount_for_month}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            discounts = self.discount_for_month

        elif self.step_discount is not None:
            if self.max_discount is None:
                error_msg = "Переменная max_discount не задана!"
                logger.error(error_msg)
                raise ValueError(error_msg)
            discounts = [
                min((self.step_discount * i), self.max_discount)
                for i in range(len(self.months))
            ]
        else:
            error_msg = "Переменные step_discount или discount_for_month не заданы!"
            logger.error(error_msg)
            raise ValueError(error_msg)

        prices = []
        for month, discount in zip(self.months, discounts):
            price_period = round(month * price)
            price_period_from_discount = round(month * price * (1 - discount))
            discount_percent = round(discount * 100)
            prices.append(
                TariffOption(
                    months=month,
                    base_price=price_period,
                    discount_price=price_period_from_discount,
                    discount_percent=discount_percent
                )
            )

        logger.debug("Список цен успешно посчитан! prices={}", prices)
        return prices

    def get_option_for_month(self, price: int, target_month: int):
        options = self.calculate_period_price(price=price)
        for opt in options:
            if opt.months == target_month:
                return opt
        error_msg = f"Период {target_month} мес. не найден в доступных опциях {self.months}"
        logger.error(error_msg)
        raise ValueError(error_msg)