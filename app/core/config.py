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

    # 项目配置
    PROJECT_NAME: str = "School Athletics Management"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: str | None = None
    DB_ENGINE: str = "postgresql+psycopg2"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "admin"
    DB_PASSWORD: str = "your-password-here"
    DB_NAME: str = "athletics"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # 前端配置
    FRONTEND_BASE_URL: str = "http://127.0.0.1:3000"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str | None = None

    # 安全配置
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Redis配置（可选）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # 监控配置
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 8000

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
