"""Explicit free download of pinned prompt/metric references; never execute them."""

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark-data/protocols")
    args = parser.parse_args()
    lock = json.loads((ROOT / "literature/native-protocol-lock.json").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for entry in lock["files"]:
        request = urllib.request.Request(entry["url"], headers={"User-Agent": "QA-War-Room/0.1"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(1_000_001)
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Protocol checksum mismatch: " + entry["id"])
        target = args.output / entry["file"]
        if target.exists() and target.read_bytes() != data:
            raise ValueError("Existing protocol differs; preserve and inspect: " + str(target))
        target.write_bytes(data)
        print(entry["id"], "verified")


if __name__ == "__main__":
    main()
