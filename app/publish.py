"""Sincronizacao do banco com o servidor Termux (fonte de verdade)."""

import os
import shlex
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path


REMOTE_SNAPSHOT_SCRIPT = """
import os, sqlite3, sys, tempfile
source = os.path.expanduser(sys.argv[1])
fd, target = tempfile.mkstemp(prefix="ice-pull-", suffix=".sqlite3")
os.close(fd)
src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
dst = sqlite3.connect(target)
src.backup(dst)
dst.close()
src.close()
print(target)
"""


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


def _validate_snapshot(path: Path) -> None:
    connection = sqlite3.connect(str(path))
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"Snapshot invalido: {integrity}")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Snapshot com referencias quebradas.")
    finally:
        connection.close()


def _backup_database(app, database_path: Path) -> Path | None:
    if not database_path.exists():
        return None
    backup_dir = Path(
        app.config.get("APP_BACKUP_DIR") or database_path.parent / "backups"
    ).expanduser()
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"backup-{time.strftime('%Y%m%d-%H%M%S')}.sqlite3"

    source_connection = sqlite3.connect(
        f"file:{database_path}?mode=ro", uri=True
    )
    target_connection = sqlite3.connect(str(target))
    try:
        source_connection.backup(target_connection)
    finally:
        target_connection.close()
        source_connection.close()
    return target


def _counts(database_path: Path) -> tuple[int, int]:
    connection = sqlite3.connect(str(database_path))
    try:
        tasks = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'open'"
        ).fetchone()[0]
        leads = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    finally:
        connection.close()
    return tasks, leads


def pull_database(app) -> str:
    """Baixa um snapshot consistente do servidor e substitui o banco local."""
    config = _deploy_config(app)
    database_path = Path(app.config["APP_DATABASE_PATH"]).expanduser()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=".ice-pull-", suffix=".sqlite3", dir=database_path.parent
    )
    os.close(descriptor)
    local_snapshot = Path(name)
    remote_snapshot = None
    try:
        result = _run(
            [
                "ssh",
                "-i",
                config["key"],
                "-p",
                config["port"],
                config["host"],
                f"python3 -c {shlex.quote(REMOTE_SNAPSHOT_SCRIPT)} "
                f"{shlex.quote(config['target'])}",
            ]
        )
        remote_snapshot = result.stdout.strip().splitlines()[-1]
        if not remote_snapshot:
            raise RuntimeError("O servidor nao informou o snapshot.")

        _run(
            [
                "scp",
                "-i",
                config["key"],
                "-P",
                config["port"],
                f"{config['host']}:{remote_snapshot}",
                str(local_snapshot),
            ]
        )
        _validate_snapshot(local_snapshot)
        backup = _backup_database(app, database_path)
        os.replace(local_snapshot, database_path)
        local_snapshot = None
    finally:
        if local_snapshot is not None:
            local_snapshot.unlink(missing_ok=True)
        if remote_snapshot:
            try:
                _run(
                    [
                        "ssh",
                        "-i",
                        config["key"],
                        "-p",
                        config["port"],
                        config["host"],
                        f"rm -f {shlex.quote(remote_snapshot)}",
                    ]
                )
            except RuntimeError:
                pass

    tasks, leads = _counts(database_path)
    backup_note = f" Backup local: {backup.name}." if backup is not None else ""
    return (
        "Banco atualizado a partir do servidor: "
        f"{tasks} tarefa(s) aberta(s), {leads} lead(s).{backup_note}"
    )


def publish_database(app, force: bool = False) -> str:
    """Excecao: sobrescreve o banco do servidor com o local.

    O fluxo normal e o oposto (`pull`): o servidor e a fonte de verdade.
    """
    if not force:
        raise RuntimeError(
            "O servidor e a fonte de verdade; use "
            "`python3 -m flask --app wsgi pull` para trazer os dados. "
            "Para sobrescrever o servidor mesmo assim, rode "
            "`python3 -m flask --app wsgi publish --force`."
        )

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
