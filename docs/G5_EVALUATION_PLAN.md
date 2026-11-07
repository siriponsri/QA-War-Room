# G5 evaluation preparation and offline analysis

Version 1, 7 November 2026. Status: **READY_FOR_REVIEW (offline engineering)**.
Scientific Stage B: **NOT_LOCKED / NOT_RUN**. Independent review and adjudication: **NOT_PERFORMED**.

## Purpose and acceptance

The owner needs a reproducible way to compare evidence-acquisition policies without losing failures, confusing authored labels with reviewed references, or exposing gold to actors. G5 supplies an input-only engineering lock, bounded run matrix, exact source replay, evaluator-only tables and a prospective analysis plan. Acceptance requires complete frozen denominators, negative gate/isolation tests, replayable raw actions and an honest handoff. No provider, paid API, new dependency, expert judgment or pharmaceutical validation is included.

The machine-readable draft is [g5-evaluation-plan-v1.json](../plans/g5-evaluation-plan-v1.json). It prepares the Manufacturing GMP claim-support study; native benchmark Stage A remains separate. Do not pool native ContractNLI, the G3 adaptation and constructed G4 cases. Previous runs and source data are preserved.

## Two distinct locks

An **engineering lock** snapshots selected public cases, whole construction families, methods, budgets, repetitions, seeds, limits, environment and implementation/data hashes before any evaluator access. Its default cohort is the existing provisional **dev** partition: 16 cases, two construction families, 8 siblings per family. Four methods × three credit budgets × one repetition produce **192 jobs**. Fourteen cases have unambiguous author-rule candidates; two preflagged ambiguous cases remain separate. The lock is developmental and does not authorize a scientific performance claim.

A **confirmatory lock request** currently writes only `REFUSAL.json` and returns exit code 2. It never writes `LOCK.json`. The supported G4 release is an unreviewed author draft, and a reviewed-release ingestion/verifier has not been implemented. Filling review hashes or margins with strings cannot bypass this restriction. A local file claiming completed review cannot establish that review occurred.

Before a future scientific lock:

1. Obtain real independent blinded ratings using [INDEPENDENT_REVIEW_PLAN.md](INDEPENDENT_REVIEW_PLAN.md), resolve disagreements through documented adjudication and preserve initial ratings.
2. Publish a new versioned reference release with review provenance, eligibility/ambiguity decisions and verified reviewed-release support. Do not edit the author-draft pack in place or flip its review flag.
3. Audit independent case origins, shared construction scaffolding, grouping, label prevalence and cross-split overlap. Six construction templates are not six independently sampled manufacturing sites.
4. Use independently reviewed development/pilot information to justify sample size, minimum meaningful FSR reduction and acceptable sensitivity/accuracy loss and coverage floor. Simulate paired clustered outcomes under declared prevalence, discordance and within-family dependence assumptions. No power result is available now.
5. Select one primary candidate/comparator, model revision, prompts, operating point, decoding/repetitions and total resource budget; freeze them before viewing held-out outputs. All relevant fields remain null in this draft.
6. Freeze an appropriate uncertainty/rare-event method and multiplicity treatment. Record any protocol amendments prospectively. Previously viewed diagnostics cannot be relabeled confirmatory evidence.

## Engineering methods and matched information

| Method | Observable behavior | Role |
|---|---|---|
| `status-shortcut-v1` | Request D6; use its closure status only | Deliberately weak baseline |
| `sop-catalog-v1` | Request D1 SOP, then its material records in catalog order | Fixed-order acquisition baseline |
| `sop-adaptive-v1` | Request D1, then D5/D4/D6/D3/D2 as required; stop on an observed decisive failure or unresolved criterion | Sequential engineering candidate |
| `ignore-applicability-v1` | Same acquisition as catalog; ignore scope/date applicability in a detached interpretation copy | Applicability ablation |

Methods are coauthored deterministic scripts interpreting structured fictional SOPs, not humans or LLMs. They receive only a copied active observation: claim, catalog/costs, acquired records and responses. They cannot access the store, gold, authoring lineage, pair labels, unrequested text or oracle actions. The ablation never modifies actual records, raw engine observations or evaluator checks. It does not remove revision/content checks; those are separate future ablations. The broader ledger, role-separation, calibrated abstention and oracle ablations in the research protocol remain prospective.

All methods receive identical case-specific access interfaces, acquisition credit budgets **0/3/7**, source-byte cap **200,000/job**, and policy-action cap **16/job**. Global policy-action cap is **10,000**, maximum jobs **10,000**, retries **0**, provider `offline_only`, API spending cap **USD 0**. One request to D5 costs two credits; the other material records cost one, so D1–D6 cost seven. Status-only baselines may spend less. Early stopping and unused budget are reported, not compensated with hidden extra evidence. There are no model tokens/calls in these engineering runs. Measured wall time includes local policy/engine work; it excludes ledger disk I/O and is not an API latency estimate.

## Endpoints and denominators

`supported`, `contradicted` and `insufficient` are submitted labels. `abstain` is a distinct action. Missing evidence does not establish a GMP violation. Preflagged ambiguity has no unique primary reference and is reported separately; this is an author-defined exclusion pending review, fixed before these runs.

Let N be all frozen primary-eligible case × repetition units at one budget/method, including failures and unstarted work. Let N+ be author-candidate supported units and N− all other primary-eligible units.

| Quantity | Numerator | Denominator |
|---|---|---|
| Primary FSR | Submitted supported on candidate contradicted/insufficient | N− |
| Supported sensitivity | Submitted supported on candidate supported | N+ |
| Decision coverage | Any valid submitted label, including insufficient | N |
| Overall accuracy | Valid submitted label equals candidate reference | N |
| Wrong share of accepted supports | Candidate-negative submitted supports | All primary submitted supports |
| Warranted-support proxy recall | Candidate-positive supports satisfying structured proxy | N+ |

Each reported rate includes its numerator/denominator; zero denominators are null. Macro F1 averages classes with nonzero actual+predicted totals; missing submissions contribute false negatives. Confusion tables retain ABSTAIN/PENDING/INVALID. Coverage and accuracy use conservative fixed denominators; FSR alone can decrease by refusing everything and must never be interpreted without guardrails.

The structured evidence proxy requires agreement with author reference, the original visible structured rules, declared cited fact locations and required unavailable-record checks. It is not an independent semantic rationale judgment or proof of minimal sufficiency. `semantic_evidence_validity` stays null. An invalid or unsupported answer cannot become warranted merely because its citation pointer exists.

## Pairing, weighting and uncertainty

Pair candidate/comparator on exact case, credit budget and repetition. Reject missing/duplicate units and reference/group disagreement rather than silently intersecting successful rows. Default engineering point comparison is adaptive minus catalog at each budget and is descriptive; the scientific primary comparison is still unset. Other methods/budgets are exploratory diagnostics with no significance claims.

The pure `paired_bootstrap` helper implements item-weighted paired family percentile arithmetic with confidence level 0.95, 2,000 draws and seed 20261107 by default. Every sampled family carries both methods, all sibling cases and all repeated runs. Repetitions never increase the independent-family count. The default estimand is case × repetition item weighted; descriptive equal-family-weighted sensitivity estimates and per-family denominators are also exported. Undefined groups are counted explicitly.

Intervals are withheld for fewer than two groups, any undefined denominator draws, zero observed FSR events in either arm, or a degenerate bootstrap distribution. The helper does not implement a rare-event upper bound, validate independence or authorize scientific inference. It must not produce an all-zero safety guarantee. A future reviewed study needs a justified rare-event analysis with its assumptions/estimand declared.

**Current analysis exports no research confidence intervals or success decision**, even though bootstrap arithmetic has fixture tests. The two dev construction families, unreviewed labels, coauthored rules/policies, unresolved margins and absent model/pilot do not support that interpretation. `SCIENTIFIC_TABLE_TEMPLATE.csv` contains blank estimates/intervals with status `NOT_RUN`.

For a future locked primary comparison, joint success requires upper CI(ΔFSR) < −minimum reduction, lower CI(Δsensitivity) > −sensitivity loss margin, lower CI(candidate coverage) ≥ coverage floor and lower CI(Δaccuracy) > −accuracy loss margin. All four conditions must hold; a non-significant difference is not equivalence. The math helper returns no decision for unresolved margins/intervals and never grants scientific authorization. Multiplicity, rare-event handling and the final confidence procedure need review before locking.

## Failure accounting and pair diagnostics

Global cap exhaustion leaves jobs `pending`; it does not drop them. Invalid actions and policy exceptions terminate that job as a recorded failure, without automatic repair/retry. Duplicate requests are idempotent but still count as policy actions. Exceeding the per-job action cap records `action_cap`. Interrupted journals resume from exact replay; a torn tail, foreign lock, concurrent writer, source response change, implementation drift or modified complete matrix is refused. Preserve artifacts for investigation rather than editing the frozen run.

Pair diagnostics use evaluator-only G4 controlled-pair annotations, restricted to complete selected families. Label-changing sensitivity requires both valid labels to match their respective candidates; any label-change rate is separately diagnostic. Label-preserving stability requires two valid equal labels; a second rate requires both to be correct. Failure, abstention and pending endpoints remain in pair denominators. Unresolved-ambiguity pairs remain separate. These are constructed author-rule perturbations, not independently reviewed counterfactuals.

## Reproduce locally

Run from the source root. Use new output directories; the commands preserve existing outputs. No downloads are needed for the existing local G4 pack.

```powershell
py -3 -m qa_war_room.study lock --pack data/derived/manufacturing-gmp-v1-final --output runs/my-g5-lock
py -3 -m qa_war_room.study run --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run --stop-after 5
py -3 -m qa_war_room.study run --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run --resume
py -3 -m qa_war_room.study replay --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --output runs/my-g5-run
py -3 -m qa_war_room.study analyze --pack data/derived/manufacturing-gmp-v1-final --lock runs/my-g5-lock --run runs/my-g5-run --output reports/my-g5-analysis
py -3 -m qa_war_room.study lock --mode confirmatory --pack data/derived/manufacturing-gmp-v1-final --output reports/my-g5-refusal
py -3 -m unittest discover -s tests -v
```

The confirmatory command's exit 2 is an expected refusal, not a completed study. For a fresh workspace, build the draft pack using [MANUFACTURING_CASE_PACK.md](MANUFACTURING_CASE_PACK.md); do not download or reconstruct independent ratings.

## Artifact boundary and handoff

| Artifact | Contents | Actor access |
|---|---|---|
| Plan / `LOCK.json` | Draft protocol, public cohort/group identifiers, complete jobs, hashes/caps | Public configuration; no gold contents |
| Run `manifest.json`, `events.jsonl`, `SUMMARY.json` | Raw actions, only requested source responses, failure/cost accounting | Gold-free |
| Analysis `evaluator/outcomes.jsonl` | Frozen jobs joined to author candidates | Evaluator-only; exclude from prompts/indexes |
| `ENGINEERING_METRICS.csv/JSON`, `REPORT.md` | Descriptive tables, denominators, paired deltas, constructed-pair diagnostics | Terminal evaluator outputs; never answer-bearing retrieval |
| `SCIENTIFIC_TABLE_TEMPLATE.csv` | Empty scientific estimates/intervals, `NOT_RUN` | Prospective template |
| `ANALYSIS.json` | Input/run/evaluator/code and output hashes | Audit metadata |
| `REFUSAL.json` | Unresolved scientific gates; no study lock | Gate evidence |

Analysis replays the source run before evaluator access, never invokes a policy, never modifies raw runs/gold and generates its tables from all frozen jobs. Locks/checksums detect drift; they are not signatures or evidence of independent human approval. The separation is architectural, not an operating-system sandbox against a developer reading local files.

Validation maps to `tests/test_study.py`: isolation and gold tampering; complete matrix/paired denominators; checkpoint and source replay; failure/cap/concurrency/serialization paths; hand-computed endpoint fixtures; clustered repeated-run arithmetic, undefined/zero-event handling and joint guardrails. Full regression evidence and current run locations are in [STATUS.md](../STATUS.md). No G5 browser integration or independent UI study is implemented.

Next actor: owner/researcher arranges actual independent review and adjudication using the prepared blinded packets. Offline follow-up can add reviewed-release ingestion tests and a sensitivity-simulation tool with explicitly hypothetical inputs; it must leave actual review and power outcomes unclaimed.
