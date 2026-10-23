
from datetime import datetime
from uuid import UUID

from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.database.memory_repository import save_approved_memory


def save_memory_with_approval(
    content: str,
    approved: bool,
    source_conversation_id: UUID | None = None,
    expires_at: datetime | None = None,
    embedding_provider: OllamaEmbeddingProvider | None = None,
) -> UUID | None:
    """Save a memory only after approval, optionally storing its embedding."""
    if not isinstance(approved, bool):
        raise TypeError("approved must be a boolean.")

    if not approved:
        return None

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Memory content cannot be empty.")

    # Preserve the original behavior when no embedding provider is supplied.
    if embedding_provider is None:
        return save_approved_memory(
            content=content,
            source_conversation_id=source_conversation_id,
            expires_at=expires_at,
        )

    # Generate the embedding only after approval.
    embedding = embedding_provider.embed(content.strip())

    return save_approved_memory(
        content=content,
        source_conversation_id=source_conversation_id,
        expires_at=expires_at,
        embedding=embedding,
    )
