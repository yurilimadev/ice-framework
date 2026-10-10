import re
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from app import create_app
from app.db import get_db
from app.tasks import TaskRepository, today_in_timezone


class FrontendInterfaceTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def create_task(self, title, tags=None):
        with self.app.app_context():
            return TaskRepository(get_db()).create(
                title,
                5,
                6,
                7,
                tags=tags,
            )

    def test_base_and_empty_state_have_accessible_structure(self):
        response = self.client.get("/")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<html lang="pt-BR">', body)
        self.assertIn('name="viewport"', body)
        self.assertIn('class="skip-link"', body)
        self.assertIn('href="#main-content"', body)
        self.assertIn('<main id="main-content"', body)
        self.assertIn('styles.css', body)
        self.assertIn('app.js', body)
        self.assertIn('data-empty', body)
        self.assertIn("Criar primeira tarefa", body)

    def test_success_message_has_ephemeral_accessible_controls(self):
        with self.client.session_transaction() as session:
            session["_flashes"] = [("success", "Tarefa criada.")]

        response = self.client.get("/")
        body = response.get_data(as_text=True)

        self.assertIn('data-message', body)
        self.assertIn('role="status"', body)
        self.assertIn('data-dismiss-message', body)
        self.assertNotIn('Tarefa criada.', self.client.get("/").get_data(as_text=True))

    def test_task_form_has_associated_labels_and_required_ice_fields(self):
        response = self.client.get("/tasks/new")
        body = response.get_data(as_text=True)

        for field in ("title", "impact", "confidence", "ease", "deadline", "tags"):
            with self.subTest(field=field):
                self.assertRegex(body, rf'<label[^>]+for="{field}"')
                self.assertRegex(body, rf'<input[^>]+id="{field}"')

        self.assertRegex(body, r'<input[^>]+id="title"[^>]+required')
        for field in ("impact", "confidence", "ease"):
            self.assertRegex(body, rf'<input[^>]+id="{field}"[^>]+required')
        self.assertIn('aria-labelledby="form-title"', body)

    def test_overdue_and_completed_states_have_text_and_contract_selectors(self):
        overdue = self.create_task("Atrasada", ["Work"])
        completed = self.create_task("Concluida", ["Study"])
        today = today_in_timezone("America/Sao_Paulo")
        with self.app.app_context():
            repository = TaskRepository(get_db())
            repository.update(overdue.id, deadline=today - timedelta(days=1))
            repository.complete(completed.id)

        response = self.client.get("/?status=all")
        body = response.get_data(as_text=True)

        self.assertIn(f'data-task-id="{overdue.id}"', body)
        self.assertIn('data-task-status="open"', body)
        self.assertIn("data-overdue", body)
        self.assertIn("Atrasada", body)
        self.assertIn(f'data-task-id="{completed.id}"', body)
        self.assertIn('data-task-status="completed"', body)
        self.assertIn("Concluida", body)

    def test_styles_define_responsive_focus_and_reduced_motion_rules(self):
        css_path = Path(__file__).parents[1] / "app" / "static" / "styles.css"
        css = css_path.read_text(encoding="utf-8")

        self.assertIn("@media (max-width: 800px)", css)
        self.assertIn("@media (max-width: 520px)", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("min-width: 320px", css)

    def test_normal_text_colors_meet_wcag_aa_contrast(self):
        css_path = Path(__file__).parents[1] / "app" / "static" / "styles.css"
        css = css_path.read_text(encoding="utf-8")
        colors = {
            "muted": re.search(r"--muted:\s*(#[0-9a-fA-F]{6})", css).group(1),
            "completed status": re.search(
                r"\.status-label\.status-completed\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})",
                css,
            ).group(1),
        }

        for name, color in colors.items():
            with self.subTest(color=name):
                self.assertGreaterEqual(
                    self.contrast_ratio(color, "#ffffff"),
                    4.5,
                    f"{name} ({color}) nao alcanca contraste AA",
                )

    @staticmethod
    def contrast_ratio(foreground, background):
        def luminance(color):
            channels = [
                int(color[index : index + 2], 16) / 255
                for index in (1, 3, 5)
            ]
            channels = [
                value / 12.92
                if value <= 0.04045
                else ((value + 0.055) / 1.055) ** 2.4
                for value in channels
            ]
            return (
                0.2126 * channels[0]
                + 0.7152 * channels[1]
                + 0.0722 * channels[2]
            )

        lighter = max(luminance(foreground), luminance(background))
        darker = min(luminance(foreground), luminance(background))
        return (lighter + 0.05) / (darker + 0.05)


if __name__ == "__main__":
    unittest.main()


class DynamicPanelTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def test_painel_declara_regioes_dinamicas_para_troca_sem_reload(self):
        body = self.client.get("/").get_data(as_text=True)

        self.assertIn('class="panel-mode"', body)
        self.assertIn('data-dynamic-region="task-area"', body)
        self.assertIn('data-dynamic-region="view-count"', body)
        self.assertIn('data-dynamic-region="filter-feedback"', body)
        self.assertIn('id="task-area"', body)
        self.assertEqual(body.count("Aplicar filtros"), 1)
        self.assertRegex(
            body,
            r"<noscript>\s*<button[^>]+type=\"submit\"[^>]*>Aplicar filtros</button>\s*</noscript>",
        )

    def test_regioes_dinamicas_permanecem_em_filtro_aplicado(self):
        body = self.client.get("/?status=completed&order=deadline").get_data(as_text=True)

        self.assertIn('data-dynamic-region="task-area"', body)
        self.assertIn('data-dynamic-region="view-count"', body)
        self.assertIn('data-dynamic-region="filter-feedback"', body)

    def test_estilos_e_script_carregam_modo_painel_e_estados_de_espera(self):
        root = Path(__file__).parents[1]
        css = (root / "app" / "static" / "styles.css").read_text(encoding="utf-8")
        script = (root / "app" / "static" / "app.js").read_text(encoding="utf-8")

        for snippet in (
            "body.panel-mode",
            "body.panel-mode .task-area { min-height: 0; overflow-y: auto; }",
            "body.panel-mode .hero-section { padding-bottom: 1.5rem; }",
            "body.panel-mode .filter-form { gap: var(--space-4); }",
            "body.panel-mode .tag-options { max-height: 8.5rem; overflow-y: auto;",
            ".task-area.is-refreshing",
            ".task-area.is-slow",
            ".sync-error",
        ):
            with self.subTest(css=snippet):
                self.assertIn(snippet, css)

        for snippet in (
            "data-dynamic-region",
            "history.replaceState",
            "AbortController",
            "is-refreshing",
            "is-slow",
            "sync-error",
        ):
            with self.subTest(js=snippet):
                self.assertIn(snippet, script)


if __name__ == "__main__":
    unittest.main()


class DigestButtonTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def _configure_smtp(self):
        self.app.config.update(
            {
                "SMTP_HOST": "smtp.exemplo.com",
                "SMTP_USER": "remetente@exemplo.com",
                "SMTP_PASSWORD": "senhadeapp",
                "SMTP_FROM": "remetente@exemplo.com",
                "DIGEST_TO": "destino@exemplo.com",
            }
        )

    def test_botao_enviar_resumo_somente_com_smtp_configurado(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Enviar resumo", body)

        self._configure_smtp()
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("Enviar resumo", body)
        self.assertIn("data-busy-form", body)
        self.assertIn("/digest/send", body)

        body_tags = self.client.get("/tags").get_data(as_text=True)
        self.assertIn("Enviar resumo", body_tags)
        self.assertIn('class="panel-mode"', body_tags)

    def test_botao_publicar_somente_com_deploy_configurado(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Publicar", body)

        self.app.config.update(
            {
                "DEPLOY_HOST": "usuario@servidor",
                "DEPLOY_KEY_PATH": "/tmp/chave-teste",
                "DEPLOY_TARGET_PATH": "~/ice-framework/data/app.sqlite3",
            }
        )
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("Publicar", body)
        self.assertIn("/publish", body)

        body_tags = self.client.get("/tags").get_data(as_text=True)
        self.assertIn("Publicar", body_tags)
