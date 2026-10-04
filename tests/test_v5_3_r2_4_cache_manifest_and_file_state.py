from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import os
import random
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import cache as cache_pkg
from legacy_documenter.cache import (
    CACHE_DIRNAME, FILE_STATE_FILENAME, MANIFEST_FILENAME, MODE_COLD, MODE_FALLBACK_FULL, MODE_WARM, CacheWriteError,
    FileRecord, begin_cache_session, build_file_state, diff_file_states, git_metadata, normalize_root, parse_file_state,
    render_file_state, repository_identity, validate_cache, write_cache,
)
from legacy_documenter.cache import context as cache_context, store
from legacy_documenter.cache.manifest import CACHE_SCHEMA_VERSION, MANIFEST_CONTRACT, STATE_COMPLETE
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.output_manifest import build_output_manifest
from legacy_documenter.fingerprints import CodeFingerprint
from legacy_documenter.models import SourceFile

ROOT = Path(__file__).resolve().parent.parent
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
NONDETERMINISTIC = {"RUN_SUMMARY.json", "RUN_SUMMARY.md", "repository.json"}


def _source(path: str, file_type: str = "vb_source") -> SourceFile:
    return SourceFile(relative_path=path, extension=Path(path).suffix, size=0, folder="", name=Path(path).name, file_type=file_type)


def _write_files(root: Path, files: dict[str, bytes]) -> None:
    for relative, data in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def _state(root: Path, kinds: dict[str, str]) -> list[FileRecord]:
    return build_file_state(root, [_source(p, k) for p, k in kinds.items()])


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in NONDETERMINISTIC and CACHE_DIRNAME not in p.relative_to(root).parts[:1]}


class _TmpCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)


class FileStateTests(_TmpCase):
    KINDS = {"a.vb": "vb_source", "b.aspx": "aspx", "c.dll": "assembly", "d.js": "javascript"}

    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        _write_files(self.repo, {"a.vb": b"Sub A()\r\nEnd Sub\r\n", "b.aspx": b"<html/>\n", "c.dll": b"\x00\x01\x02", "d.js": b"x=1;\n"})

    def _diff(self, before, kinds=None):
        return diff_file_states(before, _state(self.repo, kinds or self.KINDS))

    def test_unchanged_modified_added_deleted(self):
        before = _state(self.repo, self.KINDS)
        (self.repo / "a.vb").write_bytes(b"Sub A2()\r\nEnd Sub\r\n")
        (self.repo / "new.vb").write_bytes(b"Sub N()\n")
        (self.repo / "d.js").unlink()
        kinds = {**{k: v for k, v in self.KINDS.items() if k != "d.js"}, "new.vb": "vb_source"}
        diff = self._diff(before, kinds)
        self.assertEqual(diff.modified, ["a.vb"])
        self.assertEqual(diff.added, ["new.vb"])
        self.assertEqual(diff.deleted, ["d.js"])
        self.assertEqual(diff.unchanged, ["b.aspx", "c.dll"])

    def test_rename_candidate_is_diagnostic_and_stays_deleted_plus_added(self):
        before = _state(self.repo, self.KINDS)
        (self.repo / "b.aspx").rename(self.repo / "renamed.aspx")
        kinds = {**{k: v for k, v in self.KINDS.items() if k != "b.aspx"}, "renamed.aspx": "aspx"}
        diff = self._diff(before, kinds)
        self.assertEqual(diff.renamed_candidates, [{"from": "b.aspx", "to": "renamed.aspx", "basis": "semantic"}])
        self.assertEqual((diff.deleted, diff.added), (["b.aspx"], ["renamed.aspx"]))  # rename = deleted + added
        self.assertNotIn("b.aspx", diff.unchanged)
        self.assertNotIn("renamed.aspx", diff.unchanged)

    def test_rename_of_non_analyzed_file_uses_raw_hash(self):
        before = _state(self.repo, self.KINDS)
        (self.repo / "c.dll").rename(self.repo / "c2.dll")
        kinds = {**{k: v for k, v in self.KINDS.items() if k != "c.dll"}, "c2.dll": "assembly"}
        self.assertEqual(self._diff(before, kinds).renamed_candidates, [{"from": "c.dll", "to": "c2.dll", "basis": "raw"}])

    def test_empty_files_are_never_rename_candidates_and_pairing_is_deterministic(self):
        _write_files(self.repo, {"e1.vb": b"", "x1.vb": b"same\n", "x2.vb": b"same\n"})
        kinds = {**self.KINDS, "e1.vb": "vb_source", "x1.vb": "vb_source", "x2.vb": "vb_source"}
        before = _state(self.repo, kinds)
        for name in ("e1.vb", "x1.vb", "x2.vb"):
            (self.repo / name).rename(self.repo / ("n_" + name))
        renamed = {**self.KINDS, "n_e1.vb": "vb_source", "n_x1.vb": "vb_source", "n_x2.vb": "vb_source"}
        pairs = self._diff(before, renamed).renamed_candidates
        self.assertEqual([(p["from"], p["to"]) for p in pairs], [("x1.vb", "n_x1.vb"), ("x2.vb", "n_x2.vb")])

    def test_crlf_lf_raw_changes_semantic_same(self):
        before = _state(self.repo, self.KINDS)
        (self.repo / "a.vb").write_bytes(b"Sub A()\nEnd Sub\n")
        after = _state(self.repo, self.KINDS)
        old = next(r for r in before if r.path == "a.vb")
        new = next(r for r in after if r.path == "a.vb")
        self.assertNotEqual(old.sha256_raw, new.sha256_raw)
        self.assertEqual(old.sha256_semantic, new.sha256_semantic)
        diff = diff_file_states(before, after)
        self.assertIn("a.vb", diff.unchanged)
        self.assertEqual(diff.line_ending_only, ["a.vb"])
        self.assertEqual(diff.modified, [])

    def test_bom_change_is_modified(self):
        before = _state(self.repo, self.KINDS)
        (self.repo / "a.vb").write_bytes(b"\xef\xbb\xbf" + b"Sub A()\r\nEnd Sub\r\n")
        self.assertEqual(self._diff(before).modified, ["a.vb"])

    def test_non_analyzed_file_has_no_semantic_hash_and_compares_raw(self):
        records = {r.path: r for r in _state(self.repo, self.KINDS)}
        self.assertIsNone(records["c.dll"].sha256_semantic)
        self.assertIsNone(records["d.js"].sha256_semantic)
        self.assertEqual(records["c.dll"].sha256_raw, hashlib.sha256(b"\x00\x01\x02").hexdigest())
        before = list(records.values())
        (self.repo / "d.js").write_bytes(b"x=1;\r\n")  # line endings only, but not an analyzed type
        self.assertEqual(self._diff(before).modified, ["d.js"])

    def test_raw_hash_is_the_real_bytes_hash_like_source_artifact(self):
        from legacy_documenter.evidence.builder import _hash_file

        for record in _state(self.repo, self.KINDS):
            self.assertEqual(record.sha256_raw, _hash_file(self.repo / record.path))

    def test_mtime_without_content_change_is_unchanged(self):
        before = _state(self.repo, self.KINDS)
        for path in self.repo.iterdir():
            os.utime(path, (1_000_000, 1_000_000))
        after = _state(self.repo, self.KINDS)
        self.assertNotEqual({r.path: r.mtime_ns for r in before}, {r.path: r.mtime_ns for r in after})
        diff = diff_file_states(before, after)
        self.assertEqual((diff.modified, diff.added, diff.deleted), ([], [], []))
        self.assertEqual(len(diff.unchanged), 4)

    def test_file_type_change_is_modified(self):
        before = _state(self.repo, self.KINDS)
        self.assertEqual(self._diff(before, {**self.KINDS, "d.js": "other"}).modified, ["d.js"])

    def test_unreadable_file_is_recorded_and_never_unchanged(self):
        (self.repo / "gone.vb").write_bytes(b"x")
        kinds = {**self.KINDS, "gone.vb": "vb_source"}
        before = _state(self.repo, kinds)
        (self.repo / "gone.vb").unlink()
        after = _state(self.repo, kinds)  # still listed by the scanner, now unreadable
        record = next(r for r in after if r.path == "gone.vb")
        self.assertFalse(record.readable)
        self.assertEqual((record.sha256_raw, record.sha256_semantic, record.mtime_ns), (None, None, None))
        diff = diff_file_states(before, after)
        self.assertEqual(diff.modified, ["gone.vb"])
        self.assertNotIn("gone.vb", diff_file_states(after, after).unchanged)

    def test_order_is_deterministic_and_json_bytes_are_deterministic(self):
        sources = [_source(p, k) for p, k in self.KINDS.items()]
        shuffled = list(sources)
        random.Random(7).shuffle(shuffled)
        first = render_file_state(build_file_state(self.repo, sources))
        self.assertEqual(first, render_file_state(build_file_state(self.repo, shuffled)))
        self.assertEqual(first, render_file_state(build_file_state(self.repo, sources, workers=1)))
        paths = [r["path"] for r in json.loads(first)["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(render_file_state(parse_file_state(first)), first)

    def test_paths_are_normalized_to_forward_slashes(self):
        _write_files(self.repo, {"sub/deep/z.vb": b"Sub Z()\n"})
        (record,) = build_file_state(self.repo, [_source("sub\\deep\\z.vb")])
        self.assertEqual(record.path, "sub/deep/z.vb")

    def test_no_content_or_secrets_are_persisted(self):
        _write_files(self.repo, {"secret.vb": b'Dim cs = "Password=TopSecret123;Server=prod"\n'})
        raw = render_file_state(_state(self.repo, {**self.KINDS, "secret.vb": "vb_source"}))
        self.assertNotIn(b"TopSecret123", raw)
        self.assertNotIn(b"Password", raw)
        allowed = {"path", "size", "sha256_raw", "sha256_semantic", "file_type", "mtime_ns", "readable"}
        for entry in json.loads(raw)["files"]:
            self.assertEqual(set(entry), allowed)

    def test_malformed_file_state_is_rejected(self):
        good = render_file_state(_state(self.repo, self.KINDS))
        for bad in (b"", b"[]", b"{}", b'{"contract":"x"}', good.replace(b'"file_count":4', b'"file_count":5'),
                    good.replace(b'"readable"', b'"extra"', 1)):
            with self.subTest(bad[:30]):
                with self.assertRaises(ValueError):
                    parse_file_state(bad)

    def test_file_state_has_no_project_path_field_yet(self):
        # project_path would require the vbproj->compile mapping, i.e. extraction: out of R2.4's scope
        self.assertNotIn("project_path", FileRecord.__dataclass_fields__)


def _context(repo: Path, **changes) -> cache_context.CacheContext:
    base = cache_context.build_context(repo, ["x"], 12)
    return dataclasses.replace(base, **changes) if changes else base


class CacheManifestTests(_TmpCase):
    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        _write_files(self.repo, {"a.vb": b"Sub A()\n", "b.aspx": b"<p/>\n"})
        self.records = _state(self.repo, {"a.vb": "vb_source", "b.aspx": "aspx"})
        self.cache = self.tmp / "out" / CACHE_DIRNAME
        self.ctx = _context(self.repo)

    def _write(self, ctx=None) -> dict:
        return write_cache(self.cache, ctx or self.ctx, self.records)

    def _validate(self, ctx=None):
        return validate_cache(self.cache, ctx or self.ctx)

    def _rewrite_manifest(self, mutate):
        path = self.cache / MANIFEST_FILENAME
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_cold_start_without_cache(self):
        result = self._validate()
        self.assertEqual((result.valid, result.mode, result.reason), (False, MODE_COLD, "NO_CACHE"))

    def test_valid_manifest_is_warm_and_returns_previous_records(self):
        self._write()
        result = self._validate()
        self.assertEqual((result.valid, result.mode, result.reason), (True, MODE_WARM, None))
        self.assertEqual(result.records, self.records)
        self.assertEqual(result.informational_differences, [])

    def test_manifest_contents(self):
        manifest = self._write()
        self.assertEqual(manifest["contract"], MANIFEST_CONTRACT)
        self.assertEqual(manifest["cache_schema_version"], CACHE_SCHEMA_VERSION)
        self.assertEqual(manifest["state"], STATE_COMPLETE)
        self.assertEqual(set(manifest["versions"]), {
            "analyzer_version", "analyzer_code_fingerprint", "evidence_schema_version", "renderer_versions",
            "template_profile_fingerprint", "extraction_cache_schema_version"})
        self.assertEqual(manifest["file_state"]["file_count"], 2)
        self.assertEqual(manifest["file_state"]["sha256"], hashlib.sha256((self.cache / FILE_STATE_FILENAME).read_bytes()).hexdigest())
        self.assertEqual(manifest["file_state"]["path"], FILE_STATE_FILENAME)
        self.assertIs(manifest["validity"]["complete"], True)
        self.assertEqual(set(manifest["informative"]), {"git_head", "git_branch", "generated_at"})
        self.assertEqual(manifest["repository_identity"], repository_identity(self.repo))
        self.assertEqual(json.loads((self.cache / MANIFEST_FILENAME).read_text(encoding="utf-8")), manifest)
        self.assertEqual(sorted(p.name for p in self.cache.iterdir()), [MANIFEST_FILENAME, FILE_STATE_FILENAME])

    def test_absent_manifest_with_file_state_is_incomplete(self):
        self._write()
        (self.cache / MANIFEST_FILENAME).unlink()
        result = self._validate()
        self.assertEqual((result.valid, result.mode, result.reason), (False, MODE_FALLBACK_FULL, "INCOMPLETE_CACHE"))

    def test_corrupt_manifest_falls_back_to_full(self):
        self._write()
        path = self.cache / MANIFEST_FILENAME
        for garbage in (b"", b"not json", b"[1]", b'{"contract":"Other"}', b"\xff\xfe\x00", b'{"contract":"%s"}' % MANIFEST_CONTRACT.encode()):
            with self.subTest(garbage):
                path.write_bytes(garbage)
                result = self._validate()
                self.assertFalse(result.valid)
                self.assertEqual(result.mode, MODE_FALLBACK_FULL)

    def test_state_not_complete(self):
        self._write()
        self._rewrite_manifest(lambda m: m.update(state="IN_PROGRESS"))
        self.assertEqual(self._validate().reason, "STATE_NOT_COMPLETE")
        self._write()
        self._rewrite_manifest(lambda m: m["validity"].update(complete=False))
        self.assertEqual(self._validate().reason, "STATE_NOT_COMPLETE")

    def test_unknown_schema(self):
        self._write()
        self._rewrite_manifest(lambda m: m.update(cache_schema_version="99"))
        self.assertEqual(self._validate().reason, "UNKNOWN_CACHE_SCHEMA")

    def test_file_state_checksum_missing_and_corrupt(self):
        self._write()
        state = self.cache / FILE_STATE_FILENAME
        state.write_bytes(state.read_bytes() + b" ")
        self.assertEqual(self._validate().reason, "FILE_STATE_CHECKSUM_MISMATCH")
        state.unlink()
        self.assertEqual(self._validate().reason, "FILE_STATE_MISSING")
        self._write()
        bad = b"not a file state"
        state.write_bytes(bad)
        self._rewrite_manifest(lambda m: m["file_state"].update(sha256=hashlib.sha256(bad).hexdigest()))
        self.assertEqual(self._validate().reason, "FILE_STATE_CORRUPT")

    def test_manifest_cannot_redirect_to_another_file(self):
        self._write()
        self._rewrite_manifest(lambda m: m["file_state"].update(path="../elsewhere.json"))
        self.assertFalse(self._validate().valid)

    def test_different_repository_never_reuses_the_cache(self):
        self._write()
        other = self.tmp / "other_repo"
        other.mkdir()
        result = self._validate(_context(other))
        self.assertEqual((result.valid, result.reason), (False, "REPOSITORY_MISMATCH"))

    def test_each_extraction_incompatibility_forces_full(self):
        self._write()
        fp = dataclasses.replace(self.ctx.analyzer_code_fingerprint, sha256="0" * 64)
        cases = {
            "ANALYZER_VERSION_MISMATCH": {"analyzer_version": self.ctx.analyzer_version + 1},
            "ANALYZER_CODE_FINGERPRINT_MISMATCH": {"analyzer_code_fingerprint": fp},
            "EVIDENCE_SCHEMA_MISMATCH": {"evidence_schema_version": "9.9"},
            "ANALYSIS_CONFIG_MISMATCH": {"analysis_config_fingerprint": "f" * 64},
            "ANALYZER_SOURCES_UNAVAILABLE": {"analyzer_code_fingerprint": CodeFingerprint("unavailable", None, 0, "x")},
        }
        for reason, change in cases.items():
            with self.subTest(reason):
                result = self._validate(dataclasses.replace(self.ctx, **change))
                self.assertEqual((result.valid, result.mode, result.reason), (False, MODE_FALLBACK_FULL, reason))

    def test_real_config_change_forces_full(self):
        self._write()
        result = self._validate(cache_context.build_context(self.repo, ["different"], 12))
        self.assertEqual(result.reason, "ANALYSIS_CONFIG_MISMATCH")
        result = self._validate(cache_context.build_context(self.repo, ["x"], 13))
        self.assertEqual(result.reason, "ANALYSIS_CONFIG_MISMATCH")
        self.assertTrue(self._validate(cache_context.build_context(self.repo, ["x"], 12)).valid)

    def test_projection_and_git_differences_do_not_invalidate_extraction(self):
        self._write()
        changes = {
            "renderer_versions": {**self.ctx.renderer_versions, "hydration": {"model_version": "future"}},
            "template_profile_fingerprint": "a" * 64,
            "projection_config_fingerprint": "b" * 64,
            "git": {"git_head": "deadbeef", "git_branch": "other-branch"},
        }
        result = self._validate(dataclasses.replace(self.ctx, **changes))
        self.assertTrue(result.valid)
        self.assertEqual(result.mode, MODE_WARM)
        self.assertEqual(sorted(result.informational_differences), sorted(
            ["renderer_versions", "template_profile_fingerprint", "projection_config_fingerprint", "git_head", "git_branch"]))

    def test_manifest_is_written_last_and_previous_manifest_is_removed_first(self):
        self._write()
        calls = []
        real = store.atomic_write_bytes

        def spy(path, content):
            calls.append((Path(path).name, (self.cache / MANIFEST_FILENAME).exists()))
            real(path, content)

        with patch.object(store, "atomic_write_bytes", spy):
            self._write()
        self.assertEqual(calls, [(FILE_STATE_FILENAME, False), (MANIFEST_FILENAME, False)])
        self.assertTrue(self._validate().valid)

    def test_interruption_before_the_manifest_leaves_no_valid_cache(self):
        self._write()
        real = store.atomic_write_bytes

        def interrupt(path, content):
            if Path(path).name == MANIFEST_FILENAME:
                raise KeyboardInterrupt
            real(path, content)

        with patch.object(store, "atomic_write_bytes", interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self._write()
        result = self._validate()
        self.assertEqual((result.valid, result.mode, result.reason), (False, MODE_FALLBACK_FULL, "INCOMPLETE_CACHE"))

    def test_write_verifies_file_state_by_rereading_it(self):
        real = store.atomic_write_bytes

        def corrupting(path, content):
            real(path, content + b" " if Path(path).name == FILE_STATE_FILENAME else content)

        with patch.object(store, "atomic_write_bytes", corrupting):
            with self.assertRaises(CacheWriteError):
                self._write()
        self.assertFalse((self.cache / MANIFEST_FILENAME).exists())

    def test_unavailable_analyzer_sources_are_never_written(self):
        ctx = dataclasses.replace(self.ctx, analyzer_code_fingerprint=CodeFingerprint("unavailable", None, 0, "x"))
        with self.assertRaises(CacheWriteError):
            self._write(ctx)
        self.assertFalse((self.cache / MANIFEST_FILENAME).exists())

    def test_orphan_temporaries_are_swept(self):
        self.cache.mkdir(parents=True)
        (self.cache / ".file_state.json.ab12cd34.tmp").write_bytes(b"x")
        (self.cache / "keep.txt").write_bytes(b"x")
        self.assertEqual(store.sweep_temporary_files(self.cache), 1)
        self.assertEqual(sorted(p.name for p in self.cache.iterdir()), ["keep.txt"])
        self.assertEqual(store.sweep_temporary_files(self.tmp / "missing"), 0)


class IdentityTests(_TmpCase):
    def test_normalization(self):
        repo = self.tmp / "Repo"
        repo.mkdir()
        normalized = normalize_root(repo)
        self.assertNotIn("\\", normalized)
        self.assertFalse(normalized.endswith("/"))
        self.assertEqual(normalize_root(str(repo) + os.sep), normalized)
        if os.name == "nt":
            self.assertEqual(normalize_root(str(repo).upper()), normalized)
            self.assertEqual(normalized, normalized.lower())

    def test_identity_is_path_based_not_content_based(self):
        repo = self.tmp / "r"
        repo.mkdir()
        first = repository_identity(repo)
        (repo / "f.vb").write_text("x", encoding="utf-8")
        self.assertEqual(repository_identity(repo), first)
        other = self.tmp / "r2"
        other.mkdir()
        self.assertNotEqual(repository_identity(other)["root_fingerprint"], first["root_fingerprint"])
        self.assertEqual(first["root_fingerprint"], hashlib.sha256(first["root_normalized"].encode("utf-8")).hexdigest())

    def test_git_metadata_is_best_effort(self):
        repo = self.tmp / "g"
        (repo / ".git" / "refs" / "heads").mkdir(parents=True)
        self.assertEqual(git_metadata(repo), {"git_head": None, "git_branch": None})
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/feature/x\n", encoding="utf-8")
        self.assertEqual(git_metadata(repo), {"git_head": None, "git_branch": "feature/x"})
        (repo / ".git" / "refs" / "heads" / "feature").mkdir()
        (repo / ".git" / "refs" / "heads" / "feature" / "x").write_text("abc123\n", encoding="utf-8")
        self.assertEqual(git_metadata(repo), {"git_head": "abc123", "git_branch": "feature/x"})
        (repo / ".git" / "HEAD").write_text("0123abcd\n", encoding="utf-8")
        self.assertEqual(git_metadata(repo), {"git_head": "0123abcd", "git_branch": None})
        self.assertEqual(git_metadata(self.tmp / "none"), {"git_head": None, "git_branch": None})


class RuntimeIndependenceTests(unittest.TestCase):
    def test_cache_package_reads_no_governance_and_calls_no_ai(self):
        for path in sorted(Path(cache_pkg.__file__).parent.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            constants = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            for forbidden in ("PROJECT_STATE", "AGENTS.md", "CLAUDE.md", "prompts", "docs/", "tests", "copilot", "subprocess"):
                self.assertFalse(any(forbidden in c for c in constants if len(c) < 120), (path.name, forbidden))
            imported = {n.module.split(".")[-1] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
            imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
            self.assertFalse(imported & {"llm", "knowledge", "orchestration", "subprocess", "requests"}, path.name)

    def test_cache_never_touches_extraction(self):
        for path in Path(cache_pkg.__file__).parent.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("extract_repository", text, path.name)
            self.assertNotIn("legacy_documenter.extractors", text, path.name)


class PipelineIntegrationTests(_TmpCase):
    def _run(self, out: Path, **kwargs):
        return run_full_pipeline(FULL_SAMPLE, out, None, 12, **kwargs)

    def _logs(self, out: Path, **kwargs):
        with self.assertLogs("legacy_documenter.cache.session", level="INFO") as captured:
            result = self._run(out, **kwargs)
        return result, "\n".join(captured.output)

    def test_first_run_creates_a_valid_cold_cache(self):
        out = self.tmp / "out"
        result, log = self._logs(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertIn("'mode': 'cold'", log)
        self.assertEqual(sorted(p.name for p in (out / CACHE_DIRNAME).iterdir()), [MANIFEST_FILENAME, "RUN_METRICS.json", "extraction", FILE_STATE_FILENAME])  # R2.7 adds the metrics file
        self.assertTrue(validate_cache(out / CACHE_DIRNAME, cache_context.build_context(FULL_SAMPLE.resolve(), None, 12)).valid)

    def test_second_unchanged_run_validates_the_cache(self):
        out = self.tmp / "out"
        self._run(out)
        result, log = self._logs(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertIn("'mode': 'warm'", log)
        self.assertIn("'modified': 0, 'added': 0, 'deleted': 0, 'renamed_candidates': 0", log)
        count = json.loads((out / CACHE_DIRNAME / MANIFEST_FILENAME).read_text(encoding="utf-8"))["file_state"]["file_count"]
        self.assertIn(f"'unchanged': {count}", log)

    def test_logical_output_is_identical_with_and_without_cache(self):
        with_cache, without = self.tmp / "a", self.tmp / "b"
        self._run(with_cache)
        self._run(without, cache_mode="off")
        self.assertEqual(_tree(with_cache), _tree(without))
        self.assertTrue((with_cache / CACHE_DIRNAME).is_dir())
        self.assertFalse((without / CACHE_DIRNAME).exists())
        self._run(with_cache)  # warm rerun: still identical
        self.assertEqual(_tree(with_cache), _tree(without))

    def test_invalid_cache_means_full_but_a_correct_run_and_a_rewritten_cache(self):
        out = self.tmp / "out"
        self._run(out)
        reference = _tree(out)
        (out / CACHE_DIRNAME / MANIFEST_FILENAME).write_bytes(b"corrupt")
        result, log = self._logs(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertIn("'mode': 'fallback_full'", log)
        self.assertIn("MANIFEST_CORRUPT", log)
        self.assertEqual(_tree(out), reference)
        self.assertTrue(validate_cache(out / CACHE_DIRNAME, cache_context.build_context(FULL_SAMPLE.resolve(), None, 12)).valid)

    def test_failed_run_leaves_no_valid_manifest(self):
        out = self.tmp / "out"
        self._run(out)
        self.assertTrue((out / CACHE_DIRNAME / MANIFEST_FILENAME).is_file())
        with patch.object(stages, "render_documentation", side_effect=RuntimeError("boom")):
            result = self._run(out)
        self.assertNotEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse((out / CACHE_DIRNAME / MANIFEST_FILENAME).exists())
        # the next run is a full one and regenerates the cache
        self.assertEqual(self._run(out).status, RunStatus.SUCCESS)
        self.assertTrue((out / CACHE_DIRNAME / MANIFEST_FILENAME).is_file())

    def test_deleting_the_cache_directory_changes_no_result(self):
        out = self.tmp / "out"
        self._run(out)
        reference = _tree(out)
        shutil.rmtree(out / CACHE_DIRNAME)
        result, log = self._logs(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertIn("'mode': 'cold'", log)
        self.assertEqual(_tree(out), reference)

    def test_no_stage_is_skipped_and_extraction_is_not_reused(self):
        out = self.tmp / "out"
        self._run(out)
        with patch.object(stages, "extract_repository", wraps=stages.extract_repository) as extract:
            result = self._run(out)
        self.assertEqual(extract.call_count, 1)  # warm cache, extraction still runs in full
        statuses = {s.stage.value: s.status.value for s in result.stages}
        self.assertEqual(statuses["EXTRACTION"], "SUCCESS")
        self.assertEqual(sum(1 for v in statuses.values() if v == "SKIPPED_DUE_TO_UPSTREAM_FAILURE"), 0)
        self.assertEqual(statuses["DOCUMENTATION"], "SUCCESS")

    def test_changed_repository_content_is_reported_by_the_diff(self):
        repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, repo)
        out = self.tmp / "out"
        run_full_pipeline(repo, out, None, 12)
        vb = next(p for p in repo.rglob("*.vb"))
        vb.write_bytes(vb.read_bytes() + b"\n' changed\n")
        (repo / "added_module.vb").write_bytes(b"Module Added\nEnd Module\n")
        with self.assertLogs("legacy_documenter.cache.session", level="INFO") as captured:
            run_full_pipeline(repo, out, None, 12)
        log = "\n".join(captured.output)
        self.assertIn("'mode': 'warm'", log)
        self.assertIn("'modified': 1, 'added': 1, 'deleted': 0", log)

    def test_cache_write_failure_does_not_fail_the_run(self):
        out = self.tmp / "out"
        with patch("legacy_documenter.cache.session.write_cache", side_effect=OSError("disk full")):
            with self.assertLogs("legacy_documenter.cache.session", level="WARNING") as captured:
                result = self._run(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertIn("disk full", "\n".join(captured.output))
        self.assertFalse((out / CACHE_DIRNAME / MANIFEST_FILENAME).exists())

    def test_cache_failure_while_building_state_disables_cache_but_not_the_run(self):
        out = self.tmp / "out"
        with patch("legacy_documenter.cache.session.build_file_state", side_effect=RuntimeError("hash failure")):
            with self.assertLogs("legacy_documenter.cache.session", level="WARNING"):
                result = self._run(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse((out / CACHE_DIRNAME).exists())

    def test_cache_mode_off_and_refresh_and_custom_dir(self):
        out = self.tmp / "out"
        self._run(out, cache_mode="off")
        self.assertFalse((out / CACHE_DIRNAME).exists())
        self._run(out)
        _, log = self._logs(out, cache_mode="refresh")
        self.assertIn("REFRESH_REQUESTED", log)
        custom = self.tmp / "elsewhere"
        self._run(self.tmp / "out2", cache_dir=custom)
        self.assertTrue((custom / MANIFEST_FILENAME).is_file())
        self.assertFalse((self.tmp / "out2" / CACHE_DIRNAME).exists())

    def test_output_manifest_excludes_the_cache_directory(self):
        out = self.tmp / "out"
        self._run(out)
        paths = {entry["path"] for entry in build_output_manifest(out)["files"]}
        self.assertTrue(paths)
        self.assertFalse(any(p.startswith(CACHE_DIRNAME) for p in paths))

    def test_unknown_cache_mode_disables_the_cache(self):
        session = begin_cache_session(FULL_SAMPLE, self.tmp / "o", [], None, 12, cache_mode="bogus")
        self.assertFalse(session.enabled)
        self.assertFalse(session.persist())


if __name__ == "__main__":
    unittest.main()
