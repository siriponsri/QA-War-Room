"""G6 local manuscript/reproducibility preparation. No publication or paid APIs."""

import argparse
import json
from pathlib import Path
import subprocess
import zipfile

from .native_data import ROOT
from .publication_bundle import create_bundle, rehearse, verify_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--root", type=Path, default=ROOT)
    build.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--bundle", type=Path, required=True)
    rehearsal = commands.add_parser("rehearse")
    rehearsal.add_argument("--bundle", type=Path, required=True)
    rehearsal.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = create_bundle(args.root, args.output) if args.command == "build" else (
            verify_bundle(args.bundle) if args.command == "verify" else rehearse(args.bundle, args.output))
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Local reproducibility preparation stopped: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
