"""Deterministic decomposition of dense diagrams (post-V5 H3-R2).

Readability by decomposition, not by clever routing: when a dependency or data-interaction map is dense, the package gets one
SUMMARY (aggregated, with exact counts) plus bounded DETAIL diagrams that together carry every original relationship:

* dependency map   -> summary: projects + project references + one aggregate node per library class (the exact members stay in
  the node/edge metadata); details: one focal project per child (its project references, then its libraries per class in chunks).
* data interaction -> summary: screen groups -> inferred action categories with exact (screen, object) relation counts; details: one
  action category per child, chunked by objects, with the concrete screen -> data object edges.

`partial` keeps its H3 meaning (this single view omits or aggregates concrete nodes). A summary is described by `decomposition`
(role, children, aggregation reason, counts): the detail exists in the child diagrams of the same package.
Small diagrams are returned unchanged (a list with the single H3 projection).
"""
from __future__ import annotations

from collections import Counter, defaultdict

from legacy_documenter.documentation_v52.audience import classify_target

from .builders import (
    ACTION_LABEL, _CLASS_GROUP, VisualContext, _finish_unresolved, _neighbour_paths, _projection, build_data_interaction_map, build_dependency_map,
    interaction_rows,
)
from .model import CONFIRMED, INFERRED, UNRESOLVED, Edge, Group, Node, VisualProjection, stable_id

DENSE_EDGES = 24
CHUNK_LIBS = 14
CHUNK_OBJECTS = 10
SCREEN_GROUP = 8
MAX_SCREEN_GROUPS = 12
_CLASS_NOUN = {"internal": "Bibliotecas internas", "platform": "Bibliotecas de la plataforma", "unclassified": "Dependencias sin clasificar"}


def _scope_members(ctx: VisualContext, project: str | None, area: str | None):
    if project:
        return [ctx.modules[project]], {"type": "project", "id": project, "label": ctx.modules[project].values["name"]}
    return (sorted(ctx.area_modules(area), key=lambda m: (m.values["name"], m.slug)),
            {"type": "area", "id": area, "label": ctx.solutions[area].values["name"]})


def _link_children(summary: VisualProjection, children: list[VisualProjection], reason: str, included: int, omitted: int, **extra) -> None:
    summary.decomposition = {
        "role": "summary", "child_count": len(children), "children": [c.id for c in children], "aggregation_reason": reason,
        "included_count": included, "omitted_count": omitted, **extra,
    }


def _detail(child: VisualProjection, parent: VisualProjection, index: int, count: int, **extra) -> VisualProjection:
    child.decomposition = {"role": "detail", "parent_projection_id": parent.id, "part_index": index, "part_count": count, "scope": child.scope,
                           "included_count": len(child.nodes), "omitted_count": 0, "aggregation_reason": "", **extra}
    return child


# ------------------------------------------------------------------------------------------------------ dependency maps
def build_dependency_maps(ctx: VisualContext, project: str | None = None, area: str | None = None) -> list[VisualProjection]:
    """[single] for a small scope; [summary, *details] when the H3 map would be dense or already aggregated."""
    single = build_dependency_map(ctx, project=project, area=area)
    if len(single.edges) <= DENSE_EDGES and not single.partial["partial"]:
        return [single]
    members, scope = _scope_members(ctx, project, area)
    shown = members[: ctx.max_nodes]
    summary = _projection(ctx, "dependency-map", f"Dependencias (resumen): {scope['label']}", "technical_overview", scope)
    node_of: dict[str, str] = {}
    for m in shown:
        node_of[m.values["path"]] = stable_id("N", summary.id, "project", m.slug)
        summary.nodes.append(Node(node_of[m.values["path"]], m.values["name"], "project", CONFIRMED, [ctx.project_ref(m.values["path"])], sublabel="proyecto del alcance"))
    budget = max(0, ctx.max_nodes - len(shown))
    external: set[str] = set()
    for m in shown:
        outs, _ins = _neighbour_paths(ctx, m)
        for path in outs:
            target = ctx.module_by_path[path]
            if path not in node_of:
                if len(external) >= budget:
                    continue
                external.add(path)
                node_of[path] = stable_id("N", summary.id, "project", target.slug)
                summary.nodes.append(Node(node_of[path], target.values["name"], "project", CONFIRMED, [ctx.project_ref(path)], sublabel="proyecto referenciado"))
            summary.edges.append(Edge(node_of[m.values["path"]], node_of[path], "references", CONFIRMED, [ctx.project_ref(m.values["path"])], "referencia proyecto"))
    groups: dict[str, Group] = {}
    libs_by_class: dict[str, dict[str, list]] = {}
    for cls in ("internal", "platform", "unclassified"):
        libs: dict[str, list] = defaultdict(list)
        for m in shown:
            for lib in m.slots.get("libraries", []):
                if lib.values["class"] == cls:
                    libs[lib.values["name"]].append(m)
        if not libs:
            continue
        libs_by_class[cls] = libs
        label, status = _CLASS_GROUP[cls]
        groups[cls] = Group(stable_id("G", "dep", cls), label, status)
        users = {u.values["path"]: u for us in libs.values() for u in us}
        by_project = {u.values["name"]: sorted(n for n, us in libs.items() if u in us) for u in users.values()}
        agg = stable_id("N", summary.id, "libclass", cls)
        summary.nodes.append(Node(agg, f"{_CLASS_NOUN[cls]} ({len(libs)})", "aggregate", CONFIRMED, sorted(ctx.project_ref(p) for p in users), group=groups[cls].id,
                                  sublabel="ver diagramas de detalle",
                                  metadata={"aggregate": True, "count": len(libs), "items": sorted(libs), "class": cls, "by_project": by_project}))
        for u in sorted(users.values(), key=lambda m: m.slug):
            names = by_project[u.values["name"]]
            summary.edges.append(Edge(node_of[u.values["path"]], agg, "uses_library_group", CONFIRMED, [ctx.project_ref(u.values["path"])], f"{len(names)}",
                                      {"members": names}))
    summary.groups = list(groups.values())
    summary.partial = {"partial": False, "included_count": len(summary.nodes), "omitted_count": 0, "reason": ""}
    # one detail family per focal project, ranked by dependency degree (deterministic), bounded by max_children
    degree = {m.slug: sum(len(v) for v in (m.slots.get("project_refs_out", []), m.slots.get("project_refs_in", []))) + len(m.slots.get("libraries", [])) for m in shown}
    focal = sorted((m for m in shown if degree[m.slug]), key=lambda m: (-degree[m.slug], m.values["name"], m.slug))
    children: list[VisualProjection] = []
    unexpanded: list[str] = []
    for m in focal:
        parts = _dependency_parts(ctx, m)
        if len(children) + len(parts) > ctx.max_children:
            unexpanded.append(m.values["name"])
            continue
        for index, (part_key, build) in enumerate(parts, start=1):
            child = build(summary)
            children.append(_detail(child, summary, index, len(parts), focal_project=m.slug, part=part_key))
    _link_children(summary, children, "dense dependency map: libraries aggregated by class (exact members in metadata); expanded in the detail diagrams",
                   len(shown), len(unexpanded), unexpanded_projects=sorted(unexpanded),
                   unexpanded_reason="child diagram bound reached (--max-children); their libraries remain listed in the summary metadata" if unexpanded else "")
    return [_finish_unresolved(summary), *[_finish_unresolved(c) for c in children]]


def _dependency_parts(ctx: VisualContext, module) -> list[tuple[str, object]]:
    parts: list[tuple[str, object]] = []
    outs, ins = _neighbour_paths(ctx, module)
    if outs or ins:
        parts.append(("projects", lambda parent, m=module, o=outs, i=ins: _dep_projects_child(ctx, m, o, i)))
    for cls in ("internal", "platform", "unclassified"):
        names = sorted({lib.values["name"] for lib in module.slots.get("libraries", []) if lib.values["class"] == cls}, key=str.lower)
        chunks = [names[k:k + CHUNK_LIBS] for k in range(0, len(names), CHUNK_LIBS)]
        for n, chunk in enumerate(chunks, start=1):
            key = f"{cls}" if len(chunks) == 1 else f"{cls}-{n}of{len(chunks)}"
            parts.append((key, lambda parent, m=module, c=cls, ch=chunk, k=key: _dep_libs_child(ctx, m, c, ch, k)))
    return parts


def _child_scope(module, part: str) -> dict:
    return {"type": "project", "id": f"{module.slug}:{part}", "label": module.values["name"], "focal_project": module.slug, "part": part}


def _dep_projects_child(ctx: VisualContext, module, outs: list[str], ins: list[str]) -> VisualProjection:
    p = _projection(ctx, "dependency-map", f"Dependencias de {module.values['name']}: proyectos", "technical_overview", _child_scope(module, "projects"))
    focal = stable_id("N", p.id, "focal")
    p.nodes.append(Node(focal, module.values["name"], "project", CONFIRMED, [ctx.project_ref(module.values["path"])], column=1, sublabel="proyecto en foco"))
    for path in ins:
        target = ctx.module_by_path[path]
        nid = stable_id("N", p.id, "in", target.slug)
        p.nodes.append(Node(nid, target.values["name"], "project", CONFIRMED, [ctx.project_ref(path)], column=0, sublabel="lo referencia"))
        p.edges.append(Edge(nid, focal, "references", CONFIRMED, [ctx.project_ref(path)], "referencia proyecto"))
    for path in outs:
        target = ctx.module_by_path[path]
        nid = stable_id("N", p.id, "out", target.slug)
        p.nodes.append(Node(nid, target.values["name"], "project", CONFIRMED, [ctx.project_ref(path)], column=2, sublabel="referenciado"))
        p.edges.append(Edge(focal, nid, "references", CONFIRMED, [ctx.project_ref(module.values["path"])], "referencia proyecto"))
    p.partial = {"partial": False, "included_count": len(p.nodes), "omitted_count": 0, "reason": ""}
    return p


def _dep_libs_child(ctx: VisualContext, module, cls: str, names: list[str], part: str) -> VisualProjection:
    label, status = _CLASS_GROUP[cls]
    p = _projection(ctx, "dependency-map", f"Dependencias de {module.values['name']}: {_CLASS_NOUN[cls].lower()}", "technical_overview", _child_scope(module, part))
    focal = stable_id("N", p.id, "focal")
    p.nodes.append(Node(focal, module.values["name"], "project", CONFIRMED, [ctx.project_ref(module.values["path"])], column=0, sublabel="proyecto en foco"))
    group = Group(stable_id("G", "dep", cls), label, status)
    p.groups = [group]
    for name in names:
        lid = stable_id("N", p.id, "lib", name)
        p.nodes.append(Node(lid, name, "library", CONFIRMED, [ctx.project_ref(module.values["path"])], column=1, group=group.id, metadata={"class": cls}))
        p.edges.append(Edge(focal, lid, "uses_library", CONFIRMED, [ctx.project_ref(module.values["path"])], "usa"))
    p.partial = {"partial": False, "included_count": len(p.nodes), "omitted_count": 0, "reason": ""}
    return p


# ------------------------------------------------------------------------------------------------------ data-interaction maps
def build_data_interaction_maps(ctx: VisualContext, project: str | None = None, area: str | None = None) -> list[VisualProjection]:
    """[single] for a small scope; [summary, *details] when there are many (screen, object) relations or screens."""
    members, scope = _scope_members(ctx, project, area)
    paths = {m.values["path"] for m in members}
    pairs: dict[tuple[str, str, str], list[str]] = {}
    for screen, owner, obj, refs in interaction_rows(ctx, paths):
        pairs.setdefault((screen, owner, obj), []).extend(refs)
    screens = sorted({(s, o) for s, o, _ in pairs})
    if len(pairs) <= DENSE_EDGES and len(screens) <= 12:
        return [build_data_interaction_map(ctx, project=project, area=area)]
    summary = _projection(ctx, "data-interaction-map", f"Interacción con datos (resumen): {scope['label']}", "functional", scope)
    groups_of = [screens[k:k + SCREEN_GROUP] for k in range(0, len(screens), SCREEN_GROUP)]
    kept, folded = groups_of[:MAX_SCREEN_GROUPS], groups_of[MAX_SCREEN_GROUPS:]
    folded_screens = [s for g in folded for s in g]

    def action_of(obj: str) -> str:
        return "unknown" if obj == "SQL directo" else classify_target(obj)

    action_nodes: dict[str, str] = {}
    cat_pairs: dict[str, int] = Counter()
    cat_objects: dict[str, set] = defaultdict(set)
    for (screen, owner, obj), refs in pairs.items():
        a = action_of(obj)
        cat_pairs[a] += 1
        cat_objects[a].add(obj)
    for action in ("read", "create", "update", "delete", "mixed", "unknown"):
        if cat_pairs[action]:
            nid = stable_id("N", summary.id, "cat", action)
            action_nodes[action] = nid
            summary.nodes.append(Node(nid, ACTION_LABEL[action], "data_category", INFERRED if action != "unknown" else UNRESOLVED, [] if action == "unknown" else [ctx.manifest_ref],
                                      column=1, sublabel=f"{len(cat_objects[action])} objetos · {cat_pairs[action]} relaciones",
                                      metadata={"action": action, "objects": len(cat_objects[action]), "relations": cat_pairs[action],
                                                "rule": "inferred from the operation name (H2 classifier)"}))
    group_nodes: list[tuple[str, list[tuple[str, str]]]] = []
    for k, grp in enumerate(kept, start=1):
        gid = stable_id("N", summary.id, "screens", k)
        first, last = grp[0][0].split("\\")[-1], grp[-1][0].split("\\")[-1]
        refs = sorted({r for s, o in grp for obj in {x[2] for x in pairs if x[0] == s and x[1] == o} for r in pairs[(s, o, obj)][:2]})
        summary.nodes.append(Node(gid, f"Pantallas {k} de {len(groups_of)}", "screen_group", CONFIRMED, refs, column=0, sublabel=f"{len(grp)} pantallas: {first} … {last}",
                                  metadata={"screens": [s for s, _ in grp]}))
        group_nodes.append((gid, grp))
    if folded:
        gid = stable_id("N", summary.id, "screens-rest")
        refs = sorted({r for s, o in folded_screens for obj in {x[2] for x in pairs if x[0] == s and x[1] == o} for r in pairs[(s, o, obj)][:2]})
        summary.nodes.append(Node(gid, f"+{len(folded_screens)} pantallas más", "aggregate", CONFIRMED, refs, column=0,
                                  metadata={"aggregate": True, "count": len(folded_screens), "items": [s for s, _ in folded_screens]}))
        group_nodes.append((gid, folded_screens))
    total_edge_relations = 0
    for gid, grp in group_nodes:
        screen_set = set(grp)
        by_action: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for (screen, owner, obj), refs in sorted(pairs.items()):
            if (screen, owner) in screen_set:
                by_action[action_of(obj)].append((screen, obj))
        for action, members_ in sorted(by_action.items()):
            refs = sorted({r for (screen, obj) in members_ for o in {x[1] for x in pairs if x[0] == screen and x[2] == obj} for r in pairs[(screen, o, obj)]})
            summary.edges.append(Edge(gid, action_nodes[action], "interacts", INFERRED if action != "unknown" else UNRESOLVED, refs, f"{len(members_)}",
                                      {"relations": len(members_), "rule": "category inferred from the operation name", "members": [[s, o] for s, o in members_]}))
            total_edge_relations += len(members_)
    summary.partial = {"partial": False, "included_count": len(summary.nodes), "omitted_count": 0, "reason": ""}
    children: list[VisualProjection] = []
    omitted_parts = 0
    for action in ("read", "create", "update", "delete", "mixed", "unknown"):
        objs = sorted({obj for (_s, _o, obj) in pairs if action_of(obj) == action}, key=lambda o: (-sum(1 for k in pairs if k[2] == o), o))
        chunks = [objs[k:k + CHUNK_OBJECTS] for k in range(0, len(objs), CHUNK_OBJECTS)]
        for n, chunk in enumerate(chunks, start=1):
            if len(children) >= ctx.max_children:
                omitted_parts += 1
                continue
            part = action if len(chunks) == 1 else f"{action}-{n}of{len(chunks)}"
            children.append(_data_child(ctx, scope, pairs, action, chunk, part, summary, n, len(chunks)))
    _link_children(summary, children, "dense data-interaction map: screens grouped and relations aggregated per inferred action category (exact members in edge metadata); "
                   "expanded in the detail diagrams", len(group_nodes), omitted_parts,
                   relation_total=total_edge_relations, relation_pairs=len(pairs),
                   unexpanded_reason="child diagram bound reached (--max-children); the relations remain listed in the summary edge metadata" if omitted_parts else "")
    return [_finish_unresolved(summary), *[_finish_unresolved(c) for c in children]]


def _data_child(ctx: VisualContext, scope: dict, pairs: dict, action: str, objs: list[str], part: str, parent: VisualProjection, index: int, count: int) -> VisualProjection:
    child_scope = {**scope, "id": f"{scope['id']}:{part}", "part": part, "action": action}
    p = _projection(ctx, "data-interaction-map", f"Interacción con datos ({ACTION_LABEL[action]}): {scope['label']}", "functional", child_scope)
    group = Group(stable_id("G", "act", action), ACTION_LABEL[action], INFERRED if action != "unknown" else UNRESOLVED)
    p.groups = [group]
    wanted = set(objs)
    related = sorted({(s, o) for (s, o, obj) in pairs if obj in wanted})
    shown = related[: max(1, ctx.max_nodes - len(objs))]
    rest = related[len(shown):]
    screen_node: dict[tuple[str, str], str] = {}
    obj_node = {obj: stable_id("N", p.id, "obj", obj) for obj in objs}
    for obj in objs:
        refs = sorted({r for (s, o, ob), rr in pairs.items() if ob == obj for r in rr if str(r).startswith("DAO-")} or {r for (s, o, ob), rr in pairs.items() if ob == obj for r in rr[:1]})
        uses = sum(1 for (s, o, ob) in pairs if ob == obj)
        p.nodes.append(Node(obj_node[obj], obj, "data_object", CONFIRMED, refs, column=1, group=group.id, sublabel=f"{uses} pantalla(s)",
                            metadata={"action": action, "action_rule": "inferred from the operation name (H2 classifier)"}))
    for screen, owner in shown:
        module = ctx.module_by_path.get(owner)
        screen_node[(screen, owner)] = stable_id("N", p.id, "screen", screen, owner)
        p.nodes.append(Node(screen_node[(screen, owner)], screen, "screen", CONFIRMED,
                            sorted({r for (s, o, ob), rr in pairs.items() if (s, o) == (screen, owner) for r in rr[:2]}), column=0,
                            sublabel=f"proyecto {module.values['name']}" if module else "proyecto no identificado"))
    for (screen, owner, obj), refs in sorted(pairs.items()):
        if obj in wanted and (screen, owner) in screen_node:
            p.edges.append(Edge(screen_node[(screen, owner)], obj_node[obj], "invokes_data_object", CONFIRMED, refs, "usa"))
    if rest:
        rid = stable_id("N", p.id, "screens-rest")
        p.nodes.append(Node(rid, f"+{len(rest)} pantallas más", "aggregate", CONFIRMED, [ctx.manifest_ref], column=0,
                            metadata={"aggregate": True, "count": len(rest), "items": [s for s, _ in rest]}))
    p.partial = ({"partial": True, "included_count": len(shown) + len(objs), "omitted_count": len(rest), "reason": "more screens than the node bound: aggregated (names in the model JSON)"}
                 if rest else {"partial": False, "included_count": len(p.nodes), "omitted_count": 0, "reason": ""})
    return _detail(p, parent, index, count, action=action)
