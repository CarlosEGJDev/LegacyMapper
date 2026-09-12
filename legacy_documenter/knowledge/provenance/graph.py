"""Deterministic, acyclic provenance graph.

Canonical edge direction: EARLIER/SOURCE -> LATER/DERIVED (a parent points at
its child), for example `Material -> Evidence -> Statement`. Every traversal
method (`parents_of`, `children_of`, `ancestors_of`, `descendants_of`,
`roots_of`) and the canonical serialization use this same direction; none of
them accept or produce the reverse.

`ProvenanceGraph` builds only what LegacyMapper provenance needs: it is not a
general-purpose graph framework.
"""
import json
from dataclasses import asdict

from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.input.contracts import SourceInput
from legacy_documenter.knowledge.provenance.enums import LineageCompleteness, NodeKind
from legacy_documenter.knowledge.provenance.models import (
    ProvenanceEdge,
    ProvenanceNode,
    ProvenanceValidationError,
    new_node_id,
    normalize_edge,
    normalize_node,
)


class ProvenanceGraph:
    """An explicit, deterministic, acyclic lineage graph of nodes and edges.

    All mutation happens through `add_node`/`add_edge`, both of which
    normalize, validate, and reject structural violations (dangling
    references, self-cycles, longer cycles, conflicting duplicates)
    immediately — a graph built exclusively through this API is always
    structurally valid. `validate_graph()` exists as an explicit, independent
    re-check (for example after deserializing a graph built elsewhere).
    """

    def __init__(self) -> None:
        self._nodes: dict[str, ProvenanceNode] = {}
        self._edges: dict[str, ProvenanceEdge] = {}

    def add_node(self, node: ProvenanceNode) -> ProvenanceNode:
        """Adds `node`, or verifies an identical node already exists under the same id.

        Raises `ProvenanceValidationError` if a different node already
        occupies `node.node_id` (duplicate id with conflicting semantics is
        never silently merged).
        """
        normalized = normalize_node(node)
        existing = self._nodes.get(normalized.node_id)
        if existing is not None and existing != normalized:
            raise ProvenanceValidationError(f"duplicate_node_conflicting_semantics:{normalized.node_id}")
        self._nodes[normalized.node_id] = normalized
        return normalized

    def add_edge(self, edge: ProvenanceEdge) -> ProvenanceEdge:
        """Adds `edge` after rejecting self-cycles, dangling references, cycles, and conflicting duplicates."""
        normalized = normalize_edge(edge)
        if normalized.from_node_id == normalized.to_node_id:
            raise ProvenanceValidationError(f"self_cycle_rejected:{normalized.from_node_id}")
        if normalized.from_node_id not in self._nodes:
            raise ProvenanceValidationError(f"dangling_reference:from_node_missing:{normalized.from_node_id}")
        if normalized.to_node_id not in self._nodes:
            raise ProvenanceValidationError(f"dangling_reference:to_node_missing:{normalized.to_node_id}")

        existing = self._edges.get(normalized.edge_id)
        if existing is not None:
            if existing != normalized:
                raise ProvenanceValidationError(f"duplicate_edge_conflicting_semantics:{normalized.edge_id}")
            return normalized  # exact duplicate: idempotent no-op

        if self._path_exists(normalized.to_node_id, normalized.from_node_id):
            raise ProvenanceValidationError(
                f"cycle_detected:{normalized.from_node_id}->{normalized.to_node_id}"
            )
        self._edges[normalized.edge_id] = normalized
        return normalized

    def get_node(self, node_id: str) -> ProvenanceNode:
        """Returns the node for `node_id`, raising if it is not in the graph."""
        try:
            return self._nodes[node_id]
        except KeyError:
            raise ProvenanceValidationError(f"unknown_node:{node_id}") from None

    def parents_of(self, node_id: str) -> list[str]:
        """Returns the sorted, deterministic list of `node_id`'s direct parent node ids."""
        self.get_node(node_id)
        return sorted({e.from_node_id for e in self._edges.values() if e.to_node_id == node_id})

    def children_of(self, node_id: str) -> list[str]:
        """Returns the sorted, deterministic list of `node_id`'s direct child node ids."""
        self.get_node(node_id)
        return sorted({e.to_node_id for e in self._edges.values() if e.from_node_id == node_id})

    def ancestors_of(self, node_id: str) -> list[str]:
        """Returns the sorted, deterministic full transitive-parent closure of `node_id`."""
        return sorted(self._transitive_closure(node_id, self.parents_of))

    def descendants_of(self, node_id: str) -> list[str]:
        """Returns the sorted, deterministic full transitive-child closure of `node_id`."""
        return sorted(self._transitive_closure(node_id, self.children_of))

    def roots_of(self) -> list[str]:
        """Returns the sorted ids of every node with no incoming edge (no parents).

        A root is only "where the represented lineage begins" — it carries no
        implication of authority, approval, truth, or canonical status.
        """
        nodes_with_parents = {e.to_node_id for e in self._edges.values()}
        return sorted(node_id for node_id in self._nodes if node_id not in nodes_with_parents)

    def has_ai_ancestry(self, node_id: str) -> bool:
        """Returns whether `node_id` or any of its ancestors is `SourceType.AI_INTERPRETATION`-derived.

        AI ancestry does not invalidate knowledge; it must simply remain
        traceable through arbitrarily many derivation levels.
        """
        node = self.get_node(node_id)
        if node.source_type == SourceType.AI_INTERPRETATION:
            return True
        return any(
            self.get_node(ancestor_id).source_type == SourceType.AI_INTERPRETATION
            for ancestor_id in self.ancestors_of(node_id)
        )

    def lineage_completeness(self, node_id: str) -> LineageCompleteness:
        """Returns the caller-declared `LineageCompleteness` for `node_id`.

        This is a pure read of `ProvenanceNode.provenance_status`: the graph
        never infers `COMPLETE` from parent count, and never downgrades an
        explicit declaration on its own initiative.
        """
        return self.get_node(node_id).provenance_status

    def validate_graph(self) -> bool:
        """Re-verifies every structural invariant across the whole graph; raises on violation.

        Every edge must reference existing nodes and the edge set as a whole
        must be acyclic. Since `add_node`/`add_edge` already enforce this
        incrementally, a graph built solely through the public API always
        passes; this method is for independently re-checking a graph
        assembled by other means (for example after deserialization).
        """
        for edge in self._edges.values():
            if edge.from_node_id not in self._nodes or edge.to_node_id not in self._nodes:
                raise ProvenanceValidationError(f"dangling_reference:{edge.edge_id}")
        for node_id in self._nodes:
            if node_id in self.ancestors_of(node_id):
                raise ProvenanceValidationError(f"cycle_detected_at:{node_id}")
        return True

    def _path_exists(self, start: str, target: str) -> bool:
        """Returns whether `target` is reachable from `start` by following child edges."""
        if start == target:
            return True
        return target in self._transitive_closure(start, self.children_of)

    def _transitive_closure(self, node_id: str, neighbors) -> set[str]:
        seen: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for neighbor in neighbors(current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    frontier.append(neighbor)
        return seen

    def to_canonical_dict(self) -> dict:
        """Serializes the graph deterministically: nodes and edges sorted by id.

        Two graphs built from the same nodes/edges in different insertion
        orders always produce this same structure.
        """
        return {
            "nodes": [asdict(self._nodes[node_id]) for node_id in sorted(self._nodes)],
            "edges": [asdict(self._edges[edge_id]) for edge_id in sorted(self._edges)],
        }

    def render_canonical_json(self) -> str:
        """Renders `to_canonical_dict()` as canonical, deterministic JSON text."""
        return json.dumps(self.to_canonical_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def material_node_from_source_input(source_input: SourceInput, node_id: str | None = None) -> ProvenanceNode:
    """Represents a validated R2 `SourceInput` as a `MATERIAL` provenance node.

    Demonstrates the `SourceInput -> Material provenance node` linkage
    required for R2 compatibility without implementing R4 ingestion: no
    document parsing, filesystem scan, or network retrieval happens here.
    `node_id`, if omitted, is derived deterministically from the input's
    normalized fields via `new_node_id`, so equivalent inputs produce the
    same node id.
    """
    resolved_id = node_id or new_node_id(
        source_input.source_type.value, source_input.content, source_input.reference, source_input.title
    )
    return ProvenanceNode(
        node_id=resolved_id,
        node_kind=NodeKind.MATERIAL,
        source_type=source_input.source_type,
        reference=source_input.reference,
        origin=source_input.origin,
        metadata={"title": source_input.title} if source_input.title else {},
    )
