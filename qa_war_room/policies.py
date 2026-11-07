"""Transparent scripted policies; these are not LLMs and have no learned skill.

Inputs are public session states. This module cannot access fixture files, the
engine store, gold labels, or other agents' private state. Structured fields in
retrieved records are the source observations, not hidden grading annotations.
"""

from __future__ import annotations


PROTOCOL_ORDER = (
    "closure_protocol", "implementation_record", "training_record",
    "effectiveness_report", "deviation_trend", "status_log",
)
COUNTEREVIDENCE_ORDER = (
    "closure_protocol", "status_log", "deviation_trend", "effectiveness_report",
    "implementation_record", "training_record",
)


def _decision(verdict: str, citations: list[str], rationale: str) -> dict:
    return {"type": "decide", "verdict": verdict,
            "evidence_ids": list(dict.fromkeys(citations)), "rationale": rationale}


def assess_visible(state: dict) -> dict:
    """Apply the demo protocol to delivered records only.

    This simple rule reader is a baseline scaffold, not a general pharmaceutical
    inference system. The protocol and record schemas are intentionally narrow.
    """
    records = {record["document_type"]: record for record in state["evidence"]}
    protocol_record = records.get("closure_protocol")
    if not protocol_record:
        return _decision("insufficient", [], "The closure criteria have not been retrieved; I cannot establish the claim.")
    protocol = protocol_record["facts"]
    scope = protocol["scope"]
    as_of = state["case"]["as_of"]
    procedure = protocol["required_procedure"]
    citations = [protocol_record["id"]]
    gaps: list[tuple[str, str | None]] = []

    def current(record: dict) -> bool:
        return record["date"] <= as_of

    def contradict(record: dict, reason: str) -> dict:
        return _decision("contradicted", [protocol_record["id"], record["id"]], reason)

    def gap(message: str, record: dict | None = None) -> None:
        gaps.append((message, record["id"] if record else None))

    implementation = records.get("implementation_record")
    if implementation is None:
        gap("Implementation evidence is missing.")
    else:
        facts = implementation["facts"]
        if not current(implementation) or facts["completed_on"] > as_of:
            gap("Implementation documentation falls after the review cutoff.", implementation)
        elif facts["line"] != scope["line"] or facts["capa_id"] != protocol["capa_id"]:
            gap("The implementation record concerns a different line or CAPA.", implementation)
        elif facts["status"] != "completed" or facts["procedure"] != procedure:
            return contradict(implementation, "The implementation record explicitly fails the protocol's completion/procedure prerequisite.")
        else:
            citations.append(implementation["id"])

    training = records.get("training_record")
    if training is None:
        gap("Training evidence is missing.")
    else:
        facts = training["facts"]
        full_snapshot = facts.get("register_complete") is True and facts["as_of"] == as_of
        if not current(training) or facts["completed_on"] > as_of or not full_snapshot:
            gap("The training register is not a complete snapshot available at the review cutoff.", training)
        elif facts["capa_id"] != protocol["capa_id"]:
            gap("The training register covers a different CAPA.", training)
        elif (facts["procedure"] != procedure
              or not set(protocol["required_operator_ids"]) <= set(facts["operator_ids"])
              or facts["completed_on"] >= scope["window_start"]):
            return contradict(training, "The complete training register does not meet the required procedure revision, operator coverage, or pre-cohort timing specified by the protocol.")
        else:
            citations.append(training["id"])

    effectiveness = records.get("effectiveness_report")
    if effectiveness is None:
        gap("A completed effectiveness report has not been obtained.")
    else:
        facts = effectiveness["facts"]
        observed = facts["scope"]
        scope_matches = (
            observed["line"] == scope["line"]
            and set(scope["batch_ids"]) <= set(observed["batch_ids"])
            and set(scope["batch_ids"]) <= set(facts["batches_reviewed"])
            and observed["window_start"] <= scope["window_start"]
            and observed["window_end"] >= scope["window_end"]
        )
        if not current(effectiveness) or facts["review_completed_on"] > as_of or observed["window_end"] > as_of:
            gap("The effectiveness report was not completed within the review cutoff.", effectiveness)
        elif (facts["protocol_id"] != protocol["protocol_id"]
              or facts["protocol_revision"] != protocol["revision"] or not scope_matches):
            gap("The effectiveness report does not cover the required protocol revision, line, batches and observation window.", effectiveness)
        elif (facts["acceptance_pass"] is not True
              or len(facts["failed_acceptance_batches"]) > protocol["maximum_failed_batches"]):
            return contradict(effectiveness, "The in-scope effectiveness report records failed acceptance against the protocol's explicit criteria.")
        elif len(facts["batches_reviewed"]) < protocol["minimum_batches"]:
            gap("Too few batches were reviewed to demonstrate the required effectiveness criterion.", effectiveness)
        else:
            citations.append(effectiveness["id"])

    trend = records.get("deviation_trend")
    if trend is None:
        gap("A current related-deviation review is missing.")
    else:
        facts = trend["facts"]
        if (not current(trend) or facts["as_of"] != as_of
                or facts["line"] != scope["line"] or facts["capa_id"] != protocol["capa_id"]
                or facts.get("review_complete") is not True):
            gap("The related-deviation review is not a complete current in-scope review.", trend)
        elif facts["unresolved_related_deviations"] > protocol["maximum_unresolved_related_deviations"]:
            return contradict(trend, "The current related-deviation review exceeds the unresolved-deviation limit in the protocol.")
        else:
            citations.append(trend["id"])

    status = records.get("status_log")
    if status is None:
        gap("A current complete status register is missing.")
    else:
        facts = status["facts"]
        if (not current(status) or facts["as_of"] != as_of
                or facts["effective_date"] > as_of or facts["capa_id"] != protocol["capa_id"]
                or facts.get("register_complete") is not True):
            gap("The status register does not establish current status at the cutoff.", status)
        elif facts["status"] != "closed":
            return contradict(status, "The complete current register records an open or reopened CAPA at the review cutoff; the protocol requires closed status.")
        else:
            citations.append(status["id"])

    if gaps:
        available_gap_records = [record_id for _, record_id in gaps if record_id]
        return _decision("insufficient", [protocol_record["id"], *available_gap_records],
                         " ".join(reason for reason, _ in gaps) + " Missing or out-of-scope evidence does not by itself establish manufacturing failure.")
    return _decision("supported", citations,
                     "All explicit local-protocol prerequisites are documented in the retrieved records, within the specified scope and cutoff. This conclusion applies only to this fictional protocol and case.")


def next_action(state: dict) -> dict:
    """Select exactly one request or decision without seeing gold or hidden text."""
    role = state["auditor_role"]
    catalog = state["catalog"]
    remaining = state["budget"]["remaining"]
    if role == "auditor-newbie-01":
        summary = next((record for record in state["evidence"] if record["document_type"] == "closure_summary"), None)
        if summary:
            return _decision("supported", [summary["id"]],
                             "Shortcut baseline: the cover sheet marks this CAPA closed and effective. This policy intentionally does not verify the underlying evidence.")
        candidate = next((item for item in catalog if item["document_type"] == "closure_summary"
                          and not item["requested"] and item["cost"] <= remaining), None)
        if candidate:
            return {"type": "request", "evidence_id": candidate["id"]}
        return _decision("insufficient", [], "The shortcut policy could not retrieve a closure cover sheet.")

    assessment = assess_visible(state)
    if assessment["verdict"] in {"supported", "contradicted"}:
        return assessment

    if role == "auditor-newbie-02":
        candidates = catalog
    else:
        order = PROTOCOL_ORDER if role == "auditor-expert-01" else COUNTEREVIDENCE_ORDER
        candidates = [item for kind in order for item in catalog if item["document_type"] == kind]
    for item in candidates:
        if not item["requested"] and item["cost"] <= remaining:
            return {"type": "request", "evidence_id": item["id"]}
    return assessment
