
import re
from typing import Any

from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryRetrievalResult:
    """Summary of a memory retrieval operation."""

    total_available: int
    total_matched: int
    memories: list[dict[str, Any]]


STOP_WORDS = {
    "the", "and", "for", "are", "was", "were", "what", "when",
    "where", "which", "who", "why", "how", "does", "did", "can",
    "could", "would", "should", "have", "has", "had", "with",
    "from", "into", "about", "that", "this", "these", "those",
    "you", "your", "yours", "my", "mine", "our", "ours", "their",
    "them", "they", "his", "her", "its", "not", "but", "also",
    "tell", "please", "remember", "recall", "know", "is", "am",
    "be", "to", "of", "in", "on", "at", "it", "i", "me", "a",
    "an", "do", "as", "or", "if", "so", "we", "he", "she",
}


def _extract_keywords(text: str) -> set[str]:
    """Extract meaningful lowercase words from text."""
    words = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())

    return {
        word
        for word in words
        if len(word) >= 2 and word not in STOP_WORDS
    }


def select_relevant_memories(
    query: str,
    memories: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Rank memories by keyword overlap with a user's query."""
    if not isinstance(query, str):
        raise TypeError("query must be a string.")

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer.")

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    query_keywords = _extract_keywords(query)

    if not query_keywords:
        return []

    ranked_memories: list[tuple[int, int, dict[str, Any]]] = []

    for index, memory in enumerate(memories):
        if not isinstance(memory, dict):
            raise TypeError("Each memory must be a dictionary.")

        content = memory.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "Each memory must contain non-empty text."
            )

        memory_keywords = _extract_keywords(content)
        overlap = query_keywords & memory_keywords

        if overlap:
            ranked_memories.append(
                (len(overlap), index, memory)
            )

    ranked_memories.sort(
        key=lambda item: (-item[0], item[1])
    )

    return [
        memory
        for _, _, memory in ranked_memories[:limit]
    ]

def retrieve_relevant_memories(
        query: str,
        memories: list[dict[str, Any]],
        limit: int=5,
) -> MemoryRetrievalResult:
    """Retrieve relevant memories and report retrieval statistics."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer")

    if limit < 1:
        raise ValueError("limit must be at least 1.")
    
    matched_memories = select_relevant_memories(
        query=query,
        memories=memories,
        limit=max(len(memories), 1),
    )

    selected_memories = matched_memories[:limit]

    return MemoryRetrievalResult(
        total_available=len(memories),
        total_matched=len(matched_memories),
        memories=selected_memories
    )