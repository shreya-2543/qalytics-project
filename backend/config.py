"""
config.py - Centralized environment-backed application settings.
"""
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./qalytics.db")
SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-secret-change-me")
QA_ENV = os.getenv("QA_ENV", "staging")
ALLURE_BIN = os.getenv("ALLURE_BIN")

CORS_ALLOWED_ORIGINS = _parse_csv(
    os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://127.0.0.1:3000,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000",
    )
)

BOOTSTRAP_ADMIN_ENABLED = _parse_bool(os.getenv("BOOTSTRAP_ADMIN_ENABLED"), True)
BOOTSTRAP_ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@qalytics.dev")
BOOTSTRAP_ADMIN_ROLE = os.getenv("BOOTSTRAP_ADMIN_ROLE", "admin")
