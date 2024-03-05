from pydantic_settings import BaseSettings  # noqa: D100


class CelerySettings(BaseSettings):
    """Celery setting for the application."""

    environment: str = "development"
    debug: bool = False
    json_log_enabled: bool = True
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str | None = None
    celery_result_expires: int = 3600
    celery_proc_alive_timeout: str = "600"
