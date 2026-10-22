
import unittest

from jarvis.database.connection import get_connection
from jarvis.database.conversation_repository import (
    add_message,
    create_conversation,
    get_messages,
    get_latest_conversation,
)


class TestConversationRepository(unittest.TestCase):
    def setUp(self):
        """Create an isolated conversation for each test."""
        self.conversation_id = create_conversation(
            "Automated repository test"
        )

    def tearDown(self):
        """Delete the test conversation and its messages."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM conversations WHERE id = %s;",
                (self.conversation_id,),
            )

    def test_save_and_retrieve_messages(self):
        add_message(
            self.conversation_id,
            "user",
            "Hello Jarvis",
        )
        add_message(
            self.conversation_id,
            "assistant",
            "Hello! How can I help?",
        )

        messages = get_messages(self.conversation_id)

        self.assertEqual(len(messages), 2)
        self.assertEqual(
            [message["role"] for message in messages],
            ["user", "assistant"],
        )
        self.assertEqual(
            messages[0]["content"],
            "Hello Jarvis",
        )
        self.assertEqual(
            messages[1]["content"],
            "Hello! How can I help?",
        )

    def test_empty_conversation_has_no_messages(self):
        messages = get_messages(self.conversation_id)

        self.assertEqual(messages, [])

    def test_invalid_role_is_rejected(self):
        with self.assertRaises(ValueError):
            add_message(
                self.conversation_id,
                "admin",
                "This role is invalid",
            )

    def test_empty_message_is_rejected(self):
        with self.assertRaises(ValueError):
            add_message(
                self.conversation_id,
                "user",
                "   ",
            )

    def test_messages_belong_to_the_correct_conversation(self):
        other_conversation_id = create_conversation(
            "Another automated test"
        )

        try:
            add_message(
                self.conversation_id,
                "user",
                "First conversation",
            )
            add_message(
                other_conversation_id,
                "user",
                "Second conversation",
            )

            messages = get_messages(self.conversation_id)

            self.assertEqual(len(messages), 1)
            self.assertEqual(
                messages[0]["content"],
                "First conversation",
            )
        finally:
            with get_connection() as connection:
                connection.execute(
                    "DELETE FROM conversations WHERE id = %s;",
                    (other_conversation_id,),
                )


    def test_latest_conversation_is_found(self):
        latest_id = create_conversation("Latest conversation")

        try:
            self.assertEqual(
                get_latest_conversation(),
                latest_id,
            )
        finally:
            with get_connection() as connection:
                connection.execute(
                    "DELETE FROM conversations WHERE id = %s;",
                    (latest_id,),
                )

    def test_saved_messages_can_be_reloaded(self):
        add_message(
            self.conversation_id,
            "user",
            "Remember this message",
        )

        # Simulate loading the conversation again from the database.
        restored_messages = get_messages(self.conversation_id)

        self.assertEqual(len(restored_messages), 1)
        self.assertEqual(
            restored_messages[0]["role"],
            "user",
        )
        self.assertEqual(
            restored_messages[0]["content"],
            "Remember this message",
        )



if __name__ == "__main__":
    unittest.main()
