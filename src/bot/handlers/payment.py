from datetime import UTC, datetime

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import BuyTariffCallback, PaymentProcessCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.common.payment_texts import payment_texts
from src.core.enums import InvoiceOperation
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.subscription import SubscriptionRepository
from src.database.repositories.tariff import TariffRepository
from src.database.repositories.user import UserRepository
from src.scheams.payment import PaymentContext
from src.services.payment.exceptions import PaymentServiceError
from src.services.payment.payment import PaymentService
from src.services.tariff import TariffService

router = Router()


@router.callback_query(
    BuyTariffCallback.filter(),
    StateFilter(
        OrderTariffStates.buy_subscription,
        OrderTariffStates.extend_subscription,
        OrderTariffStates.change_subscription,
    ),
)
async def buy_tariff_menu(
    callback: CallbackQuery,
    callback_data: BuyTariffCallback,
    tariff_repo: TariffRepository,
    tariff_service: TariffService,
    sub_repo: SubscriptionRepository,
    kb: InlineKB,
    state: FSMContext,
):
    state_data = await state.get_data()
    user_state = await state.get_state()
    selected_tariff = state_data.get("tariff_id")
    user_sub_id = state_data.get("user_sub_id")

    days_left = None
    if user_state == OrderTariffStates.change_subscription and user_sub_id:
        user_subscription = await sub_repo.get_subscription_by_id(sub_id=user_sub_id)

        if not user_subscription:
            await callback.answer(
                "Ошибка: подписка не найдена. Перезапустите бота командой /start"
            )
            return
        days_left = (user_subscription.expired_at - datetime.now(UTC)).days
        days_left = max(0, days_left)

    if not selected_tariff:
        await callback.answer(payment_texts.SESSION_EXPIRED, show_alert=True)
        return

    tariff = await tariff_repo.get_active_tariff_by_id(selected_tariff)
    if not tariff:
        await callback.answer(payment_texts.TARIFF_NOT_FOUND, show_alert=True)
        return

    subscription = tariff_service.calculate_subscription_price(
        price=tariff.price, target_period=callback_data.days_amount
    )

    await state.update_data(
        price=subscription.discount_price,
        period=callback_data.days_amount,
        tariff_id=tariff.id,
    )

    text = payment_texts.format_order_confirmation(
        selected_tariff=tariff,
        days_amount=callback_data.days_amount,
        base_price=subscription.base_price,
        discount_price=subscription.discount_price,
        days_left=days_left,
    )

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.payment.select_payment_provider_kb(tariff_id=selected_tariff),
    )
    await callback.answer()


@router.callback_query(
    PaymentProcessCallback.filter(),
    StateFilter(
        OrderTariffStates.buy_subscription,
        OrderTariffStates.extend_subscription,
        OrderTariffStates.change_subscription,
    ),
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
    user = await user_repo.get_user_by_tg_id(telegram_id=callback.from_user.id)

    await state.set_state(OrderTariffStates.waiting_for_payment)

    if user is None:
        await callback.answer(payment_texts.USER_NOT_FOUND, show_alert=True)
        return

    try:
        ctx = PaymentContext(user=user, provider=callback_data.provider, **state_data)
    except ValidationError as e:
        print(e)
        await callback.answer(payment_texts.DATA_ERROR, show_alert=True)
        return

    if ctx.operation != InvoiceOperation.BUY and ctx.user_sub_id is None:
        await callback.answer(
            "Ошибка, перезапусnите бота командой /start", show_alert=True
        )
        return

    try:
        _, payment_url = await payment_service.create_invoice(
            tariff_id=ctx.tariff_id,
            period=ctx.period,
            provider_type=ctx.provider,
            amount=ctx.price,
            description=f"Пополнение для {callback.from_user.id}",
            user_id=user.id,
            subscription_id=ctx.user_sub_id,
            operation=ctx.operation,
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
