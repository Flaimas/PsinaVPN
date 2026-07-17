from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.subscription import Subscription
from sqlalchemy.dialects.postgresql import insert

class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_subscription(self, user_id: int, sub_url: str, is_active: bool = True) -> Subscription:
        subscription = Subscription(
            user_id=user_id, 
            sub_url=sub_url, 
            is_active=is_active
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription