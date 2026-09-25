from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import ReferralMenuCallback
from src.bot.utils.message import edit_callback_media
from src.common.bot_photos import DEFAULT_PHOTO
from src.common.referral_text import build_referral_text
from src.database.repositories.user import UserRepository

router = Router()


@router.callback_query(ReferralMenuCallback.filter())
async def referal_menu(
    callback: CallbackQuery, user_repo: UserRepository, kb: InlineKB, bot: Bot
):
    user_tg_id = callback.from_user.id
    user = await user_repo.get_user_by_tg_id(telegram_id=user_tg_id)
    if user:
        count_user_referrals = await user_repo.count_referrals_by_user_id(
            user_id=user.id
        )
    else:
        return

    me = await bot.me()
    ref_link = f"https://t.me/{me.username}?start={user_tg_id}"

    text = build_referral_text(ref_link=ref_link, count=count_user_referrals)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.referral.referral_menu_options(ref_link=ref_link),
    )
    await callback.answer()
