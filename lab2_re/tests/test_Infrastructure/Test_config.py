# lab2re/Unit_tests/test_Infrastructure/Test_config.py

import os
import logging
import pytest

from Infrastructure.Config.settings import Settings, get_settings
from Infrastructure.Config.logging_config import setup_logging


# ============================================================
#               TEST: Settings default values
# ============================================================

def test_settings_default_values():
    """
    Проверяем, что дефолтные значения настроек из Settings загружаются корректно.
    """
    settings = Settings()

    assert settings.PROJECT_NAME == "Book Warehouse API"
    assert settings.ENV == "dev"
    assert settings.API_HOST == "127.0.0.1"
    assert settings.API_PORT == 8000
    assert settings.API_RELOAD is True
    assert settings.DATABASE_URL == "sqlite:///./warehouse.db"
    assert settings.SECRET_KEY == "SUPER_SECRET_KEY"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert settings.LOG_LEVEL == "INFO"


# ============================================================
#               TEST: Environment variable override
# ============================================================

def test_settings_env_override(monkeypatch):
    """
    Проверяем, что переменные окружения перекрывают дефолтные значения.
    """

    monkeypatch.setenv("API_PORT", "9999")
    monkeypatch.setenv("PROJECT_NAME", "TEST PROJECT")

    settings = Settings()

    assert settings.API_PORT == 9999
    assert settings.PROJECT_NAME == "TEST PROJECT"


# ============================================================
#               TEST: get_settings() is singleton
# ============================================================

def test_get_settings_singleton():
    """
    get_settings() использует @lru_cache(),
    значит должен возвращать один и тот же объект.
    """
    s1 = get_settings()
    s2 = get_settings()

    assert s1 is s2  # singleton
    assert id(s1) == id(s2)




# ============================================================
#               TEST: env_file loading (optional)
# ============================================================

def test_settings_env_file(tmp_path, monkeypatch):
    """
    Проверяем, что Settings читает .env файл (если он есть).
    """

    # создаём временный .env
    env_path = tmp_path / ".env"
    env_path.write_text("SECRET_KEY=FROM_ENV_FILE\n")

    monkeypatch.setenv("ENV", "test")  # чтобы явно пересоздать Settings
    monkeypatch.setenv("ENV_FILE", str(env_path))

    # подменяем текущую директорию на tmp_path
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.SECRET_KEY == "FROM_ENV_FILE"
