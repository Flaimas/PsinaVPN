from aiogram.enums import ButtonStyle
from aiogram.types import CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import ManagmentSubCallback, PricesTariffCallback
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

    def managment_subscription(self, sub: Subscription, count_subscriptions: int):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Продлить подписку",
            callback_data=PricesTariffCallback(slug=sub.tariff.slug),
            style=ButtonStyle.PRIMARY,
        )
        builder.button(
            text="Копировать ссылку",
            copy_text=CopyTextButton(text=sub.sub_url),
        )
        builder.button(text="Инструкция по подключению", callback_data="instructions")
        if count_subscriptions == 1:
            builder.button(text="Назад", callback_data="start")
        else:
            builder.button(text="Назад", callback_data="select_sub_for_management")
        builder.adjust(1)
        return builder.as_markup()
