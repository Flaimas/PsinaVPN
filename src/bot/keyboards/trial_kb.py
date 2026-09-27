from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.callbacks import InstructionsCallback


def trial_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Как подключиться?", callback_data=InstructionsCallback(), style="success"
    )
    return builder.as_markup()
