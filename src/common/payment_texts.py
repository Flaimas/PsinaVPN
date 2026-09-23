from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff, TariffOption
from src.services.subscription_calculator import SubscriptionCalculator


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
        tariff_option: TariffOption,
        selected_tariff: Tariff,
        user_subscription: Subscription | None = None,
    ) -> str:
        lines = []

        lines.append(
            f"<b>Подтверждение заказа</b>\n\n"
            f"📋 <b>Тариф:</b> {selected_tariff.name}\n"
            f"⏳ <b>Срок:</b> {tariff_option.period_days} дней"
        )

        if selected_tariff.traffic_limit > 0:
            lines.append(
                f"⏳ <b>Трафик белых списков:</b> {selected_tariff.traffic_limit} ГБ\n"
            )

        if tariff_option.old_price is None:
            lines.append(f"💰 <b>Цена:</b> {tariff_option.price:.0f} руб.\n")
        else:
            lines.append(
                f"💸 <b>Старая цена:</b> <s>{tariff_option.old_price:.0f} руб.</s>\n"
                f"🔥 <b>Цена со скидкой:</b> {tariff_option.price:.0f} руб."
            )

        if user_subscription is not None:
            now = datetime.now(UTC)
            expire_at = user_subscription.expired_at
            remaining_days = max(0, (expire_at - now).days)
            result = SubscriptionCalculator.calculate_change_tariff(
                current_expire_at=expire_at,
                duration_days=tariff_option.period_days,
                price=Decimal(tariff_option.price),
                daily_rate=user_subscription.daily_rate,
                now=now,
            )
            if remaining_days > 0:
                lines.append(
                    "\n<b>⚠️ Перерасчет текущей подписки:</b>\n"
                    f"У вас осталось <b>{remaining_days}</b> дней текущего тарифа. При переходе они конвертируются в 18 дней тарифа «{selected_tariff.name}».\n"
                    f"<b>📅 Итого подписки:</b> <b>{tariff_option.period_days}</b> дней (заказ) + <b>{result.converted_days}</b> дней (перерасчет) = <b>{result.converted_days + tariff_option.period_days}</b> дней\n"
                )
        lines.append("<b>Выберите способ оплаты:</b>")
        return "\n".join(lines)


payment_texts = PaymentTexts()
