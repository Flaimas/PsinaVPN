class AppError(Exception):
    """Базовое исключение для всех ошибок сервиса"""

    def __init__(self, message: str | None = "Ошибка приложения!") -> None:
        self.message = message or self.message
        super().__init__(message)
