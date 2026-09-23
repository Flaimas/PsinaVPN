from dataclasses import dataclass

from src.core.enums import SubscriptionStatus
from src.database.models.subscription import Subscription


@dataclass(frozen=True)
class StartMessages:
    WELCOME_NEW_USER: str = (
        "🎉 <b>Привет, {username}!</b>\n"
        "Спасибо, что воспользовались услугами нашего сервиса!\n\n"
        "🎁 Вам выдан приветственный бонус в размере <code>{balance}</code> руб.\n\n"
        "Что бы протестировать сервис перейдите в меню '🛍 Купить VPN'"
    )

    USER_CABINET: str = (
        "👋 Привет, {username}!\n\n"
        "<blockquote>🆔 Ваш ID: {telegram_id}</blockquote>\n"
        "💰 Баланс: <code>{balance}</code> руб.\n\n"
        "{sub_info}"
    )

    NO_SUBSCRIPTIONS: str = (
        "☹️ У тебя пока нет активных подписок. Ты можешь купить её в меню!"
    )

    PROFILE_NOT_FOUND: str = "Профиль не найден. Пожалуйста, введите /start"

    @staticmethod
    def format_subscriptions_text(user_sub: Subscription) -> str:
        formatted_date = user_sub.expired_at.strftime("%d.%m.%Y")
        text = ""
        match user_sub.status:
            case SubscriptionStatus.ACTIVE:
                text = f"{user_sub.tariff.name} - активна до {formatted_date}"
            case SubscriptionStatus.DISABLED:
                text = f"{user_sub.tariff.name} - отключена."
            case SubscriptionStatus.EXPIRED:
                text = f"{user_sub.tariff.name} - закончилась."
            case SubscriptionStatus.LIMITED:
                text = f"{user_sub.tariff.name} - лимит трафика исчерпан."
            case _:
                text = f"{user_sub.tariff.name} — неизвестный статус."
        header = "🔑 Твоя подписка:"
        return f"{header}\n<code>{text}</code>"


start_texts = StartMessages()
