
import unittest
from unittest.mock import Mock

from jarvis.core.semantic_memory_retrieval import (
    select_semantically_relevant_memories,
)


class TestSemanticMemoryRetrieval(unittest.TestCase):
    def setUp(self):
        self.provider = Mock()

        self.memories = [
            {"id": "1", "content": "I enjoy Python programming."},
            {"id": "2", "content": "I enjoy playing football."},
            {"id": "3", "content": "I use PostgreSQL for databases."},
        ]

        # The first vector represents the query.
        # Each subsequent vector represents a memory.
        self.provider.embed.side_effect = [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
            [0.7, 0.7],
        ]

    def test_relevant_memory_ranks_first(self):
        results = select_semantically_relevant_memories(
            query="Which programming language do I enjoy?",
            memories=self.memories,
            embedding_provider=self.provider,
        )

        self.assertEqual(results[0]["id"], "1")
        self.assertGreater(
            results[0]["similarity_score"],
            results[1]["similarity_score"],
        )

    def test_results_respect_limit(self):
        results = select_semantically_relevant_memories(
            query="Tell me about my interests.",
            memories=self.memories,
            embedding_provider=self.provider,
            limit=2,
        )

        self.assertEqual(len(results), 2)

    def test_similarity_score_is_included(self):
        results = select_semantically_relevant_memories(
            query="Tell me about Python.",
            memories=self.memories,
            embedding_provider=self.provider,
        )

        for memory in results:
            self.assertIn("similarity_score", memory)

    def test_empty_memories_return_empty_list(self):
        results = select_semantically_relevant_memories(
            query="Tell me about Python.",
            memories=[],
            embedding_provider=self.provider,
        )

        self.assertEqual(results, [])
        self.provider.embed.assert_not_called()

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            select_semantically_relevant_memories(
                query=" ",
                memories=self.memories,
                embedding_provider=self.provider,
            )

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            select_semantically_relevant_memories(
                query="Tell me about Python.",
                memories=self.memories,
                embedding_provider=self.provider,
                limit=0,
            )

    def test_invalid_memory_is_rejected(self):
        with self.assertRaises(ValueError):
            select_semantically_relevant_memories(
                query="Tell me about Python.",
                memories=[{"id": "1", "content": " "}],
                embedding_provider=self.provider,
            )

    def test_non_dictionary_memory_is_rejected(self):
        with self.assertRaises(TypeError):
            select_semantically_relevant_memories(
                query="Tell me about Python.",
                memories=["not a memory"],
                embedding_provider=self.provider,
            )


    def test_stored_embeddings_are_reused(self):
        memories = [
            {
                "id": "1",
                "content": "I enjoy Python programming.",
                "embedding": [0.9, 0.1],
            },
            {
                "id": "2",
                "content": "I enjoy playing football.",
                "embedding": [0.0, 1.0],
            },
        ]

        self.provider.embed.return_value = [1.0, 0.0]

        results = select_semantically_relevant_memories(
            query="Which programming language do I enjoy?",
            memories=memories,
            embedding_provider=self.provider,
        )

        self.assertEqual(results[0]["id"], "1")
        self.assertEqual(len(results), 2)

        # Only the query should be embedded.
        self.provider.embed.assert_called_once_with(
            "Which programming language do I enjoy?"
        )


if __name__ == "__main__":
    unittest.main()
