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
        lines = []

        lines.append(
            f"<b>Подтверждение заказа</b>\n\n"
            f"📋 <b>Тариф:</b> {selected_tariff.name}\n"
            f"⏳ <b>Срок:</b> {days_amount} дней"
        )

        if selected_tariff.traffic_limit > 0:
            lines.append(
                f"⏳ <b>Трафик белых списков:</b> {selected_tariff.traffic_limit} ГБ\n"
            )

        if base_price == discount_price:
            lines.append(f"💰 <b>Цена:</b> {discount_price:.0f} руб.\n")
        else:
            lines.append(
                f"<s>Старая цена: {base_price:.0f} руб.</s>\n"
                f"🔥 <b>Цена со скидкой:</b> {discount_price:.0f} руб."
            )

        if days_left and days_left > 0:
            lines.append(
                f"⚠️ <b>Внимание:</b> Ваша текущая подписка "
                f"(осталось {days_left} дн.) будет аннулирована "
                f"без перерасчета остатка."
            )
        lines.append("<b>Выберите способ оплаты:</b>")
        return "\n".join(lines)


payment_texts = PaymentTexts()
