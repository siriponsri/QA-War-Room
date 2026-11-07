"""Gold-free, matched-budget engineering matrix with resumable source replay."""

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import platform
import time

from .native_data import digest, file_hash
from .native_runner import append_event, atomic_json, now, read_events, run_lock
from .pharma_engine import PharmaEngine, PharmaError
from .study_plan import load_lock
from .study_policies import choose_action


def apply_action(engine, action):
    # Preserve the existing G4 source snapshot while rejecting unhashable labels.
    if isinstance(action, dict) and action.get("type") == "submit" and not isinstance(action.get("verdict"), str):
        raise PharmaError("invalid_submission_fields")
    return engine.apply(deepcopy(action))


def engines_for(store, config):
    maximum = config["plan"]["engineering"]["max_source_bytes_per_job"]
    return {job["key"]: PharmaEngine(store, job["case_id"], credits=job["credits"], max_source_bytes=maximum) for job in config["jobs"]}


def replay_events(store, config, events):
    engines = engines_for(store, config)
    counts, failed, seconds = Counter(), {}, Counter()
    limits = config["plan"]["engineering"]
    for event in events:
        if event.get("kind") != "study_step" or event.get("lock_config_sha256") != digest(config) or event.get("key") not in engines:
            raise ValueError("Foreign engineering study transition")
        key = event["key"]
        engine = engines[key]
        if key in failed or engine.observation()["status"] != "active" or digest(engine.observation()) != event["before_sha256"]:
            raise ValueError("Study before-state/terminal transition mismatch")
        if type(event["policy_call"]) is not bool:
            raise ValueError("Invalid policy-action accounting")
        if event["policy_call"]:
            if counts[key] >= limits["max_actions_per_job"] or sum(counts.values()) >= limits["max_policy_actions"]:
                raise ValueError("Journal exceeds frozen action caps")
            counts[key] += 1
        elif event["status"] != "action_cap" or counts[key] < limits["max_actions_per_job"]:
            raise ValueError("Unjustified non-policy transition")
        status = event["status"]
        if status == "ok":
            after = apply_action(engine, event["action"])
        elif status == "invalid_action":
            if event["action"] is not None:
                try:
                    apply_action(engine, event["action"])
                except PharmaError as error:
                    if str(error) != event["error_code"]:
                        raise ValueError("Recorded validation error differs") from error
                else:
                    raise ValueError("Invalid action unexpectedly replays as valid")
            elif event["error_code"] not in {"invalid_serialization", "action_too_large"}:
                raise ValueError("Unexplained omitted invalid action")
            failed[key] = status
            after = engine.observation()
        elif status in {"policy_error", "action_cap"}:
            if event["action"] is not None:
                raise ValueError("Runtime failure must not contain a successful action")
            failed[key] = status
            after = engine.observation()
        else:
            raise ValueError("Unknown study step status")
        if after != event["observation"] or digest(after) != event["after_sha256"]:
            raise ValueError("Study source response does not replay")
        wall = event["wall_seconds"]
        if type(wall) not in (int, float) or not 0 <= wall < float("inf"):
            raise ValueError("Invalid runtime duration")
        seconds[key] += wall
    return engines, counts, failed, seconds


def load_run(pack, lock, output):
    locked, store = load_lock(pack, lock)
    config = locked["config"]
    manifest = json.loads((Path(output) / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("kind") != "engineering_development_only" or
            manifest["lock_sha256"] != file_hash(Path(lock) / "LOCK.json") or manifest["lock_config_sha256"] != digest(config)):
        raise ValueError("Run does not belong to this engineering lock")
    events = read_events(Path(output) / "events.jsonl")
    engines, counts, failed, seconds = replay_events(store, config, events)
    return config, store, events, engines, counts, failed, seconds


def run_matrix(pack, lock, output, *, resume=False, stop_after=None):
    if stop_after is not None and (type(stop_after) is not int or stop_after < 1):
        raise ValueError("stop_after must be a positive transition count")
    locked, store = load_lock(pack, lock)
    config, output = locked["config"], Path(output)
    limits = config["plan"]["engineering"]
    if output.exists() and not resume:
        raise ValueError("Study run exists; use --resume or a new directory")
    if resume and not (output / "manifest.json").is_file():
        raise ValueError("No engineering run to resume")
    output.mkdir(parents=True, exist_ok=True)
    with run_lock(output):
        if resume:
            _, _, events, engines, counts, failed, seconds = load_run(pack, lock, output)
        else:
            atomic_json(output / "manifest.json", {"created_utc": now(), "kind": "engineering_development_only",
                "python": platform.python_version(), "platform": platform.platform(),
                "lock_sha256": file_hash(Path(lock) / "LOCK.json"), "lock_config_sha256": digest(config)})
            events, engines, counts, failed, seconds = [], engines_for(store, config), Counter(), {}, Counter()
        transitions, state = 0, "complete"
        for job in config["jobs"]:
            key, engine = job["key"], engines[job["key"]]
            while key not in failed and engine.observation()["status"] == "active":
                if stop_after is not None and transitions >= stop_after:
                    state = "checkpointed"
                    break
                before = engine.observation()
                status, action, error_code = "ok", None, None
                policy_call = counts[key] < limits["max_actions_per_job"]
                if not policy_call:
                    status = "action_cap"
                elif sum(counts.values()) >= limits["max_policy_actions"]:
                    state = "policy_action_budget_stopped"
                    break
                started = time.monotonic()
                if policy_call:
                    counts[key] += 1
                    try:
                        action = choose_action(deepcopy(before), job["method"], limits["seed"] + job["repetition"])
                    except Exception as error:
                        status, error_code = "policy_error", type(error).__name__
                    if status == "ok":
                        try:
                            raw = json.dumps(action, ensure_ascii=False, allow_nan=False)
                        except (TypeError, ValueError):
                            action, status, error_code = None, "invalid_action", "invalid_serialization"
                        else:
                            if len(raw.encode("utf-8")) > 16384:
                                action, status, error_code = None, "invalid_action", "action_too_large"
                            else:
                                action = json.loads(raw)
                    if status == "ok":
                        try:
                            apply_action(engine, action)
                        except PharmaError as error:
                            status, error_code = "invalid_action", str(error)
                after = engine.observation()
                if status != "ok":
                    failed[key] = status
                wall = time.monotonic() - started
                seconds[key] += wall
                append_event(output / "events.jsonl", events, kind="study_step", key=key,
                    lock_config_sha256=digest(config), policy_call=policy_call, action=action, status=status,
                    error_code=error_code, before_sha256=digest(before), after_sha256=digest(after),
                    observation=after, wall_seconds=wall)
                transitions += 1
            if state != "complete":
                break
        terminal = sum(key in failed or engine.observation()["status"] == "completed" for key, engine in engines.items())
        summary = {"status": state, "jobs": len(engines), "terminal": terminal, "pending": len(engines) - terminal,
                   "runtime_failures": dict(Counter(failed.values())), "policy_actions": sum(counts.values()),
                   "transitions": len(events), "source_cases": len(config["cohort"]),
                   "construction_families": len({row["family_id"] for row in config["cohort"]}),
                   "llm_calls": 0, "model_tokens": 0, "cost_usd": "0", "scientific_performance_claim": False,
                   "last_event_sha256": events[-1]["sha256"] if events else None}
        atomic_json(output / "SUMMARY.json", summary)
        return summary


def replay_matrix(pack, lock, output):
    with run_lock(Path(output)):
        config, _, events, _, counts, failed, _ = load_run(pack, lock, output)
        return {"status": "replay_verified", "jobs": len(config["jobs"]), "transitions": len(events),
                "policy_actions": sum(counts.values()), "runtime_failures": len(failed),
                "policy_invoked": False, "gold_read": False}
