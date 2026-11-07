"""Local provider settings: secrets never leave the server, strict input, free test endpoints only."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from qa_war_room.engine import EngineError, SessionEngine
from qa_war_room.provider_settings import PROVIDERS, ProviderSettings
from qa_war_room.server import create_server

KEY = "sk-test-0123456789abcdefWXYZ"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeOpener:
    """Records requests; returns canned JSON or raises the configured error. No network."""

    def __init__(self, body=None, error=None):
        self.body, self.error, self.requests = body, error, []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        if self.error:
            raise self.error
        return FakeResponse(json.dumps(self.body).encode())


class ProviderSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "settings.json"

    def tearDown(self):
        self.temp.cleanup()

    def store(self, **kw):
        return ProviderSettings(self.path, **kw)

    def test_key_is_stored_locally_but_only_masked_in_public_view(self):
        view = self.store().update({"provider": "openai", "api_key": KEY, "model": "gpt-6-luna", "active": True})
        self.assertNotIn(KEY, json.dumps(view))
        self.assertEqual(view["configured"]["openai"]["key_hint"], "••••WXYZ")
        self.assertTrue(view["configured"]["openai"]["ready"])
        self.assertEqual(view["active"], "openai")
        self.assertFalse(view["used_by_live_rooms"])
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8"))["providers"]["openai"]["api_key"], KEY)

    def test_every_provider_has_models_with_tiers_and_a_source(self):
        self.assertEqual(set(PROVIDERS), {"typhoon", "anthropic", "openai", "gemini", "openrouter", "ollama"})
        for spec in PROVIDERS.values():
            self.assertTrue(spec["pricing_source"].startswith("https://"))
            self.assertGreaterEqual(len(spec["models"]), 2)
            self.assertTrue(all(m["tier"] in {"budget", "balanced", "best"} for m in spec["models"]))

    def test_invalid_inputs_are_rejected(self):
        store = self.store()
        bad = [
            {"provider": "nope"},
            {"provider": "openai", "api_key": "has space inside"},
            {"provider": "openai", "api_key": "short"},
            {"provider": "openai", "model": "bad model"},
            {"provider": "openai", "base_url": "http://127.0.0.1:11434"},
            {"provider": "ollama", "api_key": KEY},
            {"provider": "ollama", "base_url": "http://evil.example:11434"},
            {"provider": "ollama", "base_url": "https://127.0.0.1:11434"},
            {"provider": "ollama", "base_url": "http://127.0.0.1:11434/redirect?to=x"},
            {"provider": "openai", "active": "yes"},
        ]
        for payload in bad:
            with self.subTest(payload=payload), self.assertRaises(EngineError):
                store.update(payload)
        self.assertFalse(self.path.exists())

    def test_clear_removes_key_and_active(self):
        store = self.store()
        store.update({"provider": "anthropic", "api_key": KEY, "model": "claude-haiku-5-5", "active": True})
        view = store.clear({"provider": "anthropic"})
        self.assertFalse(view["configured"]["anthropic"]["has_key"])
        self.assertIsNone(view["active"])
        self.assertNotIn(KEY, self.path.read_text(encoding="utf-8"))

    def test_test_uses_fixed_free_endpoint_and_reports_model_match(self):
        opener = FakeOpener({"data": [{"id": "claude-haiku-5-5"}, {"id": "claude-opus-5-5"}]})
        store = self.store(opener=opener)
        store.update({"provider": "anthropic", "api_key": KEY, "model": "claude-haiku-5-5"})
        result = store.test({"provider": "anthropic"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["model_count"], 2)
        self.assertTrue(result["model_found"])
        self.assertNotIn(KEY, json.dumps(result))
        request = opener.requests[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertTrue(request.full_url.startswith("https://api.anthropic.com/v1/models"))
        self.assertIsNone(request.data)

    def test_rejected_key_and_unreachable_host_are_reported_without_bodies(self):
        store = self.store(opener=FakeOpener(error=HTTPError("u", 401, "no", {}, io.BytesIO(b'{"leak":"' + KEY.encode() + b'"}'))))
        store.update({"provider": "openai", "api_key": KEY})
        result = store.test({"provider": "openai"})
        self.assertEqual((result["ok"], result["status"], result["message"]), (False, 401, "key_rejected"))
        self.assertNotIn(KEY, json.dumps(result))
        store = self.store(opener=FakeOpener(error=URLError("refused")))
        self.assertEqual(store.test({"provider": "ollama"})["message"], "unreachable")

    def test_bare_array_model_list_is_parsed(self):
        # Shape observed from https://api.opentyphoon.ai/v1/models on 2026-11-07.
        opener = FakeOpener([{"id": "typhoon-v2.5-30b-a3b-instruct", "object": "model"}, {"id": "typhoon-ocr", "object": "model"}])
        store = self.store(opener=opener)
        store.update({"provider": "typhoon", "api_key": KEY, "model": "typhoon-v2.5-30b-a3b-instruct"})
        result = store.test({"provider": "typhoon"})
        self.assertEqual((result["ok"], result["model_count"], result["model_found"]), (True, 2, True))

    def test_test_requires_a_saved_key(self):
        with self.assertRaises(EngineError) as raised:
            self.store(opener=FakeOpener({})).test({"provider": "gemini"})
        self.assertEqual(raised.exception.code, "missing_api_key")


class ProviderSettingsHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = create_server(SessionEngine(), port=0, settings_path=Path(cls.temp.name) / "s.json")
        import threading
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def call(self, path, body=None, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        request = Request(self.base + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            with error:
                return error.code, json.loads(error.read())

    def test_routes_store_mask_and_validate(self):
        status, view = self.call("/api/settings", {"provider": "typhoon", "api_key": KEY, "model": "typhoon-v2.5-30b-a3b-instruct"})
        self.assertEqual(status, 200)
        self.assertNotIn(KEY, json.dumps(view))
        status, view = self.call("/api/settings")
        self.assertEqual(status, 200)
        self.assertTrue(view["configured"]["typhoon"]["has_key"])
        self.assertNotIn(KEY, json.dumps(view))
        self.assertEqual(self.call("/api/settings", {"provider": "typhoon", "reveal": True})[0], 400)
        self.assertEqual(self.call("/api/settings", {"provider": "typhoon"}, "https://outside.invalid")[0], 403)
        self.assertEqual(self.call("/api/settings/clear", {"provider": "typhoon"})[0], 200)

    def test_settings_page_is_served(self):
        with urlopen(self.base + "/settings.html", timeout=5) as response:
            self.assertEqual(response.status, 200)


if __name__ == "__main__":
    unittest.main()
