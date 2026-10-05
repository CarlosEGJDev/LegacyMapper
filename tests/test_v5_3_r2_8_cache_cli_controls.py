from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import fingerprints
from legacy_documenter.cache import (
    CACHE_DIRNAME, CACHE_MODES, CHANGED_RATIO_EXCEEDED, MANIFEST_FILENAME, METRICS_FILENAME, VERIFY_FAILED,
    CacheOptionError, CacheOptions, CacheValidationResult, MODE_WARM, ratio_argument, resolve_cache_dir,
)
from legacy_documenter.cache import session as cache_session_module
from legacy_documenter.cache.extraction_shards import EXTRACTION_DIRNAME
from legacy_documenter.cli import router
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.parser import build_parser
from legacy_documenter.utils.write_if_changed import LEDGER
from legacy_documenter.utils.write_policy import POLICY

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "legacy_documenter"
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
NONDETERMINISTIC = {"RUN_SUMMARY.json", "RUN_SUMMARY.md", "repository.json"}


def _tree(root: Path) -> dict[str, bytes]:
    """Deterministic product bytes of `root` (the cache directory and run-specific files excluded)."""
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in NONDETERMINISTIC and p.relative_to(root).parts[0] != CACHE_DIRNAME}


def _parse(*argv: str) -> Namespace:
    return build_parser().parse_args(["full", "repo", "--output", "out", *argv])


# =========================== parser ===========================================================================
class ParserTests(unittest.TestCase):
    def test_defaults(self):
        args = _parse()
        self.assertEqual(
            (args.cache_mode, args.cache_dir, args.verify_cache, args.trust_mtime, args.incremental_max_changed_ratio),
            ("auto", None, "fast", False, None),
        )

    def test_cache_modes(self):
        self.assertEqual(CACHE_MODES, ("auto", "off", "refresh"))
        for mode in CACHE_MODES:
            self.assertEqual(_parse("--cache-mode", mode).cache_mode, mode)

    def test_invalid_mode_is_rejected(self):
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                _parse("--cache-mode", "changed")

    def test_cache_dir_with_spaces(self):
        self.assertEqual(_parse("--cache-dir", "C:\\a b\\my cache").cache_dir, "C:\\a b\\my cache")

    def test_verify_cache_forms(self):
        self.assertEqual(_parse("--verify-cache=hash").verify_cache, "hash")
        self.assertEqual(_parse("--verify-cache=fast").verify_cache, "fast")
        self.assertEqual(build_parser().parse_args(["full", "repo", "--output", "out", "--verify-cache"]).verify_cache, "hash")
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                _parse("--verify-cache=full")

    def test_trust_mtime_is_opt_in(self):
        self.assertTrue(_parse("--trust-mtime").trust_mtime)

    def test_ratio_validation(self):
        for text, expected in (("0", 0.0), ("0.25", 0.25), ("1", 1.0)):
            self.assertEqual(_parse("--incremental-max-changed-ratio", text).incremental_max_changed_ratio, expected)
        for text in ("-0.1", "1.01", "nan", "inf", "abc", ""):
            with self.assertRaises(SystemExit, msg=text):
                with patch("sys.stderr"):
                    _parse("--incremental-max-changed-ratio", text)
        with self.assertRaises(Exception):
            ratio_argument("2")

    def test_analyze_does_not_accept_cache_controls(self):
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                build_parser().parse_args(["analyze", "repo", "--output", "out", "--cache-mode", "off"])

    def test_every_new_option_is_classified_and_none_enters_a_fingerprint(self):
        classes = fingerprints.CLI_OPTION_CLASSES
        self.assertEqual(classes["cache_dir"], fingerprints.OUTPUT_LOCATION_ONLY)
        for dest in ("cache_mode", "verify_cache", "trust_mtime", "incremental_max_changed_ratio"):
            self.assertEqual(classes[dest], fingerprints.RUNTIME_ONLY, dest)
        # the config fingerprints are functions of analysis/projection inputs only
        self.assertEqual(
            fingerprints.analysis_config_fingerprint(["x"], 12), fingerprints.analysis_config_fingerprint(["x"], 12),
        )

    def test_router_maps_every_option_to_the_library_call(self):
        args = _parse("--cache-mode", "refresh", "--cache-dir", "cd", "--verify-cache", "--trust-mtime",
                      "--incremental-max-changed-ratio", "0.5")
        with patch.object(router, "run_full_pipeline") as run:
            run.return_value.status = RunStatus.SUCCESS
            router._route_full(args)
        kwargs = run.call_args.kwargs
        self.assertEqual(
            (kwargs["cache_mode"], kwargs["cache_dir"], kwargs["verify_cache"], kwargs["trust_mtime"],
             kwargs["incremental_max_changed_ratio"]),
            ("refresh", "cd", "hash", True, 0.5),
        )


class OptionsUnitTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(CacheOptions().validate().mode, "auto")
        for bad in (CacheOptions(mode="x"), CacheOptions(verify="deep"), CacheOptions(max_changed_ratio=1.5),
                    CacheOptions(max_changed_ratio=float("nan"))):
            with self.assertRaises(CacheOptionError):
                bad.validate()

    def test_default_cache_dir_is_inside_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(resolve_cache_dir(Path(tmp) / "r", Path(tmp) / "o", None), (Path(tmp) / "o").resolve() / CACHE_DIRNAME)

    def test_unsafe_cache_dirs_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo, out = tmp / "repo", tmp / "work" / "out"
            repo.mkdir()
            out.mkdir(parents=True)
            (tmp / "afile").write_text("x")
            for bad in (repo, repo / "sub", tmp, out, out.parent, tmp / "afile"):
                with self.assertRaises(CacheOptionError, msg=str(bad)):
                    resolve_cache_dir(repo, out, bad)
            self.assertEqual(resolve_cache_dir(repo, out, tmp / "elsewhere"), (tmp / "elsewhere").resolve())
            self.assertEqual(resolve_cache_dir(repo, out, out / "mine"), (out / "mine").resolve())


# =========================== behavior =========================================================================
class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, self.repo)
        self.out = self.tmp / "out"
        self.cache = self.out / CACHE_DIRNAME

    def run_pipeline(self, repo=None, out=None, **kwargs):
        return run_full_pipeline(repo or self.repo, out or self.out, kwargs.pop("excludes", None), 12, **kwargs)

    def metrics(self, cache: Path | None = None) -> dict:
        return json.loads(((cache or self.cache) / METRICS_FILENAME).read_text(encoding="utf-8"))

    def reference(self) -> dict[str, bytes]:
        ref = self.tmp / "reference"
        if not ref.exists():
            run_full_pipeline(self.repo, ref, None, 12, cache_mode="off")
        return _tree(ref)

    def assertEquivalent(self, out: Path | None = None):
        self.assertEqual(_tree(out or self.out), self.reference())

    def shard_files(self, cache: Path | None = None) -> list[Path]:
        return sorted(((cache or self.cache) / EXTRACTION_DIRNAME).glob("ex-*.json"))

    def edit_source(self):
        target = self.repo / "Bl" / "CustomerService.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\n' changed\r\n", encoding="utf-8")
        return target


class ModeMatrixTests(_Case):
    def test_auto_cold_then_warm_then_equivalent(self):
        self.run_pipeline(cache_mode="auto")
        self.assertEqual((self.metrics()["mode"], self.metrics()["fallback_reason"]), ("full", "NO_CACHE"))
        self.run_pipeline(cache_mode="auto")
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"]), ("incremental", "warm"))
        self.assertGreater(document["extraction_cache"]["extraction_cache_hits"], 0)
        self.assertEqual(document["cache_controls"]["requested_mode"], "auto")
        self.assertEquivalent()

    def test_auto_corrupt_and_incompatible_fall_back_to_full(self):
        self.run_pipeline()
        (self.cache / MANIFEST_FILENAME).write_bytes(b"corrupt")
        self.run_pipeline()
        self.assertEqual((self.metrics()["session_mode"], self.metrics()["fallback_reason"]), ("fallback_full", "MANIFEST_CORRUPT"))
        manifest_path = self.cache / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["versions"]["analyzer_version"] = "0.0-other"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.run_pipeline()
        self.assertEqual((self.metrics()["session_mode"], self.metrics()["fallback_reason"]), ("fallback_full", "ANALYZER_VERSION_MISMATCH"))
        self.assertEquivalent()

    def test_auto_extraction_schema_mismatch_reextracts_and_heals(self):
        self.run_pipeline()
        manifest_path = self.cache / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["versions"]["extraction_cache_schema_version"] = 999
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.run_pipeline()
        document = self.metrics()
        self.assertEqual(document["extraction_cache"]["reuse_disabled_reason"], "EXTRACTION_CACHE_SCHEMA_MISMATCH")
        self.assertEqual(document["extraction_cache"]["extraction_cache_hits"], 0)
        self.run_pipeline()
        self.assertGreater(self.metrics()["extraction_cache"]["extraction_cache_hits"], 0)
        self.assertEquivalent()

    def test_off_reads_and_writes_no_cache_and_creates_no_directory(self):
        self.run_pipeline(cache_mode="off")
        self.assertFalse(self.cache.exists())
        self.assertEquivalent()

    def test_off_leaves_an_existing_cache_untouched_and_never_reuses_it(self):
        self.run_pipeline()
        before = {p.name: p.read_bytes() for p in self.cache.rglob("*") if p.is_file()}
        self.edit_source()
        self.run_pipeline(cache_mode="off")
        after = {p.name: p.read_bytes() for p in self.cache.rglob("*") if p.is_file()}
        self.assertEqual(before, after)  # manifest, shards, file state and metrics: nothing read-modify-written

    def test_off_is_the_v52_write_path_and_the_policy_never_leaks(self):
        self.run_pipeline(cache_mode="off")
        self.assertTrue(POLICY.skip_identical)  # restored after the run: a library caller's later writes are unaffected
        self.run_pipeline(cache_mode="off")  # same output again: everything is rewritten, nothing skipped
        self.assertEqual(sum(f.skipped_identical for f in LEDGER.families.values()), 0)
        self.assertGreater(sum(f.written for f in LEDGER.families.values()), 0)
        self.run_pipeline(cache_mode="auto")
        self.run_pipeline(cache_mode="auto")
        self.assertGreater(sum(f.skipped_identical for f in LEDGER.families.values()), 0)
        self.assertEquivalent()

    def test_policy_is_restored_even_when_the_run_raises(self):
        with patch.object(cache_session_module, "begin_cache_session", side_effect=KeyboardInterrupt),                 patch("legacy_documenter.cli.full_pipeline.begin_cache_session", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_pipeline(cache_mode="off")
        self.assertTrue(POLICY.skip_identical)

    def test_refresh_ignores_a_valid_cache_and_rebuilds_it(self):
        self.run_pipeline()
        self.run_pipeline(cache_mode="refresh")
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"], document["fallback_reason"]), ("refresh", "refresh", "REFRESH_REQUESTED"))
        self.assertEqual(document["extraction_cache"]["extraction_cache_hits"], 0)
        self.assertEqual(document["scope"]["mode"], "full")
        self.assertTrue((self.cache / MANIFEST_FILENAME).is_file())
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")  # the rebuilt cache is a usable one
        self.assertEquivalent()

    def test_refresh_replaces_a_corrupt_cache(self):
        self.run_pipeline()
        self.shard_files()[0].write_bytes(b"garbage")
        (self.cache / "file_state.json").write_bytes(b"garbage")
        self.run_pipeline(cache_mode="refresh")
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertEquivalent()

    def test_failed_refresh_leaves_no_valid_cache(self):
        self.run_pipeline()
        from legacy_documenter.cli import pipeline_stages as stages
        with patch.object(stages, "render_documentation", side_effect=RuntimeError("boom")):
            result = self.run_pipeline(cache_mode="refresh")
        self.assertNotEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse((self.cache / MANIFEST_FILENAME).exists())

    def test_unknown_mode_via_library_disables_the_cache(self):
        result = self.run_pipeline(cache_mode="bogus")
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse(self.cache.exists())

    def test_repository_mismatch_falls_back_to_full(self):
        shared = self.tmp / "shared_cache"
        self.run_pipeline(cache_dir=shared)
        other = self.tmp / "repo2"
        shutil.copytree(FULL_SAMPLE, other)
        (other / "Bl" / "CustomerService.vb").write_text("Public Class Other\r\nEnd Class\r\n", encoding="utf-8")
        self.run_pipeline(repo=other, out=self.tmp / "out2", cache_dir=shared)
        self.assertEqual((self.metrics(shared)["session_mode"], self.metrics(shared)["fallback_reason"]), ("fallback_full", "REPOSITORY_MISMATCH"))


class ExternalCacheDirTests(_Case):
    def test_external_cache_cold_warm_delete_regenerate(self):
        external = self.tmp / "my cache"  # a path with a space
        self.run_pipeline(cache_dir=external)
        self.assertFalse(self.cache.exists())  # nothing inside the output
        self.assertTrue((external / MANIFEST_FILENAME).is_file())
        self.run_pipeline(cache_dir=external)
        self.assertEqual(self.metrics(external)["session_mode"], "warm")
        self.assertEquivalent()
        shutil.rmtree(external)
        self.assertEquivalent()  # the product never depended on the cache
        self.run_pipeline(cache_dir=external)
        self.assertEqual((self.metrics(external)["session_mode"], self.metrics(external)["fallback_reason"]), ("cold", "NO_CACHE"))
        self.assertEquivalent()

    def test_external_cache_is_not_in_the_output_manifest_or_the_metrics_paths(self):
        external = self.tmp / "ext"
        self.run_pipeline(cache_dir=external)
        controls = self.metrics(external)["cache_controls"]
        self.assertEqual((controls["location"], controls["relative_dir"]), ("external", None))
        self.assertNotIn(str(self.tmp), (external / METRICS_FILENAME).read_text(encoding="utf-8"))
        self.assertFalse((self.out / "ext").exists())
        self.assertNotIn(METRICS_FILENAME, {p.name for p in self.out.rglob("*")})

    def test_internal_custom_dir_is_reported_relative(self):
        self.run_pipeline(cache_dir=self.out / "my_cache")
        controls = self.metrics(self.out / "my_cache")["cache_controls"]
        self.assertEqual((controls["location"], controls["relative_dir"]), ("internal", "my_cache"))
        self.assertNotIn(str(self.tmp), (self.out / "my_cache" / METRICS_FILENAME).read_text(encoding="utf-8"))

    def test_unsafe_cache_dirs_never_break_the_run_nor_get_written(self):
        for bad in (self.repo, self.repo / "Bl", self.out, self.tmp):
            result = self.run_pipeline(cache_dir=bad)
            self.assertEqual(result.status, RunStatus.SUCCESS, str(bad))
        self.assertFalse((self.repo / MANIFEST_FILENAME).exists())
        self.assertFalse((self.tmp / MANIFEST_FILENAME).exists())
        self.assertFalse((self.out / MANIFEST_FILENAME).exists())
        self.assertFalse((self.repo / "Bl" / MANIFEST_FILENAME).exists())

    def test_off_with_cache_dir_does_not_create_it(self):
        external = self.tmp / "ext"
        self.run_pipeline(cache_mode="off", cache_dir=external)
        self.assertFalse(external.exists())

    def test_housekeeping_only_touches_own_temporaries(self):
        external = self.tmp / "ext"
        self.run_pipeline(cache_dir=external)
        foreign = external / "notes.txt"
        foreign.write_text("mine")
        stray = external / ".x.1234.tmp"
        stray.write_bytes(b"")
        self.run_pipeline(cache_dir=external)
        self.assertTrue(foreign.exists())
        self.assertFalse(stray.exists())


class VerifyCacheTests(_Case):
    def test_hash_on_a_healthy_cache_is_warm_and_recorded(self):
        self.run_pipeline()
        self.run_pipeline(verify_cache="hash")
        document = self.metrics()
        self.assertEqual(document["session_mode"], "warm")
        self.assertEqual((document["cache_controls"]["verify_cache"], document["cache_controls"]["verify_result"]), ("hash", "ok"))
        self.assertEquivalent()

    def test_fast_is_the_default_and_records_no_verification(self):
        self.run_pipeline()
        self.run_pipeline()
        controls = self.metrics()["cache_controls"]
        self.assertEqual(controls["verify_cache"], "fast")
        self.assertNotIn("verify_result", controls)

    def test_one_damaged_shard_is_tolerated_by_fast_and_refused_by_hash(self):
        self.run_pipeline()
        self.shard_files()[0].write_bytes(b"garbage")
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")  # fast: that shard is re-extracted
        self.assertEqual(self.metrics()["extraction_cache"]["shards_invalid"], 1)
        self.shard_files()[0].write_bytes(b"garbage")
        self.run_pipeline(verify_cache="hash")
        document = self.metrics()
        self.assertEqual((document["session_mode"], document["fallback_reason"]), ("fallback_full", VERIFY_FAILED))
        self.assertTrue(document["cache_controls"]["verify_failure"].startswith("SHARD_INVALID:"))
        self.assertEqual(document["extraction_cache"]["extraction_cache_hits"], 0)
        self.assertEqual(document["final_status"], "SUCCESS")
        self.assertEquivalent()
        self.run_pipeline(verify_cache="hash")  # the failed verification rebuilt a healthy cache
        self.assertEqual(self.metrics()["cache_controls"]["verify_result"], "ok")

    def test_hash_detects_an_unlisted_shard_and_a_missing_shard(self):
        self.run_pipeline()
        stray = self.cache / EXTRACTION_DIRNAME / "ex-999.json"
        stray.write_bytes(b"{}")
        self.run_pipeline(verify_cache="hash")
        self.assertEqual(self.metrics()["cache_controls"]["verify_failure"], "UNLISTED_SHARD_FILE")
        self.shard_files()[0].unlink()
        self.run_pipeline(verify_cache="hash")
        self.assertTrue(self.metrics()["cache_controls"]["verify_failure"].startswith("SHARD_INVALID:"))
        self.assertEquivalent()

    def test_hash_never_raises_on_a_corrupt_cache_and_does_not_mask_the_real_reason(self):
        self.run_pipeline()
        (self.cache / MANIFEST_FILENAME).write_bytes(b"corrupt")
        self.run_pipeline(verify_cache="hash")
        self.assertEqual(self.metrics()["fallback_reason"], "MANIFEST_CORRUPT")
        self.assertNotIn("verify_result", self.metrics()["cache_controls"])

    def test_verify_on_a_cold_or_refresh_run_is_a_no_op(self):
        self.run_pipeline(verify_cache="hash")
        self.assertEqual(self.metrics()["fallback_reason"], "NO_CACHE")
        self.run_pipeline(cache_mode="refresh", verify_cache="hash")
        self.assertEqual(self.metrics()["fallback_reason"], "REFRESH_REQUESTED")


class TrustMtimeTests(_Case):
    def _same_size_edit_with_restored_mtime(self) -> Path:
        target = self.repo / "Bl" / "CustomerService.vb"
        stat = target.stat()
        data = target.read_bytes()
        index = next(i for i, byte in enumerate(data) if chr(byte).isalpha())
        flipped = bytes([data[index] ^ 0x01]) if chr(data[index] ^ 0x01).isalpha() else bytes([ord("Z")])
        target.write_bytes(data[:index] + flipped + data[index + 1:])
        os.utime(target, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(target.stat().st_size, stat.st_size)
        self.assertNotEqual(target.read_bytes(), data)
        return target

    def test_default_detects_changed_bytes_even_with_restored_size_and_mtime(self):
        self.run_pipeline()
        self._same_size_edit_with_restored_mtime()
        self.run_pipeline()
        state = self.metrics()["file_state"]
        self.assertEqual(state["modified"], 1)
        controls = self.metrics()["cache_controls"]["trust_mtime"]
        self.assertEqual((controls["enabled"], controls["files_trusted"]), (False, 0))

    def test_opt_in_trusts_a_matching_size_and_mtime_exactly_as_documented(self):
        self.run_pipeline()
        self._same_size_edit_with_restored_mtime()
        self.run_pipeline(trust_mtime=True)
        document = self.metrics()
        self.assertEqual(document["file_state"]["modified"], 0)  # the documented risk: not detected
        controls = document["cache_controls"]["trust_mtime"]
        self.assertTrue(controls["enabled"])
        self.assertEqual(controls["files_trusted"], document["file_state"]["files_total"])
        self.assertEqual(controls["files_hashed"], 0)

    def test_opt_in_still_hashes_anything_whose_size_or_mtime_differ(self):
        self.run_pipeline()
        self.edit_source()  # size grows
        touched = self.repo / "Bl" / "OtherFile.txt"
        touched.write_text("one")
        self.run_pipeline()
        touched.write_text("two")
        os.utime(touched, ns=(0, touched.stat().st_mtime_ns + 5_000_000_000))  # same size, newer mtime
        self.run_pipeline(trust_mtime=True)
        document = self.metrics()
        self.assertEqual(document["file_state"]["modified"], 1)
        self.assertEqual(document["cache_controls"]["trust_mtime"]["files_hashed"], 1)

    def test_trusted_run_without_changes_is_equivalent(self):
        self.run_pipeline()
        self.run_pipeline(trust_mtime=True)
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertEquivalent()

    def test_never_used_with_a_cold_refresh_or_unusable_cache(self):
        self.run_pipeline(trust_mtime=True)  # cold
        self.assertEqual(self.metrics()["cache_controls"]["trust_mtime"]["files_trusted"], 0)
        self.run_pipeline(trust_mtime=True, cache_mode="refresh")
        self.assertEqual(self.metrics()["cache_controls"]["trust_mtime"]["files_trusted"], 0)
        (self.cache / "file_state.json").write_bytes(b"garbage")
        self.run_pipeline(trust_mtime=True)
        document = self.metrics()
        self.assertEqual(document["session_mode"], "fallback_full")
        self.assertEqual(document["cache_controls"]["trust_mtime"]["files_trusted"], 0)
        self.assertEquivalent()


class ChangedRatioTests(_Case):
    def total(self) -> int:
        return self.metrics()["file_state"]["files_total"]

    def test_disabled_by_default_even_when_everything_changed(self):
        self.run_pipeline()
        for path in self.repo.rglob("*.vb"):
            path.write_text(path.read_text(encoding="utf-8") + "\r\n' x\r\n", encoding="utf-8")
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertIsNone(self.metrics()["cache_controls"]["incremental_max_changed_ratio"])

    def test_below_equal_and_above_the_threshold(self):
        self.run_pipeline()
        total = self.total()
        self.edit_source()
        ratio = 1 / total
        self.run_pipeline(incremental_max_changed_ratio=ratio * 2)  # below
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertEqual(self.metrics()["cache_controls"]["observed_changed_ratio"], round(ratio, 6))
        self.edit_source()
        self.run_pipeline(incremental_max_changed_ratio=round(ratio, 6))  # equal: not exceeded
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.edit_source()
        self.run_pipeline(incremental_max_changed_ratio=ratio / 2)  # above
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"], document["fallback_reason"]), ("full", "fallback_full", CHANGED_RATIO_EXCEEDED))
        self.assertEqual(document["extraction_cache"]["extraction_cache_hits"], 0)
        self.assertEqual(document["scope"]["mode"], "full")  # scope reports full, it never narrows anything
        self.assertEqual(document["file_state"]["modified"], 1)  # the observed change is still reported
        self.assertEqual(document["final_status"], "SUCCESS")
        self.assertEquivalent()
        self.run_pipeline(incremental_max_changed_ratio=ratio / 2)  # nothing changed now: the rebuilt cache is warm
        self.assertEqual(self.metrics()["session_mode"], "warm")

    def test_zero_threshold_triggers_on_any_change_only(self):
        self.run_pipeline()
        self.run_pipeline(incremental_max_changed_ratio=0.0)
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.edit_source()
        self.run_pipeline(incremental_max_changed_ratio=0.0)
        self.assertEqual(self.metrics()["fallback_reason"], CHANGED_RATIO_EXCEEDED)

    def test_rename_counts_as_added_plus_deleted(self):
        self.run_pipeline()
        total = self.total()
        source = self.repo / "Bl" / "CustomerService.vb"
        source.rename(self.repo / "Bl" / "CustomerServiceRenamed.vb")
        self.run_pipeline(incremental_max_changed_ratio=1.0)
        document = self.metrics()
        self.assertEqual((document["file_state"]["added"], document["file_state"]["deleted"]), (1, 1))
        self.assertEqual(document["cache_controls"]["observed_changed_ratio"], round(2 / total, 6))

    def test_previous_count_zero_never_triggers(self):
        self.run_pipeline()
        warm = self.cache / MANIFEST_FILENAME
        original = cache_session_module.validate_cache

        def empty_previous(cache_dir, context):
            result = original(cache_dir, context)
            return CacheValidationResult(True, MODE_WARM, None, result.manifest or {}, [], []) if result.valid else result

        with patch.object(cache_session_module, "validate_cache", empty_previous):
            self.run_pipeline(incremental_max_changed_ratio=0.0)
        self.assertTrue(warm.exists())
        self.assertIsNone(self.metrics()["cache_controls"]["observed_changed_ratio"])
        self.assertEqual(self.metrics()["session_mode"], "warm")

    def test_threshold_does_not_gate_stages_or_change_the_product(self):
        self.run_pipeline()
        self.edit_source()
        self.run_pipeline(incremental_max_changed_ratio=0.0)
        executed = set(self.metrics()["stage_seconds"])
        self.assertTrue({"SCAN", "EXTRACTION", "CALL_RESOLUTION", "FLOW_RESOLUTION", "DOCUMENTATION"} <= executed)
        text = (PACKAGE / "cache" / "session.py").read_text(encoding="utf-8")
        self.assertNotIn("analyze_scope", text)


class EquivalenceAndMetricsTests(_Case):
    def test_all_variants_match_the_reference(self):
        variants = (
            dict(cache_mode="off"), dict(cache_mode="refresh"), dict(cache_mode="auto"), dict(cache_mode="auto", verify_cache="hash"),
            dict(cache_mode="auto", trust_mtime=True), dict(cache_mode="auto", incremental_max_changed_ratio=0.5),
        )
        reference = self.reference()
        for index, variant in enumerate(variants):
            for external in (False, True):
                out = self.tmp / f"v{index}{'e' if external else 'i'}"
                kwargs = dict(variant, cache_dir=self.tmp / f"cache_{index}" if external else None)
                self.run_pipeline(out=out, **kwargs)
                self.run_pipeline(out=out, **kwargs)  # second run: warm where the mode allows it
                self.assertEqual(_tree(out), reference, f"{variant} external={external}")

    def test_incremental_change_matches_a_full_run_for_every_control(self):
        self.run_pipeline()
        self.edit_source()
        for kwargs in (dict(), dict(verify_cache="hash"), dict(trust_mtime=True), dict(incremental_max_changed_ratio=1.0)):
            self.run_pipeline(**kwargs)
        reference = self.tmp / "ref_changed"
        run_full_pipeline(self.repo, reference, None, 12, cache_mode="off")
        self.assertEqual(_tree(self.out), _tree(reference))

    def test_metrics_schema_carries_the_controls_and_no_absolute_paths(self):
        self.run_pipeline(verify_cache="hash", trust_mtime=True, incremental_max_changed_ratio=0.3)
        document = self.metrics()
        controls = document["cache_controls"]
        self.assertEqual(set(controls), {
            "requested_mode", "location", "relative_dir", "verify_cache", "trust_mtime", "incremental_max_changed_ratio",
            "observed_changed_ratio",
        })
        self.assertEqual((controls["location"], controls["relative_dir"]), ("internal", CACHE_DIRNAME))
        self.assertEqual(controls["incremental_max_changed_ratio"], 0.3)
        self.assertNotIn(str(self.tmp), (self.cache / METRICS_FILENAME).read_text(encoding="utf-8"))

    def test_controls_never_enter_the_manifest_or_the_extraction_key(self):
        self.run_pipeline()
        plain = json.loads((self.cache / MANIFEST_FILENAME).read_text(encoding="utf-8"))
        self.run_pipeline(verify_cache="hash", trust_mtime=True, incremental_max_changed_ratio=0.9)
        tuned = json.loads((self.cache / MANIFEST_FILENAME).read_text(encoding="utf-8"))
        self.assertEqual(plain["config"], tuned["config"])
        self.assertEqual(plain["versions"], tuned["versions"])
        self.assertEqual(self.metrics()["session_mode"], "warm")

    def test_scope_semantics_are_unchanged(self):
        self.run_pipeline()
        self.edit_source()
        self.run_pipeline(trust_mtime=True, verify_cache="hash", incremental_max_changed_ratio=1.0)
        scope = self.metrics()["scope"]
        self.assertEqual(scope["mode"], "full")  # a changed .vb stays conservative (global resolution)
        self.assertIn("GLOBAL_RESOLUTION_EFFECTS_NOT_BOUNDED", scope["unassertable"])
        self.assertFalse((self.cache / "artifacts.json").exists())


class StructureGuardTests(unittest.TestCase):
    def test_new_modules_depend_only_on_runtime_code(self):
        for relative in ("cache/options.py", "cache/verify.py"):
            text = (PACKAGE / relative).read_text(encoding="utf-8")
            for forbidden in ("tests", "prompts", "legacy_documenter.cli", "subprocess", "anthropic", "openai"):
                self.assertNotIn(f"import {forbidden}", text, f"{relative}: {forbidden}")
                self.assertNotIn(f"from {forbidden}", text, f"{relative}: {forbidden}")

    def test_no_new_artifact_state_or_scope_modes(self):
        for path in (PACKAGE / "cache").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            if path.name != "run_metrics.py":
                self.assertNotIn("\"artifacts.json\"", text, path.name)
        self.assertEqual(CACHE_MODES, ("auto", "off", "refresh"))

    def test_library_and_cli_share_one_signature(self):
        import inspect
        parameters = inspect.signature(run_full_pipeline).parameters
        for name in ("cache_mode", "cache_dir", "extraction_cache", "verify_cache", "trust_mtime", "incremental_max_changed_ratio"):
            self.assertIn(name, parameters)
        self.assertEqual(parameters["cache_mode"].default, "auto")  # unchanged library default


if __name__ == "__main__":
    unittest.main()
