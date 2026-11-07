# GOAL — QA War Room

**Version:** 0.1 · **Decision date:** 7 November 2026  
**Owner's choice:** solo project; Manufacturing GMP; open published benchmarks first; product and pharmaceutical journal in parallel.

## North star

Help a reviewer decide **what evidence to request next and whether that evidence justifies a specific CAPA effectiveness/closure claim**, while producing a traceable, editable report. The system should be useful when it cannot yet decide: its request for missing evidence is itself a product outcome.

The scientific objective is to test whether explicit evidence-sufficiency and applicability checks improve supported decisions under a fixed acquisition budget, compared with simpler methods. Improvement is a hypothesis. The research remains valuable if a simpler method wins or if multiple agents do not help.

## Working names

- Product: **QA War Room**
- First module: **CAPA Evidence Review**
- Constructed research resource: **QA War Room Manufacturing GMP Case Pack** (working name; not yet a validated benchmark)
- Working manuscript: *Evaluating evidence sufficiency for CAPA effectiveness claims through budgeted document acquisition in pharmaceutical manufacturing.*

Avoid "validated digital twin", "autonomous GMP auditor" and "expert auditor" as performance claims. Digital-twin and RL work are later hypotheses, not prerequisites for the first paper.

## Contributions to test

| Contribution | Scientific question | Reusable product result |
|---|---|---|
| Traceable case and evidence specification | Can verdicts be evaluated against explicit facts, applicability and predefined sufficiency rules? | Versioned documents, checklist, replay and evidence-linked report |
| Sequential evidence policy | Does choosing the next record improve performance or reduce cost at matched decision quality? | Next-evidence request recommendation |
| Sufficiency and applicability checks | Do they reduce unsupported positive closure claims without collapsing into abstention? | Evidence-gap and contradiction alerts |
| Matched counterfactual evaluation | Does changing a decisive fact change the decision appropriately while irrelevant changes do not? | Regression tests and interactive "what changed?" debrief |

These are proposed contributions. Related work already addresses pharmaceutical investigations, AI audits, retrieval-grounded compliance and multi-agent review. The narrower evaluation design must earn its novelty through a current literature comparison and credible experiments.

## Product completion conditions

1. A person can open a case, understand the claim and budget, request records, inspect provenance, submit a claim verdict, and export a report.
2. Active sessions expose only requested records. Terminal evaluation is explicit and logged.
3. Cases, policies, rules, prompts and report versions are identifiable.
4. A report distinguishes evidence seen, evidence requested but unavailable, unresolved questions and supported findings.
5. The offline mode works without model credentials; a future provider adapter cannot read gold.
6. The product never represents a simulated decision as a batch release, certification or approved real CAPA closure.

## Research completion conditions

1. Native published benchmark tasks reproduced or carefully documented with a versioned evaluation manifest.
2. Any sequential adaptation is a separate task with its own observation model, metrics and split.
3. Pharma cases have declared rules, provenance and a documented review process proportionate to claims.
4. Baselines use comparable observation, action, context and monetary/token budgets.
5. Primary endpoint, guardrails, exclusions, statistical unit and analysis are frozen before final test.
6. Independent source/case groups remain held out; no test answer leakage into prompts or training.
7. All runs including failures and null results can be reconstructed; uncertainty is reported.
8. Manuscript claims stay within the data. No human-learning or real-world effectiveness claims without corresponding studies.

## First release exclusions

No six-model training, full-facility twin, production eQMS integration, autonomous remediation, regulated electronic signatures, batch release, certification, clinical decision support, multi-tenant hosting or broad legal equivalence across jurisdictions.

## Success ladder

Engineering demo → verified native benchmark pipeline → credible sequential evaluation → reviewed pharma transfer study → research manuscript and limited product pilot → operationally validated integration. Each rung requires new evidence; finishing the previous one does not imply the next.
