from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentProvider(str, Enum):
    YOOKASSA = "yookassa"
    BALANCE = "balance"


class InvoiceOperation(str, Enum):
    BUY = "buy"
    EXTEND = "extend"
