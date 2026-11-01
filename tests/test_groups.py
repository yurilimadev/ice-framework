import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app import create_app
from app.db import get_db, get_schema_version
from app.tasks import (
    GroupKind,
    GroupNotFoundError,
    GroupRepository,
    GroupStatus,
    TaskRepository,
    ValidationError,
)


class GroupRepositoryTestCase(unittest.TestCase):
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

    def groups(self):
        return GroupRepository(get_db())

    def tasks(self):
        return TaskRepository(get_db(), "America/Sao_Paulo")

    def test_create_rename_archive_and_list_groups(self):
        with self.app.app_context():
            groups = self.groups()
            project = groups.create("  Estudos  ", "projeto")
            area = groups.create("Saude", GroupKind.AREA)

            self.assertEqual(project.name, "Estudos")
            self.assertEqual(project.kind, GroupKind.PROJECT)
            self.assertEqual(project.status, GroupStatus.ACTIVE)
            self.assertEqual(area.kind, GroupKind.AREA)

            renamed = groups.rename(project.id, "Aprendizado")
            self.assertEqual(renamed.name, "Aprendizado")
            self.assertEqual(groups.get(project.id).name, "Aprendizado")

            archived = groups.archive(area.id)
            self.assertEqual(archived.status, GroupStatus.ARCHIVED)
            self.assertEqual(
                [group.id for group in groups.list(status=GroupStatus.ACTIVE)],
                [project.id],
            )
            self.assertEqual(
                [group.id for group in groups.list(status="archived")],
                [area.id],
            )
            self.assertEqual(len(groups.list()), 2)

    def test_group_name_and_kind_are_validated(self):
        with self.app.app_context():
            groups = self.groups()
            for name in ("", "   ", "x" * 31, 123):
                with self.subTest(name=name):
                    with self.assertRaises(ValidationError):
                        groups.create(name, "projeto")

            for kind in ("tema", "", None):
                with self.subTest(kind=kind):
                    with self.assertRaises(ValidationError):
                        groups.create("Valido", kind)

    def test_delete_group_detaches_tasks_without_deleting_tasks_or_tags(self):
        with self.app.app_context():
            groups = self.groups()
            tasks = self.tasks()
            group = groups.create("Temporario", "area")
            task = tasks.create("Com grupo", 5, 5, 5, tags=["Work"], grupo_id=group.id)

            groups.delete(group.id)

            detached = tasks.get(task.id)
            self.assertIsNone(detached.grupo_id)
            self.assertEqual(detached.tags, ("Work",))
            with self.assertRaises(GroupNotFoundError):
                groups.get(group.id)

    def test_task_can_be_linked_and_unlinked_from_a_group(self):
        with self.app.app_context():
            groups = self.groups()
            tasks = self.tasks()
            first = groups.create("Projeto A", "projeto")
            second = groups.create("Area B", "area")

            task = tasks.create("Solto", 1, 1, 1)
            self.assertIsNone(task.grupo_id)

            linked = tasks.set_group(task.id, first.id)
            self.assertEqual(linked.grupo_id, first.id)

            updated = tasks.update(task.id, grupo_id=second.id)
            self.assertEqual(updated.grupo_id, second.id)

            untouched = tasks.update(task.id, title="Solto editado")
            self.assertEqual(untouched.grupo_id, second.id)

            cleared = tasks.clear_group(task.id)
            self.assertIsNone(cleared.grupo_id)

            with self.assertRaises(GroupNotFoundError):
                tasks.set_group(task.id, 999)
            with self.assertRaises(GroupNotFoundError):
                tasks.create("Grupo invalido", 1, 1, 1, grupo_id=999)

    def test_archiving_group_keeps_task_link(self):
        with self.app.app_context():
            groups = self.groups()
            tasks = self.tasks()
            group = groups.create("Arquivavel", "area")
            task = tasks.create("Vinculada", 3, 3, 3, grupo_id=group.id)

            groups.archive(group.id)

            self.assertEqual(tasks.get(task.id).grupo_id, group.id)
            self.assertEqual(groups.get(group.id).status, GroupStatus.ARCHIVED)

    def test_group_link_persists_after_new_application_instance(self):
        with self.app.app_context():
            group = self.groups().create("Persistente", "projeto")
            task = self.tasks().create("Vinculada", 2, 3, 4, grupo_id=group.id)

        second_app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(self.database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        with second_app.app_context():
            restored = TaskRepository(get_db()).get(task.id)
            self.assertEqual(restored.grupo_id, group.id)
            self.assertEqual(GroupRepository(get_db()).get(group.id).name, "Persistente")

    def test_upgrade_from_schema_2_preserves_tasks_and_adds_groups(self):
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        with tempfile.TemporaryDirectory() as upgrade_directory:
            upgrade_path = Path(upgrade_directory) / "app.sqlite3"
            connection = sqlite3.connect(upgrade_path)
            try:
                connection.executescript((migrations / "001_foundation.sql").read_text())
                connection.executescript((migrations / "002_tasks.sql").read_text())
                connection.execute(
                    """
                    INSERT INTO tasks
                        (title, impact, confidence, ease, deadline, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "Tarefa antiga",
                        2,
                        3,
                        4,
                        None,
                        "open",
                        datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            upgraded_app = create_app(
                {
                    "TESTING": True,
                    "APP_DATABASE_PATH": str(upgrade_path),
                    "APP_TIMEZONE": "America/Sao_Paulo",
                }
            )
            with upgraded_app.app_context():
                self.assertEqual(get_schema_version(), 4)
                task = TaskRepository(get_db()).get(1)
                self.assertEqual(task.title, "Tarefa antiga")
                self.assertIsNone(task.grupo_id)

                group = GroupRepository(get_db()).create("Novo", "projeto")
                linked = TaskRepository(get_db()).set_group(task.id, group.id)
                self.assertEqual(linked.grupo_id, group.id)

    def test_upgrade_from_schema_3_to_4_preserves_groups_and_links(self):
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        with tempfile.TemporaryDirectory() as upgrade_directory:
            upgrade_path = Path(upgrade_directory) / "app.sqlite3"
            connection = sqlite3.connect(upgrade_path)
            try:
                for migration in (
                    "001_foundation.sql",
                    "002_tasks.sql",
                    "003_grupos.sql",
                ):
                    connection.executescript((migrations / migration).read_text())
                created_at = datetime.now(timezone.utc).replace(
                    microsecond=0
                ).isoformat()
                connection.execute(
                    """
                    INSERT INTO grupos (id, name, kind, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (7, "Area antiga", "area", "archived", created_at),
                )
                connection.execute(
                    """
                    INSERT INTO tasks
                        (id, title, impact, confidence, ease, deadline, status,
                         created_at, grupo_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (11, "Vinculada antiga", 2, 3, 4, None, "open", created_at, 7),
                )
                connection.commit()
            finally:
                connection.close()

            upgraded_app = create_app(
                {
                    "TESTING": True,
                    "APP_DATABASE_PATH": str(upgrade_path),
                    "APP_TIMEZONE": "America/Sao_Paulo",
                }
            )
            with upgraded_app.app_context():
                self.assertEqual(get_schema_version(), 4)
                groups = GroupRepository(get_db())
                tasks = TaskRepository(get_db())
                old_group = groups.get(7)
                self.assertEqual(old_group.name, "Area antiga")
                self.assertEqual(old_group.kind, GroupKind.AREA)
                self.assertEqual(old_group.status, GroupStatus.ARCHIVED)
                self.assertEqual(tasks.get(11).grupo_id, 7)

                resource = groups.create("Referencias", "recurso")
                self.assertEqual(resource.kind, GroupKind.RESOURCE)
                linked = tasks.set_group(11, resource.id)
                self.assertEqual(linked.grupo_id, resource.id)
                self.assertEqual(
                    get_db().execute("PRAGMA foreign_key_check").fetchall(), []
                )

    def test_resource_group_aggregates_tasks(self):
        with self.app.app_context():
            groups = self.groups()
            tasks = self.tasks()
            resource = groups.create("Referencias", GroupKind.RESOURCE)
            task = tasks.create("Ler material", 3, 4, 5, grupo_id=resource.id)

            self.assertEqual(resource.kind, GroupKind.RESOURCE)
            self.assertEqual(tasks.get(task.id).grupo_id, resource.id)
            self.assertEqual(
                [item.id for item in groups.list(status=GroupStatus.ACTIVE)],
                [resource.id],
            )


if __name__ == "__main__":
    unittest.main()
