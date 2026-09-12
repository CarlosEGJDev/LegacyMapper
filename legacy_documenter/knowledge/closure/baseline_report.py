"""Builds the deterministic V4-R14 final baseline (`V4_FINAL_BASELINE.json`).

This module documents and consolidates already-approved V4-R1..R13 behavior;
it does not implement, redesign, or approve anything. It reads:

* `PROJECT_STATE.json` for the current machine-readable state pointer;
* `output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json` for the last validated
  security/regression gate and open-defect counts;
* the R10-R13 reviewed artifacts, re-hashed and compared against their
  closure-recorded values via `artifact_hashes.py`;
* the local filesystem tree, via `maintainability.py`, for a diagnostic
  pre-refactor snapshot.

No timestamp, random value, or machine-specific absolute path is ever
written to the output dict — only repository-relative paths and content
derived from already-approved repository state.
"""
from __future__ import annotations

import json
from pathlib import Path

from legacy_documenter.knowledge.closure.artifact_hashes import (
    ArtifactIntegrityError,
    all_match,
    verify_reviewed_artifacts,
)
from legacy_documenter.knowledge.closure.maintainability import (
    build_maintainability_baseline,
)

MANUAL_PATHS: tuple[str, ...] = (
    "docs/V4/V4_USER_MANUAL.md",
    "docs/V4/V4_DEVELOPER_MANUAL.md",
    "docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md",
    "docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md",
)

PLUGIN_CONTRACT_NAME = "LegacyMapperPluginKnowledge"
PLUGIN_CONTRACT_VERSION = "1.0"


class FinalBaselineIntegrityError(ValueError):
    """Raised when the R14 final baseline cannot be built safely — in
    particular, when a reviewed R10-R13 artifact hash does not match its
    recorded closure value. The caller must STOP rather than proceed."""


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_final_baseline(repo_root: Path) -> dict:
    """Builds the V4 final baseline as a plain, JSON-serializable dict.

    Raises `FinalBaselineIntegrityError` if any reviewed R10-R13 artifact's
    on-disk hash disagrees with the hash recorded in its own closure
    document — this must never be silently reconciled.
    """
    project_state = _load_json(repo_root / "PROJECT_STATE.json")
    regression_security = _load_json(
        repo_root / "output" / "v4_r13" / "V4_REGRESSION_SECURITY_REPORT.json"
    )

    artifact_results = verify_reviewed_artifacts(repo_root)
    if not all_match(artifact_results):
        mismatches = [item for item in artifact_results if not item["match"]]
        raise FinalBaselineIntegrityError(
            f"approved_artifact_integrity_mismatch:{mismatches}"
        )

    open_by_severity = regression_security["open_defect_counts_by_severity"]

    return {
        "version": "V4",
        "latest_completed_round": "V4-R14",
        "latest_approved_round": project_state["latest_approved_round"],
        "test_count": project_state["tests"],
        "readiness": project_state["readiness"],
        "ai_knowledge_allowed": project_state["ai_knowledge_allowed"],
        "ai_knowledge_generated": project_state["ai_knowledge_generated"],
        "provider_calls": project_state["provider_calls"],
        "real_llm_calls": project_state["real_llm_calls"],
        "canonical_knowledge_model": {
            "entry_type": "CanonicalKnowledgeEntry",
            "identity_prefix": "KNO-",
            "source_policy": "ONE_CANONICAL_KNOWLEDGE_SOURCE",
            "eligibility_policy": "APPROVED_ONLY",
            "traceability_fields": ["proposal_id", "approval_decision_id"],
            "package": "legacy_documenter/knowledge/canonical",
        },
        "human_projection": {
            "round": "V4-R11",
            "package": "legacy_documenter/knowledge/projection",
            "source": "R10_CANONICAL_KNOWLEDGE",
            "output_format": "MARKDOWN",
            "is_canonical_store": False,
            "sibling_of": "R12",
        },
        "plugin_projection": {
            "round": "V4-R12",
            "package": "legacy_documenter/knowledge/plugin_projection",
            "source": "R10_CANONICAL_KNOWLEDGE",
            "output_format": "JSON",
            "is_canonical_store": False,
            "sibling_of": "R11",
            "r11_dependency": "NONE",
        },
        "plugin_contract_name": PLUGIN_CONTRACT_NAME,
        "plugin_contract_version": PLUGIN_CONTRACT_VERSION,
        "security_gate": regression_security["security_gate"]["status"]
        if isinstance(regression_security.get("security_gate"), dict)
        else regression_security.get("security_gate", "PASS"),
        "regression_gate": regression_security["regression_gate"]["status"]
        if isinstance(regression_security.get("regression_gate"), dict)
        else regression_security.get("regression_gate", "PASS"),
        "critical_open": open_by_severity["CRITICAL"],
        "high_open": open_by_severity["HIGH"],
        "medium_open": open_by_severity["MEDIUM"],
        "low_open": open_by_severity["LOW"],
        "source_code_optional": True,
        "technical_lead_final_approval_authority": True,
        "v5_implemented": False,
        "post_v4_maintainability_refactor": {
            "status": "PLANNED",
            "behavior_change": "FORBIDDEN_UNTIL_EXPLICIT_TECHNICAL_LEAD_DECISION",
            "deferred_debt": [
                "TD-001",
                "TD-002",
                "TD-003",
                "TD-004",
                "TD-005",
                "DEBT-001",
                "DEBT-002",
                "DEBT-003",
            ],
        },
        "approved_artifact_hashes": [
            {
                "path": item["path"],
                "sha256": item["actual_sha256"],
            }
            for item in artifact_results
        ],
        "manuals": list(MANUAL_PATHS),
        "maintainability_baseline": build_maintainability_baseline(repo_root),
    }


def render_final_baseline_json(baseline: dict) -> str:
    """Renders the final baseline as canonical, deterministic JSON text."""
    return json.dumps(
        baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
