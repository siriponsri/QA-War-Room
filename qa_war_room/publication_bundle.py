"""Local reproducibility archives with explicit environment/evaluator separation."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

from .native_data import digest
from .native_runner import atomic_json
from .publication_evidence import (ANALYSIS, ANALYSIS_FILES, CAP_ANALYSIS, CAP_LOCK,
    CAP_PLAN, CAP_RUN, LOCK, PACK, REFUSAL, RUN, render, snapshot)

ROLES = ("source", "environment-inputs", "engineering-runs", "evaluator")
ROOT_FILES = {"README.md", "AGENTS.md", "GOAL.md", "PLAN.md", "STATUS.md", "HANDOFF_TO_CODEX.md"}
SOURCE_PATTERNS = ("qa_war_room/*.py", "qa_war_room/static/*", "tests/test_*.py", "docs/*.md",
                   "docs/templates/*.md", "plans/*.json", "literature/*.json", "literature/*.bib", "manuscript/*.md", "manuscript/*.json")
INPUT_NAMES = {PACK + "/" + name for name in ("PACK.json", "public/cases.jsonl", "public/splits.json", "private/records.jsonl")} | {
    "data/demo/README.md", "data/demo/scenarios.json", "data/demo/evidence.json"}
RUN_NAMES = {directory + "/" + name for directory in (LOCK, CAP_LOCK) for name in ("LOCK.json",)} | {
    directory + "/" + name for directory in (RUN, CAP_RUN) for name in ("manifest.json", "events.jsonl", "SUMMARY.json")} | {CAP_PLAN}
EVALUATOR_NAMES = {PACK + "/" + name for name in ("evaluator/gold.jsonl", "evaluator/pairs.jsonl", "authoring/lineage.jsonl")} | {
    "data/demo/evaluator/gold.json", REFUSAL} | {directory + "/" + name for directory in (ANALYSIS, CAP_ANALYSIS) for name in ANALYSIS_FILES}
WRITING_NAMES = {"writing/MANUSCRIPT_DRAFT.md", "writing/CLAIMS.json", "writing/EVIDENCE.json", "writing/LOCAL_USE_NOTICE.md"}
MAX_TOTAL_BYTES = 200_000_000
MAX_FILE_BYTES = 50_000_000
SOURCE_REQUIRED = ROOT_FILES | {"scripts/prepare_benchmarks.py", "plans/g5-evaluation-plan-v1.json",
    "qa_war_room/publication.py", "qa_war_room/publication_bundle.py", "qa_war_room/publication_evidence.py",
    "tests/test_publication.py", "tests/test_study.py", "manuscript/draft.md", "manuscript/claims.json"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe archive name")
    path = PurePosixPath(name)
    if path.is_absolute() or str(path) != name or any(part in {".", ".."} or part.endswith((".", " ")) for part in path.parts):
        raise ValueError("Unsafe archive path")
    reserved = {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}
    if any(part.split(".")[0].upper() in reserved for part in path.parts):
        raise ValueError("Reserved archive path")
    return name


def allowed(role, name):
    safe_name(name)
    if role == "environment-inputs":
        return name in INPUT_NAMES
    if role == "engineering-runs":
        return name in RUN_NAMES
    if role == "evaluator":
        return name in EVALUATOR_NAMES
    if role == "source":
        return name in ROOT_FILES or name == "scripts/prepare_benchmarks.py" or any(
            len(PurePosixPath(name).parts) == len(PurePosixPath(pattern).parts) and PurePosixPath(name).match(pattern) for pattern in SOURCE_PATTERNS)
    return False


def checked_bytes(root, name):
    safe_name(name)
    root = Path(root).resolve()
    path = root
    for component in PurePosixPath(name).parts:
        path = path / component
        if path.is_symlink():
            raise ValueError("Symlinks are excluded from reproducibility archives")
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise ValueError("Missing or external archive source: " + name)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Archive member exceeds the byte ceiling")
    return path.read_bytes()


def payloads(root):
    sources = ROOT_FILES | {"scripts/prepare_benchmarks.py"}
    for pattern in SOURCE_PATTERNS:
        sources |= {path.relative_to(root).as_posix() for path in root.glob(pattern) if path.is_file()}
    # Static assets have a precise extension allowlist; caches/unknown binaries are excluded.
    sources = {name for name in sources if not name.startswith("qa_war_room/static/") or Path(name).suffix in {".html", ".css", ".js", ".svg"}}
    return {role: {name: checked_bytes(root, name) for name in sorted(names)} for role, names in (
        ("source", sources), ("environment-inputs", INPUT_NAMES), ("engineering-runs", RUN_NAMES), ("evaluator", EVALUATOR_NAMES))}


def create_bundle(root, output):
    root, output = Path(root).resolve(), Path(output)
    if output.exists():
        raise ValueError("Bundle output exists; preserve it and choose a new directory")
    evidence = snapshot(root)
    payload = payloads(root)
    combined = {name: data for members in payload.values() for name, data in members.items()}
    for name, expected in evidence["provenance_sha256"].items():
        if name not in combined or sha(combined[name]) != expected:
            raise ValueError("Source changed while freezing the bundle")
    if sum(len(data) for data in combined.values()) > MAX_TOTAL_BYTES:
        raise ValueError("Bundle exceeds the total byte ceiling")
    draft = render(combined["manuscript/draft.md"].decode("utf-8"), evidence)
    claims = json.loads(combined["manuscript/claims.json"])
    if claims["schema"] != "qawr-g6-claims-v1" or claims["scientific_results"] != "NOT_RUN":
        raise ValueError("Unsupported or promoted manuscript claims")
    for claim in claims["claims"]:
        if claim["fact_key"] not in evidence["facts"] or claim["scope"] != "engineering_or_gate_status":
            raise ValueError("Claim has no permissible evidence mapping")
        claim["observed_value"] = evidence["facts"][claim["fact_key"]]
    if (len({claim["id"] for claim in claims["claims"]}) != len(claims["claims"]) or
            not set(re.findall(r"\{\{([a-z_]+)\}\}", combined["manuscript/draft.md"].decode("utf-8"))) <= {claim["fact_key"] for claim in claims["claims"]}):
        raise ValueError("Manuscript facts require unique claim IDs and complete mappings")
    output.mkdir(parents=True)
    files, archives = {}, {}
    for role, members in payload.items():
        name = role + ".zip"
        with zipfile.ZipFile(output / name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for relative, data in members.items():
                if not allowed(role, relative):
                    raise ValueError("Member violates its archive role")
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, data)
        data = (output / name).read_bytes()
        files[name] = {"sha256": sha(data), "bytes": len(data)}
        archives[role] = {relative: {"sha256": sha(data), "bytes": len(data)} for relative, data in members.items()}
    (output / "writing").mkdir()
    (output / "writing/MANUSCRIPT_DRAFT.md").write_bytes(draft.encode("utf-8"))
    atomic_json(output / "writing/CLAIMS.json", claims)
    atomic_json(output / "writing/EVIDENCE.json", evidence)
    (output / "writing/LOCAL_USE_NOTICE.md").write_text(
        "# Local research preparation only\n\nNot submitted, published, licensed for redistribution or independently reviewed. "
        "Original-code/data licensing remains an owner decision; no new license is assigned. "
        "No third-party PDFs, raw public benchmarks, credentials, real company records or reviewer identities are included. "
        "Source/tests contain answer-bearing construction and evaluator logic: developer use only, never actor retrieval. "
        "Environment inputs contain complete unrequested records for the backend only. "
        "Evaluator/writing artifacts contain references, labels and terminal results. "
        "Policies must continue to receive only requested observation records. "
        "Checksums detect drift; they are not signatures, independent approval or a scientific result.\n", encoding="utf-8")
    for name in sorted(WRITING_NAMES):
        data = (output / name).read_bytes()
        files[name] = {"sha256": sha(data), "bytes": len(data)}
    manifest = {"schema": "qawr-g6-bundle-v1", "status": "LOCAL_DRAFT", "scientific_results": "NOT_RUN",
        "independent_review": "NOT_PERFORMED", "adjudication": "NOT_PERFORMED", "submission_ready": False,
        "publication_authorized": False, "cost_usd": "0", "files": files, "archives": archives,
        "facts_sha256": digest(evidence["facts"])}
    atomic_json(output / "BUNDLE.json", manifest)
    verified = verify_bundle(output)
    return {"status": "LOCAL_DRAFT", "archives": len(archives), "members": verified["members"],
        "scientific_results": "NOT_RUN", "submission_ready": False, "cost_usd": "0"}


def verify_bundle(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("Bundle directory cannot be a symlink")
    manifest = json.loads(checked_bytes(directory, "BUNDLE.json"))
    if (manifest["schema"] != "qawr-g6-bundle-v1" or manifest["status"] != "LOCAL_DRAFT" or
            manifest["scientific_results"] != "NOT_RUN" or manifest["independent_review"] != "NOT_PERFORMED" or
            manifest["adjudication"] != "NOT_PERFORMED" or manifest["submission_ready"] is not False or
            manifest["publication_authorized"] is not False or manifest["cost_usd"] != "0"):
        raise ValueError("Bundle cannot promote scientific or publication gates")
    if set(manifest["archives"]) != set(ROLES) or set(manifest["files"]) != WRITING_NAMES | {role + ".zip" for role in ROLES}:
        raise ValueError("Incomplete or unknown bundle partition")
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
    if actual != set(manifest["files"]) | {"BUNDLE.json"}:
        raise ValueError("Unlisted or missing bundle artifact")
    for name, entry in manifest["files"].items():
        data = checked_bytes(directory, name)
        if sha(data) != entry["sha256"] or len(data) != entry["bytes"]:
            raise ValueError("Bundle checksum mismatch")
    seen, total, members = set(), 0, 0
    for role in ROLES:
        with zipfile.ZipFile(directory / (role + ".zip")) as archive:
            names = archive.namelist()
            if set(names) != set(manifest["archives"][role]) or len(names) != len(set(names)):
                raise ValueError("Archive inventory mismatch or duplicate member")
            for info in archive.infolist():
                name = safe_name(info.filename)
                if not allowed(role, name) or name.casefold() in seen or not stat.S_ISREG(info.external_attr >> 16):
                    raise ValueError("Unsafe, overlapping or cross-boundary archive member")
                seen.add(name.casefold())
                total += info.file_size
                if info.file_size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                    raise ValueError("Archive byte ceiling exceeded")
                data = archive.read(info)
                entry = manifest["archives"][role][name]
                if sha(data) != entry["sha256"] or len(data) != entry["bytes"]:
                    raise ValueError("Archive member checksum mismatch")
                members += 1
    required = {"environment-inputs": INPUT_NAMES, "engineering-runs": RUN_NAMES, "evaluator": EVALUATOR_NAMES}
    if any(set(manifest["archives"][role]) != names for role, names in required.items()):
        raise ValueError("Incomplete required evidence partition")
    if not SOURCE_REQUIRED <= set(manifest["archives"]["source"]):
        raise ValueError("Incomplete required source partition")
    evidence = json.loads(checked_bytes(directory, "writing/EVIDENCE.json"))
    if (digest(evidence["facts"]) != manifest["facts_sha256"] or evidence["scientific_performance_claim"] is not False or
            evidence["facts"]["scientific_results"] != "NOT_RUN" or evidence["submission_ready"] is not False or
            evidence["publication_authorized"] is not False or evidence["facts"]["independent_review"] != "NOT_PERFORMED" or
            evidence["facts"]["adjudication"] != "NOT_PERFORMED" or evidence["facts"]["reference_lock"] != "NOT_LOCKED"):
        raise ValueError("Writing evidence state mismatch")
    claims = json.loads(checked_bytes(directory, "writing/CLAIMS.json"))
    with zipfile.ZipFile(directory / "source.zip") as source:
        template = source.read("manuscript/draft.md").decode("utf-8")
    if (claims["scientific_results"] != "NOT_RUN" or
            any(claim["scope"] != "engineering_or_gate_status" or claim["observed_value"] != evidence["facts"].get(claim["fact_key"]) for claim in claims["claims"]) or
            render(template, evidence) != checked_bytes(directory, "writing/MANUSCRIPT_DRAFT.md").decode("utf-8")):
        raise ValueError("Rendered manuscript or claims disagree with checked facts")
    return {"status": "VERIFIED_LOCAL_DRAFT", "members": members, "uncompressed_bytes": total,
        "scientific_results": "NOT_RUN", "submission_ready": False}


def extract_roles(directory, destination, roles):
    """Internal extraction after full verification; never ZipFile.extractall."""
    for role in roles:
        with zipfile.ZipFile(Path(directory) / (role + ".zip")) as archive:
            for info in archive.infolist():
                target = destination.joinpath(*PurePosixPath(safe_name(info.filename)).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(archive.read(info))


def rehearse(directory, output, *, run_tests=True):
    directory, output = Path(directory).resolve(), Path(output)
    verify_bundle(directory)
    if output.exists():
        raise ValueError("Rehearsal output exists; preserve it and choose a new directory")
    output.mkdir(parents=True)
    workspace = output / "workspace"
    workspace.mkdir()
    extract_roles(directory, workspace, ("source", "environment-inputs", "engineering-runs"))
    if (workspace / PACK / "evaluator").exists() or (workspace / "data/demo/evaluator").exists():
        raise ValueError("Gold leaked into pre-evaluator workspace")
    commands = []
    # No inherited model credentials or Python startup customizations.
    environment = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    environment.update(PYTHONUTF8="1", PYTHONNOUSERSITE="1")
    def call(name, args, expected=0):
        argv = [sys.executable, *args]
        result = subprocess.run(argv, cwd=workspace, env=environment, text=True, encoding="utf-8", capture_output=True, timeout=180)
        (output / (name + ".txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
        commands.append({"argv": argv, "exit_code": result.returncode, "expected_exit_code": expected, "raw_log": name + ".txt"})
        atomic_json(output / "PROGRESS.json", {"commands": commands, "status": "IN_PROGRESS"})
        if result.returncode != expected:
            raise ValueError("Rehearsal command failed: " + name + "; inspect its raw log")
    call("gold-free-replay", ["-m", "qa_war_room.study", "replay", "--pack", PACK, "--lock", LOCK, "--output", RUN])
    extract_roles(directory, workspace, ("evaluator",))
    if run_tests:
        call("tests", ["-W", "error::ResourceWarning", "-m", "unittest", "discover", "-s", "tests", "-q"])
    call("analysis", ["-m", "qa_war_room.study", "analyze", "--pack", PACK, "--lock", LOCK, "--run", RUN, "--output", "reports/g6-replayed-analysis"])
    matched = all((workspace / ANALYSIS / name).read_bytes() == (workspace / "reports/g6-replayed-analysis" / name).read_bytes()
                  for name in ("ENGINEERING_METRICS.json", "ENGINEERING_METRICS.csv", "SCIENTIFIC_TABLE_TEMPLATE.csv", "evaluator/outcomes.jsonl"))
    if not matched:
        raise ValueError("Extracted replay did not reproduce the frozen analysis")
    call("confirmatory-refusal", ["-m", "qa_war_room.study", "lock", "--mode", "confirmatory", "--pack", PACK, "--output", "reports/g6-refusal"], 2)
    verify_bundle(directory)
    result = {"status": "PASS" if run_tests else "REPLAY_ONLY_TESTS_NOT_RUN", "commands": commands,
        "gold_absent_before_evaluator_extraction": True, "analysis_bytes_match": matched,
        "full_tests": "PASS" if run_tests else "NOT_RUN", "scientific_results": "NOT_RUN",
        "independent_review": "NOT_PERFORMED", "submission_ready": False, "cost_usd": "0"}
    atomic_json(output / "REHEARSAL.json", result)
    return result
