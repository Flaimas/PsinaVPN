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

    tariffs = await tariff_repo.get_active_tariffs()
    user_subscription = await sub_repo.get_by_tg_id(telegram_id=callback.from_user.id)

    user_tariff_id = None
    if operation == InvoiceOperation.CHANGE:
        if not user_subscription:
            await callback.answer("Упс.. У вас нет активной подписки!", show_alert=True)
            return
        await state.set_state(OrderTariffStates.change_subscription)
        user_tariff_id = user_subscription.tariff_id

    elif operation == InvoiceOperation.BUY:
        await state.set_state(OrderTariffStates.buy_subscription)

    elif operation == InvoiceOperation.EXTEND:
        await state.set_state(OrderTariffStates.extend_subscription)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=subscription_text.format_tariffs_menu(tariffs),
        reply_markup=kb.subscription.get_tariffs_keyboard(
            tariffs=tariffs, current_user_tariff_id=user_tariff_id, operation=operation
        ),
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
    kb: InlineKB,
    state: FSMContext,
):

    tariff_id = callback_data.tariff_id
    tariff = await tariff_repo.get_active_tariff_by_id(tariff_id)
    if not tariff:
        await callback.answer("Тариф не найден или больше не активен", show_alert=True)
        return
    operation = callback_data.operation
    text = "Выберите срок действия подписки."

    await state.update_data(tariff_id=tariff_id)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.subscription.get_tariff_prices(tariff.options, operation),
    )
    await callback.answer()
