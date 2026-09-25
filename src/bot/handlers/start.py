from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import InlineKB
from src.bot.utils.message import edit_callback_media
from src.common.bot_photos import DEFAULT_PHOTO
from src.common.start_texts import start_texts
from src.database.repositories.user import UserRepository

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_repo: UserRepository,
    command: CommandObject,
    kb: InlineKB,
    state: FSMContext,
):
    if not message.from_user:
        return

    await state.clear()

    user = await user_repo.get_user_with_subscription(telegram_id=message.from_user.id)

    if user is None:
        referrer_id: int | None = None
        if command.args and command.args.isdigit():
            potential_referrer_id = int(command.args)
            potential_referrer = await user_repo.get_user_by_tg_id(
                telegram_id=potential_referrer_id
            )
            if potential_referrer != message.from_user.id and potential_referrer:
                referrer_id = potential_referrer.id
            else:
                referrer_id = None

        new_user = await user_repo.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            referrer_id=referrer_id,
        )
        user_sub = None
        # Опционально: уведомить реферера о новом реферале (если нужно)
        # if referrer_id:
        #     await message.bot.send_message(
        #         chat_id=referrer_id,
        #         text=f"У вас новый реферал: @{user.username or user.telegram_id}!"
        #     )

        text = start_texts.WELCOME_NEW_USER.format(
            username=new_user.username or "друг",
            balance=int(new_user.balance),
        )

    else:
        user_sub = user.subscription
        if user.subscription:
            text_sub = start_texts.format_subscriptions_text(user.subscription)
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
        reply_markup=kb.start.get_main_inline_keyboard(user_sub=user_sub),
    )


@router.callback_query(F.data == "start")
async def callback_start(
    callback: CallbackQuery,
    user_repo: UserRepository,
    kb: InlineKB,
    state: FSMContext,
):
    await state.clear()

    user = await user_repo.get_user_with_subscription(telegram_id=callback.from_user.id)
    if user is None:
        await callback.answer(start_texts.PROFILE_NOT_FOUND, show_alert=True)
        return

    if user.subscription:
        text_sub = start_texts.format_subscriptions_text(user.subscription)
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
        reply_markup=kb.start.get_main_inline_keyboard(user_sub=user.subscription),
    )
    await callback.answer()
