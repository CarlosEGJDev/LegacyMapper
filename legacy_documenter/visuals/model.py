"""Structured visual model (post-V5 H3): the contract between persisted knowledge and the deterministic renderer.

A `VisualProjection` is plain data: nodes, edges, groups, legend, provenance and an explicit statement of what (if
anything) was aggregated or omitted. Nothing here draws. The renderer (`svg.py`) only reads this model, so an AI
contribution could only ever enrich the *model*, which `validate_projection` checks before anything is rendered:

* every node/edge carries an epistemic status (CONFIRMED / INFERRED / UNRESOLVED / AI_INTERPRETATION / CANONICAL);
* a CONFIRMED or CANONICAL edge must be traceable (`source_refs` non-empty); INFERRED edges must state their rule;
* statuses propagate: an edge cannot be stronger than its weakest endpoint (nothing touching an AI interpretation is
  confirmed; nothing touching an unresolved node is confirmed);
* ids are stable hashes of canonical keys, so the same input yields the same model and the same SVG byte for byte.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

CONTRACT = "LegacyMapperVisualProjection"
CONTRACT_VERSION = "1.0"

CONFIRMED, INFERRED, UNRESOLVED = "CONFIRMED", "INFERRED", "UNRESOLVED"
AI_INTERPRETATION, CANONICAL = "AI_INTERPRETATION", "CANONICAL"
STATUSES = (CONFIRMED, INFERRED, UNRESOLVED, AI_INTERPRETATION, CANONICAL)

KINDS = ("system-map", "project-layer-map", "dependency-map", "observable-flow", "data-interaction-map")
AUDIENCES = ("executive", "functional", "technical_overview")

#: Statuses an edge may NOT exceed when an endpoint has the key status (allowed edge statuses per endpoint status).
_ALLOWED_EDGE_STATUS = {
    CONFIRMED: set(STATUSES), CANONICAL: set(STATUSES),
    INFERRED: {INFERRED, UNRESOLVED, AI_INTERPRETATION},
    UNRESOLVED: {UNRESOLVED},
    AI_INTERPRETATION: {AI_INTERPRETATION},
}

LEGEND = (
    (CONFIRMED, "Confirmado", "borde continuo"),
    (INFERRED, "Inferido (regla)", "borde discontinuo"),
    (UNRESOLVED, "No resuelto", "borde punteado y marca !"),
    (AI_INTERPRETATION, "Interpretación de IA (no aprobada)", "doble borde y marca IA"),
    (CANONICAL, "Canónico (aprobado por una persona)", "borde grueso y marca OK"),
)


def stable_id(prefix: str, *parts: object) -> str:
    """`<prefix>-<12 hex>` over the canonical key. Deterministic across runs and machines."""
    digest = hashlib.sha256("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:12]}"


@dataclass
class Node:
    id: str
    label: str
    type: str
    status: str
    source_refs: list[str] = field(default_factory=list)
    group: str | None = None
    column: int | None = None  # optional layer hint for the layout (otherwise derived from edges)
    sublabel: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {"id": self.id, "label": self.label, "type": self.type, "status": self.status,
                "source_refs": sorted(set(self.source_refs)), "metadata": self.metadata}
        if self.group:
            data["group"] = self.group
        if self.sublabel:
            data["sublabel"] = self.sublabel
        if self.column is not None:
            data["column"] = self.column
        return data


@dataclass
class Edge:
    source: str
    target: str
    relation: str
    status: str
    source_refs: list[str] = field(default_factory=list)
    label: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return stable_id("E", self.source, self.target, self.relation)

    def to_dict(self) -> dict:
        data = {"id": self.id, "source": self.source, "target": self.target, "relation": self.relation, "status": self.status,
                "source_refs": sorted(set(self.source_refs)), "metadata": self.metadata}
        if self.label:
            data["label"] = self.label
        return data


@dataclass
class Group:
    id: str
    label: str
    status: str = CONFIRMED
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "status": self.status, "metadata": self.metadata}


@dataclass
class VisualProjection:
    kind: str
    title: str
    audience: str
    scope: dict
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    provenance: list[dict] = field(default_factory=list)
    unresolved: list[dict] = field(default_factory=list)
    partial: dict = field(default_factory=lambda: {"partial": False, "included_count": 0, "omitted_count": 0, "reason": ""})
    metadata: dict = field(default_factory=dict)
    #: H3-R2: only present when the diagram is a deterministic SUMMARY of, or a DETAIL part of, a decomposed view. `partial` keeps
    #: its H3 meaning (this one view omits/aggregates concrete nodes); `decomposition` says the full detail exists in child diagrams.
    decomposition: dict | None = None

    @property
    def id(self) -> str:
        return stable_id("VP", self.kind, self.scope.get("type"), self.scope.get("id"))

    def to_dict(self) -> dict:
        """Deterministic, timestamp-free machine-readable form (H4-ready)."""
        nodes = sorted(self.nodes, key=lambda n: n.id)
        return {
            "contract": CONTRACT, "contract_version": CONTRACT_VERSION, "id": self.id, "kind": self.kind, "title": self.title,
            "audience": self.audience, "scope": self.scope,
            "nodes": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in sorted(self.edges, key=lambda e: e.id)],
            "groups": [g.to_dict() for g in sorted(self.groups, key=lambda g: g.id)],
            "legend": [{"status": s, "label": label, "style": style} for s, label, style in LEGEND],
            "provenance": self.provenance, "unresolved": self.unresolved, "partial": self.partial, "metadata": self.metadata,
            **({"decomposition": self.decomposition} if self.decomposition is not None else {}),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"


class VisualModelError(ValueError):
    """The projection violates the visual model contract; it must not be rendered."""


def validate_projection(projection: VisualProjection) -> None:
    """Raises `VisualModelError` listing every contract violation (empty graphs are valid)."""
    problems: list[str] = []
    if projection.kind not in KINDS:
        problems.append(f"unknown kind {projection.kind!r}")
    if projection.audience not in AUDIENCES:
        problems.append(f"unknown audience {projection.audience!r}")
    nodes = {}
    for node in projection.nodes:
        if node.id in nodes:
            problems.append(f"duplicate node id {node.id}")
        nodes[node.id] = node
        if node.status not in STATUSES:
            problems.append(f"node {node.id}: invalid status {node.status!r}")
        if not str(node.label).strip():
            problems.append(f"node {node.id}: empty label")
        if node.status in (CONFIRMED, CANONICAL) and not node.source_refs and not node.metadata.get("aggregate"):
            problems.append(f"node {node.id}: {node.status} without source_refs")
    group_ids = {g.id for g in projection.groups}
    for node in projection.nodes:
        if node.group and node.group not in group_ids:
            problems.append(f"node {node.id}: unknown group {node.group}")
    seen_edges = set()
    for edge in projection.edges:
        if edge.id in seen_edges:
            problems.append(f"duplicate edge {edge.source}->{edge.target} ({edge.relation})")
        seen_edges.add(edge.id)
        if edge.status not in STATUSES:
            problems.append(f"edge {edge.id}: invalid status {edge.status!r}")
            continue
        if edge.source not in nodes or edge.target not in nodes:
            problems.append(f"edge {edge.id}: dangling endpoint")
            continue
        if edge.status in (CONFIRMED, CANONICAL) and not edge.source_refs:
            problems.append(f"edge {edge.id}: {edge.status} without source_refs (untraceable)")
        if edge.status == INFERRED and not (edge.label or edge.metadata.get("rule")):
            problems.append(f"edge {edge.id}: INFERRED without a stated rule")
        for endpoint in (nodes[edge.source], nodes[edge.target]):
            if edge.status not in _ALLOWED_EDGE_STATUS.get(endpoint.status, set(STATUSES)):
                problems.append(f"edge {edge.id}: status {edge.status} exceeds endpoint {endpoint.id} ({endpoint.status})")
    partial = projection.partial
    if not isinstance(partial, dict) or set(partial) != {"partial", "included_count", "omitted_count", "reason"}:
        problems.append("partial must declare partial/included_count/omitted_count/reason")
    elif partial["partial"] and not partial["reason"]:
        problems.append("partial diagram without a reason")
    dec = projection.decomposition
    if dec is not None:
        if dec.get("role") not in ("summary", "detail"):
            problems.append("decomposition.role must be summary or detail")
        elif dec["role"] == "detail":
            if not dec.get("parent_projection_id"):
                problems.append("decomposition detail without parent_projection_id")
            if not (isinstance(dec.get("part_index"), int) and isinstance(dec.get("part_count"), int) and 1 <= dec["part_index"] <= dec["part_count"]):
                problems.append("decomposition detail with invalid part_index/part_count")
        else:
            if not dec.get("aggregation_reason"):
                problems.append("decomposition summary without aggregation_reason")
            if not isinstance(dec.get("children"), list) or dec.get("child_count") != len(dec.get("children", [])):
                problems.append("decomposition summary with inconsistent children")
    if problems:
        raise VisualModelError("; ".join(problems))
