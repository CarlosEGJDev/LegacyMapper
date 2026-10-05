"""V5.3 persisted cache infrastructure (R2.4): Cache Manifest + File State, validation, comparison, safe writing.

R2.5 adds the per-file extraction cache (`extraction`, `extraction_shards`); nothing else is reused. Modules, one responsibility each:
`identity` (repository identity, Git metadata), `file_state` (hashing/records/JSON), `diff` (file classification),
`context` (current run's comparable values), `manifest` (contract + validation), `store` (safe write order),
`session` (one run's use of all of the above), (R2.8) `options` (cache controls), `verify` (`--verify-cache=hash`), plus (R2.7) `scope` (scope analysis), `run_metrics`/`run_report` (RUN_METRICS.json).
"""
from .diff import FileStateDiff, diff_file_states
from .extraction import ExtractionCache
from .extraction_shards import EXTRACTION_DIRNAME, SHARD_COUNT, parse_shard, render_shard, shard_filename, shard_index
from .file_state import FILE_STATE_FILENAME, FileRecord, build_file_state, parse_file_state, render_file_state
from .identity import git_metadata, normalize_root, repository_identity
from .manifest import (
    CACHE_DIRNAME, CACHE_SCHEMA_VERSION, MANIFEST_FILENAME, MODE_COLD, MODE_FALLBACK_FULL, MODE_WARM,
    CacheValidationResult, validate_cache,
)
from .run_metrics import METRICS_FILENAME, METRICS_SCHEMA_VERSION, read_run_metrics, write_run_metrics
from .scope import ScopeAnalysisResult, analyze_scope
from .options import (
    CACHE_MODES, VERIFY_FAST, VERIFY_HASH, VERIFY_LEVELS, CacheOptionError, CacheOptions, ratio_argument, resolve_cache_dir,
)
from .session import (
    CHANGED_RATIO_EXCEEDED, EXTRACTION_CACHE_DEFAULT_ENABLED, CacheSession, begin_cache_session,
)
from .verify import VERIFY_FAILED, verify_cache_deep
from .store import CacheWriteError, write_cache

__all__ = [name for name in dir() if not name.startswith("_")]
