"""Graph node/edge construction helpers for flow resolution (V4.1-R6)."""


def node(node_type: str, node_id: str | None, label: str | None, project: str | None = None) -> dict:
    """Builds a graph node descriptor."""
    return {"id": node_id or "", "type": node_type, "label": label or node_id or "", "project": project}


def add_node(nodes: dict[str, dict], new_node: dict) -> None:
    """Registers a node the first time its id is seen; later calls are no-ops."""
    if new_node["id"]:
        nodes.setdefault(new_node["id"], new_node)


def add_edge(edges: dict[tuple, dict], source: str | None, target: str | None, edge_type: str, confidence: str | None, evidence_ref: str | None) -> None:
    """Registers an edge the first time its (source, target, type, evidence) is seen."""
    if not source or not target:
        return
    key = (source, target, edge_type, evidence_ref)
    edges.setdefault(key, {"source": source, "target": target, "type": edge_type, "confidence": confidence or "confirmed", "evidence_refs": [evidence_ref] if evidence_ref else []})
