from pathlib import Path

from pydantic import Field, HttpUrl, TypeAdapter, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import PaymentProvider

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    UVICORN_HOST: str
    UVICORN_PORT: int

    BOT_TOKEN: str
    USE_WEBHOOK: bool = False
    TELEGRAM_SECRET_TOKEN: str | None = None
    TELEGRAM_WH_BASE_URL: str | None = None
    ADMIN_IDS: list[str] | None = None
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

    LOG_LEVEL: str = "INFO"
    START_BALANCE: float = 0.0
    PAYMENT_PROVIDERS: tuple[PaymentProvider, ...] = (PaymentProvider.YOOKASSA,)
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str

    PERIODS_SUBSCRIPTION: list[int] = [30, 60, 90, 120]
    DISCOUNT_FOR_PERIOD: list[int] | None = None
    MAX_DISCOUNT: int = Field(default=50, gt=0, lt=100)

    DEBUG: bool = True

    @field_validator("REMNAWAVE_BASE_URL", mode="before")
    @classmethod
    def clean_and_validate_url(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().rstrip("/")
        try:
            TypeAdapter(HttpUrl).validate_python(v)
        except Exception:
            raise ValueError("REMNAWAVE_BASE_URL должен быть валидным HTTP/HTTPS URL")

        return v

    @computed_field
    @property
    def telegram_web_hook_url(self) -> str | None:
        if not self.USE_WEBHOOK:
            return None

        if not self.TELEGRAM_WH_BASE_URL:
            raise ValueError(
                "TELEGRAM_WH_BASE_URL must be set when USE_WEBHOOK is True"
            )

        base_url = str(self.TELEGRAM_WH_BASE_URL).rstrip("/")
        return f"{base_url}/webhooks/telegram"

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
