from copy import deepcopy
import json
import unittest

from qa_war_room.benchmark import run_benchmark
from qa_war_room.engine import EngineError, SessionEngine, report_markdown
from qa_war_room.policies import next_action
from qa_war_room.store import FixtureStore


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = SessionEngine()
        self.initial = self.engine.create("MFG-001")
        self.sid = self.initial["session_id"]

    def assert_error(self, code, function, *args):
        with self.assertRaises(EngineError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)

    def finish_policy(self, state):
        for _ in range(12):
            if state["status"] == "completed":
                return state
            state = self.engine.step(state["session_id"])
        self.fail("Scripted policy did not terminate within its finite action bound.")

    def test_initial_state_and_case_list_exclude_evidence_and_references(self):
        self.assertEqual(self.initial["evidence"], [])
        self.assertIsNone(self.initial["feedback"])
        self.assertIsNone(self.initial["decision"])
        serialized = json.dumps({"state": self.initial, "cases": self.engine.list_cases()})
        for forbidden in ("expected_verdict", "support_sets", "unavailable_reason", "acceptance_pass", "template_group"):
            self.assertNotIn(forbidden, serialized)
        self.assertTrue(all("available" not in item and "content" not in item
                            and "facts" not in item for item in self.initial["catalog"]))

    def test_request_discloses_only_one_record_and_owner_response(self):
        state = self.engine.request(self.sid, "D4")
        self.assertEqual([record["id"] for record in state["evidence"]], ["D4"])
        self.assertEqual(state["budget"], {"total": 8, "spent": 2, "remaining": 6})
        delivered = state["events"][-1]
        self.assertEqual(delivered["type"], "evidence_delivered")
        self.assertEqual(delivered["role"], "user-02")
        self.assertIsNone(state["feedback"])
        self.assertNotIn("expected_verdict", json.dumps(state))

    def test_acquisition_retry_is_idempotent(self):
        first = self.engine.request(self.sid, "D4")
        second = self.engine.request(self.sid, "D4")
        self.assertEqual(first, second)

    def test_unavailable_record_is_charged_once_and_not_delivered(self):
        state = self.engine.create("MFG-003")
        state = self.engine.request(state["session_id"], "D4")
        self.assertEqual(state["evidence"], [])
        self.assertEqual(state["budget"]["spent"], 2)
        self.assertEqual(state["events"][-1]["type"], "evidence_unavailable")
        self.assertTrue(next(item for item in state["catalog"] if item["id"] == "D4")["requested"])
        self.assertEqual(state, self.engine.request(state["session_id"], "D4"))

    def test_unknown_id_and_path_attempt_do_not_change_budget_or_state(self):
        for invalid in ("D99", "../../evaluator/gold.json", "/etc/passwd"):
            self.assert_error("unknown_evidence", self.engine.request, self.sid, invalid)
        self.assert_error("invalid_evidence_id", self.engine.request, self.sid, {"id": "D1"})
        self.assertEqual(self.engine.state(self.sid), self.initial)

    def test_budget_cannot_be_overspent_or_mutated_on_failure(self):
        for evidence_id in ("D1", "D2", "D3", "D4", "D5", "D6", "D7"):
            state = self.engine.request(self.sid, evidence_id)
        self.assertEqual(state["budget"]["remaining"], 0)
        self.assert_error("budget_exceeded", self.engine.request, self.sid, "D8")
        self.assertEqual(self.engine.state(self.sid), state)

    def test_budget_rejects_expensive_request_even_when_some_credit_remains(self):
        for evidence_id in ("D1", "D2", "D3", "D5", "D6", "D7", "D8"):
            state = self.engine.request(self.sid, evidence_id)
        self.assertEqual(state["budget"]["remaining"], 1)
        self.assert_error("budget_exceeded", self.engine.request, self.sid, "D4")
        self.assertEqual(self.engine.state(self.sid), state)

    def test_returned_snapshots_are_detached_from_internal_state(self):
        state = self.engine.request(self.sid, "D4")
        state["evidence"][0]["facts"]["acceptance_pass"] = False
        state["budget"]["remaining"] = 999
        state["catalog"][0]["cost"] = -99
        state["events"].clear()
        fresh = self.engine.state(self.sid)
        self.assertTrue(fresh["evidence"][0]["facts"]["acceptance_pass"])
        self.assertEqual(fresh["budget"]["remaining"], 6)
        self.assertEqual(fresh["catalog"][0]["cost"], 1)
        self.assertGreater(len(fresh["events"]), 1)

    def test_sessions_do_not_share_evidence_or_actions(self):
        other = self.engine.create("MFG-002")
        self.engine.request(self.sid, "D4")
        self.assertEqual(self.engine.state(other["session_id"])["evidence"], [])
        other = self.engine.request(other["session_id"], "D4")
        self.assertFalse(other["evidence"][0]["facts"]["acceptance_pass"])
        self.assertTrue(self.engine.state(self.sid)["evidence"][0]["facts"]["acceptance_pass"])

    def test_decision_requires_retrieved_citations_and_valid_payload(self):
        self.assert_error("unretrieved_citation", self.engine.decide, self.sid, "supported", ["D4"], "I assume it passes.")
        self.assert_error("citation_required", self.engine.decide, self.sid, "supported", [], "No evidence.")
        self.assert_error("invalid_verdict", self.engine.decide, self.sid, "compliant", [], "Wrong task label.")
        self.assert_error("invalid_citations", self.engine.decide, self.sid, "insufficient", "D1", "Wrong type.")
        self.assert_error("invalid_rationale", self.engine.decide, self.sid, "insufficient", [], " ")
        self.assert_error("invalid_rationale", self.engine.decide, self.sid, "insufficient", [], "x" * 8001)
        self.assertEqual(self.engine.state(self.sid), self.initial)

    def test_duplicate_citations_do_not_inflate_score(self):
        self.engine.request(self.sid, "D1")
        self.assert_error("duplicate_citations", self.engine.decide, self.sid, "supported", ["D1", "D1"], "Cover sheet only.")

    def test_valid_citation_is_not_automatically_complete_support(self):
        self.engine.request(self.sid, "D1")
        state = self.engine.decide(self.sid, "supported", ["D1"], "I trusted the cover sheet.")
        self.assertTrue(state["feedback"]["verdict_correct"])
        self.assertFalse(state["feedback"]["evidence_support_complete"])
        self.assertFalse(state["feedback"]["decision_and_support_correct"])
        self.assertIn("D4", state["feedback"]["missing_support"])
        self.assertEqual(state["feedback"]["citations_not_in_reference"], ["D1"])

    def test_insufficient_with_no_evidence_can_match_label_but_not_support(self):
        state = self.engine.create("MFG-003")
        state = self.engine.decide(state["session_id"], "insufficient", [], "I have not investigated yet.")
        self.assertTrue(state["feedback"]["verdict_correct"])
        self.assertFalse(state["feedback"]["evidence_support_complete"])
        self.assertEqual(state["feedback"]["missing_unavailability_checks"], ["D4"])

    def test_missing_record_conclusion_requires_actual_unavailability_check(self):
        state = self.engine.create("MFG-003")
        sid = state["session_id"]
        self.engine.request(sid, "D2")
        state = self.engine.decide(sid, "insufficient", ["D2"], "No report seen yet.")
        self.assertFalse(state["feedback"]["evidence_support_complete"])
        other = self.engine.create("MFG-003")
        sid = other["session_id"]
        self.engine.request(sid, "D2")
        self.engine.request(sid, "D4")
        other = self.engine.decide(sid, "insufficient", ["D2"], "The custodian cannot provide the required report at this cutoff.")
        self.assertTrue(other["feedback"]["decision_and_support_correct"])

    def test_report_is_only_available_after_submission_and_contains_trace(self):
        self.assert_error("report_not_ready", self.engine.report, self.sid)
        self.finish_policy(self.initial)
        report = self.engine.report(self.sid)
        self.assertEqual(report["mode"], "offline_scripted_synthetic_demo")
        self.assertEqual(len(report["evidence_checklist"]), 8)
        self.assertTrue(all(item["locator"].startswith("fixture:MFG-001/") for item in report["source_trace"]))
        markdown = report_markdown(report)
        self.assertIn("Record checklist", markdown)
        self.assertIn("not a semantic entailment assessment", markdown)

    def test_completed_sessions_cannot_be_modified(self):
        state = self.engine.decide(self.sid, "insufficient", [], "Stop before investigation.")
        self.assert_error("session_completed", self.engine.request, self.sid, "D1")
        self.assert_error("session_completed", self.engine.decide, self.sid, "insufficient", [], "Try to edit.")
        self.assert_error("session_completed", self.engine.step, self.sid)
        self.assertEqual(self.engine.state(self.sid), state)

    def test_all_four_scripted_policies_terminate_within_budget(self):
        roles = [persona["id"] for persona in self.engine.personas() if persona["kind"] == "auditor"]
        self.assertEqual(len(roles), 4)
        for role in roles:
            for case in self.engine.list_cases():
                with self.subTest(role=role, case=case["id"]):
                    state = self.finish_policy(self.engine.create(case["id"], role))
                    self.assertGreaterEqual(state["budget"]["remaining"], 0)
                    self.assertEqual(state["status"], "completed")
                    self.assertIsNotNone(state["feedback"])

    def test_policy_receives_and_uses_only_supplied_public_observations(self):
        state = self.initial
        self.assertEqual(next_action(state), {"type": "request", "evidence_id": "D2"})
        state = self.engine.request(self.sid, "D2")
        state = self.engine.request(self.sid, "D4")
        changed = deepcopy(state)
        changed["evidence"][-1]["facts"]["acceptance_pass"] = False
        changed["evidence"][-1]["facts"]["failed_acceptance_batches"] = ["B212"]
        self.assertEqual(next_action(changed)["verdict"], "contradicted")
        self.assertEqual(next_action(state)["type"], "request")
        # A policy call cannot mutate the engine's true records.
        self.assertTrue(self.engine.state(self.sid)["evidence"][-1]["facts"]["acceptance_pass"])

    def test_same_template_counterfactual_changes_only_decisive_artifact(self):
        store = FixtureStore()
        for evidence_id in ("D1", "D2", "D3", "D5", "D6", "D7", "D8"):
            self.assertEqual(store.evidence("MFG-001", evidence_id), store.evidence("MFG-002", evidence_id))
        self.assertNotEqual(store.evidence("MFG-001", "D4"), store.evidence("MFG-002", "D4"))

    def test_invalid_roles_cases_and_session_limit(self):
        self.assert_error("invalid_role", self.engine.create, "MFG-001", "user-01")
        self.assert_error("unknown_case", self.engine.create, "../../evaluator/gold.json")
        self.assert_error("unknown_session", self.engine.state, "qr_not_a_session")
        bounded = SessionEngine(max_sessions=1)
        bounded.create("MFG-001")
        self.assert_error("session_limit", bounded.create, "MFG-001")

    def test_benchmark_is_deterministic_and_disclaims_scientific_results(self):
        first = run_benchmark()
        second = run_benchmark()
        self.assertEqual(first, second)
        self.assertFalse(first["scientific_performance_claim"])
        self.assertEqual(len(first["episodes"]), 32)
        self.assertEqual(len(first["template_groups"]), 2)
        self.assertIn("gold.json", " ".join(first["fixture_sha256"]))


if __name__ == "__main__":
    unittest.main()
