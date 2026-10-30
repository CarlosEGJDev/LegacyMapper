"""AI-only interpretation over an EXISTING deterministic baseline (post-V5 H1).

`interpret <baseline>` reuses the persisted output of an earlier `analyze`/`full` run:
analyze once, interpret many times. This module never scans, parses or resolves source code and
never rebuilds Evidence or documentation. Its only inputs are files under the baseline directory.

Order of operations (the order is the contract):

1. `validate_baseline` -- file-level checks of the persisted output. Any failure raises
   `BaselineInvalid` (state `AI_ONLY_INPUT_INVALID`); **no provider is resolved or called**.
2. output isolation -- the AI run directory is decided and checked before any provider work.
3. `ai_interpretation.run_ai_interpretation` (unchanged V4.2/V4.3/V5.5/V5.6 stage) reads
   `<baseline>/index/*.json` and `<baseline>/ai_context/SYSTEM_CONTEXT.json`.
4. `proposal_adapter.adapt_findings_to_proposals` (unchanged) and the same proposal writer `full` uses.

The AI run directory (default `<baseline>/ai_runs/<run-id>/`, or `--output`) is review-compatible
with the unchanged V5.7 flow: it holds `proposals/` and an `index/` of hard links (copy fallback)
to the baseline's index files, so `review ... --output <ai-run-dir>` works and a later change of the
baseline index is still detected as stale. The deterministic baseline is never modified; the
AI output is never canonical.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from legacy_documenter.evidence.entities import EVIDENCE_SCHEMA_VERSION
from legacy_documenter.evidence.persistence import EVIDENCE_MANIFEST_FILENAME
from legacy_documenter.fingerprints import analyzer_code_fingerprint
from legacy_documenter.llm.contracts import LLMProvider
from legacy_documenter.orchestration import ai_interpretation, proposal_adapter
from legacy_documenter.utils.atomic_write import atomic_write_text
from legacy_documenter.utils.json_rendering import render_deterministic_json
from legacy_documenter.versions import ANALYZER_VERSION

AI_ONLY_INPUT_INVALID = "AI_ONLY_INPUT_INVALID"
PROVENANCE_FILENAME = "AI_RUN_PROVENANCE.json"
PROVENANCE_CONTRACT = "LegacyMapperAiOnlyRun"
AI_RUNS_DIRNAME = "ai_runs"

#: Persisted evidence partitions a hydrated flow projection depends on.
REQUIRED_EVIDENCE_PARTITIONS = ("source_artifacts", "functional_flows", "functional_paths", "entry_points")
REQUIRED_INDEX_FILES = ("functional_flows.json", "functional_paths.json", "entry_points.json")
REQUIRED_AI_CONTEXT_FILES = ("SYSTEM_CONTEXT.json", "TRACEABILITY.json", "FUNCTIONAL_FLOWS.json")
#: Deterministic stages whose failure invalidates the baseline when a RUN_SUMMARY.json is present.
REQUIRED_STAGES = ("SCAN", "EXTRACTION", "CALL_RESOLUTION", "WEB_ENTRY_RESOLUTION", "DATABASE_RESOLUTION",
                   "FLOW_RESOLUTION", "DEPENDENCY_RESOLUTION", "EXPORT", "CONTEXT")


class BaselineInvalid(Exception):
    """The persisted deterministic output cannot be trusted for AI-only interpretation."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


@dataclass
class BaselineInfo:
    baseline_dir: Path
    evidence_manifest_sha256: str
    evidence_schema_version: str
    repository: dict
    analyzer: dict
    ai_context: dict
    summary_present: bool
    evidence_verification: str
    #: Gate B.1: identities that do not depend on the physical source root (None for baselines that predate `source_provenance`).
    portable_evidence_sha256: str | None = None
    logical_snapshot_sha256: str | None = None


@dataclass
class AiOnlyResult:
    status: str  # "SUCCESS" | AI_ONLY_INPUT_INVALID | AI_ONLY_OUTPUT_NOT_EMPTY | CONTEXT_UNAVAILABLE | CONTEXT_TOO_LARGE | PROVIDER_ERROR | INVALID_OUTPUT
    reason: str | None = None
    provider_called: bool = False
    ai_run_dir: Path | None = None
    proposal_count: int = 0
    proposal_review_status: str | None = None
    provenance: dict = field(default_factory=dict)
    seconds: dict = field(default_factory=dict)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, reason: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BaselineInvalid(reason, f"{path.name}:{exc.__class__.__name__}") from None


def _looks_like_json_list(path: Path) -> bool:
    with open(path, "rb") as handle:
        head = handle.read(64).lstrip(b"\xef\xbb\xbf \r\n\t")
    return head.startswith(b"[")


def validate_baseline(baseline: str | Path, verify_evidence: str = "hash") -> BaselineInfo:
    """Validates a persisted deterministic output. Reads files only; never touches the source repository.

    `verify_evidence="hash"` (default) re-hashes every evidence partition against
    `EVIDENCE_MANIFEST.json`; `"fast"` only checks presence and size > 0.
    """
    root = Path(baseline)
    if not root.is_dir():
        raise BaselineInvalid("BASELINE_NOT_FOUND", "not a directory")

    summary_present = False
    summary_path = root / "RUN_SUMMARY.json"
    if summary_path.is_file():
        summary_present = True
        summary = _load_json(summary_path, "RUN_SUMMARY_UNREADABLE")
        stages = {s.get("stage"): s.get("status") for s in (summary.get("stages") or []) if isinstance(s, dict)}
        bad = [name for name in REQUIRED_STAGES if stages.get(name) != "SUCCESS"]
        if bad:
            raise BaselineInvalid("DETERMINISTIC_RUN_INCOMPLETE", ",".join(bad))

    evidence_dir = root / "evidence"
    manifest_path = evidence_dir / EVIDENCE_MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise BaselineInvalid("EVIDENCE_MANIFEST_MISSING", EVIDENCE_MANIFEST_FILENAME)
    manifest = _load_json(manifest_path, "EVIDENCE_MANIFEST_INVALID")
    hashes = manifest.get("partition_sha256") if isinstance(manifest, dict) else None
    counts = manifest.get("entity_counts") if isinstance(manifest, dict) else None
    if not isinstance(hashes, dict) or not isinstance(counts, dict) or not hashes:
        raise BaselineInvalid("EVIDENCE_MANIFEST_INVALID", "partition_sha256/entity_counts")
    schema = str(manifest.get("evidence_schema_version"))
    if schema != EVIDENCE_SCHEMA_VERSION:
        raise BaselineInvalid("EVIDENCE_SCHEMA_UNSUPPORTED", f"{schema}!={EVIDENCE_SCHEMA_VERSION}")
    for name in REQUIRED_EVIDENCE_PARTITIONS:
        if name not in hashes:
            raise BaselineInvalid("EVIDENCE_PARTITION_MISSING", name)
    for name, expected in hashes.items():
        part = evidence_dir / f"{name}.json"
        if not part.is_file():
            raise BaselineInvalid("EVIDENCE_PARTITION_MISSING", name)
        if verify_evidence == "hash":
            if _sha256_file(part) != expected:
                raise BaselineInvalid("EVIDENCE_PARTITION_CORRUPT", name)
        elif part.stat().st_size <= 0:
            raise BaselineInvalid("EVIDENCE_PARTITION_CORRUPT", name)

    index_dir = root / "index"
    for name in REQUIRED_INDEX_FILES:
        path = index_dir / name
        if not path.is_file():
            raise BaselineInvalid("INDEX_MISSING", name)
        if not _looks_like_json_list(path):
            raise BaselineInvalid("INDEX_CORRUPT", name)

    context_dir = root / "ai_context"
    for name in REQUIRED_AI_CONTEXT_FILES:
        if not (context_dir / name).is_file():
            raise BaselineInvalid("AI_CONTEXT_MISSING", name)
    context = _load_json(context_dir / "SYSTEM_CONTEXT.json", "AI_CONTEXT_INVALID")
    meta = context.get("metadata") if isinstance(context, dict) else None
    if not isinstance(meta, dict):
        raise BaselineInvalid("AI_CONTEXT_INVALID", "metadata")
    snapshot = str(meta.get("source_snapshot_sha256") or "")
    if not snapshot:
        raise BaselineInvalid("SOURCE_IDENTITY_MISSING", "source_snapshot_sha256")

    # Cheap provenance cross-check: the persisted source-artifact partition agrees with its manifest count.
    artifacts = _load_json(evidence_dir / "source_artifacts.json", "EVIDENCE_PARTITION_CORRUPT")
    if not isinstance(artifacts, list) or len(artifacts) != counts.get("source_artifacts"):
        raise BaselineInvalid("PROVENANCE_UNRESOLVED", "source_artifacts_count_mismatch")

    analyzer = {"analyzer_version": None, "analyzer_code_fingerprint": None, "origin": "unknown"}
    cache_manifest = root / "_cache_v53" / "CACHE_MANIFEST.json"
    cache_identity: dict = {}
    if cache_manifest.is_file():
        cm = _load_json(cache_manifest, "CACHE_MANIFEST_INVALID")
        versions = cm.get("versions") or {}
        analyzer.update(analyzer_version=versions.get("analyzer_version"),
                        analyzer_code_fingerprint=versions.get("analyzer_code_fingerprint"), origin="cache_manifest")
        cache_identity = cm.get("repository_identity") or {}
    if analyzer["analyzer_version"] is not None and analyzer["analyzer_version"] != ANALYZER_VERSION:
        raise BaselineInvalid("ANALYZER_VERSION_UNSUPPORTED", f"{analyzer['analyzer_version']}!={ANALYZER_VERSION}")
    current = analyzer_code_fingerprint()
    analyzer["current_analyzer_version"] = ANALYZER_VERSION
    analyzer["current_code_fingerprint"] = current.sha256
    analyzer["fingerprint_matches_current"] = (
        None if analyzer["analyzer_code_fingerprint"] is None or current.sha256 is None
        else analyzer["analyzer_code_fingerprint"] == current.sha256)

    repository = {
        "source_repository": meta.get("source_repository"), "source_snapshot_sha256": snapshot,
        "logical_snapshot_sha256": (manifest.get("source_provenance") or {}).get("logical_snapshot_sha256"),
        "portable_evidence_sha256": (manifest.get("source_provenance") or {}).get("portable_evidence_sha256"),
        "source_file_count": meta.get("source_file_count"), "repository_id": manifest.get("repository_id"),
        "root_fingerprint": cache_identity.get("root_fingerprint"),
    }
    ai_context = {"model_version": meta.get("model_version"), "deterministic_model_version": meta.get("deterministic_model_version")}
    provenance = manifest.get("source_provenance") or {}
    return BaselineInfo(root, _sha256_file(manifest_path), schema, repository, analyzer, ai_context, summary_present, verify_evidence,
                        provenance.get("portable_evidence_sha256"), provenance.get("logical_snapshot_sha256"))


def _link_or_copy(src: Path, dst: Path) -> str:
    try:
        os.link(src, dst)
        return "hardlink"
    except OSError:
        shutil.copy2(src, dst)
        return "copy"


def _prepare_run_dir(baseline: Path, output: str | Path | None, run_id: str) -> Path:
    target = Path(output) if output else baseline / AI_RUNS_DIRNAME / run_id
    if target.resolve() == baseline.resolve():
        raise BaselineInvalid("AI_ONLY_OUTPUT_IS_BASELINE", "use a separate --output or the default ai_runs/<run-id>")
    if target.exists() and any(target.iterdir()):
        raise BaselineInvalid("AI_ONLY_OUTPUT_NOT_EMPTY", str(target.name))
    return target


def run_ai_only(
    baseline: str | Path, output: str | Path | None = None, provider: LLMProvider | None = None,
    flow_ids: list[str] | None = None, profile: str = ai_interpretation.DEFAULT_PROFILE, verify_evidence: str = "hash",
) -> AiOnlyResult:
    """Validates the baseline, then runs AI interpretation + proposal generation over its persisted files.

    `provider`, when supplied, is the seam tests use (Fake provider); otherwise the registry-resolved
    provider is used exactly as in `full --allow-ai-interpretation`. Never raises for an invalid
    baseline: it returns status `AI_ONLY_INPUT_INVALID` with `provider_called=False`.
    """
    from time import perf_counter
    from legacy_documenter.cli.full_pipeline import _write_proposal_output

    seconds: dict = {}
    started = perf_counter()
    try:
        info = validate_baseline(baseline, verify_evidence)
        seconds["validation"] = round(perf_counter() - started, 3)
        run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"AIR-{run_stamp}-{info.evidence_manifest_sha256[:8]}"
        run_dir = _prepare_run_dir(info.baseline_dir, output, run_id)
    except BaselineInvalid as exc:
        status = exc.reason if exc.reason.startswith("AI_ONLY_OUTPUT") else AI_ONLY_INPUT_INVALID
        if provider is not None:
            try:
                provider.close()
            except Exception:
                pass
        return AiOnlyResult(status=status, reason=exc.reason + (f":{exc.detail}" if exc.detail else ""), seconds=seconds)

    t = perf_counter()
    ai_result = ai_interpretation.run_ai_interpretation(info.baseline_dir, provider=provider, flow_ids=flow_ids, profile=profile)
    seconds["interpretation"] = round(perf_counter() - t, 3)

    proposals = []
    if ai_result.status == "SUCCESS":
        proposals = proposal_adapter.adapt_findings_to_proposals(ai_result.findings)

    run_dir.mkdir(parents=True, exist_ok=True)
    link_modes = set()
    if ai_result.status == "SUCCESS":
        (run_dir / "index").mkdir(exist_ok=True)
        for source in sorted((info.baseline_dir / "index").glob("*.json")):
            link_modes.add(_link_or_copy(source, run_dir / "index" / source.name))
        review_status = _write_proposal_output(run_dir, ai_result, proposals)
    else:
        review_status = None

    metrics = ai_result.metrics or {}
    provenance = {
        "contract": PROVENANCE_CONTRACT, "contract_version": "1.0", "run_id": run_dir.name,
        "source_baseline": str(info.baseline_dir.resolve()),
        "evidence_manifest_sha256": info.evidence_manifest_sha256, "evidence_schema_version": info.evidence_schema_version,
        "evidence_verification": info.evidence_verification, "baseline_has_run_summary": info.summary_present,
        "repository": info.repository, "analyzer": info.analyzer, "ai_context": info.ai_context,
        "provider": {"provider_id": ai_result.provider_id, "model_id": ai_result.model_id,
                     "provider_version": metrics.get("provider_version")},
        "ai_configuration": {"profile": profile, "flow_ids": flow_ids, "ai_config_fingerprint": metrics.get("ai_config_fingerprint"),
                             "context_package_id": ai_result.context_package_id},
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ai_status": ai_result.status, "provider_called": ai_result.provider_called, "error": ai_result.error_message,
        "proposal_count": len(proposals), "proposal_review_status": review_status,
        "canonical_knowledge_produced": False, "technical_lead_approval": False,
        "source_scanned": False, "deterministic_baseline_modified": False,
        "index_link_mode": sorted(link_modes) or None,
    }
    atomic_write_text(run_dir / PROVENANCE_FILENAME, render_deterministic_json(provenance))
    return AiOnlyResult(
        status=ai_result.status, reason=ai_result.error_message, provider_called=ai_result.provider_called, ai_run_dir=run_dir,
        proposal_count=len(proposals), proposal_review_status=review_status, provenance=provenance, seconds=seconds,
    )
