# Manuscript scaffold

**Status:** prospective structure; no results have been generated for a scientific manuscript.

G6 local preparation now supplies a concrete [manuscript draft](../manuscript/draft.md), [source-status record](../manuscript/SOURCE_STATUS.md), [claim ledger](../manuscript/claims.json), [prospective pilot brief](../manuscript/PILOT_BRIEF.md) and [reproducibility builder/rehearsal](G6_REPRODUCIBILITY.md). The generated draft contains checked engineering counts and explicitly NOT_RUN scientific results. It is not reviewed, submitted or publication ready. The outline below remains the prospective scientific structure.

## Working title

*Evaluating evidence sufficiency for CAPA effectiveness claims through budgeted document acquisition in pharmaceutical manufacturing*

The final title should follow the evidence. If only generic native benchmarks are completed, remove the pharmaceutical effectiveness implication and choose a methods venue.

## Core question

Can an evidence-acquisition policy with explicit applicability and sufficiency checks reduce unsupported support for a CAPA effectiveness claim, without unacceptable loss of legitimate support or decision coverage, under comparable resource budgets?

## Abstract structure

- Background: the practical distinction between completed actions, applicable evidence and demonstrated effectiveness.
- Objective: the narrow testable question above.
- Methods: dataset provenance; native foundations; independently reviewed manufacturing cases if obtained; grouped split; baseline budget; reference-label protocol; primary endpoint/guardrails.
- Results: **not yet available**. Populate only from the locked analysis.
- Conclusions: state the supported result and its limits; no real-world effectiveness or learning claim without corresponding evidence.

## Introduction

Establish the pharmaceutical decision problem using ICH Q10/EU GMP sources. Compare Salami's manufacturing-investigation work, WinAI, regulatory RAG and IntelliAudit. Explain why the present test concerns sequential sufficiency and applicability rather than only information extraction or plausible role dialogue. End with predeclared questions and a modest contribution statement.

## Methods

1. Intended use and claim definition.
2. Public benchmark acquisition, licenses, versions and native metrics.
3. Sequential observation/action model and information budget.
4. Manufacturing case construction, provenance, criteria and independent review.
5. Counterfactual/materiality controls and family split.
6. Baselines, provider settings and resource accounting.
7. Reference labels and primary/secondary endpoints.
8. Statistical analysis, calibration, multiplicity and failure handling.
9. Reproducibility, data availability and model-use disclosure.

## Planned tables and figures

| Output | Purpose | Source required |
|---|---|---|
| Table1: prior-work comparison | Distinguish the contribution | Verified primary papers |
| Table2: dataset/family inventory | Show domain and independence | Frozen data manifest |
| Table3: main comparison | Primary endpoint plus guardrails | Locked runs and analysis |
| Table4: ablations | Isolate mechanism from compute | Prespecified comparisons |
| Figure1: task and evidence boundary | Make evaluation reproducible | Actual system definition |
| Figure2: error versus acquisition cost | Test efficiency | All runs, including failures |
| Figure3: risk/coverage | Show abstention tradeoff | Development-frozen calibration |
| Figure4: paired counterfactual behavior | Show material-evidence sensitivity | Grouped paired results |
| Case walkthrough | Connect result to product | Cited records and honest failure example |

## Discussion

Explain which evidence failures remain, whether additional roles help beyond more computation, where simple rules suffice, how data-generation/review choices affect conclusions, and what additional evidence would support operational use. Describe deployment boundaries without turning the discussion into a general compliance checklist.

## Claims that require extra evidence

- "Improves pharmaceutical audit quality": reviewed domain outcome, not generic NLI alone.
- "Reduces staff time": observed task-time study, not API latency.
- "Trains better auditors": human learning/transfer assessment.
- "Generalizes across sites": external or genuinely held-out site/process evidence.
- "Digital twin": real referent, synchronization and intended-use fidelity validation.
- "Safe for GMP decisions": substantially more operational validation than a benchmark.

## Supplement and disclosures

Include annotation rubrics, reference examples, split IDs, error taxonomy, prompts, model settings, cost basis, all analyzed runs and deviations from the protocol. Disclose AI assistance accurately under the chosen journal's current policy. Human authors remain accountable for citations, data and interpretation. A single software author can conduct the project; acknowledge/credit external domain-review contributions according to actual contribution and journal criteria.
