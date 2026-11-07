# Live conversation and local dashboard

Status: original synthetic offline product workflow. No LLM, paid API, human expertise or real GMP approval is represented by this interface. This is a separately named product increment, not an integration of G4/G5 research cases into the browser.

## Open and use

Run `py -3 -m qa_war_room --port 8765` from the project root, then open `http://127.0.0.1:8765/` for the conversation or `/dashboard.html` for the overview. The main flow is choose a case, set a time limit and start. Optional strategy and pace live under conversation options. The previous manual workflow is preserved at `/manual.html`.

Thai is the initial UI language; English and Light/Dark preferences persist locally. The palette uses original green/white tokens inspired by the owner's requested GPO direction; no official logo, certified brand HEX or organizational affiliation is claimed. No fonts, images or scripts are fetched from a CDN. The dashboard shows actual current-server room counts, not model performance or approval rates.

Frontend v2 (7 November 2026) adds fictional illustrated characters and display-only persona voices for the four roles; see [AGENT_PERSONAS.md](AGENT_PERSONAS.md). They do not change the backend workflow, evidence access, reports or evaluation.

## Actual interaction

`live_room.py` coordinates a background process over the existing `SessionEngine`: an investigator proposes a request, the owning Manufacturing/Quality role delivers the real requested record or availability response, and an evidence reviewer checks the shared acquired facts. When a conclusion is proposed, the reviewer may challenge it and request additional material. Finalization uses the observed-data assessment through the normal decision engine; only then does the authored terminal debrief become available.

The selected investigator strategy is not an unchanged native benchmark policy: the live workflow adds a rule-based checker. Treat its transcript as a product demonstration, not a G5 baseline result. All agents are transparent deterministic roles. Messages describe executed or explicitly proposed actions and visible-record checks, not a fabricated language-model conversation or hidden reasoning trace.

The server progresses without browser polling. The client polls state to display it. Time limits are 1–300 seconds; monotonic wall time includes pauses. Per-turn delay is 100–2000 ms, default 650 ms. At most 80 automatic phases, 20 operator notes, 40 control calls, four simultaneously unfinished rooms and 50 rooms per server process are allowed. The underlying evidence budget remains enforced by the original engine. Session data is in memory and resets on server restart.

Pause stops automatic actions; resume continues if time remains. Manual record requests require pause and preserve normal credit/idempotence rules. Notes are untrusted recorded text; they do not become instructions that override policies, budgets or evidence access. Stop/deadline/turn cap preserve a partial run without forcing a verdict or reading gold. The browser never simulates success just because the clock ended.

## Thai presentation and readable records

`ui_language.py` contains authored Thai versions of workflow messages and known structured assessment phrases. It is a presentation layer, not a paid translation provider, new evaluator or independent pharmaceutical judgment. English originals remain in raw records and transcript fields. Typed notes are preserved exactly. Catalog/type translations and case-claim rendering use public metadata, not target labels or hidden records.

The record viewer shows facts from an acquired record as labeled rows, with the English original under an expandable section. It does not show unrequested source content. Chat attachments resolve only delivered record IDs. Interface text and evidence/notes are rendered with DOM text nodes; source text cannot inject markup or execute scripts. Some original source terminology remains English to preserve traceability.

## Export and APIs

The primary download is readable Markdown, with Thai/English selection, the conversation and received original evidence. JSON remains available to developers. Exports explicitly retain a partial state if no final decision exists.

| Route | Behavior |
|---|---|
| `GET /api/rooms` | Current-process public case/room summary; no gold, record content or semantic score |
| `POST /api/rooms` | Start a bounded live room from case ID and optional strategy/time/pace |
| `GET /api/rooms/{room_id}` | Current detached state and messages |
| `POST .../pause`, `.../resume`, `.../stop` | Strict empty-body control actions |
| `POST .../note` | Record a bounded operator note |
| `POST .../request` | Request an evidence ID while paused |
| `GET .../report?format=markdown&lang=th` | Readable partial or terminal conversation report |
| `GET .../report?format=json` | Structured raw conversation export |

Existing localhost host/origin, body-size and static-file restrictions remain. No production authentication, durable audit trail, regulated signature, external integration or human-use outcome is supplied. Runtime and reference boundaries remain architectural, not a sandbox against the local repository owner reading files.

## Acceptance evidence

`tests/test_live_room.py` covers all eight cases, gold-free active phases, record/citation provenance, deadline-before-closeout, pause/resume, stop/turn caps, bounded notes/control/concurrency, detached states, shortcut challenge, manual-request accounting, scheduler progress without polling, original route controls, public dashboard metadata and readable Thai partial export. Browser acceptance additionally checks actual completed and timed runs, note submission, record reading, both themes/languages, dashboard counts, mobile overflow and console errors. Current dated results and artifact paths are in STATUS.md; this guide alone is not evidence that a browser test ran.
