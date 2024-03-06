"""Unit of work is used for accessing to multiple repositories in a single database transaction."""
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository import AbstractSqlRepository


class UnitOfWork:
    """Unit of work."""

    repository_classes: Mapping[str, type[AbstractSqlRepository]] = MappingProxyType({})

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repositories: dict[str, AbstractSqlRepository] = {}

    async def __aenter__(self) -> "UnitOfWork":
        """Prepare repositories before entering the context."""
        for model_name, klass in self.repository_classes.items():
            self.repositories[model_name] = klass(self.session)
        return self

    async def __aexit__(self, *args):
        """Clean up before exiting the context."""
        await self.session.close()

    def get_repository(self, name: str) -> Any:
        """
        Get reporitoy for a given model.

        Parameters
        ----------
        model : BaseModel
            model class

        Returns
        -------
        SqlRepository
            repository instance
        """
        repo = self.repositories.get(name)
        if repo is None:
            raise ValueError(f"Repository <{name}> does not exists.")
        return repo
