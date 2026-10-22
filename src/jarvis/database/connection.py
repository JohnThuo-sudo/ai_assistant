import psycopg

from jarvis.config.settings import load_settings

def get_connection() -> psycopg.Connection:
    """Open and retrun a cooncetion to Jarvis's PstgreSQL database."""
    settings = load_settings()

    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Check your local .env file."
        )

    return psycopg.connect(
        settings.database_url,
        connect_timeout=5
    )
