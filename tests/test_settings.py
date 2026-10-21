import os
import unittest
from unittest.mock import patch

from jarvis.config.settings import load_settings

class TestLoadSettings(unittest.TestCase):
    def test_default_settings(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()

        self.assertEqual(settings.app_name, "Jarvis")
        self.assertEqual(
            settings.ollama_base_url,
            "http://localhost:11434"
        )
        self.assertEqual(settings.ollama_model, "llama3.2:3b")
        self.assertEqual(settings.log_level, "INFO")

    def test_environmentvariable_overides(self):
        custom_environment = {
            "JARVIS_APP_NAME": "MyJarvis",
            "OLLAMA_BASE_URL": "http://localhost:11434/",
            "OLLAMA_MODEL": "llama3.2:3b",
            "JARVIS_LOG_LEVEL": "debug",
        }

        with patch.dict(os.environ, custom_environment, clear=True):
            settings = load_settings()

        self.assertEqual(settings.app_name, "MyJarvis")
        self.assertEqual(
            settings.ollama_base_url,
            "http://localhost:11434"
        )
        self.assertEqual(settings.ollama_model, "llama3.2:3b")
        self.assertEqual(settings.log_level, "DEBUG")

    def test_settings_are_immutable(self):
        settings= load_settings()

        with self.assertRaises(AttributeError):
            settings.app_name = "Changed"

if __name__ == "__main__":
    unittest.main()