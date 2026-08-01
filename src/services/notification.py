from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from src.core.enums import InvoiceOperation
from src.core.media_config import DEFAULT_PHOTO
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff


class NotificationService:
    BUY_TEXT: str = (
        "🎉 <b>Оплата прошла успешно!</b>\n\n"
        "Ваша подписка успешно активирована и готова к работе.\n\n"
        "Нажмите на кнопку ниже, чтобы добавить конфигурацию в приложение:"
    )

    EXTEND_TEXT: str = (
        "🎉 <b>Оплата прошла успешно!</b>\n\n"
        "Подписка <b>{sub_name}</b> была успешно продлена до <b>{expired_at}</b>.\n\n"
        "Удачного пользования! Спасибо, что воспользовались нашим сервисом снова!"
    )

    def __init__(self, bot: Bot, dp: Dispatcher) -> None:
        self.bot = bot
        self.dp = dp

    async def notify_payment_success(
        self,
        telegram_id: int,
        operation: InvoiceOperation,
        user_sub: Subscription,
        user_tariff: Tariff | None = None,
    ) -> bool:
        state = await self._get_state_data(telegram_id=telegram_id)
        payment_msg_id = state.get("payment_msg_id")

        builder = InlineKeyboardBuilder()
        if operation == InvoiceOperation.BUY:
            text = self.BUY_TEXT
            builder.button(text="Подключиться", callback_data="start")
        elif operation == InvoiceOperation.EXTEND:
            text = self.EXTEND_TEXT.format(
                sub_name=user_tariff.name if user_tariff else "NONE",
                expired_at=user_sub.expired_at.strftime("%d.%m.%Y"),
            )
            builder.button(text="Хорошо", callback_data="start")
        else:
            logger.error(f"Неизвестный тип операции платежа: {operation}.")
            return False

        try:
            if payment_msg_id:
                try:
                    await self._edit_message_media(
                        message_id=payment_msg_id,
                        caption=text,
                        chat_id=telegram_id,
                        media=DEFAULT_PHOTO,
                        reply_markup=builder.as_markup(),
                    )
                    return True
                except TelegramAPIError as e:
                    logger.warning(
                        f"Ошибка при попытке отредактировать сообщение, отправляем новое: {e}"
                    )

            await self.bot.send_photo(
                chat_id=telegram_id,
                photo=DEFAULT_PHOTO,
                caption=text,
                reply_markup=builder.as_markup(),
            )
            return True

        except TelegramAPIError as e:
            logger.error(f"Не удалось отправить уведомление юзеру {telegram_id}: {e}")
            return False

        except (ValueError, KeyError, AttributeError) as e:
            logger.exception(
                f"Ошибка в данных или форматировании для {telegram_id}: {e}"
            )
            return False

    async def _edit_message_media(
        self,
        chat_id: int,
        message_id: int,
        media: str,
        caption: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self.bot.edit_message_media(
            InputMediaPhoto(media=media, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )

    async def _get_state_data(self, telegram_id) -> dict[str, Any]:
        state = self.dp.fsm.get_context(
            self.bot, chat_id=telegram_id, user_id=telegram_id
        )
        return await state.get_data()
