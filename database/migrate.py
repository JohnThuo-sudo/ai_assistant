
from pathlib import Path

import psycopg

from jarvis.config.settings import load_settings


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def main() -> None:
    """Apply database migrations that have not run yet."""
    settings = load_settings()

    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Check your local .env file."
        )

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    with psycopg.connect(settings.database_url) as connection:
        # Create a table that tracks successfully applied migrations.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    migration_name TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        connection.commit()

        if not migration_files:
            print("No migration files found.")
            return

        for migration_file in migration_files:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT 1
                        FROM schema_migrations
                        WHERE migration_name = %s;
                        """,
                        (migration_file.name,),
                    )

                    if cursor.fetchone():
                        print(f"Skipped: {migration_file.name}")
                        continue

                    migration_sql = migration_file.read_text(
                        encoding="utf-8"
                    )

                    cursor.execute(migration_sql)

                    cursor.execute(
                        """
                        INSERT INTO schema_migrations (migration_name)
                        VALUES (%s);
                        """,
                        (migration_file.name,),
                    )

                print(f"Applied: {migration_file.name}")

    print("Database migrations completed.")


if __name__ == "__main__":
    main()
