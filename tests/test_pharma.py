"""Original synthetic G4 data, isolation, applicability and blinded-review gates."""

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from qa_war_room.native_data import digest, file_hash, read_jsonl
from qa_war_room.native_runner import read_events
from qa_war_room.pharma_authoring import prepare_inputs
from qa_war_room.pharma_engine import PharmaEngine, PharmaError, PharmaStore
from qa_war_room.pharma_eval import build_references, evaluate_terminal, load_gold
from qa_war_room.pharma_review import check_reviews, export_review
from qa_war_room.pharma_rules import applicability, assess_visible
from qa_war_room.pharma_runner import exercise, replay, score_exercise, visible_action
from qa_war_room.sequential_data import write_jsonl


class PharmaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = self.root / "pack"
        build_references(self.pack, prepare_inputs(self.pack))
        self.store = PharmaStore(self.pack)
        self.lineage = read_jsonl(self.pack / "authoring/lineage.jsonl")
        self.aliases = {(row["family_id"], row["construction_change"]): row["id"] for row in self.lineage}

    def case_id(self, change="anchor", family="MF01"):
        return self.aliases[family, change]

    def full_observation(self, change="anchor", family="MF01"):
        engine = PharmaEngine(self.store, self.case_id(change, family))
        for row in engine.observation()["catalog"]:
            engine.apply({"type": "request", "record_id": row["id"]})
        return engine.observation()

    def forbidden_reference_reads(self):
        original = Path.open
        def guard(path, *args, **kwargs):
            if "evaluator" in path.parts or "authoring" in path.parts:
                raise AssertionError("Reference/construction metadata read in public runtime")
            return original(path, *args, **kwargs)
        return patch.object(Path, "open", guard)

    def test_counts_positive_negative_insufficient_and_ambiguous_preserved(self):
        gold = load_gold(self.store)
        self.assertEqual(len(gold), 48)
        self.assertEqual(Counter(row["candidate_verdict"] or "ambiguous" for row in gold.values()),
                         {"supported": 12, "contradicted": 12, "insufficient": 18, "ambiguous": 6})
        self.assertTrue(all(row["review_status"] == "unreviewed" for row in gold.values()))
        self.assertEqual(sum(row["primary_eligible_draft"] for row in gold.values()), 42)

    def test_input_only_builder_does_not_access_reference_data(self):
        other = self.root / "inputs"
        original = Path.open
        def no_gold(path, *args, **kwargs):
            if "evaluator" in path.parts:
                raise AssertionError("Gold read during input authoring")
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", no_gold):
            manifest = prepare_inputs(other)
        self.assertNotIn("candidate_verdict", (other / "public/cases.jsonl").read_text())
        self.assertNotIn("evaluator_files", manifest)
        self.assertFalse((other / "PACK.json").exists())

    def test_all_counterfactuals_and_templates_stay_in_one_provisional_split(self):
        self.assertEqual(len(self.store.splits["groups"]), 6)
        self.assertEqual(Counter(g["split"] for g in self.store.splits["groups"]), {"train": 2, "dev": 2, "test": 2})
        seen = set()
        for group in self.store.splits["groups"]:
            self.assertEqual(len(group["case_ids"]), 8)
            self.assertFalse(seen.intersection(group["case_ids"]))
            seen.update(group["case_ids"])
        self.assertEqual(seen, set(self.store.case_ids()))

    def test_counterfactual_pair_index_tracks_changed_and_preserving_facts(self):
        pairs = read_jsonl(self.pack / "evaluator/pairs.jsonl")
        self.assertEqual(len(pairs), 42)
        for row in pairs:
            if row["construction_change"] == "context":
                self.assertFalse(row["label_changed_under_author_rules"])
                self.assertEqual(row["variant_candidate"], "supported")
            if row["construction_change"] == "measure":
                self.assertEqual(row["changed_fact_paths"], [row["changed_fact_paths"][0]])
                self.assertEqual(row["variant_candidate"], "contradicted")
            if row["construction_change"] == "unclear":
                self.assertIsNone(row["label_changed_under_author_rules"])
                self.assertEqual(row["pair_type"], "unresolved_ambiguity")
            self.assertFalse(row["independently_reviewed"])

    def test_single_decisive_change_preserves_other_evidence_and_claim(self):
        a, b = self.case_id(), self.case_id("measure")
        card_a, card_b = self.store.card(a), self.store.card(b)
        self.assertEqual({k: v for k, v in card_a.items() if k != "id"}, {k: v for k, v in card_b.items() if k != "id"})
        self.assertEqual(self.store.catalog(a), self.store.catalog(b))
        for record_id in ("D1", "D2", "D3", "D4", "D6", "D7"):
            self.assertEqual(self.store.record(a, record_id), self.store.record(b, record_id))
        doc_a, doc_b = self.store.record(a, "D5")["document"], self.store.record(b, "D5")["document"]
        self.assertEqual(doc_a["facts"]["unreconciled_units"], 0)
        self.assertEqual(doc_b["facts"]["unreconciled_units"], 1)

    def test_baseline_timeline_and_original_affected_followup_cohorts_are_coherent(self):
        card = self.store.card(self.case_id())
        sop = self.store.record(self.case_id(), "D1")["document"]
        training = self.store.record(self.case_id(), "D4")["document"]
        self.assertLess(sop["recorded_at"], training["facts"]["trained_at"])
        self.assertTrue(set(card["scope"]["batches"]).isdisjoint(card["scope"]["affected_batches"]))
        self.assertNotEqual(self.store.record(self.case_id(), "D7")["document"]["scope"]["line"], card["scope"]["line"])

    def test_initial_observation_and_catalog_do_not_reveal_variants_or_gold(self):
        with self.forbidden_reference_reads():
            store = PharmaStore(self.pack)
            observed = PharmaEngine(store, self.case_id()).observation()
        self.assertEqual(observed["evidence"], [])
        self.assertNotIn("family_id", observed["case"])
        self.assertNotIn("split", observed["case"])
        self.assertEqual(set(observed["catalog"][0]), {"id", "cost", "title", "document_type", "requested"})
        for change in ("anchor", "measure", "unavailable", "scope", "future", "revision", "context", "unclear"):
            self.assertEqual(self.store.catalog(self.case_id(change)), self.store.catalog(self.case_id()))

    def test_only_requested_records_are_returned_and_snapshots_are_detached(self):
        engine = PharmaEngine(self.store, self.case_id())
        state = engine.apply({"type": "request", "record_id": "D3"})
        self.assertEqual([r["id"] for r in state["evidence"]], ["D3"])
        state["evidence"][0]["facts"]["implementation_status"] = "FAKE"
        self.assertNotEqual(engine.observation()["evidence"][0]["facts"]["implementation_status"], "FAKE")
        self.assertEqual(PharmaEngine(self.store, self.case_id()).observation()["evidence"], [])

    def test_missing_source_costs_once_and_contains_no_hidden_payload(self):
        engine = PharmaEngine(self.store, self.case_id("unavailable"))
        state = engine.apply({"type": "request", "record_id": "D5"})
        self.assertEqual(state["budget"]["spent"], 2)
        self.assertEqual(state["responses"][0]["status"], "source_unavailable")
        self.assertEqual(state["evidence"], [])
        self.assertEqual(engine.apply({"type": "request", "record_id": "D5"}), state)
        self.assertIsNone(self.store.record(self.case_id("unavailable"), "D5")["document"])

    def test_budget_byte_caps_unknown_and_extra_fields(self):
        engine = PharmaEngine(self.store, self.case_id(), credits=1)
        before = engine.observation()
        for action in ({"type": "request", "record_id": "D5"}, {"type": "request", "record_id": "../evaluator/gold.jsonl"},
                       {"type": "request", "record_id": "D1", "budget": 99}):
            with self.assertRaises(PharmaError):
                engine.apply(action)
            self.assertEqual(engine.observation(), before)
        capped = PharmaEngine(self.store, self.case_id(), max_source_bytes=1)
        state = capped.apply({"type": "request", "record_id": "D5"})
        self.assertEqual(state["budget"]["spent"], 2)
        self.assertEqual(state["responses"][0]["status"], "exposure_cap_not_delivered")
        self.assertEqual(state["evidence"], [])

    def test_scope_and_future_record_are_unknown_not_confirmed_failure(self):
        for change, reason in (("scope", "scope_mismatch"), ("future", "after_assessment_cutoff")):
            state = self.full_observation(change)
            assessment = assess_visible(state["case"], state["evidence"], state["responses"])
            self.assertEqual(assessment["verdict"], "insufficient")
            self.assertTrue(any(row["reason"] == reason for row in assessment["criteria"]))
        state = self.full_observation("scope")
        next(doc for doc in state["evidence"] if doc["id"] == "D5")["facts"]["unreconciled_units"] = 99
        self.assertEqual(assess_visible(state["case"], state["evidence"], state["responses"])["verdict"], "insufficient")

    def test_explicit_obsolete_training_and_failed_criteria_contradict_only_site_claim(self):
        for family in (f"MF{i:02d}" for i in range(1, 7)):
            for change in ("measure", "revision"):
                state = self.full_observation(change, family)
                result = assess_visible(state["case"], state["evidence"], state["responses"])
                self.assertEqual(result["verdict"], "contradicted")
                self.assertTrue(any(row["status"] == "fail" for row in result["criteria"]))

    def test_missing_field_is_unknown_and_bad_numeric_type_is_not_silent_gold(self):
        state = self.full_observation()
        doc = next(row for row in state["evidence"] if row["id"] == "D5")
        del doc["facts"]["unreconciled_units"]
        self.assertEqual(assess_visible(state["case"], state["evidence"], state["responses"])["verdict"], "insufficient")
        doc["facts"]["unreconciled_units"] = "0"
        with self.assertRaisesRegex(ValueError, "type mismatch"):
            assess_visible(state["case"], state["evidence"], state["responses"])

    def test_ambiguous_rule_has_no_unique_label_and_is_preexcluded_from_primary(self):
        gold = load_gold(self.store)[self.case_id("unclear")]
        self.assertIsNone(gold["candidate_verdict"])
        self.assertTrue(gold["ambiguity_preflagged"])
        self.assertFalse(gold["primary_eligible_draft"])
        self.assertIsNone(gold["declared_record_witness_sets"])
        state = self.full_observation("unclear")
        self.assertEqual(visible_action(state)["type"], "abstain")

    def test_declared_record_and_unavailability_witnesses_are_obtainable(self):
        for case_id, reference in load_gold(self.store).items():
            if reference["candidate_verdict"] is None:
                continue
            for witness in reference["declared_record_witness_sets"]:
                engine = PharmaEngine(self.store, case_id)
                for record_id in dict.fromkeys(witness + reference["required_unavailability_checks"]):
                    engine.apply({"type": "request", "record_id": record_id})
                state = engine.observation()
                self.assertEqual(assess_visible(state["case"], state["evidence"], state["responses"])["verdict"], reference["candidate_verdict"])
                self.assertLessEqual(state["budget"]["spent"], state["budget"]["total"])

    def test_citations_must_be_unique_visible_exact_locations(self):
        engine = PharmaEngine(self.store, self.case_id())
        engine.apply({"type": "request", "record_id": "D3"})
        valid = {"record_id": "D3", "pointer": "/facts/implementation_status"}
        for citations in ([{"record_id": "D5", "pointer": "/facts"}], [valid, valid],
                          [{"record_id": "D3", "pointer": "/facts/not_present"}], [],
                          [{"record_id": "D3", "pointer": True}]):
            with self.assertRaises(PharmaError):
                engine.apply({"type": "submit", "verdict": "supported", "citations": citations, "rationale": "Check"})
        engine.apply({"type": "submit", "verdict": "supported", "citations": [valid], "rationale": "A structurally valid but insufficient citation."})
        result = evaluate_terminal(self.store, engine.observation())
        self.assertTrue(result["label_matches_candidate"])
        self.assertFalse(result["declared_fact_locations_cited"])
        self.assertFalse(result["observed_decision_matches_declared_rules"])
        with self.assertRaises(PharmaError):
            engine.apply({"type": "request", "record_id": "D1"})

    def test_gold_is_only_available_to_terminal_evaluation(self):
        engine = PharmaEngine(self.store, self.case_id())
        with self.assertRaisesRegex(ValueError, "before terminal"):
            evaluate_terminal(self.store, engine.observation())
        engine.apply({"type": "abstain", "reason": "No acquired evidence"})
        result = evaluate_terminal(self.store, engine.observation())
        self.assertIsNone(result["label_matches_candidate"])

    def test_walkthrough_and_replay_are_offline_gold_free_and_score_is_separate(self):
        output = self.root / "exercise"
        with self.forbidden_reference_reads(), patch("socket.create_connection", side_effect=AssertionError("network")):
            summary = exercise(self.pack, output)
            observations, events = replay(self.store, output)
        self.assertEqual(summary["cases"], 48)
        self.assertEqual(len(events), 384)
        self.assertEqual(summary["decisions"], {"supported": 12, "contradicted": 12, "insufficient": 18, "abstain": 6})
        self.assertEqual(len(observations), 48)
        before = (output / "events.jsonl").read_bytes()
        with patch("qa_war_room.pharma_runner.visible_action", side_effect=AssertionError("scorer called policy")):
            result = score_exercise(self.pack, output)
        self.assertEqual(result["candidate_matches"], 42)
        self.assertFalse(result["independent_review_completed"])
        self.assertEqual(before, (output / "events.jsonl").read_bytes())
        self.assertNotIn('"candidate_verdict"', before.decode())
        with self.assertRaisesRegex(ValueError, "exists"):
            exercise(self.pack, output)

    def test_input_tampering_and_fake_independent_status_are_rejected(self):
        path = self.pack / "PACK.json"
        manifest = json.loads(path.read_text())
        manifest["independent_review_completed"] = True
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "cannot assert"):
            PharmaStore(self.pack)
        manifest["independent_review_completed"] = False
        path.write_text(json.dumps(manifest))
        records = self.pack / "private/records.jsonl"
        records.write_bytes(records.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "checksum"):
            PharmaStore(self.pack)

    def test_reference_tampering_does_not_affect_public_runtime_but_evaluator_refuses(self):
        gold = self.pack / "evaluator/gold.jsonl"
        gold.write_bytes(gold.read_bytes() + b" ")
        with self.forbidden_reference_reads():
            PharmaEngine(PharmaStore(self.pack), self.case_id()).observation()
        with self.assertRaisesRegex(ValueError, "checksum"):
            load_gold(self.store)

    def make_review_export(self, name="review"):
        output = self.root / name
        export_review(self.store, output, case_ids=[self.case_id(), self.case_id(family="MF02")])
        return output / "reviewer"

    def test_blinded_review_export_is_gold_free_and_has_no_source_or_pair_keys(self):
        with self.forbidden_reference_reads():
            packet = self.make_review_export()
        cases = read_jsonl(packet / "cases.jsonl")
        self.assertEqual(len(cases), 2)
        for row in cases:
            self.assertNotIn("M4_", json.dumps(row))
            self.assertNotIn("family_id", json.dumps(row))
            self.assertNotIn("construction_change", json.dumps(row))
            self.assertNotIn("candidate_verdict", json.dumps(row))
        self.assertTrue((packet.parent / "owner/link-map.jsonl").exists())
        self.assertFalse((packet / "link-map.jsonl").exists())
        self.assertTrue(all(row["verdict"] is None for row in read_jsonl(packet / "ratings-template-A.jsonl")))

    def test_blank_reviews_are_incomplete_and_never_published_as_reviewed(self):
        packet = self.make_review_export()
        result = check_reviews(packet, [packet / "ratings-template-A.jsonl", packet / "ratings-template-B.jsonl"],
                               packet / "reviewers-template.json", self.root / "blank-check")
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["distinct_attested_reviewer_codes"], 0)
        self.assertFalse(result["independent_pharmaceutical_validation_established"])
        self.assertTrue(all(row["final_verdict"] is None for row in read_jsonl(self.root / "blank-check/adjudication-template.jsonl")))

    def completed_test_reviews(self, packet):
        """Unit fixtures only, never actual reviewer records or credentials."""
        paths = []
        for code in ("TEST_ONLY_A", "TEST_ONLY_B"):
            rows = read_jsonl(packet / "ratings-template-A.jsonl")
            for row in rows:
                row.update({"reviewer_code": code, "verdict": "supported", "plausibility": "plausible",
                            "rationale": "Unit test fixture only; this is not a human review.", "primary_disposition": "include",
                            "full_packet_reviewed": True, "citations": [{"record_id": "D1", "pointer": "/facts/criteria"}]})
                for criterion in row["criteria"]:
                    criterion["status"] = "pass"
            path = self.root / (code + ".jsonl")
            write_jsonl(path, rows)
            paths.append(path)
        roster = self.root / "test-roster.json"
        roster.write_text(json.dumps({"reviewers": [{"reviewer_code": code, "manufacturing_qa_experience": "TEST FIXTURE ONLY, not human credentials",
            "independent_of_author": True, "conflicts_disclosed": True} for code in ("TEST_ONLY_A", "TEST_ONLY_B")]}))
        return paths, roster

    def test_complete_structural_intake_retains_original_bytes_and_cannot_promote_gold(self):
        packet = self.make_review_export()
        paths, roster = self.completed_test_reviews(packet)
        before = (self.pack / "evaluator/gold.jsonl").read_bytes()
        output = self.root / "intake"
        with self.forbidden_reference_reads():
            report = check_reviews(packet, paths, roster, output)
        self.assertEqual(report["status"], "RECORDS_COMPLETE_PENDING_HUMAN_VERIFICATION_AND_ADJUDICATION")
        self.assertFalse(report["identity_or_independence_verified_by_software"])
        self.assertFalse(report["reference_labels_modified"])
        self.assertEqual(before, (self.pack / "evaluator/gold.jsonl").read_bytes())
        self.assertEqual({row["sha256"] for row in report["archived_inputs"]}, {file_hash(p) for p in [roster, *paths]})
        with self.assertRaisesRegex(ValueError, "exists"):
            check_reviews(packet, paths, roster, output)

    def test_review_unknown_citations_versions_duplicate_reviewers_and_ambiguity_rejected(self):
        packet = self.make_review_export()
        paths, roster = self.completed_test_reviews(packet)
        rows = read_jsonl(paths[0])
        rows[0]["case_version"] = "wrong-version"
        rows[0]["citations"] = [{"record_id": "D99", "pointer": "/facts"}]
        rows[0]["verdict"] = "ambiguous"
        rows[0]["ambiguity_notes"] = ""
        write_jsonl(paths[0], rows)
        report = check_reviews(packet, [paths[0], paths[0]], roster, self.root / "invalid-intake")
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertTrue(any("citation" in issue for issue in report["issues"]))
        self.assertTrue(any("ambiguity" in issue for issue in report["issues"]))
        self.assertTrue(any("distinct" in issue for issue in report["issues"]))

    def test_malformed_review_values_are_retained_as_incomplete_not_false_success(self):
        packet = self.make_review_export()
        paths, roster = self.completed_test_reviews(packet)
        rows = read_jsonl(paths[0])
        rows[0]["reviewer_code"] = []
        rows[1]["verdict"] = []
        rows[1]["criteria"][0]["criterion_id"] = []
        write_jsonl(paths[0], rows)
        report = check_reviews(packet, paths, roster, self.root / "bad-values")
        self.assertEqual(report["status"], "INCOMPLETE")

    def test_blinded_packet_checksum_mismatch_and_export_overwrite_rejected(self):
        packet = self.make_review_export()
        with self.assertRaisesRegex(ValueError, "exists"):
            export_review(self.store, packet.parent)
        cases = packet / "cases.jsonl"
        cases.write_bytes(cases.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "changed"):
            check_reviews(packet, [], packet / "reviewers-template.json", self.root / "no-check")

    def test_human_readable_review_case_tampering_is_also_detected(self):
        packet = self.make_review_export()
        document = packet / "RC0001.md"
        document.write_text(document.read_text(encoding="utf-8") + "Changed human-readable facts", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            check_reviews(packet, [], packet / "reviewers-template.json", self.root / "changed-readable")


if __name__ == "__main__":
    unittest.main()
