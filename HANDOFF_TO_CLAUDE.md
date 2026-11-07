# Frontend handoff to Claude

Date: 7 November 2026 (Asia/Bangkok).
Workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.
Owner instruction: pause Codex development and let Claude refine the frontend first.

## Ownership and requested outcome

Claude owns the next **frontend design and implementation** pass. Codex has paused implementation. Do not resume the proposed persistence, local-model, independent-review or research milestones as part of this assignment. The previously proposed next-step plan was not implemented.

The owner wants a modern, minimal, LINE-like conversation UI and a distinct dashboard that a nontechnical user can operate. Preserve these explicit preferences:

- Original green/white direction inspired by GPO (Government Pharmaceutical Organization), with useful Light/Dark themes. No official logo, exact certified brand colors or institutional affiliation has been established.
- Thai as the initial language, with English switching and saved preferences. Both pages, primary controls and chat summaries need coherent language treatment. Preserve original evidence text separately.
- Main journey: choose a case, set a time limit, start, watch agents interact, optionally pause/inspect/request/note, then review or download the result. Advanced options should not dominate the primary screen.
- Real API-backed updates and existing actions, not a disconnected visual mockup, prerecorded chat, fake activity or invented dashboard metrics.
- The agents are currently rule-based offline roles. A polished chat must not imply an actual LLM, independent expert or approved GMP decision.

Improve hierarchy, Thai typography, spacing, chat readability, navigation, interaction consistency, mobile behavior and empty/loading/error/partial states. You may substantially refine the frontend rather than merely recolor it, while retaining the working backend contract. "No-code user friendly" describes the user's experience; it is not a request to migrate to a no-code hosting service or expose code/configuration to end users.

## Read first

1. `AGENTS.md` and its applicable instructions; this machine's shell rule is in `C:\Users\User\.codex\RTK.md`.
2. The pause note and latest verified handoff in `STATUS.md`.
3. `GOAL.md`, `docs/LIVE_ROOM.md` and `docs/PRODUCT_SPEC.md` for the actual task and product boundaries.
4. This file and the actual frontend files below.

The current workspace is authoritative. Older sections in `HANDOFF_TO_CODEX.md` are historical. The source archive in `reports/g6-reproducibility-v1/` has creation-time progress notes; do not restore that older copy over current work.

## Working pages and source map

| Route / file | Responsibility |
|---|---|
| `http://127.0.0.1:8765/` | Main live chat; the server serves **live.html**, not index.html |
| `/dashboard.html` | Separate dashboard with actual current-process room metadata |
| `/manual.html` | Preserved manual evidence-review workflow; keep it working |
| `qa_war_room/static/live.html` | Main chat structure and controls |
| `qa_war_room/static/live.css` | Shared conversation/dashboard styles and theme tokens |
| `qa_war_room/static/live.js` | Chat state, API calls, polling, controls, record viewer and local room history |
| `qa_war_room/static/ui.js` | Shared UI copy, language/theme persistence, case/catalog presentation and some layout initialization |
| `qa_war_room/static/dashboard.html` | Dashboard structure |
| `qa_war_room/static/dashboard.js` | Live dashboard data and rendering |
| `qa_war_room/static/manual.html`, `manual.css`, `manual.js` | Existing manual UI preserved from the earlier workspace |
| `qa_war_room/static/index.html`, `styles.css`, `app.js` | Earlier UI files; these are not the main live entry point |

Both new pages load `ui.js` before their page script. Existing scripts rely on element IDs, `data-ui`/placeholder attributes and DOM relationships. Refactor HTML/CSS/JS together if changing these; do not leave stale selectors or duplicate theme/language handlers. `ui.js` currently moves strategy and pace into an advanced-options disclosure during initialization, so inspect the rendered DOM as well as source HTML.

Default implementation is static HTML/CSS/JavaScript served by Python's standard library. No frontend build step, framework package, CDN, externally hosted font or paid API is required. Preserve that workflow for this design pass. Add original local assets only when useful and respect asset/font rights.

## Scope of edits

Primary ownership: the live/dashboard/shared frontend files under `qa_war_room/static/`, plus frontend-specific tests and documentation needed to describe the final UI. Preserve the old manual workflow. Update `STATUS.md`, README and a return handoff when finished, without erasing earlier evidence.

Treat Python backend behavior, API routes/schemas, action validation, budgets, timing, source data and evaluator semantics as fixed contracts. Do not change them to make a visual design appear functional. Record a concrete backend limitation for the owner/Codex instead of silently changing it. There is no need to add persistence, models, authentication, new research cases or another application scaffold in this frontend assignment.

Do not edit or regenerate `data/`, `benchmark-data/`, `reading-pack/`, research `plans/`, manuscript conclusions, gold, review ratings, old run logs, frozen locks or existing reproducibility archives. Create new screenshot/test evidence paths rather than overwriting prior evidence. Do not inspect `.env` or credentials. No paid APIs, external messages, uploads, publication, deployment or remote Git actions are authorized by this handoff.

## Existing interaction contract

The backend is `qa_war_room/server.py` with `live_room.py` and the original `SessionEngine`. It is provided for **read-only contract inspection**, not backend editing in this pass.

| Endpoint | Input / behavior |
|---|---|
| `GET /api/health` | Local health; offline synthetic demo mode |
| `GET /api/cases` | `{cases: [...]}` public demo case metadata; eight original cases |
| `GET /api/rooms` | `{case_count, rooms, mode}`; room summaries have room_id, public case, status, message_count, records_received, elapsed_seconds |
| `POST /api/rooms` | `{case_id, auditor_role?, time_limit?, interval_ms?}`; creates a live room and returns its state |
| `GET /api/rooms/{room_id}` | Current detached room state; existing client polls about every 600 ms |
| `POST .../pause`, `.../resume`, `.../stop` | Strict empty object `{}` |
| `POST .../note` | `{text}`; bounded note, recorded verbatim, not natural-language control of an LLM |
| `POST .../request` | `{evidence_id}`; manual request requires the room to be paused |
| `GET .../report?format=markdown&lang=th` | Readable Thai report, valid for partial and terminal rooms |
| `GET .../report?format=markdown&lang=en` | Readable English report |
| `GET .../report?format=json` | Structured developer export; keep it secondary to readable reports |

Create defaults: `auditor_role: auditor-expert-01`, `time_limit: 60` seconds, `interval_ms: 650`. Allowed time is 1–300 seconds and pace 100–2000 ms. Existing UI preset values are a subset of those limits. Extra request fields, wrong types and invalid action sequences are rejected. Keep the four strategy IDs intact even if their displayed labels change.

Room state includes `room_id`, `status`, `phase`, `turns`, `max_turns`, `time_limit`, `elapsed_seconds`, `remaining_seconds`, `lead`, `reviewer`, `next_role`, `messages`, `session`, `mode`, `llm_calls`, `cost_usd` and notice. Messages contain `seq`, `role`, `kind`, `text`, `text_th`, `citations` and `elapsed_seconds`. `session` includes public case, budget, catalog, **received evidence**, engine events, decision and feedback. Inspect actual responses if a detail is needed rather than inventing fields.

Live statuses are `running`, `paused`, `completed`, `time_limit`, `stopped`, `turn_limit`, `error`. Only `completed` represents normal finalization. A partial stop/timeout must not become a green success, a forced verdict or an independent reference review. The dashboard should count actual API states and explain that they are local demo runs.

The scheduler runs on the server even if the browser is closed. Pausing stops automatic actions, but the wall-clock deadline continues. Hard limits are 80 automatic phases, 20 notes, 40 control calls, four unfinished rooms and 50 rooms per process. The original evidence-credit budget remains enforced. Preserve request idempotence and do not add client retries that create duplicate rooms or actions.

State is in memory and resets on server restart. Theme/language preferences and a small list of room IDs are browser-local; they do not establish persistent backend history. Handle missing old room IDs clearly. The dashboard has no real company data or scientific effectiveness metrics.

## Evidence and research boundaries

- Actors see only requested records. A catalog title or case metadata is not delivered evidence. The viewer must resolve attachments against received `session.evidence` only.
- Use DOM text rendering for evidence, notes and messages. Preserve escaping; do not render untrusted text with unchecked HTML.
- Gold, full unrequested records, reference rationale, construction lineage, evaluator outcomes and benchmark answers must not enter initial client state, active chat, search indexes or suggested prompts.
- Terminal authored feedback is intentionally available after completed finalization. Keep it separate and labeled as authored fixture feedback, not independent expert judgment.
- Thai presentation must not silently relabel verdicts or alter original records. Provide original English evidence in an optional detail view.
- Missing/inapplicable evidence does not automatically establish a GMP violation. A timed-out conversation does not establish either support or contradiction.
- Independent review/adjudication are **NOT_PERFORMED**, reviewed reference **NOT_LOCKED**, confirmatory results **NOT_RUN**. G6 manuscript is a local draft. Do not change those statuses or fill review forms to improve the dashboard.

## Environment and baseline evidence

At this handoff, a read-only `/api/health` check returned HTTP 200 / `status: ok` at localhost:8765. The server was left unchanged; no room was started, stopped or altered for this handoff. Recheck before assuming it is still listening. Static assets are read per request, so ordinary frontend changes normally need a browser reload, not a backend restart. Restarting would discard in-memory sessions.

Windows PowerShell; Python 3.13.15 was the last verified runtime. There is currently no `.git` metadata in this folder; do not invent a base commit or initialize/push a repository as part of the design task. Prefix shell commands with `rtk` as required locally.

Prior accepted baseline, **not rerun during this pause/handoff**:

- Source: 185 tests passed in 116.661 seconds, `runs/g6-and-ui-tests-final.txt`.
- Extracted reproduction: 185 tests passed in 111.003 seconds, `runs/g6-rehearsal-v1/tests.txt`; full rehearsal PASS in REHEARSAL.json.
- `runs/G6-VALIDATION.json`: previous aggregate engineering evidence, not a claim about your future edits. Do not overwrite it.
- Browser evidence: `runs/g6-browser-final.json` and `runs/g6-final-*.png`. Completed and timed-out real demo rooms, both languages/themes, readable report, desktop 1440×960/mobile 390×844 were checked in the prior session. These are historical screenshots, not acceptance of a new UI.
- Native/G3/G4/G5 hashes and frozen runs remain unchanged. `reports/g6-reproducibility-v1/` is immutable; frontend changes make a new source revision, not grounds to repair that archive in place.

## Verification and delivery

Use the existing server if healthy. If it is absent, start from the project root:

```powershell
rtk proxy py -3 -m qa_war_room --port 8765
```

Relevant checks, followed by the full regression suite when the design is ready:

```powershell
rtk proxy node --check qa_war_room/static/live.js
rtk proxy node --check qa_war_room/static/ui.js
rtk proxy node --check qa_war_room/static/dashboard.js
rtk proxy py -3 -m unittest discover -s tests -p test_live_room.py -v
rtk proxy py -3 -m unittest discover -s tests -p test_http.py -v
rtk proxy py -3 -W error::ResourceWarning -m unittest discover -s tests -v
```

Node is optional syntax-check tooling, not a runtime/build dependency. Existing HTTP tests include a title/marker check for the main page; if copy is intentionally redesigned, update only relevant UI assertions with an explanation, never weaken backend or isolation tests merely to pass.

Verify the actual browser UI: both pages, Thai/English, Light/Dark and preference persistence; desktop/mobile with no horizontal overflow; keyboard focus, dialog closure, contrast and reduced motion; real start/live updates/pause/resume/stop/note/record/manual request/completion/timeout; partial and completed readable export; actual dashboard counts; empty/loading/error/stale-room states; manual desk; console/network errors. When browser tools are unavailable, label visual checks NOT_RUN instead of inventing results. Do not add mirrored cosmetic tests; test changed interactions and meaningful failure paths.

Complete local reversible frontend work without repeatedly asking permission for routine choices. Return a concrete implementation with current screenshots and test evidence. Update `STATUS.md` and create **`HANDOFF_BACK_TO_CODEX.md`** with changed files, any frontend-only contract assumptions, exact commands/results, known limits and remaining backend requests. Maintain the owner's Codex pause; returning a handoff does not authorize automatic model/backend/research development.
