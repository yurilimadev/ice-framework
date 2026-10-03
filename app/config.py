import os
import secrets
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "app.sqlite3"
DEFAULT_MIGRATIONS_PATH = PROJECT_ROOT / "migrations"
DEFAULT_SECRET_KEY = secrets.token_hex(32)


def load_config():
    return {
        "APP_DATABASE_PATH": os.getenv("APP_DATABASE_PATH", str(DEFAULT_DATABASE_PATH)),
        "APP_TIMEZONE": os.getenv("APP_TIMEZONE", "America/Sao_Paulo"),
        "MIGRATIONS_PATH": os.getenv("MIGRATIONS_PATH", str(DEFAULT_MIGRATIONS_PATH)),
        "SECRET_KEY": os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY),
        "SMTP_HOST": os.getenv("SMTP_HOST"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "SMTP_FROM": os.getenv("SMTP_FROM"),
        "DIGEST_TO": os.getenv("DIGEST_TO"),
    }


def validate_timezone(timezone_name):
    try:
        ZoneInfo(timezone_name)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        raise RuntimeError(f"Fuso horario invalido: {timezone_name}") from None
