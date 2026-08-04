from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import ManagmentSubCallback, TariffSelectCallback
from src.core.enums import InvoiceOperation, TariffCategory
from src.database.models.subscription import Subscription


class StartInlineKeyboard:
    def get_main_inline_keyboard(
        self,
        subscriptions: list[Subscription] | None = None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        subs = subscriptions or []

        match len(subs):
            case 0:
                builder.button(
                    text="🛍️ Купить VPN",
                    callback_data=TariffSelectCallback(
                        operation=InvoiceOperation.BUY, category=TariffCategory.DEFAULT
                    ),
                )
            case 1:
                builder.button(
                    text="💎 Управление подпиской",
                    callback_data=ManagmentSubCallback(subscription_id=subs[0].id),
                )
                builder.button(text="Инструкции", callback_data="instructions")
            case _:
                builder.button(
                    text="💎 Управление подписками",
                    callback_data="select_sub_for_management",
                )
                builder.button(text="Инструкции", callback_data="instructions")

        builder.button(text="Помощь", callback_data="help")
        builder.adjust(1)
        return builder.as_markup()

    def return_to_start(self):
        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
