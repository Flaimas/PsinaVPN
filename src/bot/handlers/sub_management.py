from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import ManagmentSubCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.common.subscription_text import sub_managment_text
from src.core.enums import InvoiceOperation
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.user import UserRepository

router = Router()


@router.callback_query(ManagmentSubCallback.filter())
async def sub_menu(
    callback: CallbackQuery,
    callback_data: ManagmentSubCallback,
    kb: InlineKB,
    user_repo: UserRepository,
    state: FSMContext,
):
    await callback.answer()
    await state.clear()
    await state.set_state(
        OrderTariffStates.extend_subscription,
    )
    user = await user_repo.get_user_with_subscription(telegram_id=callback.from_user.id)
    if not user:
        await callback.answer(
            text="Ошибка! Пользователь не найден в системе!", show_alert=True
        )
        return
    user_sub = user.subscription
    if not user_sub:
        await callback.answer(
            text="Ошибка, данной подписки нет у пользователя!", show_alert=True
        )
        return

    await state.update_data(
        user_sub_id=user_sub.id,
        tariff_id=user_sub.tariff.id,
        operation=InvoiceOperation.EXTEND,
    )

    text = sub_managment_text.SUB_MANAGEMENT.format(
        sub_name=user_sub.tariff.name,
        expired_at=user_sub.expired_at.strftime("%d.%m.%Y"),
        url=user_sub.sub_url,
    )
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.sub_management.managment_subscription(user_sub),
    )
