import logging
from pathlib import Path

def configure_logging(level: str) -> None:
    """Configure console and file logging for jarvis."""
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                log_dir / "jarvis.log",
                encoding="utf-8",
            )
        ],
        force=True
    )