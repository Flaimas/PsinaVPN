from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest

from src.database.models.invoice import Invoice
from src.database.models.subscription import Subscription
from src.database.models.tariff import Tariff
from src.database.models.user import User
from src.database.repositories.invoice import InvoiceRepository
from src.services.notification import NotificationService
from src.services.payment_processor import ProcessPaymentUseCase
from src.services.subscription import GrantResult, SubscriptionService


@pytest.fixture
def session_mock() -> AsyncMock:
    session = AsyncMock()

    @asynccontextmanager
    async def fake_begin_nested():
        yield None

    session.begin_nested = fake_begin_nested
    return session


@pytest.fixture
def invoice_repo_mock():
    return AsyncMock(spec=InvoiceRepository)


@pytest.fixture
def subscription_service_mock() -> AsyncMock:
    return AsyncMock(spec=SubscriptionService)


@pytest.fixture
def notifier_mock() -> AsyncMock:
    return AsyncMock(spec=NotificationService)


@pytest.fixture
def use_case(
    session_mock, invoice_repo_mock, subscription_service_mock, notifier_mock
) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(
        session=session_mock,
        invoice_repo=invoice_repo_mock,
        subscription_service=subscription_service_mock,
        notifier=notifier_mock,
    )


async def test_returns_false_if_payment_aleready_process(
    use_case, invoice_repo_mock, subscription_service_mock, notifier_mock
):
    invoice_repo_mock.mark_as_paid_if_pending.return_value = None
    result = await use_case.execute(provider_payment_id="pay_228")

    assert result is False
    invoice_repo_mock.get_with_relations.assert_not_called()
    subscription_service_mock.grant_subscription_for_invoice.assert_not_called()
    notifier_mock.notify_payment_success.assert_not_called()


async def test_execute_grants_subscription_and_notifies_user(
    use_case, invoice_repo_mock, subscription_service_mock, notifier_mock
):
    user = User(id=5, telegram_id=555)
    tariff = Tariff(id=10, name="Default")
    marked_invoice = Invoice(id=7, operation="buy", tariff=tariff)
    full_invoice = Invoice(
        id=7, operation="extend", user=user, tariff=Tariff(id=88, name="Other")
    )

    sub = Subscription(id=90, user=user)
    grant_result = GrantResult(subscription=sub, converted_days=5)

    invoice_repo_mock.mark_as_paid_if_pending.return_value = marked_invoice
    invoice_repo_mock.get_with_relations.return_value = full_invoice
    subscription_service_mock.grant_subscription_for_invoice.return_value = grant_result

    result = await use_case.execute(provider_payment_id="pay_222")

    invoice_repo_mock.get_with_relations.assert_called_once_with(invoice_id=7)
    subscription_service_mock.grant_subscription_for_invoice.assert_called_once_with(
        invoice=full_invoice
    )

    assert full_invoice.subscription_id == 90
    assert full_invoice.converted_days == 5

    notifier_mock.notify_payment_success.assert_called_once_with(
        telegram_id=555, operation="buy", user_sub=sub, user_tariff=tariff
    )

    assert result is True
