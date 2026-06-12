from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Splitly"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str  # e.g. postgresql://user:pass@host/dbname
    ASYNC_DATABASE_URL: str  # e.g. postgresql+asyncpg://user:pass@host/dbname

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Resend (email)
    RESEND_API_KEY: str
    EMAIL_FROM: str = "Splitly <noreply@splitly.app>"

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
