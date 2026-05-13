from src.database.database_config import DatabaseConfig


class DatabaseService:
    def __init__(self, database_config: DatabaseConfig) -> None:
        self.database_config = database_config

    def get_database_url(self) -> str:
        return self.database_config.database_url

    def is_sql_logging_enabled(self) -> bool:
        return self.database_config.echo_sql