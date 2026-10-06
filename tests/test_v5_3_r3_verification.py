"""R3 gaps: full-product equivalence AND recovery after every invalid-cache case."""
from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from legacy_documenter.cache.context import build_context
from legacy_documenter.cache.manifest import validate_cache
from legacy_documenter.cache.options import CacheOptionError, resolve_cache_dir
from legacy_documenter.cache.verify import VERIFY_FAILED
from legacy_documenter.cache import store
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from tools.v5_3_compare_full_incremental import compare_snapshots, snapshot_tree

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v4_2_r7_full_sample'


def run_matrix(base: Path) -> list[dict]:
    """Each mutation starts from the same healthy cache; then prove healing warm."""
    repo, out, reference = base/'repo', base/'out', base/'reference'
    shutil.copytree(FIXTURE, repo)
    assert run_full_pipeline(repo, reference, None, 12, cache_mode='off').status == RunStatus.SUCCESS
    expected = snapshot_tree(reference)
    assert run_full_pipeline(repo, out, None, 12).status == RunStatus.SUCCESS
    cache = out/'_cache_v53'
    healthy = base/'healthy'
    shutil.copytree(cache, healthy)
    cases = [
        ('manifest_missing', 'fallback_full', 'INCOMPLETE_CACHE'),
        ('manifest_json', 'fallback_full', 'MANIFEST_CORRUPT'),
        ('file_state_checksum', 'fallback_full', 'FILE_STATE_CHECKSUM_MISMATCH'),
        ('file_state_json', 'fallback_full', 'FILE_STATE_CORRUPT'),
        ('shard_fast', 'warm', None),
        ('shard_hash', 'fallback_full', VERIFY_FAILED),
        ('multiple_shards', 'warm', None),
        ('extraction_schema', 'warm', None),
        ('analyzer_version', 'fallback_full', 'ANALYZER_VERSION_MISMATCH'),
        ('analyzer_fingerprint', 'fallback_full', 'ANALYZER_CODE_FINGERPRINT_MISMATCH'),
        ('repository_identity', 'fallback_full', 'REPOSITORY_MISMATCH'),
        ('analysis_config', 'fallback_full', 'ANALYSIS_CONFIG_MISMATCH'),
        ('directory_deleted', 'cold', 'NO_CACHE'),
    ]
    results = []
    for name, mode, reason in cases:
        assert base.resolve() in cache.resolve().parents
        shutil.rmtree(cache)
        shutil.copytree(healthy, cache)
        manifest_path = cache/'CACHE_MANIFEST.json'
        manifest = json.loads(manifest_path.read_text())
        state_path = cache/'file_state.json'
        shards = sorted((cache/'extraction').glob('ex-*.json'))
        if name == 'manifest_missing':
            manifest_path.unlink()
        elif name == 'manifest_json':
            manifest_path.write_bytes(b'{')
        elif name == 'file_state_checksum':
            manifest['file_state']['sha256'] = '0'*64
        elif name == 'file_state_json':
            state_path.write_bytes(b'{')
            manifest['file_state']['sha256'] = hashlib.sha256(b'{').hexdigest()
        elif name in ('shard_fast', 'shard_hash', 'multiple_shards'):
            for shard in shards[:2 if name == 'multiple_shards' else 1]:
                shard.write_bytes(b'{')
        elif name == 'extraction_schema':
            manifest['versions']['extraction_cache_schema_version'] = 999
        elif name == 'analyzer_version':
            manifest['versions']['analyzer_version'] = 'incompatible'
        elif name == 'analyzer_fingerprint':
            manifest['versions']['analyzer_code_fingerprint'] = '0'*64
        elif name == 'repository_identity':
            manifest['repository_identity'] = {'root_fingerprint': 'other'}
        elif name == 'analysis_config':
            manifest['config']['analysis_config_fingerprint'] = '0'*64
        elif name == 'directory_deleted':
            assert base.resolve() in cache.resolve().parents
            shutil.rmtree(cache)
        if name in ('file_state_checksum', 'file_state_json', 'extraction_schema', 'analyzer_version',
                    'analyzer_fingerprint', 'repository_identity', 'analysis_config'):
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        status = run_full_pipeline(repo, out, None, 12, verify_cache='hash' if name == 'shard_hash' else 'fast').status
        metrics = json.loads((cache/'RUN_METRICS.json').read_text())
        assert status == RunStatus.SUCCESS, name
        assert (metrics['session_mode'], metrics['fallback_reason']) == (mode, reason), name
        extraction = metrics['extraction_cache']
        if name == 'shard_fast':
            assert extraction['shards_invalid'] == 1, name
            assert extraction['extraction_cache_hits'] > 0 and extraction['extraction_cache_misses'] > 0, name
        if name in ('multiple_shards', 'extraction_schema'):
            assert extraction['extraction_cache_hits'] == 0, name
            assert extraction['reuse_disabled_reason'] == ('MULTIPLE_SHARDS_INVALID' if name == 'multiple_shards' else 'EXTRACTION_CACHE_SCHEMA_MISMATCH'), name
        elif mode != 'warm':
            assert extraction['extraction_cache_hits'] == 0, name
        comparison = compare_snapshots(expected, snapshot_tree(out))
        assert comparison['equal'], name
        assert validate_cache(cache, build_context(repo, None, 12)).valid, name
        assert run_full_pipeline(repo, out, None, 12, verify_cache='hash').status == RunStatus.SUCCESS
        healed = json.loads((cache/'RUN_METRICS.json').read_text())
        assert healed['session_mode'] == 'warm' and healed['extraction_cache']['extraction_cache_hits'] > 0, name
        assert compare_snapshots(expected, snapshot_tree(out))['equal'], name
        results.append({'case':name, 'session_mode':mode, 'fallback_reason':reason,
                        'hits':extraction['extraction_cache_hits'], 'misses':extraction['extraction_cache_misses'],
                        'reuse_disabled_reason':extraction.get('reuse_disabled_reason'), 'success':True,
                        'equivalent':True, 'healed':True, 'healed_hits':healed['extraction_cache']['extraction_cache_hits']})
    return results


class RecoveryEquivalenceTests(unittest.TestCase):
    def test_matrix_recovery_equivalence_and_healing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(run_matrix(Path(tmp))), 13)

    def test_interruption_after_file_state_has_no_final_manifest_then_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo, out = base/'repo', base/'out'
            shutil.copytree(FIXTURE, repo)
            run_full_pipeline(repo, out, None, 12)
            expected = snapshot_tree(out)
            original = store.atomic_write_bytes
            def interrupt(path, content):
                if Path(path).name == 'CACHE_MANIFEST.json':
                    raise KeyboardInterrupt()
                return original(path, content)
            with patch.object(store, 'atomic_write_bytes', interrupt), self.assertRaises(KeyboardInterrupt):
                run_full_pipeline(repo, out, None, 12)
            self.assertFalse((out/'_cache_v53/CACHE_MANIFEST.json').exists())
            self.assertEqual(run_full_pipeline(repo, out, None, 12).status, RunStatus.SUCCESS)
            metrics = json.loads((out/'_cache_v53/RUN_METRICS.json').read_text())
            self.assertEqual((metrics['session_mode'], metrics['fallback_reason']), ('fallback_full','INCOMPLETE_CACHE'))
            self.assertEqual(metrics['extraction_cache']['extraction_cache_hits'], 0)
            self.assertTrue(validate_cache(out/'_cache_v53', build_context(repo,None,12)).valid)
            self.assertTrue(compare_snapshots(expected,snapshot_tree(out))['equal'])

    def test_corrupt_content_is_not_dumped_into_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo, out = base/'repo', base/'out'
            shutil.copytree(FIXTURE, repo)
            run_full_pipeline(repo, out, None, 12)
            expected = snapshot_tree(out)
            sentinel = 'R3_SYNTHETIC_SECRET_DO_NOT_EXPORT'
            (out/'_cache_v53/CACHE_MANIFEST.json').write_text('password='+sentinel, encoding='utf-8')
            disabled_level = logging.root.manager.disable
            logging.disable(logging.NOTSET)
            try:
                with self.assertLogs('legacy_documenter.cache',level='INFO') as captured:
                    self.assertEqual(run_full_pipeline(repo,out,None,12).status, RunStatus.SUCCESS)
            finally:
                logging.disable(disabled_level)
            self.assertNotIn(sentinel,'\n'.join(captured.output))
            self.assertNotIn(sentinel,(out/'_cache_v53/RUN_METRICS.json').read_text())
            self.assertTrue(compare_snapshots(expected,snapshot_tree(out))['equal'])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction integration')
    def test_real_junction_resolves_rejects_foreign_targets_and_preserves_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo, out, external = base/'repo', base/'out', base/'external'
            for p in (repo, out, external):
                p.mkdir()
            sentinel = repo/'sentinel.txt'
            sentinel.write_text('unchanged')
            for index, target in enumerate((repo, base, out, external)):
                link = base/('junction'+str(index))
                created = subprocess.run(['cmd.exe','/c','mklink','/J',str(link),str(target)], capture_output=True)
                if created.returncode:
                    self.skipTest('WINDOWS_REPARSE_REAL_TEST_NOT_AVAILABLE')
                try:
                    self.assertEqual(link.resolve(), target.resolve())
                    if target == external:
                        self.assertEqual(resolve_cache_dir(repo,out,link), external.resolve())
                    else:
                        with self.assertRaises(CacheOptionError):
                            resolve_cache_dir(repo,out,link)
                    self.assertEqual(sentinel.read_text(),'unchanged')
                    self.assertFalse((repo/'CACHE_MANIFEST.json').exists())
                finally:
                    # Remove ONLY the junction entry, never recurse through its target.
                    os.rmdir(link)


if __name__ == '__main__':
    unittest.main()
