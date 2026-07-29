from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.bot.keyboards import InlineKB
from src.bot.keyboards.callbacks import BuyTariffCallback, PaymentProcessCallback
from src.bot.states import OrderTariffStates
from src.bot.utils.message import edit_callback_media
from src.core.media_config import DEFAULT_PHOTO
from src.database.repositories.tariff import TariffRepository
from src.database.repositories.user import UserRepository
from src.services.payment.exceptions import PaymentServiceError
from src.services.payment.payment import PaymentService
from src.services.tariff import TariffService
from src.services.vpn.exceptions import RemnawaveError

router = Router()


@router.callback_query(BuyTariffCallback.filter(), OrderTariffStates.choosing_period)
async def buy_tariff_menu(
    callback: CallbackQuery,
    callback_data: BuyTariffCallback,
    tariff_repo: TariffRepository,
    tariff_service: TariffService,
    kb: InlineKB,
    state: FSMContext,
):
    user_data = await state.get_data()
    slug = user_data.get("tariff_slug")

    if not slug:
        await callback.answer(
            "Сессия истекла. Пожалуйста, выберите тариф заново.", show_alert=True
        )
        return

    tariff = await tariff_repo.get_tariff_by_slug(slug)
    subscription = tariff_service.calculate_subscription_price(
        price=tariff.price, targert_period=callback_data.days_amount
    )

    await state.set_state(OrderTariffStates.waiting_for_payment)
    await state.update_data(
        price=subscription.discount_price,
        period=callback_data.days_amount,
        tariff_id=tariff.id,
    )

    if subscription.base_price == subscription.discount_price:
        price_text = f"Цена: {subscription.discount_price} руб."
    else:
        price_text = (
            f"<s>Старая цена: {subscription.base_price} руб.</s>\n"
            f"Цена со скидкой: {subscription.discount_price} руб. 🔥"
        )
    text = (
        f"Подтверждение заказа\n\n"
        f"📋 Тариф: {tariff.name}\n"
        f"Срок: {callback_data.days_amount} дней.\n"
        f"{price_text}\n\n"
        f"Выберите способ оплаты:"
    )

    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.payment.select_payment_provider_kb(slug),
    )
    await callback.answer()


@router.callback_query(F.data == "buy", OrderTariffStates.waiting_for_payment)
async def buy_tariff_handler(
    callback: CallbackQuery,
    state: FSMContext,
    payment_service: PaymentService,
    tariff_repo: TariffRepository,
    user_repo: UserRepository,
    kb: InlineKB,
):
    user_data = await state.get_data()
    price = user_data.get("price")
    period = user_data.get("period")
    slug = user_data.get("tariff_slug")

    user = await user_repo.get_user_by_tg_id(telegram_id=callback.from_user.id)
    if not user:
        text = f"Ошибка, пользователь c telegram_id:{callback.from_user.id} не найден в системе."
        await edit_callback_media(
            callback=callback,
            media=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.start.return_to_start(),
        )
        callback.answer()
        return

    if not price or not period or not slug:
        text = "Ошибка, при получении параметров подписки, попробуйте снова."
        await edit_callback_media(
            callback=callback,
            media=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.start.return_to_start(),
        )
        callback.answer()
        return

    if user.balance < float(price):
        text = f"Недостаточно средств на счете!\nВаш баланс: {user.balance} руб.\nЧто бы пополнить баланс перейдите в меню 'Пополнить баланс'"
        await edit_callback_media(
            callback=callback,
            media=DEFAULT_PHOTO,
            caption=text,
        )
        callback.answer()
        return

    tariff_id_in_db = await tariff_repo.get_tariff_by_slug(slug=slug)

    try:
        succes_payment = await payment_service.buy_tariff_with_balance(
            user_id=user.id,
            amount=price,
            tariff_id=tariff_id_in_db.id,
            months_sub=int(period),
            activate=True,
        )
    except RemnawaveError:
        logger.error(
            "Ошибка создания VPN-юзера при покупке тарифа | user_id: {} | tariff_id: {} | amount: {}",
            user.id,
            tariff_id_in_db.id,
            price,
        )
        await callback.answer(
            "Не удалось создать подписку на сервере. Средства не списаны, попробуйте снова.",
            show_alert=True,
        )
        return

    if not succes_payment:
        text = "Ошибка шлюза оплаты, попробуйте снова."
        await edit_callback_media(
            callback=callback,
            media=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.payment.retry_payment(),
        )
        callback.answer()
        return
    else:
        text = "Спасибо за покупку!\nВаша ссылка для подключения:\n<code>http://example.com/vpn_exmple</code>"
        await edit_callback_media(
            callback=callback,
            media=DEFAULT_PHOTO,
            caption=text,
            reply_markup=kb.payment.succes_payment(),
        )

    await callback.answer()


@router.callback_query(PaymentProcessCallback.filter())
async def paymet_process(
    callback: CallbackQuery,
    callback_data: PaymentProcessCallback,
    state: FSMContext,
    kb: InlineKB,
    user_repo: UserRepository,
    payment_service: PaymentService,
):
    user_data = await state.get_data()
    price = user_data.get("price")
    tariff_id = user_data.get("tariff_id")
    period_days = user_data.get("period")
    user = await user_repo.get_user_by_tg_id(telegram_id=callback.from_user.id)

    if not price or not user or not tariff_id or not period_days:
        return

    try:
        user_invoice, payment_url = await payment_service.create_invoice(
            tariff_id=int(tariff_id),
            period=int(period_days),
            provider_type=callback_data.provider,
            amount=float(price),
            description=f"Пополнение для {callback.from_user.id}",
            user_id=user.id,
        )
    except PaymentServiceError as e:
        await callback.answer(f"{e}", show_alert=True)

    text = "Ссылка для оплаты"
    await edit_callback_media(
        callback=callback,
        media=DEFAULT_PHOTO,
        caption=text,
        reply_markup=kb.payment.url_payment(url=payment_url),
    )
