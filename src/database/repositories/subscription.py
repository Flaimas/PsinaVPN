from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.subscription import Subscription
from typing import Literal

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
    
    async def delete_subscription(self, sub_id: int) -> None:
        stmt = (
            delete(Subscription)
            .where(Subscription.id == sub_id)
        )
        await self.session.execute(stmt)
    
    async def get_active_subscriptions_by_user(
        self,
        user_id: int, 
        is_active: Literal["all", "active", "inactive"] = "all"
    ) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        if is_active != "all":
            is_active_bool = (is_active == "active")
            stmt = stmt.where(Subscription.is_active == is_active_bool)
        stmt = stmt.options(joinedload(Subscription.tariff), joinedload(Subscription.user))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def deactivate_subscription(self, sub_id: int) -> None:
        stmt = (
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(is_active=False)
        )
        await self.session.execute(stmt)