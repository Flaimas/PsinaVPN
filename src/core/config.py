from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str
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

    LOG_LEVEL: str = "DEBUG"
    START_BALANCE: float = 0.0

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @computed_field
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
