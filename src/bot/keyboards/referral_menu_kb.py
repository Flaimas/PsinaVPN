from urllib.parse import quote

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ReferralInlineKB:
    def referral_menu_options(self, ref_link: str) -> InlineKeyboardMarkup:
        share_url = f"https://t.me/share/url?url={quote(ref_link)}&text={quote('Пользуюсь этим VPN, работает стабильно и без лагов. Заходи 👇')}"
        builder = InlineKeyboardBuilder()
        builder.button(text="Пригласить", url=share_url)
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
