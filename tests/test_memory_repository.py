
import unittest
from datetime import datetime
from uuid import UUID

from jarvis.database.memory_repository import (
    delete_memory,
    get_active_memories,
    save_approved_memory,
)


class TestMemoryRepository(unittest.TestCase):
    def test_save_retrieve_and_delete_memory(self):
        content = "Automated memory repository test"

        memory_id = save_approved_memory(content)

        try:
            self.assertIsInstance(memory_id, UUID)

            memories = get_active_memories()
            saved_memory = next(
                (
                    memory
                    for memory in memories
                    if memory["id"] == memory_id
                ),
                None,
            )

            self.assertIsNotNone(saved_memory)
            self.assertEqual(saved_memory["content"], content)

            self.assertTrue(delete_memory(memory_id))
            self.assertFalse(delete_memory(memory_id))

        finally:
            # Ensure test data is removed even if an assertion fails.
            delete_memory(memory_id)

    def test_empty_content_is_rejected(self):
        with self.assertRaises(ValueError):
            save_approved_memory("   ")

    def test_expiry_requires_timezone_information(self):
        naive_datetime = datetime(2030, 1, 1, 12, 0, 0)

        with self.assertRaises(ValueError):
            save_approved_memory(
                "Temporary test memory",
                expires_at=naive_datetime,
            )


if __name__ == "__main__":
    unittest.main()
