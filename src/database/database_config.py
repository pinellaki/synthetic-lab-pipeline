"""Database configuration schema.

This module defines the DatabaseConfig model.

The model stores database connection settings used by database-related
services. It keeps database settings centralized instead of hardcoding them
inside service classes.
"""

from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    """Store database connection configuration.

    The configuration contains the database URL and a flag that controls
    whether SQL statements should be printed/logged during execution.

    The default database URL is a local SQLite-style placeholder. It can be
    replaced later with a PostgreSQL connection URL when the database loading
    pipeline is implemented.

    Fields:
        database_url: Database connection string.
        echo_sql: Whether SQL statements should be echoed for debugging.
    """

    database_url: str = "sqlite:///synthetic_lab_pipeline.db"
    echo_sql: bool = False