from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import (
    ManagmentSubCallback,
    ReferralMenuCallback,
    TariffSelectCallback,
    TrialCallback,
)
from src.core.enums import InvoiceOperation
from src.database.models.subscription import Subscription


class StartInlineKeyboard:
    def get_main_inline_keyboard(
        self,
        is_test_used: bool,
        user_sub: Subscription | None = None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if user_sub is None:
            builder.button(
                text="🛍️ Купить VPN",
                callback_data=TariffSelectCallback(operation=InvoiceOperation.BUY),
                style=ButtonStyle.SUCCESS,
            )
        else:
            builder.button(
                text="💎 Управление подпиской",
                callback_data=ManagmentSubCallback(),
                style=ButtonStyle.PRIMARY,
            )

        if not is_test_used:
            builder.button(
                text="🎁 Пробный период",
                callback_data=TrialCallback(),
                style=ButtonStyle.PRIMARY,
            )

        builder.button(text="💸 Реферальное меню", callback_data=ReferralMenuCallback())
        builder.button(text="📖 Инструкции", callback_data="instructions")
        builder.button(text="💬 Поддержка", callback_data="help")
        builder.adjust(1)
        return builder.as_markup()

    def return_to_start(self):
        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
