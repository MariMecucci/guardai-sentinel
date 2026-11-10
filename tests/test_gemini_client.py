"""Gemini adapter lifecycle tests using fake SDK objects (no API key/network)."""
import json
import sys
import types
import unittest
from unittest.mock import patch

from sentinel.ai import enhance_with_gemini
from sentinel.models import Report


class FakeClient:
    def __init__(self, *, api_key, fail=False):
        self.api_key = api_key
        self.fail = fail
        self.entered = False
        self.exited = False
        self.requested_model = None
        self.models = self

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True
        return False

    def generate_content(self, *, model, contents, config):
        if not self.entered or self.exited:
            raise RuntimeError("HTTP client already closed")
        self.requested_model = model
        if self.fail:
            raise RuntimeError("test error with sensitive key: secret-test-only")
        return types.SimpleNamespace(text=json.dumps({
            "summary": "Consulta precisa ser parametrizada.",
            "suggestions": ["Use placeholders SQL."],
        }))


class GeminiClientLifecycleTests(unittest.TestCase):
    def fake_sdk(self, client):
        google = types.ModuleType("google")
        genai = types.ModuleType("google.genai")
        types_mod = types.ModuleType("google.genai.types")
        genai.Client = lambda *, api_key: client
        types_mod.GenerateContentConfig = lambda **kwargs: kwargs
        genai.types = types_mod
        google.genai = genai
        return patch.dict(sys.modules, {
            "google": google,
            "google.genai": genai,
            "google.genai.types": types_mod,
        })

    def test_client_is_alive_during_request_and_closed_afterwards(self):
        client = FakeClient(api_key="secret-test-only")
        report = Report(filename="example.py", language="python")
        with self.fake_sdk(client):
            result = enhance_with_gemini(
                report, "cursor.execute('SELECT 1')",
                api_key="secret-test-only",
                model="gemini-3.5-flash-lite",
            )
        self.assertTrue(client.entered)
        self.assertTrue(client.exited)
        self.assertEqual(client.requested_model, "gemini-3.5-flash-lite")
        self.assertEqual(result.ai_summary, "Consulta precisa ser parametrizada.")
        self.assertEqual(result.ai_suggestions, ["Use placeholders SQL."])
        self.assertEqual(result.warnings, [])

    def test_request_error_is_sanitized_and_client_is_closed(self):
        client = FakeClient(api_key="secret-test-only", fail=True)
        report = Report(filename="example.py", language="python")
        with self.fake_sdk(client):
            result = enhance_with_gemini(
                report, "cursor.execute('SELECT 1')",
                api_key="secret-test-only",
            )
        self.assertTrue(client.exited)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("RuntimeError", result.warnings[0])
        self.assertNotIn("secret-test-only", result.warnings[0])
        self.assertIsNone(result.ai_summary)


if __name__ == "__main__":
    unittest.main()
