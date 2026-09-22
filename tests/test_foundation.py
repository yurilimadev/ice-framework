import tempfile
import unittest
from pathlib import Path

from app import create_app


class FoundationTestCase(unittest.TestCase):
    def create_test_app(self, database_path, **overrides):
        config = {
            "TESTING": True,
            "APP_DATABASE_PATH": str(database_path),
        }
        config.update(overrides)
        return create_app(config)

    def test_health_reports_database_and_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "nested" / "app.sqlite3"
            app = self.create_test_app(database_path)

            response = app.test_client().get("/health")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.get_json(),
                {"database": "ok", "schema_version": 1, "status": "ok"},
            )
            self.assertTrue(database_path.is_file())

    def test_initialization_is_idempotent_for_existing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "app.sqlite3"

            first_app = self.create_test_app(database_path)
            second_app = self.create_test_app(database_path)

            self.assertEqual(first_app.test_client().get("/health").status_code, 200)
            self.assertEqual(second_app.test_client().get("/health").status_code, 200)

    def test_invalid_timezone_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "app.sqlite3"

            with self.assertRaisesRegex(RuntimeError, "Fuso horario invalido"):
                self.create_test_app(
                    database_path,
                    APP_TIMEZONE="Invalid/Timezone",
                )


if __name__ == "__main__":
    unittest.main()
