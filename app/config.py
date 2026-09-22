import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "app.sqlite3"
DEFAULT_MIGRATIONS_PATH = PROJECT_ROOT / "migrations"


def load_config():
    return {
        "APP_DATABASE_PATH": os.getenv("APP_DATABASE_PATH", str(DEFAULT_DATABASE_PATH)),
        "APP_TIMEZONE": os.getenv("APP_TIMEZONE", "America/Sao_Paulo"),
        "MIGRATIONS_PATH": os.getenv("MIGRATIONS_PATH", str(DEFAULT_MIGRATIONS_PATH)),
    }


def validate_timezone(timezone_name):
    try:
        ZoneInfo(timezone_name)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        raise RuntimeError(f"Fuso horario invalido: {timezone_name}") from None
