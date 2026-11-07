# Handoff back to Codex / ChatGPT

Date: 7 November 2026 (Asia/Bangkok). Author: Claude (Claude Code desktop).
Workspace: `C:\Users\User\Desktop\myProject\qa-war-room` (no `.git`; nothing committed, pushed, published or deployed).
Read with: `AGENTS.md`, `STATUS.md` (top sections are newest), `docs/DECISIONS.md` (D19–D21), `docs/LIVE_ROOM.md`, `docs/AGENT_PERSONAS.md`.

The owner now hands the project back for **research continuation** (see `PROMPT_FOR_CODEX_TH.md`). Everything below is engineering state; no scientific result, independent review or reviewed reference was produced in Claude's pass.

## 1. What Claude delivered

### Frontend (live chat `/`, dashboard `/dashboard.html`)
- Rebuilt `live.html`, `live.css`, `live.js`, `ui.js`, `dashboard.html`, `dashboard.js` as readable static HTML/CSS/JS on the existing API (originals backed up in `runs/claude-frontend-v1/original-static/`). `/manual.html` untouched.
- One-screen flow: choose one of 8 cases → time (1/2/5 min or custom 1–300 s) → sticky Start. Strategy (same four IDs) and pace under "More options".
- LINE-style room: real polling of `GET /api/rooms/{id}` (700 ms, GET-only backoff, POSTs never retried), pause/resume, confirmed stop, verbatim notes, manual request while paused, received-record viewer only, TH/EN Markdown + JSON downloads. Time-limit/stop/round-limit render as **unfinished work** with no verdict and no reference.
- Dashboard: only `/api/rooms` + `/api/cases` counts; no invented scores.
- Thai default, English, Light/Dark (keys `qawr-language-v1`, `qawr-theme-v1`), desktop/mobile, reduced motion, contrast ≥ 4.5:1 on checked small text.
- Original illustrated **fictional characters** (Phum, Uncle Chai, Fon, Mind) for the four simulated roles, document-type SVG icons (`static/characters/`, `static/docs/`, generator `scripts/make_ui_svgs.py`).
- Per-character **display-only voice** from `static/personas.js` ("system prompt" style specs + deterministic templates). Facts are copied verbatim from backend fields; system wording is one click away; downloaded reports keep system wording. Details: `docs/AGENT_PERSONAS.md`.
- v3 minimal refinement (Impeccable distill pass): no decorative gradients/blur/halos/eyebrows, header avatar stack, details panel closed by default, single place for end-of-room actions.

### AI settings (owner-approved backend addition, DECISIONS D21)
- `qa_war_room/provider_settings.py`; routes `GET /api/settings`, `POST /api/settings`, `POST /api/settings/clear`, `POST /api/settings/test` in `server.py` (strict fields; existing host/origin/body limits). `create_server(..., settings_path=None)`; env `QAW_SETTINGS_PATH` overrides.
- `static/settings.html` + `settings.js`, nav link on every page.
- Providers: Typhoon, Anthropic, OpenAI, Google Gemini, OpenRouter, Ollama (loopback only). 44 curated models with USD/1M in/out and context where verified (price snapshot 2026-11-07; sources in `PROVIDERS[*].pricing_source`). OpenRouter's 20 IDs were re-checked against its live list (0 mismatches); `gpt-6.1-luna` and `gemini-3.8-flash-lite` did not exist there.
- Keys live only in `.qawr/provider-settings.json` (git-ignored), are never returned to the browser (masked last 4), and the key field is cleared after save. "Test" calls only free endpoints (model lists; OpenRouter `/api/v1/key`; Ollama `/api/tags`). Provider error bodies are not echoed.
- **Live rooms do not use these settings.** `llm_calls` stays 0; D07 (no paid inference in room runs) still holds.

### Owner key check
- Owner entered real Typhoon and OpenRouter keys (Claude never saw them; masked `••••qzos`, `••••05f3`). OpenRouter key verified (200, 460 models). Typhoon `/v1/models` is public, so the owner approved **one** chat completion: `typhoon-v2.5-30b-a3b-instruct`, max_tokens 16 → HTTP 200, reply "สวัสดี", 30 tokens. Run from a scratch script, not app code. This is the only model call made in Claude's pass.
- Bug found and fixed during that check: Typhoon returns a bare JSON array for `/v1/models`; `_model_ids` now handles it (regression test added).

## 2. Files changed / added

| Area | Files |
|---|---|
| Frontend changed | `qa_war_room/static/live.html`, `live.css`, `live.js`, `ui.js`, `dashboard.html`, `dashboard.js` |
| Frontend added | `static/personas.js`, `static/settings.html`, `static/settings.js`, `static/characters/*.svg` (5), `static/docs/*.svg` (9) |
| Backend added/changed | `qa_war_room/provider_settings.py` (new), `qa_war_room/server.py` (settings routes, `settings_path`) |
| Tests | `tests/test_provider_settings.py` (new, 10 tests, fake opener, no network); existing tests unchanged |
| Tooling | `scripts/ui_browser_check.mjs` (Chrome/Edge DevTools browser acceptance, Node ≥ 22, no packages), `scripts/make_ui_svgs.py` |
| Docs | `docs/AGENT_PERSONAS.md` (new), `docs/DECISIONS.md` (D21), `docs/LIVE_ROOM.md`, `README.md`, `STATUS.md`, this file, `PROMPT_FOR_CODEX_TH.md` (new) |
| Config | `.gitignore` (+ `.qawr/`) |
| Evidence | `runs/claude-frontend-v1/` (screens, `browser-check.json/.txt`, test logs, original static backup) |

Not touched: `data/`, `benchmark-data/`, `reading-pack/`, `plans/`, manuscript sources/conclusions, gold, reviewer forms, frozen locks, earlier `runs/` folders, `reports/g6-reproducibility-v1/`, `live_room.py`, `engine.py`, evaluators, budgets.

## 3. Verification actually performed (latest runs)

| Check | Result |
|---|---|
| `node --check` live.js, ui.js, dashboard.js, personas.js, settings.js | OK |
| Full suite `py -3 -W error::ResourceWarning -m unittest discover -s tests` | **195 OK in 131.506 s**, exit 0 (185 baseline + 10 settings tests), final run after all edits; log `runs/claude-frontend-v1/test-full-suite.txt` |
| `test_live_room.py` / `test_http.py` | 17 OK / 9 OK |
| Browser acceptance `node scripts/ui_browser_check.mjs --base http://127.0.0.1:8766` | **96/96 PASS**, 0 console problems (TH/EN × light/dark × 1440×900/390×844; completion, timeout, pause/resume, note, manual request, record viewer, downloads, stop, stale room, blocked-API errors, dashboard counts = API, persona voices keep every record ID, settings page, manual desk) |
| Impeccable design detector | only typing-indicator dots flagged (kept: shown only while a room runs) |

Earlier note: one full-suite run executed concurrently with the browser check hit `ConnectionAbortedError [WinError 10053]` in `test_http.test_body_size_type_and_malformed_json_rejected`; standalone and later solo runs passed (`runs/claude-frontend-v1/test-full-suite-run1-concurrent.txt`). Likely a Windows socket race when the server rejects a body early.

Not performed: screen-reader testing, Safari/Firefox, real devices, human usability study, any check against official GPO brand assets (none used or claimed).

## 4. Runtime state you will find

- Port **8765**: the server process started before the settings routes existed. Claude was not permitted to stop it. Restart it to serve `/settings.html` and `/api/settings` there: `py -3 -m qa_war_room --port 8765` (in-memory rooms are lost on restart).
- Port **8766**: a test server started by Claude with the current code; may still be running. Stop it when no longer needed.
- `.qawr/provider-settings.json` contains the owner's real Typhoon and OpenRouter keys. Do not print, copy, upload, archive or include it in reproducibility bundles. Read it only through `ProviderSettings`.

## 5. Known limitations

- Persona voice parses current backend English templates (`live_room.py`) and Thai output (`ui_language.py`); if those strings change, bubbles fall back to system wording.
- Room history in the sidebar is per-browser localStorage (12 IDs); rooms themselves are in-memory.
- Curated prices are a dated snapshot; Typhoon prices were not published on the docs pages checked; Gemini prices change on 1 Dec 2026 / 1 Jan 2027 (noted in UI).
- `ProviderSettings` file permissions rely on Windows folder ACLs (`chmod 600` is best effort).
- The settings test endpoint makes outbound HTTPS requests when the owner clicks Test; nothing else does.

## 6. Requests / suggestions for the next backend and research work

1. **Model adapter (only when the owner authorises model work and a budget):** read the active provider/model from `ProviderSettings`; enforce `QAW_MAX_CALLS_PER_RUN` / `QAW_MAX_COST_PER_RUN` (see `.env.example`) with reservation-before-call like `native_runner.py`; log provider, model ID, prompt/version hash, token usage and cost per call; keep the existing observation/gold isolation so the model only sees requested records; refuse on missing budget.
2. **Structured message fields** (`record_id`, `revision`, `date`, `cost`, `verdict`, `rationale`, `rationale_th`) so the UI stops parsing English templates.
3. **Persona source of truth server-side** if persona voice should appear in reports; treat voice as a research variable only under an explicit protocol.
4. **Room capacity and metadata in `/api/rooms`** (`max_rooms`, `max_running`, `created_at`, `time_limit`, `auditor_role`, `turns`) and an archive/delete endpoint for the 50-room cap.
5. **Flaky Windows socket test** above: drain the body before rejecting, or tolerate `ConnectionAbortedError` on Windows.
6. Research gates are unchanged: independent review/adjudication **NOT_PERFORMED**, reviewed reference **NOT_LOCKED**, confirmatory results **NOT_RUN**, manuscript **LOCAL_DRAFT**.

## 7. Reproduce

```powershell
py -3 -m qa_war_room --port 8765
py -3 scripts/make_ui_svgs.py
node --check qa_war_room/static/live.js
node --check qa_war_room/static/settings.js
py -3 -m unittest discover -s tests -p test_live_room.py -v
py -3 -m unittest discover -s tests -p test_provider_settings.py -v
py -3 -W error::ResourceWarning -m unittest discover -s tests -v
node scripts/ui_browser_check.mjs --out runs/<new-folder>
```

The local RTK rule prefixes these with `rtk proxy` for Codex; Claude ran them directly. `ui_browser_check.mjs` creates about 6 in-memory demo rooms per run on the target server.
