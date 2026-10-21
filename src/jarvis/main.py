import logging

from jarvis.config.settings import load_settings
from jarvis.core.logging_config import configure_logging


def main() -> None:
    """Start the Jarvis application."""
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
    print("Application foundation is working.")

    logger.info("Jarvis application initialized")

if __name__ == "__main__":
    main()