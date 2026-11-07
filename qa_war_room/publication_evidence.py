"""G6 evaluator-side evidence checks and manuscript fact rendering. Offline only."""

from collections import Counter
import json
from pathlib import Path
import re
import tempfile

from .native_data import file_hash
from .study_analysis import analyze_run
from .study_runner import load_run

PACK = "data/derived/manufacturing-gmp-v1-final"
LOCK = "runs/g5-engineering-lock-verified-v2"
RUN = "runs/g5-engineering-run-verified-v2"
ANALYSIS = "reports/g5-engineering-analysis-verified-v2"
CAP_LOCK = "runs/g5-cap-lock-verified-v2"
CAP_RUN = "runs/g5-cap-run-verified-v2"
CAP_ANALYSIS = "reports/g5-cap-analysis-verified-v2"
REFUSAL = "reports/g5-confirmatory-refusal-verified-v2/REFUSAL.json"
CAP_PLAN = "runs/g5-cap-plan-verified-v2.json"
ANALYSIS_FILES = ("ANALYSIS.json", "ENGINEERING_METRICS.json", "ENGINEERING_METRICS.csv",
                  "SCIENTIFIC_TABLE_TEMPLATE.csv", "REPORT.md", "evaluator/outcomes.jsonl")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot(root):
    """Regenerate descriptive analysis from raw runs, not trusted summary numbers.

    This function is evaluator privileged. It is never an actor/model interface.
    No policy, provider, independent-review intake or network call is invoked.
    """
    root = Path(root)
    provenance, results = {}, []
    for lock, run, analysis in ((LOCK, RUN, ANALYSIS), (CAP_LOCK, CAP_RUN, CAP_ANALYSIS)):
        config, store, events, engines, counts, failed, _ = load_run(root / PACK, root / lock, root / run)
        if any(file_hash(root / "qa_war_room" / name) != expected for name, expected in config["implementation_sha256"].items()):
            raise ValueError("Export source differs from the locked implementation")
        manifest = read_json(root / analysis / "ANALYSIS.json")
        if (manifest["scientific_performance_claim"] is not False or manifest["independent_review_completed"] is not False or
                manifest["lock_sha256"] != file_hash(root / lock / "LOCK.json") or
                manifest["implementation_sha256"] != config["implementation_sha256"] or
                manifest["last_event_sha256"] != (events[-1]["sha256"] if events else None) or
                manifest["evaluator_files"] != store.manifest["evaluator_files"]):
            raise ValueError("Analysis provenance or scientific state mismatch")
        for relative, expected in manifest["outputs"].items():
            # G5 on Windows records a backslash for nested output paths.
            relative = relative.replace("\\", "/")
            if relative not in ANALYSIS_FILES or file_hash(root / analysis / relative) != expected:
                raise ValueError("Analysis output checksum mismatch")
        if set(name.replace("\\", "/") for name in manifest["outputs"]) != set(ANALYSIS_FILES) - {"ANALYSIS.json"}:
            raise ValueError("Incomplete analysis manifest")
        for name, expected in manifest["source_run_files"].items():
            if name not in {"manifest.json", "events.jsonl"} or file_hash(root / run / name) != expected:
                raise ValueError("Analysis raw-run checksum mismatch")
        with tempfile.TemporaryDirectory() as temporary:
            regenerated = Path(temporary) / "analysis"
            analyze_run(root / PACK, root / lock, root / run, regenerated)
            for name in ("ENGINEERING_METRICS.json", "ENGINEERING_METRICS.csv", "SCIENTIFIC_TABLE_TEMPLATE.csv", "evaluator/outcomes.jsonl"):
                if (regenerated / name).read_bytes() != (root / analysis / name).read_bytes():
                    raise ValueError("Saved analysis differs from replayed raw evidence")
        metrics = read_json(root / analysis / "ENGINEERING_METRICS.json")
        if (metrics["status"] != "ENGINEERING_ONLY" or metrics["adjudication_completed"] is not False or
                any(c["confidence_intervals"] is not None or c["scientific_success"] != "NOT_EVALUATED" for c in metrics["paired_descriptive_comparisons"])):
            raise ValueError("Unreviewed data cannot support scientific results")
        terminal = sum(key in failed or engine.observation()["status"] == "completed" for key, engine in engines.items())
        summary = read_json(root / run / "SUMMARY.json")
        expected_summary = {"jobs": len(config["jobs"]), "terminal": terminal, "pending": len(engines) - terminal,
            "policy_actions": sum(counts.values()), "transitions": len(events), "runtime_failures": dict(Counter(failed.values())),
            "scientific_performance_claim": False, "llm_calls": 0, "cost_usd": "0"}
        if any(summary.get(name) != value for name, value in expected_summary.items()):
            raise ValueError("Run summary differs from raw journal accounting")
        results.append({"jobs": len(config["jobs"]), "cases": len(config["cohort"]),
            "families": len({c["family_id"] for c in config["cohort"]}), "transitions": len(events),
            "actions": sum(counts.values()), "terminal": terminal, "pending": len(engines) - terminal,
            "statuses": metrics["feasibility"]["statuses"], "tables": len(metrics["tables"]),
            "pack_cases": len(store.case_ids()), "pack_families": len(store.splits["groups"]),
            "runtime_failures": dict(Counter(failed.values()))})
        for relative in [lock + "/LOCK.json", *[run + "/" + name for name in ("manifest.json", "events.jsonl", "SUMMARY.json")],
                         *[analysis + "/" + name for name in ANALYSIS_FILES]]:
            provenance[relative] = file_hash(root / relative)
    refusal = read_json(root / REFUSAL)
    if (refusal["status"] != "REFUSED" or refusal["not_a_study_lock"] is not True or
            refusal["scientific_analysis_authorized"] is not False or (root / Path(REFUSAL).parent / "LOCK.json").exists()):
        raise ValueError("Expected a refused confirmatory request, not a scientific lock")
    for relative in (PACK + "/PACK.json", CAP_PLAN, REFUSAL):
        provenance[relative] = file_hash(root / relative)
    source_manifest = read_json(root / PACK / "PACK.json")
    for name, entry in {**source_manifest["input_files"], **source_manifest["evaluator_files"], **source_manifest["authoring_files"]}.items():
        if file_hash(root / PACK / name) != entry["sha256"]:
            raise ValueError("Pack/lineage checksum mismatch")
        provenance[PACK + "/" + name] = entry["sha256"]
    facts = {"pack_cases": results[0]["pack_cases"], "pack_families": results[0]["pack_families"],
        "dev_cases": results[0]["cases"], "dev_families": results[0]["families"], "dev_jobs": results[0]["jobs"],
        "dev_transitions": results[0]["transitions"], "dev_terminal": results[0]["terminal"],
        "dev_pending": results[0]["pending"], "dev_submissions": results[0]["statuses"].get("ok", 0),
        "dev_abstentions": results[0]["statuses"].get("abstain", 0), "dev_tables": results[0]["tables"],
        "cap_actions": results[1]["actions"], "cap_pending": results[1]["pending"],
        "independent_review": "NOT_PERFORMED", "adjudication": "NOT_PERFORMED",
        "scientific_results": "NOT_RUN", "reference_lock": "NOT_LOCKED", "cost_usd": "0"}
    return {"schema": "qawr-g6-evidence-v1", "scope": "ENGINEERING_ONLY", "facts": facts,
        "raw_run_checks": results, "provenance_sha256": provenance,
        "scientific_performance_claim": False, "submission_ready": False, "publication_authorized": False}


def render(text, evidence):
    def substitute(match):
        key = match.group(1)
        if key not in evidence["facts"]:
            raise ValueError("Unknown manuscript fact: " + key)
        return str(evidence["facts"][key])
    rendered = re.sub(r"\{\{([a-z_]+)\}\}", substitute, text)
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("Unresolved manuscript fact token")
    return rendered
