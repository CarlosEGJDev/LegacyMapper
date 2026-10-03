from __future__ import annotations

import dataclasses
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import cache as cache_pkg
from legacy_documenter.cache import (
    CACHE_DIRNAME, EXTRACTION_DIRNAME, MANIFEST_FILENAME, SHARD_COUNT, ExtractionCache, begin_cache_session,
    parse_shard, render_shard, shard_filename, shard_index,
)
from legacy_documenter.cache import context as cache_context, extraction as extraction_module, extraction_store
from legacy_documenter.cache.manifest import validate_cache
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.fingerprints import CodeFingerprint
from legacy_documenter.utils.sanitizer import SECRET_ASSIGN_RE

ROOT = Path(__file__).resolve().parent.parent
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
NONDETERMINISTIC = {"RUN_SUMMARY.json", "RUN_SUMMARY.md", "repository.json"}


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in NONDETERMINISTIC and p.relative_to(root).parts[0] != CACHE_DIRNAME}


class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, self.repo)

    # -- library-level helpers --------------------------------------------------------------------------------
    def session(self, out: Path, **kwargs):
        scan = stages.scan_repository(self.repo, kwargs.pop("excludes", None))
        return scan, begin_cache_session(scan.root, out, scan.files, None, 12, extraction_cache=True, **kwargs)

    def extract(self, out: Path, persist: bool = True, **kwargs):
        """Extraction through the cache (like the pipeline does); returns `(outcome, session)`."""
        scan, session = self.session(out, **kwargs)
        outcome = stages.extract_repository(scan.files, scan.root, session.extraction)
        if persist:
            self.assertTrue(session.persist())
        return outcome, session

    def full(self):
        scan = stages.scan_repository(self.repo, None)
        return stages.extract_repository(scan.files, scan.root)

    def assertSameExtraction(self, a, b):
        self.assertEqual(dataclasses.asdict(a), dataclasses.asdict(b))
        self.assertEqual(json.dumps(dataclasses.asdict(a)), json.dumps(dataclasses.asdict(b)))  # key order too

    def shard_files(self, out: Path) -> list[Path]:
        return sorted((out / CACHE_DIRNAME / EXTRACTION_DIRNAME).glob("ex-*.json"))

    def manifest(self, out: Path) -> dict:
        return json.loads((out / CACHE_DIRNAME / MANIFEST_FILENAME).read_text(encoding="utf-8"))

    # -- pipeline-level helpers -------------------------------------------------------------------------------
    def run_pipeline(self, out: Path, **kwargs):
        """Runs `full`; returns `(result, ExtractionCache-or-None)` (metrics survive `release`)."""
        seen = []
        real = stages.extract_repository

        def spy(files, root, cache=None):
            seen.append(cache)
            return real(files, root, cache)

        with patch.object(stages, "extract_repository", side_effect=spy):
            result = run_full_pipeline(self.repo, out, kwargs.pop("excludes", None), 12, extraction_cache=kwargs.pop("extraction_cache", True), **kwargs)
        return result, (seen[0] if seen else None)

    def reference(self) -> dict[str, bytes]:
        out = self.tmp / "reference"
        if not out.exists():
            run_full_pipeline(self.repo, out, None, 12, cache_mode="off")
        return _tree(out)


class ShardTests(unittest.TestCase):
    def test_shard_is_deterministic_and_in_range(self):
        paths = [f"Dir{i}/File{i}.vb" for i in range(300)]
        self.assertEqual([shard_index(p) for p in paths], [shard_index(p) for p in paths])
        self.assertTrue(all(0 <= shard_index(p) < SHARD_COUNT for p in paths))

    def test_known_shard_values_never_change(self):
        # frozen: persisted caches depend on this assignment (SHA-256 prefix mod 256)
        self.assertEqual(shard_index("Bl/CustomerService.vb"), shard_index("Bl/CustomerService.vb"))
        import hashlib
        expected = int.from_bytes(hashlib.sha256(b"Bl/CustomerService.vb").digest()[:4], "big") % 256
        self.assertEqual(shard_index("Bl/CustomerService.vb"), expected)

    def test_different_paths_can_land_in_different_shards(self):
        self.assertGreater(len({shard_index(f"p{i}.vb") for i in range(64)}), 8)

    def test_canonical_json_sorted_compact_ascii_and_parseable(self):
        entries = {"z.vb": '{"key":{"a":1},"record":{"v":"ñ"}}'.replace("ñ", "\\u00f1"), "a.vb": '{"key":{},"record":{}}'}
        index = shard_index("a.vb")
        a, b = render_shard(index, entries), render_shard(index, dict(reversed(list(entries.items()))))
        self.assertEqual(a, b)
        text = a.decode("ascii")
        self.assertLess(text.index('"a.vb"'), text.index('"z.vb"'))
        self.assertNotIn(": ", text)
        self.assertTrue(text.endswith("\n"))
        with self.assertRaises(ValueError):  # z.vb is in another shard (very likely) or the index mismatches
            parse_shard(a, (index + 1) % SHARD_COUNT)

    def test_parse_rejects_malformed_shards(self):
        index = shard_index("a.vb")
        good = render_shard(index, {"a.vb": '{"key":{},"record":{}}'})
        self.assertEqual(set(parse_shard(good, index)), {"a.vb"})
        for bad in (b"", b"not json", b"[]", good.replace(b"LegacyMapperExtractionShard", b"Other"),
                    render_shard(index, {"a.vb": '{"key":1,"record":{}}'}), render_shard(index, {"a.vb": '{"record":{}}'})):
            with self.assertRaises(ValueError):
                parse_shard(bad, index)

    def test_shard_filename(self):
        self.assertEqual(shard_filename(0), "ex-000.json")
        self.assertEqual(shard_filename(255), "ex-255.json")


class StoreAndSafetyTests(_Case):
    def _cache(self) -> ExtractionCache:
        scan = stages.scan_repository(self.repo, None)
        session = begin_cache_session(scan.root, self.tmp / "out", scan.files, None, 12, extraction_cache=True)
        return session.extraction

    def test_sanitization_change_means_cache_bypass(self):
        cache = self._cache()
        cache.store("Bl/CustomerService.vb", {"value": [{"signature": "Dim c = Password=hunter2"}]})
        self.assertEqual(cache.metrics["extraction_cache_bypass"], 1)
        self.assertEqual(cache._new, {})

    def test_sanitized_error_means_bypass_but_clean_error_is_cached(self):
        cache = self._cache()
        cache.store("Bl/CustomerService.vb", {"error": {"file": "x", "extractor": "E", "error": "bad token uid=admin"}})
        self.assertEqual(cache.metrics["extraction_cache_bypass"], 1)
        cache.store("Bl/CustomerService.vb", {"error": {"file": "x", "extractor": "E", "error": "not well-formed (invalid token): line 3"}})
        self.assertEqual(cache.metrics["extraction_cache_bypass"], 1)
        self.assertEqual(sum(len(v) for v in cache._new.values()), 1)

    def test_non_deterministic_errors_are_bypassed(self):
        cache = self._cache()
        cache.store("Bl/CustomerService.vb", {"error": {"error": "[Errno 13] Permission denied"}}, cacheable=False)
        self.assertEqual(cache.metrics["extraction_cache_bypass"], 1)
        self.assertEqual(cache._new, {})

    def test_record_that_does_not_round_trip_is_bypassed(self):
        cache = self._cache()
        cache.store("Bl/CustomerService.vb", {"value": ("tuple", "not", "a", "list")})
        self.assertEqual(cache.metrics["extraction_cache_bypass"], 1)

    def test_unknown_or_unreadable_files_are_never_stored(self):
        cache = self._cache()
        cache.store("nope/unknown.vb", {"value": []})
        self.assertEqual(cache._new, {})

    def test_bypassed_file_is_reextracted_every_run(self):
        out = self.tmp / "out"
        real = extraction_module._persistable_entry_text
        target = '"file": "Bl' + chr(92) * 2 + 'CustomerService.vb"'  # as json.dumps renders the backslash

        def refuse_one(key, record):
            return None if target in json.dumps(record) else real(key, record)

        with patch.object(extraction_module, "_persistable_entry_text", side_effect=refuse_one):
            self.extract(out)
            outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_bypass"], 1)
        self.assertGreaterEqual(session.extraction.metrics["extraction_cache_misses"], 1)
        self.assertSameExtraction(outcome, self.full())

    def test_no_secret_is_persisted(self):
        (self.repo / "Bl" / "Secrets.vb").write_text(
            'Public Class Secrets\r\n    Dim cs As String = "Server=x;Password=TopSecret123;User Id=sa"\r\n'
            '    Public Sub Run()\r\n    End Sub\r\nEnd Class\r\n', encoding="utf-8")
        out = self.tmp / "out"
        self.extract(out)
        blob = b"".join(p.read_bytes() for p in self.shard_files(out)).decode("ascii")
        self.assertNotIn("TopSecret123", blob)
        for match in SECRET_ASSIGN_RE.finditer(blob):
            self.assertEqual(match.group(2), "********")
        self.assertNotIn(str(self.repo.resolve()), blob)  # relative paths only


class ReuseTests(_Case):
    def test_cold_then_warm_reuses_everything_and_equals_full(self):
        out = self.tmp / "out"
        cold, cold_session = self.extract(out)
        self.assertEqual(cold_session.mode, "cold")
        self.assertEqual(cold_session.extraction.metrics["files_reused"], 0)
        self.assertSameExtraction(cold, self.full())
        warm, session = self.extract(out)
        m = session.extraction.metrics
        self.assertEqual(session.mode, "warm")
        self.assertEqual((m["extraction_cache_misses"], m["files_extracted"], m["shards_rewritten"]), (0, 0, 0))
        self.assertEqual(m["extraction_cache_hits"], m["files_reused"])
        self.assertGreater(m["files_reused"], 0)
        self.assertSameExtraction(warm, self.full())

    def test_modified_file_is_a_miss_and_only_its_shard_is_rewritten(self):
        out = self.tmp / "out"
        self.extract(out)
        before = {p.name: p.read_bytes() for p in self.shard_files(out)}
        target = self.repo / "Bl" / "CustomerService.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\n' changed\r\nPublic Class Extra\r\nEnd Class\r\n", encoding="utf-8")
        outcome, session = self.extract(out)
        m = session.extraction.metrics
        self.assertEqual((m["extraction_cache_misses"], m["files_extracted"], m["shards_rewritten"]), (1, 1, 1))
        self.assertGreater(m["extraction_cache_hits"], 0)
        after = {p.name: p.read_bytes() for p in self.shard_files(out)}
        self.assertEqual([n for n in after if after[n] != before.get(n)], [shard_filename(shard_index("Bl/CustomerService.vb"))])
        self.assertSameExtraction(outcome, self.full())

    def test_added_file_is_a_miss(self):
        out = self.tmp / "out"
        self.extract(out)
        (self.repo / "Bl" / "Added.vb").write_text("Public Class Added\r\nEnd Class\r\n", encoding="utf-8")
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 1)
        self.assertIn("Added", {s["name"] for s in outcome.symbols})
        self.assertSameExtraction(outcome, self.full())

    def test_deleted_file_is_purged_from_its_shard(self):
        out = self.tmp / "out"
        self.extract(out)
        (self.repo / "Bl" / "CustomerService.vb").unlink()
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        blob = b"".join(p.read_bytes() for p in self.shard_files(out)).decode("ascii")
        self.assertNotIn('"Bl/CustomerService.vb"', blob)
        self.assertIn('"Bl/CustomerService.vbproj"', blob)
        self.assertSameExtraction(outcome, self.full())

    def test_rename_is_delete_plus_add_without_reuse(self):
        out = self.tmp / "out"
        self.extract(out)
        (self.repo / "Bl" / "CustomerService.vb").rename(self.repo / "Bl" / "Renamed.vb")
        outcome, session = self.extract(out)
        m = session.extraction.metrics
        self.assertEqual(m["extraction_cache_misses"], 1)  # Renamed.vb: no entry, no reuse by rename
        self.assertEqual(session.diff.renamed_candidates[0]["to"], "Bl\\Renamed.vb".replace("\\", "/"))
        self.assertSameExtraction(outcome, self.full())

    def test_entry_with_a_different_key_is_a_miss(self):
        out = self.tmp / "out"
        self.extract(out)
        manifest = self.manifest(out)
        name, expected = next(iter(manifest["extraction"]["shards"].items()))
        path = out / CACHE_DIRNAME / EXTRACTION_DIRNAME / shard_filename(int(name))
        data = parse_shard(path.read_bytes(), int(name))
        for entry in data.values():
            entry["key"]["analysis_config_fingerprint"] = "0" * 64
        content = render_shard(int(name), {p: json.dumps(e, separators=(",", ":")) for p, e in data.items()})
        path.write_bytes(content)
        import hashlib
        manifest["extraction"]["shards"][name] = hashlib.sha256(content).hexdigest()
        (out / CACHE_DIRNAME / MANIFEST_FILENAME).write_text(json.dumps(manifest), encoding="utf-8")
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], len(data))
        self.assertSameExtraction(outcome, self.full())

    def test_cached_error_is_reused(self):
        (self.repo / "Bl" / "Broken.vbproj").write_text("<Project><oops></Project>", encoding="utf-8")
        out = self.tmp / "out"
        first, _ = self.extract(out)
        self.assertTrue(any(e["file"].endswith("Broken.vbproj") for e in first.errors))
        second, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        self.assertEqual(session.extraction.metrics["extraction_cache_bypass"], 0)
        self.assertSameExtraction(second, self.full())

    def test_mutating_a_run_never_alters_the_cache(self):
        out = self.tmp / "out"
        self.extract(out)
        snapshot = {p.name: p.read_bytes() for p in self.shard_files(out)}
        outcome, session = self.extract(out, persist=False)
        for collection in (outcome.symbols, outcome.calls, outcome.web_events, outcome.webforms, outcome.projects):
            for item in collection:
                item["MUTATED"] = True
        self.assertTrue(session.persist())
        self.assertEqual({p.name: p.read_bytes() for p in self.shard_files(out)}, snapshot)
        third, _ = self.extract(out)
        self.assertSameExtraction(third, self.full())

    def test_mutation_after_reuse_in_a_rewritten_shard_is_not_persisted(self):
        out = self.tmp / "out"
        self.extract(out)
        (self.repo / "Bl" / "Added.vb").write_text("Public Class Added\r\nEnd Class\r\n", encoding="utf-8")
        outcome, session = self.extract(out, persist=False)  # reused entries sharing a dirty shard are serialized at lookup
        for item in outcome.symbols:
            item["MUTATED"] = True
        session.persist()
        final, _ = self.extract(out)
        self.assertSameExtraction(final, self.full())

    def test_global_normalization_runs_after_reuse_rootnamespace_change(self):
        out = self.tmp / "out"
        self.extract(out)
        vbproj = self.repo / "Bl" / "CustomerService.vbproj"
        vbproj.write_text(vbproj.read_text(encoding="utf-8").replace("SampleLegacy.Bl", "Changed.Root"), encoding="utf-8")
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 1)  # only the .vbproj
        self.assertTrue(any((s.get("effective_namespace") or "").startswith("Changed.Root") for s in outcome.symbols))
        self.assertSameExtraction(outcome, self.full())

    def test_partial_class_consolidation_after_reuse(self):
        (self.repo / "Bl" / "PartA.vb").write_text("Partial Public Class Split\r\n    Sub A()\r\n    End Sub\r\nEnd Class\r\n", encoding="utf-8")
        vbproj = self.repo / "Bl" / "CustomerService.vbproj"
        vbproj.write_text(vbproj.read_text(encoding="utf-8").replace('<Compile Include="CustomerService.vb" />', '<Compile Include="CustomerService.vb" /><Compile Include="PartA.vb" /><Compile Include="PartB.vb" />'), encoding="utf-8")
        out = self.tmp / "out"
        self.extract(out)
        (self.repo / "Bl" / "PartB.vb").write_text("Partial Public Class Split\r\n    Sub B()\r\n    End Sub\r\nEnd Class\r\n", encoding="utf-8")
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 1)
        self.assertTrue(outcome.logical_symbols)
        self.assertSameExtraction(outcome, self.full())

    def test_line_ending_only_change_is_reused_and_equivalent(self):
        out = self.tmp / "out"
        self.extract(out)
        target = self.repo / "Bl" / "CustomerService.vb"
        target.write_bytes(target.read_bytes().replace(b"\r\n", b"\n"))
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        self.assertSameExtraction(outcome, self.full())

    def test_one_corrupt_shard_is_a_partial_miss(self):
        out = self.tmp / "out"
        self.extract(out)
        shards = self.shard_files(out)
        self.assertGreaterEqual(len(shards), 2)
        victim = shards[0]
        victim.write_bytes(victim.read_bytes()[:-5] + b"xxxxx")
        outcome, session = self.extract(out)
        m = session.extraction.metrics
        self.assertEqual(m["shards_invalid"], 1)
        self.assertGreater(m["extraction_cache_misses"], 0)
        self.assertGreater(m["extraction_cache_hits"], 0)
        self.assertSameExtraction(outcome, self.full())
        again, session = self.extract(out)  # healed
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        self.assertSameExtraction(again, self.full())

    def test_missing_shard_file_is_a_partial_miss(self):
        out = self.tmp / "out"
        self.extract(out)
        self.shard_files(out)[0].unlink()
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["shards_invalid"], 1)
        self.assertSameExtraction(outcome, self.full())

    def test_more_than_one_corrupt_shard_disables_reuse(self):
        out = self.tmp / "out"
        self.extract(out)
        for victim in self.shard_files(out)[:2]:
            victim.write_bytes(b"{broken")
        outcome, session = self.extract(out)
        m = session.extraction.metrics
        self.assertEqual(session.extraction.reuse_disabled_reason, "MULTIPLE_SHARDS_INVALID")
        self.assertEqual((m["extraction_cache_hits"], m["files_reused"]), (0, 0))
        self.assertSameExtraction(outcome, self.full())
        healed, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["extraction_cache_misses"], 0)
        self.assertSameExtraction(healed, self.full())

    def test_invalid_extraction_section_means_full_extraction(self):
        out = self.tmp / "out"
        self.extract(out)
        manifest = self.manifest(out)
        manifest["extraction"] = {"shard_count": 7, "shards": []}
        (out / CACHE_DIRNAME / MANIFEST_FILENAME).write_text(json.dumps(manifest), encoding="utf-8")
        outcome, session = self.extract(out)
        self.assertEqual(session.extraction.metrics["files_reused"], 0)
        self.assertSameExtraction(outcome, self.full())

    def test_lookup_never_raises(self):
        out = self.tmp / "out"
        self.extract(out)
        scan, session = self.session(out)
        session.extraction._old = None  # sabotage the internals
        self.assertIsNone(session.extraction.lookup("Bl/CustomerService.vb"))
        self.assertSameExtraction(stages.extract_repository(scan.files, scan.root, session.extraction), self.full())

    def test_manifest_lists_shard_checksums(self):
        import hashlib
        out = self.tmp / "out"
        self.extract(out)
        section = self.manifest(out)["extraction"]
        self.assertEqual(section["shard_count"], 256)
        files = {p.name: p for p in self.shard_files(out)}
        self.assertEqual(sorted(f"ex-{k}.json" for k in section["shards"]), sorted(files))
        for name, digest in section["shards"].items():
            self.assertEqual(hashlib.sha256(files[f"ex-{name}.json"].read_bytes()).hexdigest(), digest)
        self.assertFalse((out / CACHE_DIRNAME / "artifacts.json").exists())
        self.assertFalse((out / CACHE_DIRNAME / "RUN_METRICS.json").exists())

    def test_shard_bytes_are_reproducible(self):
        a, b = self.tmp / "a", self.tmp / "b"
        self.extract(a)
        self.extract(b)
        self.assertEqual({p.name: p.read_bytes() for p in self.shard_files(a)}, {p.name: p.read_bytes() for p in self.shard_files(b)})


class PipelineIntegrationTests(_Case):
    def assertEquivalent(self, out: Path):
        self.assertEqual(_tree(out), self.reference())

    def test_cold_run_persists_shards_and_equals_the_cache_free_run(self):
        out = self.tmp / "out"
        result, cache = self.run_pipeline(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertGreater(len(self.shard_files(out)), 0)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEqual(cache.metrics["files_extracted"], self.manifest(out)["extraction"]["entry_count"] + cache.metrics["extraction_cache_bypass"])
        self.assertEquivalent(out)

    def test_warm_run_reuses_and_resolvers_still_run(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        with patch.object(stages, "resolve_calls", wraps=stages.resolve_calls) as calls, \
             patch.object(stages, "resolve_web_entries", wraps=stages.resolve_web_entries) as web, \
             patch.object(stages, "resolve_database", wraps=stages.resolve_database) as db, \
             patch.object(stages, "resolve_flows", wraps=stages.resolve_flows) as flows, \
             patch.object(stages, "resolve_dependencies", wraps=stages.resolve_dependencies) as deps:
            result, cache = self.run_pipeline(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(cache.metrics["extraction_cache_misses"], 0)
        self.assertGreater(cache.metrics["files_reused"], 0)
        for spy in (calls, web, db, flows, deps):
            spy.assert_called_once()
        self.assertEquivalent(out)

    def test_one_corrupt_shard_in_the_pipeline(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        victim = self.shard_files(out)[0]
        victim.write_bytes(b"garbage")
        result, cache = self.run_pipeline(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(cache.metrics["shards_invalid"], 1)
        self.assertGreater(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_more_than_one_corrupt_shard_in_the_pipeline(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        for victim in self.shard_files(out)[:2]:
            victim.write_bytes(b"garbage")
        result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)
        self.assertTrue(validate_cache(out / CACHE_DIRNAME, cache_context.build_context(self.repo.resolve(), None, 12)).valid)

    def test_invalid_manifest_means_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        (out / CACHE_DIRNAME / MANIFEST_FILENAME).write_bytes(b"corrupt")
        result, cache = self.run_pipeline(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_deleted_cache_means_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        shutil.rmtree(out / CACHE_DIRNAME)
        result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_analyzer_version_change_means_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        with patch("legacy_documenter.versions.ANALYZER_VERSION", 99):
            result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_analyzer_fingerprint_change_means_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        with patch.object(cache_context, "analyzer_code_fingerprint", return_value=CodeFingerprint("available", "f" * 64, 1)):
            result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_analysis_config_change_means_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        result, cache = self.run_pipeline(out, excludes=["nonexistent_dir"])
        self.assertEqual(cache.metrics["files_reused"], 0)
        self.assertEquivalent(out)

    def test_renderer_and_template_change_do_not_invalidate_extraction(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        with patch.object(cache_context, "template_profile_fingerprint", return_value="1" * 64), \
             patch.object(cache_context.versions, "renderer_versions", return_value={"x": {"v": "9"}}):
            result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["extraction_cache_misses"], 0)
        self.assertGreater(cache.metrics["files_reused"], 0)

    def test_git_head_and_branch_change_do_not_invalidate_extraction(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        with patch.object(cache_context, "git_metadata", return_value={"git_head": "abc", "git_branch": "other"}):
            result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["extraction_cache_misses"], 0)
        self.assertGreater(cache.metrics["files_reused"], 0)

    def test_cache_write_failure_does_not_fail_the_run(self):
        out = self.tmp / "out"
        with patch.object(extraction_store, "atomic_write_bytes", side_effect=OSError("disk full")):
            result, _ = self.run_pipeline(out)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse((out / CACHE_DIRNAME / MANIFEST_FILENAME).exists())
        self.assertEquivalent(out)

    def test_cache_mode_off_reuses_nothing(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        result, cache = self.run_pipeline(out, cache_mode="off")
        self.assertIsNone(cache)
        self.assertEquivalent(out)

    def test_extraction_cache_can_be_disabled_by_the_library_flag(self):
        out = self.tmp / "out"
        result, cache = self.run_pipeline(out, extraction_cache=False)
        self.assertIsNone(cache)
        self.assertFalse((out / CACHE_DIRNAME / EXTRACTION_DIRNAME).exists())
        self.assertIsNone(self.manifest(out).get("extraction"))
        self.assertEquivalent(out)

    def test_controlled_change_equals_full(self):
        out = self.tmp / "out"
        self.run_pipeline(out)
        target = self.repo / "Sys" / "CustomerRepository.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\nPublic Class Another\r\nEnd Class\r\n", encoding="utf-8")
        result, cache = self.run_pipeline(out)
        self.assertEqual(cache.metrics["extraction_cache_misses"], 1)
        reference = self.tmp / "reference_changed"
        run_full_pipeline(self.repo, reference, None, 12, cache_mode="off")
        self.assertEqual(_tree(out), _tree(reference))


class RuntimeIndependenceTests(unittest.TestCase):
    def test_cache_package_does_not_reach_into_extractors_resolvers_or_pipeline(self):
        for path in Path(cache_pkg.__file__).parent.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("legacy_documenter.extractors", "legacy_documenter.analysis", "legacy_documenter.cli",
                              "import anthropic", "import openai", "import subprocess"):
                self.assertNotIn(forbidden, text, f"{path.name}: {forbidden}")

    def test_extraction_module_reuses_the_central_sanitizer_and_hashing(self):
        text = Path(extraction_module.__file__).read_text(encoding="utf-8")
        self.assertIn("from legacy_documenter.utils.sanitizer import sanitize_data", text)
        self.assertNotIn("re.compile", text)
        self.assertNotIn("def semantic_content_sha256", text)

    def test_default_is_consistent_with_the_documented_decision(self):
        self.assertIsInstance(cache_pkg.EXTRACTION_CACHE_DEFAULT_ENABLED, bool)


if __name__ == "__main__":
    unittest.main()
