from collections.abc import Callable  # noqa: D100

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SqlRepository, get_db_session  # type: ignore[attr-defined]
from app.models import BaseModel


def get_repository(model: type[BaseModel]) -> Callable[[AsyncSession], SqlRepository]:
    """Get repository for model."""
    def func(session: AsyncSession = Depends(get_db_session)):  # noqa: B008
        return SqlRepository(model, session)

    return func
