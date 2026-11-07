#!/usr/bin/env python3
"""Validate bundled official bytes and separate model inputs from evaluation gold.

This is data preparation, NOT a benchmark score or an interactive adaptation.
Run from repository: python scripts/prepare_benchmarks.py --source benchmark-data
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def verify_manifest(source):
    manifest = json.loads((source / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        p = (source / entry["path"]).resolve()
        if not p.is_relative_to(source.resolve()):
            raise ValueError("Manifest path escapes source")
        data = p.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Source checksum mismatch: " + entry["path"])
    return manifest

def drugqa_input(row):
    if row["marked_answer"] not in ("A","B","C","D") or len(row["choices"]) != 4:
        raise ValueError("Unexpected native MCQ schema")
    # Whitelist. Never pass marked_answer, explanation or provenance fields
    # into a purported reproduction of the native zero-shot prompt.
    return {"id":row["id"],"question":row["question"],"choices":list(row["choices"]),"language":row["language"]}

def contract_records(dataset):
    documents, tasks, gold = [], [], []
    for doc in dataset["documents"]:
        if len(doc["annotation_sets"]) != 1:
            raise ValueError("Multiple annotation sets need explicit handling")
        doc_id = str(doc["id"])
        documents.append({"id":doc_id,"text":doc["text"],"spans":doc["spans"]})
        for label_id, annotation in doc["annotation_sets"][0]["annotations"].items():
            if annotation["choice"] not in ("Entailment","Contradiction","NotMentioned"):
                raise ValueError("Unexpected native NLI label")
            task_id = doc_id + ":" + label_id
            tasks.append({"id":task_id,"document_id":doc_id,"hypothesis_id":label_id,
                          "hypothesis":dataset["labels"][label_id]["hypothesis"]})
            gold.append({"id":task_id,"label":annotation["choice"],"evidence_span_ids":annotation["spans"]})
    return documents,tasks,gold

def write_jsonl(path, records):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as stream:
        for row in records:
            stream.write(json.dumps(row,ensure_ascii=False)+"\n")

def prepare(source, output):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or source.resolve().is_relative_to(output.resolve()):
        raise ValueError("Preparation output must not contain the original source")
    provenance=verify_manifest(source)
    locked=json.loads((ROOT/"literature/dataset-lock.json").read_text(encoding="utf-8"))
    if provenance != locked:
        raise ValueError("Source manifest differs from the project dataset lock")
    report={"status":"data_preparation_only","native_metrics_run":False,"source_commits":
            {s["id"]:s["commit"] for s in provenance["sources"]},"datasets":{}}
    document_ids=set()
    for split in ("train","dev","test"):
        d=json.loads((source/"contractnli"/(split+".json")).read_text(encoding="utf-8"))
        docs,tasks,gold=contract_records(d)
        ids={row["id"] for row in docs}
        if len(ids)!=len(docs) or ids & document_ids:
            raise ValueError("Duplicate or cross-split ContractNLI document IDs")
        document_ids.update(ids)
        write_jsonl(output/"contractnli"/(split+".documents.jsonl"),docs)
        write_jsonl(output/"contractnli"/(split+".tasks.jsonl"),tasks)
        write_jsonl(output/"evaluator"/"contractnli"/(split+".gold.jsonl"),gold)
        report["datasets"]["contractnli_"+split]={"documents":len(docs),"tasks":len(tasks)}
    rows=[json.loads(line) for line in (source/"drugqa"/"all.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len({r["id"] for r in rows})!=len(rows):raise ValueError("Duplicate DrugQA IDs")
    inputs=[drugqa_input(r) for r in rows]
    gold=[{"id":r["id"],"answer":r["marked_answer"],"explanation":r["explanation"],
           "category":r["category"],"task_type":r["task_type"],"language":r["language"],
           "final_quality":r["final_quality"]} for r in rows]
    write_jsonl(output/"drugqa"/"all.inputs.jsonl",inputs)
    write_jsonl(output/"evaluator"/"drugqa"/"all.gold.jsonl",gold)
    report["datasets"]["drugqa"]={"items":len(rows),"drugs_category_items":sum(r["category"]=="Drugs" for r in rows),
        "official_training_split":False,"per_item_gmp_tag_available":any("functional_subdomain" in r for r in rows)}
    output.mkdir(parents=True,exist_ok=True)
    report["prepared_files"]={str(p.relative_to(output)).replace("\\","/"):
        {"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
        for p in sorted(output.rglob("*.jsonl"))}
    report["source_manifest_sha256"]=hashlib.sha256((source/"SOURCE_MANIFEST.json").read_bytes()).hexdigest()
    (output/"PREPARATION_REPORT.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"benchmark-data")
    p.add_argument("--output",type=Path,default=ROOT/"data/external")
    a=p.parse_args()
    print(json.dumps(prepare(a.source,a.output),indent=2))
