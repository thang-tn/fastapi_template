"""Base Model class."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql import func


@as_declarative()
class BaseModel:
    """Base model."""

    __name__: str

    id = Column(Uuid, default=uuid.uuid4, primary_key=True)  # noqa: A003, RUF100
    created_utc = Column(DateTime, default=datetime.now, server_default=func.now())
    updated_utc = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),  # type: ignore[arg-type]
    )
