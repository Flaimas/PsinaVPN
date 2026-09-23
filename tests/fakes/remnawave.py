import random
import uuid

from src.services.vpn.base import BaseVPNClient
from src.services.vpn.models import (
    InternalSquad,
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    RemnawaveUserResponse,
    Status,
)


class FakeRemnawaveClient(BaseVPNClient):
    def __init__(self) -> None:
        self.is_open: bool = False
        # Хранилище юзеров в памяти: {user_id: RemnawaveUserResponse}
        self.users: dict[int, RemnawaveUserResponse] = {}

    async def open(self) -> None:
        self.is_open = True

    async def close(self) -> None:
        self.is_open = False

    async def create_user(
        self, payload: RemnawaveCreateUserRequest
    ) -> RemnawaveUserResponse:
        user_id = random.randint(1, 100000)
        short_uuid = uuid.uuid4().hex[:8]

        squads = [
            InternalSquad(uuid=u, name="Test Squad")
            for u in (payload.active_internal_squads or [])
        ]

        user = RemnawaveUserResponse(
            id=user_id,
            short_uuid=short_uuid,
            status=payload.status,
            telegram_id=payload.telegram_id,
            subscription_url=f"https://fake-vpn.local/sub/{short_uuid}",
            expire_at=payload.expire_at,
            traffic_limit_bytes=payload.traffic_limit_bytes,
            active_internal_squads=squads,
        )

        self.users[user_id] = user
        return user

    async def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    async def get_user_by_id(self, user_id: int) -> RemnawaveUserResponse | None:
        return self.users.get(user_id)


async def update_user(self, payload: RemnawaveUpdateUser) -> RemnawaveUserResponse:
    existing_user: RemnawaveUserResponse | None = self.users.get(payload.id)

    # 1. Если status передан в payload — берем его.
    # Если нет и есть existing_user — берем его статус.
    # Иначе берем дефолтный Status.ACTIVE из Enum.
    if payload.status is not None:
        status = payload.status
    elif existing_user is not None:
        status = existing_user.status
    else:
        status = Status.ACTIVE  # или Status.active в зависимости от твоего Enum

    expire_at = payload.expire_at or (
        existing_user.expire_at if existing_user else None
    )
    short_uuid = existing_user.short_uuid if existing_user else uuid.uuid4().hex[:8]
    telegram_id = existing_user.telegram_id if existing_user else 0

    # 2. Разбор отрядов (squads)
    if payload.active_internal_squads is not None:
        squads = [
            InternalSquad(uuid=u, name="Test Squad")
            for u in payload.active_internal_squads
        ]
    else:
        squads = existing_user.active_internal_squads if existing_user else []

    # 3. Разбор лимита трафика
    traffic_limit = (
        payload.traffic_limit_bytes
        if payload.traffic_limit_bytes is not None
        else (existing_user.traffic_limit_bytes if existing_user else 0)
    )

    updated_user = RemnawaveUserResponse(
        id=payload.id,
        short_uuid=short_uuid,
        telegram_id=telegram_id,
        status=status,
        expire_at=expire_at,
        subscription_url=f"https://fake-vpn.local/sub/{short_uuid}",
        traffic_limit_bytes=traffic_limit,
        active_internal_squads=squads,
    )

    self.users[payload.id] = updated_user
    return updated_user
