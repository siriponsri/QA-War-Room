"""Dependency-free native metric formulas, with explicit failure denominators.

ContractNLI reference: contract-nli-bert 058c56f, evaluation.py; paper section 4.2.
DrugQA reference: cd026a2, analysis/score_results.py. See docs/NATIVE_BENCHMARK.md.
This implements the reported metric subset, not the complete training evaluator.
"""

from __future__ import annotations

from collections import defaultdict
import math


def mean_defined(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def ranked_metrics(pairs: list[tuple[float, bool]]) -> dict:
    """Threshold-group AP and first precision reaching recall .8; ties stay tied."""
    positives = sum(positive for _, positive in pairs)
    if not positives:
        return {"map": None, "precision@recall80": None}
    groups = defaultdict(lambda: [0, 0])
    for score, positive in pairs:
        groups[score][0] += int(positive)
        groups[score][1] += 1
    tp = seen = 0
    ap = 0.0
    p80 = None
    for score in sorted(groups, reverse=True):
        count, size = groups[score]
        tp += count
        seen += size
        precision = tp / seen
        ap += count / positives * precision
        if p80 is None and tp / positives >= 0.8:
            p80 = precision
    return {"map": ap, "precision@recall80": p80}


def class_metrics(rows: list[dict], predictions: dict[str, dict]) -> dict:
    correct = sum(predictions.get(r["id"], {}).get("label") == r["label"] for r in rows)
    result = {"n": len(rows), "correct": correct, "accuracy": correct / len(rows) if rows else None}
    for label in ("Entailment", "Contradiction"):
        positive = sum(r["label"] == label for r in rows)
        predicted = sum(predictions.get(r["id"], {}).get("label") == label for r in rows)
        tp = sum(r["label"] == label and predictions.get(r["id"], {}).get("label") == label for r in rows)
        result["f1_" + label.lower()] = 2 * tp / (positive + predicted) if positive else None
    return result


def contractnli_metrics(rows: list[dict], predictions: dict[str, dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[row["hypothesis_id"]].append(row)
    per_hypothesis = {key: class_metrics(group, predictions) for key, group in groups.items()}
    macro = {key: mean_defined([r[key] for r in per_hypothesis.values()])
             for key in ("accuracy", "f1_entailment", "f1_contradiction")}
    pairs = []
    aps = []
    missing = 0
    eligible = [r for r in rows if r["label"] != "NotMentioned"]
    for row in eligible:
        pred = predictions.get(row["id"])
        if pred is None:
            missing += 1
            aps.append(0.0)
            continue
        gold = set(row["evidence_span_ids"])
        local = [(pred["span_scores"].get(str(i), 0.0), i in gold) for i in range(row["span_count"])]
        pairs.extend(local)
        aps.append(ranked_metrics(local)["map"])
    # Do not report a successful-runtime-only native evidence score as a full-cohort result.
    complete_evidence = not missing and bool(eligible)
    return {"n": len(rows), "invalid_or_missing": sum(r["id"] not in predictions for r in rows),
            "micro_label_micro_doc": {"class": class_metrics(rows, predictions),
                "span": ranked_metrics(pairs) if complete_evidence else None},
            "macro_label_micro_doc": {"class": macro},
            "micro_label_macro_doc": {"span": {"map": mean_defined(aps)} if complete_evidence else None},
            "label_wise": per_hypothesis,
            "failure_diagnostics": {"evidence_eligible": len(eligible), "evidence_missing": missing,
                "map_with_failed_items_scored_zero": mean_defined(aps)},
            "evidence_scope": "Gold NotMentioned rows excluded, matching the native optimistic evidence evaluator.",
            "undefined_policy": "Null for absent gold class/evidence; macro averages omit undefined hypothesis F1."}


def drugqa_metrics(rows: list[dict], predictions: dict[str, dict]) -> dict:
    def score(group):
        n = len(group)
        valid = sum(r["id"] in predictions for r in group)
        correct = sum(predictions.get(r["id"], {}).get("answer") == r["answer"] for r in group)
        if n:
            p, z = correct / n, 1.959963984540054
            denominator = 1 + z * z / n
            center = (p + z * z / (2 * n)) / denominator
            half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
            interval = [max(0.0, center - half), min(1.0, center + half)]
        else:
            p, interval = None, None
        return {"n": n, "correct": correct, "invalid": n - valid,
                "accuracy": p, "valid_output_coverage": valid / n if n else None,
                "wilson_95_ci": interval}
    output = {"overall": score(rows)}
    for name, getter in (("by_task", lambda r: r["task_type"]),
                         ("by_language", lambda r: r["language"]),
                         ("by_final_quality", lambda r: r["final_quality"]),
                         ("by_object_domain", lambda r: r["category"]),
                         ("task_x_language", lambda r: r["task_type"] + "/" + r["language"])):
        groups = defaultdict(list)
        for row in rows:
            groups[getter(row)].append(row)
        output[name] = {key: score(group) for key, group in sorted(groups.items())}
    output["interval_note"] = "Native item-level Wilson diagnostic; not a source-clustered inference or pharma validation."
    return output
