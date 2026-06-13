import os
from functools import lru_cache


class Settings:
    app_name: str = "ForgePulse Platform API"
    app_version: str = "0.1.0"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @property
    def database_url(self) -> str:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "forgepulse")
        user = os.getenv("POSTGRES_USER", "forgepulse")
        password = os.getenv("POSTGRES_PASSWORD", "forgepulse")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
