"""Persists a `NormalizedEvidence` under `<output>/evidence/` (V5.0 D-03,
V5.1 R1 SS11). Uses the same crash-safe primitive (`atomic_write_text`) V4.3
already uses for every other authoritative artifact -- no new write
mechanism is introduced.

**Physical format decision (V5.1 R2.1-03), measured, not assumed:** compact
JSON (`separators=(",", ":")`, no indentation), one array per entity kind,
order of emission preserved (never resorted -- D-01). Measured on real IST
evidence (`C:\\PruebasLegacyMapper\\Resultados\\v5_1_r2_evidence_build`)
against pretty-printed JSON and against JSONL (one record per line):

* **Size:** compact and JSONL are byte-identical in total size (both just
  drop the pretty-printer's indentation whitespace) -- 12-38% smaller than
  pretty JSON depending on the partition's average record size
  (`functional_dependencies.json`: 227.2 MB pretty -> 200.5 MB compact/JSONL;
  `components.json`: 25.3 MB -> 15.7 MB).
* **Read time:** compact (one `json.loads` call over the whole array) was
  measurably *faster* than JSONL (`len(records)` separate `json.loads`
  calls) in this measurement -- JSONL's per-line Python-level call overhead
  outweighs its own size advantage when a caller ends up materializing the
  full list anyway, which every consumer in V5.1 (the legacy projector,
  every invariant check) does.
* **Determinism/inspection/traceability:** both are equally deterministic
  (`json.dump`'s list order is exactly Python list order either way) and
  equally diffable at the record level with a JSON-aware diff tool; JSONL is
  marginally more diffable with a *plain line-based* diff tool, which this
  project does not rely on anywhere today.
* **Incremental processing / V5.3 compatibility:** JSONL's real advantage
  -- true streaming reads without materializing the whole array, and
  append-only writes -- is not exercised by anything in V5.1 (no consumer
  streams a partition today), so paying its read-time cost now buys nothing
  yet. Nothing about choosing compact JSON here blocks a future move to
  JSONL when V5.3 actually needs streaming: the record *content* is
  identical either way, only the on-disk framing differs.
* **Partitioning:** unaffected by this choice -- partitioning is already
  one file per entity kind, independent of intra-file framing.

Conclusion: compact JSON wins on every measured axis for V5.1's actual
usage pattern (materialize-the-whole-partition), with strictly less
implementation complexity than JSONL (reuses the same `json.dump`/`json.load`
calls the rest of the codebase already uses, no line-splitting/joining
logic) -- "no introduzcas complejidad innecesaria". JSONL is deferred to
V5.3 if and when a real streaming consumer exists to justify it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

from .builder import NormalizedEvidence
from .entities import EVIDENCE_SCHEMA_VERSION

#: Newly-modeled entity kinds (this round's own dataclasses).
NEW_ENTITY_PARTITIONS = (
    "source_artifacts",
    "solutions",
    "projects",
    "components",
    "external_dependencies",
    "data_objects",
    "call_identities",
    "instantiations",
    "unresolved_boundaries",
)

#: Kinds V5.0/R1 preserve as-is (`NormalizedEvidence.passthrough`, see
#: `builder.PASSTHROUGH_INDEX_KEYS`). Persisting these too (not just holding
#: them in memory) is what makes `evidence/` a genuinely standalone store:
#: `index/` can be regenerated from `evidence/` alone, without keeping the
#: original run's `indexes` dict around.
PASSTHROUGH_PARTITIONS = (
    "entry_points",
    "event_bindings",
    "functional_flows",
    "functional_paths",
    "flow_unresolved",
    "data_access",
    "data_parameters",
    "calls",
    "dependencies",
    "functional_dependencies",
    "configuration",
    "errors",
    "logical_symbols",
    "flow_summary",
)

PARTITIONS = NEW_ENTITY_PARTITIONS + PASSTHROUGH_PARTITIONS

EVIDENCE_MANIFEST_FILENAME = "EVIDENCE_MANIFEST.json"


def _render(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _render_project(record: dict) -> dict:
    """`Project` is a plain dict (not a dataclass, see `builder.py`), so its
    `provenance` -- unlike every other entity's -- is still a list of live
    `EvidenceReference` objects at this point (`identity_report`/
    `validate_provenance` need those objects to call `resolve_against`
    before persistence). Serialize it here, at the one point this partition
    is actually rendered to JSON (V5.1 R3.2)."""
    return {**record, "provenance": [ref.to_dict() for ref in record["provenance"]]}


def write_evidence(evidence: NormalizedEvidence, output_dir: str | Path) -> Path:
    """Writes every partition + `EVIDENCE_MANIFEST.json` under
    `<output_dir>/evidence/`. Returns the `evidence/` directory path."""
    target = Path(output_dir) / "evidence"
    target.mkdir(parents=True, exist_ok=True)

    partition_payloads = {
        "source_artifacts": [item.to_dict() for item in evidence.source_artifacts],
        "solutions": [item.to_dict() for item in evidence.solutions],
        "projects": [_render_project(record) for record in evidence.projects],
        "components": [item.to_dict() for item in evidence.components],
        "external_dependencies": [item.to_dict() for item in evidence.external_dependencies],
        "data_objects": [item.to_dict() for item in evidence.data_objects],
        "call_identities": [item.to_dict() for item in evidence.call_identities],
        "instantiations": [item.to_dict() for item in evidence.instantiations],
        "unresolved_boundaries": [item.to_dict() for item in evidence.unresolved_boundaries],
    }
    if evidence.scan_summary is not None:
        partition_payloads["scan_summary"] = evidence.scan_summary.to_dict()
    for name in PASSTHROUGH_PARTITIONS:
        if name in evidence.passthrough:
            partition_payloads[name] = evidence.passthrough[name]

    entity_counts = {}
    partition_hashes = {}
    for name, payload in partition_payloads.items():
        rendered = _render(payload)
        atomic_write_text(target / f"{name}.json", rendered)
        entity_counts[name] = len(payload) if isinstance(payload, list) else 1
        partition_hashes[name] = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    manifest = {
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "physical_format": "json_compact",
        "entity_counts": entity_counts,
        "partition_sha256": partition_hashes,
    }
    atomic_write_text(target / EVIDENCE_MANIFEST_FILENAME, _render(manifest))
    return target
