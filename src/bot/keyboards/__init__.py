from .payment_kb import PaymentInlineKeyboard
from .start_kb import StartInlineKeyboard
from .subscription_kb import SubscriptionInkineKeyBoard


class InlineKB:
    payment = PaymentInlineKeyboard()
    start = StartInlineKeyboard()
    subscription = SubscriptionInkineKeyBoard()


keyboards = InlineKB()
