"""Builders: persisted deterministic knowledge -> `VisualProjection` (post-V5 H3).

Inputs are the same persisted artifacts the H2 audience documentation uses (the transformed + enriched audience model, the
raw flow/entry-point indexes and the Evidence ids). Nothing here scans source code, calls a provider or draws anything.

Relationship inventory (what each builder is allowed to claim):

* solution -> project (containment of a `.sln`)                      SAFE_FOR_VISUALIZATION  (CONFIRMED)
* project -> project reference (`ProjectReference`)                   SAFE_FOR_VISUALIZATION  (CONFIRMED)
* project -> layer (structural rule, H2)                              SAFE_IF_LABELED_INFERRED (INFERRED, drawn as a group)
* project -> library, classified internal                              SAFE_FOR_VISUALIZATION  (CONFIRMED)
* project -> library, classified platform                              SAFE_IF_LABELED_INFERRED (group status INFERRED)
* project -> library, unclassified                                     NOT_SAFE_YET as a nature claim: the reference is
  confirmed, its nature (own vs third party) is UNRESOLVED and drawn so
* screen -> event -> handler -> method -> data operation (a flow)     SAFE_FOR_VISUALIZATION  (edge confidence preserved)
* method -> unresolved call                                            SAFE_FOR_VISUALIZATION  (UNRESOLVED)
* screen -> data object, and its read/create/update/delete category    object edge CONFIRMED; the category is INFERRED from
  the operation NAME (H2 classifier) and is drawn as a group, never as a fact
* AI proposal / canonical record -> flow evidence                      AI_ONLY_IF_LABELED (only with `--ai-run`, always AI_INTERPRETATION
  or CANONICAL, never merged into confirmed facts)
* business grouping of projects / use cases                           NOT_SAFE_YET (not drawn)
"""
from __future__ import annotations

from collections import Counter, defaultdict

from legacy_documenter.documentation_v52.audience import classify_target
from legacy_documenter.documentation_v52.categories import AudienceDocumentModel

from .model import (
    AI_INTERPRETATION, CANONICAL, CONFIRMED, INFERRED, UNRESOLVED, Edge, Group, Node, VisualProjection, stable_id,
)

MAX_NODES = 40
MAX_AREAS = 25
ACTION_LABEL = {
    "read": "Consulta / lectura (inferida del nombre)", "create": "Registro / creación (inferida del nombre)",
    "update": "Modificación (inferida del nombre)", "delete": "Eliminación (inferida del nombre)",
    "mixed": "Operación mixta (inferida del nombre)", "unknown": "Tipo no determinado",
}
LAYER_LABEL = {"presentation": "Presentación", "logic": "Lógica / servicios", "data_access": "Acceso a datos", "unclassified": "Sin clasificar"}
LAYER_RULE = {
    "owns_screens": "tiene pantallas propias", "direct_data_access": "sin pantallas, con accesos directos a datos",
    "receives_flows_or_referenced": "recibe recorridos o tiene referencias entre proyectos", "no_rule_applies": "ninguna regla aplica",
    "no_project": "sin proyecto identificable",
}
_EDGE_LABEL = {
    "WebForm -> Event": "evento", "Event -> Handler": "manejado por", "Handler -> Method": "ejecuta", "Method -> Method": "llama a",
    "Method -> DataAccessOperation": "accede a datos", "DataAccessOperation -> StoredProcedure": "invoca",
    "DataAccessOperation -> SQL": "ejecuta SQL", "Method -> UnresolvedCall": "no resuelta",
}
_CONFIDENCE = {"confirmed": CONFIRMED, "inferred": INFERRED, "unresolved": UNRESOLVED}


class VisualContext:
    """Everything the builders read, resolved once from persisted artifacts."""

    def __init__(self, model: AudienceDocumentModel, source: dict, evidence_ids: dict, manifest_sha256: str,
                 knowledge: dict | None = None, max_nodes: int = MAX_NODES, max_children: int = 30) -> None:
        self.max_children = max_children
        self.model = model
        self.source = source
        self.max_nodes = max_nodes
        self.manifest_ref = f"evidence-manifest:{manifest_sha256[:12]}"
        self.manifest_sha256 = manifest_sha256
        self.project_ids = evidence_ids.get("projects", {})
        self.solution_ids = evidence_ids.get("solutions", {})
        self.knowledge = knowledge or {"proposals": [], "canonical": []}
        self.modules = {m.slug: m for m in model.modules if m.values["path"]}
        self.module_by_path = {m.values["path"]: m for m in model.modules if m.values["path"]}
        self.solutions = {s.slug: s for s in model.solutions}
        self.flows = {f["id"]: f for f in source.get("functional_flows", [])}
        self.ep_project = {ep.get("id"): ep.get("project") for ep in source.get("entry_points", [])}

    # ---- identity helpers
    def project_ref(self, path: str) -> str:
        return self.project_ids.get(path) or f"project:{path}"

    def solution_ref(self, path: str) -> str:
        return self.solution_ids.get(path) or f"solution:{path}"

    def area_modules(self, slug: str) -> list:
        solution = self.solutions[slug]
        return [self.module_by_path[i.values["path"]] for i in solution.slots.get("projects", []) if i.values["path"] in self.module_by_path]

    def meta(self) -> dict:
        return {"evidence_manifest_sha256": self.manifest_sha256, "generated_from": "persisted deterministic output (no source scan, no provider)"}


def _projection(ctx: VisualContext, kind: str, title: str, audience: str, scope: dict) -> VisualProjection:
    return VisualProjection(kind=kind, title=title, audience=audience, scope=scope, provenance=[{"ref": ctx.manifest_ref, "role": "evidence manifest"}],
                            metadata=ctx.meta())


def _layer_group(layer: str, status: str) -> Group:
    return Group(id=stable_id("G", "layer", layer), label=f"Capa (inferida): {LAYER_LABEL[layer]}" if layer != "unclassified" else "Capa: sin clasificar", status=status)


def _finish_unresolved(p: VisualProjection) -> VisualProjection:
    """Merges duplicate edges (same endpoints and relation: e.g. one screen reaching one object through several events) by uniting
    their references, then records the unresolved nodes. Nothing is dropped: the merged edge carries every reference."""
    merged: dict[str, Edge] = {}
    for edge in p.edges:
        if edge.id in merged:
            keep = merged[edge.id]
            keep.source_refs = sorted(set(keep.source_refs) | set(edge.source_refs))
            keep.metadata["merged"] = keep.metadata.get("merged", 1) + 1
        else:
            merged[edge.id] = edge
    p.edges = list(merged.values())
    p.unresolved = [{"node_id": n.id, "label": n.label} for n in sorted(p.nodes, key=lambda n: n.id) if n.status == UNRESOLVED]
    return p


# ------------------------------------------------------------------------------------------------------ system-map
def build_system_map(ctx: VisualContext, area: str | None = None) -> VisualProjection:
    model = ctx.model
    if area is None:
        p = _projection(ctx, "system-map", f"Mapa del sistema: {model.system['name']}", "executive", {"type": "system", "id": "system", "label": model.system["name"]})
        sid = stable_id("N", p.id, "system")
        p.nodes.append(Node(sid, str(model.system["name"]), "system", CONFIRMED, [ctx.manifest_ref], column=0,
                            sublabel=f"{model.system['areas']} áreas · {model.system['projects']} proyectos"))
        areas = list(model.slots["areas"])
        shown, rest = areas[:MAX_AREAS], areas[MAX_AREAS:]
        layer_nodes: dict[str, str] = {}
        for item in shown:
            slug = item.values["slug"]
            solution = ctx.solutions[slug]
            nid = stable_id("N", p.id, "area", slug)
            p.nodes.append(Node(nid, item.values["name"], "area", CONFIRMED, [ctx.solution_ref(solution.values["path"])], column=1,
                                sublabel=f"{item.values['projects']} proyectos · {item.values['screens']} pantallas"))
            p.edges.append(Edge(sid, nid, "contains", CONFIRMED, [ctx.solution_ref(solution.values["path"])], "contiene"))
            counts = Counter(m.values["layer"] for m in ctx.area_modules(slug))
            for layer in ("presentation", "logic", "data_access", "unclassified"):
                if counts.get(layer):
                    lid = layer_nodes.setdefault(layer, stable_id("N", p.id, "layer", layer))
                    p.edges.append(Edge(nid, lid, "has_layer", INFERRED if layer != "unclassified" else UNRESOLVED,
                                        [ctx.project_ref(m.values["path"]) for m in ctx.area_modules(slug) if m.values["layer"] == layer],
                                        f"{counts[layer]}", {"rule": "structural layer rule (H2)"}))
        for layer, lid in sorted(layer_nodes.items()):
            total = sum(1 for m in ctx.modules.values() if m.values["layer"] == layer)
            p.nodes.append(Node(lid, LAYER_LABEL[layer], "layer", INFERRED if layer != "unclassified" else UNRESOLVED,
                                [ctx.manifest_ref] if layer != "unclassified" else [], column=2, sublabel=f"{total} proyectos (regla estructural)",
                                metadata={"rule": "see layer rules"}))
        if rest:
            rid = stable_id("N", p.id, "area-rest")
            p.nodes.append(Node(rid, f"+{len(rest)} áreas más", "aggregate", CONFIRMED, [ctx.manifest_ref], column=1,
                                metadata={"aggregate": True, "count": len(rest), "items": [i.values["name"] for i in rest]}))
            p.edges.append(Edge(sid, rid, "contains", CONFIRMED, [ctx.manifest_ref], "contiene"))
            p.partial = {"partial": True, "included_count": len(shown), "omitted_count": len(rest),
                         "reason": f"more than {MAX_AREAS} areas: the rest are aggregated in one node (names kept in the model JSON)"}
        else:
            p.partial = {"partial": False, "included_count": len(shown), "omitted_count": 0, "reason": ""}
        return _finish_unresolved(p)
    solution = ctx.solutions[area]
    p = _projection(ctx, "system-map", f"Mapa del área: {solution.values['name']}", "executive", {"type": "area", "id": area, "label": solution.values["name"]})
    aid = stable_id("N", p.id, "area")
    p.nodes.append(Node(aid, solution.values["name"], "area", CONFIRMED, [ctx.solution_ref(solution.values["path"])], column=0, sublabel="solución (.sln)"))
    members = sorted(ctx.area_modules(area), key=lambda m: (-(m.values["real_flows"] + m.values["screens"] + m.values["data_ops"]), m.values["name"], m.slug))
    shown, rest = members[: ctx.max_nodes], members[ctx.max_nodes:]
    layers_seen: dict[str, str] = {}
    for m in shown:
        pid = stable_id("N", p.id, "project", m.slug)
        p.nodes.append(Node(pid, m.values["name"], "project", CONFIRMED, [ctx.project_ref(m.values["path"])], column=1,
                            sublabel=f"{m.values['screens']} pantallas · {m.values['data_ops']} oper. de datos"))
        p.edges.append(Edge(aid, pid, "contains", CONFIRMED, [ctx.solution_ref(solution.values["path"]), ctx.project_ref(m.values["path"])], "contiene"))
        layer = m.values["layer"]
        lid = layers_seen.setdefault(layer, stable_id("N", p.id, "layer", layer))
        p.edges.append(Edge(pid, lid, "has_layer", INFERRED if layer != "unclassified" else UNRESOLVED, [ctx.project_ref(m.values["path"])],
                            "inferida", {"rule": LAYER_RULE.get(m.values["layer_rule"], m.values["layer_rule"])}))
    for layer, lid in sorted(layers_seen.items()):
        p.nodes.append(Node(lid, LAYER_LABEL[layer], "layer", INFERRED if layer != "unclassified" else UNRESOLVED,
                            [ctx.manifest_ref] if layer != "unclassified" else [], column=2, metadata={"rule": "structural layer rule (H2)"}))
    if rest:
        rid = stable_id("N", p.id, "project-rest")
        p.nodes.append(Node(rid, f"+{len(rest)} proyectos más", "aggregate", CONFIRMED, [ctx.manifest_ref], column=1,
                            metadata={"aggregate": True, "count": len(rest), "items": [m.values["name"] for m in rest]}))
        p.edges.append(Edge(aid, rid, "contains", CONFIRMED, [ctx.solution_ref(solution.values["path"])], "contiene"))
    p.partial = ({"partial": True, "included_count": len(shown), "omitted_count": len(rest), "reason": f"more than {ctx.max_nodes} projects: aggregated"}
                 if rest else {"partial": False, "included_count": len(shown), "omitted_count": 0, "reason": ""})
    return _finish_unresolved(p)


# ------------------------------------------------------------------------------------------------------ project-layer-map
def _neighbour_paths(ctx: VisualContext, module) -> tuple[list[str], list[str]]:
    out = [i.values["path"] for i in module.slots.get("project_refs_out", []) if i.values["path"] in ctx.module_by_path]
    inn = [i.values["path"] for i in module.slots.get("project_refs_in", []) if i.values["path"] in ctx.module_by_path]
    return sorted(set(out)), sorted(set(inn))


def build_project_layer_map(ctx: VisualContext, project: str | None = None, area: str | None = None) -> VisualProjection:
    if project:
        centre = [ctx.modules[project]]
        scope = {"type": "project", "id": project, "label": ctx.modules[project].values["name"]}
        title = f"Capas y vecinos: {scope['label']}"
        audience = "technical_overview"
    else:
        centre = sorted(ctx.area_modules(area), key=lambda m: (m.values["name"], m.slug))
        scope = {"type": "area", "id": area, "label": ctx.solutions[area].values["name"]}
        title = f"Capas de los proyectos del área: {scope['label']}"
        audience = "technical_overview"
    p = _projection(ctx, "project-layer-map", title, audience, scope)
    wanted: dict[str, object] = {m.values["path"]: m for m in centre}
    neighbours: dict[str, object] = {}
    edges: list[tuple[str, str, object]] = []
    for m in centre:
        outs, ins = _neighbour_paths(ctx, m)
        for path in outs:
            edges.append((m.values["path"], path, m))
            if path not in wanted:
                neighbours[path] = ctx.module_by_path[path]
        for path in ins:
            edges.append((path, m.values["path"], m))
            if path not in wanted:
                neighbours[path] = ctx.module_by_path[path]
    extra = sorted(neighbours.values(), key=lambda m: (m.values["name"], m.slug))
    room = max(0, ctx.max_nodes - len(wanted))
    keep, dropped = extra[:room], extra[room:]
    allowed = set(wanted) | {m.values["path"] for m in keep}
    groups: dict[str, Group] = {}
    for m in list(centre) + keep:
        layer = m.values["layer"]
        groups.setdefault(layer, _layer_group(layer, INFERRED if layer != "unclassified" else UNRESOLVED))
        p.nodes.append(Node(stable_id("N", p.id, m.slug), m.values["name"], "project", CONFIRMED, [ctx.project_ref(m.values["path"])],
                            group=groups[layer].id, sublabel=("vecino" if m.values["path"] not in wanted else "proyecto") + f" · {m.values['screens']} pantallas",
                            metadata={"layer": layer, "layer_rule": m.values["layer_rule"]}))
    p.groups = list(groups.values())
    seen = set()
    for src, dst, owner in edges:
        if src in allowed and dst in allowed and (src, dst) not in seen:
            seen.add((src, dst))
            source_module = ctx.module_by_path[src]
            p.edges.append(Edge(stable_id("N", p.id, source_module.slug), stable_id("N", p.id, ctx.module_by_path[dst].slug), "references", CONFIRMED,
                                [ctx.project_ref(src)], "referencia"))
    if dropped:
        rid = stable_id("N", p.id, "neighbour-rest")
        p.nodes.append(Node(rid, f"+{len(dropped)} vecinos más", "aggregate", CONFIRMED, [ctx.manifest_ref],
                            metadata={"aggregate": True, "count": len(dropped), "items": [m.values["name"] for m in dropped]}))
    p.partial = ({"partial": True, "included_count": len(allowed), "omitted_count": len(dropped), "reason": f"more than {ctx.max_nodes} projects: neighbours aggregated"}
                 if dropped else {"partial": False, "included_count": len(allowed), "omitted_count": 0, "reason": ""})
    return _finish_unresolved(p)


# ------------------------------------------------------------------------------------------------------ dependency-map
_CLASS_GROUP = {
    "internal": ("Biblioteca interna del repositorio", CONFIRMED), "platform": ("Biblioteca de la plataforma (clasificada por lista)", INFERRED),
    "unclassified": ("Sin clasificar: propia o de terceros no determinado", UNRESOLVED),
}


def build_dependency_map(ctx: VisualContext, project: str | None = None, area: str | None = None) -> VisualProjection:
    if project:
        members = [ctx.modules[project]]
        scope = {"type": "project", "id": project, "label": ctx.modules[project].values["name"]}
    else:
        members = sorted(ctx.area_modules(area), key=lambda m: (m.values["name"], m.slug))
        scope = {"type": "area", "id": area, "label": ctx.solutions[area].values["name"]}
    p = _projection(ctx, "dependency-map", f"Dependencias: {scope['label']}", "technical_overview", scope)
    member_paths = {m.values["path"] for m in members}
    shown_members = members[: ctx.max_nodes]
    node_of: dict[str, str] = {}
    for m in shown_members:
        node_of[m.values["path"]] = stable_id("N", p.id, "project", m.slug)
        p.nodes.append(Node(node_of[m.values["path"]], m.values["name"], "project", CONFIRMED, [ctx.project_ref(m.values["path"])], column=1,
                            sublabel="proyecto del alcance"))
    omitted_members = len(members) - len(shown_members)
    # project -> project references
    external_budget = max(0, ctx.max_nodes - len(shown_members))
    external: dict[str, object] = {}
    for m in shown_members:
        outs, _ins = _neighbour_paths(ctx, m)
        for path in outs:
            target = ctx.module_by_path[path]
            if path not in node_of:
                if path not in external and len(external) >= external_budget:
                    continue
                external[path] = target
                node_of[path] = stable_id("N", p.id, "project", target.slug)
                p.nodes.append(Node(node_of[path], target.values["name"], "project", CONFIRMED, [ctx.project_ref(path)], column=2, sublabel="proyecto referenciado"))
            p.edges.append(Edge(node_of[m.values["path"]], node_of[path], "references", CONFIRMED, [ctx.project_ref(m.values["path"])], "referencia proyecto"))
    # project -> libraries (per class), grouped and bounded
    groups: dict[str, Group] = {}
    per_class_limit = 10 if project else 6
    for cls in ("internal", "platform", "unclassified"):
        libs: dict[str, list] = defaultdict(list)
        for m in shown_members:
            for lib in m.slots.get("libraries", []):
                if lib.values["class"] == cls:
                    libs[lib.values["name"]].append(m)
        if not libs:
            continue
        label, status = _CLASS_GROUP[cls]
        groups[cls] = Group(stable_id("G", "dep", cls), label, status)
        ordered = sorted(libs.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))
        for name, users in ordered[:per_class_limit]:
            lid = stable_id("N", p.id, "lib", name)
            p.nodes.append(Node(lid, name, "library", CONFIRMED, [ctx.project_ref(u.values["path"]) for u in users], column=3, group=groups[cls].id,
                                sublabel=f"{len(users)} proyecto(s)", metadata={"class": cls}))
            for u in users:
                p.edges.append(Edge(node_of[u.values["path"]], lid, "uses_library", CONFIRMED, [ctx.project_ref(u.values["path"])], "usa"))
        rest = ordered[per_class_limit:]
        if rest:
            rid = stable_id("N", p.id, "lib-rest", cls)
            p.nodes.append(Node(rid, f"+{len(rest)} bibliotecas más ({cls})", "aggregate", CONFIRMED, [ctx.manifest_ref], column=3, group=groups[cls].id,
                                metadata={"aggregate": True, "count": len(rest), "items": [n for n, _ in rest]}))
            for u in {u.values["path"]: u for _n, us in rest for u in us}.values():
                p.edges.append(Edge(node_of[u.values["path"]], rid, "uses_library", CONFIRMED, [ctx.project_ref(u.values["path"])], "usa"))
    p.groups = list(groups.values())
    aggregated = sum(1 for n in p.nodes if n.metadata.get("aggregate"))
    omitted = omitted_members + sum(n.metadata.get("count", 0) for n in p.nodes if n.metadata.get("aggregate"))
    p.partial = ({"partial": True, "included_count": len(p.nodes) - aggregated, "omitted_count": omitted,
                  "reason": "bounded: extra libraries/projects aggregated (names kept in the model JSON)"} if (aggregated or omitted_members)
                 else {"partial": False, "included_count": len(p.nodes), "omitted_count": 0, "reason": ""})
    return _finish_unresolved(p)


# ------------------------------------------------------------------------------------------------------ observable-flow
def _tail(label: str) -> str:
    return label.split("::")[-1] if "::" in label else label


def build_observable_flow(ctx: VisualContext, flow_id: str, include_ai: bool = False) -> VisualProjection:
    flow = ctx.flows[flow_id]
    scope = {"type": "flow", "id": flow_id, "label": f"{flow.get('webform')} / {flow.get('event')}"}
    p = _projection(ctx, "observable-flow", f"Flujo observable: {flow.get('webform')} · {flow.get('event')}", "functional", scope)
    nodes = {n["id"]: n for n in flow["nodes"]}
    edges = [e for e in flow["edges"] if e["source"] in nodes and e["target"] in nodes]
    refs_of: dict[str, set] = defaultdict(set)
    for e in edges:
        for node_id in (e["source"], e["target"]):
            refs_of[node_id].update(e.get("evidence_refs") or [])
    for n in nodes.values():
        refs_of[n["id"]].add(flow_id)
    # breadth-first depth from the screen (deterministic order), unresolved calls aggregated per method
    out: dict[str, list[dict]] = defaultdict(list)
    for e in sorted(edges, key=lambda e: (e["type"], e["source"], e["target"])):
        out[e["source"]].append(e)
    start = next((i for i, n in nodes.items() if n["type"] == "WebForm"), None)
    order, seen = [], set()
    queue = [start] if start else []
    while queue:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        order.append(cur)
        queue.extend(e["target"] for e in out.get(cur, []) if e["target"] not in seen)
    order.extend(sorted(i for i in nodes if i not in seen))
    unres_by_source: dict[str, list[dict]] = defaultdict(list)
    for e in edges:
        if nodes[e["target"]]["type"] == "UnresolvedCall":
            unres_by_source[e["source"]].append(e)
    collapsed = {e["target"] for src, es in unres_by_source.items() if len(es) > 3 for e in es}
    connected = {e["source"] for e in edges} | {e["target"] for e in edges}
    # Project nodes become groups and component (Class) nodes carry no relation of their own: both are folded into the method labels/groups.
    folded = [i for i in order if nodes[i]["type"] in ("Project", "Class") and i not in connected]
    visible = [i for i in order if i not in collapsed and i not in folded]
    included = visible[: ctx.max_nodes]
    # aggregate nodes (several unresolved calls of one method) count against the bound too
    while included and len(included) + sum(1 for src, es in unres_by_source.items() if len(es) > 3 and src in set(included)) > ctx.max_nodes:
        included.pop()
    omitted_ids = [i for i in visible if i not in set(included)]
    inc = set(included)

    def group_for(node: dict) -> Group | None:
        proj = node.get("project")
        if not proj:
            return None
        module = ctx.module_by_path.get(proj)
        label = module.values["name"] if module else proj
        return Group(stable_id("G", "proj", proj), f"Proyecto: {label}", CONFIRMED)

    groups: dict[str, Group] = {}
    pid = {}
    for i in included:
        n = nodes[i]
        kind = {"WebForm": "screen", "Event": "event", "Handler": "handler", "Class": "class", "Method": "method", "DataAccessOperation": "data_operation",
                "StoredProcedure": "data_object", "SQL": "data_object", "UnresolvedCall": "unresolved_call"}.get(n["type"], "method")
        status = UNRESOLVED if n["type"] == "UnresolvedCall" else CONFIRMED
        label = _tail(n["label"]) if n["type"] in ("Event", "Method") else n["label"]
        if n["type"] == "DataAccessOperation":
            label = "Acceso a datos"
        if n["type"] == "SQL":
            label = "SQL directo"
        g = group_for(n)
        if g:
            groups.setdefault(g.id, g)
        pid[i] = stable_id("N", p.id, i)
        p.nodes.append(Node(pid[i], label, kind, status, sorted(refs_of[i]), group=g.id if g else None,
                            sublabel=i if n["type"] == "DataAccessOperation" else "",
                            metadata={"evidence_node": i}))
    for src, es in sorted(unres_by_source.items()):
        if len(es) > 3 and src in inc:
            aid = stable_id("N", p.id, "unres", src)
            labels = sorted({nodes[e["target"]]["label"] for e in es})
            src_group = p.nodes[[n.id for n in p.nodes].index(pid[src])].group
            p.nodes.append(Node(aid, f"{len(es)} llamadas no resueltas", "unresolved_call", UNRESOLVED,
                                sorted({r for e in es for r in (e.get("evidence_refs") or [])} or {flow_id}), group=src_group,
                                sublabel="la lista completa está en el modelo JSON", metadata={"aggregate": True, "count": len(es), "items": labels}))
            p.edges.append(Edge(pid[src], aid, "unresolved_call", UNRESOLVED, sorted({r for e in es for r in (e.get("evidence_refs") or [])} or {flow_id}), "no resueltas"))
    seen_edges = set()
    for e in edges:
        if e["source"] in inc and e["target"] in inc and e["target"] not in collapsed:
            key = (e["source"], e["target"], e["type"])
            if key in seen_edges:
                continue
            seen_edges.add(key)
            status = _CONFIDENCE.get(e.get("confidence"), UNRESOLVED)
            if nodes[e["target"]]["type"] == "UnresolvedCall":
                status = UNRESOLVED
            p.edges.append(Edge(pid[e["source"]], pid[e["target"]], e["type"], status, e.get("evidence_refs") or [flow_id], _EDGE_LABEL.get(e["type"], e["type"])))
    if omitted_ids:
        rid = stable_id("N", p.id, "rest")
        unresolved_rest = any(nodes[i]["type"] == "UnresolvedCall" for i in omitted_ids)
        p.nodes.append(Node(rid, f"+{len(omitted_ids)} nodos más", "aggregate", UNRESOLVED if unresolved_rest else CONFIRMED, [flow_id],
                            metadata={"aggregate": True, "count": len(omitted_ids), "items": [nodes[i]["label"] for i in omitted_ids]}))
        for e in edges:
            if e["source"] in inc and e["target"] in set(omitted_ids):
                p.edges.append(Edge(pid[e["source"]], rid, "continues", UNRESOLVED if unresolved_rest else CONFIRMED, e.get("evidence_refs") or [flow_id], "continúa"))
                break
    p.groups = list(groups.values())
    omitted = len(omitted_ids) + sum(len(es) for es in unres_by_source.values() if len(es) > 3)
    p.partial = ({"partial": True, "included_count": len(included), "omitted_count": omitted,
                  "reason": "unresolved calls aggregated per method and/or more than the node bound: aggregates keep the items in the model JSON"}
                 if (omitted_ids or collapsed) else {"partial": False, "included_count": len(included), "omitted_count": 0, "reason": ""})
    p.metadata["flow"] = {"flow_id": flow_id, "entry_point_id": flow.get("entry_point_id"), "status": flow.get("status"), "folded_nodes": len(folded)}
    if include_ai:
        _attach_knowledge(ctx, p, flow, nodes, pid)
    return _finish_unresolved(p)


def _attach_knowledge(ctx: VisualContext, p: VisualProjection, flow: dict, nodes: dict, pid: dict) -> None:
    """AI proposals / canonical records whose evidence refs touch this flow, drawn as separate, labelled nodes."""
    flow_refs = {flow["id"], flow.get("entry_point_id"), *flow.get("terminal_operations", [])} | set(nodes)
    entries = [("proposals", AI_INTERPRETATION, "ai_note"), ("canonical", CANONICAL, "canonical_note")]
    for key, status, node_type in entries:
        for k, item in enumerate(ctx.knowledge.get(key, [])):
            hit = sorted(set(item.get("evidence_refs") or []) & flow_refs)
            if not hit:
                continue
            anchor = next((i for i in pid if i in hit or nodes[i].get("id") in hit), next(iter(pid), None))
            if anchor is None:
                continue
            nid = stable_id("N", p.id, key, k, item.get("statement", ""))
            p.nodes.append(Node(nid, str(item.get("statement", ""))[:160], node_type, status, hit if status == CANONICAL else [], column=None,
                                sublabel="afirmación " + ("aprobada por una persona" if status == CANONICAL else "propuesta, sin aprobar")))
            p.edges.append(Edge(nid, pid[anchor], "interprets", status, hit, "interpreta"))


# ------------------------------------------------------------------------------------------------------ data-interaction-map
def interaction_rows(ctx: VisualContext, paths: set[str]) -> list[tuple[str, str, str, list[str]]]:
    """(screen, owning project path, data object, refs) for every flow of the given projects that reaches a stored procedure / SQL."""
    rows: list[tuple[str, str, str, list[str]]] = []
    for flow in sorted(ctx.flows.values(), key=lambda f: f["id"]):
        owner = ctx.ep_project.get(flow.get("entry_point_id"))
        if owner not in paths:
            continue
        nodes = {n["id"]: n for n in flow["nodes"]}
        objs = sorted({n["label"] for n in nodes.values() if n["type"] == "StoredProcedure"} | ({"SQL directo"} if any(n["type"] == "SQL" for n in nodes.values()) else set()))
        for obj in objs:
            rows.append((flow["webform"], owner, obj, [flow["id"], flow.get("entry_point_id") or flow["id"], *flow.get("terminal_operations", [])]))
    return rows


def build_data_interaction_map(ctx: VisualContext, project: str | None = None, area: str | None = None) -> VisualProjection:
    if project:
        members = [ctx.modules[project]]
        scope = {"type": "project", "id": project, "label": ctx.modules[project].values["name"]}
    else:
        members = ctx.area_modules(area)
        scope = {"type": "area", "id": area, "label": ctx.solutions[area].values["name"]}
    paths = {m.values["path"] for m in members}
    p = _projection(ctx, "data-interaction-map", f"Interacción con datos: {scope['label']}", "functional", scope)
    rows = interaction_rows(ctx, paths)
    by_screen: dict[tuple[str, str], list] = defaultdict(list)
    for screen, owner, obj, refs in rows:
        by_screen[(screen, owner)].append((obj, refs))
    screens = sorted(by_screen, key=lambda k: (-len(by_screen[k]), k[0], k[1]))
    shown_screens = screens[: max(1, ctx.max_nodes // 2)]
    object_use = Counter(obj for k in shown_screens for obj, _ in by_screen[k])
    objects = [o for o, _ in sorted(object_use.items(), key=lambda kv: (-kv[1], kv[0]))]
    shown_objects = objects[: ctx.max_nodes - len(shown_screens)]
    action_groups: dict[str, Group] = {}
    obj_node: dict[str, str] = {}
    for obj in sorted(shown_objects):
        action = "unknown" if obj == "SQL directo" else classify_target(obj)
        g = action_groups.setdefault(action, Group(stable_id("G", "act", action), ACTION_LABEL[action], INFERRED if action != "unknown" else UNRESOLVED))
        obj_node[obj] = stable_id("N", p.id, "obj", obj)
        refs = sorted({r for k in shown_screens for o, rr in by_screen[k] if o == obj for r in rr if str(r).startswith("DAO-")}
                      or {r for k in shown_screens for o, rr in by_screen[k] if o == obj for r in rr[:1]})
        p.nodes.append(Node(obj_node[obj], obj, "data_object", CONFIRMED, refs, column=1, group=g.id, sublabel=f"{object_use[obj]} uso(s)",
                            metadata={"action": action, "action_rule": "inferred from the operation name (H2 classifier)"}))
    screen_node: dict[tuple[str, str], str] = {}
    for key in shown_screens:
        screen, owner = key
        module = ctx.module_by_path.get(owner)
        screen_node[key] = stable_id("N", p.id, "screen", screen, owner)
        p.nodes.append(Node(screen_node[key], screen, "screen", CONFIRMED, sorted({r for _o, rr in by_screen[key] for r in rr[:2]}), column=0,
                            sublabel=f"proyecto {module.values['name']}" if module else "proyecto no identificado"))
        for obj, refs in by_screen[key]:
            if obj in obj_node:
                p.edges.append(Edge(screen_node[key], obj_node[obj], "invokes_data_object", CONFIRMED, refs, "usa"))
    p.groups = list(action_groups.values())
    omitted_screens, omitted_objects = len(screens) - len(shown_screens), len(objects) - len(shown_objects)
    if omitted_screens or omitted_objects:
        rid = stable_id("N", p.id, "rest")
        parts = [text for text in (f"+{omitted_screens} pantallas" if omitted_screens else "", f"+{omitted_objects} objetos" if omitted_objects else "") if text]
        p.nodes.append(Node(rid, " y ".join(parts) + " más", "aggregate", CONFIRMED, [ctx.manifest_ref], column=0,
                            metadata={"aggregate": True, "count": omitted_screens + omitted_objects,
                                      "items": [f"{s} ({o})" for s, o in screens[len(shown_screens):]] + objects[len(shown_objects):]}))
    p.partial = ({"partial": True, "included_count": len(shown_screens) + len(shown_objects), "omitted_count": omitted_screens + omitted_objects,
                  "reason": "bounded by the node limit: least-used screens/objects are aggregated (kept in the model JSON)"}
                 if (omitted_screens or omitted_objects) else {"partial": False, "included_count": len(shown_screens) + len(shown_objects), "omitted_count": 0, "reason": ""})
    return _finish_unresolved(p)
