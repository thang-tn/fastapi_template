"""Database Session Manager."""

import contextlib
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import DatabaseSettings, get_settings


class DatabaseSessionManager:
    """Database Session Manager class."""

    def __init__(self, db_host: str, kwargs: dict[str, Any]) -> None:
        extra_kwargs = kwargs if kwargs else {}
        self._engine = create_async_engine(
            db_host,
            **extra_kwargs,
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
        )

    def _validate_engine(self):
        """Ensuse `self._engine` is not None."""
        if self._engine is None:
            raise RuntimeError(
                "DatabaseSessionManager is not initialized.",
            )

    async def close(self):
        """Close database connection."""
        if self._engine is None:
            return

        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Get async database connection."""
        self._validate_engine()

        async with self._engine.begin() as conn:
            try:
                yield conn
            except Exception:
                await conn.rollback()
                raise

    @contextlib.asynccontextmanager  # type: ignore[arg-type]
    async def session(self, *, scoped: bool = False) -> AsyncIterator[AsyncSession]:
        """Get async database session."""
        self._validate_engine()

        session = self._sessionmaker()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            if scoped:
                await self._engine.dispose()


# initialize session manager from app settings
db_settings: DatabaseSettings = get_settings("database")
session_manager = DatabaseSessionManager(
    db_settings.db_uri,  # type: ignore[attr-defined]
    {
        "echo": db_settings.echo_sql,  # type: ignore[attr-defined]
        "connect_args": {
            "server_settings": {
                "lock_timeout": str(db_settings.lock_timeout),
                "statement_timeout": str(db_settings.statement_timeout),
            },
        },
    },
)
