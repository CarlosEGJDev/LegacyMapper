"""Builds the deterministic V4-R14 final manifest (`V4_FINAL_MANIFEST.json`).

`FINAL_MANIFEST_IS_INDEX_NOT_AUTHORITY`: this is a discovery index of
repository-relative paths, grouped by category, so a fresh developer or AI
agent can find the important V4 artifacts quickly. It is never itself a
source of truth about their content — the files it points at are.

Every path listed is verified to exist on disk before being included, so a
manifest this module produces can never point at a broken reference for the
categories it enumerates.
"""
from __future__ import annotations

import json
from pathlib import Path


class ManifestPathError(ValueError):
    """Raised when a manifest entry would reference a path that does not
    exist in the current repository checkout."""


def _existing(repo_root: Path, candidates: list[str]) -> list[str]:
    """Filters `candidates` (repository-relative paths) to those that exist,
    sorted for determinism. A candidate that does not exist is an authoring
    error in this module, not a soft-fail — callers should keep this list
    accurate rather than relying on the filter to hide drift."""
    existing: list[str] = []
    missing: list[str] = []
    for candidate in candidates:
        if (repo_root / candidate).exists():
            existing.append(candidate)
        else:
            missing.append(candidate)
    if missing:
        raise ManifestPathError(f"manifest_candidate_paths_missing:{missing}")
    return sorted(existing)


def _round_result_docs(repo_root: Path) -> list[str]:
    docs_dir = repo_root / "docs" / "V4"
    return sorted(
        f"docs/V4/{p.name}"
        for p in docs_dir.glob("V4_R*_RESULT.md")
        if "_CLOSURE_AND_VERSIONING_" not in p.name
    )


def _round_closure_docs(repo_root: Path) -> list[str]:
    docs_dir = repo_root / "docs" / "V4"
    return sorted(
        f"docs/V4/{p.name}" for p in docs_dir.glob("V4_R*_CLOSURE_AND_VERSIONING_RESULT.md")
    )


def _contract_artifacts(repo_root: Path) -> list[str]:
    output_dir = repo_root / "output"
    return sorted(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in output_dir.glob("v4_r*/*CONTRACT*.json")
    )


def _example_artifacts(repo_root: Path) -> list[str]:
    output_dir = repo_root / "output"
    return sorted(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in output_dir.glob("v4_r*/*EXAMPLE*.json")
    )


def build_final_manifest(repo_root: Path) -> dict:
    """Builds the V4 final discovery manifest as a plain, JSON-serializable
    dict. Every listed path is verified to exist; category membership is
    static/curated for `authority_files`, `manuals`, `security_artifacts`,
    `baseline`, and `continuity_files`, and discovered by glob (then
    verified) for `round_results`, `round_closures`, `contracts`, and
    `examples`."""
    authority_files = _existing(
        repo_root,
        [
            "CLAUDE.md",
            "AGENTS.md",
            "PROJECT_STATE.json",
            ".gitignore",
            "docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md",
        ],
    )
    manuals = _existing(
        repo_root,
        [
            "docs/V4/V4_USER_MANUAL.md",
            "docs/V4/V4_DEVELOPER_MANUAL.md",
            "docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md",
            "docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md",
        ],
    )
    security_artifacts = _existing(
        repo_root,
        [
            "output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json",
            "output/v4_r13/V4_SECURITY_INVARIANTS.json",
        ],
    )
    baseline = _existing(
        repo_root,
        [
            "output/v4_r14/V4_FINAL_BASELINE.json",
            "output/v4_r14/V4_FINAL_MANIFEST.json",
        ],
    )
    continuity_files = _existing(
        repo_root,
        [
            "docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md",
            "docs/V4/V4_AI_HANDOVER.md",
            "docs/PROJECT_RECOVERY.md",
            "docs/GENERATED_ARTIFACT_POLICY.md",
        ],
    )

    return {
        "index_policy": "FINAL_MANIFEST_IS_INDEX_NOT_AUTHORITY",
        "authority_files": authority_files,
        "manuals": manuals,
        "round_results": _round_result_docs(repo_root),
        "round_closures": _round_closure_docs(repo_root),
        "contracts": _contract_artifacts(repo_root),
        "examples": _example_artifacts(repo_root),
        "security_artifacts": security_artifacts,
        "baseline": baseline,
        "continuity_files": continuity_files,
    }


def render_final_manifest_json(manifest: dict) -> str:
    """Renders the final manifest as canonical, deterministic JSON text."""
    return json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
