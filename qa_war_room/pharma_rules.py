"""Declared synthetic site criteria. Not a legal or natural-language GMP evaluator."""

from datetime import date
import math

from .pharma_authoring import RULE_VERSION

VERDICTS = ("supported", "contradicted", "insufficient")


def pointer(document, path):
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError("Use an absolute JSON pointer")
    value = document
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            if not part.isdigit():
                raise ValueError("Invalid array pointer")
            value = value[int(part)]
        elif isinstance(value, dict):
            value = value[part]
        else:
            raise ValueError("Pointer traverses a scalar")
    return value


def applicability(case, document):
    cutoff = date.fromisoformat(case["as_of"])
    if document["approval_status"] != "approved":
        return "approval_not_established"
    if any(date.fromisoformat(document[key]) > cutoff for key in ("recorded_at", "effective_from")):
        return "after_assessment_cutoff"
    scope, target = document["scope"], case["scope"]
    if scope["product"] != target["product"] or scope["line"] != target["line"] or not set(target["batches"]) <= set(scope["batches"]):
        return "scope_mismatch"
    return None


def assess_visible(case, documents, responses=()):
    """The caller controls observation access; no store/evaluator/path parameter exists."""
    index = {record["id"]: record for record in documents}
    sop = index.get("D1")
    if not sop or applicability(case, sop):
        return {"verdict": "insufficient", "criteria": [], "protocol_visible": False,
                "unresolved": ["Applicable governing synthetic SOP not observed"]}
    if sop["facts"].get("rule_version") != RULE_VERSION or sop["facts"].get("sop_id") != case["sop_id"]:
        raise ValueError("Unsupported or mismatched synthetic SOP")
    outcomes = []
    statuses = {row["record_id"]: row["status"] for row in responses}
    for criterion in sop["facts"]["criteria"]:
        record = index.get(criterion["record_id"])
        status, reason, value = "unknown", "not_acquired", None
        if criterion["expected"] is None:
            status, reason = "ambiguous", "acceptance_criterion_not_predefined"
        elif record is None:
            reason = statuses.get(criterion["record_id"], "not_acquired")
        elif applicability(case, record):
            reason = applicability(case, record)
        else:
            try:
                value = pointer(record, criterion["pointer"])
            except (ValueError, KeyError, IndexError, TypeError):
                reason = "required_fact_not_recorded"
            else:
                expected, op = criterion["expected"], criterion["op"]
                if op == "eq":
                    if type(value) is not type(expected):
                        raise ValueError("Synthetic equality criterion fact type mismatch")
                    passed = value == expected
                elif op == "includes":
                    if not isinstance(value, list) or not isinstance(expected, list):
                        raise ValueError("includes criterion requires arrays")
                    passed = set(expected) <= set(value)
                elif op == "ge":
                    if type(value) not in (int, float) or type(expected) not in (int, float):
                        raise ValueError("ge criterion requires numeric facts")
                    if not math.isfinite(value) or not math.isfinite(expected):
                        raise ValueError("Synthetic numeric facts must be finite")
                    passed = value >= expected
                else:
                    raise ValueError("Unsupported synthetic criterion operator")
                status, reason = ("pass", "declared_criterion_met") if passed else ("fail", "explicit_applicable_criterion_failure")
        outcomes.append({"criterion_id": criterion["id"], "record_id": criterion["record_id"],
                         "pointer": criterion["pointer"], "status": status, "reason": reason,
                         "observed_value": value, "expected": criterion["expected"]})
    states = {row["status"] for row in outcomes}
    verdict = ("contradicted" if "fail" in states else "ambiguous" if "ambiguous" in states else
               "insufficient" if "unknown" in states or not outcomes else "supported")
    return {"verdict": verdict, "criteria": outcomes, "protocol_visible": True,
            "unresolved": [row["criterion_id"] + ": " + row["reason"] for row in outcomes if row["status"] in {"unknown", "ambiguous"}]}
