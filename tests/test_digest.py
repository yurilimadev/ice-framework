"""Testes do resumo por email (app.digest)."""

import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app import create_app
from app.digest import render_digest_html, send_digest


def _task(title="Tarefa", score=500, deadline=None, impact=5, confidence=5, ease=5):
    return SimpleNamespace(
        title=title,
        score=score,
        deadline=deadline,
        impact=impact,
        confidence=confidence,
        ease=ease,
    )


class RenderDigestHtmlTestCase(unittest.TestCase):
    def test_render_sem_tarefas_mostra_mensagem_de_descanso(self):
        html = render_digest_html({"open": [], "overdue": []})

        self.assertIn("Nenhuma tarefa pendente", html)
        self.assertIn("Bom descanso!", html)
        self.assertIn("0 tarefa(s) aberta(s)", html)

    def test_render_mostra_titulo_score_e_prazo(self):
        task = _task("Estudar ICE", score=500, deadline=date(2026, 12, 31))
        html = render_digest_html({"open": [task], "overdue": []})

        self.assertIn("<strong>Estudar ICE</strong>", html)
        self.assertIn("score 500", html)
        self.assertIn("31/12/2026", html)
        self.assertNotIn("(atrasada)", html)

    def test_render_mostra_badge_de_atrasada(self):
        task = _task("Pagar boleto", score=125, deadline=date(2026, 9, 20))
        html = render_digest_html({"open": [task], "overdue": [task]})

        self.assertIn("(atrasada)", html)


class SendDigestTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database_path = Path(self.directory.name) / "app.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
                "SMTP_HOST": "smtp.exemplo.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "remetente@exemplo.com",
                "SMTP_PASSWORD": "senhadeapp16letras",
                "SMTP_FROM": "remetente@exemplo.com",
                "DIGEST_TO": "destino@exemplo.com",
            }
        )

    def tearDown(self):
        self.directory.cleanup()

    @staticmethod
    def _fake_server():
        server = MagicMock()
        server.__enter__.return_value = server
        return server

    def test_configuracao_incompleta_mostra_erro_orientador(self):
        self.app.config.update(
            {
                "SMTP_HOST": None,
                "SMTP_USER": None,
                "SMTP_PASSWORD": None,
                "SMTP_FROM": None,
                "DIGEST_TO": None,
            }
        )

        with self.assertRaises(RuntimeError) as context:
            send_digest(self.app)

        self.assertIn("SMTP incompleto", str(context.exception))

    def test_envio_conecta_com_starttls_envia_mensagem_e_relata_destino(self):
        server = self._fake_server()

        with patch("app.digest.smtplib.SMTP", return_value=server) as smtp_factory:
            message = send_digest(self.app)

        smtp_factory.assert_called_once_with("smtp.exemplo.com", 587)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with(
            "remetente@exemplo.com", "senhadeapp16letras"
        )
        server.send_message.assert_called_once()

        email = server.send_message.call_args[0][0]
        self.assertEqual(email["To"], "destino@exemplo.com")
        self.assertEqual(email["From"], "remetente@exemplo.com")
        self.assertIn("Resumo", email["Subject"])

        self.assertIn("Resumo enviado para destino@exemplo.com", message)


class DigestBrandingTestCase(unittest.TestCase):
    def test_html_tem_marca_e_rodape_da_identidade_ice(self):
        task = _task("Com marca", score=500, deadline=date(2026, 12, 31))
        html = render_digest_html({"open": [task], "overdue": []}, today="31/12/2026")

        self.assertIn("ICE", html)
        self.assertIn("FRAMEWORK", html)
        self.assertIn("31/12/2026", html)
        self.assertIn("prioridade com clareza", html)
        self.assertIn("#082f3a", html)

    def test_texto_puro_responde_tarefas_e_atrasadas(self):
        from app.digest import render_digest_text

        open_task = _task("Estudar", score=400, deadline=date(2026, 12, 31))
        text = render_digest_text({"open": [open_task], "overdue": [open_task]})

        self.assertIn("1 tarefa(s) aberta(s), 1 atrasada(s).", text)
        self.assertIn("- Estudar (score 400, prazo 31/12/2026 (atrasada))", text)

    def test_envio_anexa_texto_e_html_alternativos(self):
        app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": tempfile.mkdtemp() + "/app.sqlite3",
                "APP_TIMEZONE": "America/Sao_Paulo",
                "SMTP_HOST": "smtp.exemplo.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "remetente@exemplo.com",
                "SMTP_PASSWORD": "senhadeapp",
                "SMTP_FROM": "remetente@exemplo.com",
                "DIGEST_TO": "destino@exemplo.com",
            }
        )
        server = MagicMock()
        server.__enter__.return_value = server

        with patch("app.digest.smtplib.SMTP", return_value=server):
            send_digest(app)

        email = server.send_message.call_args[0][0]
        self.assertEqual(email.get_content_maintype(), "multipart")
        parts = email.get_payload()
        self.assertEqual(
            [part.get_content_type() for part in parts],
            ["text/plain", "text/html"],
        )
