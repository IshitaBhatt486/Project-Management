from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project Management API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/project_management"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    session_secret: str = "development-only-change-me"
    session_expire_days: int = 7
    session_cookie_secure: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()