
import unittest

import psycopg

from jarvis.config.settings import load_settings


class TestDatabaseConnection(unittest.TestCase):
    def test_connect_to_jarvis_database(self):
        settings = load_settings()

        self.assertTrue(
            settings.database_url,
            "DATABASE_URL is missing. Check your local .env file.",
        )

        with psycopg.connect(
            settings.database_url,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT current_user, current_database();"
                )
                current_user, current_database = cursor.fetchone()

        self.assertEqual(current_user, "jarvis_app")
        self.assertEqual(current_database, "jarvis")


if __name__ == "__main__":
    unittest.main()
