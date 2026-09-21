"""Stable, partitioned `LegacyMapperConsumerProjection 1.0` package construction (V4.3-R6).

Implements the `consumer_projection` surface fixed by V4.3-R1 section 5.3
(`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`): a JSON-stable,
self-contained projection of hydrated FLOW records for a future consumer (e.g.
a future Plugin Runtime) that must never need to open
`ai_context/FUNCTIONAL_FLOWS.json` to understand a flow. This module does not
implement Plugin Runtime (`PLUGIN_RUNTIME_NOT_IMPLEMENTED`, unchanged).

**Post-implementation correction (still V4.3-R6, before R7 started).** The
first version of this module returned one single, unbounded package whose
`records` held every hydrated flow. R1 section 5.3 requires the surface to
stay "razonablemente pequeño" ("reasonably small"); a real repository with
thousands of flows and tens/hundreds of thousands of paths would have made
that single JSON file a monolith. This is not fixed by truncating or
omitting evidence -- `SILENT_ENTRY_OMISSION` stays forbidden -- it is fixed by
**deterministic, complete partitioning**: `build` now returns one small
*manifest* plus a deterministic list of *partitions*, each independently
self-contained. See `docs/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION_RESULT.md`
section on the corrected architecture for the full rationale.

Four properties this module enforces, all fixed by R1 section 5.3 and this
correction:

1. **Independent of `human_documentation` and of `ai_projection`.** This
   module never imports `legacy_documenter.documentation` or
   `legacy_documenter.context.ai_projection`, and never imports
   `legacy_documenter.llm` -- unlike `ai_projection`, this surface is never
   sent to a provider, so it carries no budget/payload-gate concept at all.
2. **`SILENT_ENTRY_OMISSION` is forbidden**, the same completeness policy
   `legacy_documenter.knowledge.plugin_projection.service.PluginProjectionService`
   already enforces for R12's canonical-knowledge projection: every flow id
   requested must appear in exactly one partition's `records`, or the whole
   build fails loudly (`ConsumerProjectionError`) -- never a silent drop, and
   never a duplicate. Partitioning bounds *file size*, never *content*: the
   union of every partition's flow ids always equals the requested set, and
   no two partitions share a flow id.
3. **Every partition is self-contained.** A partition never needs another
   partition, or the manifest, to interpret its own `records` -- it carries
   its own `contract_name`/`contract_version`/`source_snapshot`/`provenance`
   and full hydrated records, exactly as the single-file version did. The
   manifest exists for *discovery* (which partitions exist, and where), never
   as a dependency a partition reader must resolve first.
4. **Plain JSON primitives only, no internal classes.** Both the manifest and
   every partition are exactly dict/list/str/int/bool/None -- `records` are
   exactly what `EvidenceHydrator.hydrate_flow` returns, never a
   `FunctionalFlow`/`FunctionalPath` domain object -- so a consumer needs no
   LegacyMapper class to read either.
"""
from __future__ import annotations

import hashlib
import json

from .hydration import CONFIDENCE_ORDER, MODEL_VERSION as HYDRATION_MODEL_VERSION, EvidenceHydrator

CONTRACT_NAME = "LegacyMapperConsumerProjection"
CONTRACT_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
MANIFEST_PACKAGE_TYPE = "CONSUMER_PROJECTION_MANIFEST"
PARTITION_PACKAGE_TYPE = "CONSUMER_PROJECTION_PARTITION"

#: R1 section 4: same canonical SHA-256-over-serialized-body method as
#: `CTX-`/`AIP-`, with this surface's own prefix.
PACKAGE_ID_PREFIX = "CPJ-"

#: A partition's own id uses a distinct, greppable prefix so a partition file
#: is never confused with the manifest's `package_id` at a glance, while
#: still being the same canonical SHA-256-over-serialized-body method.
PARTITION_ID_PREFIX = "CPJ-PART-"

#: Deterministic, size-controlled partitioning: flows are grouped by ordinal
#: position after sorting (never by project/webform/any narrative label --
#: "no por nombres narrativos o heurísticas humanas"), `DEFAULT_PARTITION_SIZE`
#: flows per partition. This is a real, complete partitioning of content, not
#: a budget: every flow lands in exactly one partition regardless of how many
#: partitions that requires.
DEFAULT_PARTITION_SIZE = 500

#: `consumer_projection/parts/part-000001.json`, `.../part-000002.json`, ... --
#: zero-padded and ascending, so filenames sort in the same order the
#: partitions themselves are listed in the manifest, on any filesystem or
#: `ls`, without parsing JSON first. Chosen fresh for this surface (not
#: `legacy_documenter.exporters._documentation_partitioning.build_partition_filenames`,
#: which derives a filename from a narrative group label such as a project or
#: webform name -- the opposite of what this surface's count-controlled,
#: machine-friendly partitioning needs).
PARTITION_DIRECTORY = "parts"
PARTITION_FILENAME_TEMPLATE = "part-{index:06d}.json"


class ConsumerProjectionError(ValueError):
    """Raised when a `consumer_projection` build would silently omit or duplicate a requested flow.

    Always an explicit, fail-loud failure -- `SILENT_ENTRY_OMISSION` is
    forbidden by contract (R1 section 5.3), so a flow id that cannot be
    hydrated, or that would land in more than one partition, never simply
    disappears or duplicates.
    """


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def partition_filename(index: int) -> str:
    """The deterministic filename for partition `index` (0-based)."""
    return PARTITION_FILENAME_TEMPLATE.format(index=index)


def partition_relative_path(index: int) -> str:
    """The deterministic path, relative to `consumer_projection/`, for partition `index`."""
    return f"{PARTITION_DIRECTORY}/{partition_filename(index)}"


class ConsumerProjectionBuilder:
    """Builds one `LegacyMapperConsumerProjection 1.0` manifest plus its deterministic partitions."""

    CONTRACT_NAME = CONTRACT_NAME
    CONTRACT_VERSION = CONTRACT_VERSION

    def __init__(self, hydrator: object = None, partition_size: int = DEFAULT_PARTITION_SIZE) -> None:
        if not isinstance(partition_size, int) or partition_size <= 0:
            raise ValueError("partition_size must be a positive integer")
        self.hydrator = hydrator or EvidenceHydrator()
        self.partition_size = partition_size

    def build(
        self, ix: dict, flow_ids: list[str] | None = None, source_snapshot: str | None = None,
    ) -> tuple[dict, dict[str, dict]]:
        """Hydrates and partitions `flow_ids` (default: every flow in `ix`).

        `flow_ids=None` means "every flow" here -- the opposite default from
        `ai_projection.AiProjectionBuilder.build`, which rejects `None`
        outright, because this surface has no LLM payload to bound and R1
        section 5.3 requires completeness (`SILENT_ENTRY_OMISSION=FORBIDDEN`),
        not a mandatory ceiling.

        Returns `(manifest, partitions)`: `manifest` is the small package
        meant to be `CONSUMER_PROJECTION.json`; `partitions` maps each
        partition's path (relative to `consumer_projection/`, e.g.
        `"parts/part-000001.json"`) to that partition's own complete,
        self-contained package body. Both are plain dicts -- serialization,
        sanitization and writing to disk are the caller's responsibility
        (see `legacy_documenter.cli.pipeline_stages._write_consumer_projection`),
        exactly as the pre-partitioning version left those steps to the
        caller.
        """
        requested = sorted(set(flow_ids)) if flow_ids is not None else sorted(
            {flow["id"] for flow in ix.get("functional_flows", []) if flow.get("id")}
        )
        records = [self.hydrator.hydrate_flow(flow_id, ix) for flow_id in requested]
        if len(records) != len(requested):
            # Unreachable under the loop above (hydrate_flow always returns one
            # record per requested id or raises), kept as an explicit, fail-loud
            # completeness guard mirroring PluginProjectionService's own.
            raise ConsumerProjectionError("silent_entry_omission_detected")
        return self.package(records, source_snapshot=source_snapshot)

    def package(self, records: list[dict], source_snapshot: str | None = None) -> tuple[dict, dict[str, dict]]:
        """Partitions already-hydrated records into complete, self-contained chunks plus one manifest."""
        ordered = sorted(records, key=lambda r: str(r.get("flow_id")))
        _reject_duplicate_flow_ids(ordered)

        chunks = [ordered[i:i + self.partition_size] for i in range(0, len(ordered), self.partition_size)]
        partitions: dict[str, dict] = {}
        partition_entries: list[dict] = []
        for index, chunk in enumerate(chunks):
            path = partition_relative_path(index)
            body = self._partition_body(index, source_snapshot, chunk)
            body["partition_id"] = PARTITION_ID_PREFIX + hashlib.sha256(_canonical(body).encode()).hexdigest()
            partitions[path] = body
            partition_entries.append({
                "index": index,
                "relative_path": path,
                "partition_id": body["partition_id"],
                "flow_count": len(chunk),
                "first_flow_id": chunk[0]["flow_id"],
                "last_flow_id": chunk[-1]["flow_id"],
            })
        _verify_partitioning_is_lossless(ordered, partitions)

        manifest = self._manifest_body(source_snapshot, ordered, partition_entries)
        manifest["package_id"] = PACKAGE_ID_PREFIX + hashlib.sha256(_canonical(manifest).encode()).hexdigest()
        return manifest, partitions

    def _manifest_body(self, source_snapshot: str | None, records: list[dict], partition_entries: list[dict]) -> dict:
        return {
            "package_type": MANIFEST_PACKAGE_TYPE,
            "contract_name": CONTRACT_NAME,
            "contract_version": CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "source_snapshot": source_snapshot,
            "selection_policy": {
                "surface": "consumer_projection",
                "completeness_policy": "SILENT_ENTRY_OMISSION_FORBIDDEN",
                "ordering": "flow_id_ascending",
            },
            "partitioning": {
                "strategy": "FIXED_SIZE_BY_FLOW_COUNT",
                "partition_size": self.partition_size,
                "partition_count": len(partition_entries),
                "directory": f"consumer_projection/{PARTITION_DIRECTORY}/",
                "filename_pattern": PARTITION_FILENAME_TEMPLATE,
            },
            "partitions": partition_entries,
            "statistics": {
                "flow_count": len(records),
                "path_count": sum(len(r.get("paths", [])) for r in records),
                "confirmed_flow_count": sum(r.get("confidence") == "confirmed" for r in records),
                "inferred_flow_count": sum(r.get("confidence") == "inferred" for r in records),
                "unresolved_flow_count": sum(r.get("confidence") == "unresolved" for r in records),
                "partition_count": len(partition_entries),
                "completeness": "COMPLETE",
            },
            "provenance": _provenance(),
        }

    def _partition_body(self, index: int, source_snapshot: str | None, records: list[dict]) -> dict:
        return {
            "package_type": PARTITION_PACKAGE_TYPE,
            "contract_name": CONTRACT_NAME,
            "contract_version": CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "source_snapshot": source_snapshot,
            "partition_index": index,
            "scope": {"flow_ids": [r.get("flow_id") for r in records]},
            "records": records,
            "statistics": {
                "flow_count": len(records),
                "path_count": sum(len(r.get("paths", [])) for r in records),
                "confirmed_flow_count": sum(r.get("confidence") == "confirmed" for r in records),
                "inferred_flow_count": sum(r.get("confidence") == "inferred" for r in records),
                "unresolved_flow_count": sum(r.get("confidence") == "unresolved" for r in records),
                "completeness": "COMPLETE",
            },
            "provenance": _provenance(),
        }


def _provenance() -> dict:
    return {
        "hydration_model_version": HYDRATION_MODEL_VERSION,
        "source_indexes": [
            "index/functional_flows.json", "index/functional_paths.json", "index/entry_points.json",
            "index/data_access.json", "index/stored_procedures.json", "index/sql_operations.json",
            "index/data_parameters.json",
        ],
    }


def _reject_duplicate_flow_ids(records: list[dict]) -> None:
    seen: set = set()
    for record in records:
        flow_id = record.get("flow_id")
        if flow_id in seen:
            raise ConsumerProjectionError(f"duplicate_flow_id:{flow_id}")
        seen.add(flow_id)


def _verify_partitioning_is_lossless(records: list[dict], partitions: dict[str, dict]) -> None:
    """Fail-loud guard: the union of every partition's flow ids must equal the
    requested set exactly once each -- never fewer (omission), never more
    (duplication). Unreachable given the code above (which builds partitions
    as a strict, non-overlapping slice of `records`), kept explicit for the
    same reason `PluginProjectionService.project` keeps its own equivalent
    guard: completeness here is a contract invariant, not merely an emergent
    property of the current implementation.
    """
    expected = [r.get("flow_id") for r in records]
    seen: list = []
    for body in partitions.values():
        seen.extend(r.get("flow_id") for r in body["records"])
    if sorted(seen) != sorted(expected) or len(seen) != len(set(seen)):
        raise ConsumerProjectionError("silent_entry_omission_or_duplication_detected")


def build_consumer_projection(
    ix: dict, flow_ids: list[str] | None = None, source_snapshot: str | None = None,
    partition_size: int = DEFAULT_PARTITION_SIZE,
) -> tuple[dict, dict[str, dict]]:
    """Module-level convenience wrapper over `ConsumerProjectionBuilder.build`."""
    return ConsumerProjectionBuilder(partition_size=partition_size).build(ix, flow_ids=flow_ids, source_snapshot=source_snapshot)
