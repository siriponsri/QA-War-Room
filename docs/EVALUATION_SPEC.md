# QA War Room: evaluation specification

**Version:** 0.1, 7 November 2026.  
**Purpose:** an implementation contract for a reproducible computational study of evidence sufficiency and sequential evidence requests.  
**Status:** prospective specification. Examples of schemas and configuration below describe requirements for the research runner; they do not imply that the small offline demo already implements a full benchmark harness.  
**Related documents:** [Research protocol](RESEARCH_PROTOCOL.md) and [Journal strategy](JOURNAL_STRATEGY.md).

G5 implementation note (7 November 2026): [G5_EVALUATION_PLAN.md](G5_EVALUATION_PLAN.md) and `plans/g5-evaluation-plan-v1.json` define the implemented offline engineering subset: public-input matrix lock, matched budgets, durable source replay, evaluator-only fixed-denominator descriptive metrics and paired-family arithmetic. Scientific Stage B estimates/intervals and primary comparison remain NOT_RUN; current author-draft references cannot produce a confirmatory lock. Independent review/adjudication are still pending. The broader research specification below remains prospective unless explicitly implemented.

## 1. Evaluation layers and permitted claims

| Layer | Inputs | Reference | Permitted interpretation |
|---|---|---|---|
| Engineering smoke checks | Six included synthetic cases | Their explicit authored rules | The implemented paths behave as specified on these examples |
| Native benchmark | Original released task and split | Original reference labels and official scorer where available | Performance on that named task and evaluation set |
| Derived sequential benchmark | Controlled disclosure of benchmark material | Original source target plus separately specified evidence-access evaluation | Performance under the new interaction protocol |
| Constructed GMP transfer | Original synthetic manufacturing records and a declared decision policy | Independently specified case reference, with review provenance | Performance under the assumptions of the constructed cases |
| External applicability | Independently sampled and reviewed manufacturing cases | Qualified independent review and adjudication | Bounded evidence about the specified manufacturing use case |

Do not pool these layers into one denominator or a single “audit accuracy.” A smoke-check success is not a scientific result; a native benchmark score is not a GMP finding; a constructed case is not a real audit gold standard.

In the current smoke runner, `reference_support_coverage` means authored evidence-ID set completeness; it is not the selective decision coverage defined in section 8. `false_supported_rate_on_non_supported` uses the FSR denominator below, but only on eight authored cases from two templates. Its 32 episodes (eight cases × four scripted policies) are engineering checks; native benchmark metrics and LLM experiments have not been run.

## 2. Dataset admission and native reproduction

Implementation note (7 November 2026): an offline native runner and the reported native metric subset are now implemented in `qa_war_room/native*.py`. See [NATIVE_BENCHMARK.md](NATIVE_BENCHMARK.md) for exact averaging, missing-output denominators and source pins. Deterministic wiring smoke outputs are not LLM experiments or pharmaceutical evidence; the study protocol below remains prospective.

### 2.1 Required source manifest

For every admitted dataset, preserve:

- Name, canonical URL, associated paper/DOI, and verified publication status.
- Download timestamp, immutable revision or release, original filename, byte count, and SHA-256.
- Dataset licence, code licence, source-text rights, and required attribution, recorded separately.
- Original split name, original item/source IDs, and original labels without destructive renaming.
- Any transformations, parser versions, filtering rules, and source-to-derived ID map.
- The exact public fields available for grouping and subset selection.
- Counts before/after parsing, exclusions by reason, and duplicate or malformed records.

Do not execute repository scripts merely because they came with a dataset. Review their dependency and data-loading behavior, then use a pinned environment. Keep research imports separate from the offline starter.

### 2.2 ContractNLI

Use the official dataset and retain `Entailment`, `Contradiction`, and `NotMentioned` semantics. Evidence is span-based; the task is described in its Findings of EMNLP 2021 paper and official project. The published corpus contains 607 NDAs and 17 fixed hypotheses, so hypothesis rows within a contract are not independent source samples. [Paper](https://aclanthology.org/2021.findings-emnlp.164/) · [Official project](https://stanfordnlp.github.io/contract-nli/)

Implementation requirements:

1. Preserve document split membership before any derived disclosure or paraphrase generation.
2. Retain character offsets and original span IDs. Normalize text only with an invertible offset map.
3. Check that every cited span exists and maps to the original document.
4. Use official classification/evidence metrics when reproducing the native task; clearly label any added metric.
5. Do not treat missing evidence annotations on `NotMentioned` examples as an arbitrary empty citation target for every task.
6. Do not assume the annotated span union is an enumerated collection of minimal sufficient evidence sets.
7. Evaluate hypotheses as a group for uncertainty at the contract/source-family level.

### 2.3 SciFact

Use claim verification, abstract retrieval, and rationale selection as distinct tasks. The official repository exposes train/dev labels and describes its test labels as withheld. It distinguishes oracle from open retrieval. [Paper](https://aclanthology.org/2020.emnlp-main.609/) · [Official repository](https://github.com/allenai/scifact)

Choose and freeze one of these valid local routes:

- Develop and calibrate using only source-grouped partitions of the released training data; evaluate once on the untouched official development set. Name the result **held-out evaluation on the official development split**.
- Use a documented nested, source-grouped evaluation on public labelled data. Name it **researcher-defined cross-validation**, not official test performance.
- If an official evaluation service remains available and usable, follow its current procedure and distinguish its results from local analyses.

Never fabricate test labels from a model or relabel dev as test. In the claim-verification setting, absence of retrieved evidence is not proof that a claim is false. Preserve document-level support/refutation semantics and any task-specific handling of multiple evidence documents.

### 2.4 Sino-US-DrugQA

The publication is Fu, Chen, and Lu, *PLOS One* 21(9):e0343858, 15 September 2026. The official repository provides the authoritative bilingual release, reference evaluation material, and a separate English companion. It declares CC BY 4.0 and no training split. Use the paper/repository rather than older preprint counts. [Publisher](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858) · [Repository](https://github.com/DodgeLU/Sino-US-DrugQA)

Required policies:

- Native reproduction uses the authoritative bilingual questions/choices and the original task settings. Additional RAG or interactive variants are named adaptations.
- Keep `pass` and `borderline` strata visible. Report the full native release for comparability and a predeclared `pass`-only sensitivity analysis; do not remove difficult items after seeing model errors.
- Report language, task type, and drug/non-drug category strata. These are regulatory knowledge questions, not manufacturing deviation dossiers.
- Do not use the English companion to claim reproduction of the original bilingual experiment. Do not put translations of the same question in development and evaluation partitions.
- The inspected release has no item-level `functional_subdomain` field or scorer derivation for it. The dataset-card manufacturing/quality summary does not create an available GMP row filter. Use a verified author mapping or a new, independently documented annotation protocol before claiming a GMP subset.
- The published release is an evaluation resource. Do not fine-tune or train an RL policy on its answers and then present performance on the same questions as generalization.
- For a custom development/holdout split, name it explicitly, group related sources/siblings, and lose any claim of untouched zero-shot reproduction for the development items.
- Record the regulatory corpus date. A correct answer against that snapshot is not a claim about the law in force on the date of a future deployment.

Dataset-card details: https://github.com/DodgeLU/Sino-US-DrugQA/blob/main/DATASET_CARD.md

## 3. Normalized data contracts

G3 implementation note (7 November 2026): [SEQUENTIAL_BENCHMARK.md](SEQUENTIAL_BENCHMARK.md) defines the implemented `qawr-contractnli-sequential-v1` controlled-disclosure contract. It preserves original labels, adds an explicit abstention action, records family-grouped descendants and measures published-reference coverage as a proxy. Its oracle is evaluator-only. The broader schemas, calibrated outputs, semantic assessment, counterfactuals and confirmatory analysis below remain prospective where not explicitly implemented.

These are proposed internal schemas. Adapters must retain the original records and an invertible mapping; they must not pretend that normalized fields were present in the source dataset.

### 3.1 Model-facing episode

```json
{
  "episode_id": "derived-source-017-v1",
  "track": "derived_interactive",
  "source_id": "source-017",
  "decision_target": "document_claim_support",
  "assessment_date": null,
  "question": "The original or explicitly derived claim text",
  "scope": {"source_collection": "collection-001"},
  "initial_evidence_ids": ["unit-03"],
  "available_actions": ["search", "open_record", "stop"],
  "budget_id": "frozen-budget-small",
  "policy_version": "task-policy-v1"
}
```

Do not expose `gold_label`, sufficient-evidence sets, mutation labels, or grading keys in this object. An episode ID must not encode the answer. `assessment_date` is used only when the case has valid temporal semantics; do not manufacture dates for native tasks.

### 3.2 Evidence record

```json
{
  "evidence_id": "record-004:span-12",
  "source_id": "source-017",
  "document_id": "record-004",
  "document_version": "v2",
  "content_hash": "sha256-of-original-content",
  "text": "Exact permitted source text",
  "span_start": 210,
  "span_end": 392,
  "effective_from": null,
  "effective_to": null,
  "recorded_at": null,
  "scope": {},
  "provenance_uri": "canonical-source-or-original-case-id"
}
```

Distinguish creation, approval, effective, observation, and ingestion dates when a case supplies them. A later ingestion date does not automatically make a historically valid record inadmissible; the declared assessment policy decides what was knowable and admissible at the time.

### 3.3 Hidden evaluator record

```json
{
  "episode_id": "derived-source-017-v1",
  "original_split": "test",
  "source_family_id": "family-017",
  "variant_family_id": "source-017-all-descendants",
  "reference_label": "CONTRADICTED",
  "reference_label_origin": "official_source_label",
  "reference_evidence_ids": ["unit-11", "unit-12"],
  "minimal_sufficient_sets": null,
  "reference_policy_version": "task-policy-v1",
  "label_created_at": "recorded-date",
  "review_status": "official_native_label",
  "transformations": ["controlled_disclosure_v1"]
}
```

`reference_evidence_ids` are not necessarily minimal or exhaustive. A `null` minimal-set field means such a reference is unavailable, not an empty set that a model satisfies without evidence. For new GMP cases, `reference_label_origin` must identify author construction and independent-review status honestly.

### 3.4 Model result

```json
{
  "episode_id": "derived-source-017-v1",
  "native_forced_label": "Contradiction",
  "class_probabilities": {
    "SUPPORTED": 0.08,
    "CONTRADICTED": 0.82,
    "INSUFFICIENT_EVIDENCE": 0.10
  },
  "action": "CONTRADICTED",
  "abstention_reason": null,
  "findings": [
    {
      "claim": "A narrowly specified finding",
      "citations": ["record-004:span-12"],
      "scope": "The scope actually supported by the citation"
    }
  ],
  "missing_evidence": [],
  "next_request": null,
  "stop_reason": "decisive_admissible_evidence"
}
```

The example numbers are illustrative schema values, not study results. For MCQ tasks, preserve option labels/probabilities separately rather than forcing them into an entailment label schema.

## 4. Labels, recommendations, and abstention

Use three conceptual evidence states where the task supports them:

- `SUPPORTED`: the specified proposition is supported under the reference task policy.
- `CONTRADICTED`: admissible evidence supports a conflicting proposition or fails an explicit decisive condition in the task.
- `INSUFFICIENT_EVIDENCE`: the source collection does not establish support or contradiction for the proposition under the task definition.

Add `ABSTAIN` as a **model action**, not a replacement for a reference class. A model can abstain because it lacks confidence, failed retrieval, encountered an unresolved applicability question, exceeded its budget, or could not produce a valid output. These reasons should be distinguishable.

For GMP cases, record the specific decision target: implementation, effectiveness, investigation adequacy, or closure recommendation. A case can support implementation while leaving effectiveness indeterminate. A correct `INSUFFICIENT_EVIDENCE` decision can be a useful completed assessment; it is not the same as the model refusing to assess.

Keep two outputs when feasible:

1. A forced native-task prediction for transparent comparison with the original benchmark.
2. A selective action using a threshold calibrated only on allowed development data.

Do not improve a native benchmark score by excluding abstentions from its denominator. Selective metrics have a separate denominator and must be reported with coverage.

## 5. Controlled interaction and admissibility

### 5.1 Environment procedure

For each episode:

1. Construct the immutable source collection and eligibility policy.
2. Load the same initial evidence for all compared systems.
3. Reset memory, caches that contain case-specific information, and all agent state.
4. Accept one structured action at a time.
5. Resolve the action from the frozen collection and permissions.
6. Append the exact returned text, evidence IDs, result status, and cost to the visible ledger.
7. Stop on a valid terminal action or a predefined cap.
8. Send only the submitted outputs and observable trace to the evaluator; do not let the evaluated agent inspect hidden references.

Environment errors must be distinguishable from model errors. The trace should record whether a requested record was available, absent from the collection, disallowed, malformed, or unavailable because of a runtime problem.

### 5.2 Evidence constraints

A submitted finding is structurally admissible only when all cited records exist and were visible before the finding was made. Additional checks on temporal applicability, scope, approval, or version depend on the declared task policy. Every check returns a reason code.

Deterministic checks can verify record existence, visibility, offsets, date comparisons, and exact scope fields. They cannot generally prove that a natural-language citation entails an arbitrary finding. Semantic evidence assessment therefore needs original rationale metrics, an independently labelled reference, or a separately validated evaluator. An LLM judge may be an auxiliary metric, not the sole primary reference.

### 5.3 Native versus partial-context truth

Suppose a full contract supports a claim but the agent has seen only an unrelated paragraph. The source-level target remains supported. A source-label accuracy metric can count a lucky supported guess as correct, while an observed-evidence metric correctly marks its justification as unsupported.

Report both. Do not relabel the full contract as `NotMentioned` simply because a retrieval step missed its relevant paragraph. Conversely, do not reward a guessed correct answer as an adequately evidenced assessment.

### 5.4 Time and version transformations

Add temporal/version cases only when the transformation defines:

- Which timestamp is changed and what it means.
- Which policy is effective at the assessment date.
- Whether a later record reflects an earlier fact or introduces information unavailable at the decision date.
- Whether the changed version applies to the same site, line, product, or procedure.
- Which reference outcome should change and why.

Counterfactuals must be internally coherent. Changing one date may require updating linked references, schedules, or record histories. A string replacement alone is not proof of a valid counterfactual.

## 6. Resource and information budgets

Use a vector of caps, not one headline call count:

| Budget component | Counted resource |
|---|---|
| Model requests | Every investigator, reviewer, summarizer, and verifier call |
| Input tokens | All prompts, evidence, histories, repeated contexts, and tool outputs |
| Output tokens | All agent responses, including intermediate drafts and rejected parses |
| Retrieval requests | Searches, reranks, category requests, and failed requests |
| Evidence exposure | Number of unique units and total source tokens returned |
| Wall-clock limit | End-to-end elapsed episode time, with declared concurrency |
| Monetary cost | Dated provider prices, cached-token treatment, and paid tool usage |

Internal model reasoning tokens may be reported differently across providers. Record the provider's fields and any unknown accounting; do not pretend all models offer comparable hidden-compute measurements.

Equalize both the allowed vector and the initial information. Report actual consumption. A method that uses less than its cap can be valuable; unused budget need not be forced into meaningless calls.

For a one-pass RAG comparator, allow a development-selected retrieval strategy and an input allocation competitive with the sequential system's total admissible evidence exposure. For an equal-budget review comparator, permit the same aggregate model work. Run an additional quality/cost curve over a small frozen set of budgets rather than claiming equivalence from a single cap.

A full-context model that sees every record is useful, but it must be labelled a different access condition when its exposure exceeds the interactive cap. Oracle access is a diagnostic condition even if its token cost is small.

## 7. Baseline registry and oracle separation

The research runner should register each system with a stable ID and immutable configuration hash. At minimum implement B0 rules, B1 one-pass RAG, B2 sequential single agent with a ledger, B3 equal-budget self-review, and P1 investigator/reviewer before claiming multiagent benefit.

Use separate result tables for:

| Retrieval regime | Allowed information | Interpretation |
|---|---|---|
| Deployable | Query, visible history, admissible document content/metadata | Main end-to-end evaluation |
| Oracle documents | Gold relevant document IDs | Diagnostic inference with retrieval advantage |
| Oracle spans | Gold rationale/evidence units | Diagnostic reasoning given privileged evidence |
| Full context | All admissible documents | Access/context diagnostic; check budget comparability |

Gold IDs must not influence deployable chunking, ranking, document menus, stopping, prompts, or adaptive requests. It is acceptable to calculate diagnostic oracle metrics after predictions are frozen, provided they are not mixed into the deployable result.

Report retrieval recall and reasoning conditional on successful retrieval separately. A conditional score uses a selected subset and is not an end-to-end success rate.

## 8. Endpoints and formulas

### 8.1 Notation

For eligible episode \(i\), let \(y_i\) be the reference evidence class, \(a_i\) the terminal selective action, \(\hat y_i\) the forced prediction, and \(w_i\) a predeclared analysis weight. Default \(w_i=1\) gives an item-weighted result. Let \(S\) mean supported and \(A\) mean model abstention.

Use fixed denominators determined by the frozen eligible cohort, not by which outputs were easy to parse. A zero denominator is `not estimable`, not zero error.

### 8.2 Primary endpoint: false-support rate

\[
\operatorname{FSR} =
\frac{\sum_i w_i\,\mathbf{1}(y_i\ne S\;\land\;a_i=S)}
{\sum_i w_i\,\mathbf{1}(y_i\ne S)}.
\]

This measures acceptance of a proposition whose source reference does not support it. For the constructed GMP closure task, call the corresponding metric **false supported closure recommendation rate** and give the exact closure-policy denominator. Do not call ContractNLI FSR an observed pharmaceutical closure-error rate.

The primary contrast is \(\Delta=\operatorname{FSR}_{P}-\operatorname{FSR}_{B}\), with negative values favoring the proposed method. Compare the same source episodes under the same budget and deployable information regime.

### 8.3 Guardrails against trivial refusal

Report and predeclare acceptable values/margins for:

\[
\operatorname{SupportedSensitivity}=
\frac{\sum_i w_i\,\mathbf{1}(y_i=S\;\land\;a_i=S)}
{\sum_i w_i\,\mathbf{1}(y_i=S)}
\]

and

\[
\operatorname{Coverage}=
\frac{\sum_i w_i\,\mathbf{1}(a_i\ne A)}{\sum_i w_i}.
\]

Also report forced-label macro-F1 or the native task's appropriate overall score. Predicting `INSUFFICIENT_EVIDENCE` for everything has full coverage but zero supported sensitivity; abstaining for everything has zero coverage. Neither qualifies as a successful evidence-sufficiency method.

A confirmatory H1 claim requires the primary improvement and every frozen guardrail. Select sensitivity-loss margins, coverage floors, and practical effect thresholds before viewing held-out predictions. They are task-design choices, not universal GMP limits.

One explicit decision rule for the locked analysis is the following. Freeze a minimum relevant FSR reduction `d_min`, tolerated sensitivity loss `m_s`, tolerated native-score loss `m_f`, and minimum coverage `c_min`. Using the predeclared paired clustered intervals, require all of:

- The upper confidence limit for `FSR_proposed - FSR_comparator` is below `-d_min`.
- The lower confidence limit for the supported-sensitivity difference is above `-m_s`.
- The lower confidence limit for the native overall-score difference is above `-m_f`.
- The lower confidence limit for the proposed method's coverage is at least `c_min`.
- Resource and run-validity requirements are met under the frozen failure policy.

This is a joint success rule; failure of any condition prevents the combined H1 claim. Setting `d_min` to zero asks about any improvement; a positive value asks for an improvement of practical size. Choose the rule and values before unblinding, rather than changing them after seeing the intervals. The protocol may instead use another justified rule, but the replacement must be frozen and disclosed.

### 8.4 Complementary support metrics

- **Unsupported share among accepted supports:** incorrect supported decisions divided by all supported decisions. This is useful for reviewing an accepted worklist but is unstable when very few items are accepted.
- **Evidence-valid support share:** submitted supported findings that pass the specified structural and semantic evidence checks divided by all submitted supported findings.
- **Warranted supported recall:** gold-supported episodes accepted with valid observed evidence divided by all gold-supported episodes, where the validity reference is available.
- **Contradiction detection:** recall/precision for reference contradiction cases; distinguish a missed contradiction from correct insufficient-evidence classification.
- **Insufficiency classification:** precision/recall for genuine source-level insufficient evidence, separate from model abstention.
- **Per-class confusion matrix:** include abstention and invalid outputs rather than hiding them.

Keep source-label errors and evidence-justification errors separate. A correct label with an invalid citation and an incorrect label with a relevant citation are different failure modes.

### 8.5 Native metrics

- ContractNLI: original NLI and evidence-identification metrics, plus the declared added FSR and selective metrics.
- SciFact: original document/label/rationale measures for the chosen protocol, with open and oracle retrieval separated.
- Sino-US-DrugQA: MCQ accuracy by original task/language/quality/domain strata, with abstention-aware coverage and proper probability metrics as additions. Do not map multiple-choice distractors to fabricated GMP failure labels.

Use the official scorer where practical, test adapter compatibility on development examples, and record any deviation from it. A matching metric name is not enough if the unit, averaging, or denominator has changed.

### 8.6 Sequential efficiency

Report requests, unique evidence units, source tokens, model tokens, cost, and elapsed time per episode. Summarize both successful and failed episodes.

When an independent minimal-sufficiency reference exists, add:

- Requests/time until first sufficient evidence is observed.
- Extra requests after sufficient evidence was already available.
- Probability of requesting a decisive missing category within the cap.
- Utility relative to fixed-order or random requests.

When minimal sufficiency is not annotated, do not invent an “optimal next question” accuracy. Use directly observable outcomes and label any information-gain estimate as a proxy.

## 9. Calibration and selective prediction

Obtain normalized probabilities using a specified method. Self-reported confidence, token likelihood, and a learned calibration head are different measurements. Do not compare them as though they were interchangeable.

Fit any calibration mapping and selection threshold only on permitted development/calibration groups. Freeze it before evaluation. Report:

- Brier score or a suitable multiclass proper scoring rule.
- Log loss when probabilities are valid and clipping rules are predeclared.
- Reliability plots with fixed bins and sample counts.
- Risk/coverage curves and class-specific risk, with uncertainty where feasible.
- The operating point actually selected on development data and its achieved evaluation coverage.

Report expected calibration error only as an auxiliary summary because it depends on binning and can conceal sparse high-confidence errors. A nice reliability plot does not establish a guaranteed error bound.

If comparing methods at a common coverage, use a procedure frozen on calibration data and report the resulting evaluation coverage. Post hoc selection of a threshold using evaluation errors is not a deployable operating point. An evaluation-set risk/coverage curve can be descriptive, but it must not be represented as a validated deployment threshold.

Do not describe conformal or risk-control guarantees unless the implemented method, assumptions, calibration sample, and deployment distribution justify the exact claim. Distribution shift between contracts and manufacturing records is a separate problem.

## 10. Splits, source clusters, and counterfactual families

### 10.1 Split before transformation

Build source groups first, assign partitions, then generate variants within each partition. All descendants of a source remain together. Related forms, translations, cited abstracts, or repeated provision questions can require a larger source-family group than a document ID alone.

Maintain two separate artifacts:

1. An official-split mapping for native reproduction.
2. A researcher-defined source-family mapping for derived studies and uncertainty estimates.

Do not change an official split silently to improve an independence claim. Publish overlap diagnostics and, if needed, a separate stricter generalization analysis.

### 10.2 Counterfactual design

Distinguish:

- **Label-preserving changes:** wording, display order, harmless identifiers, irrelevant distractors.
- **Label-changing changes:** an explicitly decisive contradiction, applicable-version change, scope mismatch, or timing condition changes the reference under a specified rule.
- **Ambiguous changes:** require human adjudication or exclusion from confirmatory scoring before model evaluation.

Include both transformation types. Always changing the label when any edit occurs makes edit detection a shortcut. Keep source/variant pairs in the same split and bootstrap cluster. Report consistency for label-preserving pairs and appropriate response for label-changing pairs; these are not independent samples.

### 10.3 Leakage audit

Before a locked run, verify that:

- No answer keys or evaluator references are indexed.
- No case family spans development and held-out evaluation in the derived track.
- No baseline or proposed method receives hidden episode metadata.
- No few-shot example is a transformed sibling of an evaluated item.
- Retrieval indexes are created without gold target labels.
- File names, record IDs, or document order do not deterministically reveal the reference class.
- Any caches or provider conversation history are reset between independent episodes.

Do not claim that this eliminates all possible pretrained benchmark contamination. It prevents controllable project-level leakage.

## 11. Label quality and reference adjudication

For native labels, preserve disagreements/corrections if the publisher releases them and identify the exact version. For new cases, collect a reference decision, rationale, admissible evidence, uncertain alternatives, and reviewer provenance.

An economical solo workflow is:

1. Author cases from a written policy and hidden state representation.
2. Use mechanical validation to check internal consistency and references.
3. Perform a delayed self-review without looking at model predictions, recording changes.
4. Mark the resulting set as **author-constructed**, not independently validated.
5. Seek independent manufacturing QA review before making strong domain claims; review should be blinded to system identity and, when possible, to the author's preferred outcome.

For an external review extension, reviewers should label cases independently before reconciliation, explain disagreements, and record adjudication. Report agreement by class and case family, not only a single agreement coefficient. The number and expertise of reviewers, case sampling, conflicts of interest, and any remuneration are part of the methods.

If a case remains genuinely ambiguous, preserve that ambiguity. Predeclare whether it is excluded from the primary endpoint, scored with an allowed-label set, or placed in a separate ambiguity stratum. Do not choose the treatment after observing which system benefits.

## 12. Statistical analysis and sample-size work

### 12.1 Paired clustered analysis

Use the same episodes for all compared systems. The default confidence interval procedure resamples independent source-family groups, carrying all their rows, language siblings, variants, and repeated runs together. Recompute the paired metric difference in each replicate.

Record bootstrap method, number of replicates, random seed, strata, interval construction, and treatment of empty class denominators. Validate analysis code on small hand-checkable examples before the real evaluation. Do not treat one resampled document's 17 hypotheses as 17 independent contracts.

Where few clusters, highly unequal clusters, or rare errors make a bootstrap unstable, use an appropriately justified model or conservative interval and report limitations. A single approach is not automatically valid for every dataset.

### 12.2 Rare events

Zero observed false supports does not prove a zero population rate. If evaluating independent Bernoulli source-level outcomes, exact/binomial bounds may be appropriate. If rows are dependent, a row-level binomial interval is not justified simply because there are many rows.

One conservative additional endpoint is “any false supported decision within a source family.” Its interval describes a source-family risk, not the original item-level FSR. Label the change of estimand clearly. Do not report a degenerate bootstrap interval `[0, 0]` as a safety guarantee.

### 12.3 Feasibility and power

Prepare a development-only table with candidate independent source counts, class prevalence, cluster sizes, paired discordance, average episode cost, and observed runtime failure rates. Simulate the planned analysis across plausible effect and correlation scenarios. The minimum meaningful effect and acceptable loss margins must come from the research goal and intended use, not from whichever numbers make the available sample look sufficient.

If resources cannot support the planned precision, options are to narrow the hypothesis, reduce the system matrix, gather more independent sources, or present an estimation/feasibility study. More stochastic repeats can characterize model variability but do not replace more independent source cases.

### 12.4 Multiplicity

Within each separately locked stage, the default plan has one confirmatory H1 comparison, accompanied by mandatory guardrails. All must meet their frozen criteria before claiming the combined benefit. Stage A uses the derived open-data task; the pharmaceutical-target Stage B must designate independently reviewed Track G Manufacturing GMP as primary or as a predeclared key confirmatory endpoint with appropriate multiplicity control. Native benchmarks are auxiliary in Stage B. Treat other datasets, subgroups, ablations, and H2–H5 as exploratory unless a separate multiplicity or hierarchical testing plan is declared.

Do not turn whichever subgroup has the smallest p-value into the primary result. Report effect sizes and uncertainty even when no confirmatory claim is supported. Non-significance is not equivalence.

## 13. Run failures and invalid outputs

Predefine the following policy before evaluation:

| Event | Required handling |
|---|---|
| Malformed model output | Apply a frozen parser/repair policy, charge its cost, retain the original output |
| Unknown citation | Mark citation invalid; do not silently replace it with a plausible source |
| Cap exceeded | Terminate or truncate under a predefined rule; report the overrun |
| Timeout/provider error | Apply the same retry limit/backoff policy to all methods; retain all costs and status |
| Context overflow | Record as a failure unless an approved predeclared compression strategy exists |
| Evaluator bug | Preserve original results, document the correction, rerun all affected comparisons |
| Dataset corrupt record | Apply a predeclared exclusion rule without consulting system performance |
| Reference ambiguity discovered after unblinding | Retain the original primary analysis and add a documented sensitivity analysis, unless a full preregistered correction policy applies |

Provide both intention-to-evaluate results over the frozen cohort and any successful-runtime-only diagnostic. Report the latter as selected and do not use it to conceal a system with frequent failures.

## 14. Error taxonomy

Annotate a predeclared stratified sample of errors, plus all rare high-impact false support types if feasible. Keep the reviewer unaware of method identity where practical. An episode can have more than one error code.

| Code | Meaning |
|---|---|
| `RETRIEVAL_MISS` | Available decisive evidence was not acquired |
| `CITATION_ABSENT` | A cited unit does not exist or was not visible |
| `CITATION_NON_SUPPORT` | The citation is real but does not justify the finding |
| `CONTRADICTION_IGNORED` | Relevant conflicting evidence was overlooked or dismissed without support |
| `EXCEPTION_MISREAD` | A qualifying clause or exception was misinterpreted |
| `SCOPE_MISMATCH` | Evidence concerns a different line/site/batch/product/person or period |
| `VERSION_MISMATCH` | An inapplicable or superseded version is treated as controlling |
| `TEMPORAL_LEAK` | A decision relies on evidence inadmissible at the assessment date |
| `PLAN_AS_COMPLETION` | Planned activity is treated as implemented |
| `IMPLEMENTED_AS_EFFECTIVE` | Implementation is treated as evidence of effectiveness |
| `EXPOSURE_IGNORED` | A trend interpretation ignores relevant exposure/denominator changes |
| `ABSENCE_AS_PROOF` | Failure to retrieve a record is treated as proof of its absence or of a false proposition |
| `POLICY_INVENTED` | The system adds a requirement or closure rule absent from the declared task |
| `UNNECESSARY_ABSTENTION` | The system abstains despite adequate available evidence under the task |
| `PREMATURE_STOP` | The policy stops before addressing a material unresolved issue |
| `OVER_REQUEST` | Additional requests do not improve the decision after sufficiency was established |

Do not assign GMP-specific errors to a contract benchmark without a legitimate analogue. Keep “the system disagreed with the reference” separate from the explanatory error code.

## 15. Result tables and figures

The eventual report should contain:

1. Dataset/version/split/source-group inventory and label provenance.
2. Native metrics in separate tables for each dataset.
3. Main deployable comparison with FSR, supported sensitivity, coverage, native overall score, valid-evidence share, and actual resource use.
4. Paired differences with clustered confidence intervals and the frozen success criteria.
5. Oracle/full-context diagnostics in their own table.
6. Ablations and budget curves.
7. Risk/coverage and calibration plots.
8. Transformation-family and domain-transfer results.
9. Runtime failures, excluded records, and protocol deviations.
10. Error taxonomy counts and a small, balanced set of exact evidence-based case analyses.

Use empty templates until experiments are actually run. Never put plausible-looking synthetic values in a table labelled “results.” Any illustrative chart must be explicitly marked as illustrative and kept out of reported findings.

## 16. Configuration to freeze

This template is deliberately incomplete and describes **Stage A methods feasibility**, not the primary pharmaceutical study. A research runner should refuse a confirmatory label while any required field remains unresolved.

```yaml
study_id: qa-war-room-evidence-v1
study_stage: A_methods_feasibility
status: pilot
primary_track: derived_contractnli
primary_endpoint: false_support_rate
primary_comparator: TO_BE_FROZEN_AFTER_DEVELOPMENT
dataset_revision: TO_BE_FROZEN
source_group_manifest_sha256: TO_BE_FROZEN
evaluation_ids_sha256: TO_BE_FROZEN
model_revision: TO_BE_FROZEN
prompt_bundle_sha256: TO_BE_FROZEN
retriever_revision: TO_BE_FROZEN
calibration_groups_sha256: TO_BE_FROZEN
budget:
  model_calls: TO_BE_FROZEN
  input_tokens: TO_BE_FROZEN
  output_tokens: TO_BE_FROZEN
  retrieval_requests: TO_BE_FROZEN
  source_tokens_exposed: TO_BE_FROZEN
  wall_clock_seconds: TO_BE_FROZEN
guardrails:
  minimum_relevant_fsr_reduction: TO_BE_FROZEN
  supported_sensitivity_loss_margin: TO_BE_FROZEN
  minimum_coverage: TO_BE_FROZEN
  overall_score_loss_margin: TO_BE_FROZEN
analysis:
  confidence_level: 0.95
  clustering_unit: source_family
  weighting: item_weighted
  interval_method: TO_BE_FROZEN
  stochastic_repetitions: TO_BE_FROZEN
  secondary_comparisons: exploratory
failure_policy_revision: TO_BE_FROZEN
label_policy_revision: TO_BE_FROZEN
```

Values should be chosen from development feasibility, a declared practical target, and a budget the researcher can sustain. The template does not promise a detectable effect at any particular sample size.

For the pharmaceutical-target manuscript, create a separate Stage B lock before unblinding its evaluation: set `study_stage: B_pharmaceutical`, `primary_track: independently_reviewed_manufacturing_gmp`, and `primary_endpoint: false_supported_closure_or_effectiveness_claim_rate` with the exact claim and denominator specified. Freeze its independent reference-review record, held-out source families, comparator, guardrails, budgets, and analysis; native tasks become auxiliary. If Track G review/evaluation is unavailable, retain the Stage A technical-paper route and do not claim pharmaceutical impact. Results already viewed cannot be promoted retrospectively into a confirmatory Stage B test.

## 17. Research-run acceptance criteria

Before accepting an experiment as reproducible evidence, verify:

- The data and source-group counts match the frozen manifest.
- Original and derived splits are distinguished.
- Agents cannot access gold labels or hidden state.
- The exact visible evidence trace can be replayed.
- Budgets include all agents and intermediate work.
- Model versions and prompts are recorded.
- Metric numerators and denominators can be independently recomputed.
- Confidence intervals respect the declared clustering.
- The primary comparison and guardrails were locked before unblinding.
- Negative and failed runs are retained.
- Domain claims match the highest completed validation layer.

These are study-quality requirements. Passing them does not certify a product or establish that an AI may make an authorized GMP decision.

## 18. Primary references

1. Koreeda Y, Manning CD. *ContractNLI*. Findings of EMNLP, 2021. https://aclanthology.org/2021.findings-emnlp.164/
2. ContractNLI official project and dataset terms. https://stanfordnlp.github.io/contract-nli/
3. Wadden D and colleagues. *Fact or Fiction: Verifying Scientific Claims*. EMNLP, 2020. https://aclanthology.org/2020.emnlp-main.609/
4. SciFact repository, data schema, and evaluation instructions. https://github.com/allenai/scifact
5. Fu X, Chen Z, Lu W. *Sino-US-DrugQA*. *PLOS One*, 2026. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858
6. Sino-US-DrugQA repository. https://github.com/DodgeLU/Sino-US-DrugQA
7. Sino-US-DrugQA dataset card. https://github.com/DodgeLU/Sino-US-DrugQA/blob/main/DATASET_CARD.md

The evaluation design above is a proposed project methodology, not a claim that these sources supplied the new interactive task, its labels, or the proposed statistical analysis.
