"""Worker to handle celery tasks."""

from pathlib import Path

import structlog
from celery import Celery, signals
from celery.concurrency import asynpool

from app.core.config import CelerySettings, get_settings
from app.utils.sentry import capture_exception
from app.utils.structlog import configure_logging

settings: CelerySettings = get_settings("celery")
asynpool.PROC_ALIVE_TIMEOUT = settings.celery_proc_alive_timeout  # type: ignore[attr-defined]


def get_modules() -> list[str]:
    """Get lists module of tasks."""
    tasks_module = Path(__file__).parent / "tasks"
    modules = tasks_module.glob("*.py")
    return ["app.tasks." + m.name[:-3] for m in modules if not m.name.endswith("__init__.py")]


celery_app = Celery(
    __name__,
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    include=get_modules(),
    broker_connection_retry_on_startup=True,
)
celery_app.conf.update(
    result_expires=settings.celery_result_expires,
)
celery_app.control.enable_events()


@signals.task_prerun.connect
def on_task_prerun(
    task_id,
    task,
    *_,
    **__,
):
    """Bind task information into logging context."""
    structlog.contextvars.bind_contextvars(task_id=task_id, task_name=task.name)


@signals.setup_logging.connect
def config_logger(*_, **__):
    """Config celery logger on startup."""
    configure_logging(debug=settings.debug, enable_json=settings.json_log_enabled)


@signals.task_retry.connect
@signals.task_failure.connect
@signals.task_revoked.connect
def on_task_failure(**kwargs):
    """Abort transaction on task errors."""
    # Capture the error with Sentry
    traceback = kwargs.get("traceback", "")
    capture_exception(traceback)
