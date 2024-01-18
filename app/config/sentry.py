"""Sentry Configurations."""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class SentrySettings(BaseSettings):
    """Sentry setting for the application."""

    sentry_dsn: str = ""
    sentry_traces_sample_rate: str = ""


sentry_settings = SentrySettings()
