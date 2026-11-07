"""Read local fixtures without making them directly addressable by HTTP.

The repository is deliberately inspectable. This is runtime access separation,
not a security boundary against someone who can read the source repository.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import sys


ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
PUBLIC_CASE_FIELDS = (
    "id", "title", "brief", "claim", "as_of", "process", "protocol_id",
    "simulation_notice",
)
PUBLIC_CATALOG_FIELDS = (
    "id", "title", "document_type", "owner", "revision", "date", "cost",
)
PUBLIC_EVIDENCE_FIELDS = (
    "id", "title", "document_type", "owner", "revision", "date", "content", "facts",
)


def default_data_dir() -> Path:
    """Resolve either a source checkout or the optional installed distribution."""
    candidates = (
        Path(__file__).resolve().parent.parent / "data" / "demo",
        Path(sys.prefix) / "share" / "qa-war-room" / "demo",
    )
    for candidate in candidates:
        if (candidate / "scenarios.json").is_file():
            return candidate
    raise FileNotFoundError("Demo data not found. Run from the repository or pass --data-dir.")


class FixtureStore:
    """Scenario and evidence store; never reads evaluator gold."""

    def __init__(self, directory: Path | str | None = None):
        self.directory = Path(directory) if directory is not None else default_data_dir()
        scenarios = json.loads((self.directory / "scenarios.json").read_text(encoding="utf-8"))
        self._evidence = json.loads((self.directory / "evidence.json").read_text(encoding="utf-8"))
        self._cases: dict[str, dict] = {}
        for case in scenarios["cases"]:
            case_id = case["id"]
            if not ID_RE.fullmatch(case_id) or case_id in self._cases:
                raise ValueError("Invalid or duplicate case ID in fixture.")
            if not isinstance(case["budget"], int) or case["budget"] < 1:
                raise ValueError("Case budget must be a positive integer.")
            seen = set()
            for item in case["catalog"]:
                evidence_id = item["id"]
                if not ID_RE.fullmatch(evidence_id) or evidence_id in seen:
                    raise ValueError("Invalid or duplicate evidence ID in fixture.")
                seen.add(evidence_id)
                if type(item["cost"]) is not int or item["cost"] < 1:
                    raise ValueError("Evidence acquisition cost must be a positive integer.")
                if item["owner"] not in {"user-01", "user-02"}:
                    raise ValueError("Evidence owner must be a configured auditee.")
                for field in PUBLIC_CATALOG_FIELDS:
                    if field not in item:
                        raise ValueError(f"Missing catalog field: {field}")
                artifact = self._evidence[case_id][evidence_id]
                if type(artifact.get("available")) is not bool:
                    raise ValueError("Evidence availability must be boolean.")
                if artifact["available"]:
                    if not isinstance(artifact.get("content"), str) or not isinstance(artifact.get("facts"), dict):
                        raise ValueError("Available evidence needs text and structured source fields.")
            self._cases[case_id] = deepcopy(case)

    def list_cases(self) -> list[dict]:
        return [self.public_case(case_id) for case_id in self._cases]

    def public_case(self, case_id: str) -> dict:
        return deepcopy({key: self._cases[case_id][key] for key in PUBLIC_CASE_FIELDS})

    def case(self, case_id: str) -> dict:
        return deepcopy(self._cases[case_id])

    def catalog(self, case_id: str) -> list[dict]:
        return [deepcopy({key: item[key] for key in PUBLIC_CATALOG_FIELDS})
                for item in self._cases[case_id]["catalog"]]

    def evidence(self, case_id: str, evidence_id: str) -> dict:
        """Only the engine should invoke this after validating and charging a request."""
        item = next(item for item in self._cases[case_id]["catalog"] if item["id"] == evidence_id)
        artifact = self._evidence[case_id][evidence_id]
        if not artifact["available"]:
            return {"available": False, "reason": artifact.get("unavailable_reason", "Record unavailable.")}
        return {
            "available": True,
            "record": {
                **{key: deepcopy(item[key]) for key in PUBLIC_CATALOG_FIELDS if key != "cost"},
                "content": artifact["content"],
                "facts": deepcopy(artifact["facts"]),
            },
        }

    def __contains__(self, case_id: str) -> bool:
        return case_id in self._cases
