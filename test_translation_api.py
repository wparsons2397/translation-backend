import unittest
from unittest.mock import patch
from translation_api import app

# python -m unittest discover
# to run

class TestTranslationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_running(self):
        response = self.app.get("/running")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "running"})

    @patch("translation_api.get_translations")
    def test_translate_many(self, mock_get_translations):
        # Mock the get_translations function
        mock_get_translations.return_value = [
            type("MockTranslation", (object,), {"text": "Hola"}),
            type("MockTranslation", (object,), {"text": "Bonjour"}),
            type("MockTranslation", (object,), {"text": "Hallo"})
        ]

        response = self.app.post(
            "/translate/es",
            json={"text_obj": {"text_1": "Hello", "text_2": "Hi", "text_3": "Hey"}}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "text_1": "Hola",
            "text_2": "Bonjour",
            "text_3": "Hallo"
        })

    @patch("translation_api.get_translations")
    def test_translate_many_missing_fields(self, mock_get_translations):
        # Mock the get_translations function (not called in this case)
        mock_get_translations.return_value = []

        response = self.app.post(
            "/translate/es",
            json={"text_obj": {"text_1": None, "text_2": None}}  # All fields are None
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing text fields"})

    @patch("translation_api.get_translations")
    def test_translate_many_translation_failure(self, mock_get_translations):
        # Mock the get_translations function to simulate a failure
        mock_get_translations.return_value = [
            {"text": "Hola"},  # Successful translation
            {"error": "Error translating 'Hi': Simulated failure"},  # Failed translation
            {"text": "Hallo"}  # Successful translation
        ]

        response = self.app.post(
            "/translate/es",
            json={"text_obj": {"text_1": "Hello", "text_2": "Hi", "text_3": "Hey"}}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {
            "error": "One or more translations failed",
            "details": [
                {"text": "Hola"},
                {"error": "Error translating 'Hi': Simulated failure"},
                {"text": "Hallo"}
            ]
        })

    @patch("translation_api.get_translation")
    def test_translate_one(self, mock_get_translation):
        # Mock the get_translation function
        mock_get_translation.return_value = type("MockTranslation", (object,), {"text": "Hola"})  # Single object

        response = self.app.post(
            "/translate_custom/es",
            json={"text_obj": "Hello"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"custom_text": "Hola"})

    @patch("translation_api.get_translation")
    def test_translate_one_exceeds_length(self, mock_get_translation):
        # Mock the get_translation function (not called in this case)
        mock_get_translation.return_value = None

        long_text = "a" * 15001  # Create a string with 15,001 characters
        response = self.app.post(
            "/translate_custom/es",
            json={"text_obj": long_text}
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json, {"error": "Text length exceeds limit."})

if __name__ == "__main__":
    unittest.main()
