# Integrated product and research plan

## 1. Planning basis

This is a **solo execution plan organized by evidence gates**, not a promise that publication or a regulated product can be completed in a fixed number of weeks. A planning envelope of roughly 12–20 focused weeks for a credible first computational study is reasonable only after data access, labeling workload and model budgets are measured. It is an estimate for allocation, not a forecast. External review and journal turnaround are outside it.

Prefer two concurrent workstreams sharing the same artifacts: the product creates reproducible interactions; the study determines which interactions and checks are useful. Do not build the entire game and begin evaluation afterward.

| Gate | Product work | Research work | Evidence required to move on |
|---|---|---|---|
| G0 — starter | Offline case interaction, reports, scripted roles | Define task and limitations | Tests and a human walkthrough; no scientific result |
| G1 — native data | Source register and adapters | Reproduce original input/label/metric conventions | Pinned bytes, license records, schema checks, native task report |
| G2 — minimal models | One grounded model adapter and simple retrieval | Fixed-budget baseline matrix | No gold leakage; all calls and failures logged |
| G3 — sequential task | Evidence request action and replay | Controlled hiding of information; attainable-budget analysis | Separate adapted task, grouped split, oracle upper bound |
| G4 — pharma cases | CAPA workflow, provenance and missing-evidence output | Case specification, blinded labeling/review, counterfactual families | Review report and frozen reference labels |
| G5 — final evaluation | Reliable report/export UX | Predeclared primary comparison, ablations, uncertainty | Locked run manifest and analysis generated from raw runs |
| G6 — manuscript + pilot | Demo, example report, pilot brief | Reproducibility archive and paper | Supported claims, data availability and limitations |
| G7 — optional expansion | Site-specific process representation | Transfer/RL/human study only if justified | Separate protocol and explicit feasibility evidence |

## 2. Detailed work packages

### WP0: establish a reliable local product

Read the source and run the tests and CLI before extending it. Walk through one case by hand: inspect the objective, request a relevant and irrelevant document, attempt a duplicate request, submit a verdict, then inspect the JSON/Markdown report. Confirm that case names and catalog metadata do not reveal the answer. Check the request/response boundary with browser network tools as well as the screen.

Deliverables: runnable local app, architecture map, versioned demo cases, test result, known limitations. Finish this before adding model calls. A UI with missing evidence does not require a real agent to demonstrate its workflow.

### WP1: verify published open data

Start with ContractNLI as document reasoning and Sino-US-DrugQA as pharmaceutical regulatory knowledge. Add SciFact if evidence-set evaluation is needed. ACE is optional after overlap checks. Preserve original labels and document boundaries. Do not convert all benchmarks into one synthetic "compliance accuracy" score.

For each source, retain citation, URL, commit/release, file hash, license and scope, original splits, official metric implementation, permitted evaluation/training use, label quality, and preprocessing differences. Require exact counts before use. Downloads should live outside committed source by default.

Sino-US-DrugQA has no official training split and no public per-item functional-subdomain field in the checked release. Use the native benchmark or a clearly declared Drugs-category subgroup; do not pretend a ready-to-filter GMP-only audit dataset exists. Constructing a new GMP tag requires its own documented annotation procedure.

Deliverables: a validated adapter for each chosen source, a dataset card and a tiny synthetic adapter fixture. Exit condition: original records can be reconstructed from source IDs, and model inputs exclude labels and explanations.

### WP2: implement minimal model and retrieval baselines

Implement a narrow model interface taking an observation and returning a validated action JSON. Keep provider-specific client code separate from the environment. Use one configured model first. Log actual model identifier, date, settings, prompt version, input/output tokens, retries, response validation failures and wall-clock time. Real provider prices must be recorded at execution time, not embedded as timeless assumptions.

Build deterministic keyword/BM25 retrieval before an embedding index. Add single-agent retrieval with fixed queries, then an adaptive single-agent requester. Add multi-agent review only after these work. If roles all use the same model, compare extra calls with an equally funded single-agent retry or reflection baseline.

Deliverables: executable baseline runner, cost ledger, schema validation and redacted trajectory output. Exit: no evaluated policy can inspect gold and no hidden retries are free.

### WP3: formalize the interactive adaptation

Define what the agent sees initially: claim, known scope, document inventory metadata, rule version and budget. Define each action, cost and response. Fix whether record titles, timestamps and document types are visible before acquisition. A title that implies a verdict is leakage. A "search" action that scans all hidden records for free changes the information budget and must be costed or excluded.

Create a separate adapter version for interactive hiding. Maintain an oracle that can access the full truth only for evaluation/attainability analysis. An oracle's selected evidence cannot be passed into a deployable retriever. Ensure that the required supporting evidence can actually be obtained under each tested budget.

Deliverables: observation/action schema, grouped split manifest, counterfactual family index, reachability check and budget grid. Exit: a third party can distinguish original benchmark scores from adapted scores.

### WP4: construct the pharmaceutical transfer resource

Use a small number of well-specified manufacturing failure families before scaling. Suggested families include packaging reconciliation, equipment setup/change control, recurrent deviation after retraining, process-parameter excursions, investigation scope across batches and CAPA effectiveness windows. Avoid sterile or high-hazard specialist scenarios initially unless domain review is available.

Each family has a claim; an explicit approved **synthetic site SOP**; relevant batches/product/line/date; deviation investigation; CAPA plan; implementation evidence; effectiveness criteria; follow-up results; and optional contradicting/irrelevant records. Include true support, contradiction and genuine insufficiency. Do not label every case bad.

Create matched pairs by changing one decisive fact while holding surface details fixed. Then create non-decisive changes to test stability. Audit word choice, filenames, record order and timestamps for shortcuts. Separate family generation from reference labeling. Keep a change log of disagreements and rule revisions.

A solo author can build the software and deterministic corpus. External expert review is a distinct validation activity, not proof obtained from an "expert" prompt. If no reviewer is available, limit the paper to the constructed environment and report the lack of domain validation. Do not quietly replace independent review with an LLM jury.

Deliverables: case card, annotation rubric, author-provided constraints, review sheet, adjudication log, family-held-out split and license statement. Exit: every reference decision points to facts and sufficiency rules; ambiguous cases are flagged before model testing.

### WP5: freeze and run the study

Select one primary comparison and one primary outcome plus guardrails from RESEARCH_PROTOCOL.md. Calibrate on development groups only. Choose the smallest practically useful difference with domain input; use a pilot to estimate paired disagreement and within-family correlation. Determine the final number of independent families from desired precision/power, not from how many synthetic variants a model can generate.

Freeze commit, dataset hashes, split, prompts, model settings, analysis script, exclusions and seed schedule. Store a signed/date-stamped manifest locally or in a versioned public research record when publication is authorized. Record every attempted episode and API failure. Repeat stochastic runs, but cluster uncertainty at the independent case-family level.

Run baselines before expensive ablations. Stop optional tests when the prespecified comparison is sufficiently resolved or a concrete defect requires repair. A discovered leakage defect invalidates affected runs: fix, version and rerun instead of hiding it.

### WP6: produce a manuscript and product demonstration

Create tables and figures from raw machine-readable results. Useful figures: task architecture; risk/coverage curves; correct supported decisions versus acquisition cost; paired counterfactual sensitivity; error distribution by applicability failure; case walkthrough with exact evidence chain. Never invent illustrative performance bars that could be read as results.

Draft introduction around the pharmaceutical evidence problem, methods around reproducibility, results around predeclared endpoints and discussion around applicability/limitations. Include negative results and cases where simpler baselines perform equally well. Map each claim to a table, figure or review record.

For the product, produce a 5-minute scenario: apparently complete CAPA → inspect evidence → identify wrong batch/window or recurrence → request correct record → explain the changed or unresolved decision → export a traceable draft report. This is a demonstration of behavior, not a claim of validated ROI.

## 3. Optional phases with explicit entry conditions

### RL

Proceed only if actions change what can be observed next and a heuristic/ranker cannot adequately solve the sequential decision. Freeze the language model and train a small action selector first. Separate training worlds and test families. Reward correct evidence-supported resolution, penalize unsupported decisions and acquisition cost, and evaluate abstention/coverage separately. Do not reward raw finding count. Compare with random, heuristic, supervised ranker and contextual bandit where appropriate.

### Process representation and digital twin

First create a versioned graph of batches, deviations, actions, records and effectiveness checks, with source links and timestamps. Call it an evidence/process model. A digital-twin claim later needs an identified real counterpart, update policy, fidelity criteria and validation of the intended predictions or decisions. A twin can represent a process; 3D graphics or real-time sensors are not mandatory. A fictional chat world alone is insufficient.

### Human training study

Only claim better learning or auditor performance after a separate study with relevant participants, prespecified outcomes and the required institutional/ethics determination. Prefer transfer to unseen cases and delayed assessment over satisfaction alone. Keep the first computational paper independent of this expensive phase.

## 4. Resource and cost controls

- Offline engineering and deterministic evaluation need no paid calls.
- Use a small development sample to estimate cost per episode before full runs.
- Set hard per-run token/cost/call ceilings, a per-case cap and a resumable ledger.
- Never tune on the final test or continue sampling only until a favorable result appears.
- Keep the number of model families small until a concrete generalization question justifies more.
- Local PDF and dataset folders are excluded from versioned source.
- Reserve time for provenance, annotation quality and failure analysis; these are central work, not final cleanup.

## 5. Definition of "ready to submit"

The paper has a coherent pharmaceutical question; accessible reproducible code and permitted data; locked evaluation; defensible labels; equal-budget comparisons; uncertainty; source-verified references; a data/model-use disclosure; and claims no broader than the evidence. Formatting to a journal template is the final packaging step. Journal selection is revisited after the evidence level is known.
