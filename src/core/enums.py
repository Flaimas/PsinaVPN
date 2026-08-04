from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentProvider(str, Enum):
    YOOKASSA = "yookassa"
    BALANCE = "balance"


class TariffCategory(str, Enum):
    DEFAULT = "default"
    WHITELIST = "whitelist"


class InvoiceOperation(str, Enum):
    BUY = "buy"
    EXTEND = "extend"
    CHANGE = "change"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    LIMITED = "limited"
    EXPIRED = "expired"
