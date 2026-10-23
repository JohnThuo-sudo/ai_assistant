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
from jarvis.database.memory_service import save_memory_with_approval
from jarvis.core.memory_context import build_memory_context
from jarvis.database.memory_repository import (get_active_memories, delete_memory)
from uuid import UUID
from jarvis.core.memory_retrieval import retrieve_relevant_memories
from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.core.semantic_memory_retrieval import (select_semantically_relevant_memories,)

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
    embedding_provider = OllamaEmbeddingProvider(settings)

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

        if command == "remember" or command.startswith("remember"):
            memory_content = user_message[len("remember"):].strip()

            if not memory_content:
                print("Jarvis: Provide a fact to remember.")
                print("Example: remember My favorite language is Python")
                continue

            print(f"\nFact to remember: {memory_content}")

            try:
                approval = input("Save this to long-term memory? [y/N]: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("/nJarvis: Memory request cancelled.")
                continue

            approved = approval == "y"

            if not approved:
                print("Jarvis: Memory was not saved.")
                continue

            try:
                memory_id = save_memory_with_approval(
                    content=memory_content,
                    approved=True,
                    source_conversation_id=conversation_id,
                    embedding_provider=embedding_provider,
                )

                if memory_id is not None:
                    print("Jarvis: Fact saved to long-term memory.")
                else:
                    print("Jarvis: Memory was not saved.")
            except (psycopg.Error, RuntimeError, ValueError):
                logger.exception("Could not save approved memory.")
                print("Jarvis could not save that memory")
                print("Check the database connection and try again.")

            continue

        # Display approved long-term memories
        if command == "memories":
            try:
                active_memories = get_active_memories()

                if not active_memories:
                    print("Jarvis: I have no active long-term memories.")
                    continue

                print("\nJarvis: Here is what I remember: ")

                for index, memory in enumerate(active_memories, start=1):
                    print(f"\n{index}. {memory['content']}")
                    print(f"    ID: {memory['id']}")
            except (psycopg.Error, RuntimeError):
                logger.exception("Could not retrieve saved memories.")
                print("Jarvis could not retrieve you memories.")

            continue

        if command == "forget" or command.startswith("forget "):
            memory_id_text = user_message[len("forget"):].strip()

            if not memory_id_text:
                print("Jarvis: Provide the ID of the memory to forget.")
                print("Use 'memories' to see saved memory IDs.")
                continue

            try:
                memory_id = UUID(memory_id_text)
            except ValueError:
                print("Jarvis: That is not a valid memory ID.")
                continue

            try:
                active_memories = get_active_memories()

                memory = next(
                    (
                        item
                        for item in active_memories
                        if item["id"] == memory_id
                    ),
                    None,
                )

                if memory is None:
                    print("Jarvis: I could not find that active memory.")
                    continue

                print(f"\nMemory to forget: {memory['content']}")

                try:
                    approval = input("Delete this memory permanently? [y/N]: ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    print("\nJarvis: Deletion cancelled")
                    continue

                if approval != 'y':
                    print("Jarvis: Memory was not deleted.")
                    continue
                if delete_memory(memory_id):
                    print("Jarvis: Memory deleted successfully.")
                else:
                    print("Jarvis: The memory was already deleted.")
            except (psycopg.Error, RuntimeError):
                logger.exception("Could not delete the requested memory.")
                print("Jarvis could not complete the deletion.")
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
            # Retrieve only relevant memories for the current question and add them to the AI context.
            active_memories = get_active_memories()

            selected_memories = select_semantically_relevant_memories(
                query=user_message,
                memories=active_memories,
                embedding_provider=embedding_provider,
                limit=5,
            )

            logger.info(
                "Semantic memory retrieval: available=%d, selected=%d",
                len(active_memories),
                len(selected_memories)
            )

            memory_context = build_memory_context(selected_memories)

            # Use a separate list so memory context is not persisted as an ordinary conversation message.
            # Keep memory context separate from saved conversation history
            model_messages = list(messages)

            if memory_context:
                model_messages.insert(
                    0,
                    {
                        "role": "system",
                        "context": memory_context,
                    },
                )

            response = provider.generate_chat_response(messages)
        except (psycopg.Error, RuntimeError, ValueError, TypeError) as exc:
            logger.error("Failed to retrieve memory or generate a response: %s", exc)
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