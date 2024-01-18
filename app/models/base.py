import uuid  # noqa: D100
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql import func


def gen_uuid() -> str:
    """Generate UUID."""
    return uuid.uuid4().hex


@as_declarative()
class BaseModel:
    """Base model."""

    id = Column(String(32), default=gen_uuid, primary_key=True, unique=True)  # noqa: A003, RUF100
    created_utc = Column(DateTime, default=datetime.now, server_default=func.now())
    updated_utc = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),  # type: ignore[arg-type]
    )
    __name__: str  # noqa: A003, RUF100

    def to_dict(self, exclude_attrs=["id", "created_utc", "updated_utc"]):  # noqa: B006
        """Convert model to dict."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude_attrs
        }
