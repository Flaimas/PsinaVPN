from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import PricesTariffCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.tariff import TariffRepository
from src.services.tariff import TariffService

router = Router()


@router.callback_query(F.data == "tariffs")
async def tariffs_menu(
    callback: CallbackQuery,
    tariff_repo: TariffRepository,
    kb: InlineKB,
    state: FSMContext,
):
    await state.set_state(OrderTariffStates.choosing_tariff)
    await state.update_data(tariff_slug=None)

    tariffs = await tariff_repo.get_tariffs()
    text = "Список тарифов доступые для покупки:"

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.subscription.get_tariffs_keyboard(tariffs),
    )
    await callback.answer()


@router.callback_query(PricesTariffCallback.filter())
async def prices_tariff_menu(
    callback: CallbackQuery,
    callback_data: PricesTariffCallback,
    tariff_repo: TariffRepository,
    tariff_service: TariffService,
    kb: InlineKB,
    state: FSMContext,
):

    slug = callback_data.slug
    tariff = await tariff_repo.get_tariff_by_slug(slug)
    options = tariff_service.calculate_period_price(price=tariff.price)
    text = "Выберите срок действия подписки."

    await state.set_state(OrderTariffStates.choosing_period)
    await state.update_data(tariff_slug=slug)

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.subscription.get_tariff_prices(options),
    )
    await callback.answer()
