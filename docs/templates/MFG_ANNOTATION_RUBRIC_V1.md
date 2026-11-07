# Manufacturing GMP annotation rubric v1

Version: 1.0, 7 November 2026. Intended use: independent annotation of original fictional site case packets. This rubric is not a regulatory standard, an operational CAPA approval process or evidence that expert review has occurred.

## What to assess

Assess the **specific closure/effectiveness claim at its stated cutoff**, using the complete available packet and its explicit synthetic site SOP. Do not judge the whole site, release a batch or add an unstated universal GMP threshold. Each case is an isolated alternative scenario; repeated procedure/product identifiers across packets do not describe one shared real-world site history.

First assess pharmaceutical plausibility and whether the declared rules make the intended claim defensible. The authored root-cause premise is not empirical causal validation. Flag incomplete investigations, unsupported causal assumptions, implausible monitoring or missing relationships even if the structured exercise can be solved mechanically. The purpose of independent review includes challenging the case design.

## Decision labels

| Label | Full-packet meaning |
| --- | --- |
| supported | Applicable available evidence establishes every stated criterion, with no unresolved material contradiction or undefined requirement |
| contradicted | Applicable evidence establishes at least one explicitly required condition as false, refuting the positive conjunction of criteria |
| insufficient | No decisive applicable failure is established, but the available packet does not establish all required conditions |
| ambiguous | More than one decision remains defensible because the requirement/record interpretation is unresolved; explain alternatives and needed clarification |

A wrong-line/product/cohort report or a record inadmissible after the cutoff usually leaves the correct-scope/as-of fact unknown; it does not itself prove the process failed. A record explicitly showing training against an obsolete required procedure can establish failure of that particular declared condition. A training completion flag alone does not establish an effectiveness outcome.

Reference annotation uses the full available source packet. Do not turn a policy's failure to request an obtainable record into full-source insufficiency. A record explicitly marked source_unavailable is genuinely absent from this authored packet. Distinguish that from a budget/exposure restriction or an unread document.

## Criterion-level coding

For each SOP criterion, retain its ID and record pass, fail, unknown or ambiguous with notes where unresolved. Identify the exact document and fact/metadata location used.

- pass: an applicable fact establishes the stated condition.
- fail: an applicable fact explicitly conflicts with the stated condition.
- unknown: necessary evidence is absent, inapplicable or does not record the required fact.
- ambiguous: the acceptance requirement or admissible interpretation is not adequately defined.

A single applicable failure can refute the positive all-criteria claim even when other conditions are unknown. Where no failure resolves the claim, do not conceal genuine ambiguity by forcing a unique class. Use revise or exclude_ambiguous for unresolved cases; ambiguous cases cannot enter the primary set unchanged under this draft plan.

## Applicability and provenance

Check product, line, predefined follow-up cohort and original affected batches where relevant. Check the stated cutoff and date semantics. In this exercise recorded_at means the completed approved record available to the reviewer; effective_from denotes applicability. Both must be on/before cutoff for admissibility under this synthetic policy. This rule is a declared exercise convention, not a rule about all real retrospective records or ingestion dates.

Distinguish a document's own revision from the governing procedure revision in its facts. A training record can be document revision 1 while correctly documenting procedure revision 2. Review the actual requirement and trained procedure field.

## Citation format

Use an available document ID and exact JSON pointer, for example:

```json
{"record_id":"D1","pointer":"/facts/criteria"}
```

The example is a locator format, not an answer to a case. Cite facts and any scope/time/SOP condition necessary for the reasoning. An unavailable document has no citable payload; describe its absence separately. Alternative support sets are lists of these citation objects. Software checks existence/visibility/version only; reviewers must assess semantic relevance and sufficiency.

## Required review record

Record reviewer code and verified manufacturing QA/CAPA experience through the owner-agreed roster, independence/conflicts, case_version, plausibility, full-packet verdict, criterion judgments, citations, rationale, alternatives, ambiguity notes and primary disposition. Use include, revise or exclude_ambiguous. Do not use include to erase an unresolved ambiguous verdict.

Review independently before discussion. Do not consult authored candidate decisions, paired-case orientation or system outputs. Do not delegate the reference label to an LLM. Initial files must be retained unchanged before a separate adjudication record is prepared. The software does not authenticate qualifications or independence and never converts form completion into pharmaceutical validation.
