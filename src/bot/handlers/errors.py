from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from src.core.exceptions import AppError

router = Router()


@router.error()
async def global_errors_handler(event: ErrorEvent):
    exception = event.exception
    update = event.update

    logger.error("{}", exception)

    if isinstance(exception, AppError):
        text = str(exception) or "Произошла ошибка"
        print(text)

        if update.callback_query:
            await update.callback_query.answer(text=text, show_alert=True)
            return True
    return False
