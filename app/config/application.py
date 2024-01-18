from functools import lru_cache  # noqa: D100

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.celery import CelerySettings
from app.config.database import DatabaseSettings
from app.config.kafka import KafkaSettings

load_dotenv()


class DefaultSettings(BaseSettings):
    """Default settings for the application."""

    model_config = SettingsConfigDict(env_nested_delimiter="__")
    environment: str = "development"
    debug: bool = False


class AppSettings(DefaultSettings):
    """Application settings."""

    database: DatabaseSettings
    sentence_transformer_name: str = ""
    ml_model_path: str = ""
    job_title_abbreviations_file: str = ""
    standard_job_titles_file: str = ""


class ConsumerSettings(DefaultSettings):
    """Consumer settings."""

    kafka: KafkaSettings
    dd_service: str = ""


settings = {
    "app": AppSettings,
    "celery": CelerySettings,
    "consumer": ConsumerSettings,
}


@lru_cache
def get_settings(app_type="app") -> BaseSettings:
    """
    Return configurations based on application type.

    Parameters
    ----------
    app_type : str, optional
        "app" / "consumer"

    Returns
    -------
    BaseSettings
        Settings instance
    """
    return settings.get(app_type, DefaultSettings)()
