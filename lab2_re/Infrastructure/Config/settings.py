# Infrastructure/config/settings.py

from pydantic_settings import BaseSettings

from functools import lru_cache
import os


class Settings(BaseSettings):
    # =============================
    #   ОБЩИЕ НАСТРОЙКИ
    # =============================
    PROJECT_NAME: str = "Book Warehouse API"
    ENV: str = "dev"  # dev / prod / test

    # =============================
    #   API
    # =============================
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # =============================
    #   БАЗА (если добавишь позже)
    # =============================
    DATABASE_URL: str = "sqlite:///./warehouse.db"

    # =============================
    #   SECURITY
    # =============================
    SECRET_KEY: str = "SUPER_SECRET_KEY"  # вынести в .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =============================
    #   LOGGING
    # =============================
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# singleton для FastAPI (не пересоздаётся каждый раз)
@lru_cache()
def get_settings() -> Settings:
    return Settings()
