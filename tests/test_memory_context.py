
import json
import unittest

from jarvis.core.memory_context import build_memory_context


class TestBuildMemoryContext(unittest.TestCase):
    def test_no_memories_returns_none(self):
        result = build_memory_context([])

        self.assertIsNone(result)

    def test_memory_is_included_in_context(self):
        result = build_memory_context([
            {"content": "My favorite programming language is Python"}
        ])

        self.assertIsNotNone(result)
        self.assertIn(
            "My favorite programming language is Python",
            result,
        )
        self.assertIn("user-approved long-term memories", result)

    def test_multiple_memories_are_preserved(self):
        memories = [
            {"content": "My favorite language is Python"},
            {"content": "I am learning PostgreSQL"},
        ]

        result = build_memory_context(memories)

        self.assertIsNotNone(result)

        json_section = result.split(
            "Approved memories, encoded as a JSON array of strings:\n",
            maxsplit=1,
        )[1]

        decoded_memories = json.loads(json_section)

        self.assertEqual(
            decoded_memories,
            [
                "My favorite language is Python",
                "I am learning PostgreSQL",
            ],
        )

    def test_blank_memory_is_rejected(self):
        with self.assertRaises(ValueError):
            build_memory_context([{"content": "   "}])

    def test_invalid_memory_type_is_rejected(self):
        with self.assertRaises(TypeError):
            build_memory_context(["not a memory dictionary"])


if __name__ == "__main__":
    unittest.main()
