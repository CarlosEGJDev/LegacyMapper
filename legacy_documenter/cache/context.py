"""The values of the *current* run that a cache is compared against (V5.3-R2.4).

Everything here comes from R2.3 (`versions`, `fingerprints`) plus the repository identity; nothing is read
from docs, prompts, tests or governance files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

from legacy_documenter import versions
from legacy_documenter.fingerprints import (
    CodeFingerprint, analysis_config_fingerprint, analyzer_code_fingerprint, config_fingerprint,
    projection_config_fingerprint, template_profile_fingerprint,
)

from .identity import git_metadata, repository_identity


@dataclass(frozen=True)
class CacheContext:
    """Comparable identity of one run: repository, versions and fingerprints (plus informative metadata)."""

    identity: dict
    analyzer_version: int
    extraction_cache_schema_version: int
    analyzer_code_fingerprint: CodeFingerprint
    evidence_schema_version: str
    renderer_versions: dict
    template_profile_fingerprint: str
    analysis_config_fingerprint: str
    projection_config_fingerprint: str
    config_fingerprint: str
    config: dict = field(default_factory=dict)
    git: dict = field(default_factory=dict)


def build_context(repo_root: str | Path, excludes: list[str] | None, flow_max_depth: int, *, adapter_identity: tuple[str, str] | None = None) -> CacheContext:
    """Computes the current run's context (default `documentation_v52` profiles: the CLI exposes no others)."""
    analysis = analysis_config_fingerprint(excludes, flow_max_depth)
    # Composition roots injecting another adapter must partition compatibility.
    # The production reference descriptor is already covered by analyzer code.
    if adapter_identity is not None:
        analysis = hashlib.sha256(json.dumps([analysis, list(adapter_identity)], separators=(",", ":")).encode()).hexdigest()
    projection = projection_config_fingerprint()
    return CacheContext(
        identity=repository_identity(repo_root),
        analyzer_version=versions.ANALYZER_VERSION,
        extraction_cache_schema_version=versions.EXTRACTION_CACHE_SCHEMA_VERSION,
        analyzer_code_fingerprint=analyzer_code_fingerprint(),
        evidence_schema_version=versions.evidence_schema_version(),
        renderer_versions=versions.renderer_versions(),
        template_profile_fingerprint=template_profile_fingerprint(),
        analysis_config_fingerprint=analysis,
        projection_config_fingerprint=projection,
        config_fingerprint=config_fingerprint(excludes, flow_max_depth),
        config={"excludes": sorted(set(excludes or ())), "flow_max_depth": int(flow_max_depth)},
        git=git_metadata(repo_root),
    )
