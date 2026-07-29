from types import MappingProxyType

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import PaymentProcessCallback, PricesTariffCallback
from src.core.config import settings
from src.database.models.invoice import PaymentProvider


class PaymentInlineKeyboard:
    PROVIDER_TITLES: MappingProxyType[PaymentProvider, str] = MappingProxyType(
        {
            PaymentProvider.YOOKASSA: "СБП, Банковская карта (ЮKassa) 💳",
            PaymentProvider.BALANCE: "Баланс аккаунта",
        }
    )

    def select_payment_provider_kb(self, slug: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for provider in settings.PAYMENT_PROVIDERS:
            builder.button(
                text=self.PROVIDER_TITLES[provider],
                callback_data=PaymentProcessCallback(provider=provider),
            )
        builder.button(text="Назад", callback_data=PricesTariffCallback(slug=slug))
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def retry_payment(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Повторить попытку", callback_data="buy")
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def succes_payment(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Как подключиться?", callback_data="ЗАГЛУШКА_ПОМОЩИ_ПОДКЛЮЧЕНИЯ"
        )
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def url_payment(self, url: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Оплатить", url=url, style=ButtonStyle.SUCCESS)
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
