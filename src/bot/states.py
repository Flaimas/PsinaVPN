from aiogram.fsm.state import State, StatesGroup


class OrderTariffStates(StatesGroup):
    extend_subscription = State()
    buy_subscription = State()
    change_subscription = State()
    waiting_for_payment = State()
