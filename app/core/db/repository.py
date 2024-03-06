"""Base Repository class."""

import abc
from typing import Any

from sqlalchemy import BinaryExpression, ColumnExpressionArgument, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import BaseModel


class AbstractRepository(abc.ABC):
    """Abstract Repository class."""

    @abc.abstractmethod
    def get(self, id: int | str) -> Any:
        """Get record by id.

        Parameters
        ----------
        id : int | str
            record id

        Returns
        -------
        Any
            found record

        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, data: dict) -> Any:
        """Get record by id.

        Parameters
        ----------
        data: dict
            object data

        Returns
        -------
        Any
            newly created record

        """
        raise NotImplementedError


class AbstractSqlRepository(AbstractRepository):
    """Abstract Sql Repository."""

    model: type[BaseModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int | str) -> Any:
        """
        Get record by id.

        Parameters
        ----------
        id : Union[int, str]
            object id, could be integer or string

        Returns
        -------
        Any
            found record, None if not found
        """
        return await self.session.get(self.model, id)

    async def create(self, data: dict) -> Any:
        """
        Create new record from provided data.

        Parameters
        ----------
        data : dict
            dictionary containing object data

        Returns
        -------
        Any
            new model instance
        """
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def filter_by(
        self,
        *expressions: BinaryExpression | ColumnExpressionArgument,
        limit: int = 100,
        skip: int = 0,
    ) -> list[Any]:
        """
        Filter records by conditions.

        Returns
        -------
        list
            list of records retrieved
        """
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)

        if skip:
            query = query.offset(skip)

        return list(await self.session.execute(query.limit(limit)))
