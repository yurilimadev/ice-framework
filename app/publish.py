"""Publicação do banco local no servidor Termux (o servidor é um espelho)."""

import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path


def _deploy_config(app) -> dict:
    config = {
        "host": app.config.get("DEPLOY_HOST"),
        "port": str(app.config.get("DEPLOY_PORT", 8022)),
        "key": app.config.get("DEPLOY_KEY_PATH"),
        "target": app.config.get("DEPLOY_TARGET_PATH"),
        "service": app.config.get("DEPLOY_SV_SERVICE", "ice-framework"),
    }
    missing = [
        f"DEPLOY_{name}"
        for name, value in (
            ("HOST", config["host"]),
            ("KEY_PATH", config["key"]),
            ("TARGET_PATH", config["target"]),
        )
        if not value
    ]
    if missing:
        raise RuntimeError("Publicacao incompleta; defina " + ", ".join(missing) + ".")
    return config


def _snapshot(app) -> Path:
    source = Path(app.config["APP_DATABASE_PATH"])
    if not source.exists():
        raise RuntimeError(f"Banco local nao encontrado em {source}.")

    snapshot_dir = Path(tempfile.mkdtemp(prefix="ice-publish-"))
    snapshot = snapshot_dir / source.name
    source_connection = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    snapshot_connection = sqlite3.connect(str(snapshot))
    try:
        source_connection.backup(snapshot_connection)
    except sqlite3.Error:
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        raise
    finally:
        snapshot_connection.close()
        source_connection.close()
    return snapshot


def _run(command, timeout=120) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()[-3:]
        raise RuntimeError("; ".join(detail) or f"comando falhou: rc={result.returncode}")
    return result


def publish_database(app) -> str:
    from flask import current_app

    with app.app_context():
        from .db import get_db
        from .tasks import TaskRepository

        repository = TaskRepository(get_db(), app.config["APP_TIMEZONE"])
        open_tasks = len(repository.list(status="open", order_by="score"))

    snapshot = _snapshot(app)
    try:
        config = _deploy_config(app)
        _run(
            [
                "scp",
                "-i",
                config["key"],
                "-P",
                config["port"],
                str(snapshot),
                f"{config['host']}:{config['target']}",
            ]
        )
        _run(
            [
                "ssh",
                "-i",
                config["key"],
                "-p",
                config["port"],
                config["host"],
                # O sv precisa do SVDIR; em SSH nao-interativo ele nao vem do profile.
                f'export SVDIR="$PREFIX/var/service"; sv down {config["service"]}; sv up {config["service"]}',
            ]
        )
    finally:
        shutil.rmtree(snapshot.parent, ignore_errors=True)
    return f"Publicado no servidor: {open_tasks} tarefa(s) aberta(s) publicada(s)."
