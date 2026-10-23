
from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.config.settings import load_settings
from jarvis.database.connection import get_connection
from psycopg.types.json import Jsonb


def main() -> None:
    settings = load_settings()
    embedding_provider = OllamaEmbeddingProvider(settings)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, content
            FROM memories
            WHERE embedding IS NULL
            ORDER BY created_at, id;
            """
        ).fetchall()

        print(f"Memories requiring embeddings: {len(rows)}")

        updated = 0

        for memory_id, content in rows:
            embedding = embedding_provider.embed(content)

            connection.execute(
                """
                UPDATE memories
                SET embedding = %s
                WHERE id = %s
                  AND embedding IS NULL;
                """,
                (Jsonb(embedding), memory_id),
            )

            updated += 1
            print(f"Embedded memory {memory_id}")

    print(f"Backfill complete. Memories processed: {updated}")


if __name__ == "__main__":
    main()
