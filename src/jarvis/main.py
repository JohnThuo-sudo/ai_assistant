import logging

import psycopg

from jarvis.ai.ollama_provider import OllamaProvider
from jarvis.config.settings import load_settings
from jarvis.core.logging_config import configure_logging
from jarvis.database.conversation_repository import (
    add_message,
    create_conversation,
    get_latest_conversation,
    get_messages
)

def main() -> None:
    """Start Jarvis with PostgreSQL-backed conversation history."""
    settings = load_settings()

    configure_logging(settings.log_level)
    logger = logging.getLogger("jarvis")

    print("=" * 42)
    print(f"{settings.app_name} - Personal AI Assistant")
    print("=" * 42)
    print(f"AI provider: Ollama")
    print(f"Model:  {settings.ollama_model}")
    print(f"API address: {settings.ollama_base_url}")
    print("Memory: PostgreSQL")
    print()

    provider = OllamaProvider(settings)

    print("Checking connection to Ollama...")


    if not provider.check_connection():
        print("Jarvis could not connect to Ollama.")
        print("Make sure Ollama is running and try again.")
        logger.error("Startup stopped because Ollama is unavailable")
        return

    print("Ollama is connected.")

    # Find the latest conversation or create the first one.
    try:
        conversation_id = get_latest_conversation()

        if conversation_id is None:
            conversation_id = create_conversation("Jarvis conversation")
            messages: list[dict[str, str]] = []
            print("Started a new conversation.")
        else:
            stored_messages = get_messages(conversation_id)
            messages = [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in stored_messages
            ]
            print(
                f"Resumed conversation with "
                f"{len(messages)} saved messages."
            )

    except (psycopg.Error, RuntimeError):
        logger.exception("Could not initialize conversation storage.")
        print("Jarvis could not access its conversation database.")
        print("Check PostgreSQL and your DATABASE_URL configuration.")
        return

    print("Jarvis is ready! Type 'exit' or 'quit' to stop.")
    print("Type 'clear' to clear the conversation history.")


    logger.info("Jarvis application initialized")

    while True:
        try:
            user_message = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nJarvis: Goodbye!")
            break

        if not user_message:
            continue

        command = user_message.lower()

        if command in {"exit", "quit"}:
            print("Jarvis: Goodbye!")
            break

        if command == "clear":
            try:
                conversation_id = create_conversation(
                    "Jarvis conversation"
                )
                messages.clear()
                print("Jarvis: Started a new conversation.")
            except (psycopg.Error, RuntimeError):
                logger.exception("Could not start a new conversation.")
                print("Jarvis could not create a new conversation.")
            continue

        # Save the user's message before sending it to the AI
        try:
            add_message(
                conversation_id,
                "user",
                user_message
            )
        except (psycopg.Error, RuntimeError):
            logger.exception("Could not save the user message.")
            print("Jarvis could not save your message.")
            print("Your message was not sent to the AI.")
            continue

        messages.append({
            "role": "user",
            "content": user_message,
        })

        try:
            response = provider.generate_chat_response(messages)
        except RuntimeError as exc:
            logger.error("Failed to generate a response: %s", exc)
            print(f"\nJarvis encountered an AI error: {exc}")
            print("Your message remains saved in PostgreSQL.")
            continue

        # Persist Jarvis's reply before adding it to in-memory history.
        try:
            add_message(
                conversation_id,
                "assistant",
                response,
            )
        except (psycopg.Error, RuntimeError):
            logger.exception("Could not save Jarvis's response.")
            print("Jarvis generated a reply but could not save it.")
            print("Please check the database before continuing.")
            continue

        messages.append({
            "role": "assistant",
            "content": response,
        })

        print(f"\nJarvis: {response}")

    logger.info("Jarvis application stopped")



if __name__ == "__main__":
    main()