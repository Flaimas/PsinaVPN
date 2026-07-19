from aiogram import Router, F
from aiogram.types import CallbackQuery
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.tariff import TariffRepository
from src.bot.keyboards.main_kb import InlineKeyboards

router = Router()

@router.callback_query(F.data == "tariffs")
async def tariffs_menu(callback: CallbackQuery, tariff_repo: TariffRepository, kb: InlineKeyboards):
    tariffs = await tariff_repo.get_tariffs()
    text = f"Список тарифов доступые для покупки:"

    await callback.message.edit_media(
        media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
        reply_markup=kb.get_tariffs_keyboard(tariffs)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("price:"))
async def price_tariff_menu(callback: CallbackQuery, tariff_repo: TariffRepository, kb: InlineKeyboards):
    slug = callback.data.split(":")[1]
    tariff = await tariff_repo.get_tariff_by_slug(slug)
    text = f"Выберите срок действия подписки."
    await callback.message.edit_media(
        media=kb.get_inline_media(media=DEFAULT_PHOTO, caption=text),
        reply_markup=kb.get_tariff_prices(tariff)
    )
    await callback.answer()