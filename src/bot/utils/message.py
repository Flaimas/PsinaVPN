from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message


async def edit_callback_media(
    callback: CallbackQuery,
    media: str,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message | bool:
    if isinstance(callback.message, Message):
        return await callback.message.edit_media(
            media=InputMediaPhoto(media=media, caption=caption),
            reply_markup=reply_markup,
        )
    return False
