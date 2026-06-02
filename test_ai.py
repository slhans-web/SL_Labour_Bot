import unittest
import ai_assistant
import config

class TestAIAssistant(unittest.TestCase):
    def test_ai_not_configured_by_default(self):
        # Set config to placeholder value
        config.GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
        self.assertFalse(ai_assistant.is_ai_configured())
        
        # Verify the output message instructs user
        response = ai_assistant.ask_ai_assistant("Test Query")
        self.assertIn("Google Gemini API Key", response)
        self.assertIn("Configuration Error", response)

    def test_ai_configured_state(self):
        # Verify true is returned if some custom token is supplied
        config.GEMINI_API_KEY = "dummy_token_12345"
        self.assertTrue(ai_assistant.is_ai_configured())

if __name__ == "__main__":
    unittest.main()
