import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TrafficLimitStrategy(str, Enum):
    NO_RESET = "NO_RESET"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    MONTH_ROLLING = "MONTH_ROLLING"


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    LIMITED = "LIMITED"
    EXPIRED = "EXPIRED"


class RemnawaveBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class RemnawaveCreateUserRequest(RemnawaveBaseModel):
    username: str
    telegram_id: int | None = None
    expire_at: datetime
    traffic_limit_bytes: int = 0
    traffic_limit_strategy: TrafficLimitStrategy = TrafficLimitStrategy.NO_RESET
    status: Status = Status.ACTIVE


class RemnawaveUpdateUser(RemnawaveBaseModel):
    uuid: UUID
    expire_at: datetime
    status: Status = Status.ACTIVE


class RemnawaveUserResponse(RemnawaveBaseModel):
    uuid: uuid.UUID
    telegram_id: int | None = None
    status: Status
    expire_at: datetime
    subscription_url: str
