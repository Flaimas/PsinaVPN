from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import (
    ManagmentSubCallback,
    ReferralMenuCallback,
    TariffSelectCallback,
)
from src.core.enums import InvoiceOperation
from src.database.models.subscription import Subscription


class StartInlineKeyboard:
    def get_main_inline_keyboard(
        self,
        user_sub: Subscription | None = None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if user_sub is None:
            builder.button(
                text="🛍️ Купить VPN",
                callback_data=TariffSelectCallback(operation=InvoiceOperation.BUY),
            )
        else:
            builder.button(
                text="💎 Управление подпиской",
                callback_data=ManagmentSubCallback(),
            )
            builder.button(text="Инструкции", callback_data="instructions")

        builder.button(text="Реферальное меню", callback_data=ReferralMenuCallback())
        builder.adjust(1)
        builder.button(text="Помощь", callback_data="help")
        builder.adjust(1)
        return builder.as_markup()

    def return_to_start(self):
        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
