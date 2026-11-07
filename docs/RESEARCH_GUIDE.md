# QA War Room — research and CLI guide

**Interactive evidence review for Manufacturing GMP deviation and CAPA cases.**

A solo product/research starter that asks: *What evidence should a reviewer request next, and does it justify the stated CAPA effectiveness claim?*

**Current release:** 0.1.0, offline synthetic demonstration. No API key, paid service or third-party Python package is required to run the app. The six persona names identify scripted roles; they do not represent independently trained or validated experts.

**Local development increments (7 November 2026):** G1/G2 supplies the native benchmark CLI; G3 adds the derived controlled-disclosure task; G4 adds 48 original synthetic Manufacturing GMP cases, draft criteria/candidate references and blinded independent-review materials. G5 adds a prospective evaluation plan, input-only engineering locks, matched-budget offline runs, checkpoint/replay and evaluator-only analysis with fixed failure denominators. Independent review/adjudication remain pending; scientific estimates, intervals and confirmatory lock are withheld. These are source-workspace engineering features; no new packaged release, pharmaceutical validation or LLM evaluation is claimed. See [NATIVE_BENCHMARK.md](NATIVE_BENCHMARK.md), [SEQUENTIAL_BENCHMARK.md](SEQUENTIAL_BENCHMARK.md), [MANUFACTURING_CASE_PACK.md](MANUFACTURING_CASE_PACK.md) and [G5_EVALUATION_PLAN.md](G5_EVALUATION_PLAN.md). Current verification is recorded in [STATUS.md](../STATUS.md).

## Windows workspace

G6 adds a [local manuscript draft](../manuscript/draft.md), [prospective pilot brief](../manuscript/PILOT_BRIEF.md) and [reproducibility bundle/rehearsal](G6_REPRODUCIBILITY.md). Run `py -3 -m qa_war_room.publication build --output reports/my-g6-bundle` to freeze the existing checked G5 engineering evidence, then `verify` and `rehearse` as documented. Environment inputs, raw runs and evaluator references stay in separate archives. Scientific results remain NOT_RUN; this is local preparation, with no independent review, paid API use or submission. Current verification is in [STATUS.md](../STATUS.md).

Extract this ZIP directly into your qa-war-room project folder. README.md, AGENTS.md and qa_war_room/ must be immediately inside that folder. Open that same folder in Codex and read START_CODEX_TH.md. There is no nested repository/ folder.

## Quick start

The main page now offers a minimal LINE-style live conversation and a separate [local dashboard](http://127.0.0.1:8765/dashboard.html), Thai/English and Light/Dark. The simulated investigator, two record owners and evidence reviewer advance through real bounded session actions in the background until completion or timeout. Partial runs do not force a decision. The original manual workflow is at `/manual.html`. See [LIVE_ROOM.md](LIVE_ROOM.md); this is the eight-case scripted demo, not an LLM experiment or independent GMP review.

Frontend v2 (7 Nov 2026): choose a case → set a time → start, with a sticky start bar and advanced options folded away. The four roles appear as original illustrated fictional characters (Phum, Uncle Chai, Fon, Mind) with a "who is talking" stage, blinking/talking avatars and per-character voices. Voices are a deterministic display layer over the backend's rule-based messages: facts are copied verbatim, the system wording is one click away, and downloaded reports keep the system wording. Persona "system prompts" are documented as a proposal in [AGENT_PERSONAS.md](AGENT_PERSONAS.md). Browser acceptance: `node scripts/ui_browser_check.mjs --out <new folder>` against a running server (Node ≥ 22 and local Chrome/Edge; creates a few in-memory demo rooms). Regenerate SVG assets with `py -3 scripts/make_ui_svgs.py`.

AI settings (`/settings.html`): choose Typhoon, Anthropic, OpenAI, Google Gemini, OpenRouter or local Ollama, save an API key (stored only in git-ignored `.qawr/provider-settings.json`, shown masked) and pick a model from a priced list or the live list returned by **Test connection** (free account/model-list endpoints only). Chat rooms do not use these settings yet.

Use Python 3.10+ from the repository root:

```bash
python -m qa_war_room --port 8765
```

Open **http://127.0.0.1:8765** in your browser. On Windows, use `py -3` instead of `python` if that is the installed launcher. Stop with Ctrl+C. Do not open index.html directly; it needs the local API.

1. Choose a synthetic case and auditor policy.
2. Start a session, inspect the claim and assessment cutoff.
3. Request documents using the evidence budget.
4. Read the returned records and select citations.
5. Submit supported, contradicted or insufficient with a rationale.
6. Inspect the terminal debrief and download Markdown/JSON.

A scripted step is optional. You can request records manually and then use a scripted step in the same session. It uses the same budget.

## What works now

- Eight fictional manufacturing cases across two template families.
- Six named personas; four deterministic auditor policies and two record-owner roles.
- Hidden evidence until requested; unavailable-record responses; fixed budget and idempotent retry.
- Three-way claim decisions with citations limited to records actually received.
- Terminal reference comparison, event trail and exportable record checklist/report.
- A deterministic 32-episode engineering runner.
- Pinned published benchmark snapshots in the **full starter pack**, with checksum validation and separate model/evaluator files.
- Detailed product, pharmaceutical research, evaluation, literature and journal plans.

## What remains prospective

No LLM inference, RL training, independent pharmaceutical reference review, human training trial, native-benchmark LLM score, operational digital twin or eQMS integration has been performed. Offline fake predictions have been scored only to verify the metric pipeline. Reference-set coverage in the demo does not establish semantic entailment. The eight cases and their policies were authored together; their scores are not scientific evidence.

## Verify the starter

```bash
python -m unittest discover -s tests -v
python -m qa_war_room benchmark --output runs/engineering-smoke.json
```

See [VALIDATION.md](../VALIDATION.md) for actual checks and limitations. The Windows browser workflow and responsive layout were checked on 7 November 2026; the original packaging environment's browser limitation is retained as historical context there.

## Prepare the published benchmarks

This Windows bundle places `benchmark-data/` and `reading-pack/` inside the project root. Both are excluded from Git. Run from the root:

```bash
python scripts/prepare_benchmarks.py --source benchmark-data
```

If using only this source repository, acquire the pinned public bytes explicitly:

```bash
python scripts/fetch_benchmarks.py --output benchmark-data
python scripts/prepare_benchmarks.py --source benchmark-data
```

The fetch downloads approximately 81 MB, including the official ContractNLI archive before selecting its JSON files. The preparation output is ignored by Git. It is not a trained model, a published-score reproduction or a sequential benchmark.

**Never add the evaluator folder or raw answer-bearing datasets to a model's retrieval index.**

## Run the native pipeline offline

G3 is now implemented as a **separate derived sequential task**. See [SEQUENTIAL_BENCHMARK.md](SEQUENTIAL_BENCHMARK.md) for request/submit/abstain actions, controlled source disclosure, source-family splits, checkpoint/replay and evaluator-only oracle reachability. It is a separate CLI/Python environment and is not yet integrated into the CAPA browser UI.

```powershell
py -3 -m qa_war_room.sequential run --bundle data/derived/contractnli-sequential-v1-verified --output runs/my-g3 --budgets 0,1,4,20
py -3 -m qa_war_room.sequential replay --bundle data/derived/contractnli-sequential-v1-verified --output runs/my-g3
py -3 -m qa_war_room.sequential score --bundle data/derived/contractnli-sequential-v1-verified --output runs/my-g3
```

The verified bundle exists locally; the guide includes a reproducible preparation command for new workspaces. G3 keeps original source labels, supplies no hidden-text search, and computes oracle coverage proxies only in the separate evaluator. All current policies are offline wiring checks, with zero API cost. Source/raw derived data and run artifacts remain ignored by Git.

Run from this source workspace after preparation. The small protocol download is free, uses pinned public sources, and is required once for the canonical DrugQA prompt. It is already present on this machine. No downloaded Python source is executed.

```powershell
py -3 scripts/fetch_benchmark_protocols.py
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --stop-after 5 --output runs/my-contractnli
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --output runs/my-contractnli --resume
py -3 -m qa_war_room.native score --output runs/my-contractnli
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --baseline lexical-retrieval --top-k 5 --output runs/my-retrieval
py -3 -m qa_war_room.native score --output runs/my-retrieval
py -3 -m qa_war_room.native run --dataset drugqa --split all --limit 12 --output runs/my-drugqa
py -3 -m qa_war_room.native score --output runs/my-drugqa
```

ContractNLI `--limit` counts original documents and retains all their hypotheses. DrugQA has no official development split: its prefix is a declared wiring smoke subset, not held-out data or a tuning set. `run` never opens gold; `score` is a separate evaluator invocation. Run folders contain `manifest.json`, append-only `events.jsonl`, `run-summary.json`, `metrics.json` and `REPORT.md`.

Only the deterministic offline fake is enabled. Its forced labels are hash-based and its evidence scores are lexical; it is not an LLM or a semantic reasoner. The default USD cap is zero. Existing outputs require `--resume`, which refuses changed code/data/prompts/caps. See the native guide for caps, recovery and metric definitions.

## Manufacturing GMP draft case pack (G4)

The local verified pack at data/derived/manufacturing-gmp-v1-final/ contains six fictional nonsterile oral-solid construction families, six explicit site SOPs and 48 cases. Draft authored candidates comprise 12 supported, 12 contradicted and 18 insufficient; six additional cases remain ambiguous without a unique candidate. All siblings stay in one provisional template/family partition. These are authored construction counts, not model or independently reviewed results.

```powershell
py -3 -m qa_war_room.pharma prepare --output data/derived/my-manufacturing-v1
py -3 -m qa_war_room.pharma exercise --pack data/derived/my-manufacturing-v1 --output runs/my-g4
py -3 -m qa_war_room.pharma score --pack data/derived/my-manufacturing-v1 --output runs/my-g4
py -3 -m qa_war_room.pharma review-export --pack data/derived/my-manufacturing-v1 --output reports/my-g4-review
```

G4 uses a separate CLI/Python API and readable review Markdown; it has not been integrated into the original CAPA browser. Open the prepared local reviewer/INDEX.md under reports/g4-independent-review-v1-final/ for blinded source cases. Reviewer forms are blank and no expert was contacted. [The rubric](templates/MFG_ANNOTATION_RUBRIC_V1.md) and [review plan](INDEPENDENT_REVIEW_PLAN.md) define the next human work. Complete forms do not automatically validate, adjudicate or replace gold. All thresholds are synthetic site rules, not universal GMP requirements.

## Research contribution

The proposed contribution is a reproducible test of sequential evidence acquisition and applicability/sufficiency reasoning for CAPA claims, with fair budgets, explicit abstention and matched counterfactual cases. Roleplay is the interaction; scientific value comes from the task, reference validity, controlled comparisons and measured outcomes.

[GOAL.md](../GOAL.md) defines outcomes. [PLAN.md](../PLAN.md) connects product and research gates. [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) and [EVALUATION_SPEC.md](EVALUATION_SPEC.md) define the planned experiments.

## Navigation

| Need | Read |
|---|---|
| Hand project to Codex | [HANDOFF_TO_CODEX.md](../HANDOFF_TO_CODEX.md), [CODEX_START.md](../prompts/CODEX_START.md), [AGENTS.md](../AGENTS.md) |
| Product behavior and customers | [PRODUCT_SPEC.md](PRODUCT_SPEC.md), [BUSINESS_PRODUCT_MAP.md](BUSINESS_PRODUCT_MAP.md) |
| Data and pharma cases | [DATASET_PLAN.md](DATASET_PLAN.md), [PHARMACEUTICAL_CASE_SPEC.md](PHARMACEUTICAL_CASE_SPEC.md) |
| Software structure | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Literature and citations | [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md), [references.bib](../literature/references.bib) |
| Publication route | [JOURNAL_STRATEGY.md](JOURNAL_STRATEGY.md), [MANUSCRIPT_OUTLINE.md](MANUSCRIPT_OUTLINE.md) |
| Reproducibility and decisions | [REPRODUCIBILITY.md](REPRODUCIBILITY.md), [DECISIONS.md](DECISIONS.md), [STATUS.md](../STATUS.md) |

## Rights and deployment

Original project licensing awaits the owner's choice; see [LICENSE_DECISION.md](../LICENSE_DECISION.md). Third-party licenses remain separate. The literature reading pack is included locally and excluded from versioned source. The starter binds to localhost and is intended for synthetic offline use; multi-user hosting requires additional access controls, persistence and validation.
