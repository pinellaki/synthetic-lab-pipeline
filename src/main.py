"""FastAPI application entry point.

This module creates the FastAPI application for the Synthetic Lab Pipeline.

The application exposes:

- a basic health-check endpoint
- M8 fake-data pipeline documentation endpoints
- read-only PostgreSQL endpoints for the governance dashboard

FastAPI automatically generates interactive API documentation at ``/docs``.
"""

from fastapi import FastAPI

from src.api.dashboard_routes import router as dashboard_router
from src.api.m8_routes import router as m8_router
from src.core.app_config import AppConfig


config = AppConfig()

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description=(
        "Synthetic Lab Pipeline API. "
        "The API exposes M8 fake-data pipeline documentation and read-only "
        "PostgreSQL endpoints for the governance dashboard."
    ),
)

app.include_router(m8_router)
app.include_router(dashboard_router)


@app.get(
    "/",
    summary="Health check",
)
def health_check() -> dict[str, str]:
    """Return basic application health information.

    Returns:
        A dictionary containing the service status, project name, and project
        version.
    """
    return {
        "status": "ok",
        "project": config.app_name,
        "version": config.app_version,
    }