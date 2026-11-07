# G4 Manufacturing GMP case pack

Version: `qawr-manufacturing-gmp-v1`, 7 November 2026. Status: **original synthetic author draft, unreviewed**. Prepared locally without a model/provider/API. The original eight-case demo, native benchmark and G3 task are preserved as separate artifacts.

## Implemented resource

The pack contains 48 cases from six construction templates/families, six explicit synthetic site SOPs, seven record slots per case, candidate-reference criterion traces, grouped partitions, controlled-contrast lineage and a separate independent-review export. Cases assess a specific CAPA closure/effectiveness claim, not site-wide GMP compliance or batch disposition.

| Construction family | Case-specific issue |
| --- | --- |
| Packaging reconciliation | Aggregate unreconciled-unit criterion over the declared follow-up cohort |
| Blending parameters | Predefined out-of-range-check criterion |
| Setup/change control | Runs outside the documented approved configuration |
| Recurrence after training | Related recurrence under declared follow-up exposure |
| Investigation cohort | Review of every original affected batch, distinct from the follow-up cohort |
| Effectiveness window | Eligible operating days, distinct from elapsed calendar days |

The scenario populations are fictional nonsterile oral-solid processes. All thresholds, cohort counts and cutoffs are synthetic site rules. They are not universal GMP requirements or verified regulatory equivalence. Root-cause adequacy and pharmaceutical plausibility remain independent-review questions.

Each family has eight sibling worlds: a complete anchor, one decisive-measure change, genuinely unavailable verification evidence, wrong-line evidence, post-cutoff evidence, obsolete trained-procedure revision, a non-decisive context change and an unclear acceptance criterion. Inputs do not contain the authored label or a readable variant name in case IDs/titles. Inventory order is fixed within a family; only acquired records disclose dates, revisions, scope, availability and facts.

Draft author-rule candidates are 12 supported, 12 contradicted and 18 insufficient. Six additional cases have no unique candidate and are preflagged ambiguous/excluded from the draft primary set. These are construction counts, not measured model outcomes. Pair lineage contains 30 author-rule label-changing contrasts, six preserving contrasts and six unresolved-ambiguity contrasts. None is independently validated.

## Case cards and records

Cards identify the claim, cutoff, fictional product/line, original affected batches, follow-up batches, governing SOP, process, case/template/family version and review status. The runtime observation whitelists the necessary public fields and omits family/split/construction tags and reference metadata.

Record slots are the approved synthetic SOP, deviation investigation, CAPA plan/implementation, training roster, follow-up data, related-deviation/status register and an unrelated context log. Records retain owner, document revision, recorded/effective dates, approval state, scope, exact structured facts and a matching human-readable rendering. SOP approval precedes implementation/training; follow-up occurs afterward in the anchor. A document revision is distinct from the procedure revision that training covers.

One request costs the catalogued credits; unavailable evidence and exposure-cap denials still consume that cost. Duplicate requests are idempotent. Supported/contradicted submissions require unique citations to exact JSON pointers in documents actually delivered. Insufficient and abstain are separate actions. Terminal feedback is not available before submission. The byte cap counts serialized delivered records, not model tokens.

## Reference construction and limits

Input generation and reference calculation are separate modules. No input-builder or runtime lookup needs evaluator files. The evaluator applies the explicitly authored SOP operators and applicability checks to full available source records. A wrong scope or inadmissible date produces an unknown condition, not a fabricated regulatory violation; an applicable explicit failed criterion can refute the positive all-criteria claim. Unknown/undefined acceptance is preserved rather than silently repaired.

Candidate references retain per-criterion IDs, fact locations, expected/observed values, status/reason, required source-unavailability checks, declared record witness sets, ambiguity and author origin. Witnesses for unavailable evidence refer to the acquired surrounding records plus a separately required availability check; they do not require citing nonexistent payloads. Ambiguous cases have no resolved witness set. These sets are author-defined and executable under the case budget, not independently established minimal semantic evidence.

The evaluator also reports observed-evidence rule consistency and citation-location coverage separately from candidate-label agreement. A lucky correct source label with an unacquired SOP or wrong citation does not establish observed support. Semantic rationale quality is not automatically graded.

## File separation and grouping

The verified generated pack is at data/derived/manufacturing-gmp-v1-final/ and is ignored by Git.

- public/cases.jsonl: case cards without authored outcomes.
- private/records.jsonl: the environment's full source records; never supply the whole file as a policy observation/index.
- public/splits.json: two construction families each in provisional train/dev/test, all eight siblings together.
- authoring/lineage.jsonl: construction interventions, kept out of runtime observations and reviewer packets.
- evaluator/gold.jsonl and pairs.jsonl: candidate labels, criterion traces, uncertainty and controlled-contrast outcomes.
- PACK.json: source/rule versions, builder hashes, file integrity, original-content rights status and unreviewed state. Written last.

Common schema scaffolding and solo authorship limit independence. Six templates are not six independently reviewed sites. The provisional split is not a confirmatory study lock. Current draft schema refuses a manifest claiming independent validation; real review/adjudication requires a new controlled reference release.

## Commands

Run from the source workspace with Python standard library. Use new output paths; no old pack, walkthrough or intake is overwritten.

```powershell
rtk proxy py -3 -m qa_war_room.pharma prepare --output data/derived/my-manufacturing-v1
rtk proxy py -3 -m qa_war_room.pharma exercise --pack data/derived/my-manufacturing-v1 --output runs/my-g4
rtk proxy py -3 -m qa_war_room.pharma score --pack data/derived/my-manufacturing-v1 --output runs/my-g4
rtk proxy py -3 -m qa_war_room.pharma review-export --pack data/derived/my-manufacturing-v1 --output reports/my-g4-review
rtk proxy py -3 -m qa_war_room.pharma readiness --pack data/derived/my-manufacturing-v1 --output reports/my-g4-readiness
```

The walkthrough is a deliberately coauthored acquire-all-then-rules engineering check, not a trained/independent auditor or an LLM experiment. It reads no gold. Separate scoring replays source responses against the frozen manifest before reading reference data. Six unclear-rule cases abstain; the remaining 42 candidate matches establish only executable fixture consistency.

The current review packet is at reports/g4-independent-review-v1-final/reviewer/; open INDEX.md for 48 human-readable blinded cases. Only that reviewer folder and the identical rubric should be provided externally after the owner chooses reviewers/processing scope. Keep owner/ local. No export has been sent to anyone.

Use [the annotation rubric](templates/MFG_ANNOTATION_RUBRIC_V1.md) and [independent review plan](INDEPENDENT_REVIEW_PLAN.md). Templates remain blank. The intake preserves received bytes and flags incomplete/malformed records; even complete forms cannot establish identity/independence, alter gold or certify pharmaceutical validity. A readiness report retains the outstanding independent review, adjudication and reference-lock gates.

## Verification and continuation

See STATUS.md and runs/G4-VALIDATION.json for actual commands/results. Tests cover case/pair balance, grouped descendants, chronology, input/gold separation, source applicability, unknown versus contradiction, ambiguity, obtainable witnesses, request/citation budgets, terminal transitions, gold-free walkthrough/replay, source tampering, blinded export and incomplete/complete-structure intake without reference promotion. No paid API, real company data, external expert rating, human-learning result, model superiority or operational validation is claimed.

G4 currently has CLI/Python APIs and review Markdown; it is not yet wired into the original CAPA browser UI. Next steps are owner review of the draft, independent annotation/adjudication and a versioned reference release before a pharmaceutical study. Manual UI integration and additional source families can be developed locally as separate increments.
