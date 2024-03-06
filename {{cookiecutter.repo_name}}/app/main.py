"""Main file for starting the web app."""
from contextlib import asynccontextmanager

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.api import app_router
from app.core.config import AppSettings, get_settings
from app.core.db import session_manager
from app.utils.middlewares.http_middleware import LoggingMiddleware
from app.utils.structlog import configure_logging
from app.utils.trace import patch_tracing_middleware

# logger = logging.getLogger(__name__)
logger = structlog.stdlib.get_logger(__name__)

settings: AppSettings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Return session manager to handle startup and shutdown event.

    Parameters
    ----------
    app : FastAPI
        App instance
    """
    # configure logging for web app
    configure_logging(debug=settings.debug, enable_json=settings.json_log_enabled)

    yield
    # close the db connection at startup and shutdown
    await session_manager.close()


app = FastAPI(
    title="FastAPI Project",
    lifespan=lifespan,
    docs_url="/api/docs",
)
# register middlewares
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(CorrelationIdMiddleware)
patch_tracing_middleware(app)
# register routers
app.include_router(app_router)


# adding logging for exception handler
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    """Handle web app exceptions."""
    logger.error("HTTPException: %s %s", exc.status_code, exc.detail)
    return await http_exception_handler(request, exc)
