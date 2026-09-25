from aiogram.filters.callback_data import CallbackData

from src.core.enums import InvoiceOperation, PaymentProvider


class TariffSelectCallback(CallbackData, prefix="tariffs"):
    operation: InvoiceOperation


class PricesTariffCallback(CallbackData, prefix="prices_tariff"):
    tariff_id: int
    operation: InvoiceOperation


class ChangeTariffCallback(CallbackData, prefix="change_tariff"):
    pass


class BuyTariffCallback(CallbackData, prefix="buy_tariff"):
    tariff_option_id: int


class PaymentProcessCallback(CallbackData, prefix="pay"):
    provider: PaymentProvider
    tariff_option_id: int
    operation: InvoiceOperation


class ManagmentSubCallback(CallbackData, prefix="sub_menu"):
    pass


class InstuctionPlatform(CallbackData, prefix="instr"):
    platform: str


class ReferralMenuCallback(CallbackData, prefix="ref_menu"):
    pass
