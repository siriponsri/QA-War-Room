"""G3 controlled-disclosure CLI. Offline only; independent of native scores/UI."""

import argparse
import json
from pathlib import Path

from .sequential_data import SequentialStore, prepare_inputs
from .sequential_engine import SequentialEngine
from .sequential_policies import POLICIES
from .sequential_runner import replay_run, run_sequential


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--native", type=Path, default=Path("data/external"))
    prepare.add_argument("--bundle", type=Path, required=True)
    prepare.add_argument("--spans-per-record", type=int, default=4)
    prepare.add_argument("--family-map", type=Path, help="Optional JSON object: native source document ID -> family")
    run = commands.add_parser("run")
    run.add_argument("--split", choices=("train", "dev", "test"), default="dev", help="Derived family-grouped partition")
    run.add_argument("--limit-groups", type=int, default=1)
    run.add_argument("--budgets", default="0,2,4", help="Unique nonnegative acquisition-credit grid")
    run.add_argument("--policies", nargs="+", choices=POLICIES, default=list(POLICIES))
    run.add_argument("--max-source-bytes", type=int, default=2_000_000)
    run.add_argument("--max-policy-actions", type=int, default=10_000)
    run.add_argument("--max-episode-actions", type=int, default=256)
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--resume", action="store_true")
    run.add_argument("--stop-after-actions", type=int, help="Checkpoint after N additional durable transitions")
    score = commands.add_parser("score")
    replay = commands.add_parser("replay")
    replay.add_argument("--episode", type=int, help="Include one final/current visible observation, 1-based matrix ordinal")
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--episode-id", required=True)
    inspect.add_argument("--credits", type=int, default=2)
    inspect.add_argument("--max-source-bytes", type=int, default=2_000_000)
    for command in (run, score, replay, inspect):
        command.add_argument("--bundle", type=Path, required=True)
    for command in (run, score, replay):
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            family_map = json.loads(args.family_map.read_text(encoding="utf-8")) if args.family_map else None
            manifest = prepare_inputs(args.native, args.bundle, spans_per_record=args.spans_per_record, family_map=family_map)
            from .sequential_eval import prepare_references
            manifest = prepare_references(args.native, args.bundle, manifest)
            SequentialStore(args.bundle)
            result = {"status": "prepared", "task_version": manifest["task_version"], "counts": manifest["counts"]}
        elif args.command == "run":
            result = run_sequential(args.bundle, args.output, split=args.split, limit_groups=args.limit_groups,
                budgets=tuple(int(n) for n in args.budgets.split(",")), policies=tuple(args.policies),
                max_source_bytes=args.max_source_bytes, max_policy_actions=args.max_policy_actions,
                max_episode_actions=args.max_episode_actions, seed=args.seed,
                resume=args.resume, stop_after_actions=args.stop_after_actions)
        elif args.command == "score":
            from .sequential_eval import score_sequential
            result = score_sequential(args.bundle, args.output)
        elif args.command == "replay":
            result = replay_run(args.bundle, args.output, args.episode)
        else:
            result = SequentialEngine(SequentialStore(args.bundle), args.episode_id, args.credits, args.max_source_bytes).observation()
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as error:
        parser.exit(1, f"Sequential task stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
