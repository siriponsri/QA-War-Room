"""Engineering smoke benchmark, not publication evidence.

Runs the scripted policies on the same fixtures they were designed with. There
is no held-out test set, no statistical independence across template variants,
no LLM, no human validation and no scientific performance claim.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

from .engine import AUDITOR_ROLES, SessionEngine
from .store import FixtureStore


def run_benchmark(data_dir: Path | str | None = None) -> dict:
    store = FixtureStore(data_dir)
    engine = SessionEngine(store)
    rows = []
    for role in sorted(AUDITOR_ROLES):
        for case in engine.list_cases():
            state = engine.create(case["id"], role)
            for _ in range(len(state["catalog"]) + 2):
                if state["status"] == "completed":
                    break
                state = engine.step(state["session_id"])
            if state["status"] != "completed":
                raise RuntimeError("Policy exceeded its finite action bound.")
            feedback = state["feedback"]
            rows.append({
                "case_id": case["id"], "policy": role,
                "predicted_verdict": state["decision"]["verdict"],
                "reference_verdict": feedback["expected_verdict"],
                "verdict_correct": feedback["verdict_correct"],
                "reference_support_complete": feedback["evidence_support_complete"],
                "decision_and_support_correct": feedback["decision_and_support_correct"],
                "credits_spent": state["budget"]["spent"],
                "requests": sum(1 for event in state["events"] if event["type"] == "evidence_requested"),
                "citations": state["decision"]["evidence_ids"],
            })
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["policy"]].append(row)
    summary = []
    for policy, group in sorted(grouped.items()):
        n = len(group)
        non_support = [row for row in group if row["reference_verdict"] != "supported"]
        summary.append({
            "policy": policy, "n_cases": n,
            "verdict_accuracy": sum(row["verdict_correct"] for row in group) / n,
            "reference_support_coverage": sum(row["reference_support_complete"] for row in group) / n,
            "decision_and_support_rate": sum(row["decision_and_support_correct"] for row in group) / n,
            "false_supported_rate_on_non_supported": (sum(row["predicted_verdict"] == "supported" for row in non_support) / len(non_support)) if non_support else None,
            "mean_credits": sum(row["credits_spent"] for row in group) / n,
        })
    hashes = {}
    for path in (store.directory / "scenarios.json", store.directory / "evidence.json", store.directory / "evaluator" / "gold.json"):
        hashes[str(path.relative_to(store.directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema_version": "0.1.0",
        "evaluation_kind": "engineering_smoke_test_on_author_defined_synthetic_fixtures",
        "scientific_performance_claim": False,
        "limitations": [
            "Policies and fixture rules were authored together; this is not independent evaluation.",
            "Eight cases share two templates. They are not eight independent real audit samples.",
            "All references are synthetic and have not been independently reviewed by a pharmaceutical QA expert.",
            "Reference support coverage tests IDs, not semantic entailment or rationale quality.",
            "No LLM, RL training, external dataset evaluation, real GMP validation, or human learning study was run.",
        ],
        "fixture_sha256": hashes,
        "template_groups": engine.evaluator.paired_groups(),
        "summary": summary,
        "episodes": rows,
    }


def write_benchmark(path: Path, data_dir: Path | str | None = None) -> dict:
    result = run_benchmark(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
