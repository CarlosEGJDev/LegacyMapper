"""`CACHE_MANIFEST.json` (V5.3-R2.4): contract, rendering and validation.

The cache is valid only if the manifest exists, is `COMPLETE`, has a known schema, its `file_state.json`
checksum matches and the repository identity, analyzer version/code fingerprint, evidence schema and analysis
configuration are compatible with the current run. Anything else is a `fallback_full` (never an error).

Deliberately NOT a reason for full (they change projections, not extraction -- V5.3 R1 section 11): renderer
versions, template/profile fingerprint, projection configuration, Git HEAD and branch. They are reported in
`informational_differences`.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .context import CacheContext
from .file_state import FILE_STATE_FILENAME, FileRecord, parse_file_state

CACHE_DIRNAME = "_cache_v53"
MANIFEST_FILENAME = "CACHE_MANIFEST.json"
MANIFEST_CONTRACT = "LegacyMapperCacheManifest"
CACHE_SCHEMA_VERSION = "1"
STATE_COMPLETE = "COMPLETE"

MODE_COLD = "cold"
MODE_WARM = "warm"
MODE_FALLBACK_FULL = "fallback_full"


@dataclass(frozen=True)
class CacheValidationResult:
    """`valid` only for `mode == "warm"`; `reason` explains cold/fallback; `records` are the previous File State."""

    valid: bool
    mode: str
    reason: str | None = None
    manifest: dict | None = None
    records: list[FileRecord] = field(default_factory=list)
    informational_differences: list[str] = field(default_factory=list)


def build_manifest(context: CacheContext, file_state_sha256: str, file_count: int, extraction: dict | None = None) -> dict:
    """The manifest dict for a cache whose `file_state.json` (and extraction shards) have been written and verified."""
    manifest = {
        "contract": MANIFEST_CONTRACT,
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "state": STATE_COMPLETE,
        "versions": {
            "analyzer_version": context.analyzer_version,
            "extraction_cache_schema_version": context.extraction_cache_schema_version,
            "analyzer_code_fingerprint": context.analyzer_code_fingerprint.sha256,
            "evidence_schema_version": context.evidence_schema_version,
            "renderer_versions": context.renderer_versions,
            "template_profile_fingerprint": context.template_profile_fingerprint,
        },
        "config_fingerprint": context.config_fingerprint,
        "config": {
            **context.config,
            "analysis_config_fingerprint": context.analysis_config_fingerprint,
            "projection_config_fingerprint": context.projection_config_fingerprint,
        },
        "repository_identity": context.identity,
        "informative": {
            "git_head": context.git.get("git_head"),
            "git_branch": context.git.get("git_branch"),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "file_state": {"path": FILE_STATE_FILENAME, "sha256": file_state_sha256, "file_count": file_count},
        "validity": {"complete": True},
    }
    if extraction is not None:  # R2.5: shard count + SHA-256 per shard
        manifest["extraction"] = extraction
    return manifest


def render_manifest(manifest: dict) -> bytes:
    """Canonical manifest bytes (sorted keys, LF)."""
    return (json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _full(reason: str) -> CacheValidationResult:
    return CacheValidationResult(False, MODE_FALLBACK_FULL, reason)


def validate_cache(cache_dir: str | Path, context: CacheContext) -> CacheValidationResult:
    """Decides cold / warm / fallback_full from what is on disk; never raises for a bad cache."""
    base = Path(cache_dir)
    manifest_path, state_path = base / MANIFEST_FILENAME, base / FILE_STATE_FILENAME
    try:
        if not manifest_path.is_file():
            return _full("INCOMPLETE_CACHE") if state_path.exists() else CacheValidationResult(False, MODE_COLD, "NO_CACHE")
        manifest = _load_manifest(manifest_path)
        if manifest is None:
            return _full("MANIFEST_CORRUPT")
        if manifest.get("state") != STATE_COMPLETE or manifest.get("validity", {}).get("complete") is not True:
            return _full("STATE_NOT_COMPLETE")
        if manifest.get("cache_schema_version") != CACHE_SCHEMA_VERSION:
            return _full("UNKNOWN_CACHE_SCHEMA")
        reference = manifest["file_state"]
        if reference["path"] != FILE_STATE_FILENAME:
            return _full("MANIFEST_CORRUPT")
        if manifest["repository_identity"] != context.identity:
            return _full("REPOSITORY_MISMATCH")
        records, failure = _load_file_state(state_path, reference)
        if failure:
            return _full(failure)
        reason = _incompatibility(manifest, context)
        if reason:
            return _full(reason)
        return CacheValidationResult(True, MODE_WARM, None, manifest, records, _informational_differences(manifest, context))
    except (KeyError, TypeError, AttributeError, OSError):
        return _full("MANIFEST_CORRUPT")


def _load_manifest(path: Path) -> dict | None:
    """The manifest dict, or `None` if it is not a JSON object of this contract."""
    try:
        manifest = json.loads(path.read_bytes().decode("utf-8"))
    except (ValueError, OSError):
        return None
    return manifest if isinstance(manifest, dict) and manifest.get("contract") == MANIFEST_CONTRACT else None


def _load_file_state(path: Path, reference: dict) -> tuple[list[FileRecord], str | None]:
    """`file_state.json` records checked against the manifest's checksum and count, or `([], failure reason)`."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return [], "FILE_STATE_MISSING"
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        return [], "FILE_STATE_CHECKSUM_MISMATCH"
    try:
        records = parse_file_state(raw)
    except ValueError:
        return [], "FILE_STATE_CORRUPT"
    if len(records) != reference["file_count"]:
        return [], "FILE_STATE_CORRUPT"
    return records, None


def _incompatibility(manifest: dict, context: CacheContext) -> str | None:
    """First reason (in contract order) the cached extraction state cannot be trusted, else `None`."""
    if context.analyzer_code_fingerprint.status != "available":
        return "ANALYZER_SOURCES_UNAVAILABLE"
    versions = manifest["versions"]
    if versions["analyzer_version"] != context.analyzer_version:
        return "ANALYZER_VERSION_MISMATCH"
    if versions["analyzer_code_fingerprint"] != context.analyzer_code_fingerprint.sha256:
        return "ANALYZER_CODE_FINGERPRINT_MISMATCH"
    if versions["evidence_schema_version"] != context.evidence_schema_version:
        return "EVIDENCE_SCHEMA_MISMATCH"
    if manifest["config"]["analysis_config_fingerprint"] != context.analysis_config_fingerprint:
        return "ANALYSIS_CONFIG_MISMATCH"
    return None


def _informational_differences(manifest: dict, context: CacheContext) -> list[str]:
    """Differences that do NOT invalidate extraction (projections/metadata only)."""
    versions, informative = manifest["versions"], manifest.get("informative", {})
    checks = {
        "renderer_versions": versions.get("renderer_versions") != context.renderer_versions,
        "template_profile_fingerprint": versions.get("template_profile_fingerprint") != context.template_profile_fingerprint,
        "projection_config_fingerprint": manifest["config"].get("projection_config_fingerprint") != context.projection_config_fingerprint,
        "git_head": informative.get("git_head") != context.git.get("git_head"),
        "git_branch": informative.get("git_branch") != context.git.get("git_branch"),
    }
    return [name for name, differs in checks.items() if differs]
