"""V5.3-R2.2: write-skip of `documentation_v52` by strict content verification + Windows path preflight."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli import parser as cli_parser, pipeline_stages, router
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.documentation_v52 import engine, writer
from legacy_documenter.documentation_v52.engine import (
    DocumentationV52Result, generate_documentation_v52,
)
from legacy_documenter.documentation_v52.writer import (
    MANIFEST_FILENAME,
)
from legacy_documenter.main import analyze_repository
from legacy_documenter.utils import path_limits
from legacy_documenter.utils.path_limits import (
    ATOMIC_TEMP_OVERHEAD, OutputPathTooLongError, applicable_path_limit, check_output_paths, to_extended_path,
)

ROOT = Path(__file__).resolve().parent.parent
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
IS_WINDOWS = os.name == "nt"


def _files() -> dict[str, str]:
    return {
        "README.md": "# Inicio\nñandú — café\n",
        "developer/a.md": "# A\nlínea 1\nlínea 2\n",
        "developer/sub/b.md": "# B\n",
        "general/c.md": "# C\n" + "x" * 200 + "\n",
    }


def _write(root: Path, files: dict[str, str], **kwargs) -> DocumentationV52Result:
    result = DocumentationV52Result(output_dir=root, profiles={"p": {"files": len(files)}})
    writer.write_tree(root, files, result, **kwargs)
    return result


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class WriteSkipTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "documentation_v52"
        self.addCleanup(self._tmp.cleanup)

    def test_first_run_without_previous_output_writes_everything(self):
        stats = _write(self.root, _files()).write_stats
        self.assertEqual(stats["documents_total"], 4)
        self.assertEqual((stats["documents_written"], stats["documents_skipped_write"]), (4, 0))
        self.assertEqual(stats["documents_missing"], 4)
        self.assertEqual(stats["previous_manifest"], "absent")
        self.assertEqual(stats["verification_mode"], "strict_content")
        self.assertEqual(_tree(self.root)["developer/a.md"], "# A\nlínea 1\nlínea 2\n".encode("utf-8"))

    def test_identical_second_run_rewrites_nothing_but_the_manifest(self):
        _write(self.root, _files())
        with patch.object(writer.tempfile, "mkstemp", wraps=writer.tempfile.mkstemp) as mkstemp, \
                patch.object(writer.os, "fsync", wraps=writer.os.fsync) as fsync, \
                patch.object(writer, "_replace_with_retry", wraps=writer._replace_with_retry) as replace:
            stats = _write(self.root, _files()).write_stats
        self.assertEqual((stats["documents_written"], stats["documents_skipped_write"]), (0, 4))
        self.assertEqual(stats["documents_verified"], 4)
        self.assertEqual(stats["previous_manifest"], "valid")
        self.assertEqual(stats["documents_changed_vs_previous_manifest"], 0)
        # only `MANIFEST.json` goes through the atomic mechanism: one temp file, one fsync, one replace
        self.assertEqual((mkstemp.call_count, fsync.call_count, replace.call_count), (1, 1, 1))

    def test_a_changed_document_is_the_only_one_written(self):
        _write(self.root, _files())
        changed = _files()
        changed["developer/a.md"] = "# A\nnuevo\n"
        stats = _write(self.root, changed).write_stats
        self.assertEqual((stats["documents_written"], stats["documents_skipped_write"], stats["documents_changed"]), (1, 3, 1))
        self.assertEqual(stats["documents_changed_vs_previous_manifest"], 1)
        self.assertEqual((self.root / "developer/a.md").read_bytes(), b"# A\nnuevo\n")

    def test_a_missing_document_is_rebuilt(self):
        _write(self.root, _files())
        (self.root / "developer/sub/b.md").unlink()
        stats = _write(self.root, _files()).write_stats
        self.assertEqual((stats["documents_written"], stats["documents_missing"]), (1, 1))
        self.assertEqual((self.root / "developer/sub/b.md").read_bytes(), b"# B\n")

    def test_corrupt_existing_documents_are_rebuilt_whatever_the_corruption(self):
        _write(self.root, _files())
        (self.root / "developer/a.md").write_bytes(b"")                                   # truncated
        (self.root / "general/c.md").write_bytes(b"\x00" * len(_files()["general/c.md"]))  # same size, garbage
        stats = _write(self.root, _files()).write_stats
        self.assertEqual((stats["documents_written"], stats["documents_skipped_write"]), (2, 2))
        self.assertEqual(_tree(self.root)["general/c.md"], _files()["general/c.md"].encode("utf-8"))

    def test_same_size_external_edit_with_restored_mtime_is_not_accepted(self):
        _write(self.root, _files())
        target = self.root / "developer/a.md"
        before = target.stat()
        original = target.read_bytes()
        tampered = bytearray(original)
        tampered[2] ^= 0x01                                   # flip one bit: same size
        target.write_bytes(bytes(tampered))
        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))   # same size AND same mtime
        self.assertEqual(target.stat().st_size, before.st_size)
        stats = _write(self.root, _files()).write_stats
        self.assertEqual(stats["documents_written"], 1)
        self.assertEqual(stats["documents_disk_mismatch_with_same_previous_manifest"], 1)
        self.assertEqual(target.read_bytes(), original)

    def test_absent_previous_manifest_is_safe_and_content_is_still_verified(self):
        _write(self.root, _files())
        (self.root / MANIFEST_FILENAME).unlink()
        stats = _write(self.root, _files()).write_stats
        self.assertEqual(stats["previous_manifest"], "absent")
        self.assertEqual((stats["documents_written"], stats["documents_skipped_write"]), (0, 4))
        self.assertTrue((self.root / MANIFEST_FILENAME).is_file())

    def test_corrupt_previous_manifest_is_safe(self):
        for corrupt in (b"{ not json", b"[]", b'{"contract": "Other", "files": []}', b'{"contract": "LegacyMapperDocumentationV52"}',
                        b'{"contract": "LegacyMapperDocumentationV52", "files": [1]}', b"\xff\xfe\x00"):
            with self.subTest(corrupt=corrupt):
                shutil.rmtree(self.root, ignore_errors=True)
                _write(self.root, _files())
                (self.root / MANIFEST_FILENAME).write_bytes(corrupt)
                stats = _write(self.root, _files()).write_stats
                self.assertEqual(stats["previous_manifest"], "corrupt")
                self.assertEqual((stats["documents_written"], stats["documents_skipped_write"]), (0, 4))  # content verified
                self.assertEqual(json.loads((self.root / MANIFEST_FILENAME).read_text(encoding="utf-8"))["contract"],
                                 "LegacyMapperDocumentationV52")

    def test_orphans_are_removed_and_counted(self):
        _write(self.root, _files())
        (self.root / "developer/old_orphan.md").write_bytes(b"# stale\n")
        (self.root / "stale_dir").mkdir()
        (self.root / "stale_dir/x.md").write_bytes(b"# stale\n")
        stats = _write(self.root, _files()).write_stats
        self.assertEqual(stats["orphans_removed"], 2)
        self.assertFalse((self.root / "developer/old_orphan.md").exists())
        self.assertFalse((self.root / "stale_dir").exists())          # emptied directory is pruned as before
        self.assertEqual(stats["documents_skipped_write"], 4)

    def test_empty_stale_directories_are_pruned_and_others_are_kept(self):
        _write(self.root, _files())
        (self.root / "empty_stale/deeper").mkdir(parents=True)                    # never held a document
        (self.root / "kept_with_note").mkdir()
        (self.root / "kept_with_note/NOTE.txt").write_bytes(b"not ours")          # not a `.md`: kept, directory too
        (self.root / "developer/sub/empty_child").mkdir()                          # empty dir inside an expected one
        _write(self.root, _files())
        self.assertFalse((self.root / "empty_stale").exists())
        self.assertFalse((self.root / "developer/sub/empty_child").exists())
        self.assertTrue((self.root / "kept_with_note/NOTE.txt").is_file())
        for directory in ("developer", "developer/sub", "general"):
            self.assertTrue((self.root / directory).is_dir(), directory)

    def test_manifest_and_tree_are_identical_to_a_full_generation(self):
        fresh = Path(self._tmp.name) / "fresh" / "documentation_v52"
        _write(fresh, _files())
        # a run over a dirty tree: a stale/corrupt document, a missing one, an orphan, an old manifest
        _write(self.root, _files())
        (self.root / "developer/a.md").write_bytes(b"garbage")
        (self.root / "general/c.md").unlink()
        (self.root / "orphan.md").write_bytes(b"x")
        _write(self.root, _files())
        self.assertEqual(_tree(self.root), _tree(fresh))
        self.assertEqual((self.root / MANIFEST_FILENAME).read_bytes(), (fresh / MANIFEST_FILENAME).read_bytes())
        manifest = json.loads((self.root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            raw = (self.root / entry["path"]).read_bytes()
            self.assertEqual((entry["size_bytes"], entry["sha256"]), (len(raw), hashlib.sha256(raw).hexdigest()))

    def test_encoding_and_line_endings_are_exactly_as_before(self):
        _write(self.root, _files())
        _write(self.root, _files())           # second run: everything skipped, bytes untouched
        raw = (self.root / "README.md").read_bytes()
        self.assertEqual(raw, "# Inicio\nñandú — café\n".encode("utf-8"))
        self.assertNotIn(b"\r", raw)
        self.assertNotIn(b"\r", (self.root / MANIFEST_FILENAME).read_bytes())

    def test_determinism(self):
        _write(self.root, _files())
        first = (self.root / MANIFEST_FILENAME).read_bytes()
        again = Path(self._tmp.name) / "again" / "documentation_v52"
        _write(again, _files())
        self.assertEqual(first, (again / MANIFEST_FILENAME).read_bytes())
        _write(self.root, _files())
        self.assertEqual(first, (self.root / MANIFEST_FILENAME).read_bytes())

    def test_verification_is_order_independent_and_joins_its_threads(self):
        _write(self.root, _files())
        (self.root / "developer/a.md").write_bytes(b"x")
        expected = {k: v.encode("utf-8") for k, v in _files().items()}
        alive_before = threading.active_count()
        sequential = writer._verify_existing(self.root, expected, 1)
        pooled = writer._verify_existing(self.root, expected, writer.VERIFY_WORKERS)
        self.assertEqual(sequential, pooled)
        self.assertEqual(pooled["developer/a.md"], "different")
        self.assertEqual(threading.active_count(), alive_before)        # the pool is joined before returning

    def test_end_to_end_second_run_skips_all_and_touches_nothing_else(self):
        with tempfile.TemporaryDirectory() as out:
            first = run_full_pipeline(FULL_SAMPLE, Path(out), None, 12)
            snapshot = {p: b for p, b in _tree(Path(out)).items() if not p.startswith(("documentation_v52/MANIFEST", "index/repository", "_cache_v53/CACHE_MANIFEST"))}  # R2.4 cache manifest has a generated_at
            v52_before = {p: b for p, b in _tree(Path(out)).items() if p.startswith("documentation_v52/")}
            with patch.object(pipeline_stages.LOG, "info") as info:
                second = run_full_pipeline(FULL_SAMPLE, Path(out), None, 12)
            after = _tree(Path(out))
            self.assertEqual(first.status.value, "SUCCESS")
            self.assertEqual(second.status.value, "SUCCESS")
            self.assertEqual({p: b for p, b in after.items() if p.startswith("documentation_v52/")}, v52_before)
            for path, content in snapshot.items():                       # evidence, index, projections, legacy docs unchanged
                self.assertEqual(after[path], content, path)
            stats = next(c.args[1] for c in info.call_args_list if c.args and c.args[0] == "documentation_v52 write: %s")
            self.assertEqual(stats["documents_written"], 0)
            self.assertEqual(stats["documents_skipped_write"], stats["documents_total"])


class RuntimeIndependenceTests(unittest.TestCase):
    def test_new_code_reads_no_governance_files_and_calls_no_ai(self):
        for module in (engine, writer, path_limits):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            constants = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            for forbidden in ("PROJECT_STATE", "AGENTS.md", "CLAUDE.md", "prompts", "docs/", "tests", "llm", "copilot"):
                self.assertFalse(any(forbidden in c for c in constants if len(c) < 120), (module.__name__, forbidden))
            imported = {n.module.split(".")[-1] if n.module else "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
            self.assertFalse(imported & {"llm", "knowledge", "orchestration"})


def _base_with_length(length: int) -> str:
    """An absolute path (any OS) of exactly `length` characters."""
    prefix = os.path.abspath(os.path.join(os.getcwd(), "x"))[:-1]
    return prefix + "x" * (length - len(prefix))


class PathLimitTests(unittest.TestCase):
    LIMIT = 259

    def test_path_within_the_limit_passes(self):
        base = _base_with_length(100)
        check_output_paths(base, ["a" * 50], self.LIMIT)

    def test_path_exactly_at_the_edge_passes_and_one_more_fails(self):
        base = _base_with_length(100)
        fits = self.LIMIT - ATOMIC_TEMP_OVERHEAD - len(base) - 1         # relative length that lands exactly on 259
        check_output_paths(base, ["a" * fits], self.LIMIT)
        with self.assertRaises(OutputPathTooLongError):
            check_output_paths(base, ["a" * (fits + 1)], self.LIMIT)

    def test_a_path_that_fits_alone_but_not_with_its_atomic_temp_name_fails(self):
        base = _base_with_length(100)
        rel = "a" * (self.LIMIT - len(base) - 1)                          # final path is exactly 259: fits by itself
        with self.assertRaises(OutputPathTooLongError) as caught:
            check_output_paths(base, [rel], self.LIMIT)
        self.assertEqual(caught.exception.worst_length, self.LIMIT + ATOMIC_TEMP_OVERHEAD)

    def test_the_worst_of_several_paths_is_reported_and_all_offenders_counted(self):
        base = _base_with_length(120)
        rels = ["short.md", "m" * 120, "w" * 150, "n" * 125]
        with self.assertRaises(OutputPathTooLongError) as caught:
            check_output_paths(base, rels, self.LIMIT)
        self.assertTrue(caught.exception.worst_path.endswith("w" * 150))
        self.assertEqual(caught.exception.offending_count, 2)   # 120 chars still fits (limit allows 124); 150 and 125 do not

    def test_the_error_is_explicit_and_actionable(self):
        base = _base_with_length(120)
        output = _base_with_length(100)
        with self.assertRaises(OutputPathTooLongError) as caught:
            check_output_paths(base, ["w" * 150], self.LIMIT, output_root=output)
        error = caught.exception
        message = str(error)
        self.assertEqual(error.code, "OUTPUT_PATH_TOO_LONG")
        self.assertTrue(message.startswith("OUTPUT_PATH_TOO_LONG"))
        for needed in (error.worst_path, str(error.worst_length), str(self.LIMIT), output, "--output", "No se escribió nada", "--long-paths"):
            self.assertIn(needed, message)
        self.assertEqual(error.output_root, output)

    def test_suggested_output_length_is_exact(self):
        rel = "documentation_v52-child-" + "q" * 100                          # below --output: "<sep>documentation_v52" + "/" + rel
        output = _base_with_length(150)
        base = output + os.sep + "documentation_v52"
        with self.assertRaises(OutputPathTooLongError) as caught:
            check_output_paths(base, [rel], self.LIMIT, output_root=output)
        suggested = caught.exception.suggested_max_output_length
        self.assertEqual(suggested, self.LIMIT - ATOMIC_TEMP_OVERHEAD - 1 - (len("documentation_v52") + 1 + len(rel)))
        ok_output = _base_with_length(suggested)
        check_output_paths(ok_output + os.sep + "documentation_v52", [rel], self.LIMIT, output_root=ok_output)   # fits exactly
        too_long = _base_with_length(suggested + 1)
        with self.assertRaises(OutputPathTooLongError):
            check_output_paths(too_long + os.sep + "documentation_v52", [rel], self.LIMIT, output_root=too_long)

    def test_no_limit_means_no_check(self):
        check_output_paths(_base_with_length(100), ["a" * 5000], None)

    def test_limit_depends_on_platform_and_opt_in(self):
        self.assertIsNone(applicable_path_limit(False, os_name="posix"))
        self.assertIsNone(applicable_path_limit(True, os_name="posix"))                       # --long-paths is inert off Windows
        with patch.object(path_limits, "windows_long_paths_enabled", return_value=False):
            self.assertEqual(applicable_path_limit(False, os_name="nt"), 259)
            self.assertGreater(applicable_path_limit(True, os_name="nt"), 30000)
        with patch.object(path_limits, "windows_long_paths_enabled", return_value=True):
            self.assertGreater(applicable_path_limit(False, os_name="nt"), 30000)

    def test_the_os_setting_is_read_only_and_boolean(self):
        self.assertIsInstance(path_limits.windows_long_paths_enabled(), bool)

    def test_extended_path_is_a_windows_only_change_of_handle(self):
        path = Path(tempfile.gettempdir()) / "x"
        extended = to_extended_path(path)
        if IS_WINDOWS:
            self.assertTrue(str(extended).startswith("\\\\?\\"))
            self.assertTrue(str(extended).endswith("x"))
            self.assertEqual(to_extended_path(extended), extended)
        else:
            self.assertEqual(extended, path)


class StagePathPreflightTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.out = Path(self._tmp.name)

    def test_nothing_is_written_or_deleted_when_a_path_is_too_long(self):
        root = self.out / "documentation_v52"
        _write(root, _files())
        before = _tree(root)
        changed = dict(_files())
        changed["developer/" + "z" * 300 + ".md"] = "# long\n"
        with self.assertRaises(OutputPathTooLongError):
            _write(root, changed, logical_root=root, output_dir=self.out, path_limit=259 if IS_WINDOWS else 240 + 0)
        self.assertEqual(_tree(root), before)                       # no document written, no orphan deleted, manifest untouched

    def test_nothing_is_created_when_the_stage_is_aborted_on_a_fresh_output(self):
        source = self._source()
        with patch.object(engine, "applicable_path_limit", return_value=len(str(self.out)) + 40):
            with self.assertRaises(OutputPathTooLongError):
                generate_documentation_v52(source, self.out)
        self.assertFalse((self.out / "documentation_v52").exists())

    def test_the_stage_reports_output_path_too_long_instead_of_an_ambiguous_error(self):
        indexes = self._indexes()
        with tempfile.TemporaryDirectory() as out, patch.object(engine, "applicable_path_limit", return_value=len(out) + 40):
            outcome = pipeline_stages.render_documentation(out, indexes)
            failure = dict(outcome.failures)["documentation_v52"]
            self.assertIn("OUTPUT_PATH_TOO_LONG", failure)
            self.assertNotIn("FileNotFoundError", failure)
            self.assertFalse(Path(out, "documentation_v52").exists())

    def test_manifest_relative_paths_are_unchanged_by_long_paths(self):
        source = self._source()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            normal = generate_documentation_v52(source, a)
            extended = generate_documentation_v52(source, b, long_paths=True)
            self.assertEqual(normal.files, extended.files)
            self.assertEqual(Path(a, "documentation_v52", MANIFEST_FILENAME).read_bytes(),
                             Path(b, "documentation_v52", MANIFEST_FILENAME).read_bytes())
            self.assertEqual(extended.output_dir, Path(b) / "documentation_v52")      # logical path, not the extended handle
            self.assertFalse(any(f.startswith("\\\\?") for f in extended.files))

    @unittest.skipUnless(IS_WINDOWS, "extended-length paths are a Windows mechanism")
    def test_long_paths_writes_beyond_max_path_and_default_refuses_before_writing(self):
        deep = self.out
        while len(str(deep)) < 300:
            deep = deep / ("d" * 50)
        long_files = {"developer/" + "f" * 40 + ".md": "# largo\n", "README.md": "# r\n"}
        try:
            with patch.object(path_limits, "windows_long_paths_enabled", return_value=False):
                with self.assertRaises(OutputPathTooLongError):
                    writer.write_tree(
                        deep / "documentation_v52", long_files, DocumentationV52Result(output_dir=deep),
                        logical_root=deep / "documentation_v52", output_dir=deep, path_limit=applicable_path_limit(False),
                    )
                self.assertFalse(os.path.exists(to_extended_path(deep / "documentation_v52")))        # nothing created
                fs_root = to_extended_path(deep / "documentation_v52")
                result = DocumentationV52Result(output_dir=deep / "documentation_v52")
                writer.write_tree(fs_root, long_files, result, logical_root=deep / "documentation_v52",
                                   output_dir=deep, path_limit=applicable_path_limit(True))
                self.assertEqual(result.files, sorted(long_files))                                  # relative, logical
                self.assertEqual((fs_root / "developer" / ("f" * 40 + ".md")).read_bytes(), b"# largo\n")
                again = DocumentationV52Result(output_dir=deep / "documentation_v52")
                writer.write_tree(fs_root, long_files, again, logical_root=deep / "documentation_v52",
                                   output_dir=deep, path_limit=applicable_path_limit(True))
                self.assertEqual(again.write_stats["documents_skipped_write"], 2)                   # write-skip works on extended paths
        finally:
            shutil.rmtree(to_extended_path(self.out), ignore_errors=True)

    def _indexes(self) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            return analyze_repository(FULL_SAMPLE, tmp, None, 12)

    def _source(self) -> dict:
        return pipeline_stages.source_from_indexes(self._indexes(), [])


class CliLongPathsOptionTests(unittest.TestCase):
    def test_full_accepts_long_paths_and_defaults_to_false(self):
        parser = cli_parser.build_parser()
        self.assertTrue(parser.parse_args(["full", "repo", "--long-paths"]).long_paths)
        self.assertFalse(parser.parse_args(["full", "repo"]).long_paths)

    def test_analyze_does_not_accept_it(self):
        with self.assertRaises(SystemExit):
            cli_parser.build_parser().parse_args(["analyze", "repo", "--long-paths"])

    def test_router_passes_it_to_the_pipeline(self):
        args = cli_parser.build_parser().parse_args(["full", "repo", "--long-paths"])
        with patch.object(router, "run_full_pipeline") as run:
            run.return_value.status = router.RunStatus.SUCCESS
            router.route(args, analyze_repository=None)
        self.assertTrue(run.call_args.kwargs["long_paths"])


if __name__ == "__main__":
    unittest.main()
