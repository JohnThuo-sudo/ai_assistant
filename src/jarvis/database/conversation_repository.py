
from typing import Any
from uuid import UUID

from jarvis.database.connection import get_connection


VALID_ROLES = {"system", "user", "assistant"}


def create_conversation(title: str | None = None) -> UUID:
    """Create a conversation and return its unique ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO conversations (title)
            VALUES (%s)
            RETURNING id;
            """,
            (title,),
        ).fetchone()

    return row[0]


def add_message(
    conversation_id: UUID,
    role: str,
    content: str,
) -> UUID:
    """Save a message and return its unique ID."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid message role: {role}")

    if not content.strip():
        raise ValueError("Message content cannot be empty.")

    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (conversation_id, role, content),
        ).fetchone()

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """,
            (conversation_id,),
        )

    return row[0]


def get_messages(conversation_id: UUID) -> list[dict[str, Any]]:
    """Retrieve a conversation's messages in chronological order."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at, id;
            """,
            (conversation_id,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "conversation_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def get_latest_conversation() -> UUID | None:
    """Return the most recently updated conversation ID, if one exists."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM conversations
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1;
            """
        ).fetchone()

    return row[0] if row else None
