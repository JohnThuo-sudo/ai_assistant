import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True) #frozen=True prevents normal reassignment of fields after an instance is created
class Settings:
    app_name: str
    ollama_base_url: str
    ollama_model: str
    log_level: str
    database_url: str = ""

def load_settings() -> Settings:
    """Load Jarvis configuration from environment variables."""
    load_dotenv()
    
    return Settings(
        app_name=os.getenv("JARVIS_APP_NAME", "Jarvis"),
        ollama_base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ).rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        log_level=os.getenv("JARVIS_LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "")
    )