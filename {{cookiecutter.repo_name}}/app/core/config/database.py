"""Database Configurations."""
from pydantic import ValidationError
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database settings for the application."""

    database_url: str = ""
    # for debugging purposes
    echo_sql: bool = False
    # for testing
    testing: bool = False
    test_database_url: str = ""
    # lock timeout settings, default to 10s
    lock_timeout: int = 10000
    # statement timeout settings, default to 10s
    statement_timeout: int = 10000

    @property
    def db_uri(self) -> str:
        """Return database uri."""
        if self.testing:
            if not self.test_database_url:
                raise ValidationError("TEST_DATABASE_URL is required.")
            return self.test_database_url

        if not self.database_url:
            raise ValidationError("DATABASE_URL is required.")

        return self.database_url
