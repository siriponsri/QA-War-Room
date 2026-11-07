"""Local model-provider settings: API keys, provider and model choice.

Owner-approved scope (7 November 2026): store settings on this computer and test that a key
works through each provider's free account/model-list endpoint. Nothing here sends prompts,
evidence or case data to a provider, and live rooms do not use these settings yet (agents stay
rule-based; ``llm_calls`` remains 0).

Security boundaries:
- Keys are written only to a local JSON file (default ``<project>/.qawr/provider-settings.json``,
  gitignored) and are never returned to the browser; the API exposes a masked hint only.
- Outbound requests go only to the fixed official endpoints below, or for Ollama to a loopback
  address. No user-supplied remote URL is ever fetched.
- Test responses are reduced to status, counts and model IDs; provider error bodies are not echoed.

Prices are USD per 1M tokens (input/output) as published on the listed source pages when checked;
they change, so the UI links the source and shows the check date.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .engine import EngineError

PRICE_CHECKED = "2026-11-07"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / ".qawr" / "provider-settings.json"
MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}$")
KEY = re.compile(r"^[\x21-\x7e]{8,400}$")  # printable ASCII, no spaces
LOOPBACK = {"127.0.0.1", "localhost", "::1"}


def _m(model_id, tier, input_usd=None, output_usd=None, context=None, note_en="", note_th="", recommended=False):
    return {"id": model_id, "tier": tier, "input_usd": input_usd, "output_usd": output_usd, "context": context,
            "note": {"en": note_en, "th": note_th}, "recommended": recommended}


# tier: budget (cheap/fast), balanced (good value), best (strongest)
PROVIDERS = {
    "typhoon": {
        "name": "Typhoon (SCB 10X)", "needs_key": True, "key_hint": "sk-…", "thai": True,
        "site": "https://opentyphoon.ai/", "pricing_source": "https://docs.opentyphoon.ai/en/models/",
        "price_note": {"en": "Prices are not published in the API docs checked; see the provider site.", "th": "เอกสาร API ที่ตรวจไม่ได้ระบุราคา ดูที่เว็บผู้ให้บริการ"},
        "models": [
            _m("typhoon-v2.5-30b-a3b-instruct", "balanced", context=128_000, recommended=True,
               note_en="Thai-first instruct model; 5 req/s, 200 req/min.", note_th="โมเดลเน้นภาษาไทย จำกัด 5 ครั้ง/วินาที 200 ครั้ง/นาที"),
            _m("typhoon-v2.1-12b-instruct", "budget", context=56_000,
               note_en="Smaller model in the docs; not in the current /v1/models list.", note_th="รุ่นเล็กในเอกสาร แต่ไม่อยู่ในรายการ /v1/models ล่าสุด"),
        ],
    },
    "anthropic": {
        "name": "Anthropic (Claude)", "needs_key": True, "key_hint": "sk-ant-…",
        "site": "https://platform.claude.com/", "pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing",
        "price_note": {"en": "First-party API rates (cached 2026-10-06).", "th": "ราคา API ของ Anthropic โดยตรง (ข้อมูล 2026-10-06)"},
        "models": [
            _m("claude-haiku-5-5", "budget", 0.10, 0.50, 1_000_000, recommended=True,
               note_en="Cheapest and fast; price for prompts up to 100K tokens.", note_th="ถูกและเร็วที่สุด ราคานี้สำหรับ prompt ไม่เกิน 100K token"),
            _m("claude-sonnet-5-5", "balanced", 2.00, 10.00, 1_000_000, note_en="Everyday work, good value.", note_th="งานทั่วไป คุ้มค่า"),
            _m("claude-opus-5-5", "best", 4.00, 20.00, 1_000_000, note_en="Strong reasoning; Anthropic's default model.", note_th="คิดวิเคราะห์ดี เป็นโมเดลหลักของ Anthropic"),
            _m("claude-fable-5-1", "best", 10.00, 50.00, 1_000_000, note_en="Most capable widely released Claude.", note_th="Claude ที่เก่งที่สุดที่เปิดให้ใช้ทั่วไป"),
        ],
    },
    "openai": {
        "name": "OpenAI", "needs_key": True, "key_hint": "sk-…",
        "site": "https://platform.openai.com/", "pricing_source": "https://developers.openai.com/api/docs/pricing",
        "price_note": {"en": "Standard tier, prompts up to 272K tokens.", "th": "ราคามาตรฐาน prompt ไม่เกิน 272K token"},
        "models": [
            _m("gpt-5-nano", "budget", 0.05, 0.40, note_en="Cheapest listed text model.", note_th="ถูกที่สุดในรายการ"),
            _m("gpt-6-luna", "budget", 0.10, 0.50, recommended=True, note_en="Newest small model.", note_th="รุ่นเล็กรุ่นใหม่"),
            _m("gpt-5.4-mini", "budget", 0.75, 4.50),
            _m("gpt-6.1-terra", "balanced", 1.00, 5.00, note_en="Good value mid model.", note_th="รุ่นกลาง คุ้มค่า"),
            _m("gpt-6.1-sol", "balanced", 2.00, 10.00),
            _m("gpt-6-astra", "best", 10.00, 50.00, note_en="Flagship.", note_th="รุ่นเรือธง"),
        ],
    },
    "gemini": {
        "name": "Google Gemini", "needs_key": True, "key_hint": "AIza…",
        "site": "https://aistudio.google.com/", "pricing_source": "https://aistudio.google.com/docs/pricing",
        "price_note": {"en": "Paid tier. Several Flash models also have a free tier. Some prices rise on 1 Dec 2026 / 1 Jan 2027.", "th": "ราคาแบบจ่ายเงิน รุ่น Flash หลายรุ่นมี free tier บางรุ่นขึ้นราคา 1 ธ.ค. 2026 / 1 ม.ค. 2027"},
        "models": [
            _m("gemini-2.5-flash-lite", "budget", 0.10, 0.40, note_en="Cheapest; free tier.", note_th="ถูกที่สุด มี free tier"),
            _m("gemini-3.1-flash-lite", "budget", 0.25, 1.50, note_en="Free tier.", note_th="มี free tier"),
            _m("gemini-3.5-flash-lite", "budget", 0.30, 2.50, note_en="Free tier.", note_th="มี free tier"),
            _m("gemini-3.8-flash", "balanced", 0.75, 3.75, recommended=True,
               note_en="Free tier; becomes $1.50/$7.50 on 1 Jan 2027.", note_th="มี free tier ราคาเป็น $1.50/$7.50 ตั้งแต่ 1 ม.ค. 2027"),
            _m("gemini-3.1-pro-preview", "best", 2.00, 12.00, note_en="Up to 200K prompt tokens.", note_th="ราคานี้สำหรับ prompt ไม่เกิน 200K token"),
            _m("gemini-4-argon", "best", 2.00, 10.00, note_en="Newest; becomes $4/$20 on 1 Dec 2026; no free tier.", note_th="รุ่นใหม่ล่าสุด ราคาเป็น $4/$20 ตั้งแต่ 1 ธ.ค. 2026 ไม่มี free tier"),
        ],
    },
    "openrouter": {
        "name": "OpenRouter", "needs_key": True, "key_hint": "sk-or-…",
        "site": "https://openrouter.ai/", "pricing_source": "https://openrouter.ai/api/v1/models",
        "price_note": {"en": "One key for many vendors. Prices come from OpenRouter's public model list and change often; the test loads the full live list.", "th": "key เดียวใช้ได้หลายเจ้า ราคาจากรายการโมเดลสาธารณะของ OpenRouter ซึ่งเปลี่ยนบ่อย ปุ่มทดสอบจะโหลดรายการทั้งหมดล่าสุด"},
        # IDs and prices verified against https://openrouter.ai/api/v1/models on 2026-11-07.
        # Not on OpenRouter at that time: gpt-6.1-luna (use openai/gpt-6-luna) and gemini-3.8-flash-lite.
        "models": [
            # Budget
            _m("nvidia/nemotron-3.5-super-vl:free", "budget", 0.0, 0.0, 1_000_000, note_en="Free variant (rate-limited).", note_th="รุ่นฟรี (จำกัดจำนวนครั้ง)"),
            _m("deepseek/deepseek-v4-flash", "budget", 0.091, 0.182, 1_048_576, note_en="Very cheap.", note_th="ถูกมาก"),
            _m("anthropic/claude-haiku-5.5", "budget", 0.10, 0.50, 1_000_000, recommended=True, note_en="Claude Haiku via OpenRouter.", note_th="Claude Haiku ผ่าน OpenRouter"),
            _m("openai/gpt-6-luna", "budget", 0.10, 0.50, 1_050_000, note_en="GPT-6 Luna (no 6.1 Luna listed).", note_th="GPT-6 Luna (ยังไม่มีรุ่น 6.1 Luna)"),
            _m("google/gemini-2.5-flash-lite", "budget", 0.10, 0.40, 1_048_576, note_en="Google retires 2.5 on its own API from 1 Dec 2026.", note_th="Google จะเลิกรุ่น 2.5 บน API ของตัวเองตั้งแต่ 1 ธ.ค. 2026"),
            _m("google/gemini-3.1-flash-lite", "budget", 0.25, 1.50, 1_048_576),
            _m("google/gemini-2.5-flash", "budget", 0.30, 2.50, 1_048_576, note_en="Google retires 2.5 on its own API from 1 Dec 2026.", note_th="Google จะเลิกรุ่น 2.5 บน API ของตัวเองตั้งแต่ 1 ธ.ค. 2026"),
            _m("google/gemini-3.5-flash-lite", "budget", 0.30, 2.50, 1_048_576),
            # Balanced
            _m("mistralai/mistral-large-4-0", "balanced", 0.70, 2.10, 1_048_576),
            _m("google/gemini-3.8-flash", "balanced", 0.825, 4.125, 1_048_576, note_en="Newest Flash (no 3.8 Flash-Lite listed).", note_th="Flash รุ่นใหม่สุด (ยังไม่มี 3.8 Flash-Lite)"),
            _m("openai/gpt-6.1-terra", "balanced", 1.00, 5.00, 1_050_000),
            _m("google/gemini-2.5-pro", "balanced", 1.25, 10.00, 1_048_576, note_en="Google retires 2.5 on its own API from 1 Dec 2026.", note_th="Google จะเลิกรุ่น 2.5 บน API ของตัวเองตั้งแต่ 1 ธ.ค. 2026"),
            _m("x-ai/grok-4.7", "balanced", 2.00, 6.00, 500_000),
            _m("anthropic/claude-sonnet-5.5", "balanced", 2.00, 10.00, 1_000_000),
            # Best
            _m("openai/gpt-6.1-sol", "best", 2.00, 10.00, 1_050_000),
            _m("google/gemini-3.1-pro-preview", "best", 2.00, 12.00, 1_048_576),
            _m("google/gemini-4-argon", "best", 2.00, 10.00, 1_048_576),
            _m("anthropic/claude-opus-5.5", "best", 4.00, 20.00, 1_000_000),
            _m("anthropic/claude-fable-5.1", "best", 10.00, 50.00, 1_000_000),
            _m("openai/gpt-6-astra", "best", 10.00, 50.00, 1_050_000),
        ],
    },
    "ollama": {
        "name": "Ollama (on this computer)", "needs_key": False, "key_hint": "",
        "site": "https://ollama.com/library", "pricing_source": "https://ollama.com/library",
        "price_note": {"en": "Free: runs on your own hardware. Install Ollama and `ollama pull <model>` first.", "th": "ฟรี ใช้เครื่องของคุณเอง ต้องติดตั้ง Ollama และสั่ง ollama pull <ชื่อโมเดล> ก่อน"},
        "default_base_url": "http://127.0.0.1:11434",
        "models": [
            _m("qwen3:8b", "budget", 0.0, 0.0, recommended=True, note_en="Popular multilingual 8B.", note_th="รุ่น 8B ยอดนิยม รองรับหลายภาษา"),
            _m("gemma4:12b", "balanced", 0.0, 0.0),
            _m("qwen3.5:9b", "balanced", 0.0, 0.0),
            _m("llama3.1:8b", "budget", 0.0, 0.0),
            _m("gpt-oss:20b", "best", 0.0, 0.0, note_en="Needs a strong GPU / lots of RAM.", note_th="ต้องใช้ GPU/RAM สูง"),
            _m("deepseek-r1:8b", "balanced", 0.0, 0.0, note_en="Reasoning model.", note_th="โมเดลเน้นการให้เหตุผล"),
        ],
    },
}


def _mask(key: str) -> str:
    return f"••••{key[-4:]}" if key else ""


class ProviderSettings:
    """Thread-safe local settings file. Never exposes stored keys through ``public()``."""

    def __init__(self, path: Path | None = None, opener=urlopen):
        env = os.environ.get("QAW_SETTINGS_PATH")
        self.path = Path(path or env or DEFAULT_PATH)
        self._lock = threading.Lock()
        self._open = opener

    # ---------- storage ----------
    def _load(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"active": None, "providers": {}}
        except (OSError, ValueError):
            raise EngineError("settings_unreadable", "The local settings file could not be read.", 500)
        if not isinstance(data, dict) or not isinstance(data.get("providers", {}), dict):
            raise EngineError("settings_unreadable", "The local settings file has an unexpected shape.", 500)
        data.setdefault("active", None)
        data.setdefault("providers", {})
        return data

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".settings-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            try:
                os.chmod(tmp, 0o600)  # best effort; Windows ACLs are inherited from the folder
            except OSError:
                pass
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    # ---------- views ----------
    def public(self) -> dict:
        with self._lock:
            data = self._load()
        configured = {}
        for pid, spec in PROVIDERS.items():
            saved = data["providers"].get(pid, {})
            key = saved.get("api_key", "")
            configured[pid] = {
                "has_key": bool(key), "key_hint": _mask(key), "model": saved.get("model") or "",
                "base_url": saved.get("base_url") or spec.get("default_base_url", ""),
                "ready": (bool(key) or not spec["needs_key"]) and bool(saved.get("model")),
            }
        return {"price_checked": PRICE_CHECKED, "active": data.get("active"), "configured": configured,
                "providers": [{"id": pid, **{k: v for k, v in spec.items()}} for pid, spec in PROVIDERS.items()],
                "used_by_live_rooms": False, "storage": "local_file"}

    # ---------- validation ----------
    @staticmethod
    def _provider(pid) -> dict:
        if not isinstance(pid, str) or pid not in PROVIDERS:
            raise EngineError("unknown_provider", "Choose one of the listed providers.")
        return PROVIDERS[pid]

    @staticmethod
    def _base_url(value) -> str:
        if not isinstance(value, str) or len(value) > 100:
            raise EngineError("invalid_base_url", "Use a local Ollama address such as http://127.0.0.1:11434.")
        parts = urlsplit(value.strip())
        if parts.scheme != "http" or parts.hostname not in LOOPBACK or parts.path not in {"", "/"} or parts.query or parts.username:
            raise EngineError("invalid_base_url", "Ollama must run on this computer (http://127.0.0.1 or localhost).")
        return f"http://{parts.netloc}"

    def update(self, payload: dict) -> dict:
        pid = payload.get("provider")
        spec = self._provider(pid)
        with self._lock:
            data = self._load()
            saved = dict(data["providers"].get(pid, {}))
            if "api_key" in payload:
                key = payload["api_key"]
                if not spec["needs_key"]:
                    raise EngineError("key_not_used", "This provider does not use an API key.")
                if not isinstance(key, str) or not KEY.fullmatch(key.strip()):
                    raise EngineError("invalid_api_key", "Paste the API key as one line of 8–400 visible characters.")
                saved["api_key"] = key.strip()
            if "model" in payload:
                model = payload["model"]
                if not isinstance(model, str) or not MODEL_ID.fullmatch(model.strip()):
                    raise EngineError("invalid_model", "Use a model ID of letters, digits and . _ : / @ + - only.")
                saved["model"] = model.strip()
            if "base_url" in payload:
                if pid != "ollama":
                    raise EngineError("invalid_base_url", "Only Ollama accepts a custom local address.")
                saved["base_url"] = self._base_url(payload["base_url"])
            data["providers"][pid] = saved
            if payload.get("active") is True:
                data["active"] = pid
            elif payload.get("active") is False and data.get("active") == pid:
                data["active"] = None
            elif "active" in payload and not isinstance(payload["active"], bool):
                raise EngineError("invalid_active", "active must be true or false.")
            self._save(data)
        return self.public()

    def clear(self, payload: dict) -> dict:
        pid = payload.get("provider")
        self._provider(pid)
        with self._lock:
            data = self._load()
            data["providers"].pop(pid, None)
            if data.get("active") == pid:
                data["active"] = None
            self._save(data)
        return self.public()

    # ---------- connection test (free endpoints only) ----------
    def _request(self, pid: str, saved: dict) -> Request:
        key = saved.get("api_key", "")
        if PROVIDERS[pid]["needs_key"] and not key:
            raise EngineError("missing_api_key", "Save an API key before testing.", 409)
        if pid == "anthropic":
            return Request("https://api.anthropic.com/v1/models?limit=1000", headers={"x-api-key": key, "anthropic-version": "2026-10-21"})
        if pid == "openai":
            return Request("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"})
        if pid == "gemini":
            return Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000", headers={"x-goog-api-key": key})
        if pid == "typhoon":
            return Request("https://api.opentyphoon.ai/v1/models", headers={"Authorization": f"Bearer {key}"})
        if pid == "openrouter":
            return Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"})
        base = self._base_url(saved.get("base_url") or PROVIDERS["ollama"]["default_base_url"])
        return Request(f"{base}/api/tags")

    def _get_json(self, request: Request):
        request.add_header("User-Agent", "qa-war-room-local-settings")
        with self._open(request, timeout=10) as response:
            return json.loads(response.read(4_000_000).decode("utf-8"))

    @staticmethod
    def _model_ids(pid: str, body) -> list[str]:
        if isinstance(body, list):  # Typhoon returns a bare JSON array of model objects
            return [m.get("id", "") for m in body if isinstance(m, dict)]
        if not isinstance(body, dict):
            return []
        if pid == "gemini":
            return [m.get("name", "").removeprefix("models/") for m in body.get("models", []) if isinstance(m, dict)]
        if pid == "ollama":
            return [m.get("name", "") for m in body.get("models", []) if isinstance(m, dict)]
        return [m.get("id", "") for m in body.get("data", []) if isinstance(m, dict)]

    def test(self, payload: dict) -> dict:
        pid = payload.get("provider")
        self._provider(pid)
        with self._lock:
            saved = dict(self._load()["providers"].get(pid, {}))
        request = self._request(pid, saved)
        result = {"provider": pid, "ok": False, "status": None, "models": [], "model_count": 0,
                  "selected_model": saved.get("model") or "", "model_found": None, "message": ""}
        try:
            body = self._get_json(request)
            result["status"] = 200
            if pid == "openrouter":  # key check passed; model list is public
                body = self._get_json(Request("https://openrouter.ai/api/v1/models"))
            ids = sorted({i for i in self._model_ids(pid, body) if i})
            result.update(ok=True, models=ids[:600], model_count=len(ids))
            if result["selected_model"] and ids:
                result["model_found"] = result["selected_model"] in ids
        except HTTPError as error:
            result["status"] = error.code
            result["message"] = {401: "key_rejected", 403: "key_forbidden", 404: "endpoint_not_found", 429: "rate_limited"}.get(error.code, "provider_error")
        except (URLError, TimeoutError, OSError):
            result["message"] = "unreachable"
        except ValueError:
            result["message"] = "unexpected_response"
        return result
