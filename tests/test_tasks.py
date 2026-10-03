import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from app import create_app
from app.db import get_db
from app.tasks import (
    TaskRepository,
    TaskStatus,
    ValidationError,
    normalize_tags,
    today_in_timezone,
)


class TaskDomainTestCase(unittest.TestCase):
    def test_score_uses_all_ice_dimensions(self):
        task = self._task_without_database(1, 1, 1, 1)
        self.assertEqual(task.score, 1)
        self.assertEqual(self._task_without_database(2, 10, 10, 10).score, 1000)

    def test_ice_values_must_be_integers_between_one_and_ten(self):
        for value in (0, 11, True, 1.5, "5"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    self._task_without_database(1, value, 1, 1)

    def test_title_and_tags_are_normalized_and_validated(self):
        self.assertEqual(normalize_tags([" Work ", "work", "Study"]), ("Work", "Study"))

        with self.assertRaises(ValidationError):
            self._task_without_database(1, 1, 1, 1, title="   ")
        with self.assertRaises(ValidationError):
            self._task_without_database(1, 1, 1, 1, title="x" * 121)
        with self.assertRaises(ValidationError):
            normalize_tags(["x" * 31])

    def test_non_iterable_tags_are_rejected_as_validation_error(self):
        with self.assertRaises(ValidationError):
            normalize_tags(123)

    def test_tag_normalization_accepts_none_strings_and_iterables(self):
        self.assertEqual(normalize_tags(None), ())
        self.assertEqual(normalize_tags("work"), ("work",))
        self.assertEqual(normalize_tags(iter(("work", "study"))), ("work", "study"))

    def test_open_overdue_task_is_not_equivalent_to_completed_overdue_task(self):
        open_task = self._task_without_database(1, 1, 1, 1, deadline=date(2026, 9, 20))
        completed_task = self._task_without_database(
            2,
            1,
            1,
            1,
            deadline=date(2026, 9, 20),
            status=TaskStatus.COMPLETED,
        )
        today = date(2026, 9, 21)

        self.assertTrue(open_task.is_overdue(today))
        self.assertFalse(completed_task.is_overdue(today))
        self.assertFalse(open_task.is_overdue(date(2026, 9, 20)))

    @staticmethod
    def _task_without_database(task_id, impact, confidence, ease, **overrides):
        from app.tasks import Task

        values = {
            "id": task_id,
            "title": "Task",
            "impact": impact,
            "confidence": confidence,
            "ease": ease,
            "deadline": None,
            "status": TaskStatus.OPEN,
            "created_at": datetime.now(timezone.utc),
            "tags": (),
        }
        values.update(overrides)
        return Task(**values)


class TaskRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database_path = Path(self.directory.name) / "app.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )

    def tearDown(self):
        self.directory.cleanup()

    def repository(self):
        return TaskRepository(get_db(), "America/Sao_Paulo")

    def test_create_update_status_reopen_and_delete(self):
        with self.app.app_context():
            repository = self.repository()
            task = repository.create(
                "  Estudar Flask  ",
                8,
                9,
                7,
                "2026-09-30",
                ["Backend", "backend"],
            )
            self.assertEqual(task.title, "Estudar Flask")
            self.assertEqual(task.score, 504)
            self.assertEqual(task.tags, ("Backend",))

            updated = repository.update(
                task.id,
                impact=10,
                deadline=None,
                tags=["Python"],
            )
            self.assertEqual(updated.score, 630)
            self.assertIsNone(updated.deadline)
            self.assertEqual(updated.tags, ("Python",))

            completed = repository.complete(task.id)
            self.assertEqual(completed.status, TaskStatus.COMPLETED)
            reopened = repository.reopen(task.id)
            self.assertEqual(reopened.status, TaskStatus.OPEN)

            repository.delete(task.id)
            with self.assertRaises(LookupError):
                repository.get(task.id)

    def test_reusing_a_tag_does_not_create_duplicate_tag_rows(self):
        with self.app.app_context():
            repository = self.repository()
            repository.create("First", 1, 1, 1, tags=["Work"])
            repository.create("Second", 1, 1, 1, tags=[" work "])

            count = get_db().execute("SELECT COUNT(*) FROM tags").fetchone()[0]

            self.assertEqual(count, 1)

    def test_casefold_equivalent_tags_are_reused(self):
        with self.app.app_context():
            repository = self.repository()
            repository.create("First", 1, 1, 1, tags=["Straße"])
            second = repository.create("Second", 1, 1, 1, tags=["STRASSE"])

            count = get_db().execute("SELECT COUNT(*) FROM tags").fetchone()[0]

            self.assertEqual(count, 1)
            self.assertEqual(second.tags, ("Straße",))

    def test_filters_and_ordering_keep_default_list_open_and_prioritized(self):
        with self.app.app_context():
            repository = self.repository()
            today = today_in_timezone("America/Sao_Paulo")
            low = repository.create("Low", 1, 1, 1, today + date.resolution * 3, ["work"])
            high_without_deadline = repository.create("High", 10, 10, 10, None, ["home"])
            high_with_deadline = repository.create(
                "High with deadline", 10, 10, 10, today + date.resolution, ["work", "home"]
            )
            overdue = repository.create("Overdue", 2, 2, 2, today - date.resolution, ["work"])
            repository.complete(low.id)

            default_tasks = repository.list()
            self.assertEqual(
                [task.id for task in default_tasks],
                [high_with_deadline.id, high_without_deadline.id, overdue.id],
            )
            self.assertEqual(
                [task.id for task in repository.list(status=TaskStatus.COMPLETED)],
                [low.id],
            )
            self.assertEqual(
                [task.id for task in repository.list(overdue=True)],
                [overdue.id],
            )
            self.assertEqual(
                [task.id for task in repository.list(tags=["WORK", "home"])],
                [high_with_deadline.id],
            )
            self.assertEqual(
                [task.id for task in repository.list(order_by="deadline")],
                [overdue.id, high_with_deadline.id, high_without_deadline.id],
            )

    def test_data_is_available_after_new_application_instance(self):
        with self.app.app_context():
            repository = self.repository()
            created = repository.create("Persistir", 5, 6, 7, tags=["saved"])
            database_path = self.app.config["APP_DATABASE_PATH"]

        second_app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": database_path,
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )
        with second_app.app_context():
            task = TaskRepository(get_db()).get(created.id)
            self.assertEqual(task.score, 210)
            self.assertEqual(task.tags, ("saved",))


if __name__ == "__main__":
    unittest.main()

class TagManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database_path = Path(self.directory.name) / "app.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "APP_DATABASE_PATH": str(database_path),
                "APP_TIMEZONE": "America/Sao_Paulo",
            }
        )

    def tearDown(self):
        self.directory.cleanup()

    def repository(self):
        with self.app.app_context():
            yield TaskRepository(get_db(), "America/Sao_Paulo")

    def test_delete_tag_in_use_detaches_without_deleting_tasks(self):
        with self.app.app_context():
            repository = TaskRepository(get_db(), "America/Sao_Paulo")
            task = repository.create("Precisa manter", 5, 5, 5, tags=["Work"])
            first_tag = repository.list_tags_with_usage()[0]

            repository.delete_tag(first_tag["id"])

            self.assertEqual(repository.get(task.id).tags, ())
            self.assertEqual(repository.list_tags_with_usage(), [])

    def test_rename_tag_persists_new_name(self):
        with self.app.app_context():
            repository = TaskRepository(get_db(), "America/Sao_Paulo")
            task = repository.create("Com tag", 5, 5, 5, tags=["Old"])
            tags = repository.list_tags_with_usage()

            renamed = repository.rename_tag(tags[0]["id"], "  New  ")

            self.assertEqual(renamed, "New")
            self.assertEqual(repository.get(task.id).tags, ("New",))

    def test_merge_tags_moves_tasks_to_target(self):
        with self.app.app_context():
            repository = TaskRepository(get_db(), "America/Sao_Paulo")
            task = repository.create("Com mescla", 5, 5, 5, tags=["Alpha"])
            repository.create("Ancora", 1, 1, 1, tags=["Beta"])
            usage = {
                entry["name"]: entry["id"]
                for entry in repository.list_tags_with_usage()
            }

            target = repository.merge_tags(usage["Alpha"], usage["Beta"])

            self.assertEqual(target, "Beta")
            self.assertEqual(repository.get(task.id).tags, ("Beta",))
            self.assertEqual(len(repository.list_tags_with_usage()), 1)
