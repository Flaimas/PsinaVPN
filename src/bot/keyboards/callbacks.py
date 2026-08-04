from aiogram.filters.callback_data import CallbackData

from src.core.enums import InvoiceOperation, PaymentProvider, TariffCategory


class TariffSelectCallback(CallbackData, prefix="tariffs"):
    operation: InvoiceOperation
    category: TariffCategory


class PricesTariffCallback(CallbackData, prefix="prices_tariff"):
    tariff_id: int


class ChangeTariffCallback(CallbackData, prefix="change_tariff"):
    pass


class BuyTariffCallback(CallbackData, prefix="buy_tariff"):
    days_amount: int


class PaymentProcessCallback(CallbackData, prefix="payment"):
    provider: PaymentProvider


class ManagmentSubCallback(CallbackData, prefix="sub_menu"):
    subscription_id: int


class InstuctionPlatform(CallbackData, prefix="instr"):
    platform: str
