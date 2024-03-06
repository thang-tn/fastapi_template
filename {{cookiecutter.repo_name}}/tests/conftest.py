"""Test Setups."""
import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as main_app
from tests.utils import init_test_db, tear_down_test_db, test_session_manager

logger = logging.getLogger(__name__)


##################
# SESSION FIXTURES
##################
@pytest.fixture(scope="session", autouse=True)
async def _setup_test_db():
    """Set up test database."""
    await init_test_db()
    yield
    await tear_down_test_db()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Async Test client."""
    async with AsyncClient(app=main_app, base_url="http://test") as client:
        yield client


##################
# CLASS FIXTURES
##################
@pytest.fixture(scope="class")
def event_loop() -> Any:
    """Get event loop context."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


##################
# FUNCTION FIXTURES
##################
@pytest.fixture()
async def async_session() -> AsyncGenerator[AsyncSession]:
    """Get async database session."""
    async with test_session_manager.session(scoped=True) as session:
        yield session
        # rolling back after finish a test case
        await session.rollback()
