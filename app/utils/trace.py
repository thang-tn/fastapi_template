"""Helper for ddtrace."""
from ddtrace import patch
from ddtrace.profiling import Profiler

from app.config import get_settings


def start_profiler():
    """Start ddtrace profiler."""
    prof = Profiler()
    prof.start()


def enable_trace() -> bool:
    """Enable trace when environment is not development."""
    settings = get_settings("consumer")
    return settings.environment.lower() in ("stg", "prd")  # type: ignore[attr-defined]


def path_trace():
    """Patch trace extensions."""
    if enable_trace() is False:
        return

    patch(
        fastapi=True,
        sqlalchemy=True,
        openai=True,
        langchain=True,
        redis=True,
        kafka=True,
        starlette=True,
        asgi=True,
        psycopg=True,
        requests=True,
        asyncio=True,
        aiohttp=True,
        httplib=True,
        urllib3=True,
    )

    start_profiler()


def path_kafka_trace():
    """Patch trace extensions."""
    if enable_trace() is False:
        return

    patch(
        redis=True,
        kafka=True,
        psycopg=True,
        requests=True,
        celery=True,
        aioredis=True,
        asyncio=True,
        aiohttp=True,
        httplib=True,
        urllib3=True,
        kombu=True,
    )
