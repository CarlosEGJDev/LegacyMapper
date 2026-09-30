"""V5.1 R2 -- real IST regression driver (dev tooling, not part of the
runtime package -- see AGENTS.md runtime independence rule).

Reads the `index/*.json` already produced by R0's deterministic `full` run
over the real target (`C:\\PruebasLegacyMapper\\Resultados\\v5_1_new_target_rebaseline`)
-- exactly the same dict shape `legacy_documenter.main.analyze_repository`
holds in memory as `indexes` before EXPORT -- builds the Normalized Evidence
Core from it, persists it, projects it back to the legacy shape, and reports
the comparison. Never re-scans the repository (SCAN/EXTRACTION are not
re-run); this is strictly a round-trip validation of `evidence/` <-> `index/`
(V5.0 D-04).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from legacy_documenter.evidence.builder import REFERENCE_ADAPTER_ID, NormalizedEvidenceBuilder
from legacy_documenter.evidence.identity import detect_collisions
from legacy_documenter.evidence.persistence import write_evidence
from legacy_documenter.evidence.projection import LegacyIndexProjector

BASELINE_OUTPUT = Path(r"C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline")
REPO_ROOT = Path(r"C:\Users\cgalianj\source\IST_40\Operacional")
EVIDENCE_OUTPUT = Path(r"C:\PruebasLegacyMapper\Resultados\v5_1_r2_evidence_build")

INDEX_FILES = (
    "repository", "files", "solutions", "projects", "symbols", "logical_symbols",
    "calls", "entry_points", "event_bindings", "data_access", "stored_procedures",
    "sql_operations", "data_parameters", "functional_dependencies", "functional_flows",
    "functional_paths", "flow_summary", "flow_unresolved", "webforms", "configuration",
    "dependencies", "errors",
)


def load_indexes() -> dict:
    indexes = {}
    for name in INDEX_FILES:
        path = BASELINE_OUTPUT / "index" / f"{name}.json"
        with path.open(encoding="utf-8") as handle:
            indexes[name] = json.load(handle)
    return indexes


def main() -> None:
    print(f"Loading index/*.json from: {BASELINE_OUTPUT}")
    t0 = time.perf_counter()
    indexes = load_indexes()
    print(f"  loaded in {time.perf_counter() - t0:.1f}s")

    print(f"Building NormalizedEvidence (repo_root={REPO_ROOT}, computing SourceArtifact.sha256 over real files)...")
    t0 = time.perf_counter()
    builder = NormalizedEvidenceBuilder(repo_root=REPO_ROOT)
    evidence = builder.build(indexes)
    build_seconds = time.perf_counter() - t0
    print(f"  built in {build_seconds:.1f}s")

    counts = {
        "source_artifacts": len(evidence.source_artifacts),
        "solutions": len(evidence.solutions),
        "projects": len(evidence.projects),
        "components": len(evidence.components),
        "external_dependencies": len(evidence.external_dependencies),
        "data_objects": len(evidence.data_objects),
        "call_identities": len(evidence.call_identities),
        "instantiations": len(evidence.instantiations),
        "unresolved_boundaries": len(evidence.unresolved_boundaries),
    }
    print("Entity counts:", json.dumps(counts, indent=2))

    hashed = sum(1 for a in evidence.source_artifacts if a.sha256 is not None)
    print(f"SourceArtifact.sha256 computed for {hashed}/{len(evidence.source_artifacts)} files")

    print("Running identity collision detectors (I-1)...")
    collisions = {
        "PRJ": detect_collisions(evidence.projects, "id"),
        "CMP": detect_collisions([c.to_dict() for c in evidence.components], "id"),
        "XDP": detect_collisions([d.to_dict() for d in evidence.external_dependencies], "id"),
        "CAL": detect_collisions([c.to_dict() for c in evidence.call_identities], "id"),
        "UnresolvedBoundary": detect_collisions([b.to_dict() for b in evidence.unresolved_boundaries], "id"),
        "SRC": detect_collisions([a.to_dict() for a in evidence.source_artifacts], "id"),
        "SOL": detect_collisions([s.to_dict() for s in evidence.solutions], "id"),
    }
    for kind, found in collisions.items():
        print(f"  {kind}: {len(found)} collision(s)" + (f" -- {found[:5]}" if found else ""))

    print("Projecting evidence back to legacy index shape (D-04 round trip)...")
    projected = LegacyIndexProjector(REFERENCE_ADAPTER_ID).project(evidence)

    print("Comparing projected indexes against the on-disk index/*.json (I-9)...")
    mismatches = []
    for name in INDEX_FILES:
        if projected.get(name) != indexes[name]:
            mismatches.append(name)
    if mismatches:
        print(f"  MISMATCH in: {mismatches}")
    else:
        print(f"  all {len(INDEX_FILES)} indexes byte-for-byte identical after evidence round trip")

    print(f"Persisting evidence/ to: {EVIDENCE_OUTPUT}")
    t0 = time.perf_counter()
    evidence_dir = write_evidence(evidence, EVIDENCE_OUTPUT)
    print(f"  written in {time.perf_counter() - t0:.1f}s -> {evidence_dir}")

    manifest = json.loads((evidence_dir / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    total_bytes = sum((evidence_dir / f"{name}.json").stat().st_size for name in manifest["entity_counts"])
    print(f"evidence/ total size: {total_bytes} bytes ({total_bytes / (1024 * 1024):.1f} MB)")

    result = {
        "entity_counts": counts,
        "source_artifacts_hashed": hashed,
        "build_seconds": round(build_seconds, 1),
        "collisions": {k: len(v) for k, v in collisions.items()},
        "projection_mismatches": mismatches,
        "evidence_total_bytes": total_bytes,
    }
    (EVIDENCE_OUTPUT / "R2_REGRESSION_SUMMARY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Done. Summary written to R2_REGRESSION_SUMMARY.json")


if __name__ == "__main__":
    main()
