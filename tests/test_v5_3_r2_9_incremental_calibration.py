"""R2.9: equivalence comparator and explicit final/default guardrails."""
from __future__ import annotations

import contextlib
import hashlib
import io
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from legacy_documenter.cli.parser import build_parser
from legacy_documenter.cache.options import CacheOptions
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from tools import v5_3_compare_full_incremental as comparator
from tools import v5_3_r2_9_calibrate as calibration


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.left, self.right = self.base / "left", self.base / "right"
        self.left.mkdir()
        self.right.mkdir()

    def write(self, root, path, data=b"same"):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def compare(self):
        return comparator.compare_trees(self.left, self.right)

    def test_equal_trees_counts_sizes_and_hashes(self):
        for root in (self.left, self.right):
            self.write(root, "a/b", b"payload")
        result = self.compare()
        self.assertTrue(result["equal"])
        self.assertEqual(result["files_compared"], 1)
        self.assertEqual(result["total_bytes"], {"reference": 7, "candidate": 7})
        self.assertEqual(comparator.snapshot_tree(self.left)["files"]["a/b"]["sha256"],
                         hashlib.sha256(b"payload").hexdigest())

    def test_changed_file(self):
        self.write(self.left, "x", b"old")
        self.write(self.right, "x", b"new content")
        result = self.compare()
        self.assertFalse(result["equal"])
        self.assertEqual(result["changed"], ["x"])

    def test_added_file(self):
        self.write(self.right, "added")
        self.assertEqual(self.compare()["added"], ["added"])

    def test_removed_file(self):
        self.write(self.left, "removed")
        self.assertEqual(self.compare()["removed"], ["removed"])

    def test_exclusions_are_exact_paths_not_basenames(self):
        for path in ("RUN_SUMMARY.json", "RUN_SUMMARY.md", "index/repository.json", "_cache_v53/shard.json"):
            self.write(self.left, path, b"different")
        self.assertTrue(self.compare()["equal"])
        self.assertEqual(self.compare()["excluded"]["reference"],
                         ["RUN_SUMMARY.json", "RUN_SUMMARY.md", "_cache_v53/", "index/repository.json"])
        for path in ("nested/RUN_SUMMARY.json", "repository.json", "index/keep.json", "nested/_cache_v53/keep"):
            self.write(self.left, path)
        self.assertEqual(len(self.compare()["removed"]), 4)
        (self.left / "RUN_SUMMARY.md").unlink()
        self.write(self.left, "RUN_SUMMARY.md/ordinary")
        self.assertIn("RUN_SUMMARY.md/ordinary", self.compare()["removed"])

    def test_large_file_is_hashed_in_full(self):
        data = b"x" * (comparator.CHUNK_SIZE * 3 + 17)
        for root in (self.left, self.right):
            self.write(root, "large", data)
        self.assertTrue(self.compare()["equal"])
        self.write(self.right, "large", data[:-1] + b"y")
        self.assertEqual(self.compare()["changed"], ["large"])

    def test_same_size_different_bytes_not_equivalent(self):
        self.write(self.left, "same_size", b"aaaa")
        self.write(self.right, "same_size", b"bbbb")
        self.assertEqual(self.compare()["changed"], ["same_size"])

    def test_order_is_deterministic(self):
        for name in ("z", "a", "middle"):
            self.write(self.left, name)
        for name in ("middle", "a", "z"):
            self.write(self.right, name)
        left = comparator.snapshot_tree(self.left)
        right = comparator.snapshot_tree(self.right)
        self.assertEqual(left, right)
        self.assertEqual(list(left["files"]), ["a", "middle", "z"])

    def test_read_error_is_not_hidden(self):
        self.write(self.left, "x")
        with patch.object(Path, "open", side_effect=PermissionError("sensitive detail")):
            with self.assertRaises(PermissionError):
                self.compare()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(comparator.main([str(self.left), str(self.right)]), 2)
            self.assertNotIn("sensitive detail", output.getvalue())

    def test_missing_directory_is_error_not_empty_equivalence(self):
        with self.assertRaises(ValueError):
            comparator.compare_trees(self.base / "missing", self.right)

    def test_real_cli_exit_codes_and_json_summary(self):
        argv = [sys.executable, "-X", "utf8", "-m", "tools.v5_3_compare_full_incremental", str(self.left), str(self.right)]
        root = Path(__file__).resolve().parents[1]
        for expected in (0, 1):
            if expected:
                self.write(self.right, "extra")
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertEqual(json.loads(result.stdout)["equal"], expected == 0)

    def test_report_must_be_outside_product_trees(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            comparator.main([str(self.left), str(self.right), "--json", str(self.right / "report.json")])
        self.assertEqual(error.exception.code, 2)

    def test_summary_never_exports_file_contents(self):
        self.write(self.left, "x", b"password=do_not_export")
        summary = self.base / "summary.json"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(comparator.main([str(self.left), str(self.right), "--json", str(summary)]), 1)
        self.assertNotIn("do_not_export", summary.read_text(encoding="utf-8"))


class OperationalDefaultsTests(unittest.TestCase):
    def test_cache_mode_default_remains_auto(self):
        self.assertEqual(build_parser().parse_args(["full", "repo"]).cache_mode, "auto")

    def test_ratio_default_is_explicitly_disabled_until_stable_calibration(self):
        self.assertIsNone(build_parser().parse_args(["full", "repo"]).incremental_max_changed_ratio)
        self.assertIsNone(CacheOptions().max_changed_ratio)
        self.assertIsNone(inspect.signature(run_full_pipeline).parameters["incremental_max_changed_ratio"].default)

    def test_verification_and_mtime_defaults_remain_safe(self):
        args = build_parser().parse_args(["full", "repo"])
        self.assertEqual(args.verify_cache, "fast")
        self.assertFalse(args.trust_mtime)


class ControlledMutationTests(unittest.TestCase):
    def test_source_is_read_only_and_mutations_do_not_accumulate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, work = root / "official", root / "work"
            source.mkdir()
            (work / "r").mkdir(parents=True)
            original = b"\xef\xbb\xbfPublic Class Example\r\nEnd Class\r\n"
            (source / "Example.vb").write_bytes(original)
            (work / "r" / "Example.vb").write_bytes(original)
            plan = {"order": [{"path": "Example.vb", "file_type": "vb_source"}]}
            with patch.object(calibration, "WORK", work), patch.object(calibration, "SOURCE", source):
                calibration.mutate(plan, 1, "first")
                data = (work / "r" / "Example.vb").read_bytes()
                self.assertTrue(data.startswith(b"\xef\xbb\xbf' first\r\nPublic Class"))
                calibration.mutate(plan, 1, "second")
                self.assertNotIn(b"first", (work / "r" / "Example.vb").read_bytes())
                calibration.mutate(plan, 0, "none")
                self.assertEqual((work / "r" / "Example.vb").read_bytes(), original)
            self.assertEqual((source / "Example.vb").read_bytes(), original)

    def test_mutation_guard_refuses_official_source_and_workspace_ancestors(self):
        for target in (calibration.SOURCE, calibration.SOURCE / "test.vb", calibration.WORK, calibration.ROOT):
            with self.subTest(target=target), self.assertRaises(ValueError):
                calibration.guarded(target)

    def test_utf16_vb_preserves_bom_and_valid_comment_encoding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, work = root / "official", root / "work"
            source.mkdir()
            (work / "r").mkdir(parents=True)
            original = "Public Class Example\r\nEnd Class\r\n".encode("utf-16")
            (source / "Example.vb").write_bytes(original)
            (work / "r" / "Example.vb").write_bytes(original)
            plan = {"order": [{"path": "Example.vb", "file_type": "vb_source"}]}
            with patch.object(calibration, "WORK", work), patch.object(calibration, "SOURCE", source):
                calibration.mutate(plan, 1, "test")
            text = (work / "r" / "Example.vb").read_bytes().decode("utf-16")
            self.assertTrue(text.startswith("' test\r\nPublic Class Example"))
            self.assertEqual((source / "Example.vb").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
