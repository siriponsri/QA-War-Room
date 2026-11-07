"""Bounded, deterministic evidence-acquisition transitions.

The state machine is reproducible; session identifiers are random capabilities
for convenience, not authentication. The local server is not production-ready.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import threading
from typing import Any
import uuid

from .evaluation import ReferenceEvaluator
from .store import FixtureStore


VERDICTS = {"supported", "contradicted", "insufficient"}
PERSONAS = (
    {"id": "user-01", "label": "Manufacturing record owner", "kind": "auditee", "description": "Scripted custodian of implementation and training records."},
    {"id": "user-02", "label": "Quality record owner", "kind": "auditee", "description": "Scripted custodian of closure, effectiveness and status records."},
    {"id": "auditor-newbie-01", "label": "Cover-sheet policy", "kind": "auditor", "description": "Scripted shortcut policy: trusts the closure cover sheet. Name is not validated expertise."},
    {"id": "auditor-newbie-02", "label": "Catalog-order policy", "kind": "auditor", "description": "Scripted policy: acquires records in catalog order, then applies visible-data rules."},
    {"id": "auditor-expert-01", "label": "Protocol-first policy", "kind": "auditor", "description": "Scripted policy: requests protocol and its required records. Name is not validated expertise."},
    {"id": "auditor-expert-02", "label": "Counterevidence-first policy", "kind": "auditor", "description": "Scripted policy: checks protocol, current status and adverse evidence first."},
)
AUDITOR_ROLES = {persona["id"] for persona in PERSONAS if persona["kind"] == "auditor"}


class EngineError(Exception):
    def __init__(self, code: str, message: str, http_status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status


@dataclass
class Session:
    session_id: str
    case_id: str
    auditor_role: str
    budget_total: int
    budget_spent: int = 0
    status: str = "active"
    requested: list[str] = field(default_factory=list)
    unavailable: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    decision: dict | None = None
    feedback: dict | None = None


class SessionEngine:
    def __init__(self, store: FixtureStore | None = None, *, max_sessions: int = 250):
        self.store = store or FixtureStore()
        self.evaluator = ReferenceEvaluator(self.store.directory)
        self.max_sessions = max_sessions
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def list_cases(self) -> list[dict]:
        return self.store.list_cases()

    @staticmethod
    def personas() -> list[dict]:
        return deepcopy(list(PERSONAS))

    def create(self, case_id: Any, auditor_role: Any = "auditor-expert-01") -> dict:
        with self._lock:
            if not isinstance(case_id, str) or case_id not in self.store:
                raise EngineError("unknown_case", "Choose a case returned by /api/cases.", 404)
            if not isinstance(auditor_role, str) or auditor_role not in AUDITOR_ROLES:
                raise EngineError("invalid_role", "Choose one of the four configured auditor policies.")
            if len(self._sessions) >= self.max_sessions:
                raise EngineError("session_limit", "Local demo session limit reached. Restart the server to clear sessions.", 429)
            case = self.store.case(case_id)
            session = Session("qr_" + uuid.uuid4().hex, case_id, auditor_role, case["budget"])
            self._event(session, "session_started", auditor_role, "Session started. Only requested records will be disclosed.")
            self._sessions[session.session_id] = session
            return self._state(session)

    def state(self, session_id: str) -> dict:
        with self._lock:
            return self._state(self._get(session_id))

    def request(self, session_id: str, evidence_id: Any) -> dict:
        with self._lock:
            session = self._active(session_id)
            if not isinstance(evidence_id, str):
                raise EngineError("invalid_evidence_id", "evidence_id must be a catalog ID string.")
            catalog = {item["id"]: item for item in self.store.catalog(session.case_id)}
            if evidence_id not in catalog:
                raise EngineError("unknown_evidence", "Evidence is not listed in this case's catalog.", 404)
            # A retry is idempotent: no second charge, delivery, or event.
            if evidence_id in session.requested:
                return self._state(session)
            item = catalog[evidence_id]
            if item["cost"] > session.budget_total - session.budget_spent:
                raise EngineError("budget_exceeded", "Insufficient credits for this request. Select a cheaper record or submit a decision.", 409)
            artifact = self.store.evidence(session.case_id, evidence_id)
            session.budget_spent += item["cost"]
            session.requested.append(evidence_id)
            self._event(session, "evidence_requested", session.auditor_role,
                        f"Requested {evidence_id}; cost {item['cost']} credit(s).", evidence_id=evidence_id)
            if artifact["available"]:
                session.evidence.append(artifact["record"])
                self._event(session, "evidence_delivered", item["owner"],
                            f"Provided {item['title']}.", evidence_id=evidence_id)
            else:
                session.unavailable.append(evidence_id)
                self._event(session, "evidence_unavailable", item["owner"],
                            artifact["reason"], evidence_id=evidence_id)
            return self._state(session)

    def decide(self, session_id: str, verdict: Any, evidence_ids: Any, rationale: Any) -> dict:
        with self._lock:
            session = self._active(session_id)
            if not isinstance(verdict, str) or verdict not in VERDICTS:
                raise EngineError("invalid_verdict", "Use supported, contradicted, or insufficient.")
            if (not isinstance(evidence_ids, list) or len(evidence_ids) > 40
                    or any(not isinstance(item, str) for item in evidence_ids)):
                raise EngineError("invalid_citations", "evidence_ids must be an array of at most 40 catalog ID strings.")
            if len(set(evidence_ids)) != len(evidence_ids):
                raise EngineError("duplicate_citations", "Cite each record once.")
            delivered = {record["id"] for record in session.evidence}
            if not set(evidence_ids) <= delivered:
                raise EngineError("unretrieved_citation", "A citation must identify a record actually delivered in this session.")
            if verdict != "insufficient" and not evidence_ids:
                raise EngineError("citation_required", "Supported or contradicted decisions need at least one retrieved citation.")
            if not isinstance(rationale, str) or not rationale.strip() or len(rationale) > 8000:
                raise EngineError("invalid_rationale", "Provide a nonempty rationale of at most 8000 characters.")
            decision = {"verdict": verdict, "evidence_ids": list(evidence_ids), "rationale": rationale.strip()}
            # Calculate before mutating; a broken reference cannot leave a half-completed session.
            feedback = self.evaluator.evaluate(session.case_id, decision, list(session.unavailable))
            session.decision = decision
            session.feedback = feedback
            session.status = "completed"
            self._event(session, "decision_submitted", session.auditor_role, f"Submitted {verdict} decision.")
            return self._state(session)

    def step(self, session_id: str) -> dict:
        from .policies import next_action

        with self._lock:
            session = self._active(session_id)
            # Policies receive a deep copy of public state, never store or evaluator access.
            action = next_action(self._state(session))
            if action["type"] == "request":
                return self.request(session_id, action["evidence_id"])
            return self.decide(session_id, action["verdict"], action["evidence_ids"], action["rationale"])

    def report(self, session_id: str) -> dict:
        with self._lock:
            session = self._get(session_id)
            if session.status != "completed":
                raise EngineError("report_not_ready", "Submit a decision before exporting the debrief report.", 409)
            state = self._state(session)
            return {
                "report_schema_version": "0.1.0",
                "mode": "offline_scripted_synthetic_demo",
                "notice": "Training/simulation artifact only. Not a GMP determination, CAPA approval, or batch-release decision.",
                **state,
                "evidence_checklist": [{
                    **item,
                    "outcome": ("received" if any(record["id"] == item["id"] for record in session.evidence)
                                else "unavailable" if item["id"] in session.unavailable else "not_requested"),
                } for item in state["catalog"]],
                "source_trace": [{"evidence_id": record["id"], "revision": record["revision"],
                                  "date": record["date"], "owner": record["owner"],
                                  "locator": f"fixture:{session.case_id}/{record['id']}"}
                                 for record in session.evidence],
            }

    def _get(self, session_id: str) -> Session:
        if not isinstance(session_id, str) or session_id not in self._sessions:
            raise EngineError("unknown_session", "Session does not exist in this server process.", 404)
        return self._sessions[session_id]

    def _active(self, session_id: str) -> Session:
        session = self._get(session_id)
        if session.status != "active":
            raise EngineError("session_completed", "This session is complete. Start a new session to try again.", 409)
        return session

    @staticmethod
    def _event(session: Session, event_type: str, role: str, message: str, **fields: Any) -> None:
        session.events.append({"seq": len(session.events) + 1, "type": event_type, "role": role,
                               "message": message, **fields})

    def _state(self, session: Session) -> dict:
        return deepcopy({
            "session_id": session.session_id,
            "case": self.store.public_case(session.case_id),
            "auditor_role": session.auditor_role,
            "status": session.status,
            "budget": {"total": session.budget_total, "spent": session.budget_spent,
                       "remaining": session.budget_total - session.budget_spent},
            "catalog": [{**item, "requested": item["id"] in session.requested}
                        for item in self.store.catalog(session.case_id)],
            "evidence": session.evidence,
            "events": session.events,
            "decision": session.decision,
            "feedback": session.feedback,
        })


def report_markdown(report: dict) -> str:
    case = report["case"]
    feedback = report["feedback"]
    lines = [
        "# QA War Room — synthetic session report", "", report["notice"], "",
        f"## {case['id']} · {case['title']}", "", f"**Claim:** {case['claim']}", "",
        f"**As of:** {case['as_of']}  ", f"**Policy label:** {report['auditor_role']}  ",
        f"**Budget:** {report['budget']['spent']} / {report['budget']['total']} credits", "",
        "## Submitted decision", "", f"**Verdict:** {report['decision']['verdict']}", "",
        report["decision"]["rationale"], "",
        "**Citations:** " + (", ".join(report["decision"]["evidence_ids"]) or "None"), "",
        "## Fixture feedback", "", f"**Reference verdict:** {feedback['expected_verdict']}  ",
        f"**Verdict matches reference:** {feedback['verdict_correct']}  ",
        f"**Reference support set covered:** {feedback['evidence_support_complete']}", "",
        feedback["explanation"], "", feedback["limitations"], "",
        "## Record checklist", "", "| ID | Record | Revision | Date | Outcome | Credits |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report["evidence_checklist"]:
        title = str(item["title"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item['id']} | {title} | {item['revision']} | {item['date']} | {item['outcome']} | {item['cost']} |")
    lines.extend(["", "## Event replay", ""])
    for event in report["events"]:
        lines.append(f"{event['seq']}. **{event['role']}** — {event['message']}")
    lines.extend(["", "## Source trace", ""])
    for source in report["source_trace"]:
        lines.append(f"- `{source['locator']}` · revision {source['revision']} · {source['date']} · {source['owner']}")
    return "\n".join(lines) + "\n"
