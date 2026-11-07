"""Pure evaluator arithmetic. No dataset, model, filesystem or reference access."""

from collections import Counter, defaultdict
import math
import random

LABELS = ("supported", "contradicted", "insufficient")
STATUSES = {"ok", "abstain", "pending", "invalid_action", "policy_error", "action_cap"}


def fraction(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "value": numerator / denominator if denominator else None}


def validate_rows(rows):
    seen, family = set(), {}
    for row in rows:
        for key in ("case_id", "family_id", "method"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError("Outcome identity fields must be nonempty strings")
        for key in ("credits", "repetition", "actions", "source_bytes", "acquisition_credits"):
            if type(row.get(key)) is not int or row[key] < 0:
                raise ValueError("Invalid outcome resource/schedule integer")
        if row["acquisition_credits"] > row["credits"]:
            raise ValueError("Outcome exceeds the acquisition cap")
        key = (row["case_id"], row["method"], row["credits"], row["repetition"])
        if key in seen:
            raise ValueError("Duplicate outcome unit")
        seen.add(key)
        if family.setdefault(row["case_id"], row["family_id"]) != row["family_id"]:
            raise ValueError("A source case crosses family groups")
        if (not isinstance(row.get("status"), str) or row["status"] not in STATUSES or type(row.get("primary_eligible")) is not bool or
                type(row.get("evidence_proxy")) is not bool or
                (row["primary_eligible"] and row.get("reference_label") not in LABELS) or
                (not row["primary_eligible"] and row.get("reference_label") is not None)):
            raise ValueError("Outcome status/reference eligibility mismatch")
        if ((row["status"] == "ok" and row.get("verdict") not in LABELS) or
                (row["status"] != "ok" and row.get("verdict") is not None)):
            raise ValueError("Only a valid submission may carry a scored verdict")
        value = row.get("wall_seconds")
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid elapsed-time accounting")


def summarize(rows, *, validate=True):
    if validate:
        validate_rows(rows)
    primary = [r for r in rows if r["primary_eligible"]]
    accepted = [r for r in primary if r["verdict"] == "supported"]
    positive = sum(r["reference_label"] == "supported" for r in primary)
    negative = len(primary) - positive
    correct = sum(r["status"] == "ok" and r["verdict"] == r["reference_label"] for r in primary)
    confusion = defaultdict(Counter)
    for row in primary:
        predicted = row["verdict"] or ("ABSTAIN" if row["status"] == "abstain" else
                                      "PENDING" if row["status"] == "pending" else "INVALID")
        confusion[row["reference_label"]][predicted] += 1
    f1 = {}
    for label in LABELS:
        tp = sum(r["reference_label"] == label and r["verdict"] == label for r in primary)
        denominator = sum(r["reference_label"] == label for r in primary) + sum(r["verdict"] == label for r in primary)
        f1[label] = 2 * tp / denominator if denominator else None
    defined_f1 = [value for value in f1.values() if value is not None]
    wrong_support = sum(r["reference_label"] != "supported" for r in accepted)
    proxy_supported = sum(r["evidence_proxy"] for r in accepted)
    return {"all_episodes": len(rows), "primary_episodes": len(primary), "ambiguous_separate_episodes": len(rows) - len(primary),
            "source_cases": len({r["case_id"] for r in rows}), "construction_families": len({r["family_id"] for r in rows}),
            "false_support_rate": fraction(wrong_support, negative),
            "supported_sensitivity": fraction(sum(r["reference_label"] == "supported" for r in accepted), positive),
            "coverage": fraction(sum(r["status"] == "ok" for r in primary), len(primary)),
            "overall_accuracy": fraction(correct, len(primary)),
            "macro_f1": sum(defined_f1) / len(defined_f1) if defined_f1 else None, "class_f1": f1,
            "wrong_share_of_accepted_supports": fraction(wrong_support, len(accepted)),
            "structured_evidence_proxy_share_of_supports": fraction(proxy_supported, len(accepted)),
            "warranted_support_proxy_recall": fraction(sum(r["reference_label"] == "supported" and r["evidence_proxy"] for r in accepted), positive),
            "semantic_evidence_validity": None,
            "statuses": dict(Counter(r["status"] for r in rows)), "confusion": dict(confusion),
            "resources": {key: sum(r[key] for r in rows) for key in ("actions", "source_bytes", "acquisition_credits", "wall_seconds")},
            "llm_calls": 0, "cost_usd": "0"}


def paired_rows(rows, candidate, comparator):
    validate_rows(rows)
    arms = {method: {} for method in (candidate, comparator)}
    if candidate == comparator:
        raise ValueError("Paired methods must differ")
    for row in rows:
        if row["method"] in arms:
            unit = (row["case_id"], row["credits"], row["repetition"])
            arms[row["method"]][unit] = row
    left, right = arms[candidate], arms[comparator]
    if not left or set(left) != set(right):
        raise ValueError("Paired comparison requires identical frozen source/budget/repetition units")
    for key in left:
        if any(left[key][field] != right[key][field] for field in ("family_id", "reference_label", "primary_eligible")):
            raise ValueError("Paired reference/group disagreement")
    return list(left.values()), list(right.values())


def quantile(values, probability):
    if not values or not 0 <= probability <= 1 or any(not math.isfinite(v) for v in values):
        raise ValueError("Finite quantile sample and unit-interval probability required")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def paired_bootstrap(rows, candidate, comparator, *, replicates=2000, seed=0, confidence=0.95):
    """Percentile arithmetic only; caller must establish independent-unit validity.

    Every sampled family carries both arms, all siblings and all repetitions.
    Undefined draws, zero FSR events, or degenerate distributions withhold CIs.
    """
    if (type(replicates) is not int or not 1 <= replicates <= 10000 or type(seed) is not int or
            type(confidence) not in (int, float) or not 0 < confidence < 1):
        raise ValueError("Invalid bootstrap configuration")
    left, right = paired_rows(rows, candidate, comparator)
    families = sorted({r["family_id"] for r in left})
    grouped_l = {family: [r for r in left if r["family_id"] == family] for family in families}
    grouped_r = {family: [r for r in right if r["family_id"] == family] for family in families}
    metrics = ("false_support_rate", "supported_sensitivity", "coverage", "overall_accuracy")
    point_l, point_r = summarize(left), summarize(right)
    values = {key: [] for key in metrics}
    coverage_values = []
    if len(families) >= 2:
        rng = random.Random(seed)
        for _ in range(replicates):
            selected = [rng.choice(families) for _ in families]
            sampled_l = [row for family in selected for row in grouped_l[family]]
            sampled_r = [row for family in selected for row in grouped_r[family]]
            # Duplicated sampled families are intended bootstrap weights, not duplicate data errors.
            a, b = summarize(sampled_l, validate=False), summarize(sampled_r, validate=False)
            for key in metrics:
                if a[key]["value"] is not None and b[key]["value"] is not None:
                    values[key].append(a[key]["value"] - b[key]["value"])
            if a["coverage"]["value"] is not None:
                coverage_values.append(a["coverage"]["value"])
    alpha = (1 - confidence) / 2
    def interval(sample, *, zero_events=False):
        reason = ("fewer_than_two_family_groups" if len(families) < 2 else
                  "undefined_denominator_draws" if len(sample) != replicates else
                  "zero_event_safety_inference_withheld" if zero_events else
                  "degenerate_distribution_not_a_safety_guarantee" if min(sample) == max(sample) else None)
        return {"interval": None if reason else [quantile(sample, alpha), quantile(sample, 1 - alpha)],
                "withheld_reason": reason, "defined_replicates": len(sample),
                "undefined_replicates": replicates - len(sample)}
    results = {}
    for key in metrics:
        a, b = point_l[key]["value"], point_r[key]["value"]
        zero = key == "false_support_rate" and (point_l[key]["numerator"] == 0 or point_r[key]["numerator"] == 0)
        results[key] = {"candidate_minus_comparator": a - b if a is not None and b is not None else None,
                        **interval(values[key], zero_events=zero)}
    return {"method": "paired_family_percentile_bootstrap_v1", "families": len(families), "replicates": replicates,
            "seed": seed, "confidence_level": confidence, "differences": results,
            "candidate_coverage": interval(coverage_values),
            "independence_or_domain_validity_established": False}


def joint_guardrail_arithmetic(intervals, margins):
    """Math helper, not a permission to assert a confirmatory/domain conclusion."""
    keys = {"minimum_fsr_reduction", "supported_sensitivity_loss_margin", "minimum_coverage", "overall_accuracy_loss_margin"}
    if set(margins) != keys or any(v is not None and (type(v) not in (int, float) or not 0 <= v <= 1) for v in margins.values()):
        raise ValueError("Four explicit finite unit-interval margins required")
    if any(value is None for value in margins.values()):
        return {"estimable": False, "joint_rule_met": None, "reason": "unresolved_margins"}
    required = {key: intervals["differences"][key]["interval"] for key in
                ("false_support_rate", "supported_sensitivity", "overall_accuracy")}
    coverage = intervals["candidate_coverage"]["interval"]
    if any(value is None for value in required.values()) or coverage is None:
        return {"estimable": False, "joint_rule_met": None, "reason": "withheld_or_undefined_interval"}
    checks = {"fsr": required["false_support_rate"][1] < -margins["minimum_fsr_reduction"],
              "sensitivity": required["supported_sensitivity"][0] > -margins["supported_sensitivity_loss_margin"],
              "coverage": coverage[0] >= margins["minimum_coverage"],
              "accuracy": required["overall_accuracy"][0] > -margins["overall_accuracy_loss_margin"]}
    return {"estimable": True, "joint_rule_met": all(checks.values()), "checks": checks,
            "scientific_claim_authorized": False}
