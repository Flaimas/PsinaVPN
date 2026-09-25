from .instructions import InstructionsInlineKeyboard
from .payment_kb import PaymentInlineKeyboard
from .referral_menu_kb import ReferralInlineKB
from .start_kb import StartInlineKeyboard
from .sub_management import SubManagamentInlineKeyboard
from .subscription_kb import SubscriptionInkineKeyBoard


class InlineKB:
    payment = PaymentInlineKeyboard()
    start = StartInlineKeyboard()
    subscription = SubscriptionInkineKeyBoard()
    sub_management = SubManagamentInlineKeyboard()
    instructions = InstructionsInlineKeyboard()
    referral = ReferralInlineKB()


keyboards = InlineKB()
