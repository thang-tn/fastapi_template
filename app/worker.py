"""Worker to handle celery tasks."""
from pathlib import Path

from celery import Celery, signals
from celery.concurrency import asynpool

from app.config import get_settings
from app.utils.sentry import capture_exception

settings = get_settings("celery")
asynpool.PROC_ALIVE_TIMEOUT = settings.celery_proc_alive_timeout  # type: ignore[attr-defined]


def get_modules() -> list[str]:
    """Get lists module of tasks."""
    tasks_module = Path(__file__).parent / "tasks"
    modules = tasks_module.glob("*.py")
    return ["app.tasks." + m.name[:-3] for m in modules if not m.name.endswith("__init__.py")]


celery_app = Celery(
    __name__,
    broker_url=settings.celery_broker_url,  # type: ignore[attr-defined]
    result_backend=settings.celery_result_backend,  # type: ignore[attr-defined]
    include=get_modules(),
)
celery_app.control.enable_events()


@signals.task_retry.connect
@signals.task_failure.connect
@signals.task_revoked.connect
def on_task_failure(**kwargs):
    """Abort transaction on task errors."""
    # Capture the error with Sentry
    traceback = kwargs.get("traceback", "")
    capture_exception(traceback)
