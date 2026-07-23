from aiogram import Router, F
from aiogram.types import CallbackQuery
from src.services.tariff import TariffService
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.tariff import TariffRepository
from src.bot.keyboards.main_kb import InlineKeyboards
from src.bot.states import OrderTariffStates
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "tariffs")
async def tariffs_menu(
    callback: CallbackQuery, 
    tariff_repo: TariffRepository, 
    kb: InlineKeyboards,
    state: FSMContext
):
    await state.set_state(OrderTariffStates.choosing_tariff)
    await state.update_data(tariff_slug=None)

    tariffs = await tariff_repo.get_tariffs()
    text = f"Список тарифов доступые для покупки:"

    await callback.message.edit_media(
        media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
        reply_markup=kb.get_tariffs_keyboard(tariffs)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prices_tariff:"))
async def prices_tariff_menu(
    callback: CallbackQuery,
    tariff_repo: TariffRepository,
    tariff_service: TariffService, 
    kb: InlineKeyboards,
    state: FSMContext
):
    
    slug = callback.data.split(":")[1]
    tariff = await tariff_repo.get_tariff_by_slug(slug)
    options = tariff_service.calculate_period_price(price=tariff.price)
    text = f"Выберите срок действия подписки."

    await state.set_state(OrderTariffStates.choosing_period)
    await state.update_data(tariff_slug=slug)

    await callback.message.edit_media(
        media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
        reply_markup=kb.get_tariff_prices(options)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_tariff:"), OrderTariffStates.choosing_period)
async def buy_tariff_menu(
    callback: CallbackQuery, 
    tariff_repo: TariffRepository,
    tariff_service: TariffService, 
    kb: InlineKeyboards,
    state: FSMContext
):
    
    period = callback.data.split(":")[1]
    user_data = await state.get_data()
    slug = user_data.get("tariff_slug")
    tariff = await tariff_repo.get_tariff_by_slug(slug)
    option = tariff_service.get_option_for_month(
        price=tariff.price,
        target_month=int(period)
    )

    await state.set_state(OrderTariffStates.waiting_for_payment)
    await state.update_data(price=option.discount_price, period=period, user_id=callback.from_user.id)

    if option.base_price == option.discount_price:
        price_text = f"Цена: {option.discount_price} руб."
    else:
        price_text = (
        f"<s>Старая цена: {option.base_price} руб.</s>\n"
        f"Цена со скидкой: {option.discount_price} руб. 🔥"
    )
    text = (
        f"Подтверждение заказа\n\n"
        f"📋 Тариф: {tariff.name}\n"
        f"Срок: {period} мес.\n"
        f"{price_text}"
    )
    await callback.message.edit_media(
        media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
        reply_markup=kb.buy_tariff_menu_kb(slug)
    )
    await callback.answer()