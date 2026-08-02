from aiogram.filters.callback_data import CallbackData

from src.core.enums import PaymentProvider


class PricesTariffCallback(CallbackData, prefix="prices_tariff"):
    slug: str


class BuyTariffCallback(CallbackData, prefix="buy_tariff"):
    days_amount: int


class PaymentProcessCallback(CallbackData, prefix="deposit"):
    provider: PaymentProvider


class ManagmentSubCallback(CallbackData, prefix="sub_menu"):
    subscription_id: int


class InstuctionPlatform(CallbackData, prefix="instr"):
    platform: str
