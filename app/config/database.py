"""Database Configurations."""
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database settings for the application."""

    host: str = "localhost"
    port: int = 5432
    name: str = ""
    user: str = ""
    password: str = ""
    url: str = Field(alias="database_url", default="")
    echo_sql: bool = False

    @property
    def db_uri(self) -> str:
        """Return database uri."""
        if self.url:
            return self.url
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
