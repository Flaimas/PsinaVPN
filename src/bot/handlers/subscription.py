from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import (
    PricesTariffCallback,
    TariffSelectCallback,
)
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.common.subscription_text import subscription_text
from src.core.enums import InvoiceOperation
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.tariff import TariffRepository
from src.services.tariff import TariffService

router = Router()


@router.callback_query(TariffSelectCallback.filter())
async def process_tariff_select(
    callback: CallbackQuery,
    callback_data: TariffSelectCallback,
    tariff_repo: TariffRepository,
    sub_repo: SubscriptionRepository,
    kb: InlineKB,
    state: FSMContext,
):
    operation = callback_data.operation
    category = callback_data.category

    tariffs = await tariff_repo.get_available_tariffs_for_user(
        telegram_id=callback.from_user.id, category=category
    )
    user_subscriptions = await sub_repo.get_subscriptions_by_tg_id(
        telegram_id=callback.from_user.id
    )

    state_data = await state.get_data()
    user_current_tariff = state_data.get("tariff_id")

    if operation == InvoiceOperation.CHANGE:
        if not user_subscriptions or not user_current_tariff:
            await callback.answer(
                "Упс.. У вас нет ни одной активной подписки!", show_alert=True
            )
            return
        await state.set_state(OrderTariffStates.change_subscription)

    elif operation == InvoiceOperation.BUY:
        await state.set_state(OrderTariffStates.buy_subscription)

    await state.update_data(operation=operation)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=subscription_text.TARIFFS,
        reply_markup=kb.subscription.get_tariffs_keyboard(tariffs),
    )

    await callback.answer()


@router.callback_query(
    PricesTariffCallback.filter(),
    StateFilter(
        OrderTariffStates.buy_subscription,
        OrderTariffStates.extend_subscription,
        OrderTariffStates.change_subscription,
        OrderTariffStates,
    ),
)
async def prices_tariff_menu(
    callback: CallbackQuery,
    callback_data: PricesTariffCallback,
    tariff_repo: TariffRepository,
    tariff_service: TariffService,
    kb: InlineKB,
    state: FSMContext,
):

    tariff_id = callback_data.tariff_id
    tariff = await tariff_repo.get_active_tariff_by_id(tariff_id)
    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return
    options = tariff_service.calculate_period_price(price=tariff.price)
    state_data = await state.get_data()
    user_sub_id = state_data.get("user_sub_id")
    text = "Выберите срок действия подписки."

    await state.update_data(tariff_id=tariff_id)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.subscription.get_tariff_prices(options, user_sub_id),
    )
    await callback.answer()
