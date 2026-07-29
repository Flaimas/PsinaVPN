from abc import ABC, abstractmethod


class BaseVPNClient(ABC):
    @abstractmethod
    async def create_user(self, user_id: int) -> str:
        """Абстрактный метод создания пользователя"""

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        """Абстрактный метод удаления пользователя"""
