"""Local/offline G4 Manufacturing GMP case-pack and independent-review preparation."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--output", type=Path, required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--case-id", required=True)
    run = commands.add_parser("exercise")
    score = commands.add_parser("score")
    export = commands.add_parser("review-export")
    export.add_argument("--seed", type=int, default=41)
    check = commands.add_parser("review-check")
    check.add_argument("--packet", type=Path, required=True, help="The reviewer/ subdirectory, not owner/")
    check.add_argument("--ratings", type=Path, nargs="+", required=True)
    check.add_argument("--roster", type=Path, required=True)
    readiness = commands.add_parser("readiness")
    for command in (inspect, run, score, export, readiness):
        command.add_argument("--pack", type=Path, required=True)
    for command in (run, score, export, check, readiness):
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            from .pharma_authoring import prepare_inputs
            from .pharma_eval import build_references
            from .pharma_engine import PharmaStore
            result = build_references(args.output, prepare_inputs(args.output))
            store = PharmaStore(args.output)
            result = {"pack_version": store.manifest["pack_version"], "counts": store.manifest["counts"],
                      "author_candidate_counts": result["candidate_counts"], "independent_review_completed": False}
        elif args.command == "review-check":
            from .pharma_review import check_reviews
            result = check_reviews(args.packet, args.ratings, args.roster, args.output)
        else:
            from .pharma_engine import PharmaEngine, PharmaStore
            store = PharmaStore(args.pack)
            if args.command == "inspect":
                result = PharmaEngine(store, args.case_id).observation()
            elif args.command == "exercise":
                from .pharma_runner import exercise
                result = exercise(args.pack, args.output)
            elif args.command == "score":
                from .pharma_runner import score_exercise
                result = score_exercise(args.pack, args.output)
            elif args.command == "review-export":
                from .pharma_review import export_review
                result = export_review(store, args.output, seed=args.seed)
            else:
                from .native_runner import atomic_json
                if args.output.exists():
                    raise ValueError("Readiness output exists; preserve the old report")
                args.output.mkdir(parents=True)
                result = {"engineering_pack_prepared": True, "cases": len(store.case_ids()),
                          "independent_review": "NOT_PERFORMED", "adjudication": "NOT_PERFORMED",
                          "reviewed_reference_lock": "NOT_LOCKED", "publication_or_pharma_validation_ready": False,
                          "reason": "This immutable draft pack has only authored synthetic rules and unreviewed candidate labels."}
                atomic_json(args.output / "READINESS.json", result)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        parser.exit(1, f"Manufacturing case-pack task stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
