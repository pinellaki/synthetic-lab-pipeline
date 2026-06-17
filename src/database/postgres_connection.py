"""PostgreSQL connection utilities.

This module reads local database configuration from the ignored ``.env`` file
and creates PostgreSQL connections for the one-time data load.

Database credentials are never hardcoded in the Python source code.
"""

from pathlib import Path
import os

import psycopg
from psycopg import Connection
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


def load_database_environment() -> None:
    """Load local PostgreSQL settings from the project .env file."""
    if not ENV_FILE.exists():
        raise RuntimeError(
            f"Database configuration file was not found: {ENV_FILE}"
        )

    load_dotenv(dotenv_path=ENV_FILE)


def create_postgres_connection() -> Connection:
    """Create and return a PostgreSQL database connection.

    Returns:
        An open Psycopg PostgreSQL connection.

    Raises:
        RuntimeError: If one or more required environment variables are
            missing.
    """
    load_database_environment()

    required_variables = [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
    ]

    missing_variables = [
        variable_name
        for variable_name in required_variables
        if not os.getenv(variable_name)
    ]

    if missing_variables:
        missing_names = ", ".join(missing_variables)
        raise RuntimeError(
            f"Missing required database configuration: {missing_names}"
        )

    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        connect_timeout=5,
    )