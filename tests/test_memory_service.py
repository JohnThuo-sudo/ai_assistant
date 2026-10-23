
import unittest
from unittest.mock import patch
from uuid import uuid4

from jarvis.database.memory_service import save_memory_with_approval


class TestMemoryService(unittest.TestCase):
    @patch("jarvis.database.memory_service.save_approved_memory")
    def test_unapproved_memory_is_not_saved(self, mock_save):
        result = save_memory_with_approval(
            content="My favorite language is Python",
            approved=False,
        )

        self.assertIsNone(result)
        mock_save.assert_not_called()

    @patch("jarvis.database.memory_service.save_approved_memory")
    def test_approved_memory_is_saved(self, mock_save):
        expected_id = uuid4()
        mock_save.return_value = expected_id

        result = save_memory_with_approval(
            content="My favorite language is Python",
            approved=True,
        )

        self.assertEqual(result, expected_id)
        mock_save.assert_called_once_with(
            content="My favorite language is Python",
            source_conversation_id=None,
            expires_at=None,
        )

    def test_approval_must_be_a_boolean(self):
        with self.assertRaises(TypeError):
            save_memory_with_approval(
                content="My favorite language is Python",
                approved="yes",
            )


if __name__ == "__main__":
    unittest.main()
