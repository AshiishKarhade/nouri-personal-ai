"""Application configuration loaded from environment variables via Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # App config
    timezone: str = "Asia/Kolkata"
    database_url: str = "sqlite+aiosqlite:///data/transformation.db"
    log_level: str = "INFO"

    # Google Sheets
    google_sheets_id: str = ""
    google_service_account_file: str = "credentials/google-service-account.json"

    # Dashboard
    dashboard_port: int = 8000
    dashboard_api_token: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
