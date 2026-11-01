import re
import smtplib
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app.db import get_db
from app.tasks import GroupRepository, TaskRepository, today_in_timezone


class ApplicationRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.directory.name) / "app.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(self.database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def create_task(self, title="Task", tags=None, grupo_id=None):
        with self.app.app_context():
            return TaskRepository(get_db()).create(
                title,
                5,
                6,
                7,
                tags=tags,
                grupo_id=grupo_id,
            )

    def create_group(self, name="Projeto", kind="projeto"):
        with self.app.app_context():
            return GroupRepository(get_db()).create(name, kind)

    def test_read_routes_render_html_and_context_data(self):
        task = self.create_task("Backend real", ["Backend"])

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Backend real", response.data)
        self.assertIn(b"210", response.data)
        self.assertIn(b"Backend", response.data)
        self.assertIn(str(task.id).encode(), response.data)
        self.assertEqual(self.client.get("/tasks/new").status_code, 200)
        self.assertEqual(
            self.client.get(f"/tasks/{task.id}/edit").status_code,
            200,
        )

    def test_visual_stylesheet_is_available(self):
        response = self.client.get("/static/styles.css")
        body = response.get_data()
        response.close()

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"--cyan", body)

    def test_ephemeral_message_script_is_available(self):
        response = self.client.get("/static/app.js")
        body = response.get_data()
        response.close()

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"data-dismiss-message", body)
        self.assertIn(b"4000", body)

    def test_interface_selectors_cover_empty_overdue_and_delete_states(self):
        empty_response = self.client.get("/")
        self.assertIn(b"data-empty", empty_response.data)

        task = self.create_task("Prazo vencido", ["Straße"])
        with self.app.app_context():
            repository = TaskRepository(get_db())
            repository.update(
                task.id,
                deadline=today_in_timezone("America/Sao_Paulo") - timedelta(days=1),
            )

        response = self.client.get("/?status=all&overdue=1&tag=STRASSE")
        body = response.get_data(as_text=True)
        self.assertIn(f'data-task-id="{task.id}"', body)
        self.assertIn('data-task-status="open"', body)
        self.assertIn("data-overdue", body)
        self.assertIn("Atrasada", body)
        self.assertIn('value="Straße" checked', body)
        self.assertIn("window.confirm", body)

    def test_form_errors_are_associated_with_their_fields(self):
        response = self.client.post(
            "/tasks",
            data={
                "title": "Titulo preservado",
                "impact": "11",
                "confidence": "6",
                "ease": "7",
                "deadline": "",
                "tags": "",
            },
        )

        body = response.get_data(as_text=True)
        self.assertIn('id="error-impact"', body)
        self.assertIn('aria-describedby="error-impact"', body)
        self.assertIn('aria-invalid="true"', body)

    def test_create_and_update_use_post_redirect_get(self):
        create_response = self.client.post(
            "/tasks",
            data={
                "title": "Criada por HTTP",
                "impact": "8",
                "confidence": "9",
                "ease": "7",
                "deadline": "2030-01-02",
                "tags": "Backend, Estudos",
            },
        )

        self.assertEqual(create_response.status_code, 303)
        self.assertEqual(create_response.headers["Location"], "/")
        created_landing = self.client.get("/")
        self.assertIn(b"Criada por HTTP", created_landing.data)
        self.assertIn(b"Tarefa criada.", created_landing.data)
        self.assertNotIn(b"Tarefa criada.", self.client.get("/").data)

        with self.app.app_context():
            task = TaskRepository(get_db()).list()[0]

        update_response = self.client.post(
            f"/tasks/{task.id}",
            data={
                "title": "Atualizada por HTTP",
                "impact": "10",
                "confidence": "10",
                "ease": "10",
                "deadline": "",
                "tags": "Atualizada",
            },
        )

        self.assertEqual(update_response.status_code, 303)
        self.assertEqual(update_response.headers["Location"], "/")
        updated_landing = self.client.get("/")
        self.assertIn(b"Atualizada por HTTP", updated_landing.data)
        self.assertIn(b"Tarefa atualizada.", updated_landing.data)
        self.assertIn(b"1000", updated_landing.data)
        self.assertNotIn(b"Tarefa atualizada.", self.client.get("/").data)

    def test_invalid_form_returns_400_with_values_and_field_errors(self):
        response = self.client.post(
            "/tasks",
            data={
                "title": "Valor preservado",
                "impact": "11",
                "confidence": "",
                "ease": "abc",
                "deadline": "",
                "tags": "Backend",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Valor preservado", response.data)
        self.assertIn(b'data-error-field="impact"', response.data)
        self.assertIn(b'data-error-field="confidence"', response.data)
        self.assertIn(b'data-error-field="ease"', response.data)

    def test_invalid_filters_are_controlled_and_return_400(self):
        response = self.client.get("/?status=unknown")

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Status de filtro invalido", response.data)

        response = self.client.get("/?tag=" + ("x" * 31))
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'data-error-field="tag"', response.data)

    def test_filter_query_and_status_actions(self):
        open_task = self.create_task("Open", ["Work"])
        completed_task = self.create_task("Completed", ["Home"])
        self.client.post(f"/tasks/{completed_task.id}/complete")

        completed_response = self.client.get("/?status=completed")
        self.assertIn(b"Completed", completed_response.data)
        self.assertNotIn(b"Open", completed_response.data)

        tag_response = self.client.get("/?status=all&tag=WORK")
        self.assertIn(b"Open", tag_response.data)
        self.assertNotIn(b"Completed", tag_response.data)

        self.assertEqual(
            self.client.post(f"/tasks/{completed_task.id}/reopen").status_code,
            303,
        )
        self.assertEqual(
            self.client.post(f"/tasks/{open_task.id}/delete").status_code,
            303,
        )
        self.assertEqual(self.client.get(f"/tasks/{open_task.id}/edit").status_code, 404)

    def test_default_and_overdue_filters_exclude_completed_tasks(self):
        today = today_in_timezone("America/Sao_Paulo")
        overdue_task = self.create_task("Overdue", ["Work"])
        future_task = self.create_task("Future", ["Work"])
        completed_task = self.create_task("Completed overdue", ["Work"])

        with self.app.app_context():
            repository = TaskRepository(get_db())
            repository.update(overdue_task.id, deadline=today - timedelta(days=1))
            repository.update(future_task.id, deadline=today + timedelta(days=1))
            repository.update(completed_task.id, deadline=today - timedelta(days=1))
            repository.complete(completed_task.id)

        default_response = self.client.get("/")
        self.assertIn(b"Overdue", default_response.data)
        self.assertIn(b"Future", default_response.data)
        self.assertNotIn(b"Completed overdue", default_response.data)

        overdue_response = self.client.get("/?overdue=1")
        self.assertIn(b"Overdue", overdue_response.data)
        self.assertNotIn(b"Future", overdue_response.data)
        self.assertNotIn(b"Completed overdue", overdue_response.data)

    def test_repeated_tags_and_explicit_orders_are_consumed_by_http(self):
        first = self.create_task("First", ["Work", "Study"])
        second = self.create_task("Second", ["Work"])

        tag_response = self.client.get("/?status=all&tag=WORK&tag=STUDY")
        self.assertIn(b"First", tag_response.data)
        self.assertNotIn(b"Second", tag_response.data)

        deadline_response = self.client.get("/?status=all&order=deadline")
        self.assertEqual(deadline_response.status_code, 200)
        self.assertIn(str(first.id).encode(), deadline_response.data)
        self.assertIn(str(second.id).encode(), deadline_response.data)

        created_response = self.client.get("/?status=all&order=created_at")
        self.assertEqual(created_response.status_code, 200)
        self.assertIn(str(first.id).encode(), created_response.data)
        self.assertIn(str(second.id).encode(), created_response.data)

    def test_invalid_filter_values_return_400_without_exception(self):
        invalid_filters = (
            ("/?overdue=0", b'data-error-field="overdue"'),
            ("/?order=unknown", b'data-error-field="order"'),
            ("/?tag=", b'data-error-field="tag"'),
        )
        for url, error_marker in invalid_filters:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 400)
                self.assertIn(error_marker, response.data)

    def test_update_validation_returns_400_and_preserves_submitted_values(self):
        task = self.create_task("Original", ["Work"])

        response = self.client.post(
            f"/tasks/{task.id}",
            data={
                "title": "Titulo preservado",
                "impact": "0",
                "confidence": "10",
                "ease": "10",
                "deadline": "not-a-date",
                "tags": "Work, ,Study",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Titulo preservado", response.data)
        self.assertIn(b'data-error-field="impact"', response.data)
        self.assertIn(b'data-error-field="deadline"', response.data)
        self.assertIn(b'data-error-field="tags"', response.data)
        with self.app.app_context():
            persisted = TaskRepository(get_db()).get(task.id)
        self.assertEqual(persisted.title, "Original")

    def test_lifecycle_actions_return_303_and_persist_across_new_instance(self):
        create_response = self.client.post(
            "/tasks",
            data={
                "title": "Persistida por rota",
                "impact": "5",
                "confidence": "6",
                "ease": "7",
                "deadline": "",
                "tags": "Saved",
            },
        )
        self.assertEqual(create_response.status_code, 303)

        with self.app.app_context():
            task = TaskRepository(get_db()).list()[0]

        complete_response = self.client.post(f"/tasks/{task.id}/complete")
        self.assertEqual(complete_response.status_code, 303)
        self.assertNotIn(b"Persistida por rota", self.client.get("/").data)
        self.assertIn(b"Persistida por rota", self.client.get("/?status=completed").data)

        reopen_response = self.client.post(f"/tasks/{task.id}/reopen")
        self.assertEqual(reopen_response.status_code, 303)

        second_app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(self.database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        second_response = second_app.test_client().get("/")
        self.assertEqual(second_response.status_code, 200)
        self.assertIn(b"Persistida por rota", second_response.data)
        self.assertIn(b"210", second_response.data)
        self.assertIn(b"Saved", second_response.data)

        delete_response = self.client.post(f"/tasks/{task.id}/delete")
        self.assertEqual(delete_response.status_code, 303)
        self.assertEqual(self.client.get(f"/tasks/{task.id}/edit").status_code, 404)

    def test_group_pages_create_rename_archive_and_delete(self):
        group = self.create_group("Estudos", "projeto")

        page = self.client.get("/grupos")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Estudos", body)
        self.assertIn(f'data-group-id="{group.id}"', body)
        self.assertIn('data-group-kind="projeto"', body)
        self.assertIn('name="grupo_id"', self.client.get("/tasks/new").get_data(as_text=True))

        created = self.client.post(
            "/grupos", data={"name": "Saude", "kind": "area"}
        )
        self.assertEqual(created.status_code, 303)
        body = self.client.get("/grupos").get_data(as_text=True)
        self.assertIn("Saude", body)
        self.assertIn("Grupo criado.", body)

        created_resource = self.client.post(
            "/grupos", data={"name": "Referencias", "kind": "recurso"}
        )
        self.assertEqual(created_resource.status_code, 303)
        body = self.client.get("/grupos").get_data(as_text=True)
        self.assertIn("Referencias", body)
        self.assertIn('data-group-kind="recurso"', body)
        self.assertIn("Recurso", body)

        with self.app.app_context():
            area = next(
                item
                for item in GroupRepository(get_db()).list()
                if item.name == "Saude"
            )

        renamed = self.client.post(
            f"/grupos/{area.id}/rename", data={"name": "Bem-estar"}
        )
        self.assertEqual(renamed.status_code, 303)
        self.assertIn("Bem-estar", self.client.get("/grupos").get_data(as_text=True))

        archived = self.client.post(f"/grupos/{area.id}/archive")
        self.assertEqual(archived.status_code, 303)
        self.assertIn("Arquivado", self.client.get("/grupos").get_data(as_text=True))

        deleted = self.client.post(f"/grupos/{group.id}/delete")
        self.assertEqual(deleted.status_code, 303)
        self.assertNotIn(
            f'data-group-id="{group.id}"',
            self.client.get("/grupos").get_data(as_text=True),
        )

    def test_panel_organizes_tasks_in_group_sections(self):
        project = self.create_group("Projeto X", "projeto")
        area = self.create_group("Area Y", "area")
        resource = self.create_group("Recurso Z", "recurso")
        archived = self.create_group("Arquivado W", "projeto")
        with self.app.app_context():
            GroupRepository(get_db()).archive(archived.id)

        aligned = self.create_task("Card projeto", grupo_id=project.id)
        self.create_task("Card area", grupo_id=area.id)
        self.create_task("Card recurso", grupo_id=resource.id)
        self.create_task("Card arquivado", grupo_id=archived.id)
        self.create_task("Card solto")

        form_body = self.client.get("/tasks/new").get_data(as_text=True)
        self.assertIn('name="grupo_id"', form_body)
        self.assertIn("Projeto X (Projeto)", form_body)
        self.assertIn("Area Y (Área)", form_body)
        self.assertIn("Recurso Z (Recurso)", form_body)

        body = self.client.get("/?status=all").get_data(as_text=True)
        self.assertEqual(
            re.findall(r'data-group-section="([^"]+)"', body),
            ["projetos", "areas", "recursos", "arquivos", "sem-grupo"],
        )
        for title in ("Projetos", "Áreas", "Recursos", "Arquivos", "Sem grupo"):
            self.assertIn(title, body)
        for group in (project, area, resource, archived):
            self.assertIn(f'data-section-group-id="{group.id}"', body)
        for title in (
            "Card projeto",
            "Card area",
            "Card recurso",
            "Card arquivado",
            "Card solto",
        ):
            self.assertIn(title, body)
        self.assertNotIn('name="group"', body)

        updated = self.client.post(
            f"/tasks/{aligned.id}",
            data={
                "title": "Card projeto reagrupado",
                "impact": "5",
                "confidence": "6",
                "ease": "7",
                "deadline": "",
                "tags": "",
                "grupo_id": str(resource.id),
            },
        )
        self.assertEqual(updated.status_code, 303)
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("Card projeto reagrupado", body)
        self.assertIn(f'data-section-group-id="{resource.id}"', body)

    def test_deleting_group_route_detaches_task_and_preserves_tags(self):
        group = self.create_group("Temporario", "area")
        task = self.create_task("Card do grupo", ["Work"], grupo_id=group.id)

        response = self.client.post(f"/grupos/{group.id}/delete")

        self.assertEqual(response.status_code, 303)
        with self.app.app_context():
            detached = TaskRepository(get_db()).get(task.id)
        self.assertIsNone(detached.grupo_id)
        self.assertEqual(detached.tags, ("Work",))

    def test_nonexistent_group_in_form_returns_400(self):
        response = self.client.post(
            "/tasks",
            data={
                "title": "Grupo inexistente",
                "impact": "5",
                "confidence": "6",
                "ease": "7",
                "deadline": "",
                "tags": "",
                "grupo_id": "999",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'data-error-field="grupo_id"', response.data)

    def test_missing_group_returns_404(self):
        self.assertEqual(self.client.post("/grupos/999/rename").status_code, 404)
        self.assertEqual(self.client.post("/grupos/999/archive").status_code, 404)
        self.assertEqual(self.client.post("/grupos/999/delete").status_code, 404)

    def test_missing_task_returns_404(self):
        self.assertEqual(self.client.get("/tasks/999/edit").status_code, 404)
        self.assertEqual(self.client.post("/tasks/999", data={}).status_code, 404)
        self.assertEqual(self.client.post("/tasks/999/complete").status_code, 404)
        self.assertEqual(self.client.post("/tasks/999/reopen").status_code, 404)
        self.assertEqual(self.client.post("/tasks/999/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()


class DigestSendRouteTestCase(unittest.TestCase):
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
                "DIGEST_TO": "destino@exemplo.com",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def create_task(self, title="Task", tags=None):
        with self.app.app_context():
            return TaskRepository(get_db()).create(
                title,
                5,
                6,
                7,
                tags=tags,
            )

    def _fake_server(self):
        server = MagicMock()
        server.__enter__.return_value = server
        return server

    def test_envio_bem_sucedido_flash_e_volta_para_a_origem(self):
        self.create_task("Com resumo", ["Email"])

        with patch("app.digest.smtplib.SMTP", return_value=self._fake_server()) as factory:
            response = self.client.post(
                "/digest/send",
                headers={"Referer": "http://localhost/tags"},
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Resumo enviado para destino@exemplo.com", response.get_data(as_text=True))
        self.assertIn(b"/tags", response.request.url.encode())
        factory.assert_called_once_with("smtp.exemplo.com", 587)

    def test_smtp_sem_configuracao_gera_flash_orientador(self):
        self.app.config.update(
            {
                "SMTP_HOST": None,
                "SMTP_USER": None,
                "SMTP_PASSWORD": None,
                "SMTP_FROM": None,
                "DIGEST_TO": None,
            }
        )

        response = self.client.post("/digest/send", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nao consegui enviar o resumo", response.get_data(as_text=True))

    def test_falha_de_smtp_gera_flash_de_erro_sem_explodir(self):
        server = self._fake_server()
        server.login.side_effect = smtplib.SMTPAuthenticationError(535, "negado")

        with patch("app.digest.smtplib.SMTP", return_value=server):
            response = self.client.post("/digest/send", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nao consegui enviar o resumo", response.get_data(as_text=True))


class PublishRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(Path(self.directory.name) / "app.sqlite3"),
                "APP_TIMEZONE": "America/Sao_Paulo",
                "DEPLOY_HOST": "usuario@servidor",
                "DEPLOY_PORT": "8022",
                "DEPLOY_KEY_PATH": "/tmp/chave-teste",
                "DEPLOY_TARGET_PATH": "~/ice-framework/data/app.sqlite3",
                "DEPLOY_SV_SERVICE": "ice-framework",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.directory.cleanup()

    def _fake_run(self, *args, **kwargs):
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    def test_publicar_sucesso_flash_e_redireciona_para_origem(self):
        with self.app.app_context():
            TaskRepository(get_db()).create("Publicada", 5, 6, 7)

        with patch("app.publish.subprocess.run", side_effect=self._fake_run):
            response = self.client.post(
                "/publish",
                headers={"Referer": "http://localhost/tags"},
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Publicado no servidor", response.get_data(as_text=True))

    def test_publicar_sem_configuracao_flash_orientador(self):
        self.app.config.update(
            {"DEPLOY_HOST": None, "DEPLOY_KEY_PATH": None, "DEPLOY_TARGET_PATH": None}
        )

        response = self.client.post("/publish", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nao consegui publicar", response.get_data(as_text=True))
