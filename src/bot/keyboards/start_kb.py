from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartInlineKeyboard:
    def get_main_inline_keyboard(
        self, subscriptions: list | None = None
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        if not subscriptions:
            builder.button(text="🛍️ Купить VPN", callback_data="tariffs")
        else:
            text = f"💎 Управление {'подпиской' if len(subscriptions) < 2 else 'подписками'}"
            builder.button(text=text, callback_data="panel")
        builder.button(text="Помощь", callback_data="help")
        builder.adjust(1)
        return builder.as_markup()

    def return_to_start(self):
        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
