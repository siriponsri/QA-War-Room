"""Evaluator-only source references, coverage proxies and oracle diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

from .native_data import NLI_LABELS, checked_file, file_hash, read_jsonl
from .sequential_data import INPUT_FILES, TASK_VERSION, SequentialStore, write_jsonl

GOLD_FILE = "evaluator/gold.jsonl"


def prepare_references(native: Path, output: Path, manifest: dict) -> dict:
    """Offline construction step, after segmentation/grouping has already finished."""
    prep = json.loads((native / "PREPARATION_REPORT.json").read_text(encoding="utf-8"))
    if file_hash(native / "PREPARATION_REPORT.json") != manifest["native_preparation_sha256"]:
        raise ValueError("Native preparation changed during derived construction")
    sources = {row["id"]: row for row in read_jsonl(output / INPUT_FILES[1])}
    episodes = {row["id"]: row for row in read_jsonl(output / INPUT_FILES[0])}
    gold = []
    for split in ("train", "dev", "test"):
        native_gold = read_jsonl(checked_file(native, f"evaluator/contractnli/{split}.gold.jsonl", prep))
        for row in native_gold:
            episode = episodes[row["id"]]
            source = sources[episode["source_id"]]
            all_ids = {s["id"] for record in source["records"] for s in record["spans"]}
            refs = row["evidence_span_ids"]
            if (row["label"] not in NLI_LABELS or not isinstance(refs, list) or
                    any(type(i) is not int for i in refs) or len(refs) != len(set(refs)) or not set(refs) <= all_ids or
                    (row["label"] == "NotMentioned" and refs)):
                raise ValueError("Native reference label/span mapping is invalid")
            gold.append({"id": row["id"], "source_id": episode["source_id"], "label": row["label"],
                         "reference_span_ids": refs, "original_split": split,
                         "reference_origin": "original_ContractNLI_annotation_unchanged",
                         "minimal_sufficient_sets": None,
                         "reference_policy": "all-published-spans-coverage-proxy-v1"})
    if len(gold) != len(episodes) or {r["id"] for r in gold} != set(episodes):
        raise ValueError("Derived reference cohort differs from inputs")
    write_jsonl(output / GOLD_FILE, gold)
    manifest = {**manifest, "evaluator_files": {GOLD_FILE: {"sha256": file_hash(output / GOLD_FILE),
                                                          "bytes": (output / GOLD_FILE).stat().st_size}}}
    # PACK is the completion marker. A partially prepared directory cannot run.
    (output / "PACK.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def load_references(store: SequentialStore) -> dict:
    if set(store.manifest["evaluator_files"]) != {GOLD_FILE}:
        raise ValueError("Unexpected evaluator manifest")
    entry, path = store.manifest["evaluator_files"][GOLD_FILE], store.directory / GOLD_FILE
    if file_hash(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
        raise ValueError("Derived evaluator checksum mismatch")
    return {row["id"]: row for row in read_jsonl(path)}


def fraction(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator,
            "value": numerator / denominator if denominator else None}


def evaluate_episode(store: SequentialStore, reference: dict, observation: dict) -> dict:
    """No natural-language entailment/minimality claim is made by these proxies."""
    records = [store.record(observation["episode_id"], r["id"]) for r in store.catalog(observation["episode_id"])]
    refs = set(reference["reference_span_ids"])
    required = [record for record in records if reference["label"] == "NotMentioned" or
                refs.intersection(s["id"] for s in record["spans"])]
    minimum_credits = len(required)
    required_bytes = sum(len(record["text"].encode("utf-8")) for record in required)
    has_reference = reference["label"] == "NotMentioned" or bool(refs)
    attainable = (minimum_credits <= observation["budget"]["credits_total"] and
                  required_bytes <= observation["budget"]["max_source_bytes"]) if has_reference else None
    visible = {s["id"] for record in observation["evidence"] for s in record["spans"]}
    full_source = len(observation["evidence"]) == len(records)
    observed = (full_source if reference["label"] == "NotMentioned" else refs <= visible) if has_reference else None
    decision = observation["decision"] or {}
    valid = observation["status"] == "completed"
    action = decision.get("type")
    forced = decision.get("label") if action == "submit" else decision.get("forced_label")
    citations = set(decision.get("citation_span_ids", []))
    submitted = valid and action == "submit"
    cited_complete = refs <= citations if reference["label"] != "NotMentioned" and refs else None
    return {"episode_id": observation["episode_id"], "source_id": observation["source_id"],
            "reference_label": reference["label"], "forced_label": forced,
            "selective_label": forced if submitted else ("ABSTAIN" if valid and action == "abstain" else
                                "PENDING" if observation["status"] == "active" else "INVALID"),
            "status": observation["status"], "forced_correct": valid and forced == reference["label"],
            "submitted": submitted, "full_source_observed": full_source,
            "published_reference_observed": observed, "published_reference_cited": cited_complete,
            "decision_and_reference_proxy": bool(submitted and forced == reference["label"] and observed and
                                                  (reference["label"] == "NotMentioned" or cited_complete)),
            "reference_span_recall": fraction(len(refs & visible), len(refs)),
            "source_bytes_exposed": observation["budget"]["source_bytes_exposed"],
            "credits_spent": observation["budget"]["credits_spent"],
            "unique_records_returned": len(observation["evidence"]),
            "denied_record_requests": sum(r["status"] != "delivered" for r in observation["responses"]),
            "oracle_diagnostic_only": {"proxy": "all-published-reference-coverage; NM requires full source exposure",
                "minimum_proxy_credits": minimum_credits if has_reference else None,
                "required_source_bytes": required_bytes if has_reference else None,
                "attainable_under_caps": attainable,
                "required_record_ids": [r["id"] for r in required],
                "minimal_semantic_sufficiency_known": False}}


def aggregate(rows: list[dict]) -> dict:
    n = len(rows)
    non_supported = sum(r["reference_label"] != "Entailment" for r in rows)
    supported = n - non_supported
    accepted = [r for r in rows if r["selective_label"] == "Entailment"]
    confusion = defaultdict(Counter)
    for row in rows:
        confusion[row["reference_label"]][row["selective_label"]] += 1
    proxy_defined = [r for r in rows if r["published_reference_observed"] is not None]
    return {"n": n, "source_documents": len({r["source_id"] for r in rows}),
            "source_families": len({r["source_family_id"] for r in rows}),
            "false_support_rate": fraction(sum(r["reference_label"] != "Entailment" for r in accepted), non_supported),
            "supported_sensitivity": fraction(sum(r["reference_label"] == "Entailment" for r in accepted), supported),
            "coverage": fraction(sum(r["submitted"] for r in rows), n),
            "forced_label_accuracy": fraction(sum(r["forced_correct"] for r in rows), n),
            "wrong_share_among_accepted_supports": fraction(sum(r["reference_label"] != "Entailment" for r in accepted), len(accepted)),
            "published_reference_observation_rate": fraction(sum(bool(r["published_reference_observed"]) for r in proxy_defined), len(proxy_defined)),
            "decision_and_reference_proxy_rate": fraction(sum(r["decision_and_reference_proxy"] for r in rows), n),
            "statuses": dict(Counter(r["status"] for r in rows)), "confusion": dict(confusion),
            "resource_totals": {key: sum(r[key] for r in rows) for key in
                                ("credits_spent", "source_bytes_exposed", "unique_records_returned", "denied_record_requests")},
            "llm_calls": 0, "model_tokens": 0, "cost_usd": "0"}


def score_sequential(bundle: Path, output: Path) -> dict:
    """Freeze/replay deployable traces first; only then read reference/oracle data."""
    from .native_runner import atomic_json, run_lock
    from .sequential_runner import load_replay

    store = SequentialStore(bundle)
    with run_lock(output):
        manifest, events, engines, counts = load_replay(store, output)
        references = load_references(store)
        config = manifest["config"]
        results, oracle = [], {}
        tables = defaultdict(list)
        for row in config["cohort"]:
            reference = references[row["episode_id"]]
            observation = engines[row["key"]].observation()
            result = evaluate_episode(store, reference, observation)
            diagnostic = result.pop("oracle_diagnostic_only")
            result.update({"key": row["key"], "source_family_id": row["source_family_id"],
                           "policy": row["policy"], "credits_total": row["credits"],
                           "policy_actions": counts[row["key"]]})
            oracle[(row["episode_id"], row["credits"])] = {
                "episode_id": row["episode_id"], "source_id": row["source_id"],
                "source_family_id": row["source_family_id"], "credits_total": row["credits"],
                "reference_label": reference["label"], **diagnostic}
            results.append(result)
            tables[(row["policy"], row["credits"])].append(result)
        output_tables = [{"policy": policy, "credits": budget, **aggregate(rows)}
                         for (policy, budget), rows in sorted(tables.items())]
        oracle_rows = list(oracle.values())
        reachability = []
        for budget in config["budgets"]:
            subset = [r for r in oracle_rows if r["credits_total"] == budget]
            defined = [r for r in subset if r["attainable_under_caps"] is not None]
            reachability.append({"credits": budget, "source_episodes": len(subset),
                                 "reference_defined": len(defined),
                                 "all_reference_proxy_attainable": fraction(sum(r["attainable_under_caps"] for r in defined), len(defined))})
        evaluator = output / "evaluator"
        evaluator.mkdir(exist_ok=True)
        write_jsonl(evaluator / "episodes.jsonl", [{"id": row["key"], **row} for row in results])
        atomic_json(evaluator / "oracle-diagnostics.json", {
            "diagnostic_only": True, "not_a_deployable_policy": True,
            "not_minimal_semantic_evidence": True, "budget_grid": reachability, "episodes": oracle_rows})
        report = {"task_version": TASK_VERSION, "track": "derived_sequential",
                  "native_benchmark_score": False, "study_status": "development_only",
                  "scientific_performance_claim": False, "model_is_llm": False,
                  "matrix_episodes": len(results), "pending": sum(r["status"] == "active" for r in results),
                  "source_episodes": len({r["episode_id"] for r in results}),
                  "source_documents": len({r["source_id"] for r in results}),
                  "source_families": len({r["source_family_id"] for r in results}),
                  "tables": output_tables, "policy_actions": sum(counts.values()),
                  "llm_calls": 0, "model_tokens": 0, "cost_usd": "0",
                  "manifest_sha256": file_hash(output / "manifest.json"),
                  "last_event_sha256": events[-1]["sha256"] if events else None,
                  "failure_policy": "Every frozen matrix item remains in its table denominator, including abstention, invalid and pending.",
                  "evidence_evaluation": "Published-reference-set coverage proxy only; semantic/minimal sufficiency unvalidated.",
                  "oracle_separation": "Post-run evaluator/oracle-diagnostics.json only; never passed to the policy or acquisition trace."}
        atomic_json(output / "metrics.json", report)
        lines = ["# G3 sequential engineering report", "",
                 "Development only. Offline wiring policies; zero LLM calls and USD 0. No pharmaceutical validation.", "",
                 f"Task: {TASK_VERSION}; derived split: {config['derived_split']}.",
                 f"Recorded grouping units: {report['source_families']} source families / {report['source_documents']} documents; broader independence is unverified.",
                 f"Source hypotheses: {report['source_episodes']}; matrix episodes: {len(results)}; pending: {report['pending']}.", "",
                 "## Deployable observation-only wiring paths", "",
                 "| Policy | Credits | N | Coverage | Forced correct / N | Credits spent | Source bytes |",
                 "| --- | ---: | ---: | ---: | --- | ---: | ---: |"]
        for table in output_tables:
            forced = table["forced_label_accuracy"]
            lines.append(f"| {table['policy']} | {table['credits']} | {table['n']} | {table['coverage']['value']:.3f} | "
                         f"{forced['numerator']} / {forced['denominator']} | {table['resource_totals']['credits_spent']} | "
                         f"{table['resource_totals']['source_bytes_exposed']} |")
        lines.extend(["", "Numbers above are observed engineering outputs from hash-selected labels, not semantic model results.",
                      "All source hypotheses, budgets and policy paths are dependent descendants; matrix episodes are not independent samples.",
                      "See metrics.json for FSR, sensitivity, confusion, abstention/failure denominators and resource totals.", "",
                      "## Separate oracle coverage-proxy diagnostic", "",
                      "Gold-based feasibility and witness IDs are only in evaluator/oracle-diagnostics.json.",
                      "This is an attainable all-reference-set coverage bound under the declared chunk/byte caps; it is not optimal semantic evidence or a deployable policy.",
                      "No confidence interval, significance, confirmatory hypothesis or pharmaceutical performance claim is made.", ""])
        (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
        return {key: report[key] for key in ("task_version", "matrix_episodes", "pending", "source_episodes",
                                             "source_documents", "source_families", "llm_calls", "cost_usd",
                                             "scientific_performance_claim")}
