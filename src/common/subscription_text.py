from dataclasses import dataclass

from src.core.enums import TariffCategory
from src.database.models.tariff import Tariff


class SubscriptionText:
    def format_tariffs_menu(self, tariffs: list[Tariff]):
        text = "<b>Доступные тарифы</b>\n\n"
        for t in tariffs:
            text += f"<blockquote>{self.format_tariff_description(t)}</blockquote>"
        return text

    def format_tariff_description(
        self,
        tariff: Tariff,
    ):
        if tariff.category == TariffCategory.WHITELIST:
            limit_text = f"• Лимит трафика на белые списки: {tariff.traffic_limit} ГБ"
        elif tariff.category == TariffCategory.DEFAULT:
            limit_text = "<s>• Белые списки не включены в тариф</s>"

        return (
            f"<b>{tariff.name.upper()}</b>\n"
            f"• До {tariff.device_limit} устройств в подписке\n"
            f"• Безлимитный трафик на основную подписку\n"
            f"{limit_text}\n"
        )


@dataclass(frozen=True)
class SubManagementText:
    SUB_MANAGEMENT: str = (
        "<b>Меню управления подпиской:</b>\n\n"
        "Тариф: {sub_name}\n"
        "Активна до: {expired_at}\n\n"
        "<b>Ссылка на подписку</b> (нажмите что бы скопировать):\n"
        "<blockquote><code>{url}</code></blockquote>"
    )


subscription_text = SubscriptionText()
sub_managment_text = SubManagementText()
