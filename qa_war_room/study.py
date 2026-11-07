"""G5 local engineering locks/runs/analysis. No paid provider or scientific lock."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lock = commands.add_parser("lock")
    lock.add_argument("--plan", type=Path, default=Path("plans/g5-evaluation-plan-v1.json"))
    lock.add_argument("--mode", choices=("engineering", "confirmatory"), default="engineering")
    run = commands.add_parser("run")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--stop-after", type=int)
    replay = commands.add_parser("replay")
    analyze = commands.add_parser("analyze")
    for command in (lock, run, replay, analyze):
        command.add_argument("--pack", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
    for command in (run, replay, analyze):
        command.add_argument("--lock", type=Path, required=True)
    analyze.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "lock":
            from .study_plan import make_lock
            result = make_lock(args.pack, args.plan, args.output, mode=args.mode)
        elif args.command == "run":
            from .study_runner import run_matrix
            result = run_matrix(args.pack, args.lock, args.output, resume=args.resume, stop_after=args.stop_after)
        elif args.command == "replay":
            from .study_runner import replay_matrix
            result = replay_matrix(args.pack, args.lock, args.output)
        else:
            from .study_analysis import analyze_run
            result = analyze_run(args.pack, args.lock, args.run, args.output)
        print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        return 2 if result.get("status") == "REFUSED" else 0
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as error:
        parser.exit(1, f"Evaluation preparation stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
