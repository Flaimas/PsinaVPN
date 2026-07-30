from aiogram.fsm.state import State, StatesGroup


class OrderTariffStates(StatesGroup):
    choosing_tariff = State()
    choosing_period = State()
    extend_subscription = State()
    waiting_for_payment = State()
