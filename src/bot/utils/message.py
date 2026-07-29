from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message


async def edit_callback_media(
    callback: CallbackQuery,
    media: str,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            InputMediaPhoto(media=media, caption=caption), reply_markup=reply_markup
        )
