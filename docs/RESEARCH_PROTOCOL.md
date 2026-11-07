# QA War Room: prospective research protocol

**Version:** 0.1, prepared 7 November 2026.  
**Domain:** pharmaceutical manufacturing GMP; deviation investigation, CAPA implementation, and CAPA effectiveness review.  
**Status:** proposed research, not a completed study or preregistration. No performance results are claimed.  
**Companion documents:** [Evaluation specification](EVALUATION_SPEC.md) and [Journal strategy](JOURNAL_STRATEGY.md).

## 1. Decision and research question

Build a small, inspectable evidence-reasoning system before building a six-agent world. Its central question is:

> Given a particular manufacturing deviation or CAPA decision, an applicable requirement set, an assessment date, and an incomplete collection of records, can a system request useful additional evidence and make a better supported recommendation within a fixed resource budget?

The study concerns **evidence sufficiency for a specified recommendation**. It does not treat a polished report, an auditor persona, or a completed checklist as proof that an investigation is adequate. It also does not infer that a system that answers regulatory questions can safely close a real CAPA.

The first scientific phase is feasible for a solo researcher: implement reproducible experiments using published public benchmarks and an explicitly derived interactive task. A small synthetic manufacturing casepack can test software behavior and illustrate intended use. Strong claims about pharmaceutical practice require a later, independently reviewed domain evaluation. A human auditor training trial is a different study and is not required to start this computational work.

### 1.1 Intended output

Each episode should produce an assessment containing:

1. The exact decision under review and its scope, such as whether evidence supports CAPA implementation, CAPA effectiveness, or a particular closure recommendation.
2. Atomic findings with document/version/span citations and an assessment date.
3. Relevant contradictions, missing evidence, and scope limitations.
4. A next evidence request when further information could change the decision.
5. A terminal recommendation, or an explicit abstention with a reason.
6. Resource use and a replayable record of evidence access and decisions.

These are research and decision-support outputs. The starter does not issue an authorized quality-unit approval, change an official quality record, release a batch, or establish regulatory compliance.

### 1.2 Why manufacturing GMP is a meaningful motivation

ICH Q10 section 3.2.2 describes structured investigation and CAPA; its commercial-manufacturing table calls for evaluating action effectiveness. This supports studying the distinction between evidence that an action was implemented and evidence that it worked. It does not prescribe one universal observation period or the same closure conditions for every case. [ICH Q10](https://database.ich.org/sites/default/files/Q10_Guideline.pdf)

For the US example, 21 CFR 211.192 addresses investigation of unexplained discrepancies and failures, consideration of potentially associated batches/products, and a written record of conclusions and follow-up. That motivates scope reasoning and evidence traceability. Applicability must be recorded by jurisdiction and version; this paragraph is not a cross-jurisdictional compliance checklist. [eCFR 21 CFR 211.192](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-J/section-211.192)

### 1.3 Separate the decisions that a case can contain

Use separate decision targets rather than a single universal `closed` flag:

| Decision target | Example evidence question | A tempting but invalid shortcut |
|---|---|---|
| Investigation adequacy | Are the proposed cause and relevant scope supported by the available investigation record? | A signed narrative proves the proposed cause |
| Action implementation | Was the specified action actually completed for the affected process, people, equipment, or documents? | A planned action or training assignment proves completion |
| Effectiveness assessment | Does the defined follow-up evidence satisfy the approved effectiveness criterion at the assessment date? | Completion of an action proves effectiveness |
| Closure recommendation | Are the applicable, case-specific closure conditions supported, with open issues represented accurately? | Every deviation and every linked CAPA must always close together |

The benchmark must supply or reference its decision policy. The evaluator must not silently invent a universal GMP rule. Some policies can allow an investigation to close while a linked CAPA or effectiveness check remains open. Such a case must state that policy explicitly.

## 2. Contribution boundary and closest prior work

The proposed contribution is a **testable evaluation and evidence-acquisition method**, not a claim to have invented AI auditing, multiagent systems, CAPA assistance, or digital twins.

| Prior work | Verified relevance | Boundary for this project |
|---|---|---|
| Salami, Smith-Goettler, and Yadav, 2024, *Can Foundational Large Language Models Assist with Conducting Pharmaceuticals Manufacturing Investigations?* | Studies extraction and retrieval using real manufacturing deviations; the verified source is an arXiv preprint | A close manufacturing-investigation predecessor. Do not claim that using LLMs for deviations is new. A peer-reviewed journal version was not verified in this review. [Paper](https://arxiv.org/abs/2404.15578) |
| *Integrating Artificial Intelligence in Quality Audits of Oral Solid Dosage Manufacturing Facilities*, 2026 | Published WinAI audit platform report; describes 254 simulated and 12 limited live audit datasets | Direct GMP-audit predecessor. Its reported pilot is not an independently replicated validation of QA War Room. [Publisher](https://journals.innovareacademics.in/index.php/ijap/article/view/57414) |
| Waikar, Bhat, and Ramanathan, 2026, *Retrieval Augmented Generation (RAG) for Evaluating Regulatory Compliance of Drug Information and Clinical Trial Protocols* | A pharmaceutical regulatory-compliance RAG study in *CPT: Pharmacometrics & Systems Pharmacology* | Supports a computational pharmaceutical publication route; its clinical/regulatory document tasks do not establish manufacturing CAPA performance. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12917324/) |
| ContractNLI and SciFact | Published evidence-based inference and scientific verification benchmarks | Establish reproducible component tasks; neither is a manufacturing closure benchmark. [ContractNLI paper](https://aclanthology.org/2021.findings-emnlp.164/) · [SciFact paper](https://aclanthology.org/2020.emnlp-main.609/) |
| Sino-US-DrugQA, Fu, Chen, and Lu, 2026 | Peer-reviewed pharmaceutical regulatory QA benchmark in *PLOS One*, published 15 September 2026 | Adds a regulatory-domain assessment, not evidence-bundle or CAPA-closure ground truth. [Publisher](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858) |

A potentially useful contribution would be to show, under controlled evidence access, whether explicit evidence sufficiency, sequential requests, and contradiction handling improve decisions at an acceptable cost. That is a hypothesis. Before submission, refresh the literature search and compare task definition, data, access assumptions, evaluation unit, and baselines with the closest work. Avoid “first” claims unless a documented search supports the exact, narrowly defined statement.

## 3. Four evidence tracks, kept separate

### Track N: native published benchmarks

Run the released tasks without changing their questions, labels, or official evaluation semantics. The purpose is to establish competent classification, retrieval, evidence selection, and regulatory QA components.

| Dataset | Native role | Required treatment |
|---|---|---|
| ContractNLI | Document-level entailment, contradiction, and not-mentioned decisions with evidence spans | Preserve the released document splits and hypothesis IDs. Hypotheses within one contract are dependent observations. [Project and terms](https://stanfordnlp.github.io/contract-nli/) |
| SciFact | Claim verification using scientific abstracts and evidence rationales | Distinguish document retrieval from verification. The official repository states that train/dev labels are public but test labels are withheld. Never label locally scored dev results as official test results. [Official repository](https://github.com/allenai/scifact) |
| Sino-US-DrugQA | Regulatory multiple-choice QA | Use the authoritative bilingual release for a native reproduction. Preserve task, language, quality, and domain metadata. The official release has no training split. Do not call a newly constructed split official. [Dataset card](https://github.com/DodgeLU/Sino-US-DrugQA/blob/main/DATASET_CARD.md) |

For Sino-US-DrugQA, the verified release contains 11,444 items, including 10,122 `pass` and 1,322 `borderline` items. The card includes non-drug domains and reports manufacturing/quality subdomain statistics, but the inspected release does not expose a per-item functional-subdomain field or a scoring-script derivation. Consequently, an official `Drugs AND GMP` filter cannot simply be applied. Use the released drug-category items as a regulatory-knowledge auxiliary task, or obtain an author mapping or create separately documented annotations before defining a GMP subset. A keyword filter must not be presented as an official subset. The English companion is separate from the bilingual release used in the paper. [Dataset card](https://github.com/DodgeLU/Sino-US-DrugQA/blob/main/DATASET_CARD.md)

Native benchmark results cannot be merged into a single headline “audit accuracy.” Report each task with its proper denominator and original metric.

### Track I: derived interactive evidence-acquisition benchmark

Create a new, versioned task from eligible source documents. A controller reveals an initial subset and permits additional evidence requests. The policy must decide what to request and when to stop.

Key requirements:

- Preserve source IDs, original labels, original splits, and transformation ancestry.
- Give every evaluated system the same initial packet, available record collection, access permissions, assessment date, and resource cap.
- Keep the environment response deterministic for a requested record. A conversational staff role must not fabricate an observation or reveal a hidden answer.
- Use public document structure or a frozen parser to form evidence units. Never segment or rank documents using test labels in the deployable condition.
- Keep both a source-level target and a visible-evidence state. Concealing a supporting passage does not change the original document's full-context label; it changes what the policy has seen.
- Do not assume that an official list of evidence spans encodes every minimal sufficient evidence set. Such sets need a separate construction rule or annotation.
- Use a separate oracle diagnostic when gold evidence controls retrieval or sufficiency. Do not report it as deployable performance.

The first derived task should use an unmodified source with controlled disclosure. Counterfactual edits, temporal metadata, version conflicts, and manufacturing adaptations should be added as separate tracks because they require new labels and new validity checks.

### Track G: constructed manufacturing GMP transfer cases

Build cases from original synthetic records and public requirements, with a declared as-of date and explicit reference policy. Each case should have an event timeline, record provenance, relevant scope, decision target, alternative plausible explanations, and a reference rationale.

Useful case mechanisms include:

- An action is approved but not implemented.
- Training is documented but the implicated equipment/process change is not completed.
- Effectiveness monitoring has not reached its planned observation horizon.
- A recurrence occurs after implementation and is relevant to the same failure mechanism.
- A favorable summary excludes affected batches, shifts, sites, or products.
- A superseded procedure is mistaken for the applicable version.
- A record is dated after the assessment cutoff and cannot justify the earlier decision.
- A closure narrative conflicts with source records.
- A complete, internally consistent case supports the requested recommendation.
- An unavailable record makes the answer indeterminate rather than false.

Include straightforward supported cases as well as failures. Otherwise a system that refuses every closure can appear excellent. The case generator must vary wording, document order, IDs, irrelevant background details, and the position of decisive evidence without changing the reference semantics.

The runnable eight-case starter shares two template families and is an engineering demonstration. Its 32 scripted episodes are not 32 independent samples. It is not a representative sample, a power calculation, an independent validation set, or a basis for a claim that the system improves pharmaceutical audits.

### Track F: future applicability and human-use studies

Later work can add independently reviewed manufacturing cases, licensed/deidentified real records, retrospective expert review, and prospective shadow use. A separate human training study can ask whether interacting with QA War Room improves auditors' performance on unseen cases and whether learning transfers to practice. Software benchmark success does not answer those questions.

## 4. Model of the research environment

### 4.1 Episode state

Each episode has a hidden source collection and a visible evidence ledger. The controller tracks which units have been shown, the assessment date, access results, budget consumption, and whether the policy has stopped.

Keep the following concepts distinct:

| Concept | Meaning |
|---|---|
| Source target | Label or reference decision based on the complete admissible source collection |
| Visible evidence | The exact material the policy has received so far |
| Corpus insufficiency | Even all admissible records do not resolve the specified decision |
| Retrieval failure | Relevant available evidence exists but the policy did not obtain it |
| Model uncertainty | The model cannot confidently infer a decision from what it has seen |
| Administrative ineligibility | A case-specific rule, such as an incomplete observation window, prevents the requested decision at this date |

These states have different operational implications and should not be collapsed into one “not compliant” category.

### 4.2 Actions

The initial research action set should be small:

1. Search the admissible collection using a query.
2. Open a named record or evidence unit.
3. Request a defined record category or clarification that the environment can answer from existing data.
4. Submit an intermediate finding with citations.
5. Stop with a terminal recommendation and a calibrated confidence output, or abstain.

Every access attempt costs a recorded amount, including empty results. An invalid request returns a defined response rather than an invented record. Automatic retries, context compression, verifier calls, and hidden summarization must be included in the budget.

### 4.3 Roles and multiagent conditions

The named staff and auditor roles can support the interface, but persona names are not evidence of professional competence. In research:

- Staff roles are record interfaces with declared knowledge and access, not free-form generators of facts.
- A “novice” policy can be a deliberately simpler strategy; an “expert” policy can include structured checks. These names describe experimental policies, not validated human expertise.
- Initially compare one investigator against one investigator plus one reviewer. A six-agent configuration is optional after this comparison is useful.
- Keep the base model, information access, total calls/tokens, and stopping budget matched when estimating the benefit of role separation.
- If one role receives extra facts or a better model, describe the whole intervention and do not attribute the result solely to roleplay.
- Score the final evidence-supported decision, not the persuasiveness of a debate or the majority vote among agents.

## 5. Falsifiable hypotheses and estimands

The confirmatory dataset, comparator, budget, margins, and analysis must be frozen before inspecting evaluation predictions. Section 10 gives the locking procedure. Definitions and formulas are in [EVALUATION_SPEC.md](EVALUATION_SPEC.md).

**Two separate study locks:** Stage A develops the method using native public tasks and a derived ContractNLI evaluation. Stage B is the intended pharmaceutical contribution: before viewing its held-out outputs, designate an independently reviewed Track G Manufacturing GMP endpoint as the primary or explicitly multiplicity-controlled key confirmatory endpoint, with native benchmarks auxiliary. Stage B needs its own frozen cohort, reference decisions, comparator, margins, and analysis. If that domain evaluation is unavailable, Stage A can support a technical first paper; it cannot establish pharmaceutical impact. Development order does not determine the pharmaceutical manuscript's endpoint priority.

### H1: evidence acquisition and sufficiency

**Hypothesis:** A sequential evidence-acquisition policy with a structured evidence ledger reduces unsupported acceptance relative to a strong single-agent retrieval baseline at the same deployable access conditions and resource cap, without unacceptable loss of supported-case sensitivity or decision coverage.

**Stage A primary task:** the frozen, derived ContractNLI task on held-out source documents. This provides an independently established source-level target for methods feasibility; it is not direct pharmaceutical validation. **Stage B pharmaceutical primary task:** independently reviewed Track G cases addressing a specified manufacturing deviation/CAPA effectiveness or closure claim, locked before their evaluation is unblinded.

**Primary endpoint:** false-support rate among source targets that are not supported. Define the difference as proposed minus comparator; a negative difference favors the proposal.

**Mandatory guardrails:** sensitivity on supported cases, non-abstained decision coverage, full-label task performance, and resource compliance. Predeclare tolerable margins and minimum coverage from development feasibility and the intended use of the method. A reduced false-support rate accompanied by excessive rejection, abstention, or a large loss of sensitivity does not support H1.

**Falsification:** the superiority interval does not exclude no improvement, a guardrail fails, a deployable benefit appears only with gold-informed retrieval, or the nominal advantage disappears under equal resource accounting.

### H2: role separation beyond extra computation

**Hypothesis:** An investigator/reviewer arrangement improves the H1 tradeoff over a single agent given the same ledger, evidence requests, model family, and aggregate budget.

Test the multiagent method against a single agent allowed equivalent sequential reasoning, review calls, and output tokens. If a single agent achieves comparable performance at lower cost, retain it for the product. Roleplay can still be useful as an interface, but “multiagent reasoning improves safety” would be unsupported.

Treat H2 as secondary unless a separate confirmatory comparison and multiplicity procedure are declared before unblinding.

### H3: scope, time, version, and contradiction reasoning

**Hypothesis:** Explicit structured checks improve performance on controlled changes to scope, dates, versions, or contradictory evidence, while preserving predictions under irrelevant wording/order changes.

This hypothesis belongs to a **new derived or synthetic track**, because the native datasets do not automatically supply valid labels for every transformation. Report each transformation family separately. A system that changes answers for irrelevant formatting or fails to change when the decisive admissibility condition changes fails this test.

### H4: uncertainty and abstention

**Hypothesis:** Calibration fitted only on permitted development data gives useful selective performance: fewer accepted unsupported findings at a predeclared operating point without unacceptable loss of useful decisions.

Report calibration and risk/coverage curves, not only confidence-bin accuracy. A confident incorrect decision, a justified corpus-level insufficient-evidence result, and model abstention are different outcomes. Never treat a `NotMentioned` label as model abstention.

### H5: transfer to pharmaceutical regulation and constructed GMP cases

**Hypothesis:** The method's evidence-handling behavior remains useful on an untouched regulatory QA assessment and on an independently specified constructed manufacturing task.

This is initially an exploratory transfer analysis in Stage A. For the pharmaceutical-target Stage B manuscript, elevate the independently reviewed Track G endpoint to the primary or predeclared key confirmatory role before unblinding, rather than presenting pharma impact as a post hoc transfer claim. Sino-US-DrugQA multiple-choice accuracy cannot by itself establish CAPA-closure validity. Author-created GMP cases establish behavior under the authors' assumptions, not generalization to actual facilities.

## 6. Baselines and comparison design

Use a staged matrix to remain feasible for one researcher:

| ID | System | What it tests |
|---|---|---|
| B0 | Fixed rules/checklist on available structured fields | Whether simple observable conditions solve the task |
| B1 | One-pass single-agent RAG | Basic retrieved-evidence reasoning |
| B2 | Single agent with sequential requests and an explicit ledger | Whether interaction and evidence state help |
| B3 | Single agent with equal-budget self-review | Whether extra review computation explains multiagent gains |
| P1 | Investigator plus reviewer using the same controller and ledger | The incremental value of role separation |
| D1 | Full admissible document/context, where it fits | The effect of the access constraint; a diagnostic unless budget-matched |
| O1 | Gold-evidence retrieval or gold evidence selection | Reasoning upper-bound diagnostic, never a deployable result |

Select the primary comparator from B1–B3 using a development-only rule specified before development comparison. At a minimum, a proposed multiagent system must face B2 or B3; comparing six agents only with one short prompt is inadequate.

Budget matching is necessary but not a claim of perfect equivalence. Report actual calls, input/output tokens, evidence units, retrieval calls, cost at a dated price schedule, and wall-clock time. A call-count cap alone does not control expenditure; a dollar cap alone does not control information access. Use the same budget vector and also plot quality/cost tradeoffs.

Run a small development screen first. Carry a limited, preselected set of methods to the locked evaluation. Record why methods were dropped; do not silently remove unfavorable baselines after seeing evaluation results.

## 7. Data construction, independence, and leakage controls

### 7.1 Source identity and grouping

Retain canonical source IDs and construct a lineage graph before any split. Contracts, abstracts, regulatory provisions, translated questions, paraphrases, and counterfactual siblings can generate many rows while representing few independent sources.

- Native scores retain the official splits for comparability.
- Derived tracks keep all descendants of a source in one partition.
- Near-duplicate templates and known source families should be grouped when feasible; report the grouping rule and residual overlap.
- For SciFact, shared evidence documents and related claims require group-aware uncertainty and an explicit cross-split overlap audit.
- For Sino-US-DrugQA, preserve bilingual/parallel siblings and shared regulatory-source families. If the released metadata cannot identify a clean provision-level grouping, state that limitation and use the strongest available grouping; do not assert source independence.
- Report both the number of rows and the number of independent source groups.

When an official split has source overlap, do not silently rewrite it. Report native results as released and a separately named stricter split if constructed. Changing the split changes the evaluation.

### 7.2 Label independence

For native tasks, use released reference labels. For a derived disclosure task, keep the original source target but separately score whether the submitted rationale is supported by the observed material.

For new counterfactual/GMP labels:

1. Write the decision specification and reference evidence before running compared systems.
2. Store author, creation method, timestamp, source ancestry, and version.
3. Use deterministic construction when a transformation has an unambiguous logical effect; otherwise require adjudication.
4. Keep the evaluator's reference bundle unavailable to agents and retrievers.
5. Do not let the same LLM response create a case, provide its reference answer, and act as the sole judge of a competing model.
6. If one researcher writes all labels, disclose that dependence. Expert background does not create independent validation.
7. A second LLM can assist quality screening but is not an independent pharmaceutical reference standard.

### 7.3 Prevent answer leakage

The model-facing corpus excludes reference labels, author rationales, answer keys, dataset cards that contain example answers to evaluated items, grading scripts with answers, and hidden filenames that encode the target. Labels stay in a separate evaluator namespace.

For Sino-US-DrugQA, retrieve the underlying permitted regulatory material rather than the question/answer JSONL. Never use reference answers as RAG documents. For all tasks, keep research prompts, public explanatory examples, and demonstration cases disjoint from evaluation sources.

Public benchmark memorization by pretrained models cannot usually be excluded completely. Record model/version/date, compare evidence-removed and evidence-altered diagnostic conditions, and describe contamination as a limitation. Such diagnostics do not prove that training contamination is absent.

## 8. Sample size, feasibility, and analysis

### 8.1 No invented power guarantee

The number of available benchmark rows is not an adequate sample-size justification. Power depends on independent source groups, target prevalence, paired outcome discordance, within-source dependence, effect size, and the selected operating point.

Before finalizing an evaluation:

1. Inventory eligible source groups and target classes in each partition.
2. Run a development-only pilot to measure costs, error prevalence, cluster size, paired differences, and failure rates.
3. Define a minimum scientifically meaningful effect and acceptable sensitivity/coverage loss before inspecting held-out outputs.
4. Simulate paired clustered outcomes across a range of plausible effects and dependence levels. Publish the assumptions and code.
5. Compare the required independent groups and API budget with what is available.
6. If the study cannot resolve the desired effect, reduce the claim, report interval estimates, or enlarge the independently sourced evaluation. Do not relabel many paraphrases as independent samples.

A solo researcher can publish a useful, well-delimited benchmark and failure analysis without establishing a tiny performance gain. Feasibility is a reason to narrow the question, not to imply that eight demonstration cases from two templates provide adequate scientific evidence.

### 8.2 Primary analysis

Use paired comparisons because systems see the same episodes. Resample or model at the source-family level, preserving all dependent hypotheses, counterfactuals, language siblings, and repeated stochastic runs. Report point estimates, denominators, paired differences, and 95% confidence intervals.

The default reporting estimand is the item-weighted metric over the specified finite benchmark population, with uncertainty clustered by source family. Report an equal-source-weighted sensitivity analysis if large groups could dominate. Predeclare any different estimand.

The primary H1 claim requires both an improvement on the primary endpoint and all guardrails. Secondary comparisons are descriptive unless their multiplicity treatment is frozen. A non-significant result does not demonstrate equivalence or non-inferiority.

If an error count is zero, report an appropriate upper uncertainty bound and its independence assumptions. An ordinary nonparametric bootstrap of all-zero events can produce an uninformative zero-width interval; that is not evidence of zero risk. Use a suitable rare-event analysis, or a conservative source-level event bound, and identify the changed estimand.

### 8.3 Stochastic and provider variation

Predeclare decoding settings and the number of repetitions permitted by the budget. Treat repeated runs on one source as repeated measurements, not additional independent cases. Report source-averaged estimates and run variability. Keep provider outages, malformed outputs, context-limit failures, and retries in the denominator according to the failure policy.

Pin local model revisions when possible. For hosted models, record exact returned identifiers and run dates; do not promise identical future API behavior. If the model changes materially during an evaluation, stop and decide whether to restart the affected comparison under the same version for all methods.

## 9. Ablation plan

The minimum informative ablations are:

| Ablation | Interpretation |
|---|---|
| Remove sequential requests; retain total access budget | Benefit of selecting the next request after seeing evidence |
| Remove structured ledger; retain prompts and budget | Benefit of explicit evidence state |
| Replace investigator/reviewer with equal-budget single-agent review | Role separation versus additional computation |
| Remove contradiction check | Contribution to unsupported acceptance under conflict |
| Remove scope/time/version checks on the derived track | Contribution to admissibility reasoning |
| Remove abstention/calibration, retain forced labels | Selective reporting versus underlying task accuracy |
| Replace deployable retrieval with oracle evidence | Retrieval bottleneck versus inference bottleneck |
| Random or fixed-order requests within the same cap | Whether learned/planned acquisition is better than simply revealing more |

Ablations can be staged on development data and a preselected subset carried forward. A full factorial design is not required at the start. Do not interpret an ablation outside a task where the removed component is relevant; for example, time reasoning cannot be evaluated without valid temporal labels.

## 10. Decisions to freeze before unblinding

Commit a run manifest and the following decisions before generating or viewing held-out predictions:

- Research question, primary hypothesis, primary task, comparator-selection rule, and final comparator.
- Dataset versions, hashes, licences, source grouping, inclusion/exclusion rules, transformations, and split IDs.
- Definition of all labels, decision targets, abstention, support errors, evidence validity, and unavailable-evidence states.
- Primary endpoint, guardrail margins, operating point, statistical analysis, uncertainty method, and multiplicity treatment.
- Model versions, prompts, role permissions, retriever, index, context allocation, calibration procedure, and selection thresholds.
- Resource caps, repeat count, retry policy, invalid-output policy, timeout handling, and run-order randomization.
- Planned sensitivity analyses, ablations, and subgroup analyses.
- Minimum relevant effect, feasibility/power assumptions, and rules for stopping because the study is under-resourced.
- Case-generation rules, reference-label provenance, and adjudication process for any new labels.
- Planned interpretation of positive, null, mixed, and negative outcomes.

Unknown values remain explicit `TO_BE_FROZEN` fields during development. A run with unresolved confirmatory settings is a pilot, not a confirmatory evaluation. A signed/dated local manifest is useful; a timestamped public preregistration can improve transparency when the protocol is ready. Do not claim a preregistration has occurred until it actually has.

After unblinding, log every correction or deviation. Correcting a clear implementation defect can be necessary, but rerun all affected methods, retain the original artifacts, and distinguish the corrected exploratory result from the original locked analysis.

## 11. RL and digital twin: conditional later work

### 11.1 Reinforcement learning gate

Start with deterministic request policies and prompted policies. Consider RL only if interaction is a real bottleneck and sequential acquisition provides value over fixed retrieval under a credible benchmark.

A possible later formulation has a partially observed state, permitted evidence requests, a stopping action, and a cost-sensitive terminal reward. The reward must distinguish unsupported acceptance, correct supported decisions, justified insufficiency, and unnecessary requests. Reward coefficients are research choices and must be justified and sensitivity-tested; they are not a regulatory risk scale.

Do not train on native benchmark evaluation labels or held-out source descendants. Compare RL with supervised/imitation policies, simple heuristics, and an equally budgeted prompted policy. Keep evaluator rules and test case families separate from the training simulator. Report reward gaming, early-stop exploits, and distribution shift. If interaction is not beneficial or the available training environment is too narrow, omit RL from the first paper.

### 11.2 Digital twin gate

The starter is a document-grounded simulation. A later **process or quality-system digital twin** could model the state and transitions of a specified real manufacturing quality workflow, with traceable updates from operational records and validated behavior for a stated purpose. A twin need not depend on physical sensors; a process can be connected through events, approved records, and system interfaces.

Before using that label, specify the real referent, represented state, synchronization/update mechanism, intended predictions, validation evidence, and limits. A graph of uploaded documents or a roleplay transcript alone does not establish a validated twin. Do not make the first paper depend on that claim.

## 12. Publication and product can proceed in parallel

| Phase | Research deliverable | Product deliverable | Exit decision |
|---|---|---|---|
| 0: software foundation | Six-case smoke checks; no scientific claims | Local replay, document requests, findings, export | Evidence access and evaluator separation work |
| 1: native components | Reproducible native benchmark runs | Reliable citations and structured outputs | Components are adequate to test interaction |
| 2: derived sequential task | Locked H1 comparison and ablations | Useful next-evidence requests | Continue only if benefit/tradeoff is demonstrated |
| 3: manufacturing transfer | Constructed case protocol plus independent domain review when feasible | GMP-specific report and review workflow | Domain assumptions withstand scrutiny |
| 4: applicability | Independently reviewed retrospective/shadow evaluation | Controlled pilot with traceability and version management | Claims match actual observed use |
| 5: optional extensions | RL, learning-transfer, or validated twin studies | Training or workflow integrations | Each extension has its own evidence |

This sequence does not promise a particular duration, cost, acceptance probability, or commercial return. The research artifacts can advance while the interface is improved, but the product demo must never be counted as an independent experiment on the same cases used to design it.

## 13. Negative and mixed results are useful outcomes

- **No multiagent advantage:** publish the controlled comparison and prefer the simpler agent for deployment.
- **Oracle benefit only:** identify retrieval/access as the bottleneck; do not sell the result as reasoning improvement.
- **False-support reduction with too many abstentions:** report the tradeoff and restrict the intended use to triage or evidence organization.
- **Good native results, weak GMP transfer:** publish a transfer failure analysis and revise the domain task; do not hide it behind an average score.
- **Synthetic-only success:** release the case construction and evaluation limits as a benchmark/method demonstration; defer practice claims.
- **Insufficient precision:** report confidence intervals and feasibility, not “no difference.”
- **Evidence-gate weakness:** distinguish deterministic schema checks from semantic evidence validation and improve the latter before making a safety claim.

## 14. Minimum reproducibility package

The eventual experiment release should include source and licence manifests; data download instructions; original split IDs; lineage/group files; generation code for permitted derivatives; frozen configurations; prompts; model identifiers; evaluation code; schema validators; raw normalized predictions; observable action traces; aggregate cost logs; analysis scripts; a list of failed/aborted runs; and a protocol deviation log.

Do not publish API keys, confidential records, personal information, or licensed source material that cannot be redistributed. Publicly readable content and permission to redistribute or commercialize it are different questions. Dataset licences, code licences, source-document rights, and article licences must be recorded separately.

## 15. References and verification notes

Primary sources checked for this protocol on 7 November 2026:

1. ICH. *Q10 Pharmaceutical Quality System*, 2008. https://database.ich.org/sites/default/files/Q10_Guideline.pdf
2. eCFR. *21 CFR 211.192, Production record review*. https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-J/section-211.192
3. Salami H, Smith-Goettler B, Yadav V. *Can Foundational Large Language Models Assist with Conducting Pharmaceuticals Manufacturing Investigations?* arXiv:2404.15578, 2024. https://arxiv.org/abs/2404.15578
4. Jayaprakash Narayanan J. and colleagues. *Integrating Artificial Intelligence in Quality Audits of Oral Solid Dosage Manufacturing Facilities*. *International Journal of Applied Pharmaceutics* 18(2):245–252, 2026. https://journals.innovareacademics.in/index.php/ijap/article/view/57414
5. Waikar S, Bhat AG, Ramanathan M. *Retrieval Augmented Generation (RAG) for Evaluating Regulatory Compliance of Drug Information and Clinical Trial Protocols*. *CPT: Pharmacometrics & Systems Pharmacology* 15(3):e70201, 2026. https://pmc.ncbi.nlm.nih.gov/articles/PMC12917324/
6. Koreeda Y, Manning CD. *ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts*. Findings of EMNLP, 2021. https://aclanthology.org/2021.findings-emnlp.164/
7. ContractNLI official project and terms. https://stanfordnlp.github.io/contract-nli/
8. Wadden D and colleagues. *Fact or Fiction: Verifying Scientific Claims*. EMNLP, 2020. https://aclanthology.org/2020.emnlp-main.609/
9. SciFact official repository. https://github.com/allenai/scifact
10. Fu X, Chen Z, Lu W. *Sino-US-DrugQA: A benchmark for evaluating large language models in cross-jurisdictional pharmaceutical regulation*. *PLOS One* 21(9):e0343858, 2026. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858
11. Sino-US-DrugQA official repository and dataset card. https://github.com/DodgeLU/Sino-US-DrugQA · https://github.com/DodgeLU/Sino-US-DrugQA/blob/main/DATASET_CARD.md

These references establish motivation and prior work. All proposed hypotheses, implementation choices, margins, and future experiments above are project design decisions unless explicitly attributed to a source.
