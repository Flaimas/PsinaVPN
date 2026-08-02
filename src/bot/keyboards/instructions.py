from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import InstuctionPlatform
from src.common.instructions_text import PlatformInstruction


class InstructionsInlineKeyboard:
    def select_platform(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for platform in PlatformInstruction:
            builder.button(
                text=platform.label,
                callback_data=InstuctionPlatform(platform=platform.name),
            )
        builder.adjust(2, repeat=True)
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data="start"))
        return builder.as_markup()

    def instruction_for_platform(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад", callback_data="instructions")
        builder.button(text="Главное меню", callback_data="start")
        return builder.as_markup()
