from dataclasses import dataclass


@dataclass(frozen=True)
class SubscriptionText:
    TARIFFS: str = (
        "<b>Доступные тарифы</b>\n\n"
        "<blockquote>"
        "<b>STANDART</b>\n"
        "Базовый доступ для личного пользования.\n"
        "До 3 устройств, 200 ГБ трафика.\n\n"
        "<b>GO</b>\n"
        "Оптимально для активного серфинга и видео.\n"
        "До 5 устройств, 400 ГБ трафика.\n\n"
        "<b>PRO</b>\n"
        "Максимальная скорость без ограничений.\n"
        "До 9 устройств, 800 ГБ трафика."
        "</blockquote>"
    )


subscription_text = SubscriptionText()
