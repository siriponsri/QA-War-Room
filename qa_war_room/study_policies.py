"""Observation-only G5 engineering methods; no provider, filesystem or gold access."""

from copy import deepcopy

from .pharma_rules import assess_visible

METHODS = ("status-shortcut-v1", "sop-catalog-v1", "sop-adaptive-v1", "ignore-applicability-v1")


def terminal_action(observation, assessment):
    if assessment["verdict"] == "ambiguous" or not assessment["protocol_visible"]:
        return {"type": "abstain", "reason": "Unresolved or unobserved synthetic SOP; no unique engineering decision."}
    citations = [{"record_id": "D1", "pointer": "/facts/criteria"}]
    for row in assessment["criteria"]:
        if row["status"] in {"pass", "fail"}:
            citation = {"record_id": row["record_id"], "pointer": row["pointer"]}
        elif row["reason"] in {"scope_mismatch", "after_assessment_cutoff"}:
            citation = {"record_id": row["record_id"], "pointer": "/scope" if row["reason"] == "scope_mismatch" else "/recorded_at"}
        else:
            continue
        if citation not in citations:
            citations.append(citation)
    return {"type": "submit", "verdict": assessment["verdict"], "citations": citations,
            "rationale": "Offline engineering interpretation of visible structured SOP records; not independent pharmaceutical judgment."}


def choose_action(observation, method, seed=0):
    if method not in METHODS or observation["status"] != "active":
        raise ValueError("Registered offline method and active observation required")
    catalog = {row["id"]: row for row in observation["catalog"]}
    evidence = {row["id"]: row for row in observation["evidence"]}
    def acquire(record_id):
        if catalog[record_id]["cost"] > observation["budget"]["remaining"]:
            return {"type": "abstain", "reason": "Acquisition budget exhausted before a declared material record could be obtained."}
        return {"type": "request", "record_id": record_id}
    if method == "status-shortcut-v1":
        if not catalog["D6"]["requested"]:
            return acquire("D6")
        if "D6" not in evidence:
            return {"type": "abstain", "reason": "Status record not delivered."}
        status = evidence["D6"]["facts"].get("current_status")
        return {"type": "submit", "verdict": "supported" if status == "closed" else "insufficient",
                "citations": [{"record_id": "D6", "pointer": "/facts/current_status"}],
                "rationale": "Deliberately weak status-only engineering shortcut; no sufficiency check."}
    if not catalog["D1"]["requested"]:
        return acquire("D1")
    if "D1" not in evidence:
        return {"type": "abstain", "reason": "Governing SOP was not delivered."}
    documents = deepcopy(observation["evidence"])
    if method == "ignore-applicability-v1":
        # Ablate interpretation only. Never mutate actual source/response evidence.
        for document in documents:
            document["scope"] = deepcopy(observation["case"]["scope"])
            document["recorded_at"] = min(document["recorded_at"], observation["case"]["as_of"])
            document["effective_from"] = min(document["effective_from"], observation["case"]["as_of"])
    assessment = assess_visible(observation["case"], documents, observation["responses"])
    if method == "sop-adaptive-v1" and assessment["verdict"] in {"contradicted", "ambiguous"}:
        return terminal_action(observation, assessment)
    required = {row["record_id"] for row in evidence["D1"]["facts"]["criteria"]}
    order = ("D5", "D4", "D6", "D3", "D2") if method == "sop-adaptive-v1" else tuple(sorted(required))
    for record_id in order:
        if record_id in required and not catalog[record_id]["requested"]:
            return acquire(record_id)
    if any(row["status"] == "exposure_cap_not_delivered" for row in observation["responses"]):
        return {"type": "abstain", "reason": "Exposure cap prevents a complete material-record assessment."}
    return terminal_action(observation, assessment)
