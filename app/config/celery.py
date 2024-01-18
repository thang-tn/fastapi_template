from pydantic_settings import BaseSettings  # noqa: D100


class CelerySettings(BaseSettings):
    """Celery setting for the application."""

    celery_broker_url: str = ""
    celery_result_backend: str = ""
    celery_proc_alive_timeout: str = "600"
