from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
            builder.button(text=f"{tariff.name} - {int(tariff.price)} руб.", callback_data=f"price:{tariff.slug}")
        builder.button(text="Назад", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()

    def get_tariff_prices(self, database_tariff: Tariff, tariff_repo: TariffRepository) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        price = database_tariff.price
        builder.button(
            text=f"30 дней - {tariff_repo.calculate_period_price(price=price, period=30)[-1]} руб. -0%", 
            callback_data=f"buy_tariff:30"
        )
        builder.button(
            text=f"60 дней - {tariff_repo.calculate_period_price(price=price, period=60)[-1]} руб. -10%", 
            callback_data=f"buy_tariff:60"
        )
        builder.button(
            text=f"90 дней - {tariff_repo.calculate_period_price(price=price, period=90)[-1]} руб. -20%", 
            callback_data=f"buy_tariff:90"
        )
        builder.button(
            text=f"Назад к выбору тарифа", 
            callback_data=f"tariffs"
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