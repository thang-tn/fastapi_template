"""Sentry Configurations."""
from pydantic_settings import BaseSettings


class SentrySettings(BaseSettings):
    """Sentry setting for the application."""

    sentry_dsn: str = ""
    sentry_traces_sample_rate: str = ""
