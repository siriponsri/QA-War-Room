"""Input-only engineering locks and fail-closed scientific-lock requests."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import platform

from .native_data import digest, file_hash
from .native_runner import atomic_json, now
from .pharma_engine import PharmaStore
from .study_policies import METHODS

PLAN_KEYS = {"schema", "study_id", "study_stage", "reference_requirement", "primary_endpoint", "scientific_comparison",
             "guardrails", "reviewed_reference_release_sha256", "independent_review_record_sha256", "adjudication_record_sha256",
             "sample_size_justification_sha256", "model_revision", "prompt_bundle_sha256", "analysis", "engineering"}
GUARDRAILS = {"minimum_fsr_reduction", "supported_sensitivity_loss_margin", "minimum_coverage", "overall_accuracy_loss_margin"}


def code_hashes():
    names = ("study.py", "study_plan.py", "study_policies.py", "study_runner.py", "study_metrics.py", "study_analysis.py",
             "pharma_authoring.py", "pharma_engine.py", "pharma_rules.py", "pharma_eval.py", "native_data.py", "native_runner.py",
             "sequential_data.py", "models.py", "__init__.py")
    return {name: file_hash(Path(__file__).with_name(name)) for name in names}


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != PLAN_KEYS or plan["schema"] != "qawr-g5-plan-v1":
        raise ValueError("Unsupported evaluation plan schema")
    if (plan["study_stage"] != "B_pharmaceutical_prospective" or
            plan["reference_requirement"] != "independently_reviewed_manufacturing_gmp" or
            plan["primary_endpoint"] != "false_supported_closure_or_effectiveness_claim_rate"):
        raise ValueError("Unsupported scientific task/stage")
    if set(plan["guardrails"]) != GUARDRAILS or set(plan["scientific_comparison"]) != {"candidate", "comparator"}:
        raise ValueError("Scientific comparison/guardrail schema mismatch")
    for value in plan["guardrails"].values():
        if value is not None and (type(value) not in (int, float) or not 0 <= value <= 1):
            raise ValueError("Scientific margins must be null or finite unit-interval numbers")
    settings = plan["engineering"]
    keys = {"partitions", "methods", "comparison", "budgets", "repetitions", "seed", "max_policy_actions",
            "max_actions_per_job", "max_source_bytes_per_job", "max_jobs", "provider", "max_cost_usd", "retry_limit"}
    if (set(settings) != keys or settings["provider"] != "offline_only" or
            not isinstance(settings["max_cost_usd"], str) or Decimal(settings["max_cost_usd"]) != 0 or
            type(settings["retry_limit"]) is not int or settings["retry_limit"] != 0):
        raise ValueError("Only offline, zero-cost, zero-retry engineering plans are supported")
    for key in ("max_policy_actions", "max_actions_per_job", "max_source_bytes_per_job"):
        if type(settings[key]) is not int or settings[key] < 0:
            raise ValueError("Caps must be nonnegative integers")
    if (type(settings["repetitions"]) is not int or settings["repetitions"] < 1 or
            type(settings["max_jobs"]) is not int or not 1 <= settings["max_jobs"] <= 10000 or type(settings["seed"]) is not int):
        raise ValueError("Invalid repetition/job/seed settings")
    for key, choices in (("partitions", {"train", "dev", "test"}), ("methods", set(METHODS))):
        values = settings[key]
        if not isinstance(values, list) or not values or any(not isinstance(v, str) or v not in choices for v in values) or len(values) != len(set(values)):
            raise ValueError("Choose unique registered partitions/methods")
    budgets = settings["budgets"]
    if not isinstance(budgets, list) or not budgets or any(type(n) is not int or n < 0 for n in budgets) or len(set(budgets)) != len(budgets):
        raise ValueError("Use unique nonnegative acquisition budgets")
    comparison = settings["comparison"]
    if (set(comparison) != {"candidate", "comparator"} or comparison["candidate"] == comparison["comparator"] or
            any(value not in settings["methods"] for value in comparison.values())):
        raise ValueError("Engineering comparison must name two distinct registered methods")
    analysis = plan["analysis"]
    expected_analysis = {"unit", "weighting", "interval_method", "confidence_level", "bootstrap_replicates", "bootstrap_seed",
                         "empty_denominator", "rare_events", "ambiguity_policy", "failure_policy", "multiplicity"}
    if set(analysis) != expected_analysis or analysis["unit"] != "construction_family" or analysis["weighting"] != "case_repetition_item_weighted":
        raise ValueError("Source-family clustering and item weighting must be explicit")
    if (analysis["interval_method"] != "paired_family_percentile_bootstrap_v1" or
            type(analysis["confidence_level"]) not in (int, float) or not 0 < analysis["confidence_level"] < 1 or
            type(analysis["bootstrap_replicates"]) is not int or not 1 <= analysis["bootstrap_replicates"] <= 10000 or
            type(analysis["bootstrap_seed"]) is not int or
            analysis["empty_denominator"] != "null_and_withhold_undefined_intervals" or
            analysis["rare_events"] != "withhold_zero_event_or_degenerate_intervals_pending_appropriate_method" or
            analysis["ambiguity_policy"] != "preflagged_ambiguous_separate_stratum_not_primary" or
            analysis["failure_policy"] != "all_frozen_jobs_retained_no_success_only_primary" or
            analysis["multiplicity"] != "one_future_primary_comparison_and_joint_guardrails_other_comparisons_exploratory"):
        raise ValueError("Unsupported analysis, ambiguity or failure policy")
    return deepcopy(plan)


def scientific_blockers(plan, manifest):
    reasons = []
    if manifest.get("stage") == "G4_author_draft" or not manifest.get("independent_review_completed"):
        reasons.append("Independent reference review and adjudication have not been established")
    # No supported reviewed-reference release reader exists in this increment.
    reasons.append("Current supported reference schema is author-draft only; a verified reviewed release is required")
    for key in ("reviewed_reference_release_sha256", "independent_review_record_sha256", "adjudication_record_sha256",
                "sample_size_justification_sha256", "model_revision", "prompt_bundle_sha256"):
        if not plan[key]:
            reasons.append("Unresolved: " + key)
    if not all(plan["scientific_comparison"].values()):
        reasons.append("Scientific primary comparison has not been selected/frozen")
    if any(value is None for value in plan["guardrails"].values()):
        reasons.append("Domain-informed effect and guardrail margins remain unset")
    return reasons


def matrix(store, plan):
    """Derive every complete selected family/job from public inputs, never gold."""
    settings = plan["engineering"]
    cards = [store.card(case_id) for case_id in store.case_ids() if store.card(case_id)["split"] in settings["partitions"]]
    if not cards:
        raise ValueError("No complete source families selected")
    count = len(cards) * len(settings["methods"]) * len(settings["budgets"]) * settings["repetitions"]
    if count > settings["max_jobs"]:
        raise ValueError("Engineering matrix exceeds the hard job ceiling")
    cohort = [{"case_id": card["id"], "family_id": card["family_id"], "template_id": card["template_id"],
               "partition": card["split"], "public_card_sha256": digest(card)} for card in cards]
    jobs = [{"key": digest([card["case_id"], method, budget, repetition])[:32], "case_id": card["case_id"],
             "method": method, "credits": budget, "repetition": repetition}
            for card in cohort for budget in sorted(settings["budgets"]) for repetition in range(settings["repetitions"]) for method in settings["methods"]]
    return cohort, jobs


def make_lock(pack, plan_path, output, *, mode="engineering"):
    output = Path(output)
    if mode not in {"engineering", "confirmatory"}:
        raise ValueError("Choose engineering or confirmatory lock request")
    if output.exists():
        raise ValueError("Lock output exists; preserve it and choose a new directory")
    plan = validate_plan(json.loads(Path(plan_path).read_text(encoding="utf-8")))
    store = PharmaStore(pack)
    blockers = scientific_blockers(plan, store.manifest)
    if mode == "confirmatory":
        output.mkdir(parents=True)
        refusal = {"status": "REFUSED", "not_a_study_lock": True, "scientific_analysis_authorized": False,
                   "created_utc": now(), "reasons": blockers, "plan_sha256": file_hash(Path(plan_path))}
        atomic_json(output / "REFUSAL.json", refusal)
        return refusal
    cohort, jobs = matrix(store, plan)
    config = {"kind": "engineering_development_only", "scientific_performance_claim": False,
              "environment": {"python": platform.python_version(), "platform": platform.platform()},
              "plan": plan, "plan_sha256": file_hash(Path(plan_path)),
              "pack_sha256": file_hash(store.directory / "PACK.json"), "pack_version": store.manifest["pack_version"],
              "reference_status": "author_draft_unreviewed", "cohort": cohort, "jobs": jobs,
              "implementation_sha256": code_hashes(), "scientific_blockers": blockers}
    output.mkdir(parents=True)
    atomic_json(output / "LOCK.json", {"created_utc": now(), "config": config, "config_sha256": digest(config)})
    return {"status": "ENGINEERING_LOCKED", "scientific_study_locked": False, "cases": len(cohort),
            "construction_families": len({row["family_id"] for row in cohort}), "jobs": len(jobs), "blockers": blockers}


def load_lock(pack, directory):
    record = json.loads((Path(directory) / "LOCK.json").read_text(encoding="utf-8"))
    config = record["config"]
    if config.get("kind") != "engineering_development_only" or config.get("scientific_performance_claim") is not False or record["config_sha256"] != digest(config):
        raise ValueError("Invalid or non-engineering lock")
    if config["implementation_sha256"] != code_hashes():
        raise ValueError("Study implementation changed since lock")
    store = PharmaStore(pack)
    if config["pack_sha256"] != file_hash(store.directory / "PACK.json"):
        raise ValueError("Reference/input pack changed since lock")
    validate_plan(config["plan"])
    cohort, jobs = matrix(store, config["plan"])
    if config["cohort"] != cohort or config["jobs"] != jobs:
        raise ValueError("Frozen cohort/group/job matrix mismatch")
    if config["reference_status"] != "author_draft_unreviewed" or config["scientific_blockers"] != scientific_blockers(config["plan"], store.manifest):
        raise ValueError("Frozen reference status mismatch")
    return record, store
