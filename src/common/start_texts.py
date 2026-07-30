from dataclasses import dataclass

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
    def format_subscriptions_start(user_subscriptions: list[Subscription]) -> str:
        subscriptions = "\n".join(
            [
                f"{sub.tariff.name} - {f'до {sub.expired_at.strftime("%d.%m.%Y")}' if sub.is_active else f'Истекла ({sub.expired_at.strftime("%d.%m.%Y")})'}"
                for sub in user_subscriptions
            ]
        )
        header = (
            "🔑 Твои подписки:" if len(user_subscriptions) > 1 else "🔑 Твоя подписка:"
        )
        return f"{header} \n\n<code>{subscriptions}</code>"


start_texts = StartMessages()
