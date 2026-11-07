"""Strict, gold-free request/submit/abstain state machine for the derived task."""

from __future__ import annotations

from copy import deepcopy

from .native_data import NLI_LABELS
from .sequential_data import TASK_VERSION, SequentialStore


class SequentialError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def fields(value: dict, expected: set[str]):
    if set(value) != expected:
        raise SequentialError("invalid_action_fields")


class SequentialEngine:
    def __init__(self, store: SequentialStore, episode_id: str, credits: int, max_source_bytes: int = 2_000_000):
        if any(type(n) is not int or n < 0 for n in (credits, max_source_bytes)):
            raise ValueError("Acquisition budgets must be nonnegative integers")
        self._store = store
        self._episode = store.episode(episode_id)
        self._catalog = store.catalog(episode_id)
        self._credits = credits
        self._max_bytes = max_source_bytes
        self._spent = 0
        self._source_bytes = 0
        self._responses = []
        self._evidence = []
        self._decision = None
        self._status = "active"

    def observation(self) -> dict:
        return deepcopy({
            "task_version": TASK_VERSION, "track": "derived_sequential_not_native_score",
            "episode_id": self._episode["id"], "source_id": self._episode["source_id"],
            "hypothesis": self._episode["hypothesis"], "assessment_date": None,
            "status": self._status,
            "budget": {"credits_total": self._credits, "credits_spent": self._spent,
                       "credits_remaining": self._credits - self._spent,
                       "source_bytes_exposed": self._source_bytes, "max_source_bytes": self._max_bytes},
            "catalog": [{**item, "requested": any(r["record_id"] == item["id"] for r in self._responses)}
                        for item in self._catalog],
            "responses": self._responses, "evidence": self._evidence, "decision": self._decision,
            "available_actions": ["request", "submit", "abstain"] if self._status == "active" else [],
            "policy": "Only requested source text is visible. No hidden-text search. NotMentioned is a source label, not abstention.",
        })

    def apply(self, action: dict) -> dict:
        if self._status != "active":
            raise SequentialError("episode_completed")
        if not isinstance(action, dict) or not isinstance(action.get("type"), str):
            raise SequentialError("action_object_required")
        kind = action["type"]
        if kind == "request":
            fields(action, {"type", "record_id"})
            record_id = action["record_id"]
            if not isinstance(record_id, str) or record_id not in {r["id"] for r in self._catalog}:
                raise SequentialError("unknown_record")
            if any(r["record_id"] == record_id for r in self._responses):
                return self.observation()  # Exact idempotence, including failed delivery.
            if self._spent >= self._credits:
                raise SequentialError("credits_exhausted")
            record = self._store.record(self._episode["id"], record_id)
            size = len(record["text"].encode("utf-8"))
            self._spent += 1
            delivered = self._source_bytes + size <= self._max_bytes
            self._responses.append({"record_id": record_id, "cost": 1,
                                    "status": "delivered" if delivered else "exposure_cap_not_delivered"})
            if delivered:
                self._source_bytes += size
                # Provenance is delivered with the acquired record, never catalogued for free.
                record["provenance"] = {"dataset": "ContractNLI", "source_id": self._episode["source_id"],
                                        "original_split": self._episode["original_split"],
                                        "source_commits": self._store.manifest["source_commits"]}
                self._evidence.append(record)
            return self.observation()
        if kind == "submit":
            fields(action, {"type", "label", "citation_span_ids", "rationale"})
            if not isinstance(action["label"], str) or action["label"] not in NLI_LABELS:
                raise SequentialError("invalid_native_label")
            citations = action["citation_span_ids"]
            visible = {s["id"] for record in self._evidence for s in record["spans"]}
            if (not isinstance(citations, list) or len(citations) > 10_000 or
                    any(type(i) is not int for i in citations) or len(citations) != len(set(citations)) or
                    not set(citations) <= visible):
                raise SequentialError("citation_not_unique_visible_span")
            if action["label"] != "NotMentioned" and not citations:
                raise SequentialError("citation_required")
            note = action["rationale"]
        elif kind == "abstain":
            fields(action, {"type", "forced_label", "reason"})
            if not isinstance(action["forced_label"], str) or action["forced_label"] not in NLI_LABELS:
                raise SequentialError("invalid_forced_native_label")
            note = action["reason"]
        else:
            raise SequentialError("unknown_action")
        if not isinstance(note, str) or not note.strip() or len(note) > 8000:
            raise SequentialError("invalid_terminal_reason")
        self._decision = deepcopy(action)
        self._status = "completed"
        return self.observation()

    def fail(self, reason: str) -> dict:
        """Runner-only terminal failure; never expose a fabricated forced prediction."""
        if self._status != "active":
            raise SequentialError("episode_completed")
        if reason not in {"episode_action_cap", "invalid_policy_action", "policy_error"}:
            raise SequentialError("invalid_runtime_failure")
        self._decision = {"type": "runtime_failure", "reason": reason, "forced_label": None}
        self._status = "failed"
        return self.observation()
