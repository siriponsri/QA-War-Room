"""Hand-checkable metric fixtures and evaluation-invalidating boundary tests."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from qa_war_room.models import ModelResponse, OfflineAdapter, Usage, validate_prediction
from qa_war_room.native_data import build_request, file_hash, lexical_scores, load_inputs
from qa_war_room.native_metrics import contractnli_metrics, drugqa_metrics, ranked_metrics
from qa_war_room.native_runner import Caps, run_native, score_run


def fixture(root):
    """Tiny original data; never use real benchmark answers as prompt examples."""
    records = {
        "contractnli/dev.documents.jsonl": [
            {"id": "doc1", "text": "Keep records. No sharing.", "spans": [[0, 13], [14, 25]]},
            {"id": "doc2", "text": "Review completed.", "spans": [[0, 17]]}],
        "contractnli/dev.tasks.jsonl": [
            {"id": "doc1:h1", "document_id": "doc1", "hypothesis_id": "h1", "hypothesis": "Keep records."},
            {"id": "doc1:h2", "document_id": "doc1", "hypothesis_id": "h2", "hypothesis": "Share records."},
            {"id": "doc2:h1", "document_id": "doc2", "hypothesis_id": "h1", "hypothesis": "Keep records."}],
        "evaluator/contractnli/dev.gold.jsonl": [
            {"id": "doc1:h1", "label": "Entailment", "evidence_span_ids": [0]},
            {"id": "doc1:h2", "label": "Contradiction", "evidence_span_ids": [1]},
            {"id": "doc2:h1", "label": "NotMentioned", "evidence_span_ids": []}],
        "drugqa/all.inputs.jsonl": [{"id": "mcq1", "question": "Question {options} 中文?", "choices":
            ["A. One", "B. Two", "C. Three", "D. Four"], "language": "CN"}],
        "evaluator/drugqa/all.gold.jsonl": [{"id": "mcq1", "answer": "C", "explanation": "SECRET_RATIONALE",
            "language": "CN", "task_type": "Monolingual", "category": "Drugs", "final_quality": "pass"}],
    }
    hashes = {}
    for name, rows in records.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        hashes[name] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
    (root / "PREPARATION_REPORT.json").write_text(json.dumps({"source_commits": {"fixture": "original-v1"},
                                                           "prepared_files": hashes}), encoding="utf-8")


class SpyAdapter(OfflineAdapter):
    def __init__(self, behavior="ok", bound=None, actual=None):
        self.requests = []
        self.behavior = behavior
        self.bound = bound or Usage()
        self.actual = actual or self.bound

    def upper_bound(self, request, max_output_tokens):
        return self.bound

    def predict(self, request, max_output_tokens):
        self.requests.append(request)
        if self.behavior == "interrupt":
            raise KeyboardInterrupt()
        if self.behavior == "error":
            raise RuntimeError("SECRET_API_KEY must never enter logs")
        if self.behavior == "invalid":
            return ModelResponse('{"label":"invented"}', self.actual)
        response = super().predict(request, max_output_tokens)
        return ModelResponse(response.raw, self.actual)


class NativeMetricTests(unittest.TestCase):
    def test_ranked_ap_and_p80_group_ties(self):
        metrics = ranked_metrics([(0.9, True), (0.9, False), (0.1, True)])
        self.assertAlmostEqual(metrics["map"], (0.5 + 2 / 3) / 2)
        self.assertAlmostEqual(metrics["precision@recall80"], 2 / 3)
        self.assertIsNone(ranked_metrics([(1, False)])["map"])

    def test_nli_averages_hypotheses_not_class_labels(self):
        rows = [{"id": str(i), "hypothesis_id": "h1" if i < 3 else "h2",
                 "label": "NotMentioned", "evidence_span_ids": [], "span_count": 1} for i in range(4)]
        predictions = {str(i): {"label": "NotMentioned", "span_scores": {"0": 0}} for i in range(3)}
        result = contractnli_metrics(rows, predictions)
        self.assertEqual(result["micro_label_micro_doc"]["class"]["accuracy"], 0.75)
        self.assertEqual(result["macro_label_micro_doc"]["class"]["accuracy"], 0.5)
        self.assertIsNone(result["macro_label_micro_doc"]["class"]["f1_contradiction"])
        self.assertEqual(result["invalid_or_missing"], 1)

    def test_nli_evidence_native_excludes_notmentioned_and_keeps_failures_visible(self):
        rows = [{"id": "a", "hypothesis_id": "h1", "label": "Entailment", "evidence_span_ids": [1], "span_count": 2},
                {"id": "b", "hypothesis_id": "h1", "label": "NotMentioned", "evidence_span_ids": [], "span_count": 2}]
        predictions = {"a": {"label": "NotMentioned", "span_scores": {"0": 0, "1": 1}},
                       "b": {"label": "NotMentioned", "span_scores": {"0": 1, "1": 1}}}
        result = contractnli_metrics(rows, predictions)
        self.assertEqual(result["micro_label_macro_doc"]["span"]["map"], 1)
        result = contractnli_metrics(rows, {})
        self.assertIsNone(result["micro_label_macro_doc"]["span"])
        self.assertEqual(result["failure_diagnostics"]["map_with_failed_items_scored_zero"], 0)

    def test_drugqa_fixed_denominator_strata_and_wilson(self):
        rows = [{"id": str(i), "answer": "A", "task_type": "Parallel", "language": "EN" if i else "CN",
                 "final_quality": "pass", "category": "Drugs"} for i in range(4)]
        result = drugqa_metrics(rows, {"0": {"answer": "A"}, "1": {"answer": "B"}})
        self.assertEqual(result["overall"]["accuracy"], 0.25)
        self.assertEqual(result["overall"]["invalid"], 2)
        self.assertEqual(result["overall"]["valid_output_coverage"], 0.5)
        self.assertAlmostEqual(result["overall"]["wilson_95_ci"][0], 0.0455872608)
        self.assertEqual(result["task_x_language"]["Parallel/CN"]["n"], 1)
        self.assertNotIn("by_functional_subdomain", result)


class NativeRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        fixture(self.data)
        self.output = self.root / "run"

    def run_fixture(self, **kwargs):
        return run_native(self.data, "contractnli", "dev", self.output, limit=2, **kwargs)

    def test_original_document_limit_keeps_all_hypotheses(self):
        result = run_native(self.data, "contractnli", "dev", self.output, limit=1)
        self.assertEqual(result["cohort_size"], 2)
        self.assertEqual(result["finished"], 2)

    def test_run_never_opens_gold_or_passes_it_to_adapter(self):
        original_open = Path.open
        def guarded(path, *args, **kwargs):
            if "evaluator" in path.parts:
                raise AssertionError("Gold opened during inference")
            return original_open(path, *args, **kwargs)
        spy = SpyAdapter()
        with patch.object(Path, "open", guarded):
            result = self.run_fixture(adapter=spy)
        self.assertEqual(result["successful"], 3)
        self.assertEqual(set(spy.requests[0]), {"id", "dataset", "visible_span_ids", "messages"})
        serialized = json.dumps(spy.requests)
        self.assertNotIn("evidence_span_ids\": [0]", serialized)
        self.assertNotIn("gold", serialized)
        self.assertFalse((self.output / "metrics.json").exists())
        report = score_run(self.data, self.output)
        self.assertFalse(report["scientific_performance_claim"])
        self.assertEqual(report["cohort_size"], 3)

    def test_resume_is_idempotent_and_rejects_changed_caps(self):
        spy = SpyAdapter()
        self.run_fixture(adapter=spy, stop_after=1)
        self.assertEqual(len(spy.requests), 1)
        result = self.run_fixture(adapter=spy, resume=True)
        self.assertEqual(result["finished"], 3)
        self.assertEqual(len(spy.requests), 3)
        self.run_fixture(adapter=spy, resume=True)
        self.assertEqual(len(spy.requests), 3)
        with self.assertRaisesRegex(ValueError, "differ"):
            self.run_fixture(resume=True, caps=Caps(max_calls=99))

    def test_existing_output_is_never_overwritten(self):
        self.run_fixture()
        before = (self.output / "events.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "exists"):
            self.run_fixture()
        self.assertEqual(before, (self.output / "events.jsonl").read_bytes())

    def test_call_cap_is_checked_before_adapter(self):
        spy = SpyAdapter()
        result = self.run_fixture(adapter=spy, caps=Caps(max_calls=1))
        self.assertEqual(len(spy.requests), 1)
        self.assertEqual(result["status"], "budget_stopped")
        self.assertEqual(score_run(self.data, self.output)["cohort_size"], 3)
        self.run_fixture(adapter=spy, caps=Caps(max_calls=1), resume=True)
        self.assertEqual(len(spy.requests), 1)

    def test_token_and_cost_caps_reserve_before_calls(self):
        for name, bound, caps in [
            ("input", Usage(4, 0), Caps(max_input_tokens=3)),
            ("output", Usage(0, 4), Caps(max_output_tokens=3)),
            ("cost", Usage(0, 0, "0.02"), Caps(max_cost_usd="0.01", max_item_cost_usd="0.02"))]:
            spy = SpyAdapter(bound=bound)
            self.output = self.root / name
            result = self.run_fixture(adapter=spy, caps=caps)
            self.assertEqual(result["status"], "budget_stopped")
            self.assertEqual(spy.requests, [])

    def test_failure_costs_are_retained_and_exceptions_redacted(self):
        spy = SpyAdapter("error", Usage(3, 2))
        result = self.run_fixture(adapter=spy)
        self.assertEqual(result["usage"]["input_tokens"], 9)
        self.assertEqual(result["usage"]["output_tokens"], 6)
        self.assertNotIn("SECRET_API_KEY", (self.output / "events.jsonl").read_text())
        self.assertEqual(score_run(self.data, self.output)["statuses"], {"provider_error": 3})

    def test_interrupted_reservation_is_charged_and_not_retried(self):
        spy = SpyAdapter("interrupt", Usage(3, 2))
        with self.assertRaises(KeyboardInterrupt):
            self.run_fixture(adapter=spy)
        spy.behavior = "ok"
        result = self.run_fixture(adapter=spy, resume=True)
        self.assertEqual(len(spy.requests), 3)
        self.assertEqual(result["usage"]["calls"], 3)
        self.assertEqual(result["usage"]["input_tokens"], 9)
        self.assertIn("interrupted_unknown_usage", score_run(self.data, self.output)["statuses"])

    def test_invalid_output_is_logged_and_not_repaired_for_free(self):
        result = self.run_fixture(adapter=SpyAdapter("invalid"))
        self.assertEqual(result["successful"], 0)
        report = score_run(self.data, self.output)
        self.assertEqual(report["statuses"], {"invalid_output": 3})
        self.assertEqual(report["metrics"]["invalid_or_missing"], 3)

    def test_usage_bound_violation_halts_and_cannot_resume_more_calls(self):
        spy = SpyAdapter(bound=Usage(1, 1), actual=Usage(2, 1))
        result = self.run_fixture(adapter=spy)
        self.assertEqual(result["status"], "usage_bound_violation")
        self.run_fixture(adapter=spy, resume=True)
        self.assertEqual(len(spy.requests), 1)
        self.assertEqual(result["usage"]["input_tokens"], 2)

    def test_context_overflow_fails_without_silent_truncation(self):
        spy = SpyAdapter()
        result = self.run_fixture(adapter=spy, caps=Caps(max_item_input_bytes=1))
        self.assertEqual(spy.requests, [])
        self.assertEqual(result["finished"], 3)
        self.assertEqual(score_run(self.data, self.output)["statuses"], {"context_limit": 3})

    def test_nonoffline_provider_is_refused_without_calls(self):
        class PaidIdentity(SpyAdapter):
            def identity(self):
                return {"provider": "paid", "llm": True}
        spy = PaidIdentity()
        with self.assertRaisesRegex(ValueError, "Only offline"):
            self.run_fixture(adapter=spy)
        self.assertEqual(spy.requests, [])

    def test_per_item_usage_bound_is_checked_before_calls(self):
        spy = SpyAdapter(bound=Usage(0, 1025))
        with self.assertRaisesRegex(ValueError, "per-item"):
            self.run_fixture(adapter=spy)
        self.assertEqual(spy.requests, [])

    def test_ledger_tamper_and_torn_tail_are_detected(self):
        self.run_fixture()
        log = self.output / "events.jsonl"
        original = log.read_bytes()
        log.write_bytes(original[:-2])
        with self.assertRaisesRegex(ValueError, "Torn"):
            self.run_fixture(resume=True)
        log.write_bytes(original.replace(b'attempt_started', b'attempt_changed', 1))
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.run_fixture(resume=True)

    def test_scoring_refuses_changed_gold(self):
        self.run_fixture()
        gold = self.data / "evaluator/contractnli/dev.gold.jsonl"
        gold.write_text(gold.read_text().replace("Entailment", "Contradiction"))
        with self.assertRaisesRegex(ValueError, "checksum"):
            score_run(self.data, self.output)

    def test_ledger_from_another_baseline_cannot_be_scored(self):
        self.run_fixture()
        other = self.root / "retrieval"
        run_native(self.data, "contractnli", "dev", other, limit=2, baseline="lexical-retrieval")
        (other / "events.jsonl").write_bytes((self.output / "events.jsonl").read_bytes())
        with self.assertRaisesRegex(ValueError, "different frozen run"):
            score_run(self.data, other)

    def test_changed_input_or_preparation_cannot_resume(self):
        self.run_fixture(stop_after=1)
        path = self.data / "contractnli/dev.tasks.jsonl"
        path.write_text(path.read_text().replace("Keep records.", "Delete records."))
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.run_fixture(resume=True)

    def test_writer_lock_refuses_concurrent_run(self):
        self.run_fixture()
        lock = self.output / ".writer.lock"
        lock.write_text('{"pid":0}')
        with self.assertRaisesRegex(ValueError, "locked"):
            self.run_fixture(resume=True)
        self.assertTrue(lock.exists())

    def test_retrieval_exposes_only_selected_original_spans(self):
        observations, _ = load_inputs(self.data, "contractnli", "dev")
        request = build_request(observations[0], "contractnli", "lexical-retrieval", 1)
        content = json.loads(request["messages"][1]["content"])
        self.assertNotIn("document", content)
        self.assertEqual(content["spans"][0]["text"], "Keep records.")
        self.assertEqual(request["visible_span_ids"], [0])
        self.assertEqual(lexical_scores("records", ["records", "unrelated"])[1], 0)
        bad = {"label": "Entailment", "evidence_span_ids": [1], "span_scores": {"0": 0.8}}
        with self.assertRaisesRegex(ValueError, "visible"):
            validate_prediction(json.dumps(bad), request)

    def test_schema_rejects_nan_duplicate_fields_and_unknown_fields(self):
        observations, _ = load_inputs(self.data, "contractnli", "dev")
        request = build_request(observations[2], "contractnli", "full-context", 1)
        for raw in ['{"label":"NotMentioned","evidence_span_ids":[],"span_scores":{"0":NaN}}',
                    '{"label":"NotMentioned","label":"Entailment","evidence_span_ids":[],"span_scores":{"0":0}}',
                    '{"label":"NotMentioned","evidence_span_ids":[],"span_scores":{"0":0},"gold":"secret"}']:
            with self.assertRaises(ValueError):
                validate_prediction(raw, request)

    def test_drugqa_prompt_preserves_question_and_existing_choice_prefixes(self):
        rows, _ = load_inputs(self.data, "drugqa", "all")
        request = build_request(rows[0], "drugqa", "full-context", 1,
                                ("Synthetic test instruction", "{question}\n{options}"))
        user = request["messages"][1]["content"]
        self.assertTrue(user.startswith("Question {options} 中文?"))
        self.assertIn("A. One\nB. Two", user)
        self.assertNotIn("A. A.", user)
        self.assertNotIn("SECRET_RATIONALE", json.dumps(request))
        for raw in ['{"selected_answer":"c"}', '```json\n{"predicted_answer":"C"}\n```', 'C']:
            self.assertEqual(validate_prediction(raw, request), {"answer": "C"})
        with self.assertRaises(ValueError):
            validate_prediction("unmapped", request)
        with self.assertRaises(ValueError):
            load_inputs(self.data, "drugqa", "dev")


if __name__ == "__main__":
    unittest.main()
