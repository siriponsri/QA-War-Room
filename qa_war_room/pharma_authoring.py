"""Original synthetic Manufacturing GMP inputs. No reference labels are authored here."""

from copy import deepcopy
import json
from pathlib import Path

from .native_data import digest, file_hash
from .sequential_data import write_jsonl

PACK_VERSION = "qawr-manufacturing-gmp-v1"
RULE_VERSION = "synthetic-site-closure-rules-v1"
FAMILIES = (
    ("packaging-reconciliation", "Nonsterile tablet packaging", "PK-04", "Tablet A", "D5", "unreconciled_units", "eq", 0, 0, 1,
     "Every predefined follow-up batch must have zero unreconciled units under this fictional protocol."),
    ("blending-parameters", "Nonsterile tablet blending", "BL-03", "Tablet B", "D5", "out_of_range_checks", "eq", 0, 0, 1,
     "The predefined follow-up checks must show zero out-of-range readings under this fictional protocol."),
    ("setup-change-control", "Nonsterile capsule equipment setup", "CP-02", "Capsule C", "D5", "unapproved_configuration_runs", "eq", 0, 0, 1,
     "No follow-up run may use a configuration outside the documented approved change under this fictional protocol."),
    ("recurrence-after-training", "Nonsterile tablet dispensing", "DS-05", "Tablet D", "D5", "same_mechanism_recurrences", "eq", 0, 0, 1,
     "No related recurrence is permitted in the declared exposed follow-up cohort under this fictional protocol."),
    ("investigation-cohort", "Nonsterile capsule batch investigation", "IN-06", "Capsule E", "D2", "reviewed_batches", "includes", "cohort", "cohort", "incomplete_cohort",
     "The investigation must explicitly review every batch in the declared affected cohort under this fictional protocol."),
    ("effectiveness-window", "Nonsterile tablet compression monitoring", "TC-07", "Tablet F", "D5", "eligible_operating_days", "ge", 30, 30, 14,
     "At least thirty eligible operating days must be observed within the monitoring period under this fictional protocol; calendar days alone do not satisfy this rule."),
)


def _document(record_id, kind, scope, facts, recorded_at="2026-07-31"):
    return {"id": record_id, "document_type": kind, "owner": "Synthetic site Quality" if record_id != "D3" else "Synthetic site Manufacturing",
            "revision": 1, "recorded_at": recorded_at, "effective_from": "2026-06-01",
            "approval_status": "approved", "scope": deepcopy(scope), "facts": deepcopy(facts),
            "content": "FICTIONAL SITE RECORD\n" + json.dumps(facts, ensure_ascii=False, indent=2, sort_keys=True)}


def _inputs_for_family(number, definition):
    name, process, line, product, measure_record, measure, op, expected, baseline, failed, wording = definition
    family_id = f"MF{number:02d}"
    cohort = [f"Q{number}01", f"Q{number}02", f"Q{number}03"]
    affected = [f"A{number}01", f"A{number}02", f"A{number}03"]
    expected = affected if expected == "cohort" else expected
    baseline = affected if baseline == "cohort" else baseline
    failed = affected[:-1] if failed == "incomplete_cohort" else failed
    scope = {"product": product, "line": line, "batches": cohort, "affected_batches": affected}
    criteria = [
        {"id": "C1", "record_id": "D2", "pointer": "/facts/investigation_complete", "op": "eq", "expected": True,
         "wording": "The affected-cohort investigation is documented as complete."},
        {"id": "C2", "record_id": "D3", "pointer": "/facts/implementation_status", "op": "eq", "expected": "completed",
         "wording": "All actions in the approved synthetic CAPA plan are implemented, not merely planned."},
        {"id": "C3", "record_id": "D4", "pointer": "/facts/training_complete", "op": "eq", "expected": True,
         "wording": "The record affirms completion of the declared procedure training roster."},
        {"id": "C4", "record_id": "D4", "pointer": "/facts/procedure_revision", "op": "eq", "expected": 2,
         "wording": "The completed training covers governing procedure revision 2."},
        {"id": "C5", "record_id": "D5", "pointer": "/facts/verified_batches", "op": "includes", "expected": cohort,
         "wording": "The effectiveness data explicitly cover the entire predefined follow-up cohort."},
        {"id": "C6", "record_id": "D6", "pointer": "/facts/open_related_deviations", "op": "eq", "expected": 0,
         "wording": "The applicable related-deviation register records zero open related deviations."},
        {"id": "C7", "record_id": "D6", "pointer": "/facts/current_status", "op": "eq", "expected": "closed",
         "wording": "The current applicable status register records closure."},
        {"id": "M1", "record_id": measure_record, "pointer": "/facts/" + measure, "op": op,
         "expected": deepcopy(expected), "wording": wording},
    ]
    facts = {
        "D1": {"sop_id": f"SYN-QA-{number:02d}", "procedure_revision": 2, "rule_version": RULE_VERSION,
               "rule_scope": "Fictional site-specific claim, not a universal regulatory rule",
               "admissibility": "Use only approved, recorded and effective evidence on/before cutoff for this product/line/cohort.",
               "criteria": criteria},
        "D2": {"deviation_id": f"SYN-DEV-{number:02d}", "trigger": "A manufacturing deviation prompted a scoped investigation.",
               "impact_boundary": "Only the declared fictional product, line and affected cohort.",
               "trigger_date": "2026-06-05", "affected_batches": affected,
               "investigation_complete": True, "reviewed_batches": affected},
        "D3": {"capa_id": f"SYN-CAPA-{number:02d}", "approved_plan": "Implement the approved setup/procedure controls, train the roster and verify the predefined follow-up cohort.",
               "responsible_role": "Synthetic site Manufacturing", "due_date": "2026-06-15",
               "implementation_status": "completed", "completed_at": "2026-06-12",
               "approved_change_id": f"SYN-CC-{number:02d}"},
        "D4": {"training_complete": True, "procedure_revision": 2, "trained_at": "2026-06-14",
               "roster": "All four fictional operators in the declared roster"},
        "D5": {"verified_batches": cohort, "monitoring_start": "2026-07-01", "monitoring_end": "2026-07-30",
               "exposed_followup_batches": 3, "checks_performed": 20},
        "D6": {"open_related_deviations": 0, "current_status": "closed", "status_at": "2026-07-31"},
        "D7": {"context_note": "Room log for another process; not a closure criterion", "room_temperature_c": 22},
    }
    facts[measure_record][measure] = deepcopy(baseline)
    triggers = ("A packaging count discrepancy prompted a reconciliation investigation.",
                "A blending parameter excursion prompted recipe and set-point verification.",
                "A capsule equipment setup differed from the documented approved configuration.",
                "A dispensing identification error prompted procedure revision and retraining.",
                "A deviation required an explicit impact review across the affected original batches.",
                "A compression-process excursion prompted an operating-day effectiveness period.")
    plans = ("Implement double-count reconciliation and documented discrepancy review under the approved synthetic change.",
             "Implement approved recipe/set-point verification and retain follow-up parameter checks.",
             "Implement the approved equipment configuration checklist and document configuration checks.",
             "Implement material-identification procedure revision 2 and train the four declared operators.",
             "Complete the affected-batch impact review and retain the predefined follow-up cohort verification.",
             "Implement the approved parameter-check procedure and collect thirty eligible operating days of follow-up.")
    facts["D2"]["trigger"] = triggers[number - 1]
    facts["D2"]["root_cause_basis"] = "Author-provided scenario premise for the declared procedural change; causal adequacy requires independent QA review."
    facts["D2"]["impact_boundary"] = "The declared original affected batches and follow-up cohort only; batch disposition/release is outside this claim."
    facts["D3"]["approved_plan"] = plans[number - 1]
    kinds = {"D1": "synthetic_site_sop", "D2": "deviation_investigation", "D3": "capa_plan_and_implementation",
             "D4": "training_roster", "D5": "effectiveness_data", "D6": "current_status_review", "D7": "context_log"}
    titles = {"D1": "Approved synthetic site assessment procedure", "D2": "Deviation investigation record",
              "D3": "CAPA plan and implementation record", "D4": "Procedure training record",
              "D5": "Follow-up verification record", "D6": "Related deviation and status register", "D7": "Context record"}
    order = sorted(facts, key=lambda key: digest([family_id, key]))
    split = ("train", "train", "dev", "dev", "test", "test")[number - 1]
    variants = ("anchor", "measure", "unavailable", "scope", "future", "revision", "context", "unclear")
    cases, evidence, lineage = [], [], []
    anchor_id = "M4_" + digest([PACK_VERSION, family_id, "anchor"])[:12]
    for variant in variants:
        case_id = "M4_" + digest([PACK_VERSION, family_id, variant])[:12]
        dates = {"D1": "2026-05-25", "D3": "2026-06-13", "D4": "2026-06-15"}
        docs = {key: _document(key, kinds[key], scope, value, dates.get(key, "2026-07-31"))
                for key, value in facts.items()}
        docs["D7"]["scope"] = {"product": f"Context product {number}", "line": "CTX-" + line,
                                  "batches": [], "affected_batches": []}
        changes = []
        unavailable = None
        if variant == "measure":
            docs[measure_record]["facts"][measure] = deepcopy(failed)
            changes = [f"/{measure_record}/facts/{measure}"]
        elif variant == "unavailable":
            unavailable = "D5"
            changes = ["/D5/availability_and_linked_payload_removal"]
        elif variant == "scope":
            docs["D5"]["scope"]["line"] = "OTHER-LINE"
            changes = ["/D5/scope/line"]
        elif variant == "future":
            docs["D5"]["recorded_at"] = "2026-08-05"
            changes = ["/D5/recorded_at"]
        elif variant == "revision":
            docs["D4"]["facts"]["procedure_revision"] = 1
            changes = ["/D4/facts/procedure_revision"]
        elif variant == "context":
            docs["D7"]["facts"]["room_temperature_c"] = 23
            changes = ["/D7/facts/room_temperature_c"]
        elif variant == "unclear":
            docs["D1"]["facts"]["criteria"][-1]["expected"] = None
            docs["D1"]["facts"]["criteria"][-1]["wording"] = "Follow-up should be appropriate; this approved synthetic procedure does not define an acceptance threshold."
            changes = ["/D1/facts/criteria/M1/expected", "/D1/facts/criteria/M1/wording"]
        for document in docs.values():
            document["content"] = "FICTIONAL SITE RECORD\n" + json.dumps(document["facts"], ensure_ascii=False, indent=2, sort_keys=True)
        records = [{"id": key, "cost": 2 if key == "D5" else 1, "title": titles[key],
                    "document_type": kinds[key], "available": key != unavailable,
                    "document": docs[key] if key != unavailable else None,
                    "unavailable_reason": "The authored source collection has no verification record to return." if key == unavailable else None}
                   for key in order]
        cases.append({"id": case_id, "family_id": family_id, "template_id": name + "-v1", "split": split,
                      "title": "Manufacturing CAPA evidence packet", "dataset_version": PACK_VERSION,
                      "process": process, "scope": deepcopy(scope), "as_of": "2026-08-01",
                      "sop_id": f"SYN-QA-{number:02d}", "budget": 8,
                      "claim": f"As of 2026-08-01, SYN-CAPA-{number:02d} satisfies every closure and effectiveness criterion in SYN-QA-{number:02d} revision 2 for {product}, line {line}, batches {', '.join(cohort)}.",
                      "review_status": "author_draft_unreviewed", "jurisdiction": "synthetic_site_only",
                      "author_constraints": "Original fictional nonsterile oral-solid records; the explicit site SOP defines this exercise. No regulatory equivalence, real company data or clinical use."})
        evidence.append({"id": case_id, "records": records})
        lineage.append({"id": case_id, "family_id": family_id, "template_id": name + "-v1", "split": split,
                        "anchor_id": anchor_id, "construction_change": variant, "changed_fact_paths": changes,
                        "linked_rendering_changes": "content is regenerated from facts; unavailable payload is removed",
                        "reference_label_assigned_here": False})
    return cases, evidence, lineage


def prepare_inputs(output: Path) -> dict:
    output = Path(output)
    if output.exists():
        raise ValueError("Pharma output exists; preserve it and select a new directory")
    cases, records, lineage = [], [], []
    for number, definition in enumerate(FAMILIES, 1):
        family_cases, family_records, family_lineage = _inputs_for_family(number, definition)
        cases.extend(family_cases)
        records.extend(family_records)
        lineage.extend(family_lineage)
    cases.sort(key=lambda row: row["id"])
    records.sort(key=lambda row: row["id"])
    lineage.sort(key=lambda row: row["id"])
    output.mkdir(parents=True)
    write_jsonl(output / "public/cases.jsonl", cases)
    write_jsonl(output / "private/records.jsonl", records)
    write_jsonl(output / "authoring/lineage.jsonl", lineage)
    groups = [{"family_id": f"MF{i:02d}", "template_id": definition[0] + "-v1",
               "split": ("train", "train", "dev", "dev", "test", "test")[i - 1],
               "case_ids": [row["id"] for row in cases if row["family_id"] == f"MF{i:02d}"]}
              for i, definition in enumerate(FAMILIES, 1)]
    (output / "public/splits.json").write_text(json.dumps({"status": "provisional_author_defined_not_confirmatory",
        "unit": "construction_template_and_counterfactual_family", "groups": groups,
        "limits": "Common schema scaffolding and solo construction; no independent-site or reviewed-domain generalization established."}, indent=2) + "\n", encoding="utf-8")
    inputs = ("public/cases.jsonl", "private/records.jsonl", "public/splits.json")
    return {"pack_version": PACK_VERSION, "rule_version": RULE_VERSION, "stage": "G4_author_draft",
            "author": "QA War Room project authoring pipeline; not an independent domain reviewer",
            "rights": "Original synthetic project records; project license remains undecided",
            "real_company_records": False, "independent_review_completed": False,
            "input_builder_sha256": file_hash(Path(__file__)),
            "input_files": {name: {"sha256": file_hash(output / name), "bytes": (output / name).stat().st_size} for name in inputs},
            "authoring_files": {"authoring/lineage.jsonl": {"sha256": file_hash(output / "authoring/lineage.jsonl"),
                                                            "bytes": (output / "authoring/lineage.jsonl").stat().st_size}},
            "counts": {"cases": len(cases), "construction_families": len(groups), "synthetic_site_sops": len(groups)}}
