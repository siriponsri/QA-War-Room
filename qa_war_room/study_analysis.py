"""Evaluator-only descriptive engineering analysis; scientific inference withheld."""

from collections import Counter
import csv
from pathlib import Path

from .native_data import file_hash, read_jsonl
from .native_runner import atomic_json, now, run_lock
from .pharma_eval import evaluate_terminal, load_gold
from .sequential_data import write_jsonl
from .study_metrics import fraction, paired_rows, summarize, validate_rows
from .study_runner import load_run

ENDPOINTS = ("false_support_rate", "supported_sensitivity", "coverage", "overall_accuracy")


def outcomes(config, store, engines, counts, failed, seconds):
    """Join only after source replay. Includes every frozen job, even unstarted."""
    gold = load_gold(store)
    cohort = {row["case_id"]: row for row in config["cohort"]}
    rows = []
    for job in config["jobs"]:
        key = job["key"]
        observation = engines[key].observation()
        reference = gold[job["case_id"]]
        status, verdict, proxy = failed.get(key, "pending"), None, False
        if key not in failed and observation["status"] == "completed":
            decision = observation["decision"]
            if decision["type"] == "abstain":
                status = "abstain"
            else:
                status, verdict = "ok", decision["verdict"]
                evaluation = evaluate_terminal(store, observation)
                proxy = all(evaluation[field] is True for field in (
                    "label_matches_candidate", "observed_decision_matches_declared_rules",
                    "declared_fact_locations_cited", "required_unavailability_checks_made"))
        rows.append({"id": key, "case_id": job["case_id"], "family_id": cohort[job["case_id"]]["family_id"],
                     "method": job["method"], "credits": job["credits"], "repetition": job["repetition"],
                     "primary_eligible": reference["primary_eligible_draft"], "reference_label": reference["candidate_verdict"],
                     "status": status, "verdict": verdict, "evidence_proxy": proxy, "actions": counts[key],
                     "source_bytes": observation["budget"]["source_bytes_exposed"],
                     "acquisition_credits": observation["budget"]["spent"], "wall_seconds": seconds[key]})
    validate_rows(rows)
    return rows


def pair_diagnostics(rows, pairs):
    """Author-defined pairs; failed/unstarted endpoints remain in denominators."""
    result = []
    for method, credits, repetition in sorted({(r["method"], r["credits"], r["repetition"]) for r in rows}):
        index = {r["case_id"]: r for r in rows if (r["method"], r["credits"], r["repetition"]) == (method, credits, repetition)}
        selected = []
        for pair in pairs:
            included = [identity in index for identity in (pair["anchor_id"], pair["case_id"])]
            if any(included) and not all(included):
                raise ValueError("Incomplete counterfactual source family")
            if all(included):
                selected.append(pair)
        changing = [p for p in selected if p["pair_type"] == "label_changing"]
        preserving = [p for p in selected if p["pair_type"] == "label_preserving"]
        def valid(pair):
            return all(index[identity]["status"] == "ok" for identity in (pair["anchor_id"], pair["case_id"]))
        def correct(pair):
            return valid(pair) and all(index[identity]["verdict"] == index[identity]["reference_label"] for identity in (pair["anchor_id"], pair["case_id"]))
        result.append({"method": method, "credits": credits, "repetition": repetition,
            "all_pairs": len(selected), "ambiguous_pairs_separate": sum(p["pair_type"] == "unresolved_ambiguity" for p in selected),
            "correct_label_change": fraction(sum(correct(p) for p in changing), len(changing)),
            "any_label_change": fraction(sum(valid(p) and index[p["anchor_id"]]["verdict"] != index[p["case_id"]]["verdict"] for p in changing), len(changing)),
            "label_preserving_stability": fraction(sum(valid(p) and index[p["anchor_id"]]["verdict"] == index[p["case_id"]]["verdict"] for p in preserving), len(preserving)),
            "correct_preserving_pair": fraction(sum(correct(p) for p in preserving), len(preserving)),
            "independently_reviewed": False})
    return result


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def analyze_run(pack, lock, run, output):
    output, run = Path(output), Path(run)
    if output.exists():
        raise ValueError("Analysis output exists; preserve it and choose a new directory")
    # Replay and join under a single read exclusion. No policy calls during analysis.
    with run_lock(run):
        config, store, events, engines, counts, failed, seconds = load_run(pack, lock, run)
        rows = outcomes(config, store, engines, counts, failed, seconds)
        pairs = read_jsonl(store.directory / "evaluator/pairs.jsonl")
        candidate_counts = dict(Counter(row["reference_label"] or "ambiguous" for row in rows if row["method"] == config["plan"]["engineering"]["methods"][0] and row["credits"] == min(config["plan"]["engineering"]["budgets"]) and row["repetition"] == 0))
        source_hashes = {name: file_hash(run / name) for name in ("manifest.json", "events.jsonl") if (run / name).exists()}
    tables, comparisons, csv_rows = [], [], []
    settings = config["plan"]["engineering"]
    candidate, comparator = (settings["comparison"][key] for key in ("candidate", "comparator"))
    for budget in sorted(settings["budgets"]):
        budget_rows = [row for row in rows if row["credits"] == budget]
        for method in settings["methods"]:
            method_rows = [row for row in budget_rows if row["method"] == method]
            metrics = summarize(method_rows)
            family_tables = {family: summarize([row for row in method_rows if row["family_id"] == family])
                             for family in sorted({row["family_id"] for row in method_rows})}
            metrics["family_descriptive_metrics"] = family_tables
            metrics["equal_family_weighted_sensitivity"] = {}
            for endpoint in ENDPOINTS:
                defined = [table[endpoint]["value"] for table in family_tables.values() if table[endpoint]["value"] is not None]
                metrics["equal_family_weighted_sensitivity"][endpoint] = {
                    "value": sum(defined) / len(defined) if defined else None,
                    "defined_families": len(defined), "undefined_families": len(family_tables) - len(defined)}
            tables.append({"method": method, "credits": budget, **metrics})
            for endpoint in ENDPOINTS:
                csv_rows.append({"method": method, "credits": budget, "endpoint": endpoint,
                    **metrics[endpoint], "primary_episodes": metrics["primary_episodes"],
                    "ambiguous_episodes": metrics["ambiguous_separate_episodes"], "status": "ENGINEERING_ONLY"})
        left, right = paired_rows(budget_rows, candidate, comparator)
        a, b = summarize(left), summarize(right)
        comparisons.append({"credits": budget, "candidate": candidate, "comparator": comparator,
            "paired_jobs_per_arm": len(left), "families": a["construction_families"],
            "candidate_minus_comparator": {key: a[key]["value"] - b[key]["value"] if a[key]["value"] is not None and b[key]["value"] is not None else None for key in ENDPOINTS},
            "uncertainty_status": "WITHHELD_UNREVIEWED_REFERENCE_AND_UNVALIDATED_INDEPENDENT_UNITS",
            "confidence_intervals": None, "scientific_success": "NOT_EVALUATED"})
    diagnostic = {"status": "ENGINEERING_ONLY", "scientific_performance_claim": False,
        "independent_review_completed": False, "adjudication_completed": False,
        "reference_status": "author_draft_unreviewed", "jobs": len(rows), "tables": tables,
        "paired_descriptive_comparisons": comparisons, "counterfactual_diagnostics": pair_diagnostics(rows, pairs),
        "feasibility": {"source_cases": len(config["cohort"]), "construction_families": len({r["family_id"] for r in rows}),
            "cases_per_family": dict(Counter(r["family_id"] for r in config["cohort"])),
            "author_candidate_counts": candidate_counts,
            "statuses": dict(Counter(r["status"] for r in rows)), "llm_calls": 0, "model_tokens": 0, "cost_usd": "0",
            "sample_size_adequacy": "NOT_ESTABLISHED", "power_analysis": "NOT_RUN"},
        "scientific_blockers": config["scientific_blockers"]}
    output.mkdir(parents=True)
    (output / "evaluator").mkdir()
    write_jsonl(output / "evaluator/outcomes.jsonl", rows)
    atomic_json(output / "ENGINEERING_METRICS.json", diagnostic)
    write_csv(output / "ENGINEERING_METRICS.csv", ("method", "credits", "endpoint", "numerator", "denominator", "value", "primary_episodes", "ambiguous_episodes", "status"), csv_rows)
    write_csv(output / "SCIENTIFIC_TABLE_TEMPLATE.csv", ("endpoint", "candidate", "comparator", "estimate", "ci_lower", "ci_upper", "status"),
        [{"endpoint": key, "candidate": "", "comparator": "", "estimate": "", "ci_lower": "", "ci_upper": "", "status": "NOT_RUN"} for key in ENDPOINTS])
    manifest = {"created_utc": now(), "status": "ENGINEERING_ONLY", "scientific_performance_claim": False,
        "independent_review_completed": False, "reference_status": "author_draft_unreviewed",
        "lock_sha256": file_hash(Path(lock) / "LOCK.json"), "source_run_files": source_hashes,
        "last_event_sha256": events[-1]["sha256"] if events else None,
        "evaluator_files": store.manifest["evaluator_files"], "implementation_sha256": config["implementation_sha256"],
        "outputs": {str(path.relative_to(output)): file_hash(path) for path in sorted(output.rglob("*")) if path.is_file()}}
    (output / "REPORT.md").write_text(
        "# G5 offline engineering diagnostics\n\nStatus: ENGINEERING_ONLY. Independent review and adjudication are NOT_PERFORMED; reference is NOT_LOCKED.\n\n"
        f"Replayed {len(events)} source transitions for {len(rows)} frozen jobs over {len(config['cohort'])} synthetic source cases. "
        "All pending, abstained and failed jobs remain in their planned denominators. Ambiguous author references remain a separate stratum.\n\n"
        "These are coauthored scripted policies on coauthored structured synthetic SOPs, not independent humans or language models. "
        "Construction families are clustering placeholders, not established independent manufacturing sites. Test data may not be promoted retrospectively into confirmatory evidence.\n\n"
        "ENGINEERING_METRICS.csv/JSON contain descriptive diagnostics only. Scientific estimates and intervals are NOT_RUN in SCIENTIFIC_TABLE_TEMPLATE.csv. "
        "Bootstrap arithmetic is unit-tested but research intervals and joint success are withheld here. Zero observed errors do not establish safety. "
        "Structured evidence proxies are not semantic rationale judgments. No model calls, model tokens or API spend occurred.\n\n"
        "See docs/G5_EVALUATION_PLAN.md for endpoints, fixed denominators, assumptions, review gates and the next steps.\n", encoding="utf-8")
    manifest["outputs"]["REPORT.md"] = file_hash(output / "REPORT.md")
    atomic_json(output / "ANALYSIS.json", manifest)
    return {"status": "ENGINEERING_ONLY", "jobs": len(rows), "source_cases": len(config["cohort"]),
        "tables": len(tables), "statuses": diagnostic["feasibility"]["statuses"], "gold_join": "evaluator_only_after_replay",
        "scientific_success": "NOT_EVALUATED", "confidence_intervals": "WITHHELD", "cost_usd": "0"}
