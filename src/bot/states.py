from aiogram.fsm.state import StatesGroup, State

class OrderTariffStates(StatesGroup):
    choosing_tariff = State()
    choosing_period = State()
    waiting_for_payment = State()