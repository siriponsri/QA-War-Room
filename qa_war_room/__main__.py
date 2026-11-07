"""Run the local demo or its engineering smoke benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import run_benchmark, write_benchmark
from .engine import SessionEngine
from .server import create_server
from .store import FixtureStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA War Room — offline scripted synthetic starter")
    parser.add_argument("command", choices=("serve", "benchmark"), nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=8765, help="Local HTTP port (default: 8765)")
    parser.add_argument("--host", choices=("127.0.0.1", "localhost"), default="127.0.0.1")
    parser.add_argument("--data-dir", type=Path, help="Local fixture directory; defaults to bundled demo cases")
    parser.add_argument("--output", type=Path, help="Write benchmark JSON to this path")
    arguments = parser.parse_args(argv)
    if arguments.command == "benchmark":
        result = (write_benchmark(arguments.output, arguments.data_dir) if arguments.output
                  else run_benchmark(arguments.data_dir))
        print(json.dumps({"evaluation_kind": result["evaluation_kind"],
                          "scientific_performance_claim": result["scientific_performance_claim"],
                          "summary": result["summary"],
                          "output": str(arguments.output) if arguments.output else None}, indent=2))
        return 0
    if arguments.output:
        parser.error("--output applies only to benchmark")
    if not 0 <= arguments.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    try:
        store = FixtureStore(arguments.data_dir)
        server = create_server(SessionEngine(store), arguments.host, arguments.port)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not start local demo: {error}\n")
    print(f"QA War Room: http://127.0.0.1:{server.server_address[1]}", flush=True)
    print("Offline scripted simulation. No LLM calls. Fictional records; not a GMP determination.", flush=True)
    print("Press Ctrl+C to stop. Sessions are held in memory and reset when this process stops.", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
