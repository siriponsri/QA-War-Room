# G6 local manuscript and reproducibility package

Version 1, 7 November 2026. Engineering preparation: READY_FOR_REVIEW.
Independent review/adjudication: NOT_PERFORMED. Reviewed reference: NOT_LOCKED.
Confirmatory results: NOT_RUN. Submission/publication: not performed or authorized.

## Reader's task

Inspect a concrete manuscript draft and reproduce the existing offline engineering evidence without treating authored references or scripted decisions as a scientific pharmaceutical result. The manuscript template is [draft.md](../manuscript/draft.md), with [claim mappings](../manuscript/claims.json), [source status](../manuscript/SOURCE_STATUS.md) and a [prospective pilot brief](../manuscript/PILOT_BRIEF.md). Generated writing resolves engineering counts from source replay rather than hand-entered performance numbers.

The reproducibility commands add no provider, paid calls, Python dependency or new scientific experiment. The owner separately authorized a [live bilingual conversation/dashboard](LIVE_ROOM.md) during this session; that uses the eight demo cases and does not integrate the G4/G5 scientific cohort into the browser. The bibliography and regulatory links come from existing local registers; G6 performs no fresh search/download/status verification. The owner must check citations/full-text support and current journal requirements before submission. The draft makes no priority, novelty or acceptance claim.

## Preconditions

Use Python 3.10+ standard library. The actual acceptance environment is recorded in STATUS.md. Work from the project root with the existing `manufacturing-gmp-v1-final` pack and the G5 `verified-v2` lock/run/analysis and cap/refusal artifacts. [G5_EVALUATION_PLAN.md](G5_EVALUATION_PLAN.md) explains their origin. Missing or stale artifacts cause build failure; the builder does not download substitutes, change locks or invent results. Keep third-party raw benchmarks and papers outside the archive.

The builder is evaluator privileged: it may read gold/terminal analysis to validate a writing artifact. It is never called from a policy, retrieval index or active HTTP session. Only G4 engine observations remain model-facing. Never add archives, manuscripts, tests, reference annotations or complete backend record stores to a model's evidence index.

## Build, verify, rehearse

Choose new output directories; existing artifacts are preserved. On the current machine prefix shell commands with `rtk proxy` according to its local instructions. RTK is not a runtime dependency of the extracted package.

```powershell
py -3 -m qa_war_room.publication build --output reports/my-g6-bundle
py -3 -m qa_war_room.publication verify --bundle reports/my-g6-bundle
py -3 -m qa_war_room.publication rehearse --bundle reports/my-g6-bundle --output runs/my-g6-rehearsal
```

Expected build status is `LOCAL_DRAFT`; verification is `VERIFIED_LOCAL_DRAFT`. Successful full rehearsal produces `REHEARSAL.json` with `status: PASS`, `full_tests: PASS`, `analysis_bytes_match: true` and `scientific_results: NOT_RUN`. These are software checks, not a submission or domain-review gate. An internal test-only replay path explicitly records `full_tests: NOT_RUN`; it cannot report full acceptance.

Build and verify from the source workspace. Rehearsal uses a new `workspace/` beneath its output directory; it does not overwrite the source workspace. It extracts source, environment and raw runs first, confirms gold is absent and executes G5 replay. Only afterward does it extract evaluator files, run the full suite, regenerate analysis and check exact deterministic table/outcome bytes. A fresh confirmatory request must return exit **2** and create refusal rather than lock. Child processes receive only basic OS path/temp variables and Python UTF-8/user-site controls, not inherited model credentials. No external model is enabled.

Full-suite duration depends on the machine. Commands use bounded subprocess timeouts; failures preserve logs/progress and never become PASS merely because the bundle exists. Inspect a failing command log, correct the underlying issue, and create a new bundle/rehearsal directory. Do not repair a torn journal, relabel gold or bypass the scientific gate to obtain a passing archive.

## Bundle contents and boundaries

| File | Audience / contents | Excluded boundary |
|---|---|---|
| `source.zip` | Developer code, static UI, tests, selected context/docs/plans, manuscript sources and citation metadata | No raw external datasets, papers, environment files, caches or run trees |
| `environment-inputs.zip` | Backend-only G4 PACK metadata, public cards/splits, complete private environment records; original demo inputs | No evaluator labels, authoring lineage, terminal outcomes or answer keys |
| `engineering-runs.zip` | Original matched/cap locks, normalized request/response journals and summaries; cap plan | No gold or evaluator outcome rows; never active-model retrieval |
| `evaluator.zip` | G4/demonstration gold, G4 lineage, separate G5 analyses/outcomes, original confirmatory refusal | Install only in evaluator/developer phase; never actor observations |
| `writing/MANUSCRIPT_DRAFT.md` | Rendered local draft, methods, limits and engineering counts; scientific results NOT_RUN | Not a reviewed/final/submitted article |
| `writing/CLAIMS.json` | Allowed fact keys, scopes, sections and observed values | Does not semantically validate all prose or citations |
| `writing/EVIDENCE.json` | Source-replayed counts, unresolved gates and provenance hashes | Not evidence of independent human approval |
| `writing/LOCAL_USE_NOTICE.md` | Local-use, rights and audience limitations | No new redistribution license or publication authorization |
| `BUNDLE.json` | Archive/member and writing hashes/sizes, role inventories and incomplete scientific gates | Checksums are not signatures/authentication |

Source/tests include answer-bearing construction/evaluator logic, so `source.zip` is **developer-only**, not a deployable actor corpus. `environment-inputs.zip` contains complete unrequested records for the backend, not initial model context. A machine-readable manifest references evaluator file hashes without exposing their contents; metadata alone does not complete independent review. Architectural input/gold isolation remains distinct from a filesystem sandbox against the developer.

ZIP ordering, timestamps and regular-file modes are deterministic for the same captured inputs. A later doc/source change produces a different source archive hash. No existing G5 module or hash list is altered by adding G6 modules. Native/G3/G4/G5 source compatibility is checked in current session evidence. No Git commit is invented when `.git` metadata is absent.

## Evidence validation

Before rendering, the builder loads each frozen G5 matrix, replays actions against source records, checks copied source against implementation hashes, compares summary accounting with the journal, verifies analysis output/run hashes and regenerates descriptive metrics/outcomes into an isolated temporary directory. Those bytes must match saved metrics/outcomes/blank scientific tables. It verifies that scientific intervals remain withheld and confirmatory authorization remains false. A missing case/job or poisoned summary cannot supply manuscript counts.

The source/manuscript claim ledger permits engineering counts and explicit gate states only. Unresolved fact tokens and unmapped claims are refused. Some prose still needs accountable human review; this mechanism is not a language-model fact checker or reference-quality assessment. The manuscript does not treat a citation title or pointer as proof of the surrounding claim.

The archiver uses bounded allowlists and rejects symlinks, absolute/parent-traversal paths, Windows reserved names, case-colliding/duplicate members, cross-role members and oversized payloads. Verification precedes manual extraction; `extractall` is not used. Archive/member checksums and an exact file inventory detect missing/extra/changed files. The default uncompressed ceiling is 200 MB and each file is at most 50 MB. These checks constrain accidental/path-level hazards; they cannot authenticate a fully rewritten malicious archive and its manifest. Rehearse only a locally created trusted package.

## Reproduction scope

The bundle reproduces the named G5 **engineering** runs and the standard-library test suite. It includes the original synthetic full pack because the environment owns hidden records; policies still observe requested records only. It does not rerun all downloaded native/derived benchmark evaluations, include third-party bytes, supply independent review, establish statistical independence, justify sample size or run a real language model. Existing bibliography/source pins permit later separately authorized acquisition but do not trigger it.

No new consent, ethics exemption, expert contribution, funding declaration, conflict-of-interest declaration or customer endorsement is fabricated. The owner must complete those manuscript fields from actual circumstances. No journal-specific formatting, current policy compliance or manuscript submission is claimed. G6 engineering readiness does not satisfy the scientific G4/G5 gates.

## Data dictionary and expected outputs

- `facts`: source pack cases/construction families; dev cases/families/jobs/transitions/terminal/submission/abstention/pending/table counts; cap actions/pending; explicit review/adjudication/reference/result states; zero API expenditure.
- `provenance_sha256`: project-relative source-run, lock, analysis and pack file paths mapped to original SHA-256 values. These are references, not model input content.
- `archives`: archive role mapped to a complete member inventory; each entry carries SHA-256 and uncompressed byte count. `files` also checks archive bytes and writing files.
- `REHEARSAL.json`: actual command argv, exit and expected exit, raw-log path, gold-free replay boundary, deterministic analysis match, test status, incomplete scientific states and zero spend.
- `PROGRESS.json`: completed command records while rehearsal is running or if it fails. This file's existence is not a completed rehearsal.

For endpoint/pair/bootstrap definitions and empty/failure denominators, use [G5_EVALUATION_PLAN.md](G5_EVALUATION_PLAN.md); G6 changes none of them. Current counts, paths, test evidence and handoff are in [STATUS.md](../STATUS.md).

## Next step

Owner reviews the draft, actual funding/contribution/disclosure fields and pilot scope. Genuine independent blinded reference review and adjudication remain the next scientific prerequisites. A reviewed-release importer, sampling/sample-size justification, margins, real model/prompt settings and prospective lock are later work. Continue offline preparation without filling missing expert ratings, buying model calls, contacting people or publishing this local draft automatically.
