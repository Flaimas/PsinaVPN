from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.invoice import Invoice
from src.database.repositories.user import UserRepository


@dataclass(frozen=True)
class BonusResult:
    referrer_tg_id: int
    amount: Decimal


class BonusService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository) -> None:
        self.session: AsyncSession = session
        self.user_repo: UserRepository = user_repo

    async def process_referral_bonus(self, invoice: Invoice) -> BonusResult | None:
        referrer_id = invoice.user.referrer_id
        if referrer_id is None:
            return None

        bonus_amount = invoice.amount * Decimal("0.20")
        referrer = await self.user_repo.increment_balance(
            user_id=referrer_id, amount=bonus_amount
        )
        return BonusResult(referrer_tg_id=referrer.telegram_id, amount=bonus_amount)
