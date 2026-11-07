"""Scripted input-only walkthrough and source-verified replay for G4 engineering."""

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from .native_data import digest, file_hash
from .native_runner import append_event, atomic_json, now, read_events, run_lock
from .pharma_engine import PharmaEngine, PharmaStore
from .pharma_rules import assess_visible


def code_hashes():
    return {name: file_hash(Path(__file__).with_name(name)) for name in
            ("pharma.py", "pharma_authoring.py", "pharma_engine.py", "pharma_rules.py", "pharma_eval.py", "pharma_review.py", "pharma_runner.py")}


def visible_action(observation):
    for record_id in ("D1", "D2", "D3", "D4", "D5", "D6", "D7"):
        record = next(row for row in observation["catalog"] if row["id"] == record_id)
        if not record["requested"]:
            if record["cost"] > observation["budget"]["remaining"]:
                return {"type": "abstain", "reason": "Acquisition budget exhausted before the scripted full-packet walkthrough."}
            return {"type": "request", "record_id": record_id}
    observed = assess_visible(observation["case"], observation["evidence"], observation["responses"])
    if observed["verdict"] == "ambiguous" or not observed["protocol_visible"] or any(
            row["status"] == "exposure_cap_not_delivered" for row in observation["responses"]):
        return {"type": "abstain", "reason": "Unresolved procedure interpretation or acquisition limit; retain for human review."}
    citations = [{"record_id": "D1", "pointer": "/facts/criteria"}]
    for row in observed["criteria"]:
        if row["status"] in {"pass", "fail"}:
            citation = {"record_id": row["record_id"], "pointer": row["pointer"]}
        elif row["reason"] in {"scope_mismatch", "after_assessment_cutoff"}:
            citation = {"record_id": row["record_id"], "pointer": "/scope" if row["reason"] == "scope_mismatch" else "/recorded_at"}
        else:
            continue
        if citation not in citations:
            citations.append(citation)
    return {"type": "submit", "verdict": observed["verdict"], "citations": citations,
            "rationale": "Engineering-only application of the acquired synthetic SOP and structured facts; not independent pharmaceutical judgment."}


def exercise(pack, output):
    output = Path(output)
    if output.exists():
        raise ValueError("Walkthrough output exists; select a new directory")
    store = PharmaStore(pack)
    output.mkdir(parents=True)
    config = {"pack_sha256": file_hash(store.directory / "PACK.json"), "case_ids": list(store.case_ids()),
              "code_sha256": code_hashes(), "policy": "acquire-all-then-declared-rules-v1", "max_actions_per_case": 16,
              "llm_calls": 0, "cost_usd": "0", "scientific_performance_claim": False}
    with run_lock(output):
        atomic_json(output / "manifest.json", {"created_utc": now(), "config": config, "config_sha256": digest(config)})
        events, terminal = [], []
        for case_id in store.case_ids():
            engine = PharmaEngine(store, case_id)
            for _ in range(config["max_actions_per_case"]):
                before = engine.observation()
                if before["status"] == "completed":
                    break
                action = visible_action(deepcopy(before))
                after = engine.apply(action)
                append_event(output / "events.jsonl", events, kind="pharma_transition", case_id=case_id,
                             config_sha256=digest(config), before_sha256=digest(before), action=action,
                             observation=after, after_sha256=digest(after))
            if engine.observation()["status"] != "completed":
                raise ValueError("Scripted walkthrough exceeded its action limit")
            terminal.append(engine.observation())
        summary = {"cases": len(terminal), "families": len(store.splits["groups"]), "transitions": len(events),
                   "decisions": dict(Counter(o["decision"].get("verdict", "abstain") for o in terminal)),
                   "llm_calls": 0, "cost_usd": "0", "engineering_only": True,
                   "reference_read": False, "last_event_sha256": events[-1]["sha256"]}
        atomic_json(output / "SUMMARY.json", summary)
        return summary


def replay(store, output):
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    config = manifest["config"]
    if manifest["config_sha256"] != digest(config) or config["pack_sha256"] != file_hash(store.directory / "PACK.json") or config["code_sha256"] != code_hashes():
        raise ValueError("Pharma run/pack/code manifest mismatch")
    if config["case_ids"] != list(store.case_ids()):
        raise ValueError("Pharma walkthrough cohort mismatch")
    engines = {case_id: PharmaEngine(store, case_id) for case_id in store.case_ids()}
    events = read_events(output / "events.jsonl")
    actions = Counter()
    for event in events:
        if event["kind"] != "pharma_transition" or event["config_sha256"] != digest(config) or event["case_id"] not in engines:
            raise ValueError("Foreign pharma transition")
        engine = engines[event["case_id"]]
        actions[event["case_id"]] += 1
        if actions[event["case_id"]] > config["max_actions_per_case"] or digest(engine.observation()) != event["before_sha256"]:
            raise ValueError("Pharma before-state/action cap mismatch")
        after = engine.apply(event["action"])
        if after != event["observation"] or digest(after) != event["after_sha256"]:
            raise ValueError("Pharma source response does not replay")
    observations = [engine.observation() for engine in engines.values()]
    if any(row["status"] != "completed" for row in observations):
        raise ValueError("Incomplete walkthrough; retain raw events and rerun in a new directory")
    return observations, events


def score_exercise(pack, output):
    from .pharma_eval import evaluate_terminal

    output, store = Path(output), PharmaStore(pack)
    with run_lock(output):
        observations, events = replay(store, output)
        results = [evaluate_terminal(store, observation) for observation in observations]
        report = {"cases": len(results), "transitions_replayed": len(events),
                  "unique_author_candidates": sum(row["candidate_verdict"] is not None for row in results),
                  "ambiguous_preflagged": sum(row["ambiguity_preflagged"] for row in results),
                  "candidate_matches": sum(row["label_matches_candidate"] is True for row in results),
                  "independent_review_completed": False, "scientific_performance_claim": False,
                  "interpretation": "Coauthored executable constraints and fixture consistency only; not held-out pharmaceutical/model performance.",
                  "llm_calls": 0, "cost_usd": "0"}
        atomic_json(output / "EVALUATION.json", {"summary": report, "terminal_evaluations": results})
        (output / "REPORT.md").write_text("# G4 case-pack engineering walkthrough\n\n" + report["interpretation"] + "\n\n" +
            f"Cases: {len(results)} from six construction families. Transitions replayed: {len(events)}. " +
            f"Unambiguous authored candidates: {report['unique_author_candidates']}; preflagged ambiguous: {report['ambiguous_preflagged']}.\n\n" +
            "No LLM calls, paid APIs, expert review or pharmaceutical validation were performed. " +
            "Independent annotation, adjudication and a frozen reference version are still required before a domain study.\n", encoding="utf-8")
        return report
