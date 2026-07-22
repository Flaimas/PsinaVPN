from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.services.tariff import TariffService
from src.services.payment.payment import PaymentService
from src.database.repositories.tariff import TariffRepository
from src.bot.keyboards.main_kb import InlineKeyboards
from src.services.vpn.mock import MockVPNClient
from src.database.repositories.user import UserRepository
from src.database.repositories.subscription import SubscriptionRepository
from redis.asyncio import Redis

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
        event: TelegramObject, 
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_pool() as session:
            data["tariff_repo"] = TariffRepository(session)
            data["user_repo"] = UserRepository(session)
            data["sub_repo"] = SubscriptionRepository(session)
            data["payment_service"] =  PaymentService(session=session, vpn_client=MockVPNClient())
            data["tariff_service"] = TariffService()
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e
            
class InlineKeyboardsMiddleware(BaseMiddleware):
    def __init__(self, keyboards: InlineKeyboards):
        self.keyboards = keyboards
        super().__init__()
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
        event: TelegramObject, 
        data: Dict[str, Any]
    ) -> Any:
        data["kb"] = self.keyboards
        return await handler(event, data)
    
class ShadowBanMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis):
        super().__init__()
        self.redis = redis

    async def __call__(
        self, 
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
        event: TelegramObject, 
        data: Dict[str, Any]
    ) -> Any:
        
        user: User = data.get("event_from_user")
        if user is not None:
            is_banned = await self.redis.sismember("banned_users", user.id)
            if is_banned:
                return
    
        return await handler(event, data)