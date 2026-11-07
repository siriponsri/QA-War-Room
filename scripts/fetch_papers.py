#!/usr/bin/env python3
"""Fetch listed open PDFs without bypassing publisher controls. Stdlib downloader.

Usage: python scripts/fetch_papers.py --output reading-pack --workers 3
Papers stay outside the public repository. Failures are recorded, not disguised.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 40 * 1024 * 1024

def fetch(paper, output):
    result = {k: paper[k] for k in ("id", "title", "landing_url", "license_note")}
    result.update(status="unavailable", attempts=[], downloaded_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    target = output / "papers" / (paper["id"] + ".pdf")
    for url in paper["pdf_urls"]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QA-War-Room-Research-Pack/0.1 (open-access literature retrieval)"})
            with urllib.request.urlopen(req, timeout=35) as response:
                data = response.read(MAX_BYTES + 1)
                final_url = response.geturl()
            if len(data) > MAX_BYTES:
                raise ValueError("Download exceeds 40 MiB limit")
            if not data.lstrip()[:8].startswith(b"%PDF-"):
                raise ValueError("Response is not a PDF; likely HTML or access interstitial")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            result.update(status="downloaded", path="papers/" + target.name, bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest(), downloaded_from=final_url)
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(target))
                result["pages"] = len(reader.pages)
                result["pdf_metadata_title"] = str(reader.metadata.title or "") if reader.metadata else ""
                result["validation"] = "PDF signature and parser successful; title/version checked separately"
            except ImportError:
                result["validation"] = "PDF signature only; install pypdf for parser validation"
            except Exception as error:
                result.update(status="validation_failed", validation=str(error))
                target.unlink(missing_ok=True)
            return result
        except Exception as error:
            result["attempts"].append({"url": url, "error": str(error)})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "literature/catalog.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reading-pack")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--only", nargs="*", help="Optional paper IDs")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    papers = [p for p in catalog["papers"] if not args.only or p["id"] in args.only]
    args.output.mkdir(parents=True, exist_ok=True)
    result_path = args.output / "download-manifest.json"
    existing = {}
    if args.only and result_path.exists():
        existing = {p["id"]: p for p in json.loads(result_path.read_text())["papers"]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(4, args.workers))) as pool:
        for result in pool.map(lambda p: fetch(p, args.output), papers):
            existing[result["id"]] = result
            print(result["id"], result["status"], result.get("bytes", ""), flush=True)
            result_path.write_text(json.dumps({"retrieved_for":"personal research reading; not a public-repository redistribution grant",
                "papers":sorted(existing.values(), key=lambda p:p["id"])}, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = ["# Paper download status", "", "An unavailable file is not evidence that the article is paywalled. Network restrictions and anti-bot controls are recorded below.", "",
            "| ID | Paper | Status | Local PDF / request |", "|---|---|---|---|"]
    for p in sorted(existing.values(), key=lambda p:p["id"]):
        link = "[" + p["title"] + "](" + p["landing_url"] + ")"
        filelink = "[" + p["path"] + "](" + p["path"] + ")" if p["status"] == "downloaded" else "Please download a lawful copy via the article page."
        rows.append("| " + p["id"] + " | " + link + " | " + p["status"] + " | " + filelink + " |")
    (args.output / "DOWNLOAD_STATUS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
