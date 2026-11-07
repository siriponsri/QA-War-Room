# Budgeted evidence acquisition for CAPA claim review: an offline evaluation framework and prospective manufacturing study

**Working manuscript, version 1. LOCAL DRAFT — NOT FOR SUBMISSION.**

Author names, affiliations and corresponding-author details: **[OWNER TO COMPLETE]**.
Target journal/article type: **[NOT SELECTED]**. No editor contact or submission has occurred.
Independent review: **{{independent_review}}**. Adjudication: **{{adjudication}}**.
Reviewed reference lock: **{{reference_lock}}**. Confirmatory results: **{{scientific_results}}**.

## Abstract

**Background.** A record that a corrective action was completed is a different evidentiary object from records that justify a specified effectiveness or closure claim. This project operationalizes that distinction as a bounded document-acquisition task for original synthetic pharmaceutical manufacturing scenarios. It does not assess the compliance of an actual facility.

**Objective.** To prepare a reproducible evaluation of whether sequential acquisition with explicit evidence-applicability and sufficiency checks can reduce false supported claims without unacceptable loss of legitimate support, decision coverage or overall accuracy.

**Methods.** The software separates environment inputs from evaluator references, permits only requested records in actor observations, records resource-bounded actions, and replays source responses before evaluation. A constructed Manufacturing GMP pack contains {{pack_cases}} cases in {{pack_families}} construction families with fictional site-specific SOPs. The proposed analysis pairs methods on case, budget and repetition, preserves failures in fixed denominators, and clusters uncertainty by source family. Current policies and candidate labels are coauthored engineering fixtures. Independent review, adjudication, sample-size justification and scientific model/comparator selection remain incomplete.

**Results.** Confirmatory outcomes are **{{scientific_results}}**. A separately labeled engineering rehearsal processed {{dev_jobs}} frozen jobs over {{dev_cases}} development cases in {{dev_families}} construction families, with {{dev_transitions}} source transitions. These counts establish exercised software paths and do not estimate pharmaceutical effectiveness or LLM performance. No paid model inference was used.

**Conclusion.** The offline framework supports traceable evaluation preparation. Whether it improves evidence review requires independently reviewed references and a prospectively locked comparison; the current package does not establish that improvement.

Keywords: CAPA; evidence acquisition; claim support; reproducibility; synthetic manufacturing cases; prospective evaluation.

## 1. Introduction

The decision studied here is narrow: given a specific deviation/CAPA closure or effectiveness claim, which records should a reviewer request next, and what conclusion is justified by the acquired applicable evidence? The project distinguishes action implementation, an observed follow-up result, and a conclusion supported for the declared product, line, cohort and cutoff. These distinctions define a research task; they are not a replacement for an organization's approved quality system or a batch-release decision.

ICH Q10 and EU GMP Chapter 1 provide pharmaceutical-quality-system context in the project's existing source register [R01, R04]. This draft adds no new legal interpretation, cross-jurisdiction equivalence claim or assessment against those sources. The acceptance rules used in the constructed cases are explicitly fictional site SOPs. Current jurisdiction and intended operational use remain owner decisions.

The local targeted reading register includes manufacturing-investigation assistance [P01], regulatory-compliance retrieval-augmented generation [P02], oral-solid quality audits [P03] and audit-control evaluation [P08]. Public tasks include ContractNLI [P05], SciFact [P06] and Sino-US-DrugQA [P04]. These are distinct literatures and tasks. An ability to answer a regulatory knowledge question or classify a contract hypothesis would not by itself validate a pharmaceutical CAPA decision. The source table in `manuscript/SOURCE_STATUS.md` records the local snapshot and what must be rechecked; this session performed no new literature search or full-text verification. No priority or novelty claim is made.

The proposed contribution is an inspectable information boundary, a claim-specific acquisition task, and an analysis that makes selective refusal and failures visible alongside false support. The scientific hypothesis remains prospective: an applicability-aware sequential method may reduce false supported claims under matched acquisition limits while meeting predeclared sensitivity, coverage and accuracy guardrails. A fair simpler baseline or a negative comparison is an acceptable outcome.

## 2. Methods

### 2.1 Intended use and evaluation layers

QA War Room is an offline research/product prototype for evidence-review rehearsal. The current browser demo and the separate native, sequential and Manufacturing GMP command-line tasks are different artifacts. Native benchmark conventions are preserved in their own adapters. The G3 controlled-disclosure task is an explicitly derived adaptation. The G4 resource is original synthetic manufacturing material. Results from these layers must retain separate populations, labels and denominators; no combined audit-accuracy score is defined.

The primary pharmaceutical claim is not established by completing a software milestone. A future Stage B pharmaceutical comparison needs a separate reviewed reference release and prospective lock. Native methods work remains auxiliary for that pharmaceutical route. Without the domain evidence, a subsequent paper would need a narrower engineering/methods scope.

### 2.2 Constructed resource and reference status

The current pack contains {{pack_cases}} original synthetic nonsterile oral-solid cases across {{pack_families}} construction families. Mechanisms cover packaging reconciliation, blending parameters, equipment setup/change control, recurrence after training, investigation cohort and effectiveness window. Each family includes a claim, governing fictional SOP, investigation, action implementation, training, effectiveness and status records. Variants change a material observation, availability, scope, time or trained revision; a context variant preserves the authored outcome. Unresolved acceptance criteria are preflagged separately.

Inputs and record availability are authored before the evaluator compiles candidate labels from structured SOP criteria. Candidate labels are therefore authored rule outputs, not independent human ground truth. Whole template/counterfactual families remain in one provisional partition. Common scaffolding and solo construction limit independence. The {{dev_families}} development families used in the engineering rehearsal cannot be treated as independent manufacturing sites or retrospectively promoted to an untouched confirmatory population.

The blinded review packets, rubric, intake checks and adjudication plan exist, but actual independent review is **{{independent_review}}** and adjudication is **{{adjudication}}**. Review software tests use temporary synthetic ratings only. They do not supply expert assessments. A reviewed release must preserve original ratings, reviewer provenance, disagreements and adjudication under a new version. The current reader refuses a confirmatory lock on author-draft data, even if draft review fields are populated with arbitrary strings.

### 2.3 Observation, actions and information budget

An active policy receives a detached observation containing the claim/cutoff, public record catalog and costs, remaining budget, requested-record responses and delivered evidence. It receives no evaluator label, witness set, reference rationale, pair orientation, construction lineage or unrequested record content. Source code and complete backend records remain readable to the developer; the implemented boundary is architectural rather than an operating-system sandbox.

Actions are request, submit a labeled decision with visible record pointers, or abstain. Duplicate requests are idempotent for acquisition credits and still count as policy calls. Unavailable records and exposure-cap responses are explicit. Submission and abstention are terminal; invalid actions, runtime errors, per-job caps and global interruption remain auditable. A missing or inapplicable record is unresolved information, not automatically evidence of a regulatory violation. A submitted `insufficient` label is distinct from an abstention.

The default engineering matrix fixes acquisition budgets 0, 3 and 7 credits, one deterministic repetition, at most 16 policy actions and 200,000 exposed source bytes per job, 10,000 policy actions per run and zero retries. D5 costs two credits; each other material record costs one. Provider mode is offline only with a USD {{cost_usd}} API cap. These are engineering settings rather than a measured cost-efficient operating point for a language model.

### 2.4 Baselines and ablations

The status shortcut requests only the closure-status record. The SOP catalog policy obtains the SOP and required material records in fixed order. The adaptive policy changes acquisition order and may stop on an observed decisive failure or unresolved criterion. The applicability ablation uses the same fixed acquisition order but ignores scope/date applicability in a detached interpretation copy; original source evidence and evaluator checks remain intact. All use the same access interface and hard caps. Fewer requests can be a policy outcome and do not authorize extra hidden information.

These policies are coauthored deterministic scripts over structured SOP fields. They are not human reviewers, trained agents or a language-model experiment. Model revisions, prompts, decoding, calibration, stochastic repetitions and the scientific primary comparison are **[NOT SELECTED / NOT RUN]**. Broader role-separation, ledger and calibrated-abstention ablations remain prospective.

### 2.5 Endpoints, failure handling and analysis

The proposed primary endpoint is false support rate: submitted supported decisions on primary-eligible reference-negative cases divided by all frozen reference-negative cases. Supported sensitivity uses all primary reference-supported cases. Decision coverage counts any valid submitted label, including insufficient, divided by all frozen primary cases. Overall accuracy uses correctly submitted labels divided by that same complete primary denominator. Each rate retains its numerator and denominator; empty denominators are null. Abstentions, invalid actions, policy failures and unstarted jobs are not discarded.

Preflagged ambiguous references are a separate stratum rather than forced primary labels. Their eligibility still requires independent review before a scientific lock. Structured location/rule checks are reported only as evidence proxies; semantic rationale validity is unmeasured. Pointer existence is not semantic support, and rule consistency is not proof of minimal sufficient evidence.

Paired comparisons require identical case, budget and repetition units. The planned finite-population estimand is item weighted, with descriptive equal-family sensitivity and per-family denominators. The implemented bootstrap arithmetic samples source families, carrying both arms, all dependent siblings and repeated runs together. Repetitions do not create new independent cases. Undefined draws, fewer than two groups, zero-event FSR or degenerate distributions withhold intervals. A justified rare-event analysis and independent-unit audit remain necessary; an all-zero bootstrap cannot establish safety.

The effect threshold, supported-sensitivity loss margin, coverage floor and accuracy-loss margin are unset. A future primary claim must jointly satisfy all four prospectively locked conditions. Sample size must follow reviewed pilot prevalence, paired discordance and family dependence, with explicitly declared simulation assumptions. No power result, calibration result, confirmatory interval or multiplicity-adjusted comparison is available here. Previously viewed development outcomes cannot be relabeled confirmatory.

### 2.6 Reproducibility and artifact boundaries

G5 locks the complete matrix and input/implementation hashes, journals normalized actions, resumes from source replay, and generates evaluator-only analyses. G6 regenerates saved descriptive tables from raw runs before rendering manuscript counts. A claim ledger maps permitted engineering/gate values to hashed evidence. Checksums detect changes but cannot authenticate expert independence or human approval.

The local archive separates developer source/tests, backend environment inputs, raw engineering runs, and evaluator references/analyses. Neither source/tests nor complete backend records are actor retrieval corpora. A fresh-directory rehearsal first replays without gold, then installs evaluator files to run tests and reproduce analysis. No third-party papers, raw external benchmarks, credentials, company records or actual reviewer identities are redistributed in this local bundle. Publication and original-code/data licensing remain undecided.

## 3. Results status

### 3.1 Confirmatory findings: NOT_RUN

The primary method/comparator, reviewed references, effect margins and final inference procedure are not locked. Consequently, no primary estimate, confidence interval, p-value, non-inferiority result or pharmaceutical effectiveness claim is reported. The blank scientific table is retained as `SCIENTIFIC_TABLE_TEMPLATE.csv` with status **NOT_RUN**. There is no human-learning, review-time, real-site, batch-release or operational-safety result.

### 3.2 Engineering verification only

The source-verified development rehearsal contains {{dev_jobs}} planned jobs over {{dev_cases}} cases and {{dev_families}} construction families, with {{dev_transitions}} raw transitions. It reaches {{dev_terminal}} terminal jobs, comprising {{dev_submissions}} valid submissions and {{dev_abstentions}} abstentions, with {{dev_pending}} pending jobs. Analysis produces {{dev_tables}} method/budget descriptive tables. A separate resource-stop check permits {{cap_actions}} policy action and retains {{cap_pending}} pending jobs in the complete denominator. API expenditure is USD {{cost_usd}}. These counts are software exercise evidence, not independent model observations, a sampled human cohort or efficacy estimates.

Generated engineering tables and provenance are supplied separately from the blank scientific results. Test outcomes and the fresh-directory rehearsal have their own dated logs; this draft does not infer their success from the existence of a test script. Every generated count here is resolved from checked raw-run evidence at build time.

## 4. Discussion

The implemented paths make evidence access, failure handling and source replay inspectable. Their scientific usefulness depends on an adequate reference standard and a fair comparison. Hand-coded policies may agree with coauthored structured criteria because both share the same representation; that agreement is not evidence of robust natural-language or pharmaceutical judgment. The status shortcut and applicability ablation are diagnostic controls, not estimates of how practitioners behave.

The current resource has limited construction diversity and no established independent site sampling. Family clustering cannot repair missing external validity. The finite development rehearsal also cannot justify a final sample size or replace a reviewed pilot. Budget caps constrain record acquisition; they do not establish equal reasoning compute, API latency or clinical/operational cost across future models. Public benchmark contamination and cross-source dependence need separate consideration in any future benchmark report.

The product implication is a testable workflow: expose evidence provenance, request missing records, display unresolved scope/time conflicts and export an editable review draft. No reduction in staff effort, improved learning, customer value or regulatory acceptability has been measured. The accompanying pilot brief specifies a possible future observation study; it recruits no participants and declares no institutional approval or exemption.

The next scientific step is genuine independent review and adjudication, followed by a new reviewed reference release, justified margins/sample size and a prospective Stage B lock. A negative result should be reported under that original question. Interface polish or an expanded agent cast would not resolve the missing evidence.

## 5. Conclusion

QA War Room currently provides an offline framework and original constructed materials for preparing an evidence-acquisition evaluation. Independent pharmaceutical reference review and confirmatory results are incomplete. The manuscript remains a methods draft with bounded engineering evidence and explicit unresolved scientific gates.

## Data, code and declarations

**Availability.** A local, checksummed reproducibility bundle can be generated with the G6 CLI. It has no public URL, persistent identifier, deposited release or assigned redistribution license. External benchmark bytes and third-party PDFs are excluded; existing source URLs and version manifests are retained for attribution. The actor/evaluator split must remain intact in later sharing.

**Funding, competing interests and contributions.** **[OWNER TO COMPLETE FROM ACTUAL CIRCUMSTANCES]**. No absence of funding/conflicts or reviewer contribution is assumed. Reviewer acknowledgments must describe work actually performed.

**Ethics and permissions.** No participant study, independent expert review or company-data processing was performed by this offline increment. Any future human/workflow pilot requires an institutional/organizational determination appropriate to its actual setting; no exemption or approval is claimed here.

**AI assistance.** Codex assisted with software, tests and manuscript drafting. Accountable human authors must verify sources, methods, numbers and declarations. The disclosure wording and current venue policy require review before submission. No AI persona is an independent expert or accountable author.

**References.** Primary links and local register provenance are in `manuscript/SOURCE_STATUS.md` and `literature/references.bib`. This draft is based on the existing snapshot only. Citation metadata, full texts, subsequent versions and regulatory status require rechecking before submission or operational use.
