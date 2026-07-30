from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models.subscription import Subscription
from src.database.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_tg_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя с переданным telegram_id"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_subscriptions(self, telegram_id: int) -> User | None:
        query = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(joinedload(User.subscriptions).joinedload(Subscription.tariff))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_user_by_user_id(self, user_id: int) -> User | None:
        """Возвращает пользователя с переданным telegram_id"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, username: str | None) -> User:
        """Добавляет юзера в БД"""
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_balance(self, user_id: int, new_balance: float) -> bool:
        """Обновляет баланс пользователя. Возвращает True, если запись была обновлена"""
        query = update(User).where(User.id == user_id).values(balance=new_balance)

        result = await self.session.execute(query)
        return result.rowcount > 0  # type: ignore

    async def get_banned_tg_user_ids(self) -> list[int]:
        """Возвращает список всех забаненных пользователей"""
        stmt = select(User.telegram_id).where(User.is_banned)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
