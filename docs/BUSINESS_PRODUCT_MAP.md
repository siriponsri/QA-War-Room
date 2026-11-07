# QA War Room — research-to-product and business map

**Planning date:** 7 November 2026  
**Status:** testable business hypotheses, not validated market demand or financial projections.

## 1. What could be sold

The first plausible offer is **an evidence investigation simulator for pharmaceutical QA training**, accompanied by reviewed case packs, replay, and source-linked debriefs. A second, later offer is **an evidence-readiness workspace for deviation/CAPA reviewers**. The second requires substantially stronger validation and data-governance work because it handles real organizational records and can influence real decisions.

The buyer-facing promise should describe a task the product helps complete: practice asking for the right evidence; inspect why a closure claim is or is not justified; assemble a traceable packet for human review. Avoid an “AI auditor that guarantees compliance” promise. The starter and proposed study cannot support it.

The defensible asset would be a combination of carefully scoped manufacturing cases, evidence/dependency annotations, reproducible evaluation, and a workflow that reviewers actually find useful. The number of agents, a chat interface, or an RL label is not by itself a business advantage.

## 2. Candidate offerings and the order to test them

| Offering hypothesis | Prospective buyer | Deliverable | First validation question | Stage |
| --- | --- | --- | --- | --- |
| Training case pack | QA trainer, consultant, university course | Synthetic cases, debriefs, replay, instructor notes | Does the case teach a decision distinction the trainer needs? | First |
| Team training workspace | QA training manager | Private cohorts, assignment, case versioning, reviewer notes | Can the trainer integrate it into an existing activity without excessive setup? | After useful case packs |
| Evidence-readiness review | Deviation/CAPA coordinator or QA reviewer | Missing-evidence questions, traceable checklist, draft assessment | Does it reduce reviewer effort while preserving detection of important errors? | After domain and pilot validation |
| AI evaluation kit | Organization comparing internal/vendor AI | Versioned benchmarks, runner, evidence errors, reproducible reports | Will the organization use results to make an evaluation decision? | Parallel research-derived option |
| Organization-specific process model | Pharmaceutical quality organization | Controlled process/evidence links and synchronization | Does maintaining the model produce a measurable benefit beyond document search? | Later |

These are separate purchase hypotheses. A successful educational demo does not prove that a manufacturer will buy a production readiness tool. Interviews and scoped pilots should test which buyer has the problem, budget, authority, and a usable path to deployment.

## 3. How the research becomes product value

| Proposed scientific contribution | Product feature it enables | Useful customer outcome to test | Proof needed |
| --- | --- | --- | --- |
| Manufacturing scenarios with explicit evidence sufficiency criteria | Reviewable cases and a case authoring format | Trainers can explain why a conclusion is justified | Independent review and reliable annotations |
| Sequential evidence acquisition under a budget | Suggested next evidence request | Reviewers ask fewer irrelevant questions without missing decisive records | Matched-budget comparison; representative cases |
| Temporal, lot, process, and revision consistency checks | Scope mismatch alerts in a packet | Reviewers notice that evidence belongs to another cohort or period | Controlled counterfactual cases and external review |
| Citation/span sufficiency evaluation | Source-linked draft checklist | Reviewers can verify the reason for a conclusion | Span-level gold and unsupported-claim analysis |
| Calibrated abstention | “Evidence insufficient” queue and requested follow-ups | Uncertain packets remain visible for review | Risk/coverage analysis; false support and false contradiction rates |
| Counterfactual sensitivity | Training contrasts and regression tests | Users see which changed fact legitimately changes the outcome | Matched-pair consistency and explanation checks |
| Same-budget agent comparisons | Choose a simpler or more capable policy | More useful decisions for a given time/cost | Repeated runs and uncertainty estimates |
| Reproducible process/evidence state | Replay and change history | Teams can inspect how a conclusion changed after new evidence | Provenance checks and actual workflow validation |

The strongest result would be a reliable reduction in **unjustified support for closure** without simply abstaining on everything or generating more false findings. That result must be demonstrated experimentally. It is a target outcome, not a capability claimed for this package.

## 4. A concrete initial use case

A trainer wants participants to distinguish implementation evidence from effectiveness evidence. A fictional manufacturing deviation has a documented corrective action and a signed closure form. The participant must inspect the stated effectiveness criterion, the monitored process/lot cohort, and the follow-up record to determine whether that exact closure claim is supported at the assessment date.

In paired variants, a decisive fact can change while the surrounding story remains similar: the follow-up covers the required cohort versus a different one; the evaluation occurs after the monitoring window versus before it; recurrence is absent versus recorded. The product can replay those variants and explain why a superficially complete packet can lead to different justified decisions.

This example is an authored training design. It does not assert that every real CAPA needs the same follow-up window or that the presence/absence of one record determines legal GMP status. Actual criteria depend on the scoped quality process, risk assessment, and applicable requirements.

## 5. Solo-project business development sequence

### Step 1 — demonstrate one complete investigation

Use the offline starter to demonstrate the claim, records, requests, cost, decision, and debrief. The aim is to obtain concrete criticism: which fact is unrealistic, which document is missing, which conclusion is too strong, and which interaction slows the reviewer. Record corrections as changes to the case specification.

### Step 2 — validate the problem with structured interviews

Interview people who perform or review the relevant task. A small initial convenience sample is sufficient to discover problems; it is not market-size evidence. Ask about a recent case, the records they needed, where evidence mismatches occurred, what preparation took effort, and what a useful training or readiness output would look like. Avoid asking only whether they like AI.

For each interview, distinguish observed workflow facts from the participant's guesses about purchasing. Do not record confidential manufacturing details unless the participant has authorization and the project has an agreed handling route. Fictional examples can answer most early product-design questions.

### Step 3 — test a reviewed case pack

Offer a small, explicit case pack to a trainer or course partner. Define what counts as success before running it: task completion, clarity of the debrief, types of reasoning mistakes discovered, reviewer workload, and whether the trainer would reuse the activity. Track revisions and negative feedback.

If learning improvement is a research claim, add a suitable study design, participants, ethics review where applicable, baseline/comparator, outcome definition, and retention/transfer testing as appropriate. A post-demo satisfaction survey does not establish improved auditing performance.

### Step 4 — test willingness to commit

A request for another case, participation in a pilot, a signed pilot scope, or a budget-holder discussion is stronger commercial evidence than a favorable comment. Use those commitments to decide whether to develop team administration, hosted access, or bespoke case authoring.

No price is prescribed here. Price discovery should reflect the buyer's alternative, delivery effort, review cost, support burden, and actual willingness to pay. There is no verified market size, revenue forecast, or ROI calculation in this starter.

### Step 5 — consider a bounded readiness pilot

Only after the evidence method and case quality are credible, scope a pilot that assists a human reviewer. Start with a controlled packet and a defined list of questions. Measure unsupported conclusions, missed decisive evidence, time to verified review, and correction burden. Preserve reviewer authority over the final assessment.

The next feature should follow a demonstrated bottleneck. If onboarding records is harder than model reasoning, improve import/provenance. If users cannot trust the evidence links, improve citations. If the simple policy is adequate, do not add more agents merely for presentation.

## 6. Packaging options

The research and commercial packages can coexist, but their rights and purposes should be explicit.

- **Open research repository:** original code, reproducible evaluation, licensed adapters, metadata, and a redistributable subset of authored scenarios. This supports verification and reuse.
- **Reading pack:** locally obtained papers and regulatory references for the owner. Inclusion in this starter does not grant permission to republish those PDFs in a public repository or a commercial product.
- **Reviewed scenario packs:** organization- or course-specific cases with documented permissions and versioned reference answers. These could be a service or paid content if demand is established.
- **Hosted workspace:** optional convenience, administration, private cohorts, and support. Hosting adds operational responsibility; it is not necessary for the first paper or demo.
- **Private evaluation service:** a scoped comparison of candidate models/policies using agreed test cases. Report limitations and avoid treating one benchmark rank as a guarantee of operational safety.

Choose the code license and data licenses separately. An open-access article, an open dataset, a model's terms, and a downloaded guidance document can have different reuse conditions. Record the actual permitted use of each asset before including it in a paid offering.

## 7. Evidence of business value

Use a progression of evidence rather than a single impressive demo:

| Evidence level | What it supports | What it does not support |
| --- | --- | --- |
| Runnable synthetic demo | Feasibility of the workflow | Manufacturing effectiveness, adoption, or willingness to pay |
| Held-out scenario benchmark | Performance on that defined constructed task | Broad real-world audit readiness |
| Independent domain review | Content plausibility and bounded label validity | A product-market fit or learning claim |
| Observed training use | Usability and workflow fit for the observed participants | Generalized improvement without a suitable study |
| Controlled retrospective packet study | Performance within the sampled packet population | Prospective operational impact or all GMP processes |
| Bounded live pilot | Observed benefit and burden under the pilot conditions | Universal regulatory acceptance or autonomous decision authority |
| Repeat paid use | Commercial value to those buyers | Scientific validity of every model output |

A research contribution is stronger when it identifies where a method fails, explains the failure mechanism, and changes a useful product behavior. A negative result can still improve the product: for example, if multi-agent debate increases unsupported conclusions at equal cost, a simpler single-agent workflow may be the better implementation.

## 8. Cost structure to record from the start

Track actual builder time, domain review/annotation time, inference tokens and cost, evidence parsing/OCR cost, hosting, data preparation, customer support, and case maintenance. Separate one-time research cost from recurring per-session product cost.

The offline starter has no model usage cost because it makes no model calls. This does not predict the cost of a future LLM-backed session. Log the selected model/version, pricing date, tokens, retries, and total usage when that integration is added; avoid hard-coded business forecasts based on a temporary API price.

## 9. Claims for a first product page

At the starter stage, defensible wording would be:

> Practice evidence-based decisions in synthetic manufacturing quality scenarios. Request records, assess a scoped closure claim, and inspect a replayable debrief.

After a reviewed benchmark, the product page may describe the benchmark and exact evaluation setting. After an appropriate user study, it may describe the observed outcome with its population and limits. Preserve that chain from evidence to claim.

Avoid unsupported wording such as “guarantees GMP compliance,” “replaces expert auditors,” “validated digital twin,” “proven training effectiveness,” or numerical productivity/accuracy claims that have not been measured. An attractive interface should make the evidence easier to inspect, not imply stronger validation than exists.

## 10. Owner decisions at the next commercial gate

Before committing to a paid pilot, choose:

1. Whether the first offer is training content, an evaluation tool, or readiness assistance.
2. The manufacturing process and case scope for that offer.
3. A named buyer/user hypothesis and the evidence needed to accept or reject it.
4. The qualified reviewer arrangement and rights to the records used.
5. The permitted environment and model routing for any private documents.
6. A concrete pilot deliverable, acceptance measure, support boundary, and price-discovery method.

These decisions can be made after the open starter and baseline experiments. They should not expand the current solo project into a full QMS, document-management platform, or autonomous pharmaceutical decision system.
