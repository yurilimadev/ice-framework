import re
import sqlite3
from pathlib import Path

from flask import current_app, g


MIGRATION_PATTERN = re.compile(r"^(\d+)_.*\.sql$")


def _connect(database_path):
    path = Path(database_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def get_db():
    if "db" not in g:
        g.db = _connect(current_app.config["APP_DATABASE_PATH"])
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def get_schema_version(connection=None):
    if connection is None:
        connection = get_db()
    return connection.execute("PRAGMA user_version").fetchone()[0]


def init_db(app):
    connection = _connect(app.config["APP_DATABASE_PATH"])
    try:
        current_version = get_schema_version(connection)
        for version, path in _migration_files_for_app(app):
            if version <= current_version:
                continue
            if version != current_version + 1:
                raise RuntimeError(
                    f"Migracao ausente entre as versoes {current_version} e {version}"
                )

            connection.executescript(path.read_text(encoding="utf-8"))
            connection.execute(f"PRAGMA user_version = {version}")
            connection.commit()
            current_version = version
    finally:
        connection.close()


def _migration_files_for_app(app):
    migrations_path = Path(app.config["MIGRATIONS_PATH"])
    migrations = []
    for path in migrations_path.glob("*.sql"):
        match = MIGRATION_PATTERN.match(path.name)
        if match is None:
            raise RuntimeError(f"Nome de migracao invalido: {path.name}")
        migrations.append((int(match.group(1)), path))

    migrations.sort(key=lambda item: item[0])
    versions = [version for version, _path in migrations]
    if len(versions) != len(set(versions)):
        raise RuntimeError("Versoes de migracao duplicadas")
    return migrations
