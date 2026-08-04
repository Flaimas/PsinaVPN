from aiogram.enums import ButtonStyle
from aiogram.types import CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import (
    ManagmentSubCallback,
    PricesTariffCallback,
    TariffSelectCallback,
)
from src.core.enums import InvoiceOperation
from src.database.models.subscription import Subscription


class SubManagamentInlineKeyboard:
    def select_subscription(self, subscriptions: list[Subscription]):
        builder = InlineKeyboardBuilder()
        for sub in subscriptions:
            builder.button(
                text=f"{sub.tariff.name} - до {sub.expired_at.strftime('%d.%m.%Y')}",
                callback_data=ManagmentSubCallback(subscription_id=sub.id),
            )
        builder.button(text="Назад", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def managment_subscription(
        self, selected_user_sub: Subscription, all_user_sub: list[Subscription]
    ):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Продлить подписку",
            callback_data=PricesTariffCallback(tariff_id=selected_user_sub.tariff.id),
            style=ButtonStyle.PRIMARY,
        )
        builder.button(
            text="Перейти на другой тариф",
            callback_data=TariffSelectCallback(
                category=selected_user_sub.tariff_category,
                operation=InvoiceOperation.CHANGE,
            ),
            style=ButtonStyle.SUCCESS,
        )
        builder.button(
            text="Копировать ссылку",
            copy_text=CopyTextButton(text=selected_user_sub.sub_url),
        )
        builder.button(text="Инструкция по подключению", callback_data="instructions")
        if len(all_user_sub) == 1:
            builder.button(text="Назад", callback_data="start")
        else:
            builder.button(text="Назад", callback_data="select_sub_for_management")
        builder.adjust(1)
        return builder.as_markup()
