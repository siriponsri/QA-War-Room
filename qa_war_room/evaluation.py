"""Fixture-based grading, kept separate from policies and public scenario state.

These labels and support sets were authored for synthetic engineering cases.
Set coverage is NOT a semantic entailment metric, domain validation, or evidence
of pharmaceutical safety. No model judge supplies the reference answers here.
"""

from __future__ import annotations

import json
from pathlib import Path


class ReferenceEvaluator:
    def __init__(self, directory: Path):
        self._references = json.loads((directory / "evaluator" / "gold.json").read_text(encoding="utf-8"))["cases"]

    def evaluate(self, case_id: str, decision: dict, requested_unavailable: list[str]) -> dict:
        reference = self._references[case_id]
        cited = set(decision["evidence_ids"])
        alternatives = [set(group) for group in reference["support_sets"]]
        required_unavailable = set(reference.get("required_unavailable_requests", []))
        availability_complete = required_unavailable <= set(requested_unavailable)
        reference_coverage = any(group <= cited for group in alternatives)
        nearest = min(alternatives, key=lambda group: (len(group - cited), sorted(group)))
        all_reference_ids = set().union(*alternatives)
        correct = decision["verdict"] == reference["verdict"]
        return {
            "expected_verdict": reference["verdict"],
            "verdict_correct": correct,
            "evidence_support_complete": reference_coverage and availability_complete,
            "decision_and_support_correct": correct and reference_coverage and availability_complete,
            "unsupported_citations": [],
            "citations_not_in_reference": sorted(cited - all_reference_ids),
            "missing_support": sorted(nearest - cited),
            "required_support_sets": reference["support_sets"],
            "requested_unavailable": requested_unavailable,
            "missing_unavailability_checks": sorted(required_unavailable - set(requested_unavailable)),
            "explanation": reference["explanation"],
            "limitations": (
                "Synthetic fixture feedback only. Evidence completeness is exact reference-set coverage, "
                "not a semantic entailment assessment. Extra contextual citations are not necessarily wrong. "
                "This does not establish GMP compliance, CAPA effectiveness in practice, or human learning gains."
            ),
        }

    def paired_groups(self) -> list[dict]:
        """Evaluation metadata, used only by the offline benchmark runner."""
        groups: dict[str, list[dict]] = {}
        for case_id, reference in self._references.items():
            groups.setdefault(reference["template_group"], []).append({
                "case_id": case_id,
                "reference_verdict": reference["verdict"],
            })
        return [{"template_group": group, "cases": cases} for group, cases in groups.items()]
