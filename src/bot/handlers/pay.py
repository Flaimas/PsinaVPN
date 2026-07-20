from aiogram import Router, F
from aiogram.types import CallbackQuery
from src.database.repositories.tariff import TariffRepository
from src.services.payment.payment import PaymentService
from aiogram.fsm.context import FSMContext
from src.bot.states import OrderTariffStates

router = Router()

@router.callback_query(F.data == "buy", OrderTariffStates.waiting_for_payment)
async def buy_tariff_handler(
    callback: CallbackQuery, 
    state: FSMContext, 
    payment_service: PaymentService,
    tariff_repo: TariffRepository
):
    user_data = await state.get_data()
    price = user_data.get("price")
    period = user_data.get("period")
    slug = user_data.get("tariff_slug")

    if not price or not period:
        await callback.message.answer("Ошибка, попробуйте снова.")
        return
    
    tariff_id = await tariff_repo.get_tariff_by_slug(slug=slug)

    payment = await payment_service.buy_tariff(
        telegram_id=callback.from_user.id,
        price=price,
        tariff_id=tariff_id.id,
        period=int(period),
        activate=True
    )

    if payment:
        await callback.message.answer("Оплата прошла успешно!")
        return
    else:
        await callback.message.answer("Недостаточно средств для покупки подписки, пополните счет.")
    
    await callback.answer()