"""G4 input store and gold-free evidence acquisition. Source-workspace API only."""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path

from .native_data import file_hash, read_jsonl
from .pharma_authoring import PACK_VERSION
from .pharma_rules import VERDICTS, pointer

INPUT_FILES = {"public/cases.jsonl", "private/records.jsonl", "public/splits.json"}


class PharmaError(ValueError):
    pass


class PharmaStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.manifest = json.loads((self.directory / "PACK.json").read_text(encoding="utf-8"))
        if self.manifest["pack_version"] != PACK_VERSION or set(self.manifest["input_files"]) != INPUT_FILES:
            raise ValueError("Unsupported Manufacturing GMP input pack")
        if self.manifest["independent_review_completed"] is not False:
            raise ValueError("This draft schema cannot assert independent validation")
        for name in INPUT_FILES:
            entry, path = self.manifest["input_files"][name], self.directory / name
            if file_hash(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
                raise ValueError("Pharma input checksum mismatch: " + name)
        self._cases = {row["id"]: row for row in read_jsonl(self.directory / "public/cases.jsonl")}
        self._records = {row["id"]: row["records"] for row in read_jsonl(self.directory / "private/records.jsonl")}
        self.splits = json.loads((self.directory / "public/splits.json").read_text(encoding="utf-8"))
        if set(self._cases) != set(self._records):
            raise ValueError("Case/evidence IDs differ")
        seen, templates = set(), set()
        for group in self.splits["groups"]:
            if group["template_id"] in templates or group["split"] not in {"train", "dev", "test"}:
                raise ValueError("A construction template crosses partitions")
            templates.add(group["template_id"])
            for case_id in group["case_ids"]:
                if case_id in seen:
                    raise ValueError("Case appears in multiple split groups")
                seen.add(case_id)
                row = self._cases[case_id]
                if any(row[k] != group[k] for k in ("family_id", "template_id", "split")):
                    raise ValueError("Case family/template partition mismatch")
        if seen != set(self._cases):
            raise ValueError("Ungrouped Manufacturing GMP case")
        for case_id, case in self._cases.items():
            if set(case) != {"id", "family_id", "template_id", "split", "title", "dataset_version", "process", "scope", "as_of",
                             "sop_id", "budget", "claim", "review_status", "jurisdiction", "author_constraints"}:
                raise ValueError("Unexpected case-card fields")
            date.fromisoformat(case["as_of"])
            if type(case["budget"]) is not int or case["budget"] < 0 or case["review_status"] != "author_draft_unreviewed":
                raise ValueError("Invalid draft case status/budget")
            ids = set()
            for record in self._records[case_id]:
                if (set(record) != {"id", "cost", "title", "document_type", "available", "document", "unavailable_reason"} or
                        record["id"] in ids or type(record["cost"]) is not int or record["cost"] < 1 or type(record["available"]) is not bool):
                    raise ValueError("Invalid private evidence entry")
                ids.add(record["id"])
                if not record["available"]:
                    if record["document"] is not None or not isinstance(record["unavailable_reason"], str) or not record["unavailable_reason"]:
                        raise ValueError("Unavailable source must not contain a hidden answer-bearing payload")
                    continue
                doc = record["document"]
                if (not isinstance(doc, dict) or set(doc) != {"id", "document_type", "owner", "revision", "recorded_at", "effective_from",
                        "approval_status", "scope", "facts", "content"} or doc["id"] != record["id"] or
                        doc["document_type"] != record["document_type"]):
                    raise ValueError("Invalid source document")
                for key in ("recorded_at", "effective_from"):
                    date.fromisoformat(doc[key])
                if doc["content"] != "FICTIONAL SITE RECORD\n" + json.dumps(doc["facts"], ensure_ascii=False, indent=2, sort_keys=True):
                    raise ValueError("Narrative/structured facts drift")
            if ids != {f"D{i}" for i in range(1, 8)}:
                raise ValueError("Incomplete fixed document inventory")

    def case_ids(self):
        return tuple(self._cases)

    def card(self, case_id):
        if not isinstance(case_id, str) or case_id not in self._cases:
            raise PharmaError("unknown_case")
        return deepcopy(self._cases[case_id])

    def catalog(self, case_id):
        self.card(case_id)
        return [{key: record[key] for key in ("id", "cost", "title", "document_type")} for record in self._records[case_id]]

    def record(self, case_id, record_id):
        self.card(case_id)
        for record in self._records[case_id]:
            if record["id"] == record_id:
                return deepcopy(record)
        raise PharmaError("unknown_record")


class PharmaEngine:
    def __init__(self, store, case_id, *, credits=None, max_source_bytes=200_000):
        self._store, self._card = store, store.card(case_id)
        self._total = self._card["budget"] if credits is None else credits
        if any(type(n) is not int or n < 0 for n in (self._total, max_source_bytes)):
            raise ValueError("Use nonnegative integer budgets")
        self._max_bytes, self._bytes, self._spent = max_source_bytes, 0, 0
        self._evidence, self._responses, self._decision = [], [], None

    def observation(self):
        public = {key: self._card[key] for key in ("id", "title", "claim", "process", "scope", "as_of", "sop_id", "dataset_version", "review_status", "author_constraints")}
        return deepcopy({"mode": "original_synthetic_manufacturing_gmp", "case": public,
                         "status": "completed" if self._decision else "active",
                         "budget": {"total": self._total, "spent": self._spent, "remaining": self._total - self._spent,
                                    "source_bytes_exposed": self._bytes, "max_source_bytes": self._max_bytes},
                         "catalog": [{**row, "requested": any(r["record_id"] == row["id"] for r in self._responses)}
                                     for row in self._store.catalog(self._card["id"])],
                         "responses": self._responses, "evidence": self._evidence, "decision": self._decision})

    def apply(self, action):
        if self._decision:
            raise PharmaError("case_completed")
        if not isinstance(action, dict) or not isinstance(action.get("type"), str):
            raise PharmaError("action_object_required")
        kind = action["type"]
        if kind == "request":
            if set(action) != {"type", "record_id"} or not isinstance(action["record_id"], str):
                raise PharmaError("invalid_request_fields")
            record = self._store.record(self._card["id"], action["record_id"])
            if any(r["record_id"] == record["id"] for r in self._responses):
                return self.observation()
            if self._spent + record["cost"] > self._total:
                raise PharmaError("budget_exceeded")
            self._spent += record["cost"]
            status = "source_unavailable"
            if record["available"]:
                size = len(json.dumps(record["document"], ensure_ascii=False, sort_keys=True).encode("utf-8"))
                status = "delivered" if self._bytes + size <= self._max_bytes else "exposure_cap_not_delivered"
                if status == "delivered":
                    self._evidence.append(record["document"])
                    self._bytes += size
            self._responses.append({"record_id": record["id"], "status": status, "cost": record["cost"],
                                    "message": record["unavailable_reason"] if status == "source_unavailable" else status})
            return self.observation()
        if kind == "abstain":
            if set(action) != {"type", "reason"}:
                raise PharmaError("invalid_abstain_fields")
            note = action["reason"]
        elif kind == "submit":
            if set(action) != {"type", "verdict", "citations", "rationale"} or action["verdict"] not in VERDICTS:
                raise PharmaError("invalid_submission_fields")
            citations, seen = action["citations"], set()
            if not isinstance(citations, list) or len(citations) > 40:
                raise PharmaError("invalid_citations")
            index = {row["id"]: row for row in self._evidence}
            for citation in citations:
                if (not isinstance(citation, dict) or set(citation) != {"record_id", "pointer"} or
                        not isinstance(citation["record_id"], str) or not isinstance(citation["pointer"], str)):
                    raise PharmaError("invalid_citation_schema")
                identity = (citation["record_id"], citation["pointer"])
                if identity in seen or citation["record_id"] not in index:
                    raise PharmaError("duplicate_or_unretrieved_citation")
                try:
                    pointer(index[citation["record_id"]], citation["pointer"])
                except (KeyError, IndexError, TypeError, ValueError) as error:
                    raise PharmaError("citation_pointer_not_found") from error
                seen.add(identity)
            if action["verdict"] != "insufficient" and not citations:
                raise PharmaError("citation_required")
            note = action["rationale"]
        else:
            raise PharmaError("unknown_action")
        if not isinstance(note, str) or not note.strip() or len(note) > 8000:
            raise PharmaError("invalid_terminal_reason")
        self._decision = deepcopy(action)
        return self.observation()
