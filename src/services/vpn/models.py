from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TrafficLimitStrategy(str, Enum):
    NO_RESET = "NO_RESET"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


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


class InternalSquad(RemnawaveBaseModel):
    """Внутренний сквад, к которому привязан пользователь."""

    uuid: UUID
    name: str


class RemnawaveCreateUserRequest(RemnawaveBaseModel):
    username: str
    telegram_id: int | None = None
    email: str | None = None
    expire_at: datetime
    traffic_limit_bytes: int
    traffic_limit_strategy: TrafficLimitStrategy = TrafficLimitStrategy.NO_RESET
    status: Status = Status.ACTIVE
    active_internal_squads: list[UUID] | None = None


class RemnawaveUpdateUser(RemnawaveBaseModel):
    id: int
    expire_at: datetime
    status: Status = Status.ACTIVE
    traffic_limit_bytes: int
    used_traffic_bytes: int = 0
    active_internal_squads: list[UUID] | None = None


class RemnawaveUserResponse(RemnawaveBaseModel):
    id: int
    short_uuid: str
    telegram_id: int | None = None
    status: Status
    expire_at: datetime
    traffic_limit_bytes: int = 0
    used_traffic_bytes: int = 0
    subscription_url: str
    active_internal_squads: list[InternalSquad] = Field(default_factory=list)
