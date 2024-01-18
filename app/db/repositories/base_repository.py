"""Generic Repository for accessing database."""
from typing import Generic, TypeVar, Union

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BaseModel

Model = TypeVar("Model", bound=BaseModel)


class SqlRepository(Generic[Model]):
    """Generic SQL Repository."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, id: Union[int, str]) -> Model | None:  # noqa: UP007, A002
        """Get model by id."""
        return await self.session.get(self.model, id)

    async def filter(self, *expressions: BinaryExpression) -> list[Model]:  # noqa: RUF100, A003
        """Filter model by expressions."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)

        return list(await self.session.scalars(query))

    async def create(self, data: dict) -> Model:
        """Create model."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
