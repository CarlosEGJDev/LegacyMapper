"""Recomputes and verifies SHA-256 of the reviewed R10/R11/R12/R13 artifacts.

Each artifact's expected hash is not hardcoded here as a second, potentially
drifting copy: it is read directly out of the round's own approved result
document (`docs/V4/V4_R*_RESULT.md`), which already recorded the hash at
closure time. This module only recomputes the on-disk hash and compares it
to that recorded value. If any mismatch is found, callers must STOP and
report rather than silently continuing (per the V4-R14 prompt's
`APPROVED_ARTIFACT_INTEGRITY` requirement) — this module never overwrites,
regenerates, or "fixes" a mismatched reviewed artifact.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

# (artifact relative path, result document relative path, hash field name).
# The field name is the literal token recorded in the result document, e.g.
# `CONTRACT_SHA256=<hex>`.
_REVIEWED_ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    (
        "output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json",
        "docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md",
        "CONTRACT_SHA256",
    ),
    (
        "output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json",
        "docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md",
        "EXAMPLE_SHA256",
    ),
    (
        "output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json",
        "docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md",
        "CONTRACT_SHA256",
    ),
    (
        "output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json",
        "docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md",
        "EXAMPLE_SHA256",
    ),
    (
        "output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json",
        "docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md",
        "CONTRACT_SHA256",
    ),
    (
        "output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json",
        "docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md",
        "EXAMPLE_SHA256",
    ),
    (
        "output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json",
        "docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md",
        "REGRESSION_SECURITY_REPORT_SHA256",
    ),
    (
        "output/v4_r13/V4_SECURITY_INVARIANTS.json",
        "docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md",
        "SECURITY_INVARIANTS_SHA256",
    ),
)


class ArtifactIntegrityError(ValueError):
    """Raised when a reviewed artifact's on-disk hash does not match its
    recorded closure-document value. This must never be silently repaired."""


def _sha256_of(path: Path) -> str:
    """Returns the lowercase hex SHA-256 digest of a file's raw bytes."""
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _recorded_hash(result_doc: Path, field_name: str) -> str:
    """Extracts `FIELD_NAME=<hex>` from an approved result document's text."""
    text = result_doc.read_text(encoding="utf-8")
    match = re.search(rf"{re.escape(field_name)}=([0-9a-f]{{64}})", text)
    if not match:
        raise ArtifactIntegrityError(
            f"recorded_hash_not_found:{field_name}:{result_doc}"
        )
    return match.group(1)


def verify_reviewed_artifacts(repo_root: Path) -> list[dict]:
    """Recomputes and compares every reviewed R10-R13 artifact hash.

    Returns one dict per artifact: `path`, `recorded_sha256`, `actual_sha256`,
    `match`. Never raises for a mismatch by itself (the caller decides
    whether to STOP); `ArtifactIntegrityError` is only raised when a
    recorded hash cannot be located at all, which is itself a repository
    inconsistency worth surfacing immediately.
    """
    results: list[dict] = []
    for artifact_rel, result_doc_rel, field_name in _REVIEWED_ARTIFACTS:
        artifact_path = repo_root / artifact_rel
        result_doc_path = repo_root / result_doc_rel
        recorded = _recorded_hash(result_doc_path, field_name)
        actual = _sha256_of(artifact_path)
        results.append(
            {
                "path": artifact_rel.replace("\\", "/"),
                "recorded_sha256": recorded,
                "actual_sha256": actual,
                "match": recorded == actual,
            }
        )
    return results


def all_match(results: list[dict]) -> bool:
    """True only if every verified artifact's recorded and actual hash agree."""
    return all(item["match"] for item in results)
