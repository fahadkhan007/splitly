from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Splitly"
    DEBUG: bool = False

    DATABASE_URL: str
    ASYNC_DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    RESEND_API_KEY: str
    EMAIL_FROM: str = "Splitly <noreply@splitly.app>"

    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
