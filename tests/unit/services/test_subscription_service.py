import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from src.core.enums import InvoiceOperation, TariffCategory
from src.database.models.invoice import Invoice
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff
from src.database.models.user import User
from src.database.repositories.subscription import SubscriptionRepository
from src.services.subscription import SubscriptionService
from src.services.vpn.client import RemnawaveClient
from src.services.vpn.models import (
    InternalSquad,
    RemnawaveUpdateUser,
    RemnawaveUserResponse,
    Status,
)


@pytest.fixture
def vpn_client_mock() -> AsyncMock:
    return AsyncMock(spec=RemnawaveClient)


@pytest.fixture
def sub_repo_mock() -> AsyncMock:
    return AsyncMock(spec=SubscriptionRepository)


@pytest.fixture
def service(vpn_client_mock, sub_repo_mock) -> SubscriptionService:
    return SubscriptionService(vpn_client=vpn_client_mock, sub_repo=sub_repo_mock)


@pytest.fixture
def user():
    return User(id=5, telegram_id=555)


@pytest.fixture
def tariff():
    return Tariff(
        id=5,
        name="Default",
        category=TariffCategory.DEFAULT,
        traffic_limit=50,
        device_limit=3,
        internal_squad_uuids=[uuid.uuid4()],
    )


async def test_raises_if_invoice_has_no_user(
    service, tariff, vpn_client_mock, sub_repo_mock
):
    invoice = Invoice(
        id=1,
        operation=InvoiceOperation.BUY,
        duration_days=30,
        amount=100,
        user=None,
        tariff=tariff,
    )

    with pytest.raises(ValueError, match="отсутствует пользователь"):
        await service.grant_subscription_for_invoice(invoice)

    vpn_client_mock.create_user.assert_not_called()
    sub_repo_mock.add_subscription.assert_not_called()


async def test_raises_if_tariff_is_none(
    service, vpn_client_mock, sub_repo_mock, tariff, user
):
    invoice = Invoice(
        id=1,
        operation=InvoiceOperation.BUY,
        duration_days=30,
        amount=100,
        user=user,
        tariff=None,
    )
    with pytest.raises(ValueError, match="отсутствует тариф"):
        await service.grant_subscription_for_invoice(invoice)
    vpn_client_mock.create_user.assert_not_called()
    sub_repo_mock.add_subscription.assert_not_called()


async def test_buy_creates_panel_user_and_saves_subscription(
    service, user, tariff, vpn_client_mock, sub_repo_mock
):
    invoice = Invoice(
        id=5,
        operation=InvoiceOperation.BUY,
        duration_days=30,
        amount=300,
        user=user,
        tariff=tariff,
    )

    panel_response = RemnawaveUserResponse(
        id=999,
        short_uuid="abc123",
        status=Status.ACTIVE,
        telegram_id=555,
        active_internal_squads=[InternalSquad(uuid=uuid.uuid4(), name="default")],
        subscription_url="https://fake-vpn.local/sub/abc123",
        expire_at=datetime.now(UTC) + timedelta(days=30),
    )

    vpn_client_mock.create_user.return_value = panel_response
    saved_sub = Subscription(id=50)
    sub_repo_mock.add_subscription.return_value = saved_sub

    result = await service.grant_subscription_for_invoice(invoice)

    payload = vpn_client_mock.create_user.call_args.args[0]
    assert payload.telegram_id == 555
    assert payload.traffic_limit_bytes == 50 * 1024**3
    assert payload.hwid_device_limit == 3

    sub_repo_mock.add_subscription.assert_called_once_with(
        user_id=5,
        tariff_id=5,
        tariff_category=TariffCategory.DEFAULT,
        sub_url="https://fake-vpn.local/sub/abc123",
        remnawave_user_id=999,
        expired_at=panel_response.expire_at,
        daily_rate=Decimal(10),
    )

    assert result.subscription is saved_sub
    assert result.converted_days == 0


async def test_extend_prolongs_panel_user_and_updates_subscription(
    service, user, tariff, vpn_client_mock, sub_repo_mock
):
    invoice = Invoice(
        id=5,
        operation=InvoiceOperation.EXTEND,
        duration_days=30,
        amount=300,
        user=user,
        tariff=tariff,
        subscription=Subscription(id=50, remnawave_user_id=228),
    )

    panel_response = RemnawaveUserResponse(
        id=228,
        short_uuid="abc123",
        status=Status.ACTIVE,
        telegram_id=555,
        active_internal_squads=[InternalSquad(uuid=uuid.uuid4(), name="default")],
        subscription_url="https://fake-vpn.local/sub/abc123",
        expire_at=datetime.now(UTC) + timedelta(days=30),
    )

    vpn_client_mock.extend_user_expiration_date.return_value = panel_response
    saved_sub = Subscription(id=50, remnawave_user_id=228)
    sub_repo_mock.update_subscription.return_value = saved_sub

    result = await service.grant_subscription_for_invoice(invoice)

    vpn_client_mock.extend_user_expiration_date.assert_called_once_with(
        user_remnawave_id=228,
        days=30,
    )

    sub_repo_mock.update_subscription.assert_called_once_with(
        sub_id=50,
        expired_at=panel_response.expire_at,
        daily_rate=Decimal(10),
    )

    assert result.subscription is saved_sub
    assert result.converted_days == 0


async def test_change_updates_panel_and_saves_new_tariff(
    service, user, vpn_client_mock, sub_repo_mock
):
    new_tariff = Tariff(
        id=7,
        name="Premium",
        category=TariffCategory.WHITELIST,
        traffic_limit=100,
        device_limit=5,
        internal_squad_uuids=[uuid.uuid4()],
    )

    current_expire_at = datetime(2026, 10, 1, tzinfo=UTC)

    invoice = Invoice(
        id=5,
        operation=InvoiceOperation.CHANGE,
        duration_days=30,
        amount=450,
        user=user,
        tariff=new_tariff,
        subscription=Subscription(
            id=50,
            remnawave_user_id=228,
            expired_at=current_expire_at,
            daily_rate=Decimal(10),
        ),
    )

    calc_result = SimpleNamespace(
        expire_at=datetime(2026, 11, 15, tzinfo=UTC),
        daily_rate=Decimal("12.5"),
        converted_days=7,
    )

    panel_response = RemnawaveUserResponse(
        id=228,
        short_uuid="abc123",
        status=Status.ACTIVE,
        telegram_id=555,
        active_internal_squads=[
            InternalSquad(uuid=new_tariff.internal_squad_uuids[0], name="default")
        ],
        subscription_url="https://fake-vpn.local/sub/abc123",
        expire_at=datetime(2026, 11, 16, tzinfo=UTC),
    )

    vpn_client_mock.update_user.return_value = panel_response
    saved_sub = Subscription(id=50)
    sub_repo_mock.update_subscription.return_value = saved_sub

    with patch(
        "src.services.subscription.SubscriptionCalculator.calculate_change_tariff",
        return_value=calc_result,
    ) as calc_mock:
        result = await service.grant_subscription_for_invoice(invoice)

    calc_kwargs = calc_mock.call_args.kwargs
    assert calc_kwargs["current_expire_at"] == current_expire_at
    assert calc_kwargs["duration_days"] == 30
    assert calc_kwargs["price"] == Decimal(450)
    assert calc_kwargs["daily_rate"] == Decimal(10)
    assert abs(calc_kwargs["now"] - datetime.now(UTC)) < timedelta(seconds=5)

    payload: RemnawaveUpdateUser = vpn_client_mock.update_user.call_args.kwargs[
        "payload"
    ]
    assert payload.id == 228
    assert payload.expire_at == calc_result.expire_at
    assert payload.hwid_device_limit == 5
    assert payload.traffic_limit_bytes == 100 * 1024**3
    assert payload.active_internal_squads == new_tariff.internal_squad_uuids

    sub_repo_mock.update_subscription.assert_called_once_with(
        sub_id=50,
        expired_at=panel_response.expire_at,
        tariff_id=7,
        daily_rate=Decimal("12.5"),
    )

    assert result.subscription == saved_sub
    assert result.converted_days == 7


@pytest.mark.parametrize(
    "operation, error_text",
    [
        (InvoiceOperation.EXTEND, "для продления"),
        (InvoiceOperation.CHANGE, "для смены"),
    ],
)
async def test_raises_if_invoice_has_no_subscription(
    service, tariff, user, vpn_client_mock, sub_repo_mock, operation, error_text
):
    invoice = Invoice(
        id=1,
        operation=operation,
        duration_days=30,
        amount=100,
        user=user,
        tariff=tariff,
        subscription=None,
    )

    with pytest.raises(ValueError, match=error_text):
        await service.grant_subscription_for_invoice(invoice)

    vpn_client_mock.extend_user_expiration_date.assert_not_called()
    vpn_client_mock.update_user.assert_not_called()
    sub_repo_mock.update_subscription.assert_not_called()
