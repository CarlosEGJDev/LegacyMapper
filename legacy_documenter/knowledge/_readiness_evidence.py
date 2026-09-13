"""Canonical evidence-catalog construction and evidence-closure traceability checks (DEBT-002, V4.1-R4)."""
import json
from pathlib import Path

from legacy_documenter.knowledge._readiness_io import _read


def _canonical_catalog(root: Path) -> tuple[set[str], set[str], set[str], set[str]]:
    """Builds closed evidence, assessment, package and snapshot identifier sets."""
    assessments = []
    for name in ("LOCAL_ASSESSMENTS.json", "INTERMEDIATE_ASSESSMENTS.json"):
        assessments.extend(json.loads(_read(root / "output/v3_r7_2" / name))["assessments"])
    evidence, assessment_ids, packages, snapshots = set(), set(), set(), set()
    for entry in assessments:
        payload = entry.get("assessment_payload", entry)
        assessment_ids.add(payload.get("assessment_id") or entry.get("assessment_id"))
        packages.update(payload.get("context_package_ids", []))
        snapshots.update(payload.get("source_snapshots", []))
        for claim in payload.get("claims", []):
            evidence.update(claim.get("evidence_refs", []))
            packages.update(claim.get("context_package_ids", []))
        for missing in payload.get("missing_information", []):
            evidence.update(missing.get("related_evidence_ids", []))
    return evidence, assessment_ids, packages, snapshots


def evidence_closed(documents: dict[str, dict[str, object]], details: dict[str, dict[str, dict[str, object]]],
                    snapshots: dict[str, str | None], catalog: tuple[set[str], set[str], set[str], set[str]]) -> bool:
    """Validates the complete document-to-canonical-evidence traceability chain."""
    evidence, assessments, packages, known_snapshots = catalog
    claim_refs = {ref for document in documents.values() for claim in document["claims"] for ref in claim["evidence_refs"]}
    traced = [item for values in details.values() for item in values.values()]
    request_evidence = {ref for item in traced for ref in item["evidence_ids"]}
    request_packages = {ref for item in traced for ref in item["context_package_ids"]}
    request_snapshots = {ref for item in traced for ref in item["source_snapshot_ids"]}
    assessment_refs = {ref.split(":", 1)[0] for item in traced for ref in item["assessment_claim_refs"] + item["assessment_request_refs"]}
    return (claim_refs <= evidence and request_evidence <= evidence and request_packages <= packages
            and assessment_refs <= assessments and request_snapshots <= known_snapshots
            and set(snapshots.values()) <= known_snapshots
            and all(item["evidence_ids"] and item["source_snapshot_ids"] and item["context_package_ids"]
                    and (item["assessment_claim_refs"] or item["assessment_request_refs"]) for item in traced))


def evidence_closure_diagnostics(documents: dict[str, dict[str, object]], details: dict[str, dict[str, dict[str, object]]],
                                 snapshots: dict[str, str | None], catalog: tuple[set[str], set[str], set[str], set[str]]) -> dict[str, list[str]]:
    """Lists unresolved identifiers by namespace for safe diagnostic output."""
    evidence, assessments, packages, known_snapshots = catalog
    traced = [item for values in details.values() for item in values.values()]
    actual = {
        "evidence": {ref for document in documents.values() for claim in document["claims"] for ref in claim["evidence_refs"]} | {ref for item in traced for ref in item["evidence_ids"]},
        "assessments": {ref.split(":", 1)[0] for item in traced for ref in item["assessment_claim_refs"] + item["assessment_request_refs"]},
        "packages": {ref for item in traced for ref in item["context_package_ids"]},
        "snapshots": set(snapshots.values()) | {ref for item in traced for ref in item["source_snapshot_ids"]},
    }
    known = {"evidence": evidence, "assessments": assessments, "packages": packages, "snapshots": known_snapshots}
    return {key: sorted(actual[key] - known[key]) for key in actual}
