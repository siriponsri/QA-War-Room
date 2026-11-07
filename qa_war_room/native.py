"""CLI for offline native-task development. Run and score are separate commands."""

import argparse
import json
from pathlib import Path

from .native_runner import Caps, run_native, score_run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--dataset", choices=("contractnli", "drugqa"), required=True)
    run.add_argument("--split", choices=("train", "dev", "test", "all"), required=True)
    run.add_argument("--baseline", choices=("full-context", "lexical-retrieval"), default="full-context")
    run.add_argument("--limit", type=int, default=1, help="Original documents for ContractNLI; items for DrugQA")
    run.add_argument("--top-k", type=int, default=5)
    run.add_argument("--protocols", type=Path, default=Path("benchmark-data/protocols"))
    run.add_argument("--resume", action="store_true")
    run.add_argument("--stop-after", type=int, help="Pause after N additional items; does not change frozen caps")
    for name, value in Caps().__dict__.items():
        run.add_argument("--" + name.replace("_", "-"), type=str if name.endswith("usd") else int, default=value)
    score = commands.add_parser("score")
    for command in (run, score):
        command.add_argument("--data", type=Path, default=Path("data/external"))
        command.add_argument("--output", type=Path, required=True, help="Dedicated run directory")
    args = parser.parse_args(argv)
    try:
        if args.command == "score":
            result = score_run(args.data, args.output)
        else:
            caps = Caps(**{name: getattr(args, name) for name in Caps().__dict__})
            result = run_native(args.data, args.dataset, args.split, args.output,
                                baseline=args.baseline, limit=args.limit, top_k=args.top_k, caps=caps,
                                protocols=args.protocols, resume=args.resume, stop_after=args.stop_after)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, ArithmeticError) as error:
        parser.exit(1, f"Native benchmark stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
