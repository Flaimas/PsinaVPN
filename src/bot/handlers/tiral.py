from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.callbacks import TrialCallback
from src.bot.keyboards.trial_kb import trial_kb
from src.bot.utils.message import edit_callback_media
from src.common.bot_photos import DEFAULT_PHOTO
from src.core.config import settings
from src.database.repositories.tariff import TariffRepository
from src.database.repositories.user import UserRepository
from src.services.subscription import SubscriptionService

router = Router()


@router.callback_query(TrialCallback.filter())
async def get_trial(
    callback: CallbackQuery,
    user_repo: UserRepository,
    tariff_repo: TariffRepository,
    subscription_service: SubscriptionService,
):
    user = await user_repo.get_user_with_subscription(telegram_id=callback.from_user.id)
    if not user:
        await callback.answer(text="Профиль не найден", show_alert=True)
        return
    if user.subscription is not None:
        await callback.answer(text="У вас уже есть активная подписка!", show_alert=True)
        return
    trial_tariff = await tariff_repo.get_active_tariff_by_id(settings.TRIAL_TARIFF_ID)
    if not trial_tariff:
        await callback.answer(text="Пробный тариф временно недоступен", show_alert=True)
        return
    reserved = await user_repo.mark_test_used_is_unused(user_id=user.id)
    if not reserved:
        await callback.answer("Пробрый период уже был использован", show_alert=True)
        return
    result = await subscription_service.grant_trial_subscription(
        user=user, tariff=trial_tariff, duration_days=settings.TRIAL_PERIOD_DAYS
    )
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=(
            "🎉 <b>Пробный период активирован!</b>\n\n"
            f"Вам открыт бесплатный доступ на {settings.TRIAL_PERIOD_DAYS} дн.\n\n"
            "Ваша ссылка для подключения:\n"
            f"<blockquote><code>{result.subscription.sub_url}</code></blockquote>\n\n"
            "Осталось подключиться — жмите кнопку ниже, выберите своё устройство "
            "и следуйте инструкции."
        ),
        reply_markup=trial_kb(),
    )
    await callback.answer()
