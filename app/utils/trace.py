"""Helper for ddtrace."""
import structlog
from ddtrace import patch
from ddtrace.contrib.asgi.middleware import TraceMiddleware
from ddtrace.profiling import Profiler
from fastapi import FastAPI


def start_profiler():
    """Start ddtrace profiler."""
    prof = Profiler()
    prof.start()


def enable_trace(environment: str) -> bool:
    """Enable trace when environment is not development."""
    return environment.lower() in ("staging", "production")


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


def patch_tracing_middleware(app: FastAPI):
    """Patch Datadog middleware."""
    tracing_middleware = next((m for m in app.user_middleware if m.cls == TraceMiddleware), None)
    if tracing_middleware is not None:
        app.user_middleware = [m for m in app.user_middleware if m.cls != TraceMiddleware]
        structlog.stdlib.get_logger("api.datadog_patch").info(
            "Patching Datadog tracing middleware to be the outermost middleware...",
        )
        app.user_middleware.insert(0, tracing_middleware)
        app.middleware_stack = app.build_middleware_stack()
