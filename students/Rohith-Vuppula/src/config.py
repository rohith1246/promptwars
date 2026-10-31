"""
FairShift - Application Configuration Module
Implements environment-driven hierarchical settings for development, testing, and production.
"""

import os
from typing import Type


class BaseConfig:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "fairshift-sdg8-decent-work-secret-key-2026")
    JSON_SORT_KEYS = False
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "120 per minute"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fairshift.db")


class ProductionConfig(BaseConfig):
    """Production settings optimized for Render / Cloud Run and Neon PostgreSQL."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(BaseConfig):
    """Local development settings."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True


class TestingConfig(BaseConfig):
    """Automated test suite configuration."""
    DEBUG = False
    TESTING = True
    RATELIMIT_ENABLED = False
    SESSION_COOKIE_SECURE = False


def get_config() -> Type[BaseConfig]:
    """Retrieve active configuration class based on FLASK_ENV or TESTING."""
    env = os.getenv("FLASK_ENV", "production").lower()
    if env == "testing":
        return TestingConfig
    elif env == "development":
        return DevelopmentConfig
    return ProductionConfig
