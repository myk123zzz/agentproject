"""Application configuration via environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """PolicyMind settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "PolicyMind"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "sqlite+aiosqlite:///policymind.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Read and validate environment config; tests override via dependency injection."""
    return Settings()


def validate_production_settings(settings: Settings) -> None:
    """Refuse default JWT, weak secrets, wildcard CORS, and missing dependency URLs."""
    if settings.ENVIRONMENT != "production":
        return

    forbidden = {"change-me", "changeme", "secret", "password", "default"}
    if settings.JWT_SECRET.lower() in forbidden:
        raise ValueError("Production must not use a default JWT_SECRET")
    if len(settings.JWT_SECRET) < 32:
        raise ValueError("Production JWT_SECRET must be at least 32 characters")
    if "*" in settings.CORS_ORIGINS:
        raise ValueError("Production CORS origins must not contain wildcard '*'")
