from abc import ABC, abstractmethod

from .models import (
    RemnawaveCreateUserRequest,
    RemnawaveUpdateUser,
    RemnawaveUserResponse,
)


class BaseVPNClient(ABC):
    @abstractmethod
    async def open(self) -> None:
        """Инициализация клиента / сессии"""

    @abstractmethod
    async def close(self) -> None:
        """Закрытие соединения"""

    @abstractmethod
    async def create_user(
        self, payload: RemnawaveCreateUserRequest
    ) -> RemnawaveUserResponse:
        """Создание пользователя"""

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя (True - успешно, False - не найден)"""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> RemnawaveUserResponse | None:
        """Получение пользователя по ID"""

    @abstractmethod
    async def update_user(self, payload: RemnawaveUpdateUser) -> RemnawaveUserResponse:
        """Обновление данных пользователя"""
