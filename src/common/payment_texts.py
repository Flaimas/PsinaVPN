from dataclasses import dataclass


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

    @staticmethod
    def format_order_confirmation(
        tariff_name: str, days_amount: int, base_price: float, discount_price: float
    ) -> str:
        if base_price == discount_price:
            price_text = f"Цена: {discount_price} руб."
        else:
            price_text = (
                f"<s>Старая цена: {base_price} руб.</s>\n"
                f"Цена со скидкой: {discount_price} руб. 🔥"
            )
        return (
            f"Подтверждение заказа\n\n"
            f"📋 Тариф: {tariff_name}\n"
            f"Срок: {days_amount} дней.\n"
            f"{price_text}\n\n"
            f"Выберите способ оплаты:"
        )


payment_texts = PaymentTexts()
