"""Local blinded packets and immutable review intake. Never load author gold."""

from collections import defaultdict
import json
from pathlib import Path
import re
import shutil

from .native_data import digest, file_hash, read_jsonl
from .native_runner import atomic_json, now
from .pharma_rules import pointer
from .sequential_data import write_jsonl


def export_review(store, output, *, seed=41, case_ids=None):
    if type(seed) is not int:
        raise ValueError("Review randomization seed must be an integer")
    output = Path(output)
    if output.exists():
        raise ValueError("Review export exists; preserve the original and choose a new directory")
    selected = list(store.case_ids()) if case_ids is None else list(case_ids)
    if not selected or len(set(selected)) != len(selected) or not set(selected) <= set(store.case_ids()):
        raise ValueError("Select unique known source cases")
    selected.sort(key=lambda case_id: digest([seed, case_id]))
    reviewer, owner = output / "reviewer", output / "owner"
    reviewer.mkdir(parents=True)
    owner.mkdir()
    packets, templates, mapping = [], [], []
    for ordinal, case_id in enumerate(selected, 1):
        alias = f"RC{ordinal:04d}"
        card = store.card(case_id)
        public = {key: card[key] for key in ("title", "claim", "process", "scope", "as_of", "sop_id")}
        public["id"] = alias
        records = []
        for item in store.catalog(case_id):
            source = store.record(case_id, item["id"])
            records.append({"id": item["id"], "title": item["title"],
                            "status": "available" if source["available"] else "source_unavailable",
                            "document": source["document"], "availability_note": source["unavailable_reason"]})
        packet = {"id": alias, "case": public, "records": records}
        case_version = digest(packet)
        packet["case_version"] = case_version
        packets.append(packet)
        sop = next(row["document"] for row in records if row["id"] == "D1")
        templates.append({"id": alias, "case_version": case_version, "reviewer_code": "", "plausibility": None,
                          "verdict": None, "citations": [], "rationale": "", "ambiguity_notes": "",
                          "alternative_support_sets": [], "primary_disposition": None, "full_packet_reviewed": None,
                          "criteria": [{"criterion_id": row["id"], "status": None, "notes": ""} for row in sop["facts"]["criteria"]]})
        mapping.append({"id": alias, "source_case_id": case_id, "case_version": case_version,
                        "family_id": card["family_id"], "template_id": card["template_id"]})
        lines = [f"# Blinded case {alias}", "", "Original fictional site records for independent annotation. No system prediction is supplied.",
                 "", f"Case version: {case_version}", "", "## Claim", "", card["claim"], "",
                 "## Scope and cutoff", "", json.dumps({"scope": card["scope"], "as_of": card["as_of"]}, indent=2), ""]
        for record in records:
            lines.extend([f"## {record['id']}: {record['title']}", "", f"Availability: {record['status']}", ""])
            if record["document"]:
                lines.extend(["```json", json.dumps(record["document"], ensure_ascii=False, indent=2), "```", ""])
            else:
                lines.extend([record["availability_note"], ""])
        (reviewer / f"{alias}.md").write_text("\n".join(lines), encoding="utf-8")
    write_jsonl(reviewer / "cases.jsonl", packets)
    write_jsonl(reviewer / "ratings-template-A.jsonl", templates)
    write_jsonl(reviewer / "ratings-template-B.jsonl", templates)
    atomic_json(reviewer / "reviewers-template.json", {"reviewers": [
        {"reviewer_code": "", "manufacturing_qa_experience": "", "independent_of_author": None,
         "conflicts_disclosed": None} for _ in range(2)]})
    (reviewer / "INDEX.md").write_text("# Blinded case index\n\n" + "\n".join(
        f"- [{row['id']}]({row['id']}.md)" for row in packets) + "\n", encoding="utf-8")
    atomic_json(reviewer / "REVIEW.json", {"schema": "blinded-manufacturing-review-v1", "created_utc": now(),
        "cases": len(packets), "expected_aliases": [row["id"] for row in packets], "minimum_distinct_reviewers": 2,
        "case_file_sha256": file_hash(reviewer / "cases.jsonl"), "input_only": True,
        "case_artifacts_sha256": {name: file_hash(reviewer / name) for name in
                                  ["cases.jsonl", "INDEX.md", *[row["id"] + ".md" for row in packets]]},
        "blinding_limit": "Related fictional mechanisms may be recognizable; source IDs, pair orientation and authored decisions are withheld."})
    write_jsonl(owner / "link-map.jsonl", mapping)
    atomic_json(owner / "EXPORT.json", {"source_pack_sha256": file_hash(store.directory / "PACK.json"),
                                       "seed": seed, "mapping_sha256": file_hash(owner / "link-map.jsonl")})
    (reviewer / "README.md").write_text(
        "# Independent Manufacturing QA review\n\n[Open the case index](INDEX.md).\n\n"
        "Review each case independently using its complete available source packet and the explicit fictional site procedure. "
        "Cases are isolated alternative scenarios; repeated identifiers do not denote a shared real-world procedure across cases. "
        "Do not infer a universal GMP threshold from an authored example. A record marked unavailable is absent from this source packet.\n\n"
        "Complete a copy of one ratings template and the reviewer roster. Use supported, contradicted, insufficient or ambiguous; "
        "cite exact document JSON pointers. Record criterion judgments, plausibility concerns, alternatives and unresolved questions. "
        "Do not discuss judgments with the other reviewer before initial files are sealed. Do not use an LLM to supply the reference label.\n\n"
        "The two template files are blank forms, not completed reviews or evidence that reviewers exist. "
        "Reviewer identity, experience, independence and conflicts require human verification. "
        "Submit through the owner-agreed local process; this software sends nothing.\n", encoding="utf-8")
    (output / "README.md").write_text("# Local review export\n\nProvide only reviewer/ to the reviewers. Keep owner/ local. "
        "This export does not recruit/contact anyone or establish that independent review occurred. "
        "Initial ratings must be retained unchanged before adjudication or pair-consistency review.\n", encoding="utf-8")
    return {"status": "blank_blinded_packet_prepared", "cases": len(packets), "review_completed": False,
            "reviewer_directory": str(reviewer), "owner_directory": str(owner)}


def _citation_check(citation, documents):
    if (not isinstance(citation, dict) or set(citation) != {"record_id", "pointer"} or
            not isinstance(citation["record_id"], str) or not isinstance(citation["pointer"], str) or citation["record_id"] not in documents):
        return False
    try:
        pointer(documents[citation["record_id"]], citation["pointer"])
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return True


def check_reviews(packet, rating_paths, roster_path, output):
    """Structural completeness only. Never promotes/replaces reference decisions."""
    packet, output = Path(packet), Path(output)
    if output.exists():
        raise ValueError("Review intake output exists; preserve prior ratings and choose a new directory")
    manifest = json.loads((packet / "REVIEW.json").read_text(encoding="utf-8"))
    aliases = manifest["expected_aliases"]
    if not isinstance(aliases, list) or len(set(aliases)) != len(aliases) or any(
            not isinstance(alias, str) or not re.fullmatch(r"RC[0-9]{4}", alias) for alias in aliases):
        raise ValueError("Invalid blinded case aliases")
    allowed = {"cases.jsonl", "INDEX.md", *[alias + ".md" for alias in aliases]}
    if set(manifest["case_artifacts_sha256"]) != allowed or any(
            file_hash(packet / name) != fingerprint for name, fingerprint in manifest["case_artifacts_sha256"].items()):
        raise ValueError("Blinded case artifact changed")
    if file_hash(packet / "cases.jsonl") != manifest["case_file_sha256"]:
        raise ValueError("Blinded review case file changed")
    cases = {row["id"]: row for row in read_jsonl(packet / "cases.jsonl")}
    if set(cases) != set(manifest["expected_aliases"]) or any(
            digest({k: v for k, v in row.items() if k != "case_version"}) != row["case_version"] for row in cases.values()):
        raise ValueError("Blinded case version/cohort mismatch")
    roster = json.loads(Path(roster_path).read_text(encoding="utf-8"))
    issues, valid_reviewers = [], set()
    if set(roster) != {"reviewers"} or not isinstance(roster["reviewers"], list):
        raise ValueError("Reviewer roster schema mismatch")
    for reviewer in roster["reviewers"]:
        if (not isinstance(reviewer, dict) or set(reviewer) != {"reviewer_code", "manufacturing_qa_experience", "independent_of_author", "conflicts_disclosed"}):
            issues.append("Invalid reviewer roster entry")
            continue
        code = reviewer["reviewer_code"]
        if (not isinstance(code, str) or not code.strip() or code in valid_reviewers or
                not isinstance(reviewer["manufacturing_qa_experience"], str) or not reviewer["manufacturing_qa_experience"].strip() or
                reviewer["independent_of_author"] is not True or reviewer["conflicts_disclosed"] is not True):
            issues.append("Incomplete/duplicate reviewer identity, experience or independence attestation")
        else:
            valid_reviewers.add(code)
    if len(valid_reviewers) < manifest["minimum_distinct_reviewers"]:
        issues.append("Fewer than two distinct, attested reviewer records")
    ratings, seen = [], set()
    for path in rating_paths:
        for rating in read_jsonl(Path(path)):
            ratings.append(rating)
            alias = rating["id"]
            if alias not in cases:
                issues.append("Unknown blinded case ID")
                continue
            expected_fields = {"id", "case_version", "reviewer_code", "plausibility", "verdict", "citations", "rationale",
                               "ambiguity_notes", "alternative_support_sets", "primary_disposition", "full_packet_reviewed", "criteria"}
            if set(rating) != expected_fields:
                issues.append(alias + ": rating schema mismatch")
                continue
            if not isinstance(rating["reviewer_code"], str):
                issues.append(alias + ": reviewer code must be text")
                continue
            key = (alias, rating["reviewer_code"])
            if key in seen or rating["reviewer_code"] not in valid_reviewers:
                issues.append(alias + ": duplicate or unattested reviewer")
            seen.add(key)
            case = cases[alias]
            docs = {row["id"]: row["document"] for row in case["records"] if row["document"] is not None}
            if (rating["case_version"] != case["case_version"] or not isinstance(rating["verdict"], str) or rating["verdict"] not in {"supported", "contradicted", "insufficient", "ambiguous"} or
                    not isinstance(rating["plausibility"], str) or rating["plausibility"] not in {"plausible", "concerned", "unassessable"} or
                    not isinstance(rating["primary_disposition"], str) or rating["primary_disposition"] not in {"include", "revise", "exclude_ambiguous"} or
                    rating["full_packet_reviewed"] is not True or not isinstance(rating["rationale"], str) or not rating["rationale"].strip()):
                issues.append(alias + ": incomplete judgment/version/full-packet review")
            if not isinstance(rating["citations"], list) or any(not _citation_check(c, docs) for c in rating["citations"]):
                issues.append(alias + ": citation not in available review packet")
            elif rating["verdict"] in ("supported", "contradicted") and not rating["citations"]:
                issues.append(alias + ": positive/negative judgment needs source citations")
            if not isinstance(rating["ambiguity_notes"], str) or (rating["verdict"] == "ambiguous" and (
                    not rating["ambiguity_notes"].strip() or rating["primary_disposition"] == "include")):
                issues.append(alias + ": ambiguity needs reasons and revision/exclusion from the primary set")
            alternatives = rating["alternative_support_sets"]
            if not isinstance(alternatives, list) or any(not isinstance(group, list) or not group or any(
                    not _citation_check(citation, docs) for citation in group) for group in alternatives):
                issues.append(alias + ": invalid alternative support set")
            criteria = rating["criteria"]
            expected_ids = {row["id"] for row in docs["D1"]["facts"]["criteria"]}
            if (not isinstance(criteria, list) or any(not isinstance(row, dict) or set(row) != {"criterion_id", "status", "notes"} or not isinstance(row["criterion_id"], str) for row in criteria) or
                    len(criteria) != len(expected_ids) or {row["criterion_id"] for row in criteria} != expected_ids or
                    any(not isinstance(row["status"], str) or row["status"] not in {"pass", "fail", "unknown", "ambiguous"} or not isinstance(row["notes"], str) or
                        (row["status"] in {"unknown", "ambiguous"} and not row["notes"].strip()) for row in criteria)):
                issues.append(alias + ": incomplete/invalid per-criterion review")
    for alias in cases:
        if sum((alias, code) in seen for code in valid_reviewers) < manifest["minimum_distinct_reviewers"]:
            issues.append(alias + ": insufficient distinct initial reviews")
    output.mkdir(parents=True)
    archived = []
    for ordinal, path in enumerate([Path(roster_path), *map(Path, rating_paths)], 1):
        extension = path.suffix if path.suffix in {".json", ".jsonl"} else ".jsonl"
        destination = output / f"received-{ordinal:02d}-{file_hash(path)[:12]}{extension}"
        shutil.copyfile(path, destination)
        archived.append({"file": destination.name, "sha256": file_hash(destination), "source_filename": path.name})
    report = {"status": "INCOMPLETE" if issues else "RECORDS_COMPLETE_PENDING_HUMAN_VERIFICATION_AND_ADJUDICATION",
              "issues": sorted(set(issues)), "initial_rating_rows": len(ratings), "cases": len(cases),
              "distinct_attested_reviewer_codes": len(valid_reviewers), "archived_inputs": archived,
              "identity_or_independence_verified_by_software": False, "reference_labels_modified": False,
              "independent_pharmaceutical_validation_established": False, "created_utc": now()}
    atomic_json(output / "CHECK.json", report)
    grouped = defaultdict(list)
    for row in ratings:
        if row.get("id") in cases:
            grouped[row["id"]].append({"reviewer_code": row.get("reviewer_code"), "initial_verdict": row.get("verdict")})
    write_jsonl(output / "adjudication-template.jsonl", [{"id": alias, "initial_reviews": grouped[alias],
        "final_verdict": None, "ambiguity_status": None, "adjudicator_code": "", "rationale": "", "source_revision_needed": None}
        for alias in cases])
    return report
