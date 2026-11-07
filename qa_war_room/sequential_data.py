"""Gold-free controlled disclosure and source-family grouping for G3."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from .native_data import digest, file_hash, load_inputs, read_jsonl

TASK_VERSION = "qawr-contractnli-sequential-v1"
INPUT_FILES = ("public/episodes.jsonl", "private/records.jsonl", "public/splits.json", "public/lineage.jsonl")


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")


def chunks(document: dict, spans_per_record: int) -> list[dict]:
    """Partition all original characters without using annotations or label text."""
    if type(spans_per_record) is not int or spans_per_record < 1:
        raise ValueError("spans_per_record must be a positive integer")
    text, spans = document["text"], document["spans"]
    if not text or not spans or any(a[1] > b[0] for a, b in zip(spans, spans[1:])):
        raise ValueError("Controlled disclosure requires nonempty text and ordered nonoverlapping source spans")
    records = []
    for first in range(0, len(spans), spans_per_record):
        last = min(first + spans_per_record, len(spans))
        start = 0 if first == 0 else spans[first][0]
        end = len(text) if last == len(spans) else spans[last][0]
        content = text[start:end]
        records.append({"id": f"R{len(records) + 1:04d}", "cost": 1,
                        "source_id": document["document_id"], "start": start, "end": end,
                        "text": content, "sha256": text_hash(content),
                        "spans": [{"id": i, "start": spans[i][0], "end": spans[i][1],
                                   "text": text[spans[i][0]:spans[i][1]]} for i in range(first, last)]})
    assert "".join(record["text"] for record in records) == text
    return records


def group_sources(documents: dict[str, dict], family_map: dict[str, str] | None = None) -> dict:
    """Union exact-text copies and declared families before assigning derived splits."""
    family_map = {} if family_map is None else family_map
    if (not isinstance(family_map, dict) or set(family_map) - set(documents) or
            any(not isinstance(v, str) or not v.strip() for v in family_map.values())):
        raise ValueError("Family map must map known source document IDs to nonempty family strings")
    parent = {key: key for key in documents}
    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    def union(a, b):
        a, b = find(a), find(b)
        parent[max(a, b)] = min(a, b)
    first_text, first_family = {}, {}
    for doc_id, doc in sorted(documents.items()):
        fingerprint = text_hash(doc["text"])
        if fingerprint in first_text:
            union(doc_id, first_text[fingerprint])
        first_text.setdefault(fingerprint, doc_id)
        if doc_id in family_map:
            family = family_map[doc_id]
            if family in first_family:
                union(doc_id, first_family[family])
            first_family.setdefault(family, doc_id)
    grouped = {}
    for doc_id in sorted(documents):
        grouped.setdefault(find(doc_id), []).append(doc_id)
    rank = {"train": 0, "dev": 1, "test": 2}
    groups, assignments = [], {}
    for members in grouped.values():
        group_id = "family_" + digest(members)[:24]
        derived = max((documents[key]["original_split"] for key in members), key=rank.get)
        groups.append({"id": group_id, "document_ids": members, "derived_split": derived,
                       "original_splits": sorted({documents[key]["original_split"] for key in members})})
        for key in members:
            assignments[key] = {"source_family_id": group_id, "derived_split": derived,
                                "original_split": documents[key]["original_split"]}
    return {"schema": "source-family-split-v1", "groups": sorted(groups, key=lambda g: g["id"]),
            "documents": assignments,
            "rule": "Union exact UTF-8 text copies and declared families; highest original partition wins: test > dev > train.",
            "native_split_preserved_separately": True,
            "moved_documents": sorted(k for k, v in assignments.items() if v["original_split"] != v["derived_split"]),
            "independence_limit": "Broader template/near-duplicate/translation relationships not established without an explicit family map."}


def prepare_inputs(native: Path, output: Path, *, spans_per_record: int = 4,
                   family_map: dict[str, str] | None = None) -> dict:
    """Create only public descriptors and hidden source records; never read gold."""
    if output.exists():
        raise ValueError("Derived output exists; preserve it and use a new versioned directory")
    documents, observations = {}, []
    prep_hash = file_hash(native / "PREPARATION_REPORT.json")
    for split in ("train", "dev", "test"):
        rows, prep = load_inputs(native, "contractnli", split)
        for row in rows:
            doc_id = row["document_id"]
            if doc_id in documents and documents[doc_id]["original_split"] != split:
                raise ValueError("Original source ID crosses official splits")
            documents.setdefault(doc_id, {**row, "original_split": split})
            observations.append({**row, "original_split": split})
    split_manifest = group_sources(documents, family_map)
    hidden = [{"id": doc_id, "original_split": doc["original_split"], "source_sha256": text_hash(doc["text"]),
               "records": chunks(doc, spans_per_record)} for doc_id, doc in sorted(documents.items())]
    public, lineage = [], []
    for row in observations:
        assignment = split_manifest["documents"][row["document_id"]]
        public.append({"id": row["id"], "source_id": row["document_id"], "hypothesis_id": row["hypothesis_id"],
                       "hypothesis": row["hypothesis"], **assignment})
        lineage.append({"id": row["id"], "native_id": row["id"], "source_id": row["document_id"],
                        "source_family_id": assignment["source_family_id"],
                        "variant_family_id": assignment["source_family_id"],
                        "original_split": row["original_split"], "derived_split": assignment["derived_split"],
                        "transformations": [TASK_VERSION], "counterfactual": False,
                        "label_changing_transformation": False})
    output.mkdir(parents=True)
    write_jsonl(output / INPUT_FILES[0], public)
    write_jsonl(output / INPUT_FILES[1], hidden)
    (output / INPUT_FILES[2]).write_text(json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(output / INPUT_FILES[3], lineage)
    return {"task_version": TASK_VERSION, "track": "derived_sequential", "spans_per_record": spans_per_record,
            "native_preparation_sha256": prep_hash, "source_commits": prep["source_commits"],
            "family_map_sha256": digest(family_map or {}),
            "declared_family_map": family_map or {},
            "input_files": {name: {"sha256": file_hash(output / name), "bytes": (output / name).stat().st_size}
                            for name in INPUT_FILES},
            "counts": {"documents": len(documents), "source_families": len(split_manifest["groups"]),
                       "episodes": len(public), "counterfactual_pairs": 0,
                       "cross_original_split_families": sum(len(g["original_splits"]) > 1 for g in split_manifest["groups"])},
            "reference_semantics": "Original source labels unchanged; published spans are not minimal sufficient sets.",
            "input_builder_sha256": file_hash(Path(__file__))}


class SequentialStore:
    """Environment storage. Full source is private; policies receive observations only."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.manifest = json.loads((self.directory / "PACK.json").read_text(encoding="utf-8"))
        if self.manifest["task_version"] != TASK_VERSION or set(self.manifest["input_files"]) != set(INPUT_FILES):
            raise ValueError("Unsupported derived task/input manifest")
        for name in INPUT_FILES:
            entry, path = self.manifest["input_files"][name], self.directory / name
            if file_hash(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
                raise ValueError("Derived input checksum mismatch: " + name)
        self._episodes = {r["id"]: r for r in read_jsonl(self.directory / INPUT_FILES[0])}
        self._documents = {r["id"]: r for r in read_jsonl(self.directory / INPUT_FILES[1])}
        self.splits = json.loads((self.directory / INPUT_FILES[2]).read_text(encoding="utf-8"))
        self.lineage = read_jsonl(self.directory / INPUT_FILES[3])
        self._validate()

    def _validate(self):
        seen_documents = set()
        group_ids = set()
        for group in self.splits["groups"]:
            if group["id"] in group_ids or group["derived_split"] not in {"train", "dev", "test"}:
                raise ValueError("Invalid/duplicate family partition")
            group_ids.add(group["id"])
            for doc_id in group["document_ids"]:
                if doc_id in seen_documents:
                    raise ValueError("Source appears in multiple families")
                seen_documents.add(doc_id)
                item = self.splits["documents"][doc_id]
                if item["source_family_id"] != group["id"] or item["derived_split"] != group["derived_split"]:
                    raise ValueError("Family split inconsistency")
        if seen_documents != set(self._documents):
            raise ValueError("Split/source membership mismatch")
        text_families = {}
        for doc in self._documents.values():
            if set(doc) != {"id", "original_split", "source_sha256", "records"}:
                raise ValueError("Unexpected hidden source fields")
            text = "".join(r["text"] for r in doc["records"])
            if text_hash(text) != doc["source_sha256"]:
                raise ValueError("Source reconstruction checksum mismatch")
            assignment = self.splits["documents"][doc["id"]]
            if assignment["original_split"] != doc["original_split"]:
                raise ValueError("Original source split changed")
            previous = text_families.setdefault(doc["source_sha256"], assignment["source_family_id"])
            if previous != assignment["source_family_id"]:
                raise ValueError("Exact copies escaped their source family")
            end, span_ids = 0, []
            for ordinal, record in enumerate(doc["records"], 1):
                if (set(record) != {"id", "cost", "source_id", "start", "end", "text", "sha256", "spans"} or
                        record["id"] != f"R{ordinal:04d}" or record["cost"] != 1 or
                        record["source_id"] != doc["id"] or record["start"] != end or
                        record["end"] != end + len(record["text"]) or text_hash(record["text"]) != record["sha256"]):
                    raise ValueError("Invalid controlled-disclosure record")
                end = record["end"]
                for span in record["spans"]:
                    if (set(span) != {"id", "start", "end", "text"} or type(span["id"]) is not int or
                            not record["start"] <= span["start"] < span["end"] <= record["end"] or
                            text[span["start"]:span["end"]] != span["text"]):
                        raise ValueError("Original span provenance mismatch")
                    span_ids.append(span["id"])
            if span_ids != list(range(len(span_ids))) or not span_ids:
                raise ValueError("Source span IDs must be complete and ordered")
        lineage = {r["id"]: r for r in self.lineage}
        if set(lineage) != set(self._episodes):
            raise ValueError("Lineage/episode mismatch")
        for row in self._episodes.values():
            if set(row) != {"id", "source_id", "hypothesis_id", "hypothesis", "source_family_id", "derived_split", "original_split"}:
                raise ValueError("Unexpected public episode fields")
            assignment = self.splits["documents"][row["source_id"]]
            if any(row[k] != assignment[k] for k in assignment):
                raise ValueError("Episode family split mismatch")
            if row["id"] != row["source_id"] + ":" + row["hypothesis_id"]:
                raise ValueError("Original native task ID changed")
            expected_lineage = {"id": row["id"], "native_id": row["id"], "source_id": row["source_id"],
                "source_family_id": row["source_family_id"], "variant_family_id": row["source_family_id"],
                "original_split": row["original_split"], "derived_split": row["derived_split"],
                "transformations": [TASK_VERSION], "counterfactual": False, "label_changing_transformation": False}
            if lineage[row["id"]] != expected_lineage:
                raise ValueError("Descendant lineage/family/split mismatch")

    def episode(self, episode_id: str) -> dict:
        if not isinstance(episode_id, str) or episode_id not in self._episodes:
            raise ValueError("Unknown sequential episode")
        return deepcopy(self._episodes[episode_id])

    def catalog(self, episode_id: str) -> list[dict]:
        episode = self.episode(episode_id)
        # Whitelist: no title text, sizes, scores, hashes, gold spans or full content.
        return [{"id": record["id"], "title": "Source record " + str(i), "cost": 1}
                for i, record in enumerate(self._documents[episode["source_id"]]["records"], 1)]

    def record(self, episode_id: str, record_id: str) -> dict:
        episode = self.episode(episode_id)
        for record in self._documents[episode["source_id"]]["records"]:
            if record["id"] == record_id:
                return deepcopy(record)
        raise ValueError("Unknown source record")

    def cohort(self, split: str, limit_groups: int) -> list[dict]:
        if split not in {"train", "dev", "test"} or type(limit_groups) is not int or limit_groups < 1:
            raise ValueError("Choose a derived split and positive source-family limit")
        groups = [g["id"] for g in self.splits["groups"] if g["derived_split"] == split][:limit_groups]
        return [deepcopy(row) for row in self._episodes.values() if row["source_family_id"] in groups]
