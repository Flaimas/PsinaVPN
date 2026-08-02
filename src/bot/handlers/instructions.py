from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import InstuctionPlatform
from src.bot.utils.message import edit_callback_media
from src.common.instructions_text import PlatformInstruction
from src.core.media_config import DEFAULT_PHOTO

router = Router()


@router.callback_query(F.data == "instructions")
async def select_platform(callback: CallbackQuery, kb: InlineKB):
    await callback.answer()
    text = "Выберите вашу платформу:"
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.instructions.select_platform(),
    )


@router.callback_query(InstuctionPlatform.filter())
async def instruction_for_platform(
    callback: CallbackQuery, callback_data: InstuctionPlatform, kb: InlineKB
):
    await callback.answer()
    select_enum = PlatformInstruction[callback_data.platform]
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=select_enum.text,
        reply_markup=kb.instructions.instruction_for_platform(),
    )
