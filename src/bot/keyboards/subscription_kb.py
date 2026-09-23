from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import (
    BuyTariffCallback,
    ManagmentSubCallback,
    PricesTariffCallback,
    TariffSelectCallback,
)
from src.bot.keyboards.helpers import calculate_discount_percent
from src.core.enums import InvoiceOperation
from src.database.models.tariff import Tariff, TariffOption


class SubscriptionInkineKeyBoard:
    def get_tariffs_keyboard(
        self,
        tariffs: list[Tariff],
        operation: InvoiceOperation,
        current_user_tariff_id: int | None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tariff in tariffs:
            if tariff.id != current_user_tariff_id:
                text = f"{tariff.name}"
                builder.button(
                    text=text,
                    callback_data=PricesTariffCallback(
                        tariff_id=tariff.id, operation=operation
                    ),
                )

        if operation == InvoiceOperation.BUY:
            callback_data = "start"
        else:
            callback_data = ManagmentSubCallback()
        builder.button(text="↩︎ Назад", callback_data=callback_data)
        builder.adjust(1)
        return builder.as_markup()

    def get_tariff_prices(
        self,
        tariff_options: list[TariffOption],
        operation: InvoiceOperation,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for opt in tariff_options:
            if opt.old_price is not None:
                text = f"{opt.period_days} дней | {opt.price} руб. -{calculate_discount_percent(opt.old_price, opt.price)}%"
            else:
                text = f"{opt.period_days} дней | {opt.price} руб."
            builder.button(
                text=text, callback_data=BuyTariffCallback(tariff_option_id=opt.id)
            )

        callback_data = TariffSelectCallback(operation=operation)
        if operation == InvoiceOperation.EXTEND:
            callback_data = ManagmentSubCallback()

        builder.button(text="↩︎ Назад", callback_data=callback_data)
        builder.adjust(1)
        return builder.as_markup()

    def buy_tariff_menu_kb(self, slug: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Оплатить", callback_data="buy")
        builder.button(text="Изменить срок", callback_data=f"prices_tariff:{slug}")
        builder.button(text="Отменить", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
