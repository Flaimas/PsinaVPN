from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.user import UserRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.services.vpn.base import BaseVPNClient
from src.database.models.user import User
from datetime import datetime, timezone, timedelta

class PaymentService:
    def __init__(self, session: AsyncSession, vpn_client: BaseVPNClient):
        self.session = session
        self.user_repo = UserRepository(self.session)
        self.sub_repo = SubscriptionRepository(self.session)
        self.vpn_client = vpn_client

    async def pay_with_balance(self, telegram_id: int, price: float) -> tuple[bool, User | None]:
        """
        Ищет юзера по его telegram_id и списывает сумму, переданную в этот метод.
        Если у юзера достаточно денег - списывает их и возвращает True, иначе False
        """
        user = await self.user_repo.get_user_by_tg_id(telegram_id=telegram_id)
        if not user or user.balance < price:
            return False, None
        
        new_balance = user.balance - price
        result = await self.user_repo.update_balance(telegram_id=telegram_id, new_balance=new_balance)
        return result, user

    async def buy_tariff(
        self, 
        telegram_id: int, 
        price: float, 
        tariff_id: int, 
        period: int, 
        activate: bool = True
    ) -> bool:
        status, user = await self.pay_with_balance(telegram_id=telegram_id, price=price)

        if not status:
            return False
        
        now = datetime.now(tz=timezone.utc)
        days_to_add = timedelta(days=period)
        future_date = now + days_to_add
        
        sub_url = await self.vpn_client.create_user(telegram_id=telegram_id)

        subscription = await self.sub_repo.add_subscription(
            user_id=user.id,
            tariff_id=tariff_id,
            sub_url=sub_url,
            expired_at=future_date,
            is_active=activate
        )

        return bool(subscription)