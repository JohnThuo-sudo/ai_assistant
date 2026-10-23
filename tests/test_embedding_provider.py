
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from jarvis.ai.embedding_provider import OllamaEmbeddingProvider
from jarvis.config.settings import Settings


class TestOllamaEmbeddingProvider(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            app_name="Jarvis",
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3.2:3b",
            log_level="INFO",
        )
        self.provider = OllamaEmbeddingProvider(self.settings)

    @patch("jarvis.ai.embedding_provider.urlopen")
    def test_embed_returns_float_vector(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "embeddings": [[0.12, -0.25, 0.8]]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.provider.embed("Python programming")

        self.assertEqual(result, [0.12, -0.25, 0.8])
        self.assertTrue(all(type(value) is float for value in result))

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:11434/api/embed")

        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "nomic-embed-text")
        self.assertEqual(payload["input"], "Python programming")

    def test_empty_text_is_rejected(self):
        with self.assertRaises(ValueError):
            self.provider.embed("   ")

    def test_non_string_text_is_rejected(self):
        with self.assertRaises(TypeError):
            self.provider.embed(123)

    @patch("jarvis.ai.embedding_provider.urlopen")
    def test_connection_failure_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")

        with self.assertRaisesRegex(RuntimeError, "Could not connect"):
            self.provider.embed("Python programming")

    @patch("jarvis.ai.embedding_provider.urlopen")
    def test_invalid_json_raises_runtime_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid JSON"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
            self.provider.embed("Python programming")

    @patch("jarvis.ai.embedding_provider.urlopen")
    def test_invalid_vector_is_rejected(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "embeddings": [[0.1, "invalid"]]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "invalid embedding vector"):
            self.provider.embed("Python programming")


if __name__ == "__main__":
    unittest.main()
