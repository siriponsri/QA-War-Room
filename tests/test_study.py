"""G5 leakage, prospective gates, frozen denominators, replay and paired arithmetic."""

from copy import deepcopy
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from qa_war_room.native_data import digest, file_hash, read_jsonl
from qa_war_room.native_runner import read_events, run_lock
from qa_war_room.pharma_authoring import prepare_inputs
from qa_war_room.pharma_engine import PharmaEngine, PharmaStore
from qa_war_room.pharma_eval import build_references
from qa_war_room.study_analysis import analyze_run, pair_diagnostics
from qa_war_room.study_metrics import (joint_guardrail_arithmetic, paired_bootstrap,
    paired_rows, quantile, summarize, validate_rows)
from qa_war_room.study_plan import load_lock, make_lock, validate_plan
from qa_war_room.study_policies import choose_action
from qa_war_room.study_runner import load_run, replay_matrix, run_matrix

ROOT = Path(__file__).resolve().parents[1]


def row(case, family, method, truth="insufficient", verdict=None, status=None, repetition=0):
    return {"case_id": case, "family_id": family, "method": method, "credits": 7, "repetition": repetition,
        "primary_eligible": truth is not None, "reference_label": truth, "verdict": verdict,
        "status": status or ("ok" if verdict else "abstain"), "evidence_proxy": False,
        "actions": 1, "source_bytes": 20, "acquisition_credits": 1, "wall_seconds": 0.01}


class StudyIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.pack = self.root / "pack"
        build_references(self.pack, prepare_inputs(self.pack))
        self.plan = json.loads((ROOT / "plans/g5-evaluation-plan-v1.json").read_text())
        self.plan["engineering"]["methods"] = ["sop-adaptive-v1", "sop-catalog-v1"]
        self.plan["engineering"]["budgets"] = [0, 7]
        self.plan_path = self.root / "plan.json"
        self.lock = self.root / "lock"
        self.run = self.root / "run"

    def freeze(self):
        self.plan_path.write_text(json.dumps(self.plan), encoding="utf-8")
        return make_lock(self.pack, self.plan_path, self.lock)

    def no_gold(self):
        original = Path.open
        def guard(path, *args, **kwargs):
            if "evaluator" in path.parts or "authoring" in path.parts:
                raise AssertionError("Gold/authoring accessed by actor path")
            return original(path, *args, **kwargs)
        return patch.object(Path, "open", guard)

    def test_input_only_lock_run_replay_and_evaluator_join(self):
        with self.no_gold():
            lock = self.freeze()
            summary = run_matrix(self.pack, self.lock, self.run)
            replay = replay_matrix(self.pack, self.lock, self.run)
        self.assertEqual((lock["cases"], lock["construction_families"], lock["jobs"]), (16, 2, 64))
        self.assertEqual(summary["terminal"], 64)
        self.assertFalse(replay["gold_read"])
        for path in (self.lock / "LOCK.json", self.run / "events.jsonl"):
            text = path.read_text()
            for forbidden in ("candidate_verdict", "declared_record_witness_sets", "anchor_candidate", "author_allowed_labels"):
                self.assertNotIn(forbidden, text)
        before = file_hash(self.run / "events.jsonl")
        with patch("qa_war_room.study_runner.choose_action", side_effect=AssertionError("Policy invoked during evaluation")):
            report = analyze_run(self.pack, self.lock, self.run, self.root / "analysis")
        self.assertEqual(report["jobs"], 64)
        self.assertEqual(before, file_hash(self.run / "events.jsonl"))
        tables = json.loads((self.root / "analysis/ENGINEERING_METRICS.json").read_text())["tables"]
        self.assertTrue(all(t["primary_episodes"] == 14 and t["ambiguous_separate_episodes"] == 2 for t in tables))
        with (self.root / "analysis/SCIENTIFIC_TABLE_TEMPLATE.csv").open(encoding="utf-8") as handle:
            scientific = list(csv.DictReader(handle))
        self.assertTrue(all(r["status"] == "NOT_RUN" and r["estimate"] == "" for r in scientific))

    def test_confirmatory_request_refused_even_when_fields_filled(self):
        for key in ("reviewed_reference_release_sha256", "independent_review_record_sha256", "adjudication_record_sha256",
                    "sample_size_justification_sha256", "model_revision", "prompt_bundle_sha256"):
            self.plan[key] = "unverified-user-string"
        self.plan["scientific_comparison"] = {"candidate": "a", "comparator": "b"}
        self.plan["guardrails"] = {key: 0.1 for key in self.plan["guardrails"]}
        self.plan_path.write_text(json.dumps(self.plan))
        with self.no_gold():
            result = make_lock(self.pack, self.plan_path, self.lock, mode="confirmatory")
        self.assertEqual(result["status"], "REFUSED")
        self.assertTrue(result["not_a_study_lock"])
        self.assertFalse((self.lock / "LOCK.json").exists())
        self.assertTrue(any("author-draft only" in s for s in result["reasons"]))

    def test_offline_plan_rejects_paid_cost_retry_and_invalid_schedules(self):
        mutations = [("provider", "paid"), ("max_cost_usd", "1"), ("max_cost_usd", "NaN"), ("retry_limit", 1),
            ("retry_limit", False), ("budgets", [True]), ("budgets", [1, 1]), ("methods", ["oracle"]),
            ("max_jobs", 10001), ("repetitions", 0), ("max_policy_actions", -1)]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                plan = deepcopy(self.plan)
                plan["engineering"][key] = value
                with self.assertRaises((ValueError, ArithmeticError)):
                    validate_plan(plan)
        for value in (True, -1, float("nan"), 2):
            plan = deepcopy(self.plan)
            plan["guardrails"]["minimum_coverage"] = value
            with self.assertRaises(ValueError):
                validate_plan(plan)

    def test_missing_jobs_or_families_rejected_even_if_lock_rehashed(self):
        self.freeze()
        original = json.loads((self.lock / "LOCK.json").read_text())
        for key in ("jobs", "cohort"):
            record = deepcopy(original)
            record["config"][key].pop()
            record["config_sha256"] = digest(record["config"])
            (self.lock / "LOCK.json").write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "matrix mismatch"):
                load_lock(self.pack, self.lock)

    def test_implementation_drift_and_output_overwrite_refused(self):
        self.freeze()
        with self.assertRaises(ValueError):
            self.freeze()
        with patch("qa_war_room.study_plan.code_hashes", return_value={}):
            with self.assertRaisesRegex(ValueError, "implementation changed"):
                run_matrix(self.pack, self.lock, self.run)

    def test_shared_serializer_drift_invalidates_lock(self):
        self.freeze()
        original = file_hash
        def changed(path):
            return "changed-shared-serializer" if path.name == "sequential_data.py" else original(path)
        with patch("qa_war_room.study_plan.file_hash", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "implementation changed"):
                load_lock(self.pack, self.lock)

    def test_checkpoint_resume_matches_uninterrupted_and_is_idempotent(self):
        self.freeze()
        checkpoint = run_matrix(self.pack, self.lock, self.run, stop_after=5)
        self.assertEqual(checkpoint["transitions"], 5)
        final = run_matrix(self.pack, self.lock, self.run, resume=True)
        other = self.root / "uninterrupted"
        uninterrupted = run_matrix(self.pack, self.lock, other)
        for key in ("terminal", "pending", "policy_actions", "transitions", "runtime_failures"):
            self.assertEqual(final[key], uninterrupted[key])
        a, b = read_events(self.run / "events.jsonl"), read_events(other / "events.jsonl")
        self.assertEqual([(e["key"], e["action"], e["observation"]) for e in a], [(e["key"], e["action"], e["observation"]) for e in b])
        frozen = file_hash(self.run / "events.jsonl")
        run_matrix(self.pack, self.lock, self.run, resume=True)
        self.assertEqual(frozen, file_hash(self.run / "events.jsonl"))

    def test_global_cap_preserves_unstarted_jobs_in_all_denominators(self):
        self.plan["engineering"]["max_policy_actions"] = 1
        self.freeze()
        result = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual((result["policy_actions"], result["pending"]), (1, 63))
        analyze_run(self.pack, self.lock, self.run, self.root / "analysis")
        rows = read_jsonl(self.root / "analysis/evaluator/outcomes.jsonl")
        self.assertEqual(len(rows), 64)
        self.assertEqual(sum(r["primary_eligible"] for r in rows), 56)
        self.assertEqual(sum(r["status"] == "pending" for r in rows), 63)

    def test_per_job_cap_bounds_duplicate_request_loops(self):
        self.plan["engineering"]["budgets"] = [7]
        self.plan["engineering"]["max_actions_per_job"] = 2
        self.freeze()
        with patch("qa_war_room.study_runner.choose_action", return_value={"type": "request", "record_id": "D1"}):
            result = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual(result["runtime_failures"], {"action_cap": 32})
        self.assertEqual(result["policy_actions"], 64)
        self.assertEqual(result["transitions"], 96)
        replay_matrix(self.pack, self.lock, self.run)
        _, _, _, engines, _, _, _ = load_run(self.pack, self.lock, self.run)
        self.assertTrue(all(e.observation()["budget"]["spent"] == 1 for e in engines.values()))

    def test_invalid_policy_actions_count_once_and_are_not_repaired(self):
        self.freeze()
        with patch("qa_war_room.study_runner.choose_action", return_value={"type": "reveal_gold"}):
            result = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual(result["runtime_failures"], {"invalid_action": 64})
        self.assertEqual(result["policy_actions"], 64)
        replay_matrix(self.pack, self.lock, self.run)
        analyze_run(self.pack, self.lock, self.run, self.root / "analysis")
        rows = read_jsonl(self.root / "analysis/evaluator/outcomes.jsonl")
        self.assertEqual(summarize(rows)["coverage"]["value"], 0)
        self.assertEqual(summarize(rows)["primary_episodes"], 56)

    def test_policy_exception_does_not_log_secret_exception_text(self):
        self.plan["engineering"]["max_policy_actions"] = 1
        self.freeze()
        with patch("qa_war_room.study_runner.choose_action", side_effect=RuntimeError("SENSITIVE EXCEPTION TEXT")):
            run_matrix(self.pack, self.lock, self.run)
        self.assertNotIn("SENSITIVE", (self.run / "events.jsonl").read_text())
        self.assertEqual(read_events(self.run / "events.jsonl")[0]["error_code"], "RuntimeError")
        replay_matrix(self.pack, self.lock, self.run)

    def test_oversized_and_nonserializable_actions_are_bounded(self):
        for name, action, error in (("huge", {"type": "abstain", "reason": "x" * 17000}, "action_too_large"),
                                    ("object", object(), "invalid_serialization")):
            self.plan["engineering"]["max_policy_actions"] = 1
            self.lock = self.root / (name + "-lock")
            self.freeze()
            destination = self.root / name
            with patch("qa_war_room.study_runner.choose_action", return_value=action):
                run_matrix(self.pack, self.lock, destination)
            event = read_events(destination / "events.jsonl")[0]
            self.assertIsNone(event["action"])
            self.assertEqual(event["error_code"], error)
            replay_matrix(self.pack, self.lock, destination)

    def test_nonstring_submission_label_is_logged_as_invalid_and_replays(self):
        self.plan["engineering"]["max_policy_actions"] = 1
        self.freeze()
        with patch("qa_war_room.study_runner.choose_action", return_value={"type": "submit", "verdict": [], "citations": [], "rationale": "invalid"}):
            summary = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual(summary["runtime_failures"], {"invalid_action": 1})
        replay_matrix(self.pack, self.lock, self.run)

    def test_zero_action_and_zero_exposure_caps_keep_cohort(self):
        self.plan["engineering"]["max_policy_actions"] = 0
        self.freeze()
        summary = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual((summary["pending"], summary["policy_actions"]), (64, 0))
        report = analyze_run(self.pack, self.lock, self.run, self.root / "analysis")
        self.assertEqual(report["statuses"], {"pending": 64})
        self.lock = self.root / "bytes-lock"
        self.plan["engineering"]["max_policy_actions"] = 10000
        self.plan["engineering"]["max_source_bytes_per_job"] = 0
        self.freeze()
        target = self.root / "bytes-run"
        summary = run_matrix(self.pack, self.lock, target)
        self.assertEqual(summary["terminal"], 64)
        _, _, _, engines, _, _, _ = load_run(self.pack, self.lock, target)
        self.assertTrue(all(e.observation()["budget"]["source_bytes_exposed"] == 0 for e in engines.values()))

    def test_serialized_action_matches_runtime_action(self):
        self.plan["engineering"]["max_policy_actions"] = 1
        self.freeze()
        # JSON transport converts tuple -> array before action validation.
        with patch("qa_war_room.study_runner.choose_action", return_value={"type": "submit", "verdict": "insufficient", "citations": (), "rationale": "Transport-normalized action."}):
            summary = run_matrix(self.pack, self.lock, self.run)
        self.assertEqual(summary["runtime_failures"], {})
        self.assertEqual(read_events(self.run / "events.jsonl")[0]["action"]["citations"], [])
        replay_matrix(self.pack, self.lock, self.run)

    def test_torn_tail_and_concurrent_writer_refused(self):
        self.freeze()
        run_matrix(self.pack, self.lock, self.run, stop_after=1)
        with run_lock(self.run):
            with self.assertRaisesRegex(ValueError, "locked"):
                run_matrix(self.pack, self.lock, self.run, resume=True)
        with (self.run / "events.jsonl").open("ab") as handle:
            handle.write(b"{")
        with self.assertRaisesRegex(ValueError, "Torn"):
            run_matrix(self.pack, self.lock, self.run, resume=True)

    def test_forged_source_response_rejected_after_rehash(self):
        self.plan["engineering"]["budgets"] = [7]
        self.freeze()
        run_matrix(self.pack, self.lock, self.run, stop_after=1)
        event = read_events(self.run / "events.jsonl")[0]
        event["observation"]["evidence"][0]["content"] = "FORGED SOURCE"
        event["after_sha256"] = digest(event["observation"])
        event.pop("sha256")
        event["sha256"] = digest(event)
        (self.run / "events.jsonl").write_text(json.dumps(event) + "\n")
        with self.assertRaisesRegex(ValueError, "does not replay"):
            replay_matrix(self.pack, self.lock, self.run)

    def test_gold_tampering_detected_only_in_evaluator_path(self):
        self.freeze()
        with (self.pack / "evaluator/gold.jsonl").open("a") as handle:
            handle.write("\n")
        with self.no_gold():
            run_matrix(self.pack, self.lock, self.run, stop_after=1)
            replay_matrix(self.pack, self.lock, self.run)
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            analyze_run(self.pack, self.lock, self.run, self.root / "analysis")
        self.assertFalse((self.root / "analysis").exists())

    def test_interpretation_ablation_never_mutates_original_evidence(self):
        store = PharmaStore(self.pack)
        lineage = read_jsonl(self.pack / "authoring/lineage.jsonl")
        identity = next(r["id"] for r in lineage if r["construction_change"] == "scope")
        engine = PharmaEngine(store, identity, credits=7)
        for record_id in ("D1", "D2", "D3", "D4", "D5", "D6"):
            engine.apply({"type": "request", "record_id": record_id})
        observation = engine.observation()
        before = deepcopy(observation)
        self.assertEqual(choose_action(observation, "ignore-applicability-v1")["verdict"], "supported")
        self.assertEqual(choose_action(observation, "sop-catalog-v1")["verdict"], "insufficient")
        self.assertEqual(before, observation)

    def test_adaptive_stops_on_visible_failure_without_unrequested_reads(self):
        store = PharmaStore(self.pack)
        identity = next(r["id"] for r in read_jsonl(self.pack / "authoring/lineage.jsonl") if r["construction_change"] == "measure" and r["family_id"] == "MF01")
        engine = PharmaEngine(store, identity, credits=7)
        first = choose_action(engine.observation(), "sop-adaptive-v1")
        self.assertEqual(first, {"type": "request", "record_id": "D1"})
        engine.apply(first)
        second = choose_action(engine.observation(), "sop-adaptive-v1")
        self.assertEqual(second, {"type": "request", "record_id": "D5"})
        engine.apply(second)
        action = choose_action(engine.observation(), "sop-adaptive-v1")
        self.assertEqual(action["verdict"], "contradicted")
        self.assertEqual({r["id"] for r in engine.observation()["evidence"]}, {"D1", "D5"})

    def test_pair_failures_retained_and_ambiguity_separated(self):
        rows = [row("anchor", "f", "a", "supported", "supported"), row("variant", "f", "a", "contradicted", None, "pending"), row("ambig", "f", "a", None)]
        pairs = [{"anchor_id": "anchor", "case_id": "variant", "pair_type": "label_changing"}, {"anchor_id": "anchor", "case_id": "ambig", "pair_type": "unresolved_ambiguity"}]
        diagnostic = pair_diagnostics(rows, pairs)[0]
        self.assertEqual(diagnostic["correct_label_change"], {"numerator": 0, "denominator": 1, "value": 0})
        self.assertEqual(diagnostic["ambiguous_pairs_separate"], 1)
        with self.assertRaises(ValueError):
            pair_diagnostics(rows[:1], pairs)


class StudyArithmeticTests(unittest.TestCase):
    def fixture(self):
        return [row("a", "f1", "A", "insufficient", "supported"), row("a", "f1", "B", "insufficient", "insufficient"),
                row("b", "f2", "A", "insufficient", "insufficient"), row("b", "f2", "B", "insufficient", "supported")]

    def test_hand_computed_denominators_keep_failure_abstain_and_ambiguity(self):
        rows = [row("a", "f", "A", "supported", "supported"), row("b", "f", "A", "supported"),
                row("c", "f", "A", "insufficient", "supported"), row("d", "f", "A", "contradicted", "contradicted"),
                row("e", "f", "A", "insufficient", None, "invalid_action"), row("g", "f", "A", "insufficient", None, "pending"), row("h", "f", "A", None)]
        metrics = summarize(rows)
        self.assertEqual(metrics["false_support_rate"]["value"], 1 / 4)
        self.assertEqual(metrics["supported_sensitivity"]["value"], 1 / 2)
        self.assertEqual(metrics["coverage"]["value"], 3 / 6)
        self.assertEqual(metrics["overall_accuracy"]["value"], 2 / 6)
        self.assertEqual(metrics["ambiguous_separate_episodes"], 1)
        self.assertIsNone(metrics["semantic_evidence_validity"])

    def test_insufficient_submission_is_covered_abstention_is_not(self):
        metrics = summarize([row("a", "f", "A", "insufficient", "insufficient"), row("b", "f", "A")])
        self.assertEqual(metrics["coverage"]["value"], 0.5)
        self.assertEqual(metrics["overall_accuracy"]["value"], 0.5)
        self.assertIsNone(metrics["supported_sensitivity"]["value"])
        self.assertIsNone(summarize([])["false_support_rate"]["value"])

    def test_pairing_rejects_missing_duplicate_or_changed_reference_group(self):
        rows = self.fixture()
        for values in (rows[:-1], rows + [rows[0]]):
            with self.assertRaises(ValueError):
                paired_rows(values, "A", "B")
        for key, value in (("family_id", "other"), ("reference_label", "supported")):
            values = deepcopy(rows)
            values[1][key] = value
            with self.assertRaises(ValueError):
                paired_rows(values, "A", "B")

    def test_bootstrap_resamples_paired_families_not_episode_repetitions(self):
        rows = self.fixture()
        result = paired_bootstrap(rows, "A", "B", replicates=500, seed=41)
        self.assertEqual(result["families"], 2)
        self.assertEqual(result["differences"]["false_support_rate"]["interval"], [-1, 1])
        self.assertEqual(result, paired_bootstrap(rows, "A", "B", replicates=500, seed=41))
        repeated = rows + [{**r, "repetition": 1} for r in rows]
        self.assertEqual(result, paired_bootstrap(repeated, "A", "B", replicates=500, seed=41))
        self.assertFalse(result["independence_or_domain_validity_established"])

    def test_item_weighting_is_not_equal_family_rate_weighting(self):
        rows = self.fixture()
        rows += [row("c", "f1", "A", "insufficient", "supported"), row("c", "f1", "B", "insufficient", "insufficient")]
        result = paired_bootstrap(rows, "A", "B", replicates=100, seed=41)
        self.assertAlmostEqual(result["differences"]["false_support_rate"]["candidate_minus_comparator"], 1 / 3)

    def test_zero_events_degenerate_and_undefined_draws_withhold_intervals(self):
        rows = self.fixture()
        for r in rows:
            if r["method"] == "A":
                r["verdict"] = "insufficient"
        result = paired_bootstrap(rows, "A", "B", replicates=100)
        self.assertEqual(result["differences"]["false_support_rate"]["withheld_reason"], "zero_event_safety_inference_withheld")
        self.assertIsNone(result["candidate_coverage"]["interval"])
        self.assertEqual(result["candidate_coverage"]["withheld_reason"], "degenerate_distribution_not_a_safety_guarantee")
        for r in rows:
            if r["case_id"] == "b":
                r["reference_label"] = "supported"
        result = paired_bootstrap(rows, "A", "B", replicates=100)
        endpoint = result["differences"]["false_support_rate"]
        self.assertGreater(endpoint["undefined_replicates"], 0)
        self.assertEqual(endpoint["withheld_reason"], "undefined_denominator_draws")

    def test_single_cluster_is_not_an_inference_sample(self):
        result = paired_bootstrap(self.fixture()[:2], "A", "B", replicates=20)
        self.assertEqual(result["differences"]["false_support_rate"]["withheld_reason"], "fewer_than_two_family_groups")

    def test_quantile_interpolation_and_invalid_input(self):
        self.assertEqual(quantile([0, 10], 0.25), 2.5)
        for values, q in (([], 0.5), ([1], 2), ([float("nan")], 0.5)):
            with self.assertRaises(ValueError):
                quantile(values, q)

    def test_guardrails_require_all_four_and_never_authorize_science(self):
        margins = {"minimum_fsr_reduction": 0.01, "supported_sensitivity_loss_margin": 0.1,
                   "minimum_coverage": 0.8, "overall_accuracy_loss_margin": 0.1}
        intervals = {"differences": {"false_support_rate": {"interval": [-0.3, -0.02]}, "supported_sensitivity": {"interval": [-0.05, 0.02]},
            "overall_accuracy": {"interval": [-0.01, 0.1]}}, "candidate_coverage": {"interval": [0.9, 1]}}
        result = joint_guardrail_arithmetic(intervals, margins)
        self.assertTrue(result["joint_rule_met"])
        self.assertFalse(result["scientific_claim_authorized"])
        intervals["candidate_coverage"]["interval"] = [0.7, 1]
        self.assertFalse(joint_guardrail_arithmetic(intervals, margins)["joint_rule_met"])
        margins["minimum_coverage"] = None
        self.assertIsNone(joint_guardrail_arithmetic(intervals, margins)["joint_rule_met"])
        with self.assertRaises(ValueError):
            joint_guardrail_arithmetic(intervals, {})

    def test_malformed_outcomes_and_invalid_bootstrap_caps_refused(self):
        for key, value in (("credits", True), ("wall_seconds", float("inf")), ("status", []), ("verdict", "unsupported")):
            r = row("a", "f", "A")
            r[key] = value
            with self.assertRaises(ValueError):
                validate_rows([r])
        for kwargs in ({"replicates": 0}, {"replicates": True}, {"confidence": 1}, {"seed": False}):
            with self.assertRaises(ValueError):
                paired_bootstrap(self.fixture(), "A", "B", **kwargs)


if __name__ == "__main__":
    unittest.main()
