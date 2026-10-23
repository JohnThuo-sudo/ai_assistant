
import unittest

from jarvis.core.memory_retrieval import select_relevant_memories


class TestSelectRelevantMemories(unittest.TestCase):
    def setUp(self):
        self.memories = [
            {
                "content": "My favorite programming language is Python"
            },
            {
                "content": "I am learning PostgreSQL database design"
            },
            {
                "content": "I prefer dark themes in applications"
            },
        ]

    def test_most_relevant_memory_ranks_first(self):
        results = select_relevant_memories(
            "What is my favorite programming language?",
            self.memories,
        )

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(
            results[0]["content"],
            "My favorite programming language is Python",
        )

    def test_irrelevant_memories_are_excluded(self):
        results = select_relevant_memories(
            "PostgreSQL database design",
            self.memories,
        )

        contents = [memory["content"] for memory in results]

        self.assertIn(
            "I am learning PostgreSQL database design",
            contents,
        )
        self.assertNotIn(
            "I prefer dark themes in applications",
            contents,
        )

    def test_result_limit_is_respected(self):
        results = select_relevant_memories(
            "Python PostgreSQL applications",
            self.memories,
            limit=1,
        )

        self.assertLessEqual(len(results), 1)

    def test_query_without_meaningful_keywords_returns_empty(self):
        results = select_relevant_memories(
            "what is it",
            self.memories,
        )

        self.assertEqual(results, [])

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            select_relevant_memories(
                "Python",
                self.memories,
                limit=0,
            )

    def test_boolean_limit_is_rejected(self):
        with self.assertRaises(TypeError):
            select_relevant_memories(
                "Python",
                self.memories,
                limit=True,
            )

    def test_invalid_query_type_is_rejected(self):
        with self.assertRaises(TypeError):
            select_relevant_memories(
                None,
                self.memories,
            )

    def test_retrieval_statistics_are_correct(self):
        from jarvis.core.memory_retrieval import (
            retrieve_relevant_memories,
        )

        result = retrieve_relevant_memories(
            "Python programming",
            self.memories,
            limit=5,
        )

        self.assertEqual(result.total_available, 3)
        self.assertEqual(result.total_matched, 1)
        self.assertEqual(len(result.memories), 1)

    def test_retrieval_limit_is_respected(self):
        from jarvis.core.memory_retrieval import (
            retrieve_relevant_memories,
        )

        result = retrieve_relevant_memories(
            "Python PostgreSQL database applications themes",
            self.memories,
            limit=1,
        )

        self.assertEqual(len(result.memories), 1)

    def test_invalid_retrieval_limit_is_rejected(self):
        from jarvis.core.memory_retrieval import (
            retrieve_relevant_memories,
        )

        with self.assertRaises(ValueError):
            retrieve_relevant_memories(
                "Python",
                self.memories,
                limit=0,
            )

    def test_boolean_retrieval_limit_is_rejected(self):
        from jarvis.core.memory_retrieval import (
            retrieve_relevant_memories,
        )

        with self.assertRaises(TypeError):
            retrieve_relevant_memories(
                "Python",
                self.memories,
                limit=True,
            )

if __name__ == "__main__":
    unittest.main()
