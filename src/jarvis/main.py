import logging

from jarvis.ai.ollama_provider import OllamaProvider
from jarvis.config.settings import load_settings
from jarvis.core.logging_config import configure_logging


def main() -> None:
    """Start the interactive Jarvis terminal assistant."""
    settings = load_settings()

    configure_logging(settings.log_level)
    logger = logging.getLogger("jarvis")

    print("=" * 42)
    print(f"{settings.app_name} - Personal AI Assistant")
    print("=" * 42)
    print(f"AI provider: Ollama")
    print(f"Model:  {settings.ollama_model}")
    print(f"API address: {settings.ollama_base_url}")
    print()
    print("Checking connection to Ollama...")

    provider = OllamaProvider(settings)

    if not provider.check_connection():
        print("Jarvis could not connect to Ollama.")
        print("Make sure Ollama is running and try again.")
        logger.error("Startup stopped because Ollama is unavailable")
        return

    print("Ollama is connected.")
    print("Jarvis is ready! Type 'exit' or 'quit' to stop.")
    print("Type 'clear' to clear the conversation history.")

    #Conversation history exists only for this running session.
    messages: list[dict[str, str]] = []

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
            messages.clear()
            print("Jarvis: Conversation history cleared.")
            continue

        #Add the new user message to the conversation
        messages.append({
            "role": "user",
            "content": user_message,
        })

        try:
            response = provider.generate_chat_response(messages)
            print(f"\nJarvis: {response}")

            # Store Jarvis's reply so future prompts have context.
            messages.append({
                "role": "assistant",
                "content": response,
            })

        except RuntimeError as exc:
            #Remove the unanswered message so history stays consistent
            messages.pop()


            logger.error("Failed to generate a response: %s", exc)
            print(f"\nJarvis encountered an error: {exc}")

    logger.info("Jarvis application stopped")

if __name__ == "__main__":
    main()