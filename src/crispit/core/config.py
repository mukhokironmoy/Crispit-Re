from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CRISPIT_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Crispit"
    app_environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: str = ""
    test_database_url: str | None = None
    supabase_database_url: str | None = None

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("CRISPIT_DATABASE_URL must be set.")

        return value


@lru_cache
def get_settings() -> Settings:
    """Return one shared settings instance for the current process."""

    return Settings()