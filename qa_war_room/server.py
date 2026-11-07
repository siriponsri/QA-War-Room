"""A local-only HTTP interface, intentionally free of paid services and keys.

This bounded demonstration does not provide production authentication, durable
storage, validated audit trails, signatures, authorization or QMS integration.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit

from . import __version__
from .engine import EngineError, SessionEngine, report_markdown
from .live_room import LiveRooms, transcript_markdown
from .provider_settings import ProviderSettings


MAX_BODY_BYTES = 16 * 1024
SESSION_PATH = re.compile(r"/api/sessions/(qr_[0-9a-f]{32})(?:/(request|decide|step|report))?\Z")
ROOM_PATH = re.compile(r"/api/rooms/(room_[0-9a-f]{32})(?:/(pause|resume|stop|note|request|report))?\Z")
STATIC_EXTENSIONS = {".html", ".css", ".js", ".svg", ".ico", ".png", ".woff2"}


def _payload_fields(payload: dict, allowed: set[str], required: set[str]) -> None:
    if set(payload) - allowed:
        raise EngineError("unknown_field", "The request contains fields not accepted by this endpoint.")
    if required - set(payload):
        raise EngineError("missing_field", "The request is missing a required field.")


def make_handler(engine: SessionEngine, static_dir: Path | None = None, rooms=None, settings=None):
    static_root = (static_dir or Path(__file__).resolve().parent / "static").resolve()
    rooms = rooms or LiveRooms(engine)
    settings = settings or ProviderSettings()

    class Handler(BaseHTTPRequestHandler):
        server_version = "QA-War-Room/" + __version__
        sys_version = ""

        def log_message(self, format: str, *args) -> None:
            # Deliberately do not log request bodies, evidence, or user rationales.
            return

        def _send(self, status: int, body: bytes, content_type: str, filename: str | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            if filename:
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, value: dict, filename: str | None = None) -> None:
            self._send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", filename)

        def _error(self, error: EngineError) -> None:
            self._json(error.http_status, {"error": {"code": error.code, "message": error.message}})

        def _validate_local_request(self) -> None:
            port = self.server.server_address[1]
            allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            host = self.headers.get("Host", "").lower()
            if host not in allowed_hosts:
                raise EngineError("invalid_host", "Use the localhost URL printed by the server.", 403)
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://" + allowed for allowed in allowed_hosts}:
                raise EngineError("cross_origin_denied", "Cross-origin access is not enabled for this local demo.", 403)

        def _body(self) -> dict:
            if self.headers.get("Transfer-Encoding"):
                raise EngineError("transfer_encoding_denied", "Chunked request bodies are not supported.", 400)
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                raise EngineError("json_required", "Send an application/json request body.", 415)
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise EngineError("length_required", "Content-Length is required.", 411)
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise EngineError("invalid_length", "Content-Length must be a nonnegative integer.") from exc
            if length < 0 or length > MAX_BODY_BYTES:
                raise EngineError("request_too_large", "The request body exceeds the local demo limit.", 413)
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("Truncated JSON request.")
                payload = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeError, RecursionError) as exc:
                raise EngineError("invalid_json", "The request body must be valid UTF-8 JSON.") from exc
            if not isinstance(payload, dict):
                raise EngineError("object_required", "The JSON request body must be an object.")
            return payload

        def do_GET(self) -> None:
            try:
                self._validate_local_request()
                url = urlsplit(self.path)
                path = unquote(url.path)
                if path == "/api/health":
                    self._json(200, {"status": "ok", "version": __version__, "mode": "offline_scripted_synthetic_demo"})
                    return
                if path == "/api/cases":
                    self._json(200, {"cases": engine.list_cases()})
                    return
                if path == "/api/personas":
                    self._json(200, {"personas": engine.personas()})
                    return
                if path == "/api/rooms":
                    self._json(200, rooms.overview())
                    return
                if path == "/api/settings":
                    self._json(200, settings.public())
                    return
                room_match = ROOM_PATH.fullmatch(path)
                if room_match:
                    room_id, action = room_match.groups()
                    if action is None:
                        self._json(200, rooms.state(room_id))
                        return
                    if action == "report":
                        params = parse_qs(url.query, keep_blank_values=True)
                        if set(params) - {"format", "lang"} or any(len(values) != 1 for values in params.values()):
                            raise EngineError("invalid_format", "Use one format and language parameter.")
                        kind, language = params.get("format", ["json"])[0], params.get("lang", ["th"])[0]
                        if kind not in {"json", "markdown"} or language not in {"th", "en"}:
                            raise EngineError("invalid_format", "Use json/markdown and th/en.")
                        report = rooms.report(room_id)
                        if kind == "markdown":
                            self._send(200, transcript_markdown(report, language).encode("utf-8"), "text/markdown; charset=utf-8", f"{room_id}-conversation.md")
                        else:
                            self._json(200, report, f"{room_id}-transcript.json")
                        return
                matched = SESSION_PATH.fullmatch(path)
                if matched:
                    session_id, action = matched.groups()
                    if action is None:
                        self._json(200, engine.state(session_id))
                        return
                    if action == "report":
                        params = parse_qs(url.query, keep_blank_values=True)
                        if set(params) - {"format"} or len(params.get("format", ["json"])) != 1:
                            raise EngineError("invalid_format", "Use one format parameter: json or markdown.")
                        format_name = params.get("format", ["json"])[0]
                        if format_name not in {"json", "markdown"}:
                            raise EngineError("invalid_format", "Report format must be json or markdown.")
                        report = engine.report(session_id)
                        if format_name == "json":
                            self._json(200, report, f"{session_id}-report.json")
                        else:
                            self._send(200, report_markdown(report).encode("utf-8"), "text/markdown; charset=utf-8", f"{session_id}-report.md")
                        return
                if path.startswith("/api/"):
                    raise EngineError("not_found", "API endpoint not found.", 404)
                relative = ("live.html" if (static_root / "live.html").is_file() else "index.html") if path == "/" else path.lstrip("/")
                file_path = (static_root / relative).resolve()
                try:
                    file_path.relative_to(static_root)
                except ValueError as exc:
                    raise EngineError("not_found", "File not found.", 404) from exc
                if file_path.suffix not in STATIC_EXTENSIONS or not file_path.is_file():
                    raise EngineError("not_found", "File not found.", 404)
                content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
                if file_path.suffix in {".html", ".css", ".js", ".svg"}:
                    content_type += "; charset=utf-8"
                self._send(200, file_path.read_bytes(), content_type)
            except EngineError as error:
                self._error(error)
            except (OSError, ValueError, KeyError):
                self._error(EngineError("internal_error", "The local demo could not process this request.", 500))

        def do_POST(self) -> None:
            try:
                self._validate_local_request()
                url = urlsplit(self.path)
                if url.query:
                    raise EngineError("query_not_allowed", "POST endpoints do not accept URL query parameters.")
                path = unquote(url.path)
                payload = self._body()
                if path == "/api/rooms":
                    _payload_fields(payload, {"case_id", "auditor_role", "time_limit", "interval_ms"}, {"case_id"})
                    self._json(201, rooms.create(payload["case_id"], payload.get("auditor_role", "auditor-expert-01"), payload.get("time_limit", 60), payload.get("interval_ms", 650)))
                    return
                if path == "/api/settings":
                    _payload_fields(payload, {"provider", "api_key", "model", "base_url", "active"}, {"provider"})
                    self._json(200, settings.update(payload))
                    return
                if path == "/api/settings/clear":
                    _payload_fields(payload, {"provider"}, {"provider"})
                    self._json(200, settings.clear(payload))
                    return
                if path == "/api/settings/test":
                    _payload_fields(payload, {"provider"}, {"provider"})
                    self._json(200, settings.test(payload))
                    return
                room_match = ROOM_PATH.fullmatch(path)
                if room_match:
                    room_id, action = room_match.groups()
                    if action in {"pause", "resume", "stop"}:
                        _payload_fields(payload, set(), set())
                        state = rooms.control(room_id, action)
                    elif action == "note":
                        _payload_fields(payload, {"text"}, {"text"})
                        state = rooms.note(room_id, payload["text"])
                    elif action == "request":
                        _payload_fields(payload, {"evidence_id"}, {"evidence_id"})
                        state = rooms.request(room_id, payload["evidence_id"])
                    else:
                        raise EngineError("not_found", "Room action not found.", 404)
                    self._json(200, state)
                    return
                if path == "/api/sessions":
                    _payload_fields(payload, {"case_id", "auditor_role"}, {"case_id"})
                    self._json(201, engine.create(payload["case_id"], payload.get("auditor_role", "auditor-expert-01")))
                    return
                matched = SESSION_PATH.fullmatch(path)
                if not matched:
                    raise EngineError("not_found", "API endpoint not found.", 404)
                session_id, action = matched.groups()
                if action == "request":
                    _payload_fields(payload, {"evidence_id"}, {"evidence_id"})
                    state = engine.request(session_id, payload["evidence_id"])
                elif action == "decide":
                    _payload_fields(payload, {"verdict", "evidence_ids", "rationale"}, {"verdict", "evidence_ids", "rationale"})
                    state = engine.decide(session_id, payload["verdict"], payload["evidence_ids"], payload["rationale"])
                elif action == "step":
                    _payload_fields(payload, set(), set())
                    state = engine.step(session_id)
                else:
                    raise EngineError("not_found", "API endpoint not found.", 404)
                self._json(200, state)
            except EngineError as error:
                self._error(error)
            except (OSError, ValueError, KeyError):
                self._error(EngineError("internal_error", "The local demo could not process this request.", 500))

    return Handler


def create_server(engine: SessionEngine, host: str = "127.0.0.1", port: int = 8765,
                  static_dir: Path | None = None, settings_path: Path | None = None) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("This starter binds to localhost only. Production serving is outside its scope.")
    rooms = LiveRooms(engine)
    settings = ProviderSettings(settings_path)
    server = ThreadingHTTPServer((host, port), make_handler(engine, static_dir, rooms, settings))
    server.rooms = rooms
    server.settings = settings
    original_close = server.server_close
    def close_server():
        rooms.close()
        original_close()
    server.server_close = close_server
    server.daemon_threads = True
    # Bound idle socket reads to avoid an indefinite incomplete local request.
    original_get_request = server.get_request

    def get_request():
        connection, address = original_get_request()
        connection.settimeout(10)
        return connection, address

    server.get_request = get_request
    return server
