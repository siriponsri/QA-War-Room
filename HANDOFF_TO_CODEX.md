# Handoff to Codex

## Paused for Claude frontend work — 7 November 2026

The owner explicitly paused Codex implementation and requested a frontend transfer to Claude. See [HANDOFF_TO_CLAUDE.md](HANDOFF_TO_CLAUDE.md), [PROMPT_FOR_CLAUDE_TH.md](PROMPT_FOR_CLAUDE_TH.md) and the latest pause note in [STATUS.md](STATUS.md). No application code or scientific gate was changed for this handoff. The earlier persistence/local-model plan remains a proposal. On an owner-authorized return, read Claude's actual HANDOFF_BACK_TO_CODEX.md and inspect its current frontend edits/evidence before resuming; preserve them and do not reset to the immutable G6 archive. Do not automatically resume backend/model/research work merely because a return file exists.

## G6 and live bilingual UI update — 7 November 2026

The requested local/offline manuscript and reproducibility package plus the owner-requested modern minimal LINE-style chat/dashboard are complete as engineering increments. Read the current [STATUS.md](STATUS.md), [G6_REPRODUCIBILITY.md](docs/G6_REPRODUCIBILITY.md) and [LIVE_ROOM.md](docs/LIVE_ROOM.md). Main chat is localhost:8765, dashboard /dashboard.html, manual desk /manual.html. Thai/English and Light/Dark work with GPO-inspired original green tokens. A bounded background scripted team performs real session requests/reviews until completion or timeout; no LLM or independent expert is implied. Final source and fresh-extracted package each pass 185 tests. The frozen package is reports/g6-reproducibility-v1; generated draft is writing/MANUSCRIPT_DRAFT.md. Fresh rehearsal replays without gold before separate evaluator extraction, reproduces exact analysis bytes and correctly refuses a confirmatory lock. Current STATUS/HANDOFF supersedes creation-time notes inside the immutable archive. Independent review/adjudication remain NOT_PERFORMED; reviewed reference NOT_LOCKED; scientific results NOT_RUN. No paid APIs, new license, publication, contact or deployment. Earlier native/G3/G4/G5 hashes remain compatible. Next scientific step is genuine review/adjudication, not filling draft gates with invented results.

## G5 continuation update — 7 November 2026

The requested local/offline G5 plan and analysis preparation is implemented. Read the current [STATUS.md](STATUS.md) and [G5_EVALUATION_PLAN.md](docs/G5_EVALUATION_PLAN.md) first. The strict engineering-only lock/run/replay/analyze CLI retains all frozen jobs and evaluator-only gold; 147 tests pass. Current verified-v2 dev diagnostics cover 192 jobs over 16 synthetic cases/two construction families, with 614 replayed transitions. A cap-one-action run retains 191 pending jobs. Scientific estimates/intervals are withheld; confirmatory requests are refused without creating a scientific lock. Actual independent review/adjudication remain NOT_PERFORMED; reviewed reference remains NOT_LOCKED. No paid API, model inference or G5 browser integration occurred. Old native/G3/G4 implementations remain unchanged. Earlier sections are historical; do not interpret the offline engineering increment as completion of the G4/G5 scientific gates.

## G4 continuation update — 7 November 2026

The requested local/offline G4 authoring and review-preparation increment is implemented. Start from the current [STATUS.md](STATUS.md), [case-pack guide](docs/MANUFACTURING_CASE_PACK.md), [annotation rubric](docs/templates/MFG_ANNOTATION_RUBRIC_V1.md) and [independent review plan](docs/INDEPENDENT_REVIEW_PLAN.md). There are 48 original fictional cases in six construction families, 42 unambiguous author-rule candidates and six preflagged ambiguous cases, separate input/gold, visible citations and blinded reviewer packets. The full suite has 116 passing tests. No paid API, external review, adjudication or pharmaceutical validation occurred; no new G4 browser integration is claimed. Earlier updates below are historical.

## G3 continuation update — 7 November 2026

The owner authorized G3 local/offline work without paid APIs. The separate `qawr-contractnli-sequential-v1` CLI/environment is implemented: controlled disclosure, strict request/submit/abstain, source-byte/credit caps, 606 grouped source families, lineage, durable checkpoint/replay, source/selective metrics and evaluator-only coverage-proxy reachability. The full suite has 89 passing tests. Read the current top section of [STATUS.md](STATUS.md) and [docs/SEQUENTIAL_BENCHMARK.md](docs/SEQUENTIAL_BENCHMARK.md) first. The CAPA browser has no new G3 integration; no semantic model, counterfactual relabeling, pharma validation or paid inference is claimed. Earlier updates below are historical.

## Windows continuation update — 7 November 2026

The local walkthrough and native offline engineering increment are now completed. Start from [STATUS.md](STATUS.md) and [docs/NATIVE_BENCHMARK.md](docs/NATIVE_BENCHMARK.md): 60 tests pass, browser workflow/exports work, and native full-context/retrieval paths have frozen manifests, resumable bounded logs and separate metrics. Only an offline wiring fake is enabled; no LLM/API inference occurred. Real G2 inference needs provider/model and spending authorization; G3 remains a separately named local adaptation. The original handoff below is retained as historical context.

## Mission

Continue QA War Room as a solo project with a useful product and a defensible pharmaceutical research study. The owner explicitly chose **Manufacturing GMP**. Start from the delivered code; do not replace it with a new unrelated boilerplate app.

Read AGENTS.md → GOAL.md → STATUS.md → PLAN.md → docs/DECISIONS.md. Then inspect the implementation and run the acceptance commands. The full scientific protocol is intentionally more extensive than the current code.

## Repository import

The target repository inspected for this package was https://github.com/siriponsri/QA-War-Room, public and empty at inspection. No remote files were changed. If it now contains work, inspect and preserve it.

This Windows bundle is already arranged with code at the project root. Open that exact root in Codex. reading-pack/ and benchmark-data/ live inside the local project but are excluded from Git. Keep .env and real/company data untracked. Read START_CODEX_TH.md for the owner prompt.

If the owner authorizes a commit/push, inspect the staged paths first and use a normal descriptive commit. Do not upload third-party PDF papers, raw gold data, API keys or generated runs unintentionally. Do not request confirmation for ordinary local implementation already within the task.

## First commands

```bash
python --version
python -m unittest discover -s tests -v
python -m qa_war_room benchmark --output runs/engineering-smoke.json
python scripts/prepare_benchmarks.py --source benchmark-data
python -m qa_war_room --port 8765
```

If benchmark-data is absent, the explicitly invoked fetch_benchmarks.py script retrieves the pinned official sources. Offline app work does not depend on this download.

## Current implementation

The web app and backend support a complete scripted episode. Eight cases share two template families. Four scripted auditor policies plus two auditee labels expose the six requested roles. A received record is not automatically sufficient evidence; terminal feedback checks authored reference sets. Code tests cover the important state/data boundaries.

The frontend has passed static checks but needs a visual interaction check on the owner's machine. A local browser could not be used in the authoring environment. Do not state that visual browser validation already passed.

The published datasets are real source snapshots. Their preparation script preserves native semantics and separates inputs/gold; the app does not yet run LLMs against them. The full research metric harness, future schemas and statistical protocol are prospective.

## Next milestone: G1 → G2, native benchmark runner

1. Confirm visual behavior locally and fix concrete defects.
2. Inspect prepared data and implement native benchmark input builders matching original papers.
3. Implement native metrics with tiny hand-checkable fixtures. Avoid inventing a universal audit score.
4. Add a narrow model-provider interface and a fake/deterministic adapter for offline tests.
5. Add resumable run manifests and hard call/token/cost caps.
6. Implement one retrieval baseline and one single-agent baseline.
7. Run a small development smoke batch only when credentials and budget are configured/authorized.
8. Produce raw outputs, error accounting, cost summary and a clear "development only" report.
9. Update STATUS with exact changes and results, then proceed to the next already authorized local task.

Do not start six-agent training, RL or operational twin integrations now. Do not use test answers as examples in prompts. Treat missing credentials as a specific blocked inference subtask while completing offline implementation.

## How to extend without invalidating the study

Use an interface such as `choose_action(observation, config) -> validated_action`. The observation cannot contain full unrequested records, gold, oracle support sets or reference rationales. The action must be request or submit (later abstain explicitly). Strictly record retries and failures.

Separate source gold truth from what can be justified given acquired evidence. Do not silently map benchmark NotMentioned to abstention. Do not silently interpret case-level insufficient evidence as a noncompliance. Preserve positive cases so excessive refusal is measurable.

For the pharmaceutical paper, the final Manufacturing GMP cases need a review/validation plan and an endpoint frozen before evaluation. Open generic tasks are foundations; they are not a substitute for the domain contribution.

## Known limits

- In-memory sessions; no authentication or durable regulated audit trail.
- Scripted demo policies designed against visible fixture structure.
- Exact evidence-set coverage, no semantic rationale evaluator.
- Two template families; insufficient for scientific generalization.
- Raw source gold is readable in the local research pack.
- No real provider run, model comparison, compute-cost estimate or sample-size result.
- No independent domain review or human-use outcome.
- One research paper PDF and one optional technical-report PDF unavailable; full-text XML for the research paper is included.
- Owner decisions on jurisdiction, compute budget, independent reviewer access and original code license remain open.

## Completion reporting

For each milestone, state what works, why it changed, what was tested, actual result files and unresolved limits. Link relevant files. Keep implementation and scientific claims distinct. No invented experiment values, journal rankings, acceptance probabilities or customer ROI.
