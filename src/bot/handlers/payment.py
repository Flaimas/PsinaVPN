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
    sub_repo: SubscriptionRepository,
    kb: InlineKB,
    state: FSMContext,
):
    user_state = await state.get_state()

    user_subscription = None
    if user_state == OrderTariffStates.change_subscription:
        user_subscription = await sub_repo.get_by_tg_id_with_relations(
            telegram_id=callback.from_user.id
        )
        if not user_subscription:
            await callback.answer(
                "Что бы сменить подписку. у вас должна быть другая активная подписка!"
            )
            return
        operation = InvoiceOperation.CHANGE

    elif user_state == OrderTariffStates.extend_subscription:
        operation = InvoiceOperation.EXTEND

    elif user_state == OrderTariffStates.buy_subscription:
        operation = InvoiceOperation.BUY

    tariff_option = await tariff_repo.get_tariff_option_by_id(
        callback_data.tariff_option_id
    )

    if not tariff_option:
        await callback.answer(
            "Для данного тарифа нет доступных опций.", show_alert=True
        )
        return

    selected_tariff = await tariff_repo.get_active_tariff_by_id(tariff_option.tariff_id)
    if not selected_tariff:
        await callback.answer(payment_texts.TARIFF_NOT_FOUND, show_alert=True)
        return

    text = payment_texts.format_order_confirmation(
        selected_tariff=selected_tariff,
        tariff_option=tariff_option,
        user_subscription=user_subscription,
    )

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.payment.select_payment_provider_kb(
            tariff_id=selected_tariff.id,
            operation=operation,
            tariff_option_id=tariff_option.id,
        ),
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
    tariff_repo: TariffRepository,
):
    user = await user_repo.get_user_with_subscription(telegram_id=callback.from_user.id)
    tariff_option = await tariff_repo.get_tariff_option_by_id(
        callback_data.tariff_option_id
    )

    await state.set_state(OrderTariffStates.waiting_for_payment)

    if user is None:
        await callback.answer(payment_texts.USER_NOT_FOUND, show_alert=True)
        return
    if tariff_option is None:
        await callback.answer("Ошибка, опция тарифа не найдена.", show_alert=True)
        return
    user_subscription = user.subscription
    user_sub_id = None if not user_subscription else user_subscription.id
    try:
        ctx = PaymentContext(
            user=user,
            provider=callback_data.provider,
            operation=callback_data.operation,
            tariff_id=tariff_option.tariff_id,
            price=tariff_option.price,
            period=tariff_option.period_days,
            user_sub_id=user_sub_id,
        )
    except ValidationError as e:
        print(e)
        await callback.answer(payment_texts.DATA_ERROR, show_alert=True)
        return

    if ctx.operation != InvoiceOperation.BUY and ctx.user_sub_id is None:
        await callback.answer(
            "Ошибка, подписка для продления/измененеия не найдена!", show_alert=True
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
