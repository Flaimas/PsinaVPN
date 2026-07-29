from typing import Any

from src.core.exceptions import AppError


class RemnawaveError(AppError):
    """Базовое исключение для всех косяков Remnawave."""

    def __init__(self, message: str = "Ошибка VPN сервиса", payload: Any = None):
        super().__init__(message)
        self.message = message
        self.payload = payload


class RemnawaveConnectionError(RemnawaveError):
    """Ошибка на стороне сети, вызывается при ошибках HTTPX"""


class RemnawaveNotFoundError(RemnawaveError):
    """Ресурс не найден (400)"""


class RemnawaveValidationError(RemnawaveError):
    """Панель не приняла данные / 400 Bad Request."""


class RemnawaveServerError(RemnawaveError):
    """Упал Nginx, сама панель или 500+."""


class RemnawaveUnexpectedStatusError(RemnawaveError):
    """Неизвестная ошибка"""
