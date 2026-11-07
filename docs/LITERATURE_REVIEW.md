# Targeted literature review and research positioning

**Search/update date:** 7 November 2026.  
**Review type:** targeted narrative/scoping review for project design. This is not a completed systematic review, PRISMA review, meta-analysis or exhaustive novelty search.  
**Scope:** pharmaceutical manufacturing investigations and audits; evidence-grounded compliance; sequential evidence acquisition; citation/abstention evaluation; role simulation and optional RL.

The reading pack contains the papers available through lawful public endpoints, with a separate download manifest. Downloaded PDF availability does not establish availability of training data, gold labels or a commercial reuse grant. Bibliographic metadata and paper versions are in [catalog.json](../literature/catalog.json) and [references.bib](../literature/references.bib).

## 1. Executive assessment

The area is already active. A generic claim that "LLMs can assist pharmaceutical investigations", "RAG helps compliance", or "multiple agents can simulate an audit" would be weak positioning. The proposed project should investigate a narrower unresolved behavior: **how reliably a system acquires enough applicable evidence to support or reject a CAPA effectiveness claim, and how it behaves when that evidence is missing, contradictory, outside the stated scope or too late**.

The candidate novelty is a combination of task/resource design and controlled evaluation. It must be demonstrated, not declared: a pharmaceutical case resource with traceable reference decisions; budgeted sequential acquisition; paired material/nonmaterial evidence changes; and a false-support reduction tested alongside coverage and sensitivity. A useful negative result could establish that transparent rules plus a single grounded model perform as well as elaborate roleplay.

## 2. Search approach and limits

Primary materials inspected included publisher pages/PDFs, ACL Anthology records, arXiv author manuscripts, official project repositories, public dataset cards and regulator/ICH documents. Search phrases included:

- "deviation CAPA large language models pharmaceutical audit evidence";
- "Can Foundational Large Language Models Assist manufacturing investigations";
- "Integrating Artificial Intelligence Quality Audits oral solid";
- "IntelliAudit evidence sufficiency";
- "Smart Audit System Empowered by LLM";
- "ContractNLI", "COMPACT compliance", "Sino-US-DrugQA";
- citation evaluation, selective prediction and sequential tool-agent evaluation;
- official EU GMP Annex 22 and ICH Q10 CAPA effectiveness.

Prioritized sources: directly relevant pharmaceutical studies; accessible benchmark papers with traceable data; foundational methods that justify a particular design decision. Excluded from the core evidence claim: vendor performance claims without independent evaluation, generic medical QA presented as GMP validation, and molecular/ADMET benchmarks unrelated to audit evidence.

Review depth varies. Directly relevant pharmaceutical/audit papers and dataset cards received closer inspection, including relevant methods/limitations where available. Broader methods papers were reviewed for their stated task and design relevance. The paper-by-paper matrix is a project design assessment, not a formal risk-of-bias instrument. Before manuscript submission, repeat the search in a documented bibliographic database workflow, record exclusions and confirm publisher metadata/version for every cited entry.

## 3. Closest pharmaceutical and audit work

### P01 — Salami, Smith-Goettler and Yadav (2024)

*Can Foundational Large Language Models Assist with Conducting Pharmaceuticals Manufacturing Investigations?* [Author manuscript](https://arxiv.org/abs/2404.15578).

The study uses real manufacturing deviation reports to examine information extraction and retrieval of related historical incidents. It explicitly discusses hallucination risks and the need to define individual tasks. It is a close pharmaceutical predecessor; a journal version was not verified in this search. The public manuscript does not establish that its underlying company records are an open reusable benchmark.

**Implication for this project:** do not claim novelty for extracting CAPA/root-cause information or searching earlier deviations. The proposed difference is prospective evidence selection and applicability-aware assessment of a precisely defined claim, evaluated under controlled missingness and resource budgets.

### P02 — Waikar, Bhat and Ramanathan (2026)

*Retrieval Augmented Generation (RAG) for Evaluating Regulatory Compliance of Drug Information and Clinical Trial Protocols.* [DOI](https://doi.org/10.1002/psp4.70201).

This pharmaceutical journal paper evaluates RAG against drug information and clinical-trial protocol requirements. Its subject supports the feasibility of a pharmaceutical publication route for evaluated regulatory AI. It does not validate manufacturing CAPA closure or establish an open CAPA audit benchmark. Public full-text XML was retrieved; publisher PDF access failed in this environment and is listed for owner assistance.

**Implication:** a grounded pharmaceutical task can be publishable, but changing the domain label on a generic RAG app is insufficient. The question, reference outcomes and evaluation must be pharmaceutical.

### P03 — Narayanan and colleagues (2026), WinAI

*Integrating Artificial Intelligence in Quality Audits of Oral Solid Dosage Manufacturing Facilities.* [Publisher](https://journals.innovareacademics.in/index.php/ijap/article/view/57414).

WinAI combines a web audit workflow, NLP, rule-based severity scoring and recurrence tracking. Its pilot includes simulated and limited live audit data. The authors report favorable performance, but these results are not independently reproduced here; public reusable data/code were not established. The article acknowledges generalization and language-interpretation limitations.

**Implication:** dashboards, standardized checklists, severity rules and recurrence alerts already have direct GMP audit prior art. A stronger contribution is transparent evidence-sufficiency evaluation with held-out families and meaningful counterfactual controls.

### P08 — Wilson and colleagues (2026), IntelliAudit

*IntelliAudit: Using Large Language Models to Evaluate Audit Controls.* [Preprint](https://arxiv.org/abs/2608.07688).

The system retrieves evidence, produces an audit assessment, challenges adverse findings and adjudicates disagreements. It studies IT audit controls and includes human assessments of reasoning/evidence sufficiency. This is especially close to the proposed multi-role architecture; prompts named Auditor/Defender/Judge are not new.

**Implication:** compare against a similar review architecture under equal budgets. Test both unsupported positive claims and missed legitimate support. Do not assume a released evidence collection is an independently labeled gold dataset suitable for RL rewards.

### P09 — Yao and colleagues (2024), Smart Audit

*Smart Audit System Empowered by LLM.* [Apple research page](https://machinelearning.apple.com/research/smart-audit).

The work proposes manufacturing audit support involving risk assessment, a compliance copilot and commonality analysis. It is a manufacturing workflow predecessor, although not specifically the CAPA evidence task proposed here. A reusable public dataset was not established during this review.

**Implication:** a manufacturing audit assistant alone is not the research gap. The contribution must survive comparison with simpler retrieval and workflow automation.

### P21 — Knott, Krebs and Kerscher (2026)

*Large language models in healthcare quality management: a European perspective on process automation and compliance.* [DOI](https://doi.org/10.3389/fdgth.2026.1761641).

This narrative review discusses quality-management applications and governance in European healthcare. It is context and secondary synthesis, not direct experimental validation of this product. Its discussion of evolving requirements should be checked against current primary official sources.

**Implication:** use it to frame the adoption problem and locate further references, while deriving benchmark rules and regulatory status from original sources.

## 4. Published open benchmark evidence

| ID | Paper / native task | Role in this project | What it cannot establish |
|---|---|---|---|
| P04 | [Sino-US-DrugQA](https://doi.org/10.1371/journal.pone.0343858): regulatory MCQs | Pharmaceutical regulatory knowledge anchor | Complete CAPA evidence reasoning, real audit readiness or Thai GMP applicability |
| P05 | [ContractNLI](https://aclanthology.org/2021.findings-emnlp.164/): document NLI plus evidence spans | Contradiction, absence and evidence-localization foundation | Pharmaceutical validity; sequential performance without a separate adaptation |
| P06 | [SciFact](https://aclanthology.org/2020.emnlp-main.609/): scientific claim verification | Evidence-set reasoning and stance | GMP compliance or a locally reproducible official hidden-test score |
| P07 | [COMPACT/ACE](https://aclanthology.org/2026.eacl-long.377/): cross-clause compliance | Optional clause-graph/multi-clause comparator | Independence from ContractNLI source documents or pharma applicability |
| P20 | [LabSafety Bench](https://doi.org/10.1038/s42256-025-01152-1): laboratory safety knowledge/risk | Optional later adjacent-domain evaluation | Manufacturing CAPA or laboratory quality-system audit competence |

Detailed counts, splits, licenses and schema limitations are centralized in [DATASET_PLAN.md](DATASET_PLAN.md), avoiding accidental substitution of adjacent benchmarks for pharmaceutical audit evidence.

The key design lesson is to retain two separate evidence streams: competence on established native tasks and validity on the constructed pharmaceutical task. A combined average score would hide domain and task differences.

## 5. Methods worth reusing, with boundaries

| ID | Method source | Concrete design use | Main boundary |
|---|---|---|---|
| P10 | [Lewis et al., RAG](https://arxiv.org/abs/2005.11401) | Strong retrieval-grounded baseline | Retrieval does not establish sufficient, applicable evidence |
| P11 | [Yao et al., ReAct](https://arxiv.org/abs/2210.03629) | Action/observation loop for document requests | Tool use can still stop early or act on unsupported conclusions |
| P12 | [Gao et al., ALCE](https://aclanthology.org/2023.emnlp-main.398/) | Evaluate citation correctness and completeness | A present citation ID is not semantic entailment |
| P13 | [Asai et al., Self-RAG](https://arxiv.org/abs/2310.11511) | Adaptive retrieval/critique comparator | Self-critique is not independent reference truth |
| P14 | [Niu et al., RAGTruth](https://arxiv.org/abs/2401.00396) | Track unsupported/contradictory generated claims | Grounded input alone does not eliminate hallucination |
| P15 | [Liu et al., Lost in the Middle](https://arxiv.org/abs/2307.03172) | Record-order and context-position robustness controls | Long context cannot be assumed equivalent to reliable evidence use |
| P16 | [Yao et al., tau-bench](https://arxiv.org/abs/2406.12045) | Objective terminal-state checks and repeated-run reliability | User simulation and policy execution differ from pharmaceutical sufficiency |
| P17 | [Park et al., Generative Agents](https://arxiv.org/abs/2304.03442) | Role/memory/replay design for the interaction | Believable behavior does not establish expert performance |
| P18 | [Andriotis & Papakonstantinou](https://doi.org/10.1016/j.ress.2021.107551) | Later constrained sequential inspection-policy formulation | Engineering maintenance worlds are not GMP evidence worlds |
| P19 | [Geifman & El-Yaniv, SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html) | Risk/coverage analysis and an explicit reject option | A threshold or abstention policy requires calibration on the actual task |
| P22 | [Es et al., RAGAs](https://aclanthology.org/2024.eacl-demo.16/) | Diagnostic evaluation of retrieval/generation components | An automated judge cannot supply the sole ground truth |

Method selection should follow the task. A structured checklist, ranker or single model may outperform an expensive multi-agent arrangement. Compare the simplest method capable of expressing the relevant evidence dependency.

## 6. Regulatory context that shapes the research

The primary pharmaceutical motivation is effectiveness evidence, grounded in ICH Q10 and EU GMP Chapter 1. Case-specific numerical thresholds must come from a declared site protocol, not be invented as universal regulations.

The EU Annex 22 material in this pack is explicitly a **2025 consultation draft** plus a **2026 EMA workshop report**. The official EudraLex index and consultation pages were checked on the search date. The workshop discusses possible changes to the scope for AI models; it is not an enacted permission or prohibition. Review the current final sources before any operational deployment. [Official consultation](https://health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en); [EMA workshop report](https://www.ema.europa.eu/en/documents/report/report-multistakeholder-workshop-expert-contributions-artificial-intelligence-guidance-development-annex-22_en.pdf).

These references define research context and deployment questions. The starter is not a validated GMP computerized system, and its software tests do not establish that status.

## 7. Candidate gap and falsifiable tests

| Candidate contribution | Closest prior art | Distinguishing test | Failure condition |
|---|---|---|---|
| Pharma evidence resource with explicit criteria | Manufacturing investigations, WinAI, regulatory QA | Independent reference review; held-out source/template families | Ambiguous rules, label leakage or unrealistic cases |
| Sequential evidence acquisition | ReAct, smart audit, tool-agent benchmarks | Same information/action budget and comparable model resources | Gain disappears versus heuristic/ranker or equal-budget single model |
| Reduced unsupported closure claims | IntelliAudit, citation/grounding work | False-support endpoint with sensitivity and coverage guardrails | Reject-all behavior or unsupported severity escalation |
| Material counterfactual sensitivity | General robustness/evidence evaluation | Paired decisive changes plus irrelevant-change controls | Model follows filenames/style rather than the changed fact |
| Transparent product report | Existing compliance/audit applications | Verifiable source locations and actionable missing-evidence request | Attractive report with untraceable claims |

The "gap" here is a reason to run a study. This review does not prove that no other group has tested the same combination. Update closest-work comparisons before freezing the manuscript contribution statement.

## 8. What to read first

**Day 1:** P01, P03, P08 and ICH Q10. Write down precisely what already exists and what a closure/effectiveness claim means.

**Day 2:** P05, P04 and their dataset cards/licenses. Inspect actual fields before designing an adapter. Review P06 if evidence sets are part of the primary task.

**Day 3:** P12, P16 and P19. Finalize grounding, repeated-run and selective-decision metrics. Read P22 as tooling context rather than a substitute for reference labels.

**Then:** P09/P02 for deployment/publication precedents; P07/P13/P15 for method and robustness choices. P17/P18 are later design references, and P20 is optional for a future laboratory extension.

## 9. Manuscript literature-update checklist

Before submission, recheck publication status of preprints, corrections/retractions, dataset versions and licenses; search for CAPA/deviation evidence evaluation published after this cutoff; verify each claimed novelty against the closest method; add the chosen journal's recent relevant papers if actually applicable; and describe searches without invented database hit counts.

Maintain citation keys from references.bib. Avoid quoting competitor accuracy figures as a benchmark unless task, data and metric are directly comparable and independently reproducible.
