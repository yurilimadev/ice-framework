import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app.db import get_db
from app.peixe import LeadStatus, PeixeRepository
from app.peixe_digest import (
    render_daily_html,
    render_daily_text,
    render_weekly_html,
    render_weekly_text,
    send_peixe_daily,
    send_peixe_weekly,
)


class PeixeDigestTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
                "SMTP_HOST": "smtp.exemplo.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "remetente@exemplo.com",
                "SMTP_PASSWORD": "senhadeapp",
                "SMTP_FROM": "remetente@exemplo.com",
                "PEIXE_TO": "peixe@exemplo.com",
                "PEIXE_BASE_URL": "https://ice.exemplo.com",
            }
        )

    def tearDown(self):
        self.directory.cleanup()

    def create_mission(self):
        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            lead = repository.create_lead(
                "Clinica Sorriso",
                "odontologia",
                "Natal",
                "whatsapp",
                "5511999999999",
                "Posts sobre implantes",
                contact="Dra. Ana",
            )
            repository.update_status(lead.id, LeadStatus.TO_SEND)
            return lead

    @staticmethod
    def _fake_server():
        server = MagicMock()
        server.__enter__.return_value = server
        return server

    def test_daily_renders_mission_message_stats_and_link(self):
        self.create_mission()
        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            text = render_daily_text(repository, "https://ice.exemplo.com")
            html = render_daily_html(repository, "https://ice.exemplo.com")

        self.assertIn("Clinica Sorriso", text)
        self.assertIn("Dra. Ana", text)
        self.assertIn("Posts sobre implantes", text)
        self.assertIn("pode ser por aqui?", text)
        self.assertIn("Aprendiz", text)
        self.assertIn("https://ice.exemplo.com/peixe", text)
        self.assertIn("Clinica Sorriso", html)
        self.assertIn("Missao de hoje", html)
        self.assertIn("https://ice.exemplo.com/peixe", html)
        self.assertIn("#082f3a", html)

    def test_weekly_renders_numbers_quest_learning_and_link(self):
        lead = self.create_mission()
        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            repository.log_interaction(lead.id, "mensagem")
            repository.log_interaction(lead.id, "resposta")
            repository.log_interaction(lead.id, "conversa")
            repository.log_interaction(lead.id, "proposta")
            repository.set_setting("weekly_learning", "Menos volume.")
            repository.set_setting("weekly_blocker", "Agenda.")
            text = render_weekly_text(repository, "https://ice.exemplo.com")
            html = render_weekly_html(repository, "https://ice.exemplo.com")

        self.assertIn("Mensagens: 1", text)
        self.assertIn("Respostas: 1", text)
        self.assertIn("Conversas: 1", text)
        self.assertIn("Propostas: 1", text)
        self.assertIn("Quest:", text)
        self.assertIn("Aprendizado: Menos volume.", text)
        self.assertIn("Bloqueio: Agenda.", text)
        self.assertIn("https://ice.exemplo.com/peixe/semana", text)
        self.assertIn("Fechamento da semana", html)
        self.assertIn("Menos volume.", html)

    def test_send_daily_uses_peixe_to_and_attaches_text_and_html(self):
        self.create_mission()
        server = self._fake_server()

        with patch("app.peixe_digest.smtplib.SMTP", return_value=server) as factory:
            message = send_peixe_daily(self.app)

        factory.assert_called_once_with("smtp.exemplo.com", 587)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("remetente@exemplo.com", "senhadeapp")
        email = server.send_message.call_args[0][0]
        self.assertEqual(email["To"], "peixe@exemplo.com")
        self.assertEqual(email["From"], "remetente@exemplo.com")
        self.assertIn("missão de hoje", email["Subject"])
        self.assertEqual(
            [part.get_content_type() for part in email.get_payload()],
            ["text/plain", "text/html"],
        )
        self.assertIn("Resumo diario do Peixe enviado", message)

    def test_send_weekly_falls_back_to_digest_to(self):
        self.app.config.update({"PEIXE_TO": None, "DIGEST_TO": "digest@exemplo.com"})
        self.create_mission()
        server = self._fake_server()

        with patch("app.peixe_digest.smtplib.SMTP", return_value=server):
            send_peixe_weekly(self.app)

        email = server.send_message.call_args[0][0]
        self.assertEqual(email["To"], "digest@exemplo.com")
        self.assertIn("fechamento da semana", email["Subject"])

    def test_missing_smtp_or_recipient_raises_runtime_error(self):
        self.create_mission()
        self.app.config.update({"SMTP_HOST": None})
        with self.assertRaisesRegex(RuntimeError, "SMTP incompleto"):
            send_peixe_daily(self.app)

        self.app.config.update(
            {
                "SMTP_HOST": "smtp.exemplo.com",
                "PEIXE_TO": None,
                "DIGEST_TO": None,
            }
        )
        with self.assertRaisesRegex(RuntimeError, "PEIXE_TO ou DIGEST_TO"):
            send_peixe_daily(self.app)


if __name__ == "__main__":
    unittest.main()
