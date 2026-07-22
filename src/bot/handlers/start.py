from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.user import UserRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.bot.keyboards.main_kb import InlineKeyboards
from src.bot.states import OrderTariffStates
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def cmd_start(
    message: Message, 
    user_repo: UserRepository, 
    sub_repo: SubscriptionRepository, 
    kb: InlineKeyboards,
    state: FSMContext
):
    await state.clear()

    user = await user_repo.get_user_by_tg_id(telegram_id=message.from_user.id)
    is_create = False
    if user is None:
        user = await user_repo.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        is_create = True

    if is_create:
        await message.answer_photo(
                photo=DEFAULT_PHOTO,
                caption=(
                    f"🎉 <b>Привет, {user.username or 'друг'}!</b>\n"
                    f"Спасибо, что воспользовались услугами нашего сервиса!\n\n"
                    f"🎁 Вам выдан приветственный бонус в размере <code>{user.balance}</code> руб."
                    f"Что бы протестировать сервис перейдите в меню '🛍 Купить VPN'"
                ),
                reply_markup=kb.get_main_inline_keyboard()
            )
    else:
        user_subscriptions = await sub_repo.get_subscriptions_by_user(user_id=user.id, load_tariff=True)
        if user_subscriptions:
            subscriptions = "\n".join(
                [f"{sub.tariff.name} - {'Активна' if sub.is_active else 'Неактивна'}" for sub in user_subscriptions]
            )
            text_sub = f"🔑{'Твои подписки:' if len(user_subscriptions) > 1 else 'Твоя подписка:'} \n\n<code>{subscriptions}</code>"
        else:
            text_sub = "У тебя пока нет активных подписок. Ты можешь купить её в меню!"
        await message.answer_photo(
                photo=DEFAULT_PHOTO,
                caption=(
                    f"👤 Кабинет пользователя\n\n"
                    f"🆔 Ваш ID: {user.telegram_id}\n"
                    f"💰 Баланс: <code>{int(user.balance)}</code> руб.\n"
                    f"{text_sub}"
                ),
                reply_markup=kb.get_main_inline_keyboard()
            )

@router.callback_query(F.data == "start")
async def callback_start(
    callback: CallbackQuery, 
    user_repo: UserRepository, 
    sub_repo: SubscriptionRepository, 
    kb: InlineKeyboards,
    state: FSMContext
):
    await state.clear()

    user = await user_repo.get_user_by_tg_id(telegram_id=callback.from_user.id)
    if user is None:
        await callback.answer("Профиль не найден. Пожалуйста, введите /start", show_alert=True)
        return
    
    user_subscriptions = await sub_repo.get_subscriptions_by_user(user.id)
    if user_subscriptions:
        subscriptions = "\n".join(
            [f"{sub.tariff.name} - {'Активна' if sub.is_active else 'Неактивна'}" for sub in user_subscriptions]
        )
        text_sub = f"🔑{'Твои подписки:' if len(user_subscriptions) > 1 else 'Твоя подписка:'} \n\n<code>{subscriptions}</code>"
    else:
        text_sub = "У тебя пока нет активных подписок. Ты можешь купить её в меню!"

    text = (
        f"👤 Кабинет пользователя\n\n"
        f"🆔 Ваш ID: {user.telegram_id}\n"
        f"💰 Баланс: <code>{int(user.balance)}</code> руб.\n"
        f"{text_sub}"
    )

    await callback.message.edit_media(
            media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
            reply_markup=kb.get_main_inline_keyboard()
        )
    await callback.answer()