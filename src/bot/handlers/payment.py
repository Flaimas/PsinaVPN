from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import BuyTariffCallback, PaymentProcessCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.common.payment_texts import payment_texts
from src.core.enums import InvoiceOperation
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.tariff import TariffRepository
from src.database.repositories.user import UserRepository
from src.services.payment.exceptions import PaymentServiceError
from src.services.payment.payment import PaymentService
from src.services.tariff import TariffService

router = Router()


@router.callback_query(
    BuyTariffCallback.filter(),
    StateFilter(
        OrderTariffStates.choosing_period, OrderTariffStates.extend_subscription
    ),
)
async def buy_tariff_menu(
    callback: CallbackQuery,
    callback_data: BuyTariffCallback,
    tariff_repo: TariffRepository,
    tariff_service: TariffService,
    kb: InlineKB,
    state: FSMContext,
):
    state_data = await state.get_data()
    slug = state_data.get("tariff_slug")

    if not slug:
        await callback.answer(payment_texts.SESSION_EXPIRED, show_alert=True)
        return

    tariff = await tariff_repo.get_tariff_by_slug(slug)
    if not tariff:
        await callback.answer(payment_texts.TARIFF_NOT_FOUND, show_alert=True)
        return

    subscription = tariff_service.calculate_subscription_price(
        price=tariff.price, target_period=callback_data.days_amount
    )

    await state.set_state(OrderTariffStates.waiting_for_payment)
    await state.update_data(
        price=subscription.discount_price,
        period=callback_data.days_amount,
        tariff_id=tariff.id,
    )

    text = payment_texts.format_order_confirmation(
        tariff_name=tariff.name,
        days_amount=callback_data.days_amount,
        base_price=subscription.base_price,
        discount_price=subscription.discount_price,
    )

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.payment.select_payment_provider_kb(slug),
    )
    await callback.answer()


@router.callback_query(
    PaymentProcessCallback.filter(), OrderTariffStates.waiting_for_payment
)
async def payment_process(
    callback: CallbackQuery,
    callback_data: PaymentProcessCallback,
    state: FSMContext,
    kb: InlineKB,
    user_repo: UserRepository,
    payment_service: PaymentService,
):
    state_data = await state.get_data()
    price = state_data.get("price")
    tariff_id = state_data.get("tariff_id")
    period_days = state_data.get("period")
    user_sub_id = state_data.get("user_sub_id")

    user = await user_repo.get_user_by_tg_id(telegram_id=callback.from_user.id)

    if not price or not user or not tariff_id or not period_days:
        await callback.answer(payment_texts.DATA_ERROR, show_alert=True)
        return

    try:
        operation = InvoiceOperation.EXTEND if user_sub_id else InvoiceOperation.BUY
        _, payment_url = await payment_service.create_invoice(
            tariff_id=int(tariff_id),
            period=int(period_days),
            provider_type=callback_data.provider,
            amount=float(price),
            description=f"Пополнение для {callback.from_user.id}",
            user_id=user.id,
            subscription_id=user_sub_id,
            operation=operation,
        )
    except PaymentServiceError as e:
        await callback.answer(str(e), show_alert=True)
        return

    msg = await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=payment_texts.PAYMENT_LINK_CAPTION,
        reply_markup=kb.payment.url_payment(url=payment_url),
    )
    if isinstance(msg, Message):
        await state.update_data(payment_msg_id=msg.message_id)
    await callback.answer()
