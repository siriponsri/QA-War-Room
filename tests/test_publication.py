"""G6 local archives: evidence integrity, namespace boundaries and fresh replay."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from qa_war_room.native_data import file_hash
from qa_war_room.pharma_authoring import prepare_inputs
from qa_war_room.pharma_eval import build_references
from qa_war_room.publication import main
from qa_war_room.publication_bundle import (EVALUATOR_NAMES, INPUT_NAMES, ROOT_FILES,
    SOURCE_PATTERNS, allowed, checked_bytes, create_bundle, rehearse, safe_name, sha, verify_bundle)
from qa_war_room.publication_evidence import (ANALYSIS, CAP_ANALYSIS, CAP_LOCK, CAP_PLAN,
    CAP_RUN, LOCK, PACK, REFUSAL, RUN, render, snapshot)
from qa_war_room.study_analysis import analyze_run
from qa_war_room.study_plan import make_lock
from qa_war_room.study_runner import run_matrix

ROOT = Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        base = cls.base = Path(cls.fixture.name) / "base"
        base.mkdir()
        names = ROOT_FILES | {"scripts/prepare_benchmarks.py"}
        for pattern in SOURCE_PATTERNS:
            names |= {path.relative_to(ROOT).as_posix() for path in ROOT.glob(pattern) if path.is_file()}
        names |= {"data/demo/README.md", "data/demo/scenarios.json", "data/demo/evidence.json", "data/demo/evaluator/gold.json"}
        for name in names:
            destination = base / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes())
        build_references(base / PACK, prepare_inputs(base / PACK))
        plan = json.loads((ROOT / "plans/g5-evaluation-plan-v1.json").read_text())
        plan["engineering"]["methods"] = ["sop-catalog-v1", "sop-adaptive-v1"]
        plan["engineering"]["budgets"] = [0, 7]
        plan_path = base / "fixture-plan.json"
        plan_path.write_text(json.dumps(plan))
        make_lock(base / PACK, plan_path, base / LOCK)
        run_matrix(base / PACK, base / LOCK, base / RUN)
        analyze_run(base / PACK, base / LOCK, base / RUN, base / ANALYSIS)
        make_lock(base / PACK, plan_path, (base / REFUSAL).parent, mode="confirmatory")
        plan["engineering"]["max_policy_actions"] = 1
        cap_path = base / CAP_PLAN
        cap_path.write_text(json.dumps(plan))
        make_lock(base / PACK, cap_path, base / CAP_LOCK)
        run_matrix(base / PACK, base / CAP_LOCK, base / CAP_RUN)
        analyze_run(base / PACK, base / CAP_LOCK, base / CAP_RUN, base / CAP_ANALYSIS)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "root"
        shutil.copytree(self.base, self.root)
        self.bundle = Path(temp.name) / "bundle"
        self.work = Path(temp.name)

    def build(self):
        return create_bundle(self.root, self.bundle)

    def rewrite_archive(self, role, change):
        path = self.bundle / (role + ".zip")
        manifest_path = self.bundle / "BUNDLE.json"
        manifest = json.loads(manifest_path.read_text())
        with zipfile.ZipFile(path) as archive:
            members = {i.filename: (archive.read(i), i.external_attr) for i in archive.infolist()}
        change(members)
        with zipfile.ZipFile(path, "w") as archive:
            for name, (data, mode) in members.items():
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = mode
                archive.writestr(info, data)
        manifest["archives"][role] = {name: {"sha256": sha(data), "bytes": len(data)} for name, (data, _) in members.items()}
        manifest["files"][role + ".zip"] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
        manifest_path.write_text(json.dumps(manifest))

    def test_snapshot_uses_raw_counts_and_retains_pending_gate_status(self):
        evidence = snapshot(self.root)
        self.assertEqual(evidence["facts"]["dev_jobs"], 64)
        self.assertEqual(evidence["facts"]["cap_pending"], 63)
        self.assertEqual(evidence["facts"]["scientific_results"], "NOT_RUN")
        self.assertFalse(evidence["submission_ready"])
        self.assertEqual(render("jobs={{dev_jobs}}; {{independent_review}}", evidence), "jobs=64; NOT_PERFORMED")
        for text in ("{{unknown}}", "{{dev_jobs", "{{NotAValidKey}}"):
            with self.assertRaises(ValueError):
                render(text, evidence)

    def test_archive_partitions_rendering_and_repeatable_zip_bytes(self):
        self.build()
        verified = verify_bundle(self.bundle)
        self.assertEqual(verified["status"], "VERIFIED_LOCAL_DRAFT")
        with zipfile.ZipFile(self.bundle / "environment-inputs.zip") as archive:
            self.assertEqual(set(archive.namelist()), INPUT_NAMES)
            self.assertTrue(all("evaluator" not in name and "authoring" not in name for name in archive.namelist()))
        with zipfile.ZipFile(self.bundle / "evaluator.zip") as archive:
            self.assertEqual(set(archive.namelist()), EVALUATOR_NAMES)
        draft = (self.bundle / "writing/MANUSCRIPT_DRAFT.md").read_text(encoding="utf-8")
        self.assertNotIn("{{", draft)
        self.assertIn("NOT FOR SUBMISSION", draft)
        self.assertIn("NOT_PERFORMED", draft)
        other = self.work / "other"
        create_bundle(self.root, other)
        self.assertEqual({p.name: file_hash(p) for p in self.bundle.glob("*.zip")}, {p.name: file_hash(p) for p in other.glob("*.zip")})

    def test_secrets_external_data_pdfs_and_caches_excluded_without_reads(self):
        for relative in (".env", "benchmark-data/gold.json", "reading-pack/paper.pdf", "qa_war_room/__pycache__/secrets.pyc"):
            path = self.root / relative
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text("DO NOT COPY THIS SENTINEL")
        original = Path.open
        def guard(path, *args, **kwargs):
            if path.name == ".env" or "benchmark-data" in path.parts or "reading-pack" in path.parts:
                raise AssertionError("Excluded file was opened")
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", guard):
            self.build()
        with zipfile.ZipFile(self.bundle / "source.zip") as archive:
            self.assertFalse(any(name.endswith((".pdf", ".pyc")) or ".env" in name for name in archive.namelist()))

    def test_tampered_analysis_rejected_even_with_repaired_output_hash(self):
        path = self.root / ANALYSIS / "ENGINEERING_METRICS.json"
        metrics = json.loads(path.read_text())
        metrics["jobs"] += 1
        path.write_text(json.dumps(metrics))
        manifest_path = self.root / ANALYSIS / "ANALYSIS.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["outputs"]["ENGINEERING_METRICS.json"] = file_hash(path)
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "differs from replayed"):
            self.build()
        self.assertFalse(self.bundle.exists())

    def test_locked_source_drift_is_rejected_before_export(self):
        with (self.root / "qa_war_room/study_metrics.py").open("a") as handle:
            handle.write("\n# Changed source\n")
        with self.assertRaisesRegex(ValueError, "Export source differs"):
            self.build()

    def test_poisoned_summary_cannot_enter_manuscript(self):
        path = self.root / RUN / "SUMMARY.json"
        data = json.loads(path.read_text())
        data["terminal"] = 99999
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "summary differs"):
            self.build()

    def test_raw_journal_corruption_and_gold_checksum_drift_refused(self):
        path = self.root / RUN / "events.jsonl"
        saved = path.read_bytes()
        path.write_bytes(saved + b"{")
        with self.assertRaisesRegex(ValueError, "Torn"):
            self.build()
        path.write_bytes(saved)
        with (self.root / PACK / "evaluator/gold.jsonl").open("a") as handle:
            handle.write("\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.build()

    def test_scientific_refusal_cannot_be_replaced_by_a_completed_lock(self):
        path = self.root / REFUSAL
        data = json.loads(path.read_text())
        data["scientific_analysis_authorized"] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "refused confirmatory"):
            self.build()

    def test_unmapped_or_promoted_claim_ledger_refused(self):
        path = self.root / "manuscript/claims.json"
        claims = json.loads(path.read_text())
        claims["claims"][0]["fact_key"] = "validated_pharma_accuracy"
        path.write_text(json.dumps(claims))
        with self.assertRaisesRegex(ValueError, "permissible evidence"):
            self.build()

    def test_checksums_unlisted_artifacts_and_overwrites_refused(self):
        self.build()
        with self.assertRaisesRegex(ValueError, "exists"):
            self.build()
        extra = self.bundle / "unexpected.txt"
        extra.write_text("unlisted")
        with self.assertRaisesRegex(ValueError, "Unlisted"):
            verify_bundle(self.bundle)
        extra.unlink()
        with (self.bundle / "writing/MANUSCRIPT_DRAFT.md").open("a") as handle:
            handle.write("injected unsupported result")
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify_bundle(self.bundle)

    def test_gold_cannot_be_reclassified_as_environment_even_if_rehashed(self):
        self.build()
        self.rewrite_archive("environment-inputs", lambda members: members.update({PACK + "/evaluator/gold.jsonl": (b"[]", (stat.S_IFREG | 0o644) << 16)}))
        with self.assertRaisesRegex(ValueError, "cross-boundary"):
            verify_bundle(self.bundle)

    def test_missing_evaluator_member_rejected_even_with_repaired_inventory(self):
        self.build()
        self.rewrite_archive("evaluator", lambda members: members.pop(PACK + "/evaluator/gold.jsonl"))
        with self.assertRaisesRegex(ValueError, "Incomplete required"):
            verify_bundle(self.bundle)

    def test_missing_required_source_member_refused(self):
        self.build()
        self.rewrite_archive("source", lambda members: members.pop("qa_war_room/publication.py"))
        with self.assertRaisesRegex(ValueError, "Incomplete required source"):
            verify_bundle(self.bundle)

    def test_rendered_prose_cannot_change_by_only_repairing_its_checksum(self):
        self.build()
        path = self.bundle / "writing/MANUSCRIPT_DRAFT.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nUNSUPPORTED RESULT\n", encoding="utf-8")
        manifest_path = self.bundle / "BUNDLE.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"]["writing/MANUSCRIPT_DRAFT.md"] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Rendered manuscript"):
            verify_bundle(self.bundle)

    def test_lineage_tampering_refused(self):
        with (self.root / PACK / "authoring/lineage.jsonl").open("a") as handle:
            handle.write("\n")
        with self.assertRaisesRegex(ValueError, "lineage checksum"):
            self.build()

    def test_traversal_and_zip_symlinks_refused_before_extraction(self):
        self.build()
        self.rewrite_archive("source", lambda members: members.update({"../escape.py": (b"pass", (stat.S_IFREG | 0o644) << 16)}))
        with self.assertRaisesRegex(ValueError, "Unsafe archive"):
            verify_bundle(self.bundle)
        self.rewrite_archive("source", lambda members: (members.pop("../escape.py"), members.update({"qa_war_room/link.py": (b"outside", (stat.S_IFLNK | 0o777) << 16)})))
        with self.assertRaisesRegex(ValueError, "Unsafe, overlapping"):
            verify_bundle(self.bundle)

    def test_case_collisions_and_oversized_archives_refused(self):
        self.build()
        def collide(members):
            members["qa_war_room/X.py"] = (b"pass", (stat.S_IFREG | 0o644) << 16)
            members["qa_war_room/x.py"] = (b"pass", (stat.S_IFREG | 0o644) << 16)
        self.rewrite_archive("source", collide)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            verify_bundle(self.bundle)
        with patch("qa_war_room.publication_bundle.MAX_TOTAL_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "byte ceiling"):
                verify_bundle(self.bundle)

    def test_status_flag_promotion_refused(self):
        self.build()
        path = self.bundle / "BUNDLE.json"
        manifest = json.loads(path.read_text())
        manifest["independent_review"] = "COMPLETED"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "cannot promote"):
            verify_bundle(self.bundle)

    def test_path_validation_and_source_symlink_guard(self):
        for name in ("/absolute", "../escape", "a/../b", "C:/secret", "a\\b", "CON.txt", "a/", "a//b", "x. "):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    safe_name(name)
        self.assertFalse(allowed("source", "outside/qa_war_room/secret.py"))
        with patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaisesRegex(ValueError, "Symlinks"):
                checked_bytes(self.root, "README.md")

    def test_fresh_replay_before_gold_then_exact_analysis_without_inherited_keys(self):
        self.build()
        actual_run = subprocess.run
        child_environments = []
        def observed(*args, **kwargs):
            child_environments.append(kwargs.get("env", {}))
            return actual_run(*args, **kwargs)
        with patch.dict(os.environ, {"FAKE_PROVIDER_API_KEY": "PRIVATE_SENTINEL"}), patch("qa_war_room.publication_bundle.subprocess.run", side_effect=observed):
            result = rehearse(self.bundle, self.work / "rehearsal", run_tests=False)
        self.assertTrue(result["gold_absent_before_evaluator_extraction"])
        self.assertTrue(result["analysis_bytes_match"])
        self.assertEqual(result["status"], "REPLAY_ONLY_TESTS_NOT_RUN")
        self.assertEqual(result["full_tests"], "NOT_RUN")
        self.assertTrue(all("FAKE_PROVIDER_API_KEY" not in env for env in child_environments))
        self.assertEqual([c["exit_code"] for c in result["commands"]], [0, 0, 2])
        with self.assertRaisesRegex(ValueError, "exists"):
            rehearse(self.bundle, self.work / "rehearsal", run_tests=False)

    def test_cli_verifies_local_bundle_without_publishing(self):
        self.build()
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(["verify", "--bundle", str(self.bundle)])
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(stream.getvalue())["submission_ready"])


if __name__ == "__main__":
    unittest.main()
