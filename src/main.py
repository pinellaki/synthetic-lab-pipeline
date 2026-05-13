from fastapi import FastAPI

from src.core.app_config import AppConfig


config = AppConfig()

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "project": config.app_name,
        "version": config.app_version,
    }