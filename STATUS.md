# Status — G6 local manuscript/reproducibility and bilingual live UI

## Professional README and first public push — 7 November 2026 (latest)

Owner asked for an English-only professional README with a logo and diagrams, pushed to `main` of https://github.com/siriponsri/QA-War-Room (public). New `README.md`; previous README preserved as `docs/RESEARCH_GUIDE.md` (links re-pointed); original logo and light/dark architecture and room-flow SVGs in `docs/assets/` from `scripts/make_readme_assets.py`; three screenshots copied there from `runs/claude-frontend-v1/screens/`. README rendered through the GitHub Markdown API and checked visually; all 30 relative links resolve. Push scope: files not excluded by `.gitignore` (no `.qawr/` keys, `.env`, runs, reports, benchmark data, derived data or PDFs); demo cases with their demo evaluator files and the research-case generator code are public by design.

## Handed back for research — 7 November 2026

Claude's frontend and AI-settings pass is complete. Consolidated handoff: **[HANDOFF_BACK_TO_CODEX.md](HANDOFF_BACK_TO_CODEX.md)**. Ready-to-paste Thai prompt for ChatGPT/Codex research continuation: **[PROMPT_FOR_CODEX_TH.md](PROMPT_FOR_CODEX_TH.md)** (owner fills in the API budget; blank = no paid calls). Research gates unchanged: independent review NOT_PERFORMED, reference NOT_LOCKED, confirmatory results NOT_RUN. Restart the port-8765 server before continuing; `.qawr/provider-settings.json` holds real owner keys and must never be printed or archived.

## AI settings page — 7 November 2026 (latest)

Owner chose: settings + connection test only, keys in a local server file, providers Typhoon / Anthropic / OpenAI / Google Gemini / OpenRouter / Ollama (DECISIONS D21). **Live rooms still do not use any model** (`llm_calls: 0`, D07 unchanged). No key was entered or saved by Claude; no paid call was made.

- New `/settings.html` (+ `settings.js`, styles in `live.css`, nav link on every page): provider list with status, masked saved key, password field cleared after save, model list grouped Budget / Balanced / Best with USD per 1M tokens in/out and context where verified, "other model ID" with the live list from the last test, default-provider switch, Test connection, Remove (two-click).
- New backend `qa_war_room/provider_settings.py` and routes `GET /api/settings`, `POST /api/settings`, `/api/settings/clear`, `/api/settings/test` (strict fields, existing host/origin/body checks). Keys are written to `.qawr/provider-settings.json` (added to `.gitignore`), never returned. Tests call only fixed free endpoints: Anthropic/OpenAI/Gemini/Typhoon model lists, OpenRouter `/api/v1/key` + public model list, Ollama `/api/tags` on loopback only. Error bodies are not echoed.
- OpenRouter list expanded on owner request to 20 verified IDs (Claude Haiku/Sonnet/Opus/Fable, GPT-6 Luna, GPT-6.1 Terra/Sol, GPT-6 Astra, Gemini 2.5 Flash-Lite/Flash/Pro, 3.1 Flash-Lite, 3.5 Flash-Lite, 3.8 Flash, 3.1 Pro, 4 Argon, plus DeepSeek, Mistral, Grok, a free Nemotron); every ID and price re-checked against the live OpenRouter list (0 mismatches). Not on OpenRouter on 2026-11-07: `gpt-6.1-luna`, `gemini-3.8-flash-lite`. Prices now show up to 3 decimals. Total curated models: 44.
- 35 curated models (initial). Sources and check date 2026-11-07: Anthropic from the bundled claude-api skill (cached 2026-10-06); OpenAI `developers.openai.com/api/docs/pricing`; Gemini `aistudio.google.com/docs/pricing` (some prices rise 1 Dec 2026 / 1 Jan 2027, noted in the UI); OpenRouter public `/api/v1/models`; Typhoon models/rate limits from `docs.opentyphoon.ai` (no prices published there, UI says so); Ollama names from `ollama.com/library` (free, local).
- Verification (actual): new `tests/test_provider_settings.py` 9 OK (fake opener, no network); full suite **194 OK in 132.495 s**; browser acceptance **96/96 PASS** against a second server on port 8766 (settings TH/EN, light/dark, desktop/mobile; Ollama test shows "unreachable" because Ollama is not installed here). Live API probe: Typhoon public model list reachable; other providers return 401 without a key, as expected.
- Owner real-key test (keys entered by the owner, never seen by Claude; masked ••••qzos / ••••05f3): OpenRouter `/api/v1/key` 200, 460 live models, selected `nvidia/nemotron-3.5-super-vl:free` found. Typhoon first returned 0 models because `/v1/models` is a bare JSON array; fixed in `_model_ids` with a regression test (settings tests now 10 OK); retest 200, 7 models, `typhoon-v2.5-30b-a3b-instruct` found. Typhoon's model list is public, so this does not prove the Typhoon key is valid; that needs one real (possibly billed) completion. **Owner then approved one call:** `POST /v1/chat/completions` to `typhoon-v2.5-30b-a3b-instruct`, max_tokens 16 → HTTP 200, reply “สวัสดี”, usage 25 prompt + 5 completion = 30 tokens. The Typhoon key is confirmed. This single call was a key check run from a scratch script, not part of the app; live rooms still make no model calls.
- **Action needed:** the server on port 8765 was started before these routes exist; Claude was not permitted to stop that process. Restart it (`py -3 -m qa_war_room --port 8765`) to get the settings page there; restarting clears in-memory demo rooms. A test server may still be running on port 8766.

## Minimal refinement (v3) — 7 November 2026 (latest, after the v2 pass below)

Owner asked for a more modern and minimal UI (`/impeccable` distill pass, Operate mode). Same functions, characters, voices and API contract; frontend files only (`live.html`, `live.css`, `live.js`, `ui.js`, `dashboard.html`).

- Removed decoration: eyebrow labels, gradient text/buttons, glass blur, mesh/dot chat background, glow halos, 4px side accent border, glyph speech bubbles, hover lifts, per-message entrance animation. One authored motion remains: the speaking character's mouth; pulse only on a genuinely running status badge.
- Simplified structure: team stage row → header avatar stack (group-chat style); details panel closed by default (opened from the paused hint, "View evidence" or ⓘ); download/new-room actions shown once (dock); "System wording" link appears on hover/focus; note help shows when the composer is focused; neutral message meta; one type scale; KPI cards → one divided strip; dashboard hero → plain heading row. Browser selection/caret/scrollbar/accent colours themed.
- Thai headings shortened so they no longer break mid-phrase.

Verification (actual): `node --check` OK (4 files); `test_live_room.py` 17 OK; `test_http.py` 9 OK; browser acceptance **87/87 PASS** (adds "details closed by default" and "paused hint opens evidence panel"); Impeccable detector: only the typing-indicator dots remain flagged, kept deliberately because they appear only while a room is running. Full 185-test suite not rerun for this CSS/markup-only pass (last full run: 185 OK, below). Screens in `runs/claude-frontend-v1/screens/` now show v3.

## Claude frontend pass — 7 November 2026

**Frontend v2 implemented and browser-verified; returned to Codex in [HANDOFF_BACK_TO_CODEX.md](HANDOFF_BACK_TO_CODEX.md). Codex remains PAUSED pending owner direction.** No backend/API, dataset, gold, budget, evaluator, archive or research file was changed; no paid API, push, deploy or external message.

- `/` (live.html): one-screen case → time → Start flow with sticky start bar; LINE-style chat with original illustrated fictional characters (Phum / ลุงชัย / ฝน / มายด์), "who is talking" stage, typing indicator from the server's next phase, document-type SVG attachments, received-record viewer, pause/resume, confirmed stop, verbatim notes, manual request while paused, TH/EN Markdown + JSON downloads, and clear loading/error/paused/unfinished/stale states. Time-limit/stop/round-limit stay unfinished with no verdict or reference.
- `/dashboard.html`: real counts from `/api/rooms` and `/api/cases` only (KPIs, status mix, filterable rooms, per-case usage), 5 s auto-refresh, error/empty states.
- Per-character response style ("system prompt") in `static/personas.js`, applied as a **display-only** deterministic voice; facts copied verbatim, system wording one click away, reports unchanged. Proposed prompts for a future LLM backend: [AGENT_PERSONAS.md](docs/AGENT_PERSONAS.md) — NOT wired.
- Thai default, English switch, Light/Dark, both remembered; mobile 390×844 and desktop 1440×900 without horizontal overflow; reduced motion respected; small-text contrast ≥ 4.5:1 on the setup screen in both themes.
- `/manual.html` unchanged and loading.

Verification (actual, final run after all edits): `node --check` OK for live.js/ui.js/dashboard.js/personas.js; `test_live_room.py` 17 OK; `test_http.py` 9 OK; full suite with ResourceWarning as error **185 OK in 85.357 s**; browser acceptance `node scripts/ui_browser_check.mjs` **85/85 PASS** with 0 console problems. One earlier full-suite run executed concurrently with the browser check hit a Windows `ConnectionAbortedError` in `test_http` (kept as `test-full-suite-run1-concurrent.txt`); standalone and later solo runs passed.

Evidence folder: `runs/claude-frontend-v1/` (28 screenshots, `browser-check.json`, test logs, original static backups). Independent review NOT_PERFORMED, reviewed reference NOT_LOCKED, scientific results NOT_RUN — unchanged.

## Owner pause and frontend transfer — 7 November 2026

**Codex implementation is PAUSED at the owner's explicit request.** The owner will have Claude refine the frontend first. This session only prepared transfer documents and performed read-only inspection/health checking; it did not change application code, run a new test suite, restart the server, start/stop rooms, rebuild archives or advance research/model work.

Read **[HANDOFF_TO_CLAUDE.md](HANDOFF_TO_CLAUDE.md)** for frontend ownership, design preferences, source map, API contract, safety/data boundaries and acceptance checks. The ready-to-paste Thai owner prompt is **[PROMPT_FOR_CLAUDE_TH.md](PROMPT_FOR_CLAUDE_TH.md)**. Claude should return **HANDOFF_BACK_TO_CODEX.md** and update this status after its actual work. That return does not itself resume Codex development; wait for owner direction.

Scope transferred: main LINE-style chat and distinct modern minimal dashboard, no-code-friendly flow, GPO-inspired original green/white, Light/Dark and Thai/English. Preserve real API-backed workflow and the manual desk. Backend, datasets/gold, budgets/evaluation, manuscript claims and frozen research artifacts are outside this frontend pass. Persistence, local-model integration and actual independent review remain proposed/uncompleted next work; do not mistake the earlier plan for authorization to start them now.

At handoff a read-only `GET http://127.0.0.1:8765/api/health` returned `status: ok`, version 0.1.0, offline_scripted_synthetic_demo. The listener was left unchanged; recheck before assuming it is still running. Historical test evidence below remains the last accepted baseline (185 source tests and 185 extracted tests), not newly rerun pause-session results. Older G6 audit hashes refer to their own frozen evidence snapshot; these new handoff/document changes do not repair or overwrite that evidence.

Independent review/adjudication remain NOT_PERFORMED, reviewed reference NOT_LOCKED, scientific results NOT_RUN, paid API spend USD 0. All previously verified engineering work and historical notes below are preserved.

Updated 7 November 2026 (Asia/Bangkok). Active workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.

## Current handoff

The requested **G6 local/offline manuscript and reproducibility preparation** and the separately requested **modern minimal LINE-style chat/dashboard, GPO-inspired green palette, Light/Dark and Thai/English** are implemented and verified. Engineering status: **READY_FOR_REVIEW**. Independent reference review and adjudication: **NOT_PERFORMED**. Reviewed reference: **NOT_LOCKED**. Confirmatory scientific results: **NOT_RUN**. No paid API, LLM/provider inference, expert rating, participant recruitment, company data, external contact, publication, push, deployment or license assignment occurred. API/model spend: **USD 0**.

The actual local server is running at **http://127.0.0.1:8765/**. Main chat: `/`; dashboard: `/dashboard.html`; preserved manual evidence desk: `/manual.html`. The server was restarted to load the new routes; old in-memory demo sessions were reset. It remains a localhost-only synthetic prototype. Current server tool session: 62359. Windows Python 3.13.15; standard-library runtime, no added dependency. No `.git` metadata exists in this source folder; file hashes identify the candidate.

## Product behavior now available

- Main page is a minimal conversation with optional room details, plain-language labels and advanced strategy/pace options tucked away. Thai is the initial language; English and theme preferences persist locally. The separate dashboard shows actual current-process room/case/status counts, not scientific scores or real CAPA approvals.
- The background runner advances an investigator, Manufacturing/Quality record custodians and an evidence checker through real `SessionEngine` requests and visible-data checks until finalization, deadline, stop or hard turn cap. Browser polling displays state; it does not drive progress. These are **rule-based scripted agents**, not an LLM conversation or independent experts.
- Time limit 1–300 seconds, default 60; pause/resume/stop; max 80 automatic phases, 20 notes and 40 control actions. The wall clock continues while paused. Up to four unfinished rooms and 50 rooms per process. Original evidence credits remain enforced. A deadline/stop leaves a partial run and does not force a decision or read gold.
- Operator notes are recorded verbatim. They do not become policy instructions. Pause before requesting a record manually. Chat attachments open only received records. Facts appear as readable rows, with the English original expandable; raw JSON is not the main reading flow. The primary report download is readable Markdown in Thai/English; structured JSON remains available by API.
- GPO-inspired means an original green/white direction, with corresponding dark tokens. No exact official HEX, official logo or affiliation is claimed; no online brand lookup, licensed font copying or CDN asset was used. The live browser still uses the **eight original demo cases**; G4/G5 research cohorts are not silently integrated or relabeled.

Read [LIVE_ROOM.md](docs/LIVE_ROOM.md). Added `live_room.py`, `ui_language.py`, strict `/api/rooms` routes in `server.py`, `static/live.html`, `live.css`, `live.js`, shared `ui.js`, `dashboard.html` and `dashboard.js`. The previous UI files are preserved, including explicit manual copies. Original native/G3/G4/G5 source hash compatibility passes; the new live workflow is not presented as an unchanged G5 baseline.

## G6 writing and reproducibility

Read [G6_REPRODUCIBILITY.md](docs/G6_REPRODUCIBILITY.md). Manuscript sources: `manuscript/draft.md`, `claims.json`, `SOURCE_STATUS.md`, `PILOT_BRIEF.md`. The generated draft is **`reports/g6-reproducibility-v1/writing/MANUSCRIPT_DRAFT.md`**. It includes a concrete abstract, introduction, implemented/prospective methods, NOT_RUN confirmatory results, engineering-only exercise counts, limitations, data/code availability and incomplete author/declaration fields. The pilot brief is prospective; no participants or approvals are invented. Citations reuse the existing local bibliography snapshot; no new full-text/current-policy/regulatory verification or novelty claim was made.

`publication_evidence.py` checks locked implementation/source bytes, replays both G5 raw runs, validates summary accounting, regenerates analysis and compares deterministic metrics/outcome/table bytes before rendering. `publication_bundle.py` creates/verifies role-separated archives and rehearses a fresh extraction. `publication.py` is the CLI. All 18 rendered engineering/gate fact keys have claim mappings; the ledger is not a semantic validation of every prose statement or citation.

Canonical local package: **`reports/g6-reproducibility-v1/`**. Status **LOCAL_DRAFT**, submission_ready **false**. Four deterministic ZIPs, **130 members / 7,623,050 uncompressed bytes**:

| Archive | Boundary |
|---|---|
| `source.zip` | Developer code/tests/docs/manuscript sources and citation metadata. Construction/tests are answer-bearing developer materials, never actor retrieval. |
| `environment-inputs.zip` | Public cards/splits/PACK metadata and complete private backend records plus demo inputs. No evaluator gold, lineage or terminal results. Complete records are backend-only, not initial model context. |
| `engineering-runs.zip` | Frozen G5 matched/cap locks, raw request/response journals, summaries and cap plan. |
| `evaluator.zip` | Separate G4/demo gold, authoring lineage, saved analyses/outcomes and original confirmatory refusal. |

`writing/` contains the rendered draft, CLAIMS.json, EVIDENCE.json and local-use notice. `BUNDLE.json` pins all archive/member/writing bytes. No `.env`, credentials, real company records, reviewer identities, third-party PDFs, raw external benchmarks or caches were included. Verification rejects altered/missing/extra/cross-role files, symlinks, traversal, duplicate/case-colliding members and oversized payloads. Checksums are not signatures or proof of review. Original-code/data redistribution licensing remains an owner decision.

The package is frozen before the final session handoff: its source STATUS/HANDOFF are creation-time snapshots. This current workspace STATUS/HANDOFF supersedes those notes. Executable source/assets and the frozen G5 data/run/analysis still match the tested package; do not mutate the immutable package merely to update a progress note.

## Actual verification

| Check | Observed result |
|---|---|
| Before G6 | PASS, 147 baseline tests |
| G6 before live UI | PASS, 168 tests in 94.401 s; `runs/g6-tests-final.txt` (historical intermediate) |
| Final source suite | **PASS, 185 tests in 116.661 s**, exit 0; `runs/g6-and-ui-tests-final.txt`; 21 G6 + 17 live tests added to the 147 baseline; ResourceWarnings promoted to errors |
| Real package build/verify | PASS, 4 ZIPs / 130 members / 7,623,050 uncompressed bytes; `reports/g6-reproducibility-v1/BUNDLE.json` |
| Fresh-directory rehearsal | **PASS**, `runs/g6-rehearsal-v1/REHEARSAL.json`: replay with gold absent, then separate evaluator extraction, **185 tests in 111.003 s**, exact analysis-byte match, new confirmatory request correctly refused with exit 2 |
| Manuscript counts | Rechecked original G5 dev 16 cases / two construction families / 192 jobs / 614 transitions / 76 submissions / 116 abstentions; cap-one-action keeps 191 pending jobs; engineering only, no scientific estimates or CIs |
| Browser live run | Actual Thai conversation completed with 23 messages / 21 phases, authored fixture decision supported; pause, Thai note and received-record reading also exercised |
| Browser deadline | One-second run ended time_limit, 4 messages / 2 phases, no decision or feedback; export evaluation state NOT_EVALUATED |
| Browser dashboard | Actual current server has eight sample cases, two inspected rooms, one completed and one timed out at final capture; values are ephemeral demo process counts |
| Browser presentation | Thai/English switch and persistence, both themes and theme persistence, 1440×960 desktop and 390×844 mobile, no horizontal document overflow, no console errors/warnings in the inspected checks |
| Readable export | HTTP 200, text/markdown UTF-8, Thai conversation report; source original preserved, partial export remains partial |
| JavaScript | Node syntax checks passed for live.js, ui.js, dashboard.js; Node is verification tooling, not a runtime dependency |
| Earlier pipelines | Four native v2, three G3 v2 and G4 implementation hashes preserved; G5 verified-v2 lock loads unchanged; `runs/g6-compatibility.json` |
| Independent review/science | NOT_PERFORMED / NOT_LOCKED / NOT_RUN; unchanged G4/G5 gates |

Screenshots and structured browser evidence are under `runs/g6-final-*.png` and `runs/g6-browser-final.json`. Browser tools initially saved under `C:\Users\User\Documents\ChatGPT\QA War room`; the recorded copies are in the actual project runs folder. Aggregate evidence: `runs/G6-VALIDATION.json`. No independent software reviewer or human usability study was used.

Testing covers malformed/rehashed analysis, source/summary/lineage drift, missing/cross-boundary archive inventory, rendering/fact-map consistency, unsafe extraction paths/modes, bounded limits, gold-free active phases and replay, deadline immediately before closeout, all eight scripted cases, actual background progression, HTTP host/origin/payload restrictions, dashboard privacy and Thai partial export. Software tests do not establish pharmaceutical validity or natural-language reasoning.

## Reproduce / continue

Run in the active workspace. Prefix shell commands with `rtk proxy` per the local RTK instructions. Choose new output paths; existing archives/locks/runs are immutable.

```powershell
rtk proxy py -3 -m qa_war_room --port 8765
rtk proxy py -3 -W error::ResourceWarning -m unittest discover -s tests -v
rtk proxy py -3 -m qa_war_room.publication build --output reports/my-g6-bundle
rtk proxy py -3 -m qa_war_room.publication verify --bundle reports/my-g6-bundle
rtk proxy py -3 -m qa_war_room.publication rehearse --bundle reports/my-g6-bundle --output runs/my-g6-rehearsal
```

Rehearsal runs from extracted source using plain Python; RTK is not bundled as a dependency. The bundle reproduces the named G5 engineering runs and stdlib tests, not all downloaded native datasets/LLM experiments. A built/verified package alone is not a passed rehearsal; inspect REHEARSAL.json and actual logs.

Session tooling corrections were local and preserved existing work: an initial patch attempted delete+add on the same static path and was rejected before mutation; new live files were added separately instead. A nested shell quote and a screenshot path restriction were corrected; screenshots were saved within the browser tool's allowed root and copied. A shell-based export-link substitution was replaced with an explicit local helper and validated by an HTTP 200 readable export. None changed gold or supplied a fabricated scientific outcome.

## Next session

1. Use this current handoff. UI/G6 local preparation is complete; do not repeat it merely because an archived progress note predates final acceptance.
2. Arrange genuine blinded independent G4 ratings, intake and adjudication using the prepared packets. Do not fill forms with synthetic reviewer ratings. Implement a new versioned reviewed-reference importer only with real provenance; preserve the author draft.
3. Resolve actual jurisdiction/intended use, independently sourced sampling, reviewed pilot/sample-size assumptions, meaningful effect/guardrail margins, primary methods, model/prompt revisions and rare-event/multiplicity procedures before a scientific Stage B lock. Current refusal is intentional.
4. Have the owner review manuscript sources/full-text citations and actual authorship/funding/conflict/AI-assistance declarations; no journal-specific compliance or submission is claimed. The pilot brief needs its real setting/permissions/institutional determination before recruitment.
5. If real language-model conversations are desired later, select an actual local model/provider and assess feasibility separately. The current agents are scripted. Paid inference still requires explicit prices and budget authorization. Do not send messages, publish, assign a license or deploy automatically.


## Historical G5 handoff

Updated 7 November 2026 (Asia/Bangkok). Active workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.

## Current G5 handoff

The owner-authorized **G5 local/offline evaluation-plan and analysis-pipeline increment is implemented and verified**. Engineering status: **READY_FOR_REVIEW**. Scientific Stage B: **NOT_LOCKED / NOT_RUN**. Actual independent review: **NOT_PERFORMED**; adjudication: **NOT_PERFORMED**. G4 readiness remains unchanged. No paid API, provider/LLM inference, expert ratings, external contact, company data, publication, push or deployment occurred. API calls/model tokens/spend: **0 / 0 / USD 0**.

Read [G5_EVALUATION_PLAN.md](docs/G5_EVALUATION_PLAN.md), [the JSON draft](plans/g5-evaluation-plan-v1.json) and the G4 review materials below. G5 is a separate CLI/Python path; no new browser integration or G5 visual UI check is claimed. No dependencies were added; Windows Python **3.13.15**, standard library only. This folder currently has no `.git` metadata; reproducibility uses file hashes rather than an invented commit identifier.

### What now works

- `study_plan.py`: strict zero-cost/offline plan validation; complete public family/cohort and method × budget × repetition matrix; environment, input and implementation hashes; drift/missing-job rejection. Locking/running/replaying never opens evaluator or authoring files.
- `study_policies.py`: observation-only status shortcut, SOP catalog order, adaptive acquisition and scope/date interpretation ablation. All get equal caps/interfaces; original evidence remains unchanged. These are coauthored scripts, not humans or language models.
- `study_runner.py` / `study.py`: `lock`, `run`, `replay`, `analyze`; normalized bounded actions, no automatic repair/retry, durable hash-chained ledger, checkpoint/resume, exact source replay, writer exclusion and frozen resource limits. Runtime failures and unstarted jobs remain in the planned cohort.
- `study_metrics.py`: hand-checked FSR, supported sensitivity, decision coverage, conservative accuracy, macro F1, confusion/status/resource counts; strict pairing; item-weighted paired family bootstrap arithmetic carrying siblings/repetitions together; undefined/zero-event/degenerate interval withholding; joint guardrail arithmetic with no scientific authorization.
- `study_analysis.py`: replay first, evaluator-only gold join second; complete frozen outcome rows; descriptive method/budget and family tables, equal-family sensitivity, paired deltas and controlled-pair diagnostics; CSV/JSON/Markdown exports with audit hashes. Semantic rationale validity stays null.
- A confirmatory request fails closed with `REFUSAL.json` and exit **2**; it never creates `LOCK.json`. Current reader only supports author-draft references. Supplying arbitrary review/model hashes or margins cannot establish review or bypass the gate.

The scientific comparison, meaningful effect/guardrail margins, reviewed-release/review/adjudication/sample-size records, model revision and prompt hashes remain **null** in the prospective plan. No scientific effect, power result, p-value, confidence interval, equivalence result or safety conclusion has been generated. The scientific CSV template is blank with **NOT_RUN**. Zero observed errors are not a safety guarantee.

### Current verified artifacts

Use the **verified-v2** artifacts below. Earlier `*-final` G5 outputs are preserved historical engineering attempts, superseded after adding shared serializer/import source hashes; current code correctly refuses their old implementation locks. The G4 `manufacturing-gmp-v1-final` input pack and old native/G3/G4 implementations are unchanged.

| Artifact | Actual result |
|---|---|
| `runs/g5-tests-verified-v2.txt` | **147 tests PASS**, 22.780 seconds, exit 0; includes 31 new G5 tests and the 116-test baseline; ResourceWarnings promoted to errors |
| `runs/G5-VALIDATION-v2.json` | **PASS**, 17 checks; actual CLI commands, exit codes, source/code/output hashes, raw-log pointers and old pipeline compatibility |
| `runs/g5-engineering-lock-verified-v2/LOCK.json` | Engineering-only, original synthetic G4 dev **16 cases / 2 construction families / 192 frozen jobs** |
| `runs/g5-engineering-run-verified-v2/` | Checkpoint at 5 transitions, resume to **192 terminal jobs**, **614 actions/transitions**, no runtime failures or pending jobs; replay verified |
| `reports/g5-engineering-analysis-verified-v2/REPORT.md` | Descriptive report generated from the replayed raw run; **76 submissions / 116 abstentions**, not a model-performance result |
| `reports/g5-engineering-analysis-verified-v2/ENGINEERING_METRICS.csv` and `.json` | **12 method/budget tables**; each retains 14 primary + 2 ambiguous episodes; primary FSR denominator 10, supported denominator 4; family and pair diagnostics |
| `reports/g5-engineering-analysis-verified-v2/evaluator/outcomes.jsonl` | All **192** frozen jobs, including 168 primary and 24 ambiguity-stratum episodes; evaluator-only answer-bearing output |
| `reports/g5-engineering-analysis-verified-v2/SCIENTIFIC_TABLE_TEMPLATE.csv` | Blank estimates and intervals, **NOT_RUN** |
| `reports/g5-engineering-analysis-verified-v2/ANALYSIS.json` | Lock/run/evaluator/code and generated-output hashes; no review claim |
| `reports/g5-confirmatory-refusal-verified-v2/REFUSAL.json` | Expected refusal, exit **2**, no scientific `LOCK.json` |
| `runs/g5-cap-plan-verified-v2.json`, `runs/g5-cap-lock-verified-v2/`, `runs/g5-cap-run-verified-v2/` | Global cap **1 policy action**; **1 terminal / 191 pending**; source replay verified |
| `reports/g5-cap-analysis-verified-v2/` | All **192** jobs retained despite cap exhaustion; no success-only denominator |

Default engineering methods: `status-shortcut-v1`, `sop-catalog-v1`, `sop-adaptive-v1`, `ignore-applicability-v1`. Budgets **0/3/7 credits**, one deterministic repetition; max **16 actions/job**, **200,000 exposed source bytes/job**, **10,000 actions/run**, **10,000 jobs**, **0 retries**, USD **0**. The two dev construction families share authored scaffolding and are not established independent sites. No untouched holdout is used by this workflow.

### Exact reproduction and verification

Run in the active workspace. Use new output directories; never overwrite a frozen artifact. Prefix shell commands with `rtk proxy` on this machine as required by `C:\Users\User\.codex\RTK.md`.

```powershell
rtk proxy py -3 -W error::ResourceWarning -m unittest discover -s tests -v
rtk proxy py -3 -m qa_war_room.study lock --pack data/derived/manufacturing-gmp-v1-final --output runs/my-g5-lock
rtk proxy py -3 -m qa_war_room.study run --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run --stop-after 5
rtk proxy py -3 -m qa_war_room.study run --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run --resume
rtk proxy py -3 -m qa_war_room.study replay --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run
rtk proxy py -3 -m qa_war_room.study analyze --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --run runs/my-g5-run --output reports/my-g5-analysis
rtk proxy py -3 -m qa_war_room.study lock --mode confirmatory --pack data/derived/manufacturing-gmp-v1-final --output reports/my-g5-refusal
```

The final command's expected exit is **2**. The actual session workflow and logs are listed in `runs/G5-VALIDATION-v2.json`. `runs/validate_g5_offline_v2.py --collect-existing` rechecks preserved outputs; running that session collector without its collection option will refuse existing locks. It is an ignored local evidence helper, not the public pipeline entry point.

Coverage includes forbidden gold/authoring reads during lock/run/replay; gold tamper detection during evaluation; strict zero-cost plans and complete grouped matrices; source/serializer drift; source response forgery, torn journals and concurrent writers; mid-job resume/idempotence; global/per-job/byte caps; malformed/oversized/nonserializable actions; exception-text redaction; original evidence preservation under ablation; paired missing/duplicate units; fixed failure denominators; ambiguity/pair handling; hand-computed metrics; clustered bootstrap with repeated siblings; zero/undefined/degenerate intervals and all four guardrails. No independent software reviewer was used.

Session tooling corrections: the first evidence collector assumed the G4 manifest used `implementation_sha256`; its actual legacy key is `code_sha256`. A versioned collector also initially substituted old G4 pack/history path names while preparing G5 v2; those paths were corrected, failed logs retained and completed CLI outputs collected without modifying source data or frozen runs. A shell quoting error while generating that helper changed no project files. These were evidence-helper failures; the final product test suite and artifact checks pass. Earlier test logs (146 tests) remain historical; use the 147-test v2 log above.

### Next session: retain the scientific gates

1. Actual independent reviewers must complete the existing blinded G4 packets; intake/check, disagreement resolution and adjudication remain undone. Do not fill their forms with synthetic ratings or silently assert review completion.
2. Implement a **new versioned reviewed-reference release importer/verifier** with tests and provenance, after genuine review records exist. Preserve the author-draft release. Current confirmatory refusal is intentional.
3. Resolve intended jurisdiction/use case and independent source sampling; justify sample size and margins from reviewed development/pilot evidence. A future sensitivity simulation may use explicitly hypothetical inputs but must not masquerade as a measured pilot or power result.
4. Select/freeze the real primary methods, prompts, operating point, model revisions, repeated-run schedule, uncertainty/rare-event handling and multiplicity before held-out evaluation. Keep previously viewed diagnostics developmental.
5. Real paid inference still needs explicit provider/model, prices and spending authorization before execution. Continue useful offline work without paid calls; no permission was requested or needed for this increment.

## Historical G4 handoff — superseded by the current section above

Updated 7 November 2026 (Asia/Bangkok). Workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.

## Current G4 handoff

The requested **local/offline case-pack, evaluation-rubric and independent-review-plan deliverables are implemented and verified**. Status: **READY_FOR_REVIEW**. The scientific G4 reference gate is still pending actual independent annotation, adjudication and reference freeze. No paid API, LLM/provider inference, real company record, expert rating, external contact or pharmaceutical validation occurred.

Task/resource: `qawr-manufacturing-gmp-v1`, original synthetic nonsterile oral-solid Manufacturing GMP scenarios. Current source is a draft: candidate outcomes follow explicit fictional site SOPs, not universal GMP rules. G4 is a CLI/Python API plus readable review Markdown; it has not been integrated into the original CAPA browser UI.

Read [the case-pack guide](docs/MANUFACTURING_CASE_PACK.md), [annotation rubric](docs/templates/MFG_ANNOTATION_RUBRIC_V1.md) and [independent review plan](docs/INDEPENDENT_REVIEW_PLAN.md). For human inspection open `reports/g4-independent-review-v1-final/reviewer/INDEX.md`.

## Current case pack

- **48 cases / six construction families / six synthetic site SOP identifiers**: packaging reconciliation, blending parameters, equipment setup/change control, recurrence after training, investigation cohort and eligible operating-day effectiveness window.
- Each family has eight sibling worlds: complete anchor, decisive measure change, unavailable record, wrong scope, post-cutoff record, obsolete trained-procedure revision, unrelated context change and unclear acceptance criterion.
- Authored candidates: **12 supported, 12 contradicted, 18 insufficient**. **Six additional ambiguous cases have no unique candidate**, no resolved witness set and no draft primary eligibility. These are construction counts, not measured model or expert performance.
- **42 controlled pairs**: 30 author-rule label-changing, six preserving and six unresolved-ambiguity contrasts. Changed fact paths and linked rendering/payload-removal changes are retained outside model observations. No ambiguity is converted into an invented changed gold label.
- Two complete template/counterfactual families each in provisional train/dev/test; all eight siblings stay together. Common schema scaffolding and solo construction limit independence. This is not a confirmatory lock or six independently reviewed sites.
- Original affected batches are distinct from post-change follow-up batches. SOP approval/effectivity, implementation, training and monitoring chronology are explicit. Context records concern a different scope. Reviewers must still assess pharmaceutical plausibility and root-cause adequacy.

## Input, reference and reviewer boundaries

Canonical pack: `data/derived/manufacturing-gmp-v1-final/` (ignored by Git). public/cases.jsonl holds cards; private/records.jsonl is the environment source; public/splits.json holds construction groups; authoring/lineage.jsonl holds interventions; evaluator/gold.jsonl and pairs.jsonl hold unreviewed candidates/criterion traces. PACK.json records hashes, rule/builder versions and unreviewed state.

Input construction assigns no reference labels. The reference compiler separately applies the declared structured SOP criteria. Runtime observations expose only requested records, exact source-pointer citations and budget responses; they omit family/split/intervention/reference data. Missing/inapplicable evidence is unknown, not automatically a violation. A submitted insufficient decision differs from abstention. Gold is read only by the separate evaluator after terminal submission/source replay.

Reviewer export: `reports/g4-independent-review-v1-final/`. Provide reviewer/ and its copied identical rubric only after the owner chooses the reviewers/process. Keep owner/ local. Reviewer cases use RC aliases, full available evidence, no original source case IDs, pair orientation, authored decision or system output. The owner protocol lock pins the supplied rubric and review source manifest. Related mechanisms may still be recognizable; no perfect-blinding claim is made.

All 96 initial-rating template rows remain blank and the roster contains no actual reviewer. Intake preserves exact received bytes under hashed filenames and creates a blank adjudication template. Complete structure cannot authenticate expertise/identity/independence, modify reference labels or establish pharmaceutical validation.

## Actual verification

| Check | Observed result / artifact |
| --- | --- |
| Baseline before G4 | PASS, 89 tests |
| Final full suite | PASS, **116 tests in 23.356s**, exit 0; `runs/g4-tests-final-candidate.txt`; 27 new G4 tests plus all earlier suites |
| Final preparation | PASS, 48 original cases, six construction groups/SOPs, separate input/reference/lineage; `data/derived/manufacturing-gmp-v1-final/PACK.json` |
| Candidate construction | PASS, 12/12/18 unique supported/contradicted/insufficient candidates and six unresolved ambiguous cases; all status unreviewed |
| Controlled-pair audit | PASS, all **42** pairs match declared fact deltas, fixed within-family catalogs/claims and linked representation changes |
| Declared witness audit | PASS, all **42** unambiguous record/availability witnesses obtainable within their case budget and reproduce the declared-rule candidate; no independent minimality claim |
| Gold-free walkthrough | PASS, 48 cases and **384** source transitions; no reference reads, LLM calls or API cost; `runs/g4-walkthrough-final/SUMMARY.json` |
| Separate evaluator/replay | PASS, source responses replay; 42 coauthored candidate matches and six ambiguity abstentions. This is executable fixture consistency, not a held-out model/pharma result; EVALUATION.json and REPORT.md in the same run |
| Runtime boundary tests | PASS, only requested records, detached sessions/snapshots, scope/time unknown versus explicit failure, missing fact/type handling, byte/credit caps, unavailable cost/idempotence, exact visible citations, terminal restrictions, no network provider |
| Blinded export | PASS, 48 readable case Markdown files and JSON packets, case/Markdown hashes, alias-only source IDs and blank forms; `reports/g4-independent-review-v1-final/reviewer/` |
| Blank review intake | Correctly **INCOMPLETE**, zero attested reviewer codes and zero completed expert ratings; `reports/g4-review-intake-blank-final/CHECK.json` |
| Structural review workflow tests | PASS, invalid versions/citations/duplicates/ambiguity/malformed values rejected; original received bytes retained; complete temporary test fixtures still cannot promote gold or establish human independence |
| Readiness | Independent review NOT_PERFORMED, adjudication NOT_PERFORMED, reference NOT_LOCKED; publication/pharma validation readiness false; `reports/g4-readiness-final/READINESS.json` |
| G1/G2/G3 preservation | PASS, source hashes match four original native v2 manifests and all three final G3 v2 manifests; no earlier pipeline/artifact overwritten |
| Cost | **0 LLM calls, 0 model/provider usage, USD 0** |

Aggregate audit and candidate hashes: `runs/G4-VALIDATION.json`. Earlier `manufacturing-gmp-v1-draft`, `...-verified`, initial walkthrough and unsuffixed review artifacts are retained as pre-final iterations; use **-final** paths above. The underlying resource version is v1; file/manifest hashes identify these engineering iterations.

## Exact continuation commands

Run from the workspace root. Use new output paths; no source pack, walkthrough or intake is overwritten. Shell execution is prefixed with rtk per `C:\Users\User\.codex\RTK.md`.

```powershell
rtk proxy py -3 -m unittest discover -s tests -v
rtk proxy py -3 -m qa_war_room.pharma prepare --output data/derived/next-manufacturing-v1
rtk proxy py -3 -m qa_war_room.pharma exercise --pack data/derived/manufacturing-gmp-v1-final --output runs/next-g4
rtk proxy py -3 -m qa_war_room.pharma score --pack data/derived/manufacturing-gmp-v1-final --output runs/next-g4
rtk proxy py -3 -m qa_war_room.pharma review-export --pack data/derived/manufacturing-gmp-v1-final --output reports/next-g4-review
rtk proxy py -3 -m qa_war_room.pharma readiness --pack data/derived/manufacturing-gmp-v1-final --output reports/next-g4-readiness
```

The current final reviewer packet already includes ANNOTATION_RUBRIC_V1.md and the owner's protocol hash record. For a newly exported packet, supply the identical versioned rubric from docs/templates/ and retain its hash before real annotation. The export command builds cases/forms; it does not recruit/contact reviewers or perform annotation. Use one ratings JSONL per reviewer and preserve the original case_version.

Example intake, using actual completed reviewer files only when available:

```powershell
rtk proxy py -3 -m qa_war_room.pharma review-check --packet reports/next-g4-review/reviewer --ratings reports/reviewer-A-initial.jsonl reports/reviewer-B-initial.jsonl --roster reports/actual-reviewer-roster.json --output reports/next-review-intake
```

Those example completed files do not exist in this session; do not create synthetic ratings to satisfy a scientific gate. The only completed review records used by tests were explicitly marked temporary unit fixtures, not session expert artifacts.

## Remaining work and boundaries

1. Owner/domain review of the draft case plausibility, SOP conditions and causal/investigation assumptions. All numeric thresholds are scenario rules. Jurisdiction/intended pilot and original-content license remain owner decisions; no equivalence or publication rights were invented.
2. Follow the independent review plan: identify/verify suitable non-author manufacturing QA reviewers, pilot the instrument on development families, issue identical versioned blinded materials, seal initial ratings and separately adjudicate disagreements/ambiguity. No external contact or payment is authorized/performed by this local task.
3. Publish no validated-reference claim until actual review/adjudication, source corrections, ambiguity treatment and a new reference lock exist. Structural form acceptance does not meet this requirement. G4's scientific gate is not complete.
4. Optional next local product increment: manually inspect G4 cases through a browser adapter to the same strict engine. The current CAPA browser remains the original eight-case demo; G4 has CLI/Python and review Markdown only. No new G4 browser validation is claimed.
5. G5 requires a separate predeclared comparison, guardrails, independent-family/sample justification and locked analysis. Current 48 siblings, 384 scripted transitions and 42 candidate matches are not independent empirical evidence or model superiority.
6. Continue local/offline work without paid APIs. No SDK/dependency installation was needed; Python standard library remains sufficient. The workspace is still not a Git repository (verified this session), so no commit/push/publication was made. Existing Thai guides, native snapshots, literature and earlier source fixtures were preserved.

## Historical G3 snapshot (superseded by the G4 handoff above)

Updated 7 November 2026 (Asia/Bangkok). Workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.

## Current G3 handoff

The requested **G3 local/offline engineering milestone is implemented and verified**, ready for owner review. Task: `qawr-contractnli-sequential-v1`. Status: **READY_FOR_REVIEW**. It is a separately named derived ContractNLI task with controlled evidence disclosure, strict request/submit/abstain actions, source-family partitions, durable checkpoint/replay, selective/source metrics and evaluator-only coverage-proxy reachability.

G3 currently runs through a CLI/Python API. It has not been integrated into the CAPA browser UI. No paid API, LLM, training/RL, new counterfactual labels, semantic model, independent code/domain review or pharmaceutical validation occurred. The accepted Manufacturing GMP product direction remains unchanged; contracts are the methods foundation, not new GMP closure gold.

## Implemented this session

- `sequential_data.py`: gold-free segmentation preserving every original character/span; generic record catalog; exact-copy and optional declared-family union; separate original/derived split maps; source/variant lineage. Known related documents move together into the most held-out derived partition while preserving original split membership.
- `sequential_engine.py`: detached visible observations, request cost and unique UTF-8 exposure caps, exact duplicate idempotence, strict visible citations, native source labels and explicit abstention, terminal-state protection.
- `sequential_policies.py`: three offline wiring policies using only supplied observations. No free hidden-text search or gold-selected initial evidence/ranking.
- `sequential_runner.py`: frozen source/policy/budget matrix, action caps, config-bound append-only transitions, writer lock, mid-episode checkpoint/resume and source-verified replay without invoking policy or evaluator.
- `sequential_eval.py`: separate original-reference preparation, source/selective metrics with fixed denominators, reference observation/citation proxies, and post-run oracle witnesses only under evaluator/.
- `sequential.py`: prepare/run/replay/inspect/score CLI. Added 29 G3 regression tests and documentation. `data/derived/` is now ignored to prevent accidental publication of third-party source/gold.
- Updated README, architecture/evaluation/native guides, decision record, validation and handoff. Read [SEQUENTIAL_BENCHMARK.md](docs/SEQUENTIAL_BENCHMARK.md) for the exact implemented contract and limits.

## Actual verification and artifacts

| Check | Observed result / artifact |
| --- | --- |
| Baseline suite before G3 | PASS, 60 tests |
| Final full suite | PASS, **89 tests in 7.133s**, exit 0; `runs/g3-tests-verified-v2.txt` |
| Real derived preparation | PASS, 607 documents, **606 source families**, **10,319 unchanged source labels/reference sets**; `data/derived/contractnli-sequential-v1-verified/PACK.json` |
| Family/split audit | 423 train / 61 dev / 122 test families; one exact-copy group within original test, no cross-original-split family or moved document in the default map. Synthetic tests verify transitive declared families and cross-split handling |
| Source and lineage integrity | All characters/spans reconstruct; original and derived maps are separate; all hypotheses/budget/policy descendants remain grouped. Counterfactual pairs: **0** |
| Main dev smoke | One source family/document (source 563), 17 hypotheses × 3 wiring policies × budgets **0/1/4/20 = 204 dependent episodes**; `runs/g3-sequential-verified-v2/` |
| Checkpoint/resume | Stopped after 4 transitions with a request in progress, resumed to **1,479 transitions**, 204 terminal / 0 pending; first four event hashes preserved; `runs/g3-checkpoint-v2.json` |
| Replay | PASS for main, action-cap and exposure-cap runs; no gold read or policy invocation, exact returned-text/state verification; replay-console.json in each run |
| Oracle witness execution | PASS, all **68** episode/budget witnesses checked through ordinary requests: 40 attainable and 28 unattainable under the declared reference-coverage proxy |
| Reachability grid | On this one source: credits 0/1/4/20 allow complete proxy coverage on 0/9/14/17 of 17 hypotheses. This is a diagnostic, not semantic or model performance |
| Hard run action cap | PASS, stopped after 1 policy action; all 17 hypotheses remain pending and in the metric denominator; `runs/g3-action-cap-v2/` |
| Source-byte cap | PASS, 17 charged requests denied under a one-byte exposure cap; 0 source bytes/records returned; `runs/g3-exposure-cap-v2/` |
| Isolation/negative tests | PASS: no gold reads during input construction/run/replay; changed-gold input invariance; no network call from G3 runtime; unrequested text absent; visible-only citations; invalid/duplicate/terminal actions, loops, logs, locks and failures checked |
| Source-level evaluation | PASS: source label is unchanged when evidence is hidden; NotMentioned differs from abstention; a lucky label with wrong evidence fails the reference proxy; zero denominators are null |
| G1/G2 compatibility | PASS, source hashes match all four old native v2 manifests; native code/outputs were preserved |
| Existing app | `/api/health` reports ok at `http://127.0.0.1:8765`; this remains the original synthetic CAPA UI, not a new G3 screen |
| Cost | **0 LLM calls, 0 model tokens, USD 0** |

Aggregate evidence and current candidate hashes: `runs/G3-VALIDATION.json`. Each final run has manifest.json, events.jsonl, run-summary.json, metrics.json, REPORT.md and evaluator/. Evaluator gold/proxy witnesses are never inserted into the raw acquisition journal. Source references and every native label/span mapping were checked across all 10,319 items by the post-run audit.

Earlier G3 iterations (`g3-initial-smoke`, unsuffixed g3-sequential-verified/action-cap/exposure-cap) are preserved as historical outputs. Use the **-v2** run folders above for current code. The v2 suffix is a candidate iteration, not a claim that the task protocol changed to v2. Changed source hashes intentionally prevent replaying/resuming an older run under new code.

## Exact commands for the next session

Use the existing verified bundle, or prepare into a new directory. Run from the workspace root and prefix shell execution with rtk per `C:\Users\User\.codex\RTK.md`.

```powershell
rtk proxy py -3 -m unittest discover -s tests -v
rtk proxy py -3 -m qa_war_room.sequential prepare --native data/external --bundle data/derived/my-next-sequential-v1 --spans-per-record 4
rtk proxy py -3 -m qa_war_room.sequential run --bundle data/derived/contractnli-sequential-v1-verified --output runs/next-g3 --budgets 0,1,4,20 --stop-after-actions 4
rtk proxy py -3 -m qa_war_room.sequential run --bundle data/derived/contractnli-sequential-v1-verified --output runs/next-g3 --budgets 0,1,4,20 --resume
rtk proxy py -3 -m qa_war_room.sequential replay --bundle data/derived/contractnli-sequential-v1-verified --output runs/next-g3
rtk proxy py -3 -m qa_war_room.sequential replay --bundle data/derived/contractnli-sequential-v1-verified --output runs/next-g3 --episode 4
rtk proxy py -3 -m qa_war_room.sequential score --bundle data/derived/contractnli-sequential-v1-verified --output runs/next-g3
rtk proxy py -3 -m qa_war_room.sequential inspect --bundle data/derived/contractnli-sequential-v1-verified --episode-id 563:nda-11 --credits 4
```

Defaults use one complete derived source family and three policies. Twenty credits covers this selected document's 20 records, not every contract. For larger/final studies freeze the cohort/caps after development attainability review. Resume requires identical code/bundle/split/groups/policies/budgets/caps/seed. stop-after-actions is only a checkpoint control. Never overwrite prior outputs, blindly clear a writer lock or truncate a torn ledger. No final test inference was performed.

## Remaining limits and next work

- All current policy labels are hash-selected wiring outputs. Their correctness/FSR numbers are not LLM, semantic or pharmaceutical results. The 204 paths come from one document/family and are not independent samples; no confidence interval or confirmatory benefit is claimed.
- Published span completeness is a declared **coverage proxy**, not independently annotated minimal sufficiency. NotMentioned's full-source exposure rule is a conservative engineering proxy, not a new official annotation. Oracle witness IDs/labels remain evaluator-only.
- Exact-copy grouping does not establish broader template/form/translation independence. Review and import a documented family map before claiming source-family generalization. Current lineage supports future descendants but contains no newly authored counterfactuals or changed-label study.
- The next optional product increment is a manual G3 browser inspector using this same strict engine/replay API. No G3 browser acceptance is claimed here. The existing CAPA UI/session behavior is unchanged and remains in memory; G3 logs are durable local files.
- The next research increment is G4: versioned Manufacturing GMP case/SOP/reference specifications, annotation rubric, counterfactual family design and a proportionate independent QA review plan. Authoring fixtures/software can remain offline; do not claim independent labels until review occurs.
- Continue local work without paid APIs under the owner's instruction. Any future paid/model work needs separate provider/model/cost authorization before execution. No owner decision on jurisdiction/reviewer/customer/license was invented.
- The workspace is still not a Git repository (verified this session). No commit/push/publication occurred. Candidate versions are file hashes; runtime remains Python standard library with no added dependency. Existing literature, source bytes, Thai guides, fixtures and earlier evidence were preserved.

## Historical G1/G2 snapshot (superseded by the G3 handoff above)

Updated 7 November 2026 (Asia/Bangkok). Workspace: `C:\Users\User\Desktop\myProject\qa-war-room`.

## Current handoff

The Windows starter and native benchmark **offline engineering increment** now work. Status: **READY_FOR_REVIEW**. This is not the entire G2 research gate, a published-model reproduction or pharmaceutical validation. The browser remains a scripted synthetic CAPA demo; the native CLI is separate. No paid API, LLM inference, RL, independent domain review, human study, real-site pilot or remote publication occurred.

## Environment and preservation

- Python: `py -3`, version 3.13.15. Standard-library runtime; no dependency installation needed.
- This is an extracted starter, **not a Git repository**. `git status` returned “Not a git repository”. No commit/push/remote mutation occurred; native manifests record candidate source hashes. PACKAGE_MANIFEST.json remains the historical bundle inventory, not an updated checksum claim.
- Existing fixtures, benchmark source bytes, Thai guides, literature and reading pack were preserved. Raw data/references/runs remain ignored. No code-license decision was imposed.
- Server started with `py -3 -m qa_war_room --port 8765` and was left running at `http://127.0.0.1:8765`. Check `/api/health` before starting another process. Browser sessions are in memory and reset when the server stops.

## Implemented changes

- `native_data.py`: strict checked native inputs, original text/span IDs, canonical DrugQA prompt and document-local BM25. No evaluator reads.
- `models.py`: narrow adapter protocol, detached visible requests, native prediction validation and deterministic wiring fake; non-offline identities refused.
- `native_runner.py` / `native.py`: separate run/score commands, document-grouped frozen cohorts, prompt/data/code hashes, append-only config-bound hash-chain events, exclusive writer lock, resume and call/token/cost caps. Unknown interrupted/error usage retains its reservation; no automatic retries.
- `native_metrics.py`: ContractNLI hypothesis-macro classification and evidence ranking; DrugQA fixed-denominator accuracy, validity, Wilson and public strata. No combined audit score.
- Preparation now verifies the project dataset lock, rejects cross-split ContractNLI document overlap, hashes prepared files and retains DrugQA language in evaluator metadata.
- Added a pinned/free protocol-reference fetch script and `literature/native-protocol-lock.json`. References are read as text, never executed. The canonical prompt was matched to reference literals with AST inspection.
- Fixed the missing favicon/404. Clarified that debrief missing-support IDs mean records absent from submitted citations, even if already retrieved.
- Added 25 tests; updated README, architecture/evaluation documentation, validation record and [native guide](docs/NATIVE_BENCHMARK.md).

## Actual verification

| Check | Outcome / evidence |
| --- | --- |
| Initial unittest discovery | PASS, original 35 tests |
| Final `py -3 -m unittest discover -s tests -v` | PASS, 60 tests in 2.186s; live HTTP plus native isolation, metric arithmetic, failure accounting, caps, interruption/resume, locks, foreign/changed/torn ledger rejection |
| `py -3 -m qa_war_room benchmark --output runs/engineering-smoke.json` | PASS, 32 authored scripted episodes; engineering only |
| `py -3 scripts/prepare_benchmarks.py --source benchmark-data` | PASS; `data/external/PREPARATION_REPORT.json` includes prepared hashes |
| Source counts | ContractNLI train/dev/test: 423/61/123 documents and 7,191/1,037/2,091 tasks. DrugQA: 11,444 items; 4,571 raw Drugs-category items; no official training split/per-item functional-subdomain field |
| `node --check qa_war_room/static/app.js` | PASS, exit 0 |
| Canonical DrugQA prompt | PASS, system/user template strings equal pinned reference literals; no extra choice prefixes |
| Native full-context | PASS, one dev contract / 17 tasks; paused after 5, resumed to 17 without duplicate calls; `runs/native-contractnli-full-v2/` |
| Native retrieval | PASS, same one dev contract / 17 tasks, top-k=5; `runs/native-contractnli-retrieval-v2/` |
| DrugQA wiring smoke | PASS, declared 12-item source-prefix subset, not held-out/tuning data; `runs/native-drugqa-v2/` |
| Hard call-cap smoke | PASS, stopped before call 3, 2 finished / 15 pending, scoring denominator 17; `runs/native-cap-check-v2/` |
| Separate evaluator commands | PASS for all four v2 folders; metrics.json, score-console.json and REPORT.md; USD 0/no LLM calls |
| Actual Chromium UI | PASS at 1440/390px; manual relevant/irrelevant requests, free reopening, manual verdict, scripted completion, debrief and actual Markdown/JSON downloads; no horizontal document overflow |
| Browser boundaries | PASS, initial evidence empty/feedback null, only requested D2 returned, duplicate POST leaves spend/events unchanged, early report and late mutation rejected 409 |
| Browser console | Final 0 errors/0 warnings after favicon fix; clarified citation label verified on an incomplete-citation debrief |

Browser evidence is in `runs/browser/`; aggregate evidence is in `runs/WINDOWS-VALIDATION.json`. Earlier v1 outputs are preserved as historical pre-hardening runs; use v2 for the final candidate. Source hashes deliberately prevent resuming old runs after code changes.

## Exact continuation commands

Use new output names. Prefix shell execution with `rtk` per `C:\Users\User\.codex\RTK.md`.

```powershell
rtk proxy py -3 -m unittest discover -s tests -v
rtk proxy py -3 -m qa_war_room --port 8765
rtk proxy py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --stop-after 5 --output runs/next-contractnli
rtk proxy py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --output runs/next-contractnli --resume
rtk proxy py -3 -m qa_war_room.native score --output runs/next-contractnli
rtk proxy py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --baseline lexical-retrieval --top-k 5 --output runs/next-retrieval
rtk proxy py -3 -m qa_war_room.native score --output runs/next-retrieval
rtk proxy py -3 -m qa_war_room.native run --dataset drugqa --split all --limit 12 --output runs/next-drugqa
rtk proxy py -3 -m qa_war_room.native score --output runs/next-drugqa
```

Resume requires unchanged dataset/split/baseline/limit/top-k/caps/code. stop-after is an operational pause only. Changed caps/code/data require a new run directory; no prior output is overwritten. Inspect stale writer locks/torn logs before explicit recovery; do not blindly delete or repeat uncertain calls.

## Material limitations

- Forced classes/answers are hash-selected; evidence scores are lexical. These fake outputs are not LLM/semantic/pharma performance. Only the reported native metric subset is implemented; the full upstream BERT evaluator was inspected, not installed/executed. No independent code review is claimed.
- Current complete native smoke uses one contract across two paths plus 12 DrugQA items. Seventeen hypotheses are not 17 independent contracts. No test-split inference occurred. The DrugQA smoke prefix has no official dev status and cannot become a retrospectively held-out test.
- Native evidence scoring excludes gold NotMentioned rows and is optimistic by construction. Macro label means hypothesis ID; undefined classes/incomplete evidence have explicit null/diagnostic behavior.
- Browser sessions remain in memory; only benchmark logs are durable. The hash chain is not a signed/regulated audit trail against an owner who rewrites all hashes. Default USD caps are zero; real provider tokenization/billing control is not implemented.
- Product cases/policies remain eight authored examples from two template families with ID-set feedback. Domain review, semantic grading, clustered study analysis and confirmatory locks remain separate gates.

## Next concrete work

1. Review the native metric/source mapping and current candidate. Offline engineering is ready for review, not a scientific release.
2. Before real G2 inference: obtain provider/model choice, server-side key setup, pilot/run USD ceilings and processing scope. Verify current official prices, implement one provider behind the existing interface, and measure a small authorized pilot before estimating a full run. The current CLI refuses non-offline identities. Report costs/requirements before paid calls.
3. Next independent local milestone is G3: separately named sequential adaptation with observation/action/cost contract, grouped splits and attainable-budget/oracle checks. Do not describe native full-document retrieval as hidden-record acquisition. Keep Manufacturing GMP scope; no RL/six-agent training now.
4. Jurisdiction/pilot, independent manufacturing QA reviewer, customer segment and original code license remain open in docs/DECISIONS.md. These do not block ordinary local work.

## Original starter state (historical)

Updated 7 November 2026.

## Completed

- Offline local browser app, bounded session/evidence engine, six personas and four scripted auditor policies.
- Eight original synthetic cases from two template families; terminal reference-set comparison.
- JSON/Markdown reports and two completed example exports.
- Thirty-five automated tests passing in the authoring environment.
- JavaScript syntax and HTML/DOM/API contract checks.
- Two published benchmark snapshots pinned and verified; model-input/gold preparation completed.
- Targeted review of22 selected papers,21 downloaded PDFs plus P02full-text XML;6 regulatory/context PDFs.
- Detailed product/research/evaluation/journal documentation and Codex prompt.

## Next

G1/G2: visually check the UI on an accessible local browser; implement native benchmark metrics/runners and one bounded model adapter with an offline fake; add resumable run/cost manifests. Preserve original task semantics.

## Not yet performed

LLM calls or model scores; RL; semantic evidence grading; independent pharma reference review; human study; real site pilot; operational twin; remote publication or push.

## Material limitations

Demo policies and fixtures were authored together. Thirty-two scripted episodes are eight cases × four policies, not32 independent samples. Current reference_support_coverage is authored ID-set completeness, not selective decision coverage. Current sessions are in memory and local only.

Actual browser rendering was blocked by the authoring environment; static frontend and live HTTP API checks passed. Paper P02 publisher PDF and optional NIST report R07PDF remain unavailable; original full-text XML ofP02is included.

## Owner decisions awaiting later input

Jurisdiction/intended pilot, independent domain-review access, inference budget/provider, first customer segment and project license. These do not block authorized offline implementation. See docs/DECISIONS.md.
