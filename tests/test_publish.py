"""Testes da publicação do banco local para o servidor Termux."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app.db import get_db
from app.publish import publish_database
from app.tasks import TaskRepository

DEPLOY_OVERRIDES = {
    "DEPLOY_HOST": "usuario@servidor",
    "DEPLOY_PORT": "8022",
    "DEPLOY_KEY_PATH": "/tmp/chave-teste",
    "DEPLOY_TARGET_PATH": "~/ice-framework/data/app.sqlite3",
    "DEPLOY_SV_SERVICE": "ice-framework",
}


class PublishDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
                **DEPLOY_OVERRIDES,
            }
        )
        for title in ("Publicada 1", "Publicada 2"):
            with self.app.app_context():
                TaskRepository(get_db()).create(title, 5, 6, 7)

    def tearDown(self):
        self.directory.cleanup()

    def test_configuracao_incompleta_mostra_variaveis_que_faltam(self):
        self.app.config.update(
            {"DEPLOY_HOST": None, "DEPLOY_KEY_PATH": None, "DEPLOY_TARGET_PATH": None}
        )

        with self.assertRaises(RuntimeError) as context:
            publish_database(self.app)

        self.assertIn("Publicacao incompleta", str(context.exception))
        for name in ("DEPLOY_HOST", "DEPLOY_KEY_PATH", "DEPLOY_TARGET_PATH"):
            self.assertIn(name, str(context.exception))

    def test_publicacao_gera_snapshot_consistente_e_publica(self):
        runs = []
        published = Path(self.directory.name) / "snapshot-capturado.sqlite3"

        def fake_run(command, capture_output, text, timeout):
            runs.append(list(command))
            if command[0] == "scp":
                # Captura o snapshot no momento do envio (antes da limpeza do finally).
                shutil.copy(command[-2], published)
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        with patch("app.publish.subprocess.run", side_effect=fake_run):
            message = publish_database(self.app)

        self.assertIn("Publicado no servidor: 2 tarefa(s) aberta(s)", message)
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0][0], "scp")
        self.assertEqual(runs[0][-1], "usuario@servidor:~/ice-framework/data/app.sqlite3")

        import sqlite3

        connection = sqlite3.connect(published)
        titles = [
            row[0] for row in connection.execute("SELECT title FROM tasks ORDER BY title")
        ]
        connection.close()
        self.assertEqual(titles, ["Publicada 1", "Publicada 2"])

        self.assertEqual(runs[1][0], "ssh")
        remote_command = runs[1][-1]
        self.assertIn("sv down ice-framework", remote_command)
        self.assertIn("sv up ice-framework", remote_command)

    def test_falha_no_scp_vira_runtime_error_orientador(self):
        def fake_run(command, capture_output, text, timeout):
            result = MagicMock()
            result.returncode = 255
            result.stdout = ""
            result.stderr = "scp: Permission denied"
            return result

        with patch("app.publish.subprocess.run", side_effect=fake_run):
            with self.assertRaises(RuntimeError) as context:
                publish_database(self.app)

        self.assertIn("Permission denied", str(context.exception))


if __name__ == "__main__":
    unittest.main()
