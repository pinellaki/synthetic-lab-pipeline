from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    database_url: str = "sqlite:///synthetic_lab_pipeline.db"
    echo_sql: bool = False