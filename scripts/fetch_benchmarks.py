#!/usr/bin/env python3
"""Re-fetch pinned official benchmark bytes. Explicit network operation (~81 MB).
Usage: python scripts/fetch_benchmarks.py --output benchmark-data
No model API, login or paid service is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def download(url, target, limit=150_000_000):
    total=0
    request=urllib.request.Request(url,headers={"User-Agent":"QA-War-Room-Research/0.1"})
    with urllib.request.urlopen(request,timeout=45) as response, target.open("wb") as out:
        while True:
            block=response.read(1024*1024)
            if not block:break
            total+=len(block)
            if total>limit:raise ValueError("Download exceeds configured byte limit")
            out.write(block)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"benchmark-data")
    args=parser.parse_args()
    lock=json.loads((ROOT/"literature/dataset-lock.json").read_text(encoding="utf-8"))
    sources={s["id"]:s for s in lock["sources"]}
    expected={e["path"]:e for e in lock["files"]}
    args.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qawr-data-") as temp:
        archive=Path(temp)/"contract-nli.zip"
        download(sources["contractnli"]["source_url"],archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=sources["contractnli"]["archive_sha256"]:
            raise ValueError("ContractNLI archive hash mismatch; stop and investigate version drift")
        with zipfile.ZipFile(archive) as z:
            for name in ("train.json","dev.json","test.json","LICENSE"):
                data=z.read("contract-nli/"+name)  # Exact allowlist; no extractall.
                write_checked(args.output,"contractnli/"+name,data,expected)
        commit=sources["drugqa"]["commit"]
        base="https://raw.githubusercontent.com/DodgeLU/Sino-US-DrugQA/"+commit+"/"
        for local,remote in (("all.jsonl","data/release/all.jsonl"),("LICENSE","LICENSE"),("DATASET_CARD.md","DATASET_CARD.md")):
            target=Path(temp)/local
            download(base+remote,target,30_000_000)
            write_checked(args.output,"drugqa/"+local,target.read_bytes(),expected)
    (args.output/"SOURCE_MANIFEST.json").write_text(json.dumps(lock,indent=2)+"\n",encoding="utf-8")
    print("Pinned benchmark files verified in",args.output)

def write_checked(output,relative,data,expected):
    e=expected[relative]
    if len(data)!=e["bytes"] or hashlib.sha256(data).hexdigest()!=e["sha256"]:
        raise ValueError("Source hash mismatch: "+relative)
    target=output/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    print(relative,len(data),"verified",flush=True)

if __name__=="__main__":main()
