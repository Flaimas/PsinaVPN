from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import PaymentProvider

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    BOT_TOKEN: str
    TELEGRAM_SECRET_TOKEN: str
    ADMIN_IDS: str
    PROXY_URL: str | None = None

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int = 6379

    REMNAWAVE_BASE_URL: str
    REMNAWAVE_API_TOKEN: str

    LOG_LEVEL: str = "DEBUG"
    START_BALANCE: float = 0.0
    PAYMENT_PROVIDERS: tuple[PaymentProvider, ...] = (
        PaymentProvider.YOOKASSA,
        PaymentProvider.BALANCE,
    )
    YOOKASSA_SHOP_ID: str = "test_shop_id_123456"
    YOOKASSA_SECRET_KEY: str = "test_secret_key_123456"

    PERIODS_SUBSCRIPTION: list[int] = [30, 60, 90, 120, 150]
    DISCOUNT_FOR_PERIOD: list[int] | None = None
    MAX_DISCOUNT: int = Field(default=50, gt=0, lt=100)

    DEBUG: bool = True

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return (
                f"redis://{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
            )
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()  # type: ignore
