"""Append-only, resumable native runs. Gold is read only by score_run()."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import platform
import time

from .models import ModelAdapter, OfflineAdapter, Usage, validate_prediction
from .native_data import (INPUT_VERSION, ROOT, build_request, checked_file, digest, file_hash,
                          load_drugqa_prompt, load_inputs, read_jsonl)

RUN_VERSION = "native-run-v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Caps:
    max_calls: int = 50
    max_input_tokens: int = 100_000
    max_output_tokens: int = 50_000
    max_cost_usd: str = "0"
    max_item_input_bytes: int = 500_000
    max_item_output_tokens: int = 1024
    max_item_cost_usd: str = "0"

    def validate(self):
        for key, value in asdict(self).items():
            if key.endswith("usd"):
                Usage(cost_usd=value).validate()
            elif type(value) is not int or value < 0:
                raise ValueError("Caps must be nonnegative integers")


def atomic_json(path: Path, value: dict):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


@contextmanager
def run_lock(directory: Path):
    path = directory / ".writer.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise ValueError("Run is locked. Check the recorded PID before manually removing a stale .writer.lock.") from error
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(json.dumps({"pid": os.getpid(), "created_utc": now()}))
        yield
    finally:
        path.unlink()


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError("Torn ledger tail: preserve events.jsonl and inspect before recovery; no calls repeated")
    events = []
    previous = None
    for line in data.splitlines():
        event = json.loads(line)
        claimed = event.pop("sha256")
        if event.get("seq") != len(events) + 1 or event.get("previous") != previous or digest(event) != claimed:
            raise ValueError("Ledger integrity mismatch")
        event["sha256"] = claimed
        previous = claimed
        events.append(event)
    return events


def append_event(path: Path, events: list[dict], **fields):
    event = {"seq": len(events) + 1, "previous": events[-1]["sha256"] if events else None,
             "utc": now(), **fields}
    event["sha256"] = digest(event)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    events.append(event)


def ledger_state(events: list[dict], cohort: list[str]) -> tuple[dict, dict]:
    starts, finishes = {}, {}
    for event in events:
        item_id = event["id"]
        if item_id not in cohort:
            raise ValueError("Ledger item outside frozen cohort")
        if event["kind"] == "attempt_started":
            if item_id in starts or item_id in finishes:
                raise ValueError("Duplicate attempt; zero-retry policy violated")
            Usage(**event["reservation"]).validate()
            starts[item_id] = event
        elif event["kind"] == "item_finished":
            if item_id in finishes:
                raise ValueError("Duplicate terminal item")
            if event.get("usage") is not None:
                if item_id not in starts:
                    raise ValueError("Unreserved usage")
                Usage(**event["usage"]).validate()
            finishes[item_id] = event
        else:
            raise ValueError("Unknown ledger event")
    usage = {"calls": len(starts), "input_tokens": 0, "output_tokens": 0, "cost_usd": "0"}
    for item_id, start in starts.items():
        # Failed/abandoned calls retain the full reservation when actual usage is unknown.
        charged = finishes.get(item_id, {}).get("usage") or start["reservation"]
        usage["input_tokens"] += charged["input_tokens"]
        usage["output_tokens"] += charged["output_tokens"]
        usage["cost_usd"] = str(Decimal(usage["cost_usd"]) + Decimal(charged["cost_usd"]))
    return finishes, usage


def implementation_hashes() -> dict:
    # Changes to parsing/retrieval/evaluation cannot silently reuse an old run.
    return {name: file_hash(Path(__file__).with_name(name)) for name in
            ("native_runner.py", "native_data.py", "models.py", "native_metrics.py")}


def run_native(data: Path, dataset: str, split: str, output: Path, *,
               baseline: str = "full-context", limit: int = 17, top_k: int = 5,
               caps: Caps | None = None, protocols: Path | None = None,
               resume: bool = False, stop_after: int | None = None,
               adapter: ModelAdapter | None = None) -> dict:
    caps = caps or Caps()
    caps.validate()
    if type(limit) is not int or limit < 1 or type(top_k) is not int or top_k < 1:
        raise ValueError("limit and top_k must be positive integers")
    if stop_after is not None and (type(stop_after) is not int or stop_after < 1):
        raise ValueError("stop_after must be positive")
    observations, preparation = load_inputs(data, dataset, split)
    adapter = adapter or OfflineAdapter()
    identity = adapter.identity()
    if identity.get("provider") != "offline" or identity.get("llm") is not False:
        raise ValueError("Only offline adapters are enabled; paid inference needs a separately authorized implementation")
    if dataset == "contractnli":
        # Limit independent documents, keeping every hypothesis for each selected contract.
        groups = list(dict.fromkeys(row["document_id"] for row in observations))[:limit]
        selected = [row for row in observations if row["document_id"] in groups]
        selection = {"unit": "original_document", "count": len(groups), "method": "source_order_prefix"}
    else:
        selected = observations[:limit]
        selection = {"unit": "item", "count": len(selected), "method": "source_order_prefix",
                     "held_out": False, "note": "No official dev split; smoke only, not tuning or training."}
    if not selected:
        raise ValueError("Empty benchmark cohort")
    canonical = load_drugqa_prompt(protocols or ROOT / "benchmark-data/protocols") if dataset == "drugqa" else None
    if dataset == "drugqa" and baseline != "full-context":
        raise ValueError("Retrieval is not the native DrugQA zero-shot setting")
    if baseline not in {"full-context", "lexical-retrieval"}:
        raise ValueError("Unknown baseline")
    config = {"schema": RUN_VERSION, "dataset": dataset, "split": split,
              "baseline": baseline, "top_k": top_k, "selection": selection,
              "limit": limit, "cohort": [{"id": r["id"], "input_sha256": digest(r),
                  **({"document_id": r["document_id"], "hypothesis_id": r["hypothesis_id"], "span_count": len(r["spans"])}
                     if dataset == "contractnli" else {"language": r["language"]})} for r in selected],
              "source_commits": preparation["source_commits"],
              "preparation_sha256": file_hash(data / "PREPARATION_REPORT.json"),
              "input_builder": INPUT_VERSION, "prompt_sha256": digest(canonical),
              "implementation_sha256": implementation_hashes(), "model": identity, "caps": asdict(caps),
              "retry_policy": "zero_retries; failures terminal; interrupted calls charged at reservation",
              "study_status": "development_only", "scientific_performance_claim": False}
    output = Path(output)
    if output.exists() and not resume:
        raise ValueError("Output exists; choose a new run directory or explicitly --resume")
    if resume and not (output / "manifest.json").is_file():
        raise ValueError("No manifest to resume")
    output.mkdir(parents=True, exist_ok=True)
    with run_lock(output):
        manifest_path, log_path = output / "manifest.json", output / "events.jsonl"
        if resume:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest["config"] != config or manifest["config_sha256"] != digest(config):
                raise ValueError("Resume config/data/code/prompt/caps differ; use a new run directory")
        else:
            manifest = {"created_utc": now(), "python": platform.python_version(),
                        "platform": platform.platform(), "config": config, "config_sha256": digest(config)}
            atomic_json(manifest_path, manifest)
        events = read_events(log_path)
        if any(e.get("config_sha256") != manifest["config_sha256"] for e in events):
            raise ValueError("Ledger belongs to a different frozen run")
        def emit(**fields):
            append_event(log_path, events, config_sha256=manifest["config_sha256"], **fields)
        ids = [r["id"] for r in selected]
        finished, usage = ledger_state(events, ids)
        for event in list(events):
            if event["kind"] == "attempt_started" and event["id"] not in finished:
                emit(kind="item_finished", id=event["id"],
                             status="interrupted_unknown_usage", usage=event["reservation"], raw=None, prediction=None)
        finished, usage = ledger_state(events, ids)
        processed, status = 0, "complete"
        violation = any(e.get("status") == "usage_bound_violation" for e in finished.values())
        if violation:
            status = "usage_bound_violation"
        for observation in ([] if violation else selected):
            item_id = observation["id"]
            if item_id in finished:
                continue
            if stop_after is not None and processed >= stop_after:
                status = "paused_after_items"
                break
            request = build_request(observation, dataset, baseline, top_k, canonical)
            request_bytes = len(json.dumps(request, ensure_ascii=False).encode("utf-8"))
            if request_bytes > caps.max_item_input_bytes:
                emit(kind="item_finished", id=item_id, status="context_limit",
                             usage=None, raw=None, prediction=None, input_bytes=request_bytes)
                processed += 1
                continue
            reservation = adapter.upper_bound(deepcopy(request), caps.max_item_output_tokens)
            reservation.validate()
            if reservation.output_tokens > caps.max_item_output_tokens or Decimal(reservation.cost_usd) > Decimal(caps.max_item_cost_usd):
                raise ValueError("Adapter bound exceeds the per-item cap")
            _, usage = ledger_state(events, ids)
            if (usage["calls"] + 1 > caps.max_calls or
                    usage["input_tokens"] + reservation.input_tokens > caps.max_input_tokens or
                    usage["output_tokens"] + reservation.output_tokens > caps.max_output_tokens or
                    Decimal(usage["cost_usd"]) + Decimal(reservation.cost_usd) > Decimal(caps.max_cost_usd)):
                status = "budget_stopped"
                break
            emit(kind="attempt_started", id=item_id,
                         request=request, request_sha256=digest(request), input_bytes=request_bytes,
                         reservation=asdict(reservation))
            started = time.monotonic()
            raw, actual, prediction, outcome = None, None, None, "provider_error"
            error_type = None
            try:
                response = adapter.predict(deepcopy(request), caps.max_item_output_tokens)
                response.usage.validate()
                actual = asdict(response.usage)
                raw = response.raw
                if (response.usage.input_tokens > reservation.input_tokens or
                        response.usage.output_tokens > reservation.output_tokens or
                        Decimal(response.usage.cost_usd) > Decimal(reservation.cost_usd)):
                    outcome = "usage_bound_violation"
                else:
                    outcome = "invalid_output"
                    prediction = validate_prediction(raw, request)
                    outcome = "ok"
            except Exception as error:
                # Do not put provider exceptions (which may carry credentials) into logs.
                error_type = type(error).__name__
            # Output is bounded even for a broken adapter; retain a digest and explicit truncation.
            raw_digest = digest(raw) if isinstance(raw, str) else None
            truncated = isinstance(raw, str) and len(raw) > 1_000_000
            if truncated:
                raw = raw[:1_000_000]
            emit(kind="item_finished", id=item_id, status=outcome,
                         usage=actual, raw=raw if isinstance(raw, str) else None,
                         raw_sha256=raw_digest, raw_truncated=truncated, prediction=prediction,
                         error_type=error_type, wall_seconds=time.monotonic() - started)
            processed += 1
            if outcome == "usage_bound_violation":
                status = "usage_bound_violation"
                break
        finished, usage = ledger_state(events, ids)
        summary = {"updated_utc": now(), "status": status, "cohort_size": len(ids),
                   "finished": len(finished), "pending": len(ids) - len(finished),
                   "successful": sum(e["status"] == "ok" for e in finished.values()),
                   "usage": usage, "last_event_sha256": events[-1]["sha256"] if events else None,
                   "study_status": "development_only", "scientific_performance_claim": False}
        atomic_json(output / "run-summary.json", summary)
        return summary


def score_run(data: Path, output: Path) -> dict:
    """Separate evaluator entry point; never calls a model or changes raw events."""
    from .native_metrics import contractnli_metrics, drugqa_metrics

    with run_lock(output):
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        config = manifest["config"]
        if digest(config) != manifest["config_sha256"]:
            raise ValueError("Manifest integrity mismatch")
        if file_hash(data / "PREPARATION_REPORT.json") != config["preparation_sha256"]:
            raise ValueError("Preparation changed since run")
        # Recheck the complete frozen input cohort, not only evaluator bytes.
        inputs, prep = load_inputs(data, config["dataset"], config["split"])
        input_index = {r["id"]: r for r in inputs}
        for row in config["cohort"]:
            if row["input_sha256"] != digest(input_index[row["id"]]):
                raise ValueError("Frozen model input changed")
        relative = (f"evaluator/contractnli/{config['split']}.gold.jsonl" if config["dataset"] == "contractnli"
                    else "evaluator/drugqa/all.gold.jsonl")
        gold_index = {r["id"]: r for r in read_jsonl(checked_file(data, relative, prep))}
        cohort = [row["id"] for row in config["cohort"]]
        rows = [{**gold_index[row["id"]], **row} for row in config["cohort"]]
        events = read_events(output / "events.jsonl")
        if any(e.get("config_sha256") != manifest["config_sha256"] for e in events):
            raise ValueError("Ledger belongs to a different frozen run")
        finished, usage = ledger_state(events, cohort)
        predictions = {}
        starts = {e["id"]: e for e in events if e["kind"] == "attempt_started"}
        for item_id, event in finished.items():
            if event["status"] != "ok":
                continue
            start = starts[item_id]
            if digest(start["request"]) != start["request_sha256"]:
                raise ValueError("Request digest mismatch")
            normalized = validate_prediction(event["raw"], start["request"])
            if normalized != event["prediction"]:
                raise ValueError("Stored prediction differs from validated raw output")
            predictions[item_id] = normalized
        metric_function = contractnli_metrics if config["dataset"] == "contractnli" else drugqa_metrics
        from collections import Counter
        report = {"dataset": config["dataset"], "split": config["split"], "baseline": config["baseline"],
                  "study_status": "development_only", "scientific_performance_claim": False,
                  "model_is_llm": False, "native_task_not_sequential": True,
                  "cohort_size": len(cohort), "pending": len(cohort) - len(finished),
                  "failure_policy": "All frozen cohort items remain in classification/MCQ denominators.",
                  "statuses": dict(Counter(e["status"] for e in finished.values())),
                  "usage": usage, "manifest_sha256": file_hash(output / "manifest.json"),
                  "last_event_sha256": events[-1]["sha256"] if events else None,
                  "evaluator_version": file_hash(Path(__file__).with_name("native_metrics.py")),
                  "metrics": metric_function(rows, predictions)}
        atomic_json(output / "metrics.json", report)
        lines = ["# Native benchmark engineering report", "",
                 "Development only. Deterministic offline wiring fake; no LLM performance or pharmaceutical validation.", "",
                 f"Dataset: {config['dataset']} / {config['split']}; baseline: {config['baseline']}.",
                 f"Frozen cohort: {len(cohort)} items; pending: {report['pending']}. All remain in the denominator.",
                 f"Actual model calls: 0; adapter invocations: {usage['calls']}; cost: USD {usage['cost_usd']}.", "",
                 "See metrics.json for separate native metrics, numerators, failure accounting and source hashes.",
                 "This is not a reproduced published model score, a sequential task, or a held-out pharma study.", ""]
        (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
        return report
