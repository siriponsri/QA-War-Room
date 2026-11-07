# Independent Manufacturing QA review plan

Version 1.0, 7 November 2026. Status: prospective, local materials prepared; **no independent review has been performed**. No reviewer has been recruited/contacted and no remuneration or data transfer was authorized in this task.

## Scope and purpose

Review the pharmaceutical plausibility, declared SOP logic, applicability, candidate-reference validity, alternative evidence and ambiguity of the original `qawr-manufacturing-gmp-v1` draft. This is a reference-development activity for a constructed environment, not an approval of a real CAPA, batch release, site compliance or operational software.

The draft has six construction families and eight sibling cases per family. Shared software/schema and solo construction limit independence. Source/template/counterfactual siblings stay in one provisional train/dev/test group; none of these names establishes a locked or representative clinical/pharmaceutical test population.

## Reviewer roles and eligibility

Aim for at least two distinct non-author reviewers with relevant manufacturing QA, deviation/CAPA investigation and effectiveness-review experience. Record role, relevant process experience, independence, conflicts and the owner's identity/qualification verification outside the blinded case files. Current persona names and model prompts do not establish expertise. The blank roster is not a reviewer list.

If only one suitable reviewer is available, record that limitation and do not compute inter-rater agreement from their repeated ratings. Do not silently replace independent review with an LLM jury or an author scoring their own work.

## Stage 1: pilot the instrument

Use development-family cases for a small feasibility pilot before final annotation. Record actual review time, unclear instructions, additional source needs and interpretation disagreements. Revise the rubric, source facts or SOPs in a new version and issue a new packet hash when necessary. Preserve earlier files and their reason-for-change log. Do not adjust instructions after examining evaluated-model performance to favor a method.

The package may be exported for a selected case list using the Python export_review(..., case_ids=...) API; the default CLI exports all 48. Keep final evaluation families out of prompt/model tuning. Independent annotation of source references is not model training.

## Stage 2: blinded individual annotation

Provide only the reviewer/ folder plus the identical versioned annotation rubric. Keep owner/ and all authoring/evaluator folders local to the curator. Reviewer packets use randomized RC aliases, complete available records, SOPs, source-unavailability notices and blank rating forms. They omit source case IDs, construction-change tags, paired-case orientation, authored labels, model predictions and score feedback.

Document the actual blinding achieved. Related mechanisms/identifiers can remain recognizable from required evidence; this is not a guarantee that reviewers cannot infer sibling relationships. Do not place matched siblings side by side or supply a “correct answer” explanation in the initial round. Each packet is an isolated alternative world.

Use [the rubric](templates/MFG_ANNOTATION_RUBRIC_V1.md). Require a full-packet label, criterion judgments, plausible/concerned/unassessable context rating, exact evidence locations, alternatives, unresolved questions and include/revise/exclude_ambiguous disposition. Preserve ambiguity rather than forcing agreement. Reviewers should challenge root-cause/causal adequacy and whether the synthetic procedure makes a credible pharmaceutical task, not merely repeat a machine-computed rule outcome.

## Stage 3: seal initial records

Receive one JSONL file per reviewer, with each review case ID unique within that file. Keep roster and case/rubric versions. The intake tool preserves exact received bytes under new hashed filenames, records provenance and refuses to overwrite prior intake. Initial files are never replaced by reconciled ratings.

Blank/partial forms, unknown aliases, wrong case versions, missing criterion judgments, invalid source pointers, duplicate reviewers and insufficient distinct ratings remain incomplete. Case JSON and human-readable case Markdown hashes are checked. The separate rubric hash is retained in owner/REVIEW_PROTOCOL_LOCK.json for this prepared local packet; verify that same guide was supplied to both reviewers before actual annotation.

Structural acceptance means only records are complete enough for human verification/adjudication. The checker does not verify human identity, independence, expertise or the semantics of a rationale. Its output never changes source gold or establishes independent pharmaceutical validation. Hashes are provenance/corruption checks, not signed identity proof or a regulated audit trail.

## Stage 4: independent adjudication and pair consistency

After initial ratings are sealed, compare disagreements without discarding the original judgments. A designated qualified adjudicator or documented reviewer consensus should record final permitted label(s), rationale, exact supporting locations, alternate sets, ambiguity treatment and source revisions. Where the author disagrees, retain that fact; do not force a majority vote to conceal ambiguity.

Then inspect complete families and controlled contrasts: decisive fact changes, scope/time/revision changes, genuinely unavailable evidence, and a non-decisive context change. Confirm that linked rendering changes are necessary consequences rather than hidden additional interventions. Six unresolved-criterion siblings have no unique authored candidate; they are preflagged for revision/exclusion, not forced into an invented gold label.

The intake creates a blank adjudication template. A completed form is not automatically a new reference release. Any revised source, SOP, admissible label set, support set or ambiguity decision requires a new traceable pack/reference version.

## Stage 5: reference and study lock

Before an evaluation claim, record verified reviewer provenance, initial-rating hashes, adjudication, remaining ambiguous cases, case/rule/rubric versions, family partitions and eligibility. Decide the intended jurisdiction/use separately; current site rules do not assert US/EU/Thai/PIC/S equivalence. Resolve the original-content license before distribution/reuse. Plan the number of genuinely independent families and precision from the study question and measured feasibility, not from 48 siblings or scripted consistency.

Report disagreements and exclusions by class and construction family. If agreement is later computed, describe reviewers, units, sampling and dependence; do not invent a current agreement value. Keep a pharmaceutical Stage B protocol/reference lock separate from the native/derived-contract methods work.

Current readiness is deliberately false for independent domain validation, adjudication and reference freeze. Offline authoring/testing and a polished review packet cannot satisfy these external-evidence gates.
