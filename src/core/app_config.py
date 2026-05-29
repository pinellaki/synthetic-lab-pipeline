"""Application configuration schema.

This module defines the AppConfig model.

The model stores basic application settings, data folder paths, and logging
configuration for the Synthetic Lab Pipeline project.
"""

from pydantic import BaseModel


class AppConfig(BaseModel):
    """Store application-level configuration values.

    This configuration object centralizes default project settings so they can
    be reused by ingestion, validation, database, and reporting components.

    Fields:
        app_name: Human-readable application name.
        app_version: Current application version.
        environment: Runtime environment, such as development, test, or
            production.
        raw_data_path: Folder path for raw source data.
        staging_data_path: Folder path for intermediate staged data.
        trusted_data_path: Folder path for cleaned and trusted data.
        rejected_data_path: Folder path for rejected records.
        reports_data_path: Folder path for generated reports.
        logging_level: Default logging level used by the application.
    """

    app_name: str = "Synthetic Lab Pipeline"
    app_version: str = "0.1.0"
    environment: str = "development"

    raw_data_path: str = "data/raw"
    staging_data_path: str = "data/staging"
    trusted_data_path: str = "data/trusted"
    rejected_data_path: str = "data/rejected"
    reports_data_path: str = "data/reports"

    logging_level: str = "INFO"