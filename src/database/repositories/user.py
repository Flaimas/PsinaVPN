from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.user import User
from sqlalchemy.dialects.postgresql import insert

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_tg_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя с переданным telegram_id"""
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(self, telegram_id: int, username: str | None) -> tuple[User, bool]:
        """
        Возвращает кортеж (User, bool).
        Если пользователь уже был в базе, возвращает (user, False).
        Если пользователя не было, создает его и возвращает (user, True).
        """
        user = await self.get_user_by_tg_id(telegram_id=telegram_id)
        if user:
            return user, False
        user = User(
            telegram_id=telegram_id,
            username=username
        )
        self.session.add(user)
        await self.session.flush()
        return user, True

    async def update_balance(self, telegram_id: int, new_balance: float) -> bool:
        """Обновляет баланс пользователя. Возвращает True, если запись была обновлена"""
        query = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(balance=new_balance)
        )
        
        result = await self.session.execute(query)
        return result.rowcount > 0