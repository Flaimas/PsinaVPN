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
    def format_subscriptions_text(user_subscriptions: list[Subscription]) -> str:
        if not user_subscriptions:
            return "🔑 У тебя нет активных подписок."

        format_subs: list[str] = []
        for sub in user_subscriptions:
            formatted_date = sub.expired_at.strftime("%d.%m.%Y")
            text = ""
            match sub.status:
                case SubscriptionStatus.ACTIVE:
                    text = f"{sub.tariff.name} - активна до {formatted_date}"
                case SubscriptionStatus.DISABLED:
                    text = f"{sub.tariff.name} - отключена."
                case SubscriptionStatus.EXPIRED:
                    text = f"{sub.tariff.name} - закончилась."
                case SubscriptionStatus.LIMITED:
                    text = f"{sub.tariff.name} - лимит трафика исчерпан."
                case _:
                    text = f"{sub.tariff.name} — неизвестный статус."
            format_subs.append(text)
        header = (
            "🔑 Твои подписки:" if len(user_subscriptions) > 1 else "🔑 Твоя подписка:"
        )
        subscription_str = "/n".join(format_subs)
        return f"{header} \n\n<code>{subscription_str}</code>"


start_texts = StartMessages()
