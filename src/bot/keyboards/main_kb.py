from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.database.models.tariff import Tariff

class InlineKeyboards:
    def get_inline_media(self, media: str, caption: str) -> InputMediaPhoto:
        """Генерирует готовый объект медиа для edit_media"""
        return InputMediaPhoto(
            media=media,
            caption=caption
        )
    
    def get_main_inline_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🛍️ Купить VPN", callback_data="tariffs")
        builder.button(text="💳 Пополнить баланс", callback_data="pay")
        builder.button(text="Помощь", callback_data="help")
        builder.adjust(2)
        return builder.as_markup()

    def get_tariffs_keyboard(self, database_tariffs: list[Tariff]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tariff in database_tariffs:
            builder.button(text=f"{tariff.name} - {tariff.price} руб.", callback_data=f"price:{tariff.slug}")
        builder.button(text="Назад", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def get_tariff_prices(self, database_tariff: Tariff):
        builder = InlineKeyboardBuilder()
        price, slug = database_tariff.price, database_tariff.slug
        builder.button(
            text=f"30 дней - {int(price)} руб. -0%", 
            callback_data=f"buy_tariff:{slug}:30"
        )
        builder.button(
            text=f"60 дней - {int((price - ((price / 100) * 10)) * 2)} руб. -10%", 
            callback_data=f"buy_tariff:{slug}:60"
        )
        builder.button(
            text=f"90 дней - {int((price - ((price / 100) * 20)) * 3)} руб. -20%", 
            callback_data=f"buy_tariff:{slug}:90"
        )
        builder.button(
            text=f"Назад к выбору тарифа", 
            callback_data=f"tariffs"
        )
        builder.adjust(1)
        return builder.as_markup()

keyboards = InlineKeyboards()