import random
import uuid

from src.services.vpn.models import (
    InternalSquad,
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    RemnawaveUserResponse,
)


class FakeRemnawaveClient:
    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def create_user(
        self, payload: RemnawaveCreateUserRequest
    ) -> RemnawaveUserResponse:
        short_uuid = uuid.uuid4().hex[:8]
        squads = [
            InternalSquad(uuid=u, name="Test Squad")
            for u in (payload.active_internal_squads or [])
        ]
        return RemnawaveUserResponse(
            id=random.randint(1, 10000),
            short_uuid=short_uuid,
            status=payload.status,
            telegram_id=payload.telegram_id,
            subscription_url=f"https://fake-vpn.local/sub/{short_uuid}",
            expire_at=payload.expire_at,
            traffic_limit_bytes=payload.traffic_limit_bytes,
            active_internal_squads=squads,
        )

    async def update_user(self, payload: RemnawaveUpdateUser) -> RemnawaveUserResponse:
        short_uuid = uuid.uuid4().hex[:8]
        squads = [
            InternalSquad(uuid=u, name="Test Squad")
            for u in (payload.active_internal_squads or [])
        ]

        return RemnawaveUserResponse(
            id=payload.id,
            short_uuid=short_uuid,
            status=payload.status,
            expire_at=payload.expire_at,
            subscription_url=f"https://fake-vpn.local/sub/{short_uuid}",
            active_internal_squads=squads,
        )
