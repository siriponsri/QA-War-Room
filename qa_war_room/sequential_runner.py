"""Offline sequential matrix, durable transitions and gold-free deterministic replay."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import platform
import time

from .native_data import digest, file_hash
from .native_runner import append_event, atomic_json, now, read_events, run_lock
from .sequential_data import TASK_VERSION, SequentialStore
from .sequential_engine import SequentialEngine, SequentialError
from .sequential_policies import POLICIES, choose_action


def code_hashes() -> dict:
    names = ("sequential.py", "sequential_data.py", "sequential_engine.py", "sequential_policies.py", "sequential_runner.py",
             "sequential_eval.py", "native_data.py", "native_runner.py")
    return {name: file_hash(Path(__file__).with_name(name)) for name in names}


def validate_caps(budgets, max_source_bytes, max_policy_actions, max_episode_actions, limit_groups, seed):
    if (not budgets or any(type(n) is not int or n < 0 for n in budgets) or len(budgets) != len(set(budgets)) or
            any(type(n) is not int or n < 0 for n in (max_source_bytes, max_policy_actions, max_episode_actions)) or
            type(limit_groups) is not int or limit_groups < 1 or type(seed) is not int):
        raise ValueError("Use unique nonnegative budgets/caps, a positive group limit and integer seed")


def create_config(store, split, limit_groups, policies, budgets, max_source_bytes,
                  max_policy_actions, max_episode_actions, seed):
    validate_caps(budgets, max_source_bytes, max_policy_actions, max_episode_actions, limit_groups, seed)
    if not policies or len(policies) != len(set(policies)) or any(p not in POLICIES for p in policies):
        raise ValueError("Choose unique registered offline wiring policies")
    episodes = store.cohort(split, limit_groups)
    if not episodes:
        raise ValueError("Derived split has no eligible source families")
    cohort = [{"key": digest([e["id"], budget, policy])[:32], "episode_id": e["id"],
               "source_family_id": e["source_family_id"], "source_id": e["source_id"],
               "credits": budget, "policy": policy}
              for e in episodes for budget in sorted(budgets) for policy in policies]
    if len({r["key"] for r in cohort}) != len(cohort):
        raise ValueError("Run key collision")
    return {"schema": "sequential-run-v1", "task_version": TASK_VERSION, "track": "derived_sequential",
            "native_benchmark_score": False, "scientific_performance_claim": False, "study_status": "development_only",
            "pack_sha256": file_hash(store.directory / "PACK.json"), "derived_split": split,
            "limit_groups": limit_groups, "cohort": cohort, "policies": list(policies), "budgets": sorted(budgets),
            "max_source_bytes": max_source_bytes, "max_policy_actions": max_policy_actions,
            "max_episode_actions": max_episode_actions, "seed": seed,
            "implementation_sha256": code_hashes(), "llm_calls": 0, "cost_cap_usd": "0",
            "failure_policy": "Strict invalid actions fail terminally; no retries; pending/failures stay in denominator.",
            "checkpoint_policy": "Only completed deterministic local transitions are journaled; replay has no external side effects."}


def initial_engines(store, config):
    return {row["key"]: SequentialEngine(store, row["episode_id"], row["credits"], config["max_source_bytes"])
            for row in config["cohort"]}


def apply_recorded(engine, event):
    if event["internal_failure"]:
        return engine.fail(event["internal_failure"])
    try:
        result = engine.apply(deepcopy(event["action"]))
    except SequentialError as error:
        if error.code != event["error_code"]:
            raise ValueError("Recorded action error does not replay") from error
        return engine.fail("invalid_policy_action")
    if event["error_code"] is not None:
        raise ValueError("Recorded error contradicts successful transition")
    return result


def replay_events(store, config, events):
    engines = initial_engines(store, config)
    policy_counts = Counter()
    config_hash = digest(config)
    for event in events:
        if event.get("kind") != "sequential_transition" or event.get("config_sha256") != config_hash:
            raise ValueError("Sequential ledger belongs to a different task/run")
        key = event["key"]
        if key not in engines:
            raise ValueError("Transition outside frozen cohort")
        engine = engines[key]
        if digest(engine.observation()) != event["before_sha256"]:
            raise ValueError("Sequential before-observation mismatch")
        if type(event["policy_call"]) is not bool or event["internal_failure"] not in (
                None, "episode_action_cap", "policy_error", "invalid_policy_action"):
            raise ValueError("Invalid transition accounting")
        if event["internal_failure"] == "episode_action_cap":
            if event["policy_call"] or policy_counts[key] < config["max_episode_actions"]:
                raise ValueError("Invalid forced action-cap termination")
        elif not event["policy_call"]:
            raise ValueError("A non-forced transition must account for a policy action")
        if event["policy_call"]:
            if (sum(policy_counts.values()) >= config["max_policy_actions"] or
                    policy_counts[key] >= config["max_episode_actions"]):
                raise ValueError("Ledger exceeds policy-action cap")
            policy_counts[key] += 1
        observation = apply_recorded(engine, event)
        if digest(observation) != event["after_sha256"] or observation != event["observation"]:
            raise ValueError("Sequential returned observation does not replay")
    return engines, policy_counts


def load_replay(store: SequentialStore, output: Path):
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    config = manifest["config"]
    if manifest["config_sha256"] != digest(config) or config["task_version"] != TASK_VERSION:
        raise ValueError("Sequential manifest integrity mismatch")
    if file_hash(store.directory / "PACK.json") != config["pack_sha256"]:
        raise ValueError("Derived bundle changed since run")
    if config["implementation_sha256"] != code_hashes():
        raise ValueError("Replay code changed; use the recorded source version or a new run")
    # Rebuild the cohort, including source-family boundaries, before replaying.
    expected = create_config(store, config["derived_split"], config["limit_groups"], config["policies"],
                             config["budgets"], config["max_source_bytes"], config["max_policy_actions"],
                             config["max_episode_actions"], config["seed"])
    if config != expected:
        raise ValueError("Frozen sequential cohort/config mismatch")
    events = read_events(output / "events.jsonl")
    engines, counts = replay_events(store, config, events)
    return manifest, events, engines, counts


def run_sequential(bundle: Path, output: Path, *, split="dev", limit_groups=1,
                   budgets=(0, 2, 4), policies=POLICIES, max_source_bytes=2_000_000,
                   max_policy_actions=10_000, max_episode_actions=256, seed=0,
                   resume=False, stop_after_actions=None):
    if stop_after_actions is not None and (type(stop_after_actions) is not int or stop_after_actions < 1):
        raise ValueError("stop_after_actions must be a positive transition count")
    store = SequentialStore(bundle)
    config = create_config(store, split, limit_groups, policies, budgets, max_source_bytes,
                           max_policy_actions, max_episode_actions, seed)
    output = Path(output)
    if output.exists() and not resume:
        raise ValueError("Sequential run exists; choose a new directory or --resume")
    if resume and not (output / "manifest.json").is_file():
        raise ValueError("No sequential run to resume")
    output.mkdir(parents=True, exist_ok=True)
    with run_lock(output):
        if resume:
            manifest, events, engines, counts = load_replay(store, output)
            if manifest["config"] != config:
                raise ValueError("Resume config differs; preserve the old run and use a new directory")
        else:
            manifest = {"created_utc": now(), "python": platform.python_version(),
                        "config": config, "config_sha256": digest(config)}
            atomic_json(output / "manifest.json", manifest)
            events, engines, counts = [], initial_engines(store, config), Counter()
        processed, status = 0, "complete"
        for row in config["cohort"]:
            key, engine = row["key"], engines[row["key"]]
            while engine.observation()["status"] == "active":
                if stop_after_actions is not None and processed >= stop_after_actions:
                    status = "checkpointed"
                    break
                before = engine.observation()
                started = time.monotonic()
                action, internal_failure, error_code = None, None, None
                policy_call = counts[key] < max_episode_actions
                if not policy_call:
                    internal_failure = "episode_action_cap"
                elif sum(counts.values()) >= max_policy_actions:
                    status = "policy_action_budget_stopped"
                    break
                else:
                    counts[key] += 1
                    try:
                        action = choose_action(deepcopy(before), row["policy"], seed)
                        serialized = json.dumps(action, ensure_ascii=False, allow_nan=False)
                        if len(serialized.encode("utf-8")) > 16_384:
                            action, internal_failure, error_code = None, "invalid_policy_action", "action_too_large"
                    except Exception as error:
                        action, internal_failure, error_code = None, "policy_error", type(error).__name__
                if internal_failure:
                    after = engine.fail(internal_failure)
                else:
                    try:
                        after = engine.apply(deepcopy(action))
                    except SequentialError as error:
                        error_code = error.code
                        after = engine.fail("invalid_policy_action")
                append_event(output / "events.jsonl", events, kind="sequential_transition", key=key,
                             config_sha256=manifest["config_sha256"], policy_call=policy_call,
                             action=action, internal_failure=internal_failure, error_code=error_code,
                             before_sha256=digest(before), after_sha256=digest(after), observation=after,
                             wall_seconds=time.monotonic() - started)
                processed += 1
            if status != "complete":
                break
        observations = [engine.observation() for engine in engines.values()]
        summary = {"updated_utc": now(), "status": status, "task_version": TASK_VERSION,
                   "matrix_episodes": len(observations),
                   "source_episodes": len({r["episode_id"] for r in config["cohort"]}),
                   "source_documents": len({r["source_id"] for r in config["cohort"]}),
                   "source_families": len({r["source_family_id"] for r in config["cohort"]}),
                   "terminal": sum(o["status"] != "active" for o in observations),
                   "pending": sum(o["status"] == "active" for o in observations),
                   "policy_actions": sum(counts.values()), "logged_transitions": len(events),
                   "credits_spent": sum(o["budget"]["credits_spent"] for o in observations),
                   "source_bytes_exposed": sum(o["budget"]["source_bytes_exposed"] for o in observations),
                   "llm_calls": 0, "model_tokens": 0, "cost_usd": "0",
                   "scientific_performance_claim": False,
                   "last_event_sha256": events[-1]["sha256"] if events else None}
        atomic_json(output / "run-summary.json", summary)
        return summary


def replay_run(bundle: Path, output: Path, episode_ordinal: int | None = None):
    """Verify journaled source responses without invoking policy or evaluator."""
    store = SequentialStore(bundle)
    with run_lock(output):
        manifest, events, engines, counts = load_replay(store, output)
        result = {"status": "replay_verified", "transitions": len(events),
                  "matrix_episodes": len(engines), "policy_actions": sum(counts.values()),
                  "gold_read": False, "policy_invoked": False}
        if episode_ordinal is not None:
            cohort = manifest["config"]["cohort"]
            if type(episode_ordinal) is not int or not 1 <= episode_ordinal <= len(cohort):
                raise ValueError("Episode ordinal must be within the frozen matrix (1-based)")
            result["observation"] = engines[cohort[episode_ordinal - 1]["key"]].observation()
        return result
