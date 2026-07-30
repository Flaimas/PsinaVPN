from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models.tariff import Tariff
from src.scheams.tariff import TariffOption


class SubscriptionInkineKeyBoard:
    def get_tariffs_keyboard(
        self, database_tariffs: list[Tariff]
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tariff in database_tariffs:
            text = f"{tariff.name} - {int(tariff.price)} руб."
            builder.button(text=text, callback_data=f"prices_tariff:{tariff.slug}")
        builder.button(text="↩︎ Назад", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def get_tariff_prices(self, options: list[TariffOption]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for opt in options:
            if opt.discount_percent > 0:
                text = f"{opt.period_days} дней {opt.discount_price} руб. -{opt.discount_percent}%"
            else:
                text = f"{opt.period_days} дней - {opt.base_price} руб."
            builder.button(text=text, callback_data=f"buy_tariff:{opt.period_days}")

        builder.button(text="↩︎ Назад", callback_data="tariffs")
        builder.adjust(1)
        return builder.as_markup()

    def buy_tariff_menu_kb(self, slug: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Оплатить", callback_data="buy")
        builder.button(text="Изменить срок", callback_data=f"prices_tariff:{slug}")
        builder.button(text="Отменить", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
