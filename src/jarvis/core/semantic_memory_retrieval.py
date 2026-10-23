
from typing import Any

from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.core.semantic_similarity import cosine_similarity


def select_semantically_relevant_memories(
    query: str,
    memories: list[dict[str, Any]],
    embedding_provider: OllamaEmbeddingProvider,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Rank memories using stored embeddings when available."""
    if not isinstance(query, str):
        raise TypeError("query must be a string.")

    if not query.strip():
        raise ValueError("query cannot be empty.")

    if not isinstance(memories, list):
        raise TypeError("memories must be a list.")

    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer.")

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    if not memories:
        return []

    # Embed the current query once.
    query_vector = embedding_provider.embed(query.strip())
    ranked_memories: list[dict[str, Any]] = []

    for memory in memories:
        if not isinstance(memory, dict):
            raise TypeError("Each memory must be a dictionary.")

        content = memory.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "Each memory must contain non-empty text."
            )

        memory_vector = memory.get("embedding")

        # Backward compatibility for memories without stored vectors.
        if memory_vector is None:
            memory_vector = embedding_provider.embed(content.strip())

        score = cosine_similarity(query_vector, memory_vector)

        ranked_memories.append({
            **memory,
            "similarity_score": score,
        })

    ranked_memories.sort(
        key=lambda memory: memory["similarity_score"],
        reverse=True,
    )

    return ranked_memories[:limit]
