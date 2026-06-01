"""FastAPI application entry point.

This module creates the FastAPI application for the Synthetic Lab Pipeline.

The application currently exposes a simple health-check endpoint that confirms
the service is running and returns basic project metadata.
"""

from fastapi import FastAPI

from src.core.app_config import AppConfig


config = AppConfig()

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
)


@app.get("/")
def health_check() -> dict[str, str]:
    """Return basic application health information.

    Returns:
        A dictionary containing the service status, project name, and project
        version.

    Example:
        A successful response looks like::

            {
                "status": "ok",
                "project": "Synthetic Lab Pipeline",
                "version": "0.1.0"
            }
    """
    return {
        "status": "ok",
        "project": config.app_name,
        "version": config.app_version,
    }