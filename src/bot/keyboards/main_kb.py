from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.scheams.tariff import TariffOption
from src.database.repositories.tariff import TariffRepository
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
            text=f"{tariff.name} - {int(tariff.price)} руб."
            builder.button(
                text=text,
                callback_data=f"price:{tariff.slug}"
            )
        builder.button(text="Назад", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def get_tariff_prices(self, options: list[TariffOption]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for opt in options:
            if opt.discount_percent > 0:
                text = f"{opt.months} мес. {opt.discount_price} руб. -{opt.discount_percent}%"
            else:
                text = f"{opt.months} мес. - {opt.base_price} руб."
            builder.button(
                text=text,
                callback_data=f"buy_tariff:{opt.months}"
            )
        builder.button(
            text="Назад",
            callback_data="back_to_tariffs"
        )
        builder.adjust(1)
        return builder.as_markup()
    
    def buy_tariff_menu_kb(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Оплатить", callback_data="buy")
        builder.button(text="Изменить срок", callback_data=f"change_period")
        builder.button(text="Отменить", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

keyboards = InlineKeyboards()