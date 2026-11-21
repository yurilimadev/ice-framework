import sqlite3
import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from app import create_app
from app.db import get_db, get_schema_version
from app.peixe import (
    Channel,
    InteractionKind,
    LeadNotFoundError,
    LeadStatus,
    PeixeRepository,
    level_for,
    xp_for,
)
from app.tasks import GroupRepository, TaskRepository, ValidationError

TZ = ZoneInfo("America/Sao_Paulo")


def local_today():
    return datetime.now(TZ).date()


def local_noon(days_ago=0):
    today = local_today()
    moment = datetime.combine(today - timedelta(days=days_ago), time(12), tzinfo=TZ)
    return moment.astimezone(timezone.utc)


class PeixeDomainTestCase(unittest.TestCase):
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

    def tearDown(self):
        self.directory.cleanup()

    def repository(self):
        return PeixeRepository(get_db(), "America/Sao_Paulo")

    def create_lead(self, **overrides):
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
        return self.repository().create_lead(**values)

    def test_new_database_uses_schema_5_and_default_settings(self):
        with self.app.app_context():
            self.assertEqual(get_schema_version(), 5)
            settings = dict(
                get_db().execute("SELECT key, value FROM settings").fetchall()
            )
            self.assertEqual(settings["daily_target"], "1")
            self.assertEqual(settings["weekly_messages"], "5")
            self.assertEqual(settings["current_ocean"], "odontologia")
            self.assertEqual(settings["current_city"], "Natal")

    def test_upgrade_from_schema_4_preserves_tasks_tags_groups_and_links(self):
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        with tempfile.TemporaryDirectory() as upgrade_directory:
            path = Path(upgrade_directory) / "app.sqlite3"
            connection = sqlite3.connect(path)
            try:
                for name in (
                    "001_foundation.sql",
                    "002_tasks.sql",
                    "003_grupos.sql",
                    "004_grupos_recurso.sql",
                ):
                    connection.executescript((migrations / name).read_text())
                created_at = datetime.now(timezone.utc).replace(
                    microsecond=0
                ).isoformat()
                connection.execute(
                    "INSERT INTO tags (id, name) VALUES (?, ?)", (1, "Work")
                )
                connection.execute(
                    """
                    INSERT INTO grupos (id, name, kind, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (2, "Projeto antigo", "projeto", "active", created_at),
                )
                connection.execute(
                    """
                    INSERT INTO tasks
                        (id, title, impact, confidence, ease, deadline, status,
                         created_at, grupo_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (3, "Tarefa antiga", 2, 3, 4, None, "open", created_at, 2),
                )
                connection.execute(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (3, 1)
                )
                connection.commit()
            finally:
                connection.close()

            upgraded = create_app(
                {
                    "TESTING": True,
                    "APP_DATABASE_PATH": str(path),
                    "APP_TIMEZONE": "America/Sao_Paulo",
                }
            )
            with upgraded.app_context():
                connection = get_db()
                self.assertEqual(get_schema_version(), 5)
                task_row = connection.execute(
                    "SELECT title, grupo_id FROM tasks WHERE id = 3"
                ).fetchone()
                self.assertEqual((task_row["title"], task_row["grupo_id"]), ("Tarefa antiga", 2))
                self.assertEqual(
                    connection.execute(
                        "SELECT name FROM tags WHERE id = 1"
                    ).fetchone()[0],
                    "Work",
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT name FROM grupos WHERE id = 2"
                    ).fetchone()[0],
                    "Projeto antigo",
                )
                self.assertEqual(
                    connection.execute("PRAGMA foreign_key_check").fetchall(), []
                )

    def test_xp_for_each_kind_and_level_boundaries(self):
        expected = {
            "mensagem": 10,
            "resposta": 15,
            "conversa": 30,
            "proposta": 50,
            "piloto": 150,
            "nota": 0,
            "pausa": 0,
        }
        for kind, xp in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(xp_for(kind), xp)
        limits = (
            (0, "Aprendiz"),
            (99, "Aprendiz"),
            (100, "Piloto"),
            (299, "Piloto"),
            (300, "Timoneiro"),
            (699, "Timoneiro"),
            (700, "Capitão"),
            (2000, "Capitão"),
        )
        for xp, level in limits:
            with self.subTest(xp=xp):
                self.assertEqual(level_for(xp), level)

    def test_message_sets_sent_status_followup_and_updated_at(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            sent_at = local_noon()

            interaction = repository.log_interaction(
                lead.id, "mensagem", notes="Primeira abordagem", created_at=sent_at
            )

            updated = repository.get_lead(lead.id)
            expected_followup = sent_at.astimezone(TZ).date() + timedelta(days=3)
            self.assertEqual(interaction.kind, InteractionKind.MESSAGE)
            self.assertEqual(updated.status, LeadStatus.SENT)
            self.assertEqual(updated.next_action_at, expected_followup)
            self.assertEqual(updated.updated_at, sent_at.replace(microsecond=0))
            self.assertEqual(repository.xp_total(), 10)
            self.assertEqual(repository.level(), "Aprendiz")

    def test_status_transitions_valid_and_invalid(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            for status in (
                LeadStatus.TO_SEND,
                LeadStatus.SENT,
                LeadStatus.REPLIED,
                LeadStatus.CONVERSATION,
                LeadStatus.PROPOSAL,
                LeadStatus.PILOT,
                LeadStatus.WON,
            ):
                lead = repository.update_status(lead.id, status)
                self.assertEqual(lead.status, status)

            other = self.create_lead(handle="outro")
            with self.assertRaises(ValidationError):
                repository.update_status(other.id, LeadStatus.WON)

            paused = self.create_lead(handle="pausado")
            repository.update_status(paused.id, LeadStatus.TO_SEND)
            repository.update_status(paused.id, LeadStatus.SENT)
            self.assertEqual(
                repository.update_status(paused.id, LeadStatus.PAUSED).status,
                LeadStatus.PAUSED,
            )
            self.assertEqual(
                repository.update_status(paused.id, LeadStatus.SENT).status,
                LeadStatus.SENT,
            )
            self.assertEqual(
                repository.update_status(paused.id, LeadStatus.LOST).status,
                LeadStatus.LOST,
            )
            with self.assertRaises(ValidationError):
                repository.update_status(paused.id, LeadStatus.SENT)

    def test_channel_and_handle_are_unique(self):
        with self.app.app_context():
            repository = self.repository()
            self.create_lead()
            with self.assertRaises(ValidationError):
                self.create_lead()
            other_channel = self.create_lead(channel="linkedin")
            self.assertEqual(other_channel.channel, Channel.LINKEDIN)

    def test_update_lead_changes_fields_and_keeps_status_and_next_action(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            repository.update_status(lead.id, LeadStatus.TO_SEND)
            repository.update_status(lead.id, LeadStatus.SENT)
            followup = local_today() + timedelta(days=3)
            repository.set_next_action(lead.id, followup)
            before = repository.get_lead(lead.id)

            updated = repository.update_lead(
                lead.id,
                company="Clinica Sorriso Norte",
                contact="Dra. Ana Paula",
                sector="odontologia",
                city="Parnamirim",
                channel="instagram",
                handle="@sorrisonorte",
                observation="Posts sobre alinhadores",
            )

            self.assertEqual(updated.company, "Clinica Sorriso Norte")
            self.assertEqual(updated.contact, "Dra. Ana Paula")
            self.assertEqual(updated.city, "Parnamirim")
            self.assertEqual(updated.channel, Channel.INSTAGRAM)
            self.assertEqual(updated.handle, "@sorrisonorte")
            self.assertEqual(updated.observation, "Posts sobre alinhadores")
            self.assertEqual(updated.status, LeadStatus.SENT)
            self.assertEqual(updated.next_action_at, followup)
            self.assertEqual(updated.created_at, before.created_at)

    def test_update_lead_rejects_duplicates_and_invalid_data(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            other = self.create_lead(handle="outro")

            same = repository.update_lead(
                lead.id,
                company=lead.company,
                contact=lead.contact,
                sector=lead.sector,
                city=lead.city,
                channel=lead.channel,
                handle=lead.handle,
                observation=lead.observation,
            )
            self.assertEqual(same.id, lead.id)

            with self.assertRaises(ValidationError):
                repository.update_lead(
                    other.id,
                    company="Outra Clinica",
                    sector="odontologia",
                    city="Natal",
                    channel="whatsapp",
                    handle=lead.handle,
                    observation="Teste",
                )
            with self.assertRaises(ValidationError):
                repository.update_lead(
                    lead.id,
                    company=" ",
                    sector="odontologia",
                    city="Natal",
                    channel="whatsapp",
                    handle=lead.handle,
                    observation="Teste",
                )
            with self.assertRaises(LeadNotFoundError):
                repository.update_lead(
                    999,
                    company="Fantasma",
                    sector="odontologia",
                    city="Natal",
                    channel="whatsapp",
                    handle="123",
                    observation="Teste",
                )

    def test_streak_counts_consecutive_days_and_breaks(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            for days_ago in (0, 1, 2):
                repository.log_interaction(
                    lead.id, "mensagem", created_at=local_noon(days_ago)
                )
            self.assertEqual(repository.streak(), 3)

            with get_db() as connection:
                connection.execute("DELETE FROM interactions")
            broken = self.create_lead(handle="quebrado")
            for days_ago in (0, 2, 3):
                repository.log_interaction(
                    broken.id, "mensagem", created_at=local_noon(days_ago)
                )
            self.assertEqual(repository.streak(), 1)

    def test_weekly_progress_counts_messages_replies_and_conversations(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            now = local_noon()
            repository.log_interaction(lead.id, "mensagem", created_at=now)
            repository.log_interaction(lead.id, "resposta", created_at=now)
            repository.log_interaction(lead.id, "conversa", created_at=now)
            repository.log_interaction(lead.id, "nota", created_at=now)
            repository.log_interaction(
                lead.id, "mensagem", created_at=now - timedelta(days=14)
            )

            self.assertEqual(
                repository.weekly_progress(),
                {"messages": 1, "replies": 1, "conversations": 1},
            )

    def test_daily_mission_prioritizes_overdue_followup(self):
        with self.app.app_context():
            repository = self.repository()
            no_date = self.create_lead(handle="sem-data")
            repository.update_status(no_date.id, LeadStatus.TO_SEND)
            overdue = self.create_lead(handle="vencido")
            repository.update_status(overdue.id, LeadStatus.TO_SEND)
            repository.update_status(overdue.id, LeadStatus.SENT)
            repository.set_next_action(
                overdue.id, local_today() - timedelta(days=1)
            )
            future = self.create_lead(handle="futuro")
            repository.update_status(future.id, LeadStatus.TO_SEND)
            repository.update_status(future.id, LeadStatus.SENT)
            repository.set_next_action(future.id, local_today() + timedelta(days=2))

            mission = repository.daily_mission()

            self.assertIsNotNone(mission)
            self.assertEqual(mission.id, overdue.id)

    def test_followups_due_only_sent_and_past(self):
        with self.app.app_context():
            repository = self.repository()
            due = self.create_lead(handle="due")
            repository.update_status(due.id, LeadStatus.TO_SEND)
            repository.update_status(due.id, LeadStatus.SENT)
            repository.set_next_action(due.id, local_today() - timedelta(days=1))

            today = self.create_lead(handle="today")
            repository.update_status(today.id, LeadStatus.TO_SEND)
            repository.update_status(today.id, LeadStatus.SENT)
            repository.set_next_action(today.id, local_today())

            future = self.create_lead(handle="future")
            repository.update_status(future.id, LeadStatus.TO_SEND)
            repository.update_status(future.id, LeadStatus.SENT)
            repository.set_next_action(future.id, local_today() + timedelta(days=1))

            replied = self.create_lead(handle="replied")
            repository.update_status(replied.id, LeadStatus.TO_SEND)
            repository.update_status(replied.id, LeadStatus.SENT)
            repository.update_status(replied.id, LeadStatus.REPLIED)
            repository.set_next_action(replied.id, local_today() - timedelta(days=1))

            self.assertEqual([lead.id for lead in repository.followups_due()], [due.id])

    def test_badges_and_pipeline_counts(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            repository.log_interaction(lead.id, "mensagem", created_at=local_noon())
            repository.log_interaction(lead.id, "resposta", created_at=local_noon())
            repository.log_interaction(lead.id, "conversa", created_at=local_noon())
            repository.log_interaction(lead.id, "piloto", created_at=local_noon())

            badges = repository.badges()
            for badge in (
                "primeira_mensagem",
                "primeira_resposta",
                "primeira_conversa",
                "primeiro_piloto",
            ):
                self.assertIn(badge, badges)

            counts = repository.pipeline_counts()
            self.assertEqual(counts["enviado"], 1)
            self.assertEqual(sum(counts.values()), 1)
            self.assertEqual(set(counts), {status.value for status in LeadStatus})

    def test_four_week_streak_badge(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            current_week = datetime.now(TZ).date()
            current_week -= timedelta(days=current_week.weekday())
            for offset in range(4):
                week = current_week - timedelta(days=7 * offset)
                moment = datetime.combine(week, time(12), tzinfo=TZ).astimezone(
                    timezone.utc
                )
                repository.log_interaction(
                    lead.id, "mensagem", created_at=moment
                )

            self.assertIn("streak_4_semanas", repository.badges())

    def test_lead_and_interaction_validation(self):
        with self.app.app_context():
            repository = self.repository()
            with self.assertRaises(ValidationError):
                self.create_lead(company="   ")
            with self.assertRaises(ValidationError):
                self.create_lead(handle="x", observation="x" * 201)
            with self.assertRaises(ValidationError):
                self.create_lead(channel="telefone")
            with self.assertRaises(ValidationError):
                self.create_lead(next_action_at="31/10/2026")

            lead = self.create_lead(handle="valido")
            with self.assertRaises(ValidationError):
                repository.log_interaction(lead.id, "tipo-invalido")
            with self.assertRaises(ValidationError):
                repository.log_interaction(lead.id, "nota", channel="sistema-invalido")
            with self.assertRaises(LeadNotFoundError):
                repository.log_interaction(999, "nota")
            with self.assertRaises(LeadNotFoundError):
                repository.get_lead(999)

    def test_deleting_lead_cascades_interactions(self):
        with self.app.app_context():
            repository = self.repository()
            lead = self.create_lead()
            repository.log_interaction(lead.id, "nota")
            with get_db() as connection:
                connection.execute("DELETE FROM leads WHERE id = ?", (lead.id,))
            self.assertEqual(repository.list_interactions(), [])


if __name__ == "__main__":
    unittest.main()
