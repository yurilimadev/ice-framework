import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app.db import get_db
from app.peixe import InteractionKind, LeadStatus, PeixeRepository
from app.peixe_routes import build_message


class PeixeRoutesTestCase(unittest.TestCase):
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

    def repository(self):
        with self.app.app_context():
            return PeixeRepository(get_db(), "America/Sao_Paulo")

    def create_lead(self, **overrides):
        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            values = {
                "company": "Clinica Sorriso",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "whatsapp",
                "handle": "5511999999999",
                "observation": "Posts sobre implantes",
                "contact": "Dra. Ana",
            }
            values.update(overrides)
            return repository.create_lead(**values)

    def test_dashboard_shows_mission_and_ice_priorities(self):
        lead = self.create_lead()
        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            repository.update_status(lead.id, LeadStatus.TO_SEND)
            from app.tasks import TaskRepository

            TaskRepository(get_db(), "America/Sao_Paulo").create(
                "Preparar proposta", 9, 8, 7
            )

        response = self.client.get("/peixe")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("MISSAO DO DIA", body)
        self.assertIn("Clinica Sorriso", body)
        self.assertIn("Dra. Ana", body)
        self.assertIn("Preparar proposta", body)
        self.assertIn("mission-message", body)
        self.assertIn("data-copy-target", body)
        self.assertIn("wa.me/5511999999999", body)

    def test_create_lead_redirects_and_appears_in_pipeline(self):
        response = self.client.post(
            "/peixe/leads",
            data={
                "company": "Odonto Centro",
                "contact": "Dr. Bruno",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "instagram",
                "handle": "@odontocentro",
                "observation": "Conteudo sobre alinhadores",
            },
        )

        self.assertEqual(response.status_code, 303)
        body = self.client.get("/peixe/leads").get_data(as_text=True)
        self.assertIn("Odonto Centro", body)
        self.assertIn("Instagram", body)
        self.assertIn('data-lead-status="novo"', body)

    def test_edit_lead_form_and_update(self):
        lead = self.create_lead(handle="084994017101")

        form = self.client.get(f"/peixe/leads/{lead.id}/editar")
        form_body = form.get_data(as_text=True)
        self.assertEqual(form.status_code, 200)
        self.assertIn("EDITAR LEAD", form_body)
        self.assertIn("Salvar alteracoes", form_body)
        self.assertIn('value="Clinica Sorriso"', form_body)
        self.assertIn('value="084994017101"', form_body)

        response = self.client.post(
            f"/peixe/leads/{lead.id}/editar",
            data={
                "company": "Clinica Sorriso Norte",
                "contact": "Dra. Ana Paula",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "whatsapp",
                "handle": "84994017101",
                "observation": "voces tem boas avaliacoes no Google",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Lead atualizado", body)
        self.assertIn("Clinica Sorriso Norte", body)
        self.assertIn("Dra. Ana Paula", body)
        self.assertIn("wa.me/5584994017101", body)
        self.assertIn(f'href="/peixe/leads/{lead.id}/editar"', body)
        with self.app.app_context():
            updated = PeixeRepository(get_db()).get_lead(lead.id)
            self.assertEqual(updated.company, "Clinica Sorriso Norte")
            self.assertEqual(updated.contact, "Dra. Ana Paula")
            self.assertEqual(updated.handle, "84994017101")
            self.assertEqual(updated.status, LeadStatus.NEW)

    def test_edit_lead_invalid_and_missing(self):
        lead = self.create_lead()
        invalid = self.client.post(
            f"/peixe/leads/{lead.id}/editar",
            data={
                "company": " ",
                "contact": "",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "whatsapp",
                "handle": "84994017101",
                "observation": "Teste",
            },
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn(b'data-error-field="company"', invalid.data)

        self.assertEqual(self.client.get("/peixe/leads/999/editar").status_code, 404)
        self.assertEqual(
            self.client.post("/peixe/leads/999/editar", data={}).status_code, 404
        )

    def test_whatsapp_link_ignores_leading_zero(self):
        lead = self.create_lead(handle="084994017101")
        body = self.client.get(f"/peixe/leads/{lead.id}").get_data(as_text=True)
        self.assertIn("wa.me/5584994017101", body)

        with_country = self.create_lead(
            company="Outra Clinica", handle="55084994017102"
        )
        body = self.client.get(f"/peixe/leads/{with_country.id}").get_data(
            as_text=True
        )
        self.assertIn("wa.me/5584994017102", body)

    def test_invalid_lead_form_returns_400_with_field_error(self):
        response = self.client.post(
            "/peixe/leads",
            data={
                "company": " ",
                "contact": "",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "telefone",
                "handle": "123",
                "observation": "Teste",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'data-error-field="company"', response.data)

        channel_response = self.client.post(
            "/peixe/leads",
            data={
                "company": "Clinica",
                "contact": "",
                "sector": "odontologia",
                "city": "Natal",
                "channel": "telefone",
                "handle": "123",
                "observation": "Teste",
            },
        )
        self.assertEqual(channel_response.status_code, 400)
        self.assertIn(b'data-error-field="channel"', channel_response.data)

    def test_send_and_followup_actions_update_status_xp_and_timeline(self):
        lead = self.create_lead()

        sent = self.client.post(f"/peixe/leads/{lead.id}/send", follow_redirects=True)
        self.assertEqual(sent.status_code, 200)
        self.assertIn("Mensagem registrada", sent.get_data(as_text=True))

        with self.app.app_context():
            repository = PeixeRepository(get_db(), "America/Sao_Paulo")
            updated = repository.get_lead(lead.id)
            self.assertEqual(updated.status, LeadStatus.SENT)
            self.assertIsNotNone(updated.next_action_at)
            self.assertEqual(repository.xp_total(), 10)
            self.assertEqual(repository.list_interactions(lead.id)[0].kind, InteractionKind.MESSAGE)

        for path, status in (
            ("reply", LeadStatus.REPLIED),
            ("conversation", LeadStatus.CONVERSATION),
            ("proposal", LeadStatus.PROPOSAL),
            ("pilot", LeadStatus.PILOT),
        ):
            response = self.client.post(
                f"/peixe/leads/{lead.id}/{path}", follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            with self.app.app_context():
                self.assertEqual(
                    PeixeRepository(get_db()).get_lead(lead.id).status, status
                )

        detail = self.client.get(f"/peixe/leads/{lead.id}").get_data(as_text=True)
        self.assertIn("data-interaction-kind=\"mensagem\"", detail)
        self.assertIn("data-interaction-kind=\"piloto\"", detail)
        self.assertIn("Piloto", detail)

    def test_note_and_pause_actions(self):
        lead = self.create_lead()
        with self.app.app_context():
            repository = PeixeRepository(get_db())
            repository.update_status(lead.id, LeadStatus.TO_SEND)
            repository.update_status(lead.id, LeadStatus.SENT)

        note = self.client.post(
            f"/peixe/leads/{lead.id}/note",
            data={"notes": "Prefere contato a tarde."},
            follow_redirects=True,
        )
        self.assertEqual(note.status_code, 200)
        self.assertIn("Nota registrada", note.get_data(as_text=True))

        paused = self.client.post(
            f"/peixe/leads/{lead.id}/pause", follow_redirects=True
        )
        self.assertEqual(paused.status_code, 200)
        with self.app.app_context():
            repository = PeixeRepository(get_db())
            self.assertEqual(
                repository.get_lead(lead.id).status, LeadStatus.PAUSED
            )
            self.assertEqual(repository.xp_total(), 0)

    def test_missing_lead_returns_404(self):
        self.assertEqual(self.client.get("/peixe/leads/999").status_code, 404)
        self.assertEqual(self.client.post("/peixe/leads/999/send").status_code, 404)
        self.assertEqual(self.client.post("/peixe/leads/999/note").status_code, 404)

    def test_week_page_and_saved_learning(self):
        lead = self.create_lead()
        with self.app.app_context():
            repository = PeixeRepository(get_db())
            repository.log_interaction(lead.id, "mensagem")
            repository.log_interaction(lead.id, "resposta")
            repository.log_interaction(lead.id, "conversa")

        page = self.client.get("/peixe/semana")
        body = page.get_data(as_text=True)
        self.assertEqual(page.status_code, 200)
        self.assertIn("mensagens", body)
        self.assertIn("1", body)
        self.assertIn("Aprendizado e bloqueio", body)

        saved = self.client.post(
            "/peixe/semana",
            data={"learning": "Menos volume, mais contexto.", "blocker": "Agenda"},
            follow_redirects=True,
        )
        self.assertEqual(saved.status_code, 200)
        with self.app.app_context():
            repository = PeixeRepository(get_db())
            self.assertEqual(
                repository.get_setting("weekly_learning"),
                "Menos volume, mais contexto.",
            )
            self.assertEqual(repository.get_setting("weekly_blocker"), "Agenda")

    def test_dashboard_email_buttons_and_manual_send(self):
        self.create_lead()
        body = self.client.get("/peixe").get_data(as_text=True)
        self.assertNotIn("Enviar resumo diario", body)

        self.app.config.update(
            {
                "SMTP_HOST": "smtp.exemplo.com",
                "SMTP_USER": "remetente@exemplo.com",
                "SMTP_PASSWORD": "senhadeapp",
                "SMTP_FROM": "remetente@exemplo.com",
                "PEIXE_TO": "peixe@exemplo.com",
            }
        )
        body = self.client.get("/peixe").get_data(as_text=True)
        self.assertIn("Enviar resumo diario", body)
        self.assertIn("Enviar fechamento", body)

        server = MagicMock()
        server.__enter__.return_value = server
        with patch("app.peixe_digest.smtplib.SMTP", return_value=server):
            response = self.client.post("/peixe/email/daily", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Resumo diario do Peixe enviado", response.get_data(as_text=True))

    def test_agenda_shows_next_seven_days(self):
        lead = self.create_lead()
        with self.app.app_context():
            repository = PeixeRepository(get_db())
            repository.update_status(lead.id, LeadStatus.TO_SEND)
            repository.update_status(lead.id, LeadStatus.SENT)
            from app.peixe_routes import _today

            with self.app.test_request_context():
                next_day = _today() + timedelta(days=1)
            repository.set_next_action(lead.id, next_day)

        page = self.client.get("/peixe/agenda")
        body = page.get_data(as_text=True)
        self.assertEqual(page.status_code, 200)
        self.assertIn(next_day.strftime("%d/%m/%Y"), body)
        self.assertIn("Clinica Sorriso", body)

    def test_message_builder_and_pipeline_filter(self):
        lead = self.create_lead()
        message = build_message(lead)
        self.assertIn("Oi, Dra. Ana", message)
        self.assertIn("Posts sobre implantes", message)
        self.assertIn("clínicas odontológicas de Natal", message)
        self.assertIn("sem venda", message)
        self.assertIn("2 perguntas", message)
        self.assertIn("pode ser por aqui?", message)

        other = self.create_lead(
            company="Studio Estetica",
            sector="Estetica",
            city="Parnamirim",
            channel="instagram",
            handle="@studio",
        )
        other_message = build_message(other)
        self.assertIn("clínicas de estetica de Parnamirim", other_message)

        with self.app.app_context():
            repository = PeixeRepository(get_db())
            repository.update_status(lead.id, LeadStatus.TO_SEND)
        page = self.client.get("/peixe/leads?status=a_enviar").get_data(as_text=True)
        self.assertIn("Clinica Sorriso", page)
        self.assertNotIn("Nenhum lead neste filtro", page)

    def test_nav_has_peixe_link(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('href="/peixe"', body)
        self.assertIn("Peixe", body)


if __name__ == "__main__":
    unittest.main()
