"""API router."""
from fastapi import APIRouter, Depends

from app.api.v1 import api_v1_router
from app.config import AppSettings, get_settings

router = APIRouter()
# register routers below
router.include_router(api_v1_router)


# Health check
@router.get("/ping", tags=["healthz"])
def ping(settings: AppSettings = Depends(get_settings)):  # noqa: B008
    """Health check."""
    return {
        "status": "ok",
        "env": settings.environment,
    }
