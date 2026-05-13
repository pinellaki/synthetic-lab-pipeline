from pydantic import BaseModel


class AppConfig(BaseModel):
    app_name: str = "Synthetic Lab Pipeline"
    app_version: str = "0.1.0"
    environment: str = "development"

    raw_data_path: str = "data/raw"
    staging_data_path: str = "data/staging"
    trusted_data_path: str = "data/trusted"
    rejected_data_path: str = "data/rejected"
    reports_data_path: str = "data/reports"

    logging_level: str = "INFO"