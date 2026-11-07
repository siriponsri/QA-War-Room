# Native benchmark development pipeline

Date: 7 November 2026. Status: implemented offline increment, ready for owner review. No paid provider, LLM inference, sequential benchmark or pharmaceutical validation is claimed.

## Requirement and observable result

The solo developer needs to check task semantics, leakage, metric arithmetic and resumable accounting before buying inference. The CLI creates a frozen cohort, passes only visible inputs into one adapter call per item, retains raw outputs/failures, and scores in a separate process. Acceptance requires hand-checkable metrics, no gold reads during inference, stable resume behavior and caps checked before each call. These are engineering conditions, not research findings.

The existing browser remains the synthetic CAPA evidence-review product. This CLI is a separate research foundation. It does not add model-generated advice to the UI or close a real CAPA.

## Reproducible setup

Use Python 3.10+ and the source workspace. The app and native CLI require only the standard library. No package was installed for this increment. The native CLI uses repository locks and is not yet advertised as a standalone installed-wheel interface.

```powershell
py -3 scripts/prepare_benchmarks.py --source benchmark-data
py -3 scripts/fetch_benchmark_protocols.py
py -3 -m unittest discover -s tests -v
```

Preparation verifies source bytes against the source manifest and the repository dataset lock, rejects document overlap across ContractNLI splits, separates inputs/gold, and records hashes/byte counts for prepared JSONL. Input loading checks those hashes and strict allowed fields again. Evaluator metadata includes DrugQA language/category/task/quality without exposing explanations or answers to the adapter.

`fetch_benchmark_protocols.py` is an explicit, free download of approximately 30 KB of pinned prompt/parser/metric references to ignored `benchmark-data/protocols/`. SHA-256 and byte counts are in `literature/native-protocol-lock.json`. It refuses to overwrite differing files. Downloaded reference code is inspected as text and never imported or executed. The canonical prompt is loaded as data and verified before use. Existing dataset LICENSE files remain applicable; the ContractNLI evaluator reference is Apache 2.0 and DrugQA references are from its CC BY 4.0 repository. These files are not included in public source by default; original code licensing still awaits the owner.

## Inputs and baseline paths

| Path | Model-visible input | Meaning |
| --- | --- | --- |
| ContractNLI full-context | Original complete contract, unchanged hypothesis, original character offsets and span texts/IDs | Single-call native-task input; local zero-shot instruction, not the original fine-tuned BERT procedure |
| ContractNLI lexical-retrieval | Hypothesis and top-k document-local BM25 spans, with original IDs/offsets | Declared retrieval baseline on native labels, not a sequential adaptation |
| DrugQA full-context | Canonical pinned system/user template, unchanged stored question, stored choices joined by newlines | Native bilingual zero-shot input; no added choice prefixes, examples or regulatory retrieval |

BM25 uses ASCII word tokens, k1=1.2, b=0.75, natural-log IDF and a fixed score/(1+score) transform. Ties use original span order. Retrieval scans only the current already-visible native contract. It does not index other documents, annotations, answers, gold rationales or an oracle. This free within-document search is legitimate for the native full-document task; it must not be reused as a free hidden-record search in G3.

The narrow adapter contract is `identity()`, `upper_bound(request, max_output_tokens)` and `predict(request, max_output_tokens) -> ModelResponse(raw, usage)`. Requests are detached JSON-compatible values. They contain no filesystem path, evaluator, provider key or tool capability. This is runtime interface isolation, not an operating-system sandbox against malicious code installed by the repository owner.

`OfflineAdapter` returns a hash-selected forced label/answer and lexical span scores. There are zero model tokens and USD 0 usage; source bytes and adapter invocations are recorded separately. It is a wiring fake, not an evidence-sufficiency or pharmaceutical baseline. Full-context and retrieval runs establish that the baseline *paths* execute. Their different fake accuracies do not establish a method advantage.

ContractNLI retains `Entailment`, `Contradiction`, `NotMentioned`; the last is never mapped to abstention. NLI output JSON must have exactly label, evidence_span_ids and span_scores. Citations must be unique visible integer span IDs. Every visible span needs a finite [0,1] score. Unselected retrieval spans receive zero during native ranking evaluation; no gold is used to select them.

DrugQA parsing follows the pinned reference priority: quoted selected_answer, quoted predicted_answer, then a standalone A-D letter. Raw output is retained, including tolerated non-JSON responses. No undocumented LLM repair or retry is performed. This parsing policy is more permissive than the prompt's requested JSON format and is recorded explicitly.

## Native metrics and limits

Definitions were checked against the [ContractNLI paper, section 4.2](https://aclanthology.org/2021.findings-emnlp.164.pdf), [dataset specification](https://stanfordnlp.github.io/contract-nli/), [pinned ContractNLI evaluator](https://github.com/stanfordnlp/contract-nli-bert/blob/058c56fd62d56897bb4fcfbf1be71b17aee3a79c/contract_nli/evaluation.py), and [pinned DrugQA scorer](https://github.com/DodgeLU/Sino-US-DrugQA/blob/cd026a27a5e039863de9080b8d7d95acaf1f5a39/analysis/score_results.py). The local implementation uses independent standard-library arithmetic and tiny fixtures; the upstream training/evaluation dependencies were not installed or run.

| Output | Definition |
| --- | --- |
| ContractNLI macro_label_micro_doc.class | Accuracy and F1(E)/F1(C) computed across documents for each hypothesis ID, then averaged over hypothesis IDs; “label” here means hypothesis, not three-way class |
| ContractNLI micro_label_micro_doc.class | Additional pooled classification diagnostic |
| ContractNLI micro_label_macro_doc.span.map | Average precision for each gold E/C document-hypothesis pair, then mean across pairs |
| ContractNLI micro_label_micro_doc.span.precision@recall80 | Pool all gold E/C span scores; use first tied-score threshold reaching recall >= .8 |
| ContractNLI micro_label_micro_doc.span.map | Additional pooled AP diagnostic |
| DrugQA overall/strata | Correct/frozen N, invalid count, valid-output coverage and native Wilson 95% diagnostic, by task, language, quality, raw object-domain category, task × language |

AP thresholds include all equal-score spans together; score ties are not arbitrarily ordered into optimistic ranks. Absent positive classes produce null F1, matching the reference evaluator's undefined/NaN treatment before macro averaging. Gold NotMentioned rows are excluded from evidence scoring, matching the upstream evaluator's explicitly optimistic convention. This does not mean the system's predicted NLI class must be correct for evidence ranking to receive credit.

Invalid, interrupted, context-limited and pending rows remain in the classification/MCQ denominator. A missing prediction cannot earn a correct native class. If any gold E/C item lacks valid scores, complete-cohort native evidence metrics are null; a separately named AP diagnostic assigns failed evidence items zero. No successful-only subset is silently substituted.

This is the reported native metric subset, not every ROC/binary/top-k diagnostic from the BERT training evaluator. No probability calibration metric or native model-score reproduction is claimed. Item-level Wilson intervals are source-comparison diagnostics, not a clustered study analysis. There is no universal combined audit score, inferred GMP subgroup, significance test or domain-validity claim.

## Cohort and run examples

```powershell
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --stop-after 5 --output runs/my-native-full
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --output runs/my-native-full --resume
py -3 -m qa_war_room.native score --output runs/my-native-full
py -3 -m qa_war_room.native run --dataset contractnli --split dev --limit 1 --baseline lexical-retrieval --top-k 5 --output runs/my-native-retrieval
py -3 -m qa_war_room.native score --output runs/my-native-retrieval
py -3 -m qa_war_room.native run --dataset drugqa --split all --limit 12 --output runs/my-native-drugqa
py -3 -m qa_war_room.native score --output runs/my-native-drugqa
```

ContractNLI limit is in source documents and keeps every associated hypothesis. One document gives 17 tasks, not 17 independent contracts. DrugQA only accepts all; no artificial official dev split is created. Its source-order smoke prefix is not held-out and must not be used for prompt tuning or training. Paired/language/source grouping requires a separate declared analysis design before a research run.

The manifest freezes ordered IDs and per-input hashes, source commits, preparation hash, prompt/implementation hashes, baseline parameters, adapter identity, caps, retry policy and development-only status. run and score are separate CLI processes: only score opens evaluator gold. The raw ledger never receives gold explanations or reference labels. Reports aggregate scores and remain local/ignored.

## Caps, failures and resume

Defaults: 50 adapter calls, 100,000 total input tokens, 50,000 total output tokens, 500,000 input bytes per item, 1,024 maximum output tokens per item, USD 0 per item/run. Flags are shown by `py -3 -m qa_war_room.native run --help`. Only offline adapters are enabled even if a larger USD cap is supplied. Current failure policy has zero retries; a real provider's retry policy would need an explicitly versioned, equally budgeted increment.

Before a call, reserve the adapter's input/output/cost upper bounds and fsync an attempt event. After the call, retain raw output, validated prediction, actual usage, status, wall time and error class. Unknown usage retains the full reservation. Exceptions are not logged verbatim because future provider errors may contain secrets. A usage-bound violation is retained and stops further calls, including on resume. Preflight controls assume an adapter honors its declared bounds; there is no external billing control implemented for a future provider.

`--stop-after N` pauses after N additional terminal items without changing the frozen cohort/caps. Resume skips all terminal items. An interrupted call is charged conservatively and marked interrupted_unknown_usage, never automatically repeated. Changed data/code/prompts/caps require a new output directory. Old outputs are retained. To raise a cap after a stopped run, create a new named run rather than silently altering a completed ledger.

Each event includes its frozen config hash, previous-event hash and own hash. A foreign-run ledger, edited event or malformed trailing write is rejected. This detects accidental corruption and mismatched runs; it is not a signed or regulated audit trail against an owner who rewrites every hash. A dedicated writer lock prevents concurrent writers. After a hard process kill, inspect the PID in .writer.lock and confirm it is no longer running before manually removing that stale lock. Preserve a torn ledger for inspection before an explicit recovery; the runner never truncates it or silently reissues an uncertain call.

## Next provider and research gate

Before implementing/running paid inference, obtain the owner's provider/model choice, server-side key setup, USD pilot/run ceilings and data-processing permission. Verify current official pricing for that chosen model, estimate cost from a small *authorized* development pilot, then add a provider-specific adapter with conservative preflight bounds, explicit actual-usage accounting, timeout/context behavior and a frozen retry policy. No key or provider was selected or charged in this session.

G3 is now implemented separately as `qawr-contractnli-sequential-v1`; see [SEQUENTIAL_BENCHMARK.md](SEQUENTIAL_BENCHMARK.md). It provides initial observations, request/submit/abstain actions, acquisition costs, grouped source splits and evaluator-only coverage-proxy reachability. The native retrieval baseline remains a different task. Independent pharmaceutical reference review, confirmatory locks, a real pilot and manuscript results are later gates.
