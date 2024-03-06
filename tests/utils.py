"""Utility functions for testing."""
import logging

from sqlalchemy.pool import NullPool

from app.core.config import DatabaseSettings, get_settings
from app.core.db.session import DatabaseSessionManager
from app.core.models import BaseModel

logger = logging.getLogger(__name__)
db_settings: DatabaseSettings = get_settings("database")
test_session_manager = DatabaseSessionManager(
    db_settings.db_uri,  # type: ignore[attr-defined]
    {
        "echo": db_settings.echo_sql,  # type: ignore[attr-defined]
        "poolclass": NullPool,
        "connect_args": {"server_settings": {"lock_timeout": "2000"}},  # set lock_timeout to 2s for quick test
    },
)


async def init_test_db():
    """Initialize test database."""
    logger.info("Setting up database: %s", test_session_manager._engine.url)
    async with test_session_manager.connect() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    await test_session_manager._engine.dispose()


async def tear_down_test_db():
    """Tear down test database."""
    logger.info("Cleaning up database.")
    async with test_session_manager.connect() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await test_session_manager._engine.dispose()
