from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import ManagmentSubCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.common.subscription_text import sub_managment_text
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.user import UserRepository

router = Router()


@router.callback_query(F.data.startswith("select_sub_for_management"))
async def menu(
    callback: CallbackQuery, user_repo: UserRepository, kb: InlineKB, state: FSMContext
):
    await callback.answer()
    user = await user_repo.get_user_with_subscriptions(
        telegram_id=callback.from_user.id
    )
    if not user:
        callback.answer(text="Ошибка, пользователь не найден.", show_alert=True)
        await state.clear()
        return
    if not user.subscriptions:
        callback.answer(text="У вас нет ни одной подписки!", show_alert=True)
        await state.clear()
        return

    user.subscriptions.sort(key=lambda sub: (sub.tariff.price, sub.tariff.id))

    text = "Выберите подписку:"
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.sub_management.select_subscription(user.subscriptions),
    )


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
    user = await user_repo.get_user_with_subscriptions(
        telegram_id=callback.from_user.id
    )
    if not user:
        await callback.answer(
            text="Ошибка! Пользователь не найден в системе!", show_alert=True
        )
        return

    current_sub = next(
        (sub for sub in user.subscriptions if sub.id == callback_data.subscription_id),
        None,
    )
    if not current_sub:
        await callback.answer(
            text="Ошибка, данной подписки нет у пользователя!", show_alert=True
        )
        return

    await state.set_state(OrderTariffStates.extend_subscription)
    await state.update_data(
        tariff_slug=current_sub.tariff.slug, user_sub_id=current_sub.id
    )

    text = sub_managment_text.SUB_MANAGMNET.format(
        sub_name=current_sub.tariff.name,
        expired_at=current_sub.expired_at.strftime("%d.%m.%Y"),
    )
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.sub_management.managment_subscription(
            current_sub, len(user.subscriptions)
        ),
    )
