from __future__ import annotations

import ast
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import cache as cache_pkg, fingerprints, versions
from legacy_documenter.cache import (
    CACHE_DIRNAME, MANIFEST_FILENAME, begin_cache_session, validate_cache,
)
from legacy_documenter.cache import context as cache_context
from legacy_documenter.cache.manifest import MODE_WARM
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.utils import write_if_changed as wic
from legacy_documenter.utils.write_if_changed import LEDGER, write_bytes_if_changed, write_text_if_changed

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "legacy_documenter"
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
NONDETERMINISTIC = {"RUN_SUMMARY.json", "RUN_SUMMARY.md", "repository.json"}

# --- EXTRACTION CACHE CONTRACT guard -----------------------------------------------------------------------
# Lives in the TEST on purpose. Procedure when `test_extraction_contract_guard` fails: the executable code of
# `cache/extraction.py`, `cache/extraction_shards.py` or `cache/extraction_store.py` changed. Decide whether
# the persisted contract (shard format, entry structure/key, cache_bypass rules, loading/validation) could make
# an older cache parse but mean something else: if so bump `versions.EXTRACTION_CACHE_SCHEMA_VERSION`. Then
# update BOTH values below to the new version and the fingerprint printed by the failure.
GUARD_EXTRACTION_CACHE_SCHEMA_VERSION = 1
GUARD_EXTRACTION_CONTRACT_FINGERPRINT = "b32ef1db75b90eb4c5d6c7f7e2a244413cac7a78cedbe8847a54419ff894f809"


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in NONDETERMINISTIC and p.relative_to(root).parts[0] != CACHE_DIRNAME}


class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        LEDGER.reset()
        self.addCleanup(LEDGER.reset)


# =========================== PART A: extraction cache guardian ===============================================
class GuardianTests(_Case):
    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, self.repo)
        self.out = self.tmp / "out"

    def _extract(self):
        scan = stages.scan_repository(self.repo, None)
        session = begin_cache_session(scan.root, self.out, scan.files, None, 12, extraction_cache=True)
        outcome = stages.extract_repository(scan.files, scan.root, session.extraction)
        session.persist()
        return outcome, session

    def _manifest(self) -> dict:
        return json.loads((self.out / CACHE_DIRNAME / MANIFEST_FILENAME).read_text(encoding="utf-8"))

    def _edit_manifest(self, mutate):
        manifest = self._manifest()
        mutate(manifest)
        (self.out / CACHE_DIRNAME / MANIFEST_FILENAME).write_text(json.dumps(manifest), encoding="utf-8")

    def test_version_is_in_the_manifest(self):
        self._extract()
        self.assertEqual(self._manifest()["versions"]["extraction_cache_schema_version"], versions.EXTRACTION_CACHE_SCHEMA_VERSION)

    def test_same_version_is_compatible(self):
        self._extract()
        _, session = self._extract()
        self.assertGreater(session.extraction.metrics["files_reused"], 0)
        self.assertIsNone(session.extraction.reuse_disabled_reason)

    def test_different_version_invalidates_only_the_extraction_cache(self):
        first, _ = self._extract()
        self._edit_manifest(lambda m: m["versions"].update(extraction_cache_schema_version=999))
        context = cache_context.build_context(self.repo.resolve(), None, 12)
        self.assertEqual(validate_cache(self.out / CACHE_DIRNAME, context).mode, MODE_WARM)  # File State still valid
        outcome, session = self._extract()
        self.assertEqual(session.extraction.reuse_disabled_reason, "EXTRACTION_CACHE_SCHEMA_MISMATCH")
        self.assertEqual(session.extraction.metrics["files_reused"], 0)
        self.assertEqual(outcome, first)
        self.assertEqual(self._manifest()["versions"]["extraction_cache_schema_version"], versions.EXTRACTION_CACHE_SCHEMA_VERSION)
        _, healed = self._extract()
        self.assertGreater(healed.extraction.metrics["files_reused"], 0)

    def test_manifest_without_the_field_means_full_extraction(self):
        first, _ = self._extract()
        self._edit_manifest(lambda m: m["versions"].pop("extraction_cache_schema_version"))
        outcome, session = self._extract()
        self.assertEqual(session.mode, "warm")
        self.assertEqual(session.extraction.reuse_disabled_reason, "EXTRACTION_CACHE_SCHEMA_MISSING")
        self.assertEqual(session.extraction.metrics["files_reused"], 0)
        self.assertEqual(outcome, first)

    def test_renderer_template_and_git_changes_do_not_invalidate_extraction(self):
        self._extract()
        with patch.object(cache_context, "template_profile_fingerprint", return_value="2" * 64), \
             patch.object(cache_context.versions, "renderer_versions", return_value={"x": {"v": "1"}}), \
             patch.object(cache_context, "git_metadata", return_value={"git_head": "z", "git_branch": "y"}):
            _, session = self._extract()
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        self.assertIsNone(session.extraction.reuse_disabled_reason)

    def test_extraction_contract_guard(self):
        current = fingerprints.extraction_contract_fingerprint()
        self.assertIsNotNone(current, "los módulos del contrato de la extraction cache no son legibles")
        if versions.EXTRACTION_CACHE_SCHEMA_VERSION == GUARD_EXTRACTION_CACHE_SCHEMA_VERSION:
            self.assertEqual(
                current, GUARD_EXTRACTION_CONTRACT_FINGERPRINT,
                "\nCAMBIÓ EL CÓDIGO DEL CONTRATO DE LA EXTRACTION CACHE y EXTRACTION_CACHE_SCHEMA_VERSION sigue en "
                f"{versions.EXTRACTION_CACHE_SCHEMA_VERSION}.\nSi el contrato persistido puede cambiar: suba "
                "legacy_documenter.versions.EXTRACTION_CACHE_SCHEMA_VERSION y luego actualice "
                f"GUARD_EXTRACTION_CACHE_SCHEMA_VERSION y GUARD_EXTRACTION_CONTRACT_FINGERPRINT a:\n  {current}\n"
                "(ver el procedimiento en el encabezado de este archivo)",
            )
        else:
            self.fail(
                f"EXTRACTION_CACHE_SCHEMA_VERSION ahora es {versions.EXTRACTION_CACHE_SCHEMA_VERSION} pero el guardián sigue en "
                f"{GUARD_EXTRACTION_CACHE_SCHEMA_VERSION}: actualice GUARD_EXTRACTION_CACHE_SCHEMA_VERSION y "
                f"GUARD_EXTRACTION_CONTRACT_FINGERPRINT = {current!r}"
            )

    def _copy_contract_tree(self) -> Path:
        root = self.tmp / "pkg"
        for relative in fingerprints.EXTRACTION_CONTRACT_FILES:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PACKAGE / relative, root / relative)
        return root

    def test_fingerprint_ignores_comments_docstrings_and_formatting_but_not_code(self):
        root = self._copy_contract_tree()
        base = fingerprints.extraction_contract_fingerprint(root)
        self.assertEqual(base, fingerprints.extraction_contract_fingerprint())
        target = root / "cache" / "extraction_shards.py"
        text = target.read_text(encoding="utf-8")
        target.write_text("# a new comment\n\n" + text.replace('"""Deterministic sharding', '"""Rewritten docstring', 1) + "\n\n\n", encoding="utf-8")
        self.assertEqual(fingerprints.extraction_contract_fingerprint(root), base)
        target.write_text(text.replace("SHARD_COUNT = 256", "SHARD_COUNT = 128"), encoding="utf-8")
        self.assertNotEqual(fingerprints.extraction_contract_fingerprint(root), base)

    def test_fingerprint_is_none_when_sources_are_missing(self):
        root = self._copy_contract_tree()
        (root / "cache" / "extraction.py").unlink()
        self.assertIsNone(fingerprints.extraction_contract_fingerprint(root))

    def test_the_contract_files_are_the_cache_modules_that_define_it(self):
        for relative in fingerprints.EXTRACTION_CONTRACT_FILES:
            self.assertTrue((PACKAGE / relative).is_file(), relative)
            ast.parse((PACKAGE / relative).read_text(encoding="utf-8"))


# =========================== PART B: write-if-changed helper ================================================
class HelperTests(_Case):
    def test_missing_file_is_written(self):
        target = self.tmp / "d" / "a.txt"
        self.assertTrue(write_text_if_changed(target, "hola", family="t"))
        self.assertEqual(target.read_bytes(), b"hola")

    def test_identical_file_is_skipped_without_touching_it(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"abc", "t")
        before = os.stat(target).st_mtime_ns
        with patch.object(wic, "atomic_write_bytes") as writer:
            self.assertFalse(write_bytes_if_changed(target, b"abc", "t"))
        writer.assert_not_called()
        self.assertEqual(os.stat(target).st_mtime_ns, before)

    def test_different_file_is_rewritten(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"abc", "t")
        self.assertTrue(write_bytes_if_changed(target, b"abcd", "t"))
        self.assertEqual(target.read_bytes(), b"abcd")

    def test_same_size_different_content_is_rewritten(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"abcd", "t")
        self.assertTrue(write_bytes_if_changed(target, b"abce", "t"))
        self.assertEqual(target.read_bytes(), b"abce")

    def test_restored_mtime_does_not_hide_a_change(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"abcd", "t")
        stat = os.stat(target)
        target.write_bytes(b"XXXX")
        os.utime(target, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(os.stat(target).st_size, stat.st_size)
        self.assertTrue(write_bytes_if_changed(target, b"abcd", "t"))
        self.assertEqual(target.read_bytes(), b"abcd")

    def test_empty_file(self):
        target = self.tmp / "e.txt"
        self.assertTrue(write_bytes_if_changed(target, b"", "t"))
        self.assertFalse(write_bytes_if_changed(target, b"", "t"))
        self.assertTrue(write_bytes_if_changed(target, b"x", "t"))
        self.assertTrue(write_bytes_if_changed(target, b"", "t"))
        self.assertEqual(target.read_bytes(), b"")

    def test_unicode_text(self):
        target = self.tmp / "u.md"
        text = "Información — ñandú 日本語 ✓\n"
        write_text_if_changed(target, text, newline="\n")
        self.assertEqual(target.read_bytes(), text.encode("utf-8"))
        self.assertFalse(write_text_if_changed(target, text, newline="\n"))

    def test_binary_content_is_exact(self):
        target = self.tmp / "b.bin"
        data = bytes(range(256)) + b"\r\n\x00\xff"
        write_bytes_if_changed(target, data, "t")
        self.assertEqual(target.read_bytes(), data)
        self.assertFalse(write_bytes_if_changed(target, data, "t"))

    def test_failed_write_keeps_the_original_and_counts_nothing_written(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"old", "t")
        with patch.object(wic, "atomic_write_bytes", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                write_bytes_if_changed(target, b"new", "t")
        self.assertEqual(target.read_bytes(), b"old")
        self.assertEqual(LEDGER.stats("t").written, 1)  # only the first (successful) write

    def test_no_temporary_is_left_behind_on_replace_failure(self):
        target = self.tmp / "a.txt"
        write_bytes_if_changed(target, b"old", "t")
        with patch("legacy_documenter.utils.atomic_write.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                write_bytes_if_changed(target, b"new", "t")
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["a.txt"])
        self.assertEqual(target.read_bytes(), b"old")

    def test_writes_are_atomic_through_the_existing_primitive(self):
        target = self.tmp / "a.txt"
        with patch.object(wic, "atomic_write_bytes", wraps=wic.atomic_write_bytes) as writer:
            write_bytes_if_changed(target, b"x", "t")
        writer.assert_called_once_with(target, b"x")

    def test_long_path_within_the_platform_limit(self):
        directory = self.tmp
        while len(str(directory)) < 150:
            directory = directory / ("d" * 20)
        target = directory / "file.json"
        self.assertTrue(write_text_if_changed(target, "{}", newline="\n"))
        self.assertFalse(write_text_if_changed(target, "{}", newline="\n"))

    def test_counters_are_deterministic_per_family(self):
        a, b = self.tmp / "a.txt", self.tmp / "b.txt"
        write_bytes_if_changed(a, b"1234", "one")
        write_bytes_if_changed(a, b"1234", "one")
        write_bytes_if_changed(b, b"12", "two")
        snapshot = LEDGER.snapshot()
        self.assertEqual(list(snapshot), ["one", "two"])
        one = snapshot["one"]
        self.assertEqual((one["generated"], one["written"], one["skipped_identical"], one["bytes_generated"], one["bytes_written"]),
                         (2, 1, 1, 8, 4))
        self.assertEqual(snapshot["two"]["written"], 1)
        LEDGER.reset()
        self.assertEqual(LEDGER.snapshot(), {})

    def test_line_endings_are_not_altered(self):
        exact = self.tmp / "exact.txt"
        write_text_if_changed(exact, "a\nb\r\nc\n", newline="\n")
        self.assertEqual(exact.read_bytes(), b"a\nb\r\nc\n")
        raw = self.tmp / "raw.bin"
        write_bytes_if_changed(raw, b"a\r\nb\n", "t")
        self.assertEqual(raw.read_bytes(), b"a\r\nb\n")
        legacy = self.tmp / "legacy.txt"  # default: same bytes as `Path.write_text`
        reference = self.tmp / "reference.txt"
        write_text_if_changed(legacy, "x\ny\n")
        reference.write_text("x\ny\n", encoding="utf-8")
        self.assertEqual(legacy.read_bytes(), reference.read_bytes())

    def test_directories_are_not_regular_files(self):
        target = self.tmp / "dir"
        target.mkdir()
        with self.assertRaises(OSError):
            write_bytes_if_changed(target, b"x", "t")


# =========================== PART B: per-family behaviour in the pipeline ====================================
class FamilyTests(_Case):
    def _run(self, out: Path, **kwargs):
        return run_full_pipeline(FULL_SAMPLE, out, None, 12, **kwargs)

    def _cold_warm(self):
        out = self.tmp / "out"
        self._run(out)
        cold = LEDGER.snapshot()
        reference = _tree(out)
        self._run(out)
        return out, cold, LEDGER.snapshot(), reference

    def test_cold_writes_everything_and_warm_skips_deterministic_families(self):
        out, cold, warm, reference = self._cold_warm()
        families = {"index", "evidence", "consumer_projection", "flujos_humanos", "ai_context", "context", "documentation"}
        self.assertEqual(set(cold), families)
        for family in families:
            self.assertEqual(cold[family]["skipped_identical"], 0, family)
            self.assertEqual(cold[family]["written"], cold[family]["generated"], family)
            self.assertEqual(warm[family]["generated"], cold[family]["generated"], family)
        for family in ("consumer_projection", "flujos_humanos", "ai_context", "context", "documentation"):
            self.assertEqual((warm[family]["written"], warm[family]["bytes_written"]), (0, 0), family)
            self.assertEqual(warm[family]["skipped_identical"], warm[family]["generated"], family)
        # index: only repository.json (duration_seconds) may differ; evidence: only what derives from it
        self.assertLessEqual(warm["index"]["written"], 1)
        self.assertLessEqual(warm["evidence"]["written"], 2)
        self.assertEqual(_tree(out), reference)

    def test_warm_output_is_logically_identical_to_a_cache_free_cold_run(self):
        out, _, _, _ = self._cold_warm()
        other = self.tmp / "other"
        self._run(other, cache_mode="off")
        self.assertEqual(_tree(out), _tree(other))

    def test_a_real_change_rewrites_only_the_affected_files(self):
        out = self.tmp / "out"
        repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, repo)
        run_full_pipeline(repo, out, None, 12)
        target = repo / "Sys" / "CustomerRepository.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\nPublic Class Another\r\nEnd Class\r\n", encoding="utf-8")
        run_full_pipeline(repo, out, None, 12)
        warm = LEDGER.snapshot()
        self.assertGreater(warm["index"]["written"], 0)
        self.assertGreater(warm["index"]["skipped_identical"], 0)
        reference = self.tmp / "ref"
        run_full_pipeline(repo, reference, None, 12, cache_mode="off")
        self.assertEqual(_tree(out), _tree(reference))

    def _corrupt_same_size(self, path: Path):
        data = path.read_bytes()
        stat = os.stat(path)
        flipped = bytearray(data)
        flipped[len(flipped) // 2] = (flipped[len(flipped) // 2] + 1) % 256 or 1
        path.write_bytes(bytes(flipped))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(os.stat(path).st_size, stat.st_size)
        self.assertNotEqual(path.read_bytes(), data)

    def test_external_corruption_with_same_size_and_mtime_is_corrected(self):
        out, _, _, reference = self._cold_warm()
        victims = [
            out / "index" / "symbols.json", out / "evidence" / "solutions.json",
            next((out / "consumer_projection" / "parts").glob("*.json")), out / "ai_context" / "SYSTEM_CONTEXT.json",
            out / "documentation" / "HUMAN_DOCUMENTATION.md", out / "documentation" / "PROJECT_OVERVIEW.md",
        ]
        for victim in victims:
            self.assertTrue(victim.is_file(), victim)
            self._corrupt_same_size(victim)
        self._run(out)
        self.assertEqual(_tree(out), reference)

    def test_deleted_outputs_are_recreated(self):
        out, _, _, reference = self._cold_warm()
        for relative in ("index/symbols.json", "evidence/solutions.json", "ai_context/SYSTEM_CONTEXT.json",
                         "documentation/PROJECT_OVERVIEW.md", "consumer_projection/CONSUMER_PROJECTION.json",
                         "context/projects.json"):
            (out / relative).unlink()
        flujos = out / "documentation" / "flujos_humanos"
        if flujos.is_dir():
            next(flujos.glob("*.md")).unlink()
        self._run(out)
        self.assertEqual(_tree(out), reference)

    def test_no_temporaries_remain_and_summary_is_untouched(self):
        out, _, _, _ = self._cold_warm()
        self.assertEqual([p for p in out.rglob("*.tmp")], [])
        self.assertTrue((out / "RUN_SUMMARY.json").is_file())

    def test_documentation_v52_keeps_its_own_write_skip(self):
        out = self.tmp / "out"
        self._run(out)
        self.assertNotIn("documentation_v52", LEDGER.snapshot())
        text = (PACKAGE / "documentation_v52" / "writer.py").read_text(encoding="utf-8")
        self.assertNotIn("write_if_changed", text)

    def test_ledger_is_in_memory_only(self):
        out = self.tmp / "out"
        self._run(out)
        # R2.7 persists metrics, but only inside the cache directory -- never among the product outputs
        names = {p.name for p in out.rglob("*") if p.relative_to(out).parts[0] != "_cache_v53"}
        self.assertNotIn("RUN_METRICS.json", names)
        self.assertNotIn("artifacts.json", names)


class RuntimeIndependenceTests(unittest.TestCase):
    def test_helper_depends_only_on_the_atomic_primitive(self):
        text = (PACKAGE / "utils" / "write_if_changed.py").read_text(encoding="utf-8")
        for forbidden in ("legacy_documenter.cli", "legacy_documenter.cache", "legacy_documenter.evidence",
                          "import subprocess", "import anthropic", "import openai"):
            self.assertNotIn(forbidden, text)

    def test_no_pipeline_family_writer_bypasses_the_helper(self):
        for relative in ("exporters/json_exporter.py", "evidence/persistence.py", "context/system_context_builder.py",
                         "context/context_builder.py", "exporters/markdown_exporter.py", "cli/artifact_lifecycle.py"):
            text = (PACKAGE / relative).read_text(encoding="utf-8")
            self.assertIn("write_text_if_changed", text, relative)
            self.assertNotIn(".write_text(", text.replace("def write_text(", ""), relative)

    def test_guardian_is_not_part_of_the_analyzer_fingerprint(self):
        self.assertNotIn("cache/", " ".join(fingerprints.ANALYZER_CODE_FILES + fingerprints.ANALYZER_CODE_DIRECTORIES))
        self.assertTrue(hasattr(cache_pkg, "ExtractionCache"))


if __name__ == "__main__":
    unittest.main()
