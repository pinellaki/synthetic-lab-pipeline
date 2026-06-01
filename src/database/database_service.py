"""Database service utilities.

This module defines the DatabaseService class.

The service provides simple access to database configuration values. It keeps
database-related configuration access separate from other pipeline components.
"""

from src.database.database_config import DatabaseConfig


class DatabaseService:
    """Expose database configuration values to the pipeline.

    The service receives a DatabaseConfig object and provides small helper
    methods for reading database settings.

    At this stage, the service does not open database connections or execute
    SQL. It only exposes configuration values that can be used later by the
    database loading pipeline.
    """

    def __init__(self, database_config: DatabaseConfig) -> None:
        """Initialize the database service.

        Args:
            database_config: Database configuration object containing the
                database URL and SQL logging flag.
        """
        self.database_config = database_config

    def get_database_url(self) -> str:
        """Return the configured database URL.

        Returns:
            Database connection string from the DatabaseConfig object.
        """
        return self.database_config.database_url

    def is_sql_logging_enabled(self) -> bool:
        """Return whether SQL logging is enabled.

        Returns:
            True if SQL logging is enabled, otherwise False.
        """
        return self.database_config.echo_sql