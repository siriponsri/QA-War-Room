# QA War Room: journal and product strategy

**Version:** 0.1, 7 November 2026.  
**Chosen domain:** pharmaceutical manufacturing GMP.  
**Research design:** [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md).  
**Metrics and implementation contract:** [EVALUATION_SPEC.md](EVALUATION_SPEC.md).

## 1. Recommendation

The pharmaceutical-journal route is credible if the paper's principal question, evaluation, and implications concern pharmaceutical quality decisions. The strongest initial positioning is **evidence sufficiency for deviation/CAPA review**, especially the distinction between implementation, effectiveness, and an adequately supported closure recommendation.

An interactive interface, several named AI auditors, or a regulatory chatbot alone is not a sufficient scientific contribution. Contract reasoning and scientific fact verification can establish useful components, but contracts-only evaluation does not validate manufacturing GMP use. Sino-US-DrugQA adds a regulatory knowledge assessment; it is not a CAPA dossier benchmark.

**Working target:** Journal of Pharmaceutical Innovation, conditional on a credible pharmaceutical evaluation and a reproducible methods contribution. PDA Journal of Pharmaceutical Science and Technology is a strong subject-matter option when practical manufacturing quality implications are well established. AAPS Open is plausible when the paper makes a clear pharmaceutical-science contribution beyond an interface demonstration. These are scope assessments, not acceptance predictions.

The first phase can be solo and use public data. Human learning trials are not a prerequisite for a computational method paper. Independent domain review can occur later in the development sequence, but it is required before making strong claims that the method represents pharmaceutical practice or reliably assesses actual CAPA closure.

The intended pharmaceutical paper must make independently reviewed Manufacturing GMP evaluation its primary or predeclared key confirmatory result. Stage A open-data methods work is the starting point; Stage B gets a separate protocol lock before its held-out outputs are inspected, with native benchmarks auxiliary. If Stage B validation is unavailable, the first paper follows the technical route without claiming pharmaceutical impact.

## 2. Scope evidence and fit

The following descriptions are concise paraphrases of official sources checked on 7 November 2026. Recheck author instructions, article types, fees, and scope before submission; no impact factor, quartile, acceptance rate, or publication-time estimate is assumed.

| Journal | Official scope evidence | Appropriate QA War Room paper | Main fit risk |
|---|---|---|---|
| **Journal of Pharmaceutical Innovation** | Includes pharmaceutical regulatory affairs, information management, process automation/control, and quality management | A reproducible study of evidence-based manufacturing QA decisions with defined error types, budget-matched comparisons, and clear pharmaceutical implications | Generic agent engineering with little pharmaceutical evaluation |
| **PDA Journal of Pharmaceutical Science and Technology** | PDA describes its remit around pharmaceutical/biopharmaceutical manufacturing, quality, and regulatory science; research and technology applications are among its article types | A practical manufacturing deviation/CAPA assessment method with convincing case definitions and independent domain evaluation | Broad AI benchmark results that do not explain manufacturing consequences |
| **AAPS Open** | Welcomes experimental or theoretical pharmaceutical studies, including modeling/simulation, regulatory science, and commercial manufacturing; expects innovation in primary research | A method that advances pharmaceutical-science practice or knowledge and is evaluated accordingly | A standard RAG implementation with a game layer and insufficient scientific innovation |

Official sources:

- [Journal of Pharmaceutical Innovation: aims and scope](https://link.springer.com/journal/12247/aims-and-scope)
- [PDA: journal scope, article types, and review expectations](https://www.pda.org/pda-letter-portal/home/full-article/the-role-of-peer-review-in-the-success-of-the-pda-journal-of-pharmaceutical-science-and-technology)
- [AAPS Open: aims and scope](https://link.springer.com/journal/41120/aims-and-scope)

The table's recommended fit and risks are editorial judgments based on those scopes. They are not statements from the journals about this particular project. Before committing to a manuscript format, inspect recent papers closest to the completed work and the current submission instructions. A presubmission inquiry can be useful after a concrete abstract and evidence summary exist; do not contact an editor automatically.

## 3. Choose the manuscript according to the evidence actually obtained

### Route A: open computational method and benchmark paper

**Evidence available:** native ContractNLI/SciFact results, a reproducible derived sequential task, Sino-US-DrugQA as a separately reported auxiliary assessment, and an illustrative synthetic manufacturing casepack.

**Defensible claim:** the method changes evidence-acquisition or evidence-supported decision behavior on the specified public tasks under controlled budgets.

**Possible title:**

> Budgeted sequential evidence acquisition for auditable document decisions: an open benchmark study with a pharmaceutical manufacturing application

Use the application wording only when the paper contains a substantive, transparently labelled manufacturing extension. If the domain evidence remains only the eight demonstration cases from two templates, use a domain-neutral methods title and discuss manufacturing as a future application.

**Journal decision:** a methods/AI or broad computational-research venue may be more appropriate than a pharmaceutical journal when the main evaluation remains generic. Do not force a pharmaceutical framing by putting “GMP” in the title while reporting contract inference as the main proof.

### Route B: constructed manufacturing benchmark and method paper

**Evidence available:** Route A plus a well-specified manufacturing case corpus with explicit requirements, timelines, scope, version histories, reference decisions, and independent domain review.

**Defensible claim:** the method performs in a particular way on independently reviewed constructed manufacturing cases, with measured tradeoffs and limitations.

**Possible title:**

> Evidence sufficiency for CAPA effectiveness assessment in pharmaceutical manufacturing: a reproducible evaluation on constructed cases

**Journal decision:** Journal of Pharmaceutical Innovation is the first scope-based option. PDA JPST becomes attractive if practical investigation and quality-system consequences dominate. AAPS Open requires a clear explanation of the scientific innovation.

Constructed cases can be useful science. Their value depends on construction validity, independence, realistic variation, meaningful controls, and an honest external-validity boundary. They must not be described as actual audits or as a representative estimate of facility-level compliance.

### Route C: applicability study in manufacturing QA

**Evidence available:** Route B plus independently sampled, authorized retrospective records or a prospective shadow evaluation, with independent expert reference assessment and a predefined workflow.

**Defensible claim:** performance and workload consequences in the specified setting, population, and decision-support role.

**Possible title:**

> Evidence-grounded AI review of deviation and CAPA records: a retrospective evaluation in pharmaceutical manufacturing

Use “retrospective” only if the study actually uses retrospective real records. A shadow evaluation must remain observational if that is how it was conducted; do not imply causal workflow improvement from a single uncontrolled pilot.

**Journal decision:** JPI or PDA JPST can be well aligned, depending on the scientific versus operational emphasis. This route is not required to start the project, and it should not be made a dependency for building the public-data foundation.

### Route D: auditor training study

**Evidence available:** an instructional intervention with human participants, an appropriate comparison, unseen assessment cases, and follow-up/transfer measures.

**Defensible claim:** the observed learning effect under that study design.

**Journal decision:** education or simulation venues may be more suitable, or a pharmaceutical venue if professional pharmaceutical training is central. This is a separate research question. Model-to-model roleplay cannot demonstrate that novice human auditors learn more or that professional expertise improves.

## 4. Closest prior work and how to position the contribution

The study must directly discuss prior pharmaceutical investigation and audit work. The following are particularly relevant:

| Work | Why it matters to positioning | Comparison to make |
|---|---|---|
| Salami, Smith-Goettler, and Yadav, 2024, manufacturing-investigation preprint | Already studies LLM extraction and retrieval around real deviations | Extraction/retrieval versus sequential evidence sufficiency, access assumptions, data openness, and unsupported decisions |
| WinAI oral-solid-dose audit paper, 2026 | A direct published AI/GMP audit predecessor | Audit classification/checklists versus closure/effectiveness evidence; simulated and limited live evaluation versus the present validation layers |
| Waikar, Bhat, and Ramanathan, 2026, regulatory-compliance RAG | A peer-reviewed pharmaceutical computational precedent | Regulatory document question answering versus manufacturing case-level decision evidence |
| Sino-US-DrugQA, 2026 | Public regulatory QA benchmark with a paper | Knowledge assessment versus record-level proof of implementation or effectiveness |

Primary references:

- [Salami et al., arXiv:2404.15578](https://arxiv.org/abs/2404.15578). Cite as a preprint unless a journal version is subsequently verified.
- [WinAI publisher page, DOI 10.22159/ijap.2026v18i2.57414](https://journals.innovareacademics.in/index.php/ijap/article/view/57414)
- [Waikar et al., DOI 10.1002/psp4.70201](https://pmc.ncbi.nlm.nih.gov/articles/PMC12917324/)
- [Fu et al., DOI 10.1371/journal.pone.0343858](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858)

Do not borrow reported vendor/paper outcomes as expected QA War Room performance. A predecessor's pilot, an author's reported time saving, or a platform screenshot is not an independent validation of this implementation. No global novelty claim is needed: a carefully defined task, reusable evaluation, fair comparison, and useful failure analysis can be the contribution.

## 5. Minimum evidence package for a credible submission

### 5.1 The research question must survive removal of the interface

An editor should be able to understand the scientific contribution even if the game screen is replaced by a command-line runner. The interface can support interaction and dissemination; the paper needs an evaluable claim about decisions, evidence, learning, or workflow.

For the initial computational study, the core package is:

1. A precise task and label definition, including the distinction between source insufficiency and model abstention.
2. A documented source/lineage split that keeps related evidence and counterfactuals together.
3. A predeclared primary endpoint, sensitivity/coverage guardrails, and resource caps.
4. Strong single-agent and simple-rule baselines, plus equal-budget review controls.
5. Deployable retrieval results separated from oracle diagnostics.
6. Cluster-aware uncertainty and an honest feasibility/sample-size discussion.
7. Calibration and error analyses that explain unsupported recommendations.
8. Data/code/configuration access sufficient to reproduce the permitted parts.
9. A pharmaceutical evaluation layer proportionate to the pharmaceutical claims.
10. A clear report of null findings, runtime failures, and protocol deviations.

### 5.2 What independent domain review adds

External review tests whether the case construction, decision policy, reference evidence, and expected decisions represent the intended manufacturing use. It can identify oversimplified closure rules, unrealistic timelines, implausible records, and ambiguity that a solo author missed.

It need not be a human training trial. Reviewers can assess a fixed case corpus and reference policy before model evaluation, with independence and disagreements documented. The study should report what review was actually done, rather than using “expert-validated” as a blanket label.

For a strong pharmaceutical claim, the most valuable review is about task validity and reference decisions, not whether the interface looks realistic. If external review is unavailable initially, preserve the solo method route and label the manufacturing extension as author-constructed.

### 5.3 What not to promise

Do not claim that the system:

- Reduces real audit time without a measured workflow study.
- Improves novice auditor competence without a human learning evaluation.
- Reliably closes real CAPAs based only on open QA or contract benchmarks.
- Is regulator-approved because it cites public guidance.
- Is a validated digital twin because it contains documents and roleplay agents.
- Is superior because it uses more agents, RL, or a larger model.
- Has zero hallucinations because no errors occurred in a small casepack.

These are claim boundaries tied to evidence, not reasons to delay building the initial system.

## 6. Manuscript structure

### Introduction

Describe the manufacturing decision problem: a closure narrative can be convincing while its supporting records are incomplete, contradictory, out of scope, or inapplicable at the assessment date. Explain why implementation and effectiveness require different evidence. Ground the motivation in the applicable quality-system material and the nearest pharmaceutical AI work.

Finish with the exact hypothesis and contribution. Avoid a broad claim that “AI can transform GMP auditing.”

### Methods

Describe the system only as far as needed to reproduce the experiment. Give the environment/action space, evidence ledger, allowed information, role policies, stopping rule, budget, datasets, transformations, label provenance, split construction, baseline selection, calibration, endpoints, and statistical plan.

Put the regulator/source snapshot date beside the dataset description. Separate native reproduction from derived task results. State what the authors constructed and what was independently reviewed.

### Results

For the pharmaceutical manuscript, lead with its predeclared Manufacturing GMP comparison and guardrails, followed by native benchmark competence as auxiliary evidence, oracle diagnostics, ablations, and uncertainty. For a Stage A technical manuscript, lead with the open-data methods comparison and label the manufacturing extension appropriately. Include failures and contradictory evidence; do not allow an attractive case study to stand in for cohort results.

Use result placeholders until runs exist. A statement such as “the method reduced false supported closure recommendations by [estimate]” is appropriate only after the corresponding manufacturing evaluation is complete; a contract FSR reduction must retain its benchmark name.

### Discussion

Explain the mechanism suggested by results, plausible alternative explanations, cost tradeoffs, reference-label limitations, contamination concerns, source dependence, and transfer failures. State what the study does and does not establish about actual manufacturing decisions. Discuss next steps based on the observed bottleneck.

### Data/code and declarations

Provide a release/reproduction path, licences and attribution, model/provider details, data-access restrictions, funding, conflicts, and contributions. Describe AI assistance in the manner required by the selected journal's current policy. Confirm that authors have checked sources, code, and reported results; no AI system should be treated as an accountable author.

## 7. Product development in parallel

### 7.1 Initial product hypothesis

A focused product proposition is:

> Help a manufacturing QA reviewer identify which evidence is missing or conflicting before submitting a deviation/CAPA package for a specified review decision.

This is a hypothesis about user value, not a demonstrated market. It is narrower and more measurable than a complete autonomous audit platform. Potential early users are manufacturing QA reviewers, investigation owners, CAPA coordinators, and internal audit teams. Confirm their workflow and purchasing constraints through later authorized customer discovery.

Useful initial outputs are an evidence request list, a finding-to-source table, a scope/timeline view, unresolved contradictions, and an exportable review draft. The game/roleplay layer can make the interaction approachable and support later training; it is not the only source of value.

### 7.2 Product evidence and research evidence

| Product question | Appropriate evidence | What the benchmark alone cannot establish |
|---|---|---|
| Does it find the relevant record? | Retrieval tests and reviewer verification | Whether the customer's actual repository is complete or accessible |
| Does it reduce review effort? | Timed, defined workflow comparison | Savings in actual QA labor |
| Are findings usable? | Reviewer acceptance, correction effort, citation checking | Organization-wide acceptance or regulatory adequacy |
| Does it improve package readiness? | Independent assessment of submitted packages under a defined policy | Facility compliance or successful regulatory inspection |
| Does roleplay help learning? | Human training/transfer study | Auditor competence gains |
| Will an organization buy it? | Authorized discovery and a concrete pilot/value discussion | Market size, willingness to pay, or procurement success |

Build logging and export early so the same core can support research replay and later reviewer inspection. Keep research datasets and customer data separated. Do not turn customer records into training data or public examples without appropriate authorization and rights.

### 7.3 Product gates

1. **Offline demonstration:** deterministic records, evidence requests, traceable findings, and clear scenario labels.
2. **Research-capable engine:** stable schemas, reproducible runs, budgets, and evaluator separation.
3. **Domain review:** verify the manufacturing decision policy and case validity.
4. **Controlled evaluation:** use real or independently sourced cases under a defined review process when access becomes available.
5. **Operational integration:** define intended use, access control, record retention, model/version changes, monitoring, and quality-system responsibilities for the actual setting.

The first two can proceed solo without waiting for a proprietary site pilot. Later gates are tied to stronger product claims and actual use, not prerequisites for a local prototype.

## 8. Regulatory and rights considerations that affect the plan

Keep this section practical and versioned. It is a research/product planning note, not a legal determination about a future deployment.

### 8.1 Separate public guidance from product validation

The project's motivation is consistent with investigating evidence for CAPA and quality-system decisions, but citation of a requirement is not validation of an AI system against that requirement. The real intended use determines what must be demonstrated.

The 2026 EMA workshop report discusses ongoing Annex 22 development, including reconsideration of the draft treatment of generative/probabilistic models. It also mentions an agentic deviation-management example while noting that some examples were pilots or theoretical frameworks. Treat the report as guidance-development context, not enacted permission, a final prohibition, or independent evidence of effectiveness. Recheck the official status before operational deployment. [EMA workshop report](https://www.ema.europa.eu/en/documents/report/report-multistakeholder-workshop-expert-contributions-artificial-intelligence-guidance-development-annex-22_en.pdf)

### 8.2 Data rights and commercialization

Maintain separate records for article licences, dataset licences, code licences, and underlying regulatory/document rights. A licence on a repository does not automatically grant rights to every linked third-party source or a customer's records.

The open benchmark phase can use documented permitted access and released annotations. A later commercial product needs a source-by-source rights review for material it redistributes, embeds, or uses in training. Do not assume that a paid standards document, a publicly downloadable manual, or an open-access article grants unrestricted commercial model-training rights. Use original synthetic manufacturing records for the shareable demo and keep source attribution intact.

### 8.3 Current operational posture

The starter should present recommendations as drafts for review and retain the evidence needed to challenge them. This is the chosen initial product design. It should not be described as satisfying all applicable computerized-system, electronic-record, or manufacturing requirements merely because a human can click “approve.” Actual organizational validation and responsibilities depend on the intended use and current applicable framework.

## 9. Submission decision gates

Before choosing a journal, answer these questions using completed evidence:

| Question | If yes | If no |
|---|---|---|
| Is the central result a reproducible method/benchmark finding? | Prepare a research manuscript | Continue development; a product demo is insufficient |
| Is a pharmaceutical decision the main evaluated task? | JPI/PDA/AAPS scope can be credible | Use a methods venue or retain pharma as motivation |
| Are new manufacturing reference decisions independently reviewed? | State the reviewed scope precisely | Label the set author-constructed and limit domain claims |
| Does the proposed method beat a fair baseline or reveal a useful boundary? | Report the result and tradeoff | Publish a rigorous negative/benchmark result if it is informative |
| Does the claim involve human learning or real workflow benefit? | Include the matching human/workflow study | Remove that claim from the computational paper |
| Are data/code/licence and model-version details reproducible? | Assemble the submission package | Resolve the missing materials before submission |

A negative result does not force a change of research question after the fact. A finding that one well-designed agent matches six agents at lower cost, or that retrieval quality dominates agent structure, can be valuable if the comparison is rigorous and the limitations are clear.

## 10. Concrete next research deliverables

The next work should produce, in order:

1. A verified dataset/source manifest and native-task adapters.
2. A source-group/split inventory, including DrugQA schema limitations and SciFact label availability.
3. A reproducible single-agent baseline and resource-accounting runner.
4. A versioned controlled-disclosure task, retaining original source targets.
5. A small development comparison to choose budgets, comparator, and feasible precision.
6. A frozen protocol/analysis manifest before held-out runs.
7. A complete result bundle including failures and negative findings.
8. A manufacturing case construction/review package proportionate to the desired pharmaceutical claim.
9. A concrete journal-specific abstract and evidence summary based on what was actually completed.

RL, a six-agent cast, and a digital twin are optional later hypotheses. None is required to make the initial evidence-sufficiency study scientifically useful.

## 11. Primary reference list

1. Journal of Pharmaceutical Innovation, official aims and scope. https://link.springer.com/journal/12247/aims-and-scope
2. PDA, *The Role of Peer Review in the Success of the PDA Journal of Pharmaceutical Science and Technology*. https://www.pda.org/pda-letter-portal/home/full-article/the-role-of-peer-review-in-the-success-of-the-pda-journal-of-pharmaceutical-science-and-technology
3. AAPS Open, official aims and scope. https://link.springer.com/journal/41120/aims-and-scope
4. Salami H, Smith-Goettler B, Yadav V. Manufacturing investigations preprint, 2024. https://arxiv.org/abs/2404.15578
5. Jayaprakash Narayanan J. and colleagues. WinAI audit paper, 2026. https://journals.innovareacademics.in/index.php/ijap/article/view/57414
6. Waikar S, Bhat AG, Ramanathan M. Regulatory-compliance RAG, 2026. https://pmc.ncbi.nlm.nih.gov/articles/PMC12917324/
7. Fu X, Chen Z, Lu W. Sino-US-DrugQA, 2026. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343858
8. EMA. *Multistakeholder workshop on expert contributions to artificial intelligence guidance development (Annex 22)*, workshop dated 30 June 2026. https://www.ema.europa.eu/en/documents/report/report-multistakeholder-workshop-expert-contributions-artificial-intelligence-guidance-development-annex-22_en.pdf

No submission, editor contact, customer outreach, or publication has been performed by creating this strategy.
