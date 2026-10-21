import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from jarvis.config.settings import Settings

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Communicate with a locally running ollama model."""

    def __init__(self, Settings:Settings, timeout: int=120) -> None:
        self.base_url = Settings.ollama_base_url
        self.model = Settings.ollama_model
        self.timeout = timeout

    def check_connection(self) -> bool:
        """Return True if the Ollama server is reachable."""
        url= f"{self.base_url}/api/tags"
        request = Request(url, method="GET")

        try:
            with urlopen(request, timeout=5) as response:
                return response.status == 200
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            logger.warning("Could not connect to Ollama: %s", exc)
            return False

    def generate_response(self, prompt: str) -> str:
        """Send a prompt to Ollama and return the generated text."""
        if not prompt or not prompt.strip():
            raise ValueError("The prompt cannot be empty")

        url = f"{self.base_url}/api/generate"

        payload = {
            "model" : self.model,
            "prompt": prompt,
            "stream": False,
        }

        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST"
        )

        start_time = time.perf_counter()

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            logger.error("Ollama returned HTTP %s: %s", exc.code, details)
            raise RuntimeError(
                f"Ollama returned HTTP {exc.code}: {details}"
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.error("Ollama returned as invalid response.")
            raise RuntimeError(
                "Ollama returned an invalid response."
            ) from exc

        elapsed = time.perf_counter() - start_time
        logger.info("Ollama response generated in %.2f seconds", elapsed)

        generated_text = result.get("response")

        if not isinstance(generated_text, str):
            raise RuntimeError("Ollama response did not contain generated text.")

        return generated_text.strip()