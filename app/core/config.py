from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "async-fetcher"

    environment: str = Field(
        default="development",
        description="Application environment.",
    )

    debug: bool = False

    request_timeout: float = Field(
        default=10.0,
        gt=0,
        description="HTTP request timeout in seconds.",
    )

    max_concurrency: int = Field(
        default=20,
        gt=0,
        description="Maximum number of concurrent HTTP requests.",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries after a failed request.",
    )

    retry_base_delay: float = Field(
        default=0.5,
        gt=0,
        description="Base delay used for exponential backoff.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
