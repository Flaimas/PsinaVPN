from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartInlineKeyboard:
    def get_main_inline_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🛍️ Купить VPN", callback_data="tariffs")
        builder.button(text="💳 Пополнить баланс", callback_data="pay")
        builder.button(text="Помощь", callback_data="help")
        builder.adjust(2)
        return builder.as_markup()

    def return_to_start(self):
        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
