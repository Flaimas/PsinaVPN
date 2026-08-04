from dataclasses import dataclass

from src.database.models.tariff import Tariff


@dataclass(frozen=True)
class PaymentTexts:
    SESSION_EXPIRED: str = "Сессия истекла. Пожалуйста, выберите тариф заново."
    TARIFF_NOT_FOUND: str = "Тариф не найден."
    DATA_ERROR: str = "Ошибка при получении параметров подписки, попробуйте снова."
    PAYMENT_LINK_CAPTION: str = (
        "⏳ <b>Ссылка на оплату действительна 10 минут.</b>\n\n"
        "Пополните счет в течение этого времени, чтобы активировать подписку.\n\n"
        "Нажмите на кнопку ниже для перехода к оплате 👇"
    )
    USER_NOT_FOUND: str = "Пользователь не найден!"

    @staticmethod
    def format_order_confirmation(
        selected_tariff: Tariff,
        days_amount: int,
        base_price: float,
        discount_price: float,
        days_left: int | None = None,
    ) -> str:
        if base_price == discount_price:
            price_text = f"💰 Цена: {discount_price:.0f} руб."
        else:
            price_text = (
                f"<s>Старая цена: {base_price:.0f} руб.</s>\n"
                f"🔥 Цена со скидкой: {discount_price:.0f} руб."
            )

        notification = ""
        if days_left and days_left > 0:
            notification = (
                f"\n⚠️ <b>Внимание:</b> Ваша текущая подписка "
                f"(осталось {days_left} дн.) будет аннулирована "
                f"без перерасчета остатка.\n"
            )

        return (
            f"<b>Подтверждение заказа</b>\n\n"
            f"📋 <b>Тариф:</b> {selected_tariff.name} ({selected_tariff.traffic_limit} ГБ)\n"
            f"⏳ <b>Срок:</b> {days_amount} дней\n"
            f"{price_text}\n"
            f"{notification}\n"
            f"Выберите способ оплаты:"
        )


payment_texts = PaymentTexts()
