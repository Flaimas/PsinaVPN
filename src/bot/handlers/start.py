from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import InlineKB
from src.bot.utils.message import edit_callback_media
from src.common.start_texts import start_texts
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.user import UserRepository

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_repo: UserRepository,
    sub_repo: SubscriptionRepository,
    kb: InlineKB,
    state: FSMContext,
):
    assert message.from_user is not None
    await state.clear()

    user = await user_repo.get_user_with_subscriptions(telegram_id=message.from_user.id)
    is_create = False
    if user is None:
        user = await user_repo.create_user(
            telegram_id=message.from_user.id, username=message.from_user.username
        )
        is_create = True

    if is_create:
        text = start_texts.WELCOME_NEW_USER.format(
            username=user.username or "друг",
            balance=int(user.balance),
        )
        await message.answer_photo(
            photo=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.start.get_main_inline_keyboard(),
        )
    else:
        if user.subscriptions:
            text_sub = start_texts.format_subscriptions_text(user.subscriptions)
        else:
            text_sub = start_texts.NO_SUBSCRIPTIONS

        text = start_texts.USER_CABINET.format(
            username=message.from_user.username,
            telegram_id=user.telegram_id,
            balance=int(user.balance),
            sub_info=text_sub,
        )
        await message.answer_photo(
            photo=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.start.get_main_inline_keyboard(
                subscriptions=user.subscriptions
            ),
        )


@router.callback_query(F.data == "start")
async def callback_start(
    callback: CallbackQuery,
    user_repo: UserRepository,
    kb: InlineKB,
    state: FSMContext,
):
    await state.clear()

    user = await user_repo.get_user_with_subscriptions(
        telegram_id=callback.from_user.id
    )
    if user is None:
        await callback.answer(start_texts.PROFILE_NOT_FOUND, show_alert=True)
        return

    if user.subscriptions:
        text_sub = start_texts.format_subscriptions_text(user.subscriptions)
    else:
        text_sub = start_texts.NO_SUBSCRIPTIONS

    text = start_texts.USER_CABINET.format(
        username=callback.from_user.username,
        telegram_id=user.telegram_id,
        balance=int(user.balance),
        sub_info=text_sub,
    )

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.start.get_main_inline_keyboard(
            subscriptions=user.subscriptions
        ),
    )
    await callback.answer()
