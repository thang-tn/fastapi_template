import contextlib  # noqa: D100
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


class DatabaseSessionManager:
    """Database Session Manager class."""

    def __init__(self, db_host: str, kwargs: dict[str, Any]) -> None:  # noqa: RUF100
        extra_kwargs = kwargs if kwargs else {}
        self._engine = create_async_engine(db_host, **extra_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
        )

    def _validate_engine(self):
        """Ensuse `self._engine` is not None."""
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized.")  # noqa: TRY002

    async def close(self):
        """Close database connection."""
        self._validate_engine()
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
    async def session(self) -> AsyncIterator[AsyncSession]:
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


# initialize session manager from app settings
settings = get_settings()
session_manager = DatabaseSessionManager(
    settings.database.db_uri,  # type: ignore[attr-defined]
    {
        "echo": settings.database.echo_sql,  # type: ignore[attr-defined]
    },
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Return current database session.

    Yields
    ------
    AsyncIterator[AsyncSession]
        Async database connection
    """
    async with session_manager.session() as session:
        yield session
