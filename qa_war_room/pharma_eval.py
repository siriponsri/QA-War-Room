"""Author-defined structured references and terminal-only G4 evaluation."""

from collections import Counter
import json
from pathlib import Path

from .native_data import file_hash, read_jsonl
from .pharma_rules import assess_visible
from .sequential_data import write_jsonl


def build_references(output, manifest):
    cases = read_jsonl(output / "public/cases.jsonl")
    records = {row["id"]: row["records"] for row in read_jsonl(output / "private/records.jsonl")}
    gold = []
    for case in cases:
        source = records[case["id"]]
        assessment = assess_visible(case, [row["document"] for row in source if row["available"]],
                                    [{"record_id": row["id"], "status": "delivered" if row["available"] else "source_unavailable"} for row in source])
        verdict = assessment["verdict"]
        failed = [row for row in assessment["criteria"] if row["status"] == "fail"]
        available_ids = {row["id"] for row in source if row["available"]}
        witnesses = (None if verdict == "ambiguous" else [["D1", row["record_id"]] for row in failed] if failed
                     else [[key for key in ("D1", "D2", "D3", "D4", "D5", "D6") if key in available_ids]])
        gold.append({"id": case["id"], "family_id": case["family_id"], "template_id": case["template_id"],
                     "reference_origin": "author_defined_structured_synthetic_SOP_not_independent_review",
                     "review_status": "unreviewed", "candidate_verdict": None if verdict == "ambiguous" else verdict,
                     "author_allowed_labels": ["supported", "insufficient"] if verdict == "ambiguous" else [verdict],
                     "ambiguity_preflagged": verdict == "ambiguous", "primary_eligible_draft": verdict != "ambiguous",
                     "assessment": assessment, "declared_record_witness_sets": witnesses,
                     "minimal_sufficiency_independently_reviewed": False,
                     "required_unavailability_checks": [row["id"] for row in source if not row["available"]],
                     "scope_time_policy": "Only approved recorded/effective records at/before cutoff for this product/line/cohort."})
    write_jsonl(output / "evaluator/gold.jsonl", gold)
    lineage = read_jsonl(output / "authoring/lineage.jsonl")
    index = {row["id"]: row for row in gold}
    pairs = [{"id": row["id"], "family_id": row["family_id"], "anchor_id": row["anchor_id"],
              "case_id": row["id"], "construction_change": row["construction_change"],
              "changed_fact_paths": row["changed_fact_paths"], "linked_rendering_changes": row["linked_rendering_changes"],
              "anchor_candidate": index[row["anchor_id"]]["candidate_verdict"],
              "variant_candidate": index[row["id"]]["candidate_verdict"],
              "pair_type": ("unresolved_ambiguity" if index[row["id"]]["candidate_verdict"] is None else
                            "label_preserving" if index[row["anchor_id"]]["candidate_verdict"] == index[row["id"]]["candidate_verdict"] else "label_changing"),
              "label_changed_under_author_rules": (None if index[row["id"]]["candidate_verdict"] is None else
                    index[row["anchor_id"]]["candidate_verdict"] != index[row["id"]]["candidate_verdict"]),
              "independently_reviewed": False} for row in lineage if row["id"] != row["anchor_id"]]
    write_jsonl(output / "evaluator/pairs.jsonl", pairs)
    manifest = {**manifest, "reference_builder_sha256": file_hash(Path(__file__)),
                "evaluator_files": {name: {"sha256": file_hash(output / name), "bytes": (output / name).stat().st_size}
                                    for name in ("evaluator/gold.jsonl", "evaluator/pairs.jsonl")}}
    (output / "PACK.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest, "candidate_counts": dict(Counter(row["candidate_verdict"] or "ambiguous" for row in gold))}


def load_gold(store):
    if set(store.manifest["evaluator_files"]) != {"evaluator/gold.jsonl", "evaluator/pairs.jsonl"}:
        raise ValueError("Unsupported pharma evaluator files")
    for name, entry in store.manifest["evaluator_files"].items():
        path = store.directory / name
        if file_hash(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise ValueError("Pharma evaluator checksum mismatch")
    return {row["id"]: row for row in read_jsonl(store.directory / "evaluator/gold.jsonl")}


def evaluate_terminal(store, observation):
    if observation["status"] != "completed":
        raise ValueError("Submit or abstain before terminal evaluation")
    reference = load_gold(store)[observation["case"]["id"]]
    observed = assess_visible(observation["case"], observation["evidence"], observation["responses"])
    decision = observation["decision"]
    verdict = decision.get("verdict") if decision["type"] == "submit" else None
    submitted = verdict is not None
    actual_citations = {(row["record_id"], row["pointer"]) for row in decision.get("citations", [])}
    relevant = [row for row in observed["criteria"] if row["status"] == "fail"] if observed["verdict"] == "contradicted" else observed["criteria"]
    required_locations = {("D1", "/facts/criteria")}
    for row in relevant:
        if row["status"] in {"pass", "fail"}:
            required_locations.add((row["record_id"], row["pointer"]))
        elif row["reason"] in {"scope_mismatch", "after_assessment_cutoff"}:
            required_locations.add((row["record_id"], "/scope" if row["reason"] == "scope_mismatch" else "/recorded_at"))
    facts_cited = bool(relevant) and required_locations <= actual_citations
    availability = set(reference["required_unavailability_checks"]) <= {
        row["record_id"] for row in observation["responses"] if row["status"] == "source_unavailable"}
    return {"case_id": observation["case"]["id"], "reference_status": "author_draft_unreviewed",
            "candidate_verdict": reference["candidate_verdict"], "primary_eligible_draft": reference["primary_eligible_draft"],
            "label_matches_candidate": (verdict == reference["candidate_verdict"]) if reference["candidate_verdict"] and submitted else None,
            "observed_assessment": observed, "observed_decision_matches_declared_rules": submitted and verdict == observed["verdict"],
            "declared_fact_locations_cited": facts_cited, "required_unavailability_checks_made": availability,
            "ambiguity_preflagged": reference["ambiguity_preflagged"],
            "limitations": "Structured fictional SOP checks only; no semantic rationale grading or independent pharmaceutical validation."}
