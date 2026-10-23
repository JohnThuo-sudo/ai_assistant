
import json
import logging
import math
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from jarvis.config.settings import Settings


logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider:
    """Generate text embeddings using a local Ollama model."""

    def __init__(
        self,
        settings: Settings,
        model: str = "nomic-embed-text",
        timeout: int = 30,
    ) -> None:
        self.base_url = settings.ollama_base_url
        self.model = model
        self.timeout = timeout

    def embed(self, text: str) -> list[float]:
        """Convert one piece of text into an embedding vector."""
        if not isinstance(text, str):
            raise TypeError("text must be a string.")

        if not text.strip():
            raise ValueError("text cannot be empty.")

        payload = {
            "model": self.model,
            "input": text,
        }

        request = Request(
            url=f"{self.base_url}/api/embed",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            embeddings = result.get("embeddings")

            if (
                not isinstance(embeddings, list)
                or not embeddings
                or not isinstance(embeddings[0], list)
            ):
                raise RuntimeError(
                    "Ollama returned an invalid embedding response."
                )

            vector = embeddings[0]

            if not vector or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in vector
            ):
                raise RuntimeError(
                    "Ollama returned an invalid embedding vector."
                )

            logger.debug(
                "Generated embedding with %d dimensions using %s",
                len(vector),
                self.model,
            )

            return [float(value) for value in vector]

        except HTTPError as exc:
            raise RuntimeError(
                f"Ollama embedding API returned HTTP {exc.code}."
            ) from exc

        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                "Could not connect to the Ollama embedding API."
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc
