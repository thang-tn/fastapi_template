"""Web app configurations."""
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings."""

    environment: str = "development"
    debug: bool = False
    json_log_enabled: bool = True
