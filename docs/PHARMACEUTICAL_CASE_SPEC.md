# Pharmaceutical case specification

G4 implementation update (7 November 2026): [MANUFACTURING_CASE_PACK.md](MANUFACTURING_CASE_PACK.md) documents the 48-case, six-family author draft and its implemented structured-rule subset. [The independent review plan](INDEPENDENT_REVIEW_PLAN.md) and [rubric](templates/MFG_ANNOTATION_RUBRIC_V1.md) are prepared locally. Six cases retain unresolved ambiguity and all references remain unreviewed. The full scientific/operational requirements below must not be read as already independently validated.

## 1. Intended scientific object

Evaluate a specific statement such as: "At the assessment cutoff, this CAPA has implemented its required actions and demonstrated effectiveness for the stated product, line and batch cohort." This is narrower than deciding whether an entire manufacturing site is GMP compliant.

The case rules make the statement testable. The benchmark should not invent universal GMP thresholds such as "three batches always prove effectiveness." A synthetic site protocol may specify a number of follow-up batches for a particular fictional case; that is a declared scenario rule, not a regulatory rule.

## 2. Pharmaceutical rationale and source hierarchy

ICH Q10 section 3.2.2 and its lifecycle table describe a CAPA system and evaluation of action effectiveness. EU GMP Chapter 1 section 1.4(xiv) links investigation, corrective/preventive actions and monitoring/assessment of effectiveness. These motivate the task; they do not supply a universal case-specific pass/fail algorithm. [ICH Q10](https://database.ich.org/sites/default/files/Q10_Guideline.pdf); [EU GMP Chapter 1](https://health.ec.europa.eu/document/download/e458c423-f564-4171-b344-030a461c567f_en?filename=vol4-chap1_2013-01_en.pdf).

For each case, distinguish: applicable regional requirement; broader guideline; approved synthetic site procedure; and observed record. Record jurisdiction and version. The starter does not assert equivalence among US, EU, Thai and PIC/S frameworks. FDA Q9(R1) provides risk-management context; use risk to justify the case's review effort and criteria, not to excuse missing evidence. [FDA Q9(R1)](https://www.fda.gov/media/167721/download).

## 3. Case card fields

- case_id, family_id, template_id, dataset_version, author, review status;
- fictional product/process/line and scope of the claim;
- assessment cutoff and explicit date semantics;
- approved SOP/protocol ID, revision, effective date and applicability;
- triggering deviation, known impact and investigation boundary;
- CAPA actions, responsibilities, deadlines and implementation records;
- effectiveness criterion, monitoring window and follow-up cohort;
- evidence inventory with IDs, provenance, document type, owner and acquisition cost;
- availability condition and response when a requested record is unavailable;
- reference label, minimal sufficient evidence sets and decisive facts;
- alternative valid supporting sets and acceptable expressions of uncertainty;
- counterfactual sibling IDs and exact manipulated facts;
- ambiguity, exclusions, assumptions and reviewer disagreements.

The delivered JSON fixtures implement a smaller schema sufficient for engineering. The fields above are the research schema to finalize before expanding the corpus.

## 4. Decision rubric

**Supported:** applicable evidence satisfies the stated scenario criteria, covers the correct scope and time, and contains no unresolved material contradiction under the case rule. This is support for the specified claim, not proof of universal process effectiveness.

**Contradicted:** applicable evidence establishes a failure of a condition required by the stated claim, for example a documented failed criterion or a relevant reopening before the cutoff. A mismatched document can leave the correct-scope claim unknown rather than automatically false.

**Insufficient:** no justified positive or negative decision can be made from the available relevant evidence. Distinguish genuinely unavailable evidence in the full packet from a policy that stopped before acquiring obtainable evidence. Score full-packet correctness and observation-supported behavior separately.

A closure cover sheet and a completed training register may document administrative actions. They do not by themselves establish an effectiveness outcome. Conversely, a low evidence volume does not imply a failure if an authorized, appropriate record already establishes the narrowly defined fact.

## 5. Proposed failure families

| Family | Decisive question | Controlled contrast |
|---|---|---|
| Implementation versus effectiveness | Were actions completed, and was the intended outcome evaluated? | Same closure sheet; effectiveness record present versus unavailable |
| Recurrence | Did the same failure recur under the stated criterion? | Change only a relevant follow-up result |
| Scope | Does the report cover this product/line/cohort? | Correct cohort versus unrelated cohort |
| Temporal applicability | Was supporting evidence valid at the assessment cutoff? | Same report before versus after cutoff |
| Revision applicability | Was training/change implementation based on the governing revision? | Current versus obsolete procedure revision |
| Investigation scope | Were related batches considered as required by the scenario rule? | Complete versus explicitly incomplete affected-batch review |
| Change control | Was the change evaluated according to its approved conditions? | Aligned implementation versus undocumented change |
| Status contradiction | Does a later applicable status supersede a closed cover sheet? | Closed versus reopened before cutoff |

Do not mix factual changes and more persuasive language within a supposedly single-fact pair. Non-decisive perturbations should include record order, neutral paraphrases and irrelevant records. A model should change for material evidence and remain stable for cosmetic changes.

## 6. Review and adjudication

Write the case and its rule before running evaluated models. Independently review a blinded subset or all final evaluation families when feasible. Reviewer tasks: assess pharmaceutical plausibility, rule applicability, label correctness, supporting-set sufficiency, ambiguity and whether the counterfactual manipulation truly changes only one material fact.

Use a fixed review form. Preserve initial ratings, disagreements and final adjudication. If only one domain reviewer is available, report that limitation; do not compute inter-rater agreement from a single person's repeated answers as if multiple reviewers participated. Synthetic generation by the same LLM that is evaluated is a bias to examine, not an independence guarantee.

## 7. Scaling criteria

Do not scale from eight demo cases to thousands by paraphrasing. First achieve diversity in failure mechanisms, document styles, scopes and independent templates. Audit label balance and shortcuts. Use a pilot to estimate ambiguity and per-family review effort. Freeze final families and reference answers before model comparison. The number of independent families, including challenging ambiguous cases, matters more than raw prompt count.

## 8. Operational product outputs

A report should contain the assessed claim and cutoff, reviewer identity/role, evidence IDs and exact locations, applicable SOP/rule version, supported facts, contradictions, missing information, proposed next request and review status. The report must make unresolved uncertainty visible. A regulated workflow requires additional intended-use validation and controls beyond this starter.
