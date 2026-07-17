from abc import ABC, abstractmethod

class BaseVPNClient(ABC):
    @abstractmethod
    async def create_user(self, telegram_id: int) -> str:
        """Абстрактный метод создания пользователя"""
        pass

    @abstractmethod
    async def delete_user(self, telegram_id: int) -> None:
        """Абстрактный метод удаления пользователя"""
        pass
