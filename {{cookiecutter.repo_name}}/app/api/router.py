"""API router."""
from fastapi import APIRouter

from app.api.v1 import api_v1_router

router = APIRouter()
# register routers below
router.include_router(api_v1_router)


# Health check
@router.get("/healthz", tags=["healthz"])
def healthz():
    """Health check."""
    return {"status": "ok"}
