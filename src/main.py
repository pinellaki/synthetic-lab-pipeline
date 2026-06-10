"""FastAPI application entry point.

This module creates the FastAPI application for the Synthetic Lab Pipeline.

The application exposes:

- a basic health-check endpoint
- M8 fake-data pipeline documentation endpoints

The M8 endpoints are included so FastAPI can automatically generate API
documentation that shows the available routes, response schemas, and pipeline
summaries.
"""

from fastapi import FastAPI

from src.api.m8_routes import router as m8_router
from src.core.app_config import AppConfig


config = AppConfig()

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description=(
        "Synthetic Lab Pipeline API. "
        "This API exposes health-check information and M8 fake-data pipeline "
        "documentation endpoints."
    ),
)

app.include_router(m8_router)


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