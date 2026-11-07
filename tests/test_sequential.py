"""G3: isolation, grouping, accounting, replay and hand-checkable evaluator proxies."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from qa_war_room.native_data import digest, file_hash
from qa_war_room.native_runner import read_events
from qa_war_room.sequential_data import INPUT_FILES, SequentialStore, group_sources, prepare_inputs, write_jsonl
from qa_war_room.sequential_engine import SequentialEngine, SequentialError
from qa_war_room.sequential_eval import (aggregate, evaluate_episode, load_references,
                                        prepare_references, score_sequential)
from qa_war_room.sequential_policies import choose_action
from qa_war_room.sequential_runner import replay_run, run_sequential


def make_native(root):
    text_a = "HEADER PRIVATE_ONLY_A\nKeep records.\nNo sharing.\nFOOTER"
    text_b = "PRIVATE_ONLY_B 中文\nStore copies.\nReview ended.\nPreserve logs.\nTAIL"
    sources = {"train": ("a", text_a, ["Keep records.", "No sharing."]),
               "dev": ("b", text_b, ["Store copies.", "Review ended.", "Preserve logs."]),
               "test": ("c", text_a, ["Keep records.", "No sharing."])}
    hashes = {}
    for split, (doc_id, text, phrases) in sources.items():
        spans = [[text.index(s), text.index(s) + len(s)] for s in phrases]
        records = {f"contractnli/{split}.documents.jsonl": [{"id": doc_id, "text": text, "spans": spans}],
                   f"contractnli/{split}.tasks.jsonl": [], f"evaluator/contractnli/{split}.gold.jsonl": []}
        for i, label in enumerate(("Entailment", "Contradiction", "NotMentioned")):
            task_id = f"{doc_id}:h{i}"
            records[f"contractnli/{split}.tasks.jsonl"].append({"id": task_id, "document_id": doc_id,
                "hypothesis_id": f"h{i}", "hypothesis": ("Keep records.", "Allow sharing.", "Meet weekly.")[i]})
            records[f"evaluator/contractnli/{split}.gold.jsonl"].append({"id": task_id, "label": label,
                "evidence_span_ids": [i] if i < 2 else []})
        for name, rows in records.items():
            write_jsonl(root / name, rows)
            hashes[name] = {"sha256": file_hash(root / name), "bytes": (root / name).stat().st_size}
    (root / "PREPARATION_REPORT.json").write_text(json.dumps({"source_commits": {"fixture": "original-v1"},
                                                           "prepared_files": hashes}), encoding="utf-8")


class SequentialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.native = self.root / "native"
        make_native(self.native)
        self.bundle = self.root / "bundle"
        manifest = prepare_inputs(self.native, self.bundle, spans_per_record=1)
        prepare_references(self.native, self.bundle, manifest)
        self.store = SequentialStore(self.bundle)
        self.output = self.root / "run"

    def engine(self, credits=3, max_source_bytes=2_000_000):
        return SequentialEngine(self.store, "b:h0", credits, max_source_bytes)

    def run_fixture(self, **kwargs):
        settings = {"split": "dev", "limit_groups": 1, "budgets": (2,), "policies": ("catalog-wiring-v1",)}
        settings.update(kwargs)
        return run_sequential(self.bundle, self.output, **settings)

    def forbid_gold(self):
        original = Path.open
        def guarded(path, *args, **kwargs):
            if "evaluator" in path.parts:
                raise AssertionError("Gold read outside evaluator")
            return original(path, *args, **kwargs)
        return patch.object(Path, "open", guarded)

    def test_chunking_preserves_every_original_character_and_span_offset(self):
        records = [self.store.record("b:h0", r["id"]) for r in self.store.catalog("b:h0")]
        original = json.loads((self.native / "contractnli/dev.documents.jsonl").read_text(encoding="utf-8"))
        self.assertEqual("".join(r["text"] for r in records), original["text"])
        self.assertEqual([[s["start"], s["end"]] for r in records for s in r["spans"]], original["spans"])
        self.assertEqual([r["cost"] for r in records], [1, 1, 1])

    def test_input_preparation_never_reads_gold(self):
        other = self.root / "input-only"
        with self.forbid_gold():
            manifest = prepare_inputs(self.native, other, spans_per_record=1)
        self.assertEqual(set(manifest["input_files"]), set(INPUT_FILES))
        self.assertFalse((other / "PACK.json").exists())
        with self.assertRaises(FileNotFoundError):
            SequentialStore(other)

    def test_changed_gold_does_not_change_inputs_chunking_or_grouping(self):
        gold = self.native / "evaluator/contractnli/dev.gold.jsonl"
        gold.write_text(gold.read_text().replace("Entailment", "Contradiction"))
        prep_path = self.native / "PREPARATION_REPORT.json"
        prep = json.loads(prep_path.read_text())
        prep["prepared_files"]["evaluator/contractnli/dev.gold.jsonl"] = {"sha256": file_hash(gold), "bytes": gold.stat().st_size}
        prep_path.write_text(json.dumps(prep))
        other = self.root / "changed-gold"
        manifest = prepare_inputs(self.native, other, spans_per_record=1)
        for name in INPUT_FILES:
            self.assertEqual((self.bundle / name).read_bytes(), (other / name).read_bytes())
        self.assertNotEqual(manifest["native_preparation_sha256"], self.store.manifest["native_preparation_sha256"])

    def test_exact_copies_and_descendants_stay_together_original_splits_preserved(self):
        split = self.store.splits
        self.assertEqual(split["documents"]["a"]["source_family_id"], split["documents"]["c"]["source_family_id"])
        self.assertEqual(split["documents"]["a"]["original_split"], "train")
        self.assertEqual(split["documents"]["a"]["derived_split"], "test")
        self.assertEqual(split["moved_documents"], ["a"])
        cohort = self.store.cohort("test", 1)
        self.assertEqual({r["source_id"] for r in cohort}, {"a", "c"})
        self.assertEqual(len(cohort), 6)
        self.assertTrue(all(not r["counterfactual"] for r in self.store.lineage))
        self.assertEqual(len({r["source_family_id"] for r in cohort}), 1)

    def test_declared_families_union_transitively_with_exact_copies(self):
        rows = {}
        for split in ("train", "dev", "test"):
            row = json.loads((self.native / f"contractnli/{split}.documents.jsonl").read_text(encoding="utf-8"))
            rows[row["id"]] = {**row, "original_split": split}
        grouped = group_sources(rows, {"a": "related", "b": "related"})
        self.assertEqual(len(grouped["groups"]), 1)
        self.assertEqual(grouped["groups"][0]["document_ids"], ["a", "b", "c"])
        with self.assertRaises(ValueError):
            group_sources(rows, {"unknown": "family"})
        with self.assertRaises(ValueError):
            group_sources(rows, [])
        self.assertEqual(grouped, group_sources(dict(reversed(list(rows.items()))), {"a": "related", "b": "related"}))

    def test_existing_bundle_is_not_overwritten_and_tampered_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError, "exists"):
            prepare_inputs(self.native, self.bundle)
        path = self.bundle / "private/records.jsonl"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "checksum"):
            SequentialStore(self.bundle)

    def test_lineage_split_tamper_is_rejected_even_when_file_checksums_are_updated(self):
        path = self.bundle / "public/lineage.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]["derived_split"] = "dev"  # Original train source was grouped with its test copy.
        write_jsonl(path, rows)
        manifest_path = self.bundle / "PACK.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["input_files"]["public/lineage.jsonl"] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "lineage"):
            SequentialStore(self.bundle)

    def test_initial_catalog_and_observation_exclude_all_hidden_text_and_gold(self):
        observation = self.engine().observation()
        serialized = json.dumps(observation)
        self.assertNotIn("PRIVATE_ONLY", serialized)
        self.assertNotIn("reference_span", serialized)
        self.assertNotIn("source_family_id", observation)
        self.assertEqual(observation["evidence"], [])
        self.assertIsNone(observation["decision"])
        self.assertEqual(set(observation["catalog"][0]), {"id", "title", "cost", "requested"})

    def test_only_requested_record_is_disclosed_and_observations_are_detached(self):
        engine = self.engine()
        state = engine.apply({"type": "request", "record_id": "R0002"})
        self.assertEqual([r["id"] for r in state["evidence"]], ["R0002"])
        self.assertNotIn("PRIVATE_ONLY_B", json.dumps(state))
        self.assertIn("source_commits", state["evidence"][0]["provenance"])
        state["evidence"][0]["text"] = "MUTATED"
        self.assertNotEqual(engine.observation()["evidence"][0]["text"], "MUTATED")
        other = self.engine()
        self.assertEqual(other.observation()["evidence"], [])

    def test_duplicate_request_is_exactly_idempotent(self):
        engine = self.engine()
        first = engine.apply({"type": "request", "record_id": "R0001"})
        self.assertEqual(first, engine.apply({"type": "request", "record_id": "R0001"}))

    def test_failed_delivery_costs_once_without_exposing_content_or_citations(self):
        engine = self.engine(max_source_bytes=1)
        first = engine.apply({"type": "request", "record_id": "R0001"})
        self.assertEqual(first["budget"]["credits_spent"], 1)
        self.assertEqual(first["budget"]["source_bytes_exposed"], 0)
        self.assertEqual(first["responses"][0]["status"], "exposure_cap_not_delivered")
        self.assertEqual(first["evidence"], [])
        self.assertEqual(first, engine.apply({"type": "request", "record_id": "R0001"}))

    def test_invalid_unknown_and_over_budget_actions_cannot_mutate_state(self):
        engine = self.engine(credits=0)
        before = engine.observation()
        for action in ({"type": "search", "query": "hidden"}, {"type": "request", "record_id": "../evaluator/gold.jsonl"},
                       {"type": "request", "record_id": "R0001", "gold": True},
                       {"type": "request", "record_id": "R0001"}, {"type": "request", "record_id": []}):
            with self.assertRaises(SequentialError):
                engine.apply(action)
            self.assertEqual(engine.observation(), before)

    def test_unseen_duplicate_boolean_and_noninteger_citations_rejected(self):
        engine = self.engine()
        engine.apply({"type": "request", "record_id": "R0001"})
        for ids in ([1], [0, 0], [True], ["0"], [-1], []):
            with self.assertRaises(SequentialError):
                engine.apply({"type": "submit", "label": "Entailment", "citation_span_ids": ids, "rationale": "Check"})
        engine.apply({"type": "submit", "label": "Entailment", "citation_span_ids": [0], "rationale": "Visible span"})
        with self.assertRaisesRegex(SequentialError, "episode_completed"):
            engine.apply({"type": "request", "record_id": "R0002"})

    def test_notmentioned_is_a_submitted_source_class_and_abstain_is_separate(self):
        engine = self.engine(credits=0)
        engine.apply({"type": "submit", "label": "NotMentioned", "citation_span_ids": [], "rationale": "A wiring guess"})
        other = self.engine(credits=0)
        other.apply({"type": "abstain", "forced_label": "NotMentioned", "reason": "No visible evidence"})
        self.assertNotEqual(engine.observation()["decision"]["type"], other.observation()["decision"]["type"])
        self.assertEqual(other.observation()["evidence"], [])
        with self.assertRaises(SequentialError):
            self.engine().apply({"type": "submit", "label": "ABSTAIN", "citation_span_ids": [], "rationale": "X"})

    def test_budget_and_seed_schema_reject_boolean_or_negative_caps(self):
        for credits in (True, -1, 1.5):
            with self.assertRaises(ValueError):
                self.engine(credits=credits)
        for kwargs in ({"budgets": (True,)}, {"budgets": (1, 1)}, {"max_policy_actions": -1}, {"seed": True}):
            with self.assertRaises(ValueError):
                self.run_fixture(**kwargs)

    def test_policies_use_only_supplied_observation_and_visible_text(self):
        observation = self.engine(credits=1).observation()
        with self.forbid_gold():
            first = choose_action(observation, "catalog-wiring-v1")
            self.assertEqual(first, {"type": "request", "record_id": "R0001"})
            self.assertEqual(choose_action(observation, "random-wiring-v1", 7), choose_action(observation, "random-wiring-v1", 7))
        guarded = self.engine(credits=1)
        guarded.apply(first)
        self.assertEqual(choose_action(guarded.observation(), "catalog-guarded-wiring-v1")["type"], "abstain")

    def test_runner_and_replay_never_open_gold_or_call_network(self):
        with self.forbid_gold(), patch("socket.create_connection", side_effect=AssertionError("Network called")):
            result = self.run_fixture()
            with patch("qa_war_room.sequential_runner.choose_action", side_effect=AssertionError("Replay invoked policy")):
                replay = replay_run(self.bundle, self.output, 1)
        self.assertEqual(result["terminal"], 3)
        self.assertFalse(replay["gold_read"])
        self.assertFalse(replay["policy_invoked"])
        self.assertNotIn("reference_label", (self.output / "events.jsonl").read_text())
        self.assertNotIn("oracle", (self.output / "events.jsonl").read_text())

    def test_mid_episode_checkpoint_and_resume_match_uninterrupted_transitions(self):
        first = self.run_fixture(stop_after_actions=1)
        self.assertEqual(first["status"], "checkpointed")
        self.assertEqual(first["pending"], 3)
        self.run_fixture(resume=True)
        events = read_events(self.output / "events.jsonl")
        other = self.root / "uninterrupted"
        run_sequential(self.bundle, other, budgets=(2,), policies=("catalog-wiring-v1",))
        expected = read_events(other / "events.jsonl")
        for a, b in zip(events, expected):
            self.assertEqual({k: a[k] for k in ("key", "action", "before_sha256", "after_sha256", "observation")},
                             {k: b[k] for k in ("key", "action", "before_sha256", "after_sha256", "observation")})
        self.assertEqual(len(events), len(expected))
        before = (self.output / "events.jsonl").read_bytes()
        self.run_fixture(resume=True)
        self.assertEqual(before, (self.output / "events.jsonl").read_bytes())

    def test_run_outputs_not_overwritten_changed_resume_and_concurrent_writer_refused(self):
        self.run_fixture(stop_after_actions=1)
        with self.assertRaisesRegex(ValueError, "exists"):
            self.run_fixture()
        with self.assertRaisesRegex(ValueError, "config differs"):
            self.run_fixture(resume=True, budgets=(1,))
        lock = self.output / ".writer.lock"
        lock.write_text('{"pid":0}')
        with self.assertRaisesRegex(ValueError, "locked"):
            self.run_fixture(resume=True)
        self.assertTrue(lock.exists())

    def test_global_action_cap_stops_before_next_policy_call(self):
        result = self.run_fixture(max_policy_actions=1)
        self.assertEqual(result["policy_actions"], 1)
        self.assertEqual(result["status"], "policy_action_budget_stopped")
        self.assertEqual(result["pending"], 3)
        before = (self.output / "events.jsonl").read_bytes()
        self.run_fixture(max_policy_actions=1, resume=True)
        self.assertEqual(before, (self.output / "events.jsonl").read_bytes())
        score_sequential(self.bundle, self.output)
        table = json.loads((self.output / "metrics.json").read_text())["tables"][0]
        self.assertEqual(table["coverage"], {"numerator": 0, "denominator": 3, "value": 0})
        self.assertEqual(table["statuses"], {"active": 3})

    def test_duplicate_policy_loop_is_bounded_and_replayable(self):
        with patch("qa_war_room.sequential_runner.choose_action", return_value={"type": "request", "record_id": "R0001"}):
            result = self.run_fixture(max_episode_actions=3)
        self.assertEqual(result["policy_actions"], 9)
        self.assertEqual(result["credits_spent"], 3)
        self.assertEqual(result["logged_transitions"], 12)
        replay_run(self.bundle, self.output)
        score_sequential(self.bundle, self.output)
        self.assertEqual(json.loads((self.output / "metrics.json").read_text())["tables"][0]["statuses"], {"failed": 3})

    def test_invalid_policy_outputs_fail_without_free_repair_and_errors_are_redacted(self):
        with patch("qa_war_room.sequential_runner.choose_action", return_value={"type": "request", "record_id": "hidden"}):
            self.run_fixture()
        self.assertTrue(all(e["error_code"] == "unknown_record" for e in read_events(self.output / "events.jsonl")))
        replay_run(self.bundle, self.output)
        self.output = self.root / "exceptions"
        with patch("qa_war_room.sequential_runner.choose_action", side_effect=RuntimeError("SECRET_KEY")):
            self.run_fixture()
        self.assertNotIn("SECRET_KEY", (self.output / "events.jsonl").read_text())
        self.assertEqual(replay_run(self.bundle, self.output)["transitions"], 3)

    def test_torn_corrupt_and_foreign_ledgers_are_rejected(self):
        self.run_fixture(stop_after_actions=1)
        path = self.output / "events.jsonl"
        original = path.read_bytes()
        path.write_bytes(original[:-1])
        with self.assertRaisesRegex(ValueError, "Torn"):
            replay_run(self.bundle, self.output)
        path.write_bytes(original.replace(b'credits_spent', b'credits_spant', 1))
        with self.assertRaisesRegex(ValueError, "integrity"):
            replay_run(self.bundle, self.output)
        other = self.root / "other"
        run_sequential(self.bundle, other, budgets=(1,), policies=("catalog-wiring-v1",), stop_after_actions=1)
        path.write_bytes((other / "events.jsonl").read_bytes())
        with self.assertRaisesRegex(ValueError, "different task/run"):
            replay_run(self.bundle, self.output)

    def test_replay_detects_invented_hidden_response_even_with_recomputed_event_hash(self):
        self.run_fixture(stop_after_actions=1)
        event = read_events(self.output / "events.jsonl")[0]
        event["observation"]["evidence"][0]["text"] = "FABRICATED"
        event["after_sha256"] = digest(event["observation"])
        del event["sha256"]
        event["sha256"] = digest(event)
        (self.output / "events.jsonl").write_text(json.dumps(event) + "\n")
        with self.assertRaisesRegex(ValueError, "does not replay"):
            replay_run(self.bundle, self.output)

    def test_scoring_does_not_change_raw_trace_or_invoke_policy_and_gold_is_separate(self):
        self.run_fixture()
        before = (self.output / "events.jsonl").read_bytes()
        with patch("qa_war_room.sequential_runner.choose_action", side_effect=AssertionError("Policy invoked by evaluator")):
            report = score_sequential(self.bundle, self.output)
        self.assertEqual(before, (self.output / "events.jsonl").read_bytes())
        self.assertFalse(report["scientific_performance_claim"])
        self.assertTrue((self.output / "evaluator/oracle-diagnostics.json").exists())
        self.assertTrue((self.output / "evaluator/episodes.jsonl").exists())
        gold = self.bundle / "evaluator/gold.jsonl"
        gold.write_bytes(gold.read_bytes() + b" ")
        replay_run(self.bundle, self.output)  # Gold is irrelevant to input replay.
        with self.assertRaisesRegex(ValueError, "evaluator checksum"):
            score_sequential(self.bundle, self.output)

    def test_lucky_label_with_wrong_acquired_span_is_not_reference_supported(self):
        engine = self.engine()
        engine.apply({"type": "request", "record_id": "R0002"})
        state = engine.apply({"type": "submit", "label": "Entailment", "citation_span_ids": [1], "rationale": "Wiring guess"})
        result = evaluate_episode(self.store, load_references(self.store)["b:h0"], state)
        self.assertTrue(result["forced_correct"])
        self.assertFalse(result["published_reference_observed"])
        self.assertFalse(result["decision_and_reference_proxy"])

    def test_oracle_credit_and_byte_reachability_matches_executable_requests(self):
        refs = load_references(self.store)
        for credits in (0, 1, 3):
            engine = self.engine(credits=credits)
            result = evaluate_episode(self.store, refs["b:h0"], engine.observation())
            oracle = result["oracle_diagnostic_only"]
            self.assertEqual(oracle["minimum_proxy_credits"], 1)
            self.assertEqual(oracle["attainable_under_caps"], credits >= 1)
            if credits:
                for record_id in oracle["required_record_ids"]:
                    engine.apply({"type": "request", "record_id": record_id})
                self.assertTrue(evaluate_episode(self.store, refs["b:h0"], engine.observation())["published_reference_observed"])
        too_small = self.engine(max_source_bytes=1)
        self.assertFalse(evaluate_episode(self.store, refs["b:h0"], too_small.observation())["oracle_diagnostic_only"]["attainable_under_caps"])

    def test_notmentioned_proxy_requires_all_source_not_merely_empty_gold_spans(self):
        engine = SequentialEngine(self.store, "b:h2", 3)
        refs = load_references(self.store)
        first = evaluate_episode(self.store, refs["b:h2"], engine.observation())
        self.assertFalse(first["published_reference_observed"])
        self.assertEqual(first["oracle_diagnostic_only"]["minimum_proxy_credits"], 3)
        for row in engine.observation()["catalog"]:
            engine.apply({"type": "request", "record_id": row["id"]})
        self.assertTrue(evaluate_episode(self.store, refs["b:h2"], engine.observation())["published_reference_observed"])

    def test_metrics_hand_fixture_keeps_abstentions_failures_and_undefined_denominators(self):
        base = {"source_id": "source", "source_family_id": "family", "published_reference_observed": False,
                "decision_and_reference_proxy": False, "credits_spent": 0, "source_bytes_exposed": 0,
                "unique_records_returned": 0, "denied_record_requests": 0}
        rows = [{**base, "reference_label": "Contradiction", "selective_label": "Entailment", "submitted": True,
                 "forced_correct": False, "status": "completed"},
                {**base, "reference_label": "Entailment", "selective_label": "ABSTAIN", "submitted": False,
                 "forced_correct": True, "status": "completed"},
                {**base, "reference_label": "NotMentioned", "selective_label": "INVALID", "submitted": False,
                 "forced_correct": False, "status": "failed"}]
        result = aggregate(rows)
        self.assertEqual(result["false_support_rate"]["value"], 0.5)
        self.assertEqual(result["supported_sensitivity"]["value"], 0)
        self.assertEqual(result["coverage"]["value"], 1 / 3)
        self.assertEqual(result["forced_label_accuracy"]["value"], 1 / 3)
        self.assertIsNone(aggregate([rows[1]])["false_support_rate"]["value"])
        self.assertIn("INVALID", result["confusion"]["NotMentioned"])


if __name__ == "__main__":
    unittest.main()
