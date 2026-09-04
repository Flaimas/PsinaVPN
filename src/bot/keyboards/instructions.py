from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import InstuctionPlatform
from src.common.instructions_text import platform_instructions


class InstructionsInlineKeyboard:
    def select_platform(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for platform_key, platform_data in platform_instructions:
            builder.button(
                text=platform_data.label,
                callback_data=InstuctionPlatform(platform=platform_key),
            )

        builder.adjust(2, repeat=True)
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data="start"))
        return builder.as_markup()

    def instruction_for_platform(self, downloads) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for download in downloads:
            builder.button(text=download.name, url=str(download.url))
        builder.button(text="Назад", callback_data="instructions")
        builder.button(text="Главное меню", callback_data="start")
        builder.adjust(1)
        return builder.as_markup()
