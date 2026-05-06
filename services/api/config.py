# FastAPI application settings — loaded from environment variables.

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/seo_agent_os"
    sync_database_url: str = "postgresql://postgres:postgres@localhost:5432/seo_agent_os"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI / Hermes
    hermes_api_key: str = ""
    hermes_endpoint: str = "http://localhost:8080"
    hermes_timeout: int = 120

    # External APIs
    google_api_key: str = ""
    google_search_console_client_id: str = ""
    google_search_console_client_secret: str = ""

    # Storage
    storage_backend: str = "local"
    storage_path: str = "./storage"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # API
    api_v1_prefix: str = "/api/v1"
    api_title: str = "SEO Agent OS API"
    api_version: str = "1.0.0"
    api_description: str = "Autonomous SEO and GEO agent system API"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()


settings = get_settings()
