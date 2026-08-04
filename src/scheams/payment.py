from pydantic import BaseModel, ConfigDict

from src.core.enums import InvoiceOperation, PaymentProvider
from src.database.models.user import User


class PaymentContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: User
    tariff_id: int
    provider: PaymentProvider
    price: float
    period: int
    operation: InvoiceOperation
    user_sub_id: int | None = None
