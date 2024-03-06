from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

from app.core.config.application import AppSettings
from app.core.config.celery import CelerySettings
from app.core.config.database import DatabaseSettings
from app.core.config.kafka import KafkaSettings
from app.core.config.sentry import SentrySettings

load_dotenv()


@lru_cache
def get_settings(app_type="app") -> Any:
    """
    Return configurations based on application type.

    Parameters
    ----------
    app_type : str, default "app"
        "app" | "celery" | "database" | "kafka" | "sentry"

    Returns
    -------
    Any
        Settings instance
    """
    settings = {
        "app": AppSettings,
        "celery": CelerySettings,
        "database": DatabaseSettings,
        "kafka": KafkaSettings,
        "sentry": SentrySettings,
    }

    if app_type not in settings:
        raise TypeError(f"Configuration not found for: {app_type}")

    return settings[app_type]()
