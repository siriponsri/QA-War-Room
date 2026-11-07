import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from qa_war_room.engine import SessionEngine
from qa_war_room.server import MAX_BODY_BYTES, create_server


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        static_dir = Path(cls.temp.name)
        (static_dir / "index.html").write_text("<!doctype html><title>test fixture frontend</title>", encoding="utf-8")
        (static_dir / "app.js").write_text("'use strict';", encoding="utf-8")
        cls.engine = SessionEngine()
        cls.server = create_server(cls.engine, port=0, static_dir=static_dir)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.temp.cleanup()

    def request(self, method, path, payload=None, headers=None, raw_body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        body = raw_body if raw_body is not None else (json.dumps(payload).encode() if payload is not None else None)
        request_headers = {"Content-Type": "application/json"} if body is not None else {}
        request_headers.update(headers or {})
        connection.request(method, path, body=body, headers=request_headers)
        response = connection.getresponse()
        data = response.read()
        status = response.status
        response_headers = dict(response.getheaders())
        connection.close()
        parsed = json.loads(data) if response_headers.get("Content-Type", "").startswith("application/json") else data
        return status, parsed, response_headers

    def start(self, case_id="MFG-001"):
        status, state, _ = self.request("POST", "/api/sessions", {"case_id": case_id})
        self.assertEqual(status, 201)
        return state

    def test_case_and_persona_endpoints(self):
        status, value, _ = self.request("GET", "/api/cases")
        self.assertEqual(status, 200)
        self.assertEqual(len(value["cases"]), 8)
        self.assertNotIn("support_sets", json.dumps(value))
        status, value, _ = self.request("GET", "/api/personas")
        self.assertEqual(status, 200)
        self.assertEqual(len(value["personas"]), 6)
        status, value, _ = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(value["mode"], "offline_scripted_synthetic_demo")

    def test_static_assets_are_local_and_have_no_cache_security_headers(self):
        status, body, headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"test fixture frontend", body)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(self.request("GET", "/app.js")[0], 200)

    def test_gold_and_arbitrary_files_cannot_be_read_over_http(self):
        for path in (
            "/data/demo/evidence.json", "/data/demo/evaluator/gold.json",
            "/%2e%2e/%2e%2e/data/demo/evaluator/gold.json",
            "/%252e%252e/%252e%252e/data/demo/evaluator/gold.json",
            "/etc/passwd", "/api/evaluator/gold", "/api/cases/MFG-001/evidence/D4",
        ):
            with self.subTest(path=path):
                status, value, _ = self.request("GET", path)
                self.assertEqual(status, 404)
                self.assertNotIn("expected_verdict", json.dumps(value))

    def test_cross_origin_and_rebinding_hosts_rejected(self):
        status, error, _ = self.request("GET", "/api/cases", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)
        self.assertEqual(error["error"]["code"], "invalid_host")
        status, error, _ = self.request("POST", "/api/sessions", {"case_id": "MFG-001"}, headers={"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        self.assertEqual(error["error"]["code"], "cross_origin_denied")
        status, _, _ = self.request("POST", "/api/sessions", {"case_id": "MFG-001"}, headers={"Origin": f"http://127.0.0.1:{self.port}"})
        self.assertEqual(status, 201)

    def test_body_size_type_and_malformed_json_rejected(self):
        examples = (
            (b"x" * (MAX_BODY_BYTES + 1), {}, 413, "request_too_large"),
            (b"not-json", {}, 400, "invalid_json"),
            (b"\xff", {}, 400, "invalid_json"),
            (b"[]", {}, 400, "object_required"),
            (b"{}", {"Content-Type": "text/plain"}, 415, "json_required"),
        )
        for body, headers, expected_status, code in examples:
            with self.subTest(code=code):
                status, error, _ = self.request("POST", "/api/sessions", raw_body=body, headers=headers)
                self.assertEqual(status, expected_status)
                self.assertEqual(error["error"]["code"], code)

    def test_deeply_nested_json_does_not_crash_handler(self):
        status, error, _ = self.request("POST", "/api/sessions", raw_body=b"[" * 2000 + b"0" + b"]" * 2000)
        self.assertEqual(status, 400)
        # Some Python builds parse this depth; others raise RecursionError.
        self.assertIn(error["error"]["code"], {"invalid_json", "object_required"})
        self.assertEqual(self.request("GET", "/api/health")[0], 200)

    def test_payload_cannot_override_budget_or_include_gold(self):
        status, error, _ = self.request("POST", "/api/sessions", {"case_id": "MFG-001", "budget": 999})
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "unknown_field")

    def test_full_http_episode_and_report(self):
        state = self.start("MFG-002")
        sid = state["session_id"]
        base = f"/api/sessions/{sid}"
        status, error, _ = self.request("GET", base + "/report?format=json")
        self.assertEqual(status, 409)
        self.assertEqual(error["error"]["code"], "report_not_ready")
        for eid in ("D2", "D4"):
            status, state, _ = self.request("POST", base + "/request", {"evidence_id": eid})
            self.assertEqual(status, 200)
            self.assertIsNone(state["feedback"])
            self.assertNotIn("expected_verdict", json.dumps(state))
        status, state, _ = self.request("POST", base + "/decide", {
            "verdict": "contradicted", "evidence_ids": ["D2", "D4"],
            "rationale": "Protocol requires zero failed acceptance batches; B212 failed.",
        })
        self.assertEqual(status, 200)
        self.assertTrue(state["feedback"]["decision_and_support_correct"])
        status, report, headers = self.request("GET", base + "/report?format=json")
        self.assertEqual(status, 200)
        self.assertEqual(report["report_schema_version"], "0.1.0")
        self.assertIn("attachment", headers["Content-Disposition"])
        status, markdown, _ = self.request("GET", base + "/report?format=markdown")
        self.assertEqual(status, 200)
        self.assertIn(b"Record checklist", markdown)
        status, error, _ = self.request("POST", base + "/request", {"evidence_id": "D3"})
        self.assertEqual(status, 409)
        self.assertEqual(error["error"]["code"], "session_completed")

    def test_step_endpoint_takes_no_hidden_instruction_parameters(self):
        state = self.start()
        path = f"/api/sessions/{state['session_id']}/step"
        status, error, _ = self.request("POST", path, {"expected_verdict": "supported"})
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "unknown_field")
        status, state, _ = self.request("POST", path, {})
        self.assertEqual(status, 200)
        self.assertEqual([record["id"] for record in state["evidence"]], ["D2"])


if __name__ == "__main__":
    unittest.main()
