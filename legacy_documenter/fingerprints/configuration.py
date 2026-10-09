"""Config fingerprints and the CLI option classification (V5.3-R2.3).

`analysis_config_fingerprint` covers what changes extraction/resolution, `projection_config_fingerprint` what
changes `documentation_v52` output, `config_fingerprint` is R1's combined `CONFIG_FINGERPRINT`. The extraction
cache will key on the analysis part alone (projections are always regenerated). `allow_ai_interpretation`,
`--verbose`, `--long-paths`, the cache controls (`--cache-*`, `--verify-cache`, `--trust-mtime`,
`--incremental-max-changed-ratio`) and output paths never enter any of them.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ._common import sha256_json
from .templates import _default_profiles, template_profile_fingerprint

#: Every CLI option/argument (by argparse `dest`) must be classified here. A guard test enumerates the real
#: parser and fails on an unclassified or stale entry, so a new option cannot be added without deciding
#: whether it invalidates a cache.
ANALYSIS_AFFECTING = "analysis-affecting"
PROJECTION_AFFECTING = "projection-affecting"
RUNTIME_ONLY = "runtime-only"
AI_ONLY = "ai-only"
OUTPUT_LOCATION_ONLY = "output-location-only"
#: The repository argument is the *input*: its content is covered by per-file hashes and (future)
#: `repository_identity`, so its path is deliberately not part of any config fingerprint.
REPOSITORY_IDENTITY = "repository-identity"

CLI_OPTION_CLASSES = {
    "repository": REPOSITORY_IDENTITY,
    "exclude": ANALYSIS_AFFECTING,
    "flow_max_depth": ANALYSIS_AFFECTING,
    # V5.9-R2 declared logical repository identity: it only namespaces SourceArtifact ids in the evidence that every run rebuilds
    # from the indexes; extraction results, their cache and the projections do not depend on it.
    "repository_id": REPOSITORY_IDENTITY,
    "output": OUTPUT_LOCATION_ONLY,
    "output_dir": OUTPUT_LOCATION_ONLY,
    "verbose": RUNTIME_ONLY,
    "long_paths": RUNTIME_ONLY,
    "allow_ai_interpretation": AI_ONLY,
    # V5.3-R2.8 cache controls: they change how much of a valid cache is reused, never what the analysis means.
    "cache_mode": RUNTIME_ONLY,
    "cache_dir": OUTPUT_LOCATION_ONLY,
    "verify_cache": RUNTIME_ONLY,
    "trust_mtime": RUNTIME_ONLY,  # opt-in: lets unchanged (size, mtime_ns) skip hashing in File State
    "incremental_max_changed_ratio": RUNTIME_ONLY,
    # V5.7 `review` subcommand selector: explicit human review never touches extraction or its cache.
    "review_command": RUNTIME_ONLY,
}
#: `generate_documentation_v52` parameters that are not CLI options (library-level); classified likewise.
V52_PARAMETER_CLASSES = {
    "profiles": PROJECTION_AFFECTING,
    "custom_dir": PROJECTION_AFFECTING,
    "strict_templates": PROJECTION_AFFECTING,
    "interpreted": AI_ONLY,
    "partition_override": PROJECTION_AFFECTING,
    "long_paths": RUNTIME_ONLY,
    "terminology": PROJECTION_AFFECTING,
}


def analysis_config_fingerprint(excludes: Iterable[str] | None = None, flow_max_depth: int = 12) -> str:
    """Effective configuration that changes extraction/resolution: scanner exclusions and flow depth.

    `excludes` is a set (order and duplicates irrelevant; case is significant, as in the scanner).
    `DEFAULT_EXCLUDES`, `VTI_PREFIX` and `TEXT_EXTENSIONS` are read from `legacy_documenter.config` at call time.
    """
    from legacy_documenter import config

    return sha256_json("analysis_config", {
        "default_excludes": sorted(config.DEFAULT_EXCLUDES),
        "vti_prefix": config.VTI_PREFIX,
        "text_extensions": sorted(config.TEXT_EXTENSIONS),
        "excludes": sorted(set(excludes or ())),
        "flow_max_depth": int(flow_max_depth),
    })


def projection_config_fingerprint(
    profiles: Iterable[str] | None = None,
    custom_dir: str | Path | None = None,
    strict_templates: bool = False,
    defaults_dir: str | Path | None = None,
    terminology: str | None = None,
) -> str:
    """Effective configuration that changes `documentation_v52` output: active profiles, `custom_dir` content,
    `strict_templates` (a custom item that is invalid falls back vs. raises) and, through the template/profile
    fingerprint, every default/custom template, profile, catalog, noise policy and language."""
    active = list(_default_profiles() if profiles is None else profiles)
    payload = {
        "profiles": active,
        "strict_templates": bool(strict_templates),
        "template_profile_fingerprint": template_profile_fingerprint(active, custom_dir, defaults_dir),
    }
    if terminology:  # only when a vocabulary overlay is active, so the default fingerprint is unchanged
        payload["terminology"] = terminology
    return sha256_json("projection_config", payload)


def config_fingerprint(
    excludes: Iterable[str] | None = None,
    flow_max_depth: int = 12,
    profiles: Iterable[str] | None = None,
    custom_dir: str | Path | None = None,
    strict_templates: bool = False,
    defaults_dir: str | Path | None = None,
) -> str:
    """R1's `CONFIG_FINGERPRINT`: the analysis and projection parts combined."""
    return sha256_json("config", {
        "analysis": analysis_config_fingerprint(excludes, flow_max_depth),
        "projection": projection_config_fingerprint(profiles, custom_dir, strict_templates, defaults_dir),
    })
