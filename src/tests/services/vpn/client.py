import uuid

from src.services.vpn.models import RemnawaveCreateUserRequest, RemnawaveUserResponse


class FakeRemnawaveClient:
    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def create_user(
        self, payload: RemnawaveCreateUserRequest
    ) -> RemnawaveUserResponse:
        random_uuid = uuid.uuid4()

        return RemnawaveUserResponse(
            uuid=random_uuid,
            status=payload.status,
            telegram_id=payload.telegram_id,
            subscription_url=f"https://fake-vpn.local/sub/{random_uuid}",
            expire_at=payload.expire_at,
        )
