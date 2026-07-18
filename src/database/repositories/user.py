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

    async def get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        """Возвращает пользователя, если его нет — создает"""
        insert_stmt = (
            insert(User)
            .values(telegram_id=telegram_id, username=username)
        )

        upsert_stmt = (
            insert_stmt.on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_={"username": username}
            )
            .returning(User)
        )

        result = await self.session.execute(upsert_stmt)
        return result.scalar_one()

    async def update_balance(self, telegram_id: int, new_balance: float) -> bool:
        """Обновляет баланс пользователя. Возвращает True, если запись была обновлена"""
        query = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(balance=new_balance)
        )
        
        result = await self.session.execute(query)
        return result.rowcount > 0