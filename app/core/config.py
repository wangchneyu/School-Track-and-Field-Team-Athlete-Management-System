"""Application configuration powered by environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "School Athletics Management"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    SQLALCHEMY_DATABASE_URI: str | None = None
    DB_ENGINE: str = "postgresql+psycopg2"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "admin"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "athletics"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 30 * 60
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]
    FRONTEND_BASE_URL: str = "http://127.0.0.1:3000"

    def assemble_db_connection(self) -> str:
        """Return the SQLAlchemy database URL."""

        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        host = self.DB_HOST
        port = self.DB_PORT
        database = self.DB_NAME
        return f"{self.DB_ENGINE}://{user}:{password}@{host}:{port}/{database}"

    @property
    def database_uri(self) -> str:
        return self.assemble_db_connection()


@lru_cache
def get_settings() -> Settings:
    return Settings()
