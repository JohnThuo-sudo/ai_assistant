
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

from jarvis.ai.ollama_provider import OllamaProvider
from jarvis.config.settings import Settings


class TestOllamaProvider(unittest.TestCase):
    def setUp(self):
        settings = Settings(
            app_name="Jarvis",
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3.2:3b",
            log_level="INFO",
        )
        self.provider = OllamaProvider(settings)

    @patch("jarvis.ai.ollama_provider.urlopen")
    def test_check_connection_success(self, mock_urlopen):
        response = Mock()
        response.status = 200
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = response

        self.assertTrue(self.provider.check_connection())

    @patch("jarvis.ai.ollama_provider.urlopen")
    def test_check_connection_failure(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")

        self.assertFalse(self.provider.check_connection())

    @patch("jarvis.ai.ollama_provider.urlopen")
    def test_generate_response_success(self, mock_urlopen):
        expected_response = "Jarvis is online."

        response = Mock()
        response.read.return_value = json.dumps(
            {"response": expected_response}
        ).encode("utf-8")
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = response

        result = self.provider.generate_response("Say hello")

        self.assertEqual(result, expected_response)

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))

        self.assertEqual(payload["model"], "llama3.2:3b")
        self.assertEqual(payload["prompt"], "Say hello")
        self.assertFalse(payload["stream"])

    def test_generate_response_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            self.provider.generate_response("   ")


if __name__ == "__main__":
    unittest.main()
