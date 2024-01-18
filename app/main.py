import logging  # noqa: D100
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import app_router
from app.config import get_settings
from app.db import session_manager

settings = get_settings()
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if settings.debug else logging.INFO,  # type: ignore[attr-defined]
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Return session manager to handle startup and shutdown event.

    Parameters
    ----------
    app : FastAPI
        App instance
    """
    yield
    if session_manager._engine is not None:  # noqa: SLF001
        # close the db connection at startup and shutdown
        await session_manager.close()


app = FastAPI(
    title="SmartMatch",
    lifespan=lifespan,
    docs_url="/api/docs",
)
app.include_router(app_router)
