from src.services.vpn.base import BaseVPNClient
import asyncio

class MockVPNClient(BaseVPNClient):
    async def create_user(self, telegram_id: int) -> str:
        await asyncio.sleep(0.5)
        return f"vless://mock-uuid-12345@127.0.0.1:443?peer={telegram_id}"

    async def delete_user(self, telegram_id: int) -> None:
        await asyncio.sleep(0.5)
