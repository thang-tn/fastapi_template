"""Test healthz api."""
from fastapi import status
from httpx import AsyncClient


async def test_healthz(async_client: AsyncClient):
    """Test healthz api."""
    resp = await async_client.get("/healthz")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status": "ok"}
