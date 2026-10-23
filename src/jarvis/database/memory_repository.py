
from datetime import datetime
from math import isfinite
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb

from jarvis.database.connection import get_connection


def save_approved_memory(
    content: str,
    source_conversation_id: UUID | None = None,
    expires_at: datetime | None = None,
    embedding: list[float] | None = None,
) -> UUID:
    """Save an approved memory and its optional embedding."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Memory content cannot be empty.")

    if expires_at is not None and expires_at.tzinfo is None:
        raise ValueError(
            "expires_at must include timezone information."
        )

    if embedding is not None:
        if not isinstance(embedding, list) or not embedding:
            raise ValueError(
                "Embedding must be a non-empty list of numbers."
            )

        for value in embedding:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError(
                    "Embedding values must be finite numbers."
                )

    with get_connection() as connection:
        if embedding is None:
            row = connection.execute(
                """
                INSERT INTO memories (
                    content,
                    source_conversation_id,
                    expires_at
                )
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    content.strip(),
                    source_conversation_id,
                    expires_at,
                ),
            ).fetchone()
        else:
            row = connection.execute(
                """
                INSERT INTO memories (
                    content,
                    source_conversation_id,
                    expires_at,
                    embedding
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    content.strip(),
                    source_conversation_id,
                    expires_at,
                    Jsonb(embedding),
                ),
            ).fetchone()

    return row[0]


def get_active_memories() -> list[dict[str, Any]]:
    """Return unexpired memories, including stored embeddings."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, content, source_conversation_id,
                   created_at, expires_at, embedding
            FROM memories
            WHERE expires_at IS NULL
               OR expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC, id;
            """
        ).fetchall()

    return [
        {
            "id": row[0],
            "content": row[1],
            "source_conversation_id": row[2],
            "created_at": row[3],
            "expires_at": row[4],
            # The fallback also supports older mocked test rows.
            "embedding": row[5] if len(row) > 5 else None,
        }
        for row in rows
    ]


def delete_memory(memory_id: UUID) -> bool:
    """Delete a memory; return True if a row was deleted."""
    with get_connection() as connection:
        row = connection.execute(
            """
            DELETE FROM memories
            WHERE id = %s
            RETURNING id;
            """,
            (memory_id,),
        ).fetchone()

    return row is not None
