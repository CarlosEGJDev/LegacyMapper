"""Bounded, deterministic fact selection per interpretation request (no source access, no provider access)."""
from __future__ import annotations

from collections import Counter, defaultdict

from .inventory import Inventory, Project, Solution
from .models import Fact, HUMAN_STATUS

MAX_CONTEXT_CHARS = 20000
MAX_FACT_CHARS = 420
VIEW_CHUNK = 20
MAX_VIEW_CHUNKS = 6
MAX_PROJECT_FLOWS = 10
MAX_DATA_FACTS = 45
MAX_PAIR_FACTS = 40
MAX_CHILD_FACTS = 100

_RANK = {"confirmed": 0, "inferred": 1, "unresolved": 2}


def _clip(text: str) -> str:
    return text if len(text) <= MAX_FACT_CHARS else text[:MAX_FACT_CHARS - 1].rstrip() + "…"


def _names(items, limit: int) -> str:
    items = list(items)
    shown = ", ".join(items[:limit])
    return shown + (f" y {len(items) - limit} más" if len(items) > limit else "")


def bound_facts(facts: list[Fact], max_chars: int = MAX_CONTEXT_CHARS) -> list[Fact]:
    """Keeps facts in order while the budget lasts; the omission is itself declared as an unresolved fact (never silent)."""
    kept, used = [], 0
    for fact in facts:
        cost = len(fact.text) + 60
        if used + cost > max_chars:
            break
        kept.append(fact)
        used += cost
    omitted = len(facts) - len(kept)
    if omitted:
        kept.append(Fact("", "unresolved", "unresolved", f"{omitted} hechos adicionales no se incluyeron por el límite de contexto."))
    return [Fact(f"F{i + 1:02d}", f.kind, f.certainty, f.text, f.evidence) for i, f in enumerate(kept)]


def _renumber(facts: list[Fact]) -> list[Fact]:
    return [Fact(f"F{i + 1:02d}", f.kind, f.certainty, f.text, f.evidence) for i, f in enumerate(facts)]


def project_views(inv: Inventory, pid: str) -> dict:
    """view name -> aggregated observable behavior (events, handlers, reached operations, other projects)."""
    views: dict[str, dict] = {}
    for f in inv.flows_owned.get(pid, []):
        v = views.setdefault(f["webform"] or f["view"], {"view": f["view"], "events": set(), "handlers": set(), "terminals": set(),
                                                           "projects": set(), "flows": 0, "certainty": "unresolved", "evidence": []})
        v["flows"] += 1
        v["events"].add(f["event"])
        v["handlers"].add(f["handler"])
        v["terminals"].update(f["terminals"])
        v["projects"].update(p for p in f["projects"] if p != pid)
        if _RANK[f["certainty"]] < _RANK[v["certainty"]]:
            v["certainty"] = f["certainty"]
        if f["id"]:
            v["evidence"].append(f["id"])
    return views


def project_facts(inv: Inventory, p: Project) -> list[Fact]:
    facts: list[Fact] = [Fact("", "name", "confirmed", f"Nombre del proyecto: {p.name}.", (p.id,))]
    if p.namespace:
        facts.append(Fact("", "name", "confirmed", f"Espacio de nombres raíz: {p.namespace}.", (p.id,)))
    if p.output_type:
        facts.append(Fact("", "structure", "confirmed", f"Tipo de salida del proyecto: {p.output_type}.", (p.id,)))
    sols = [inv_s.display for inv_s in inv.solutions if inv_s.id in p.solution_ids]
    if sols:
        facts.append(Fact("", "structure", "confirmed", f"Pertenece a las soluciones: {_names(sols, 6)}.", tuple(p.solution_ids)))
    if p.reference_names:
        facts.append(Fact("", "reference", "confirmed", f"Referencia a los proyectos: {_names(p.reference_names, 15)}.", (p.id,)))

    views = project_views(inv, p.id)
    ordered = sorted(views.values(), key=lambda v: (-v["flows"], v["view"].lower()))
    if ordered:
        facts.append(Fact("", "view", "confirmed",
                          f"Vistas con eventos observables ({len(ordered)}): {_names([v['view'] for v in ordered], 25)}.",
                          tuple(e for v in ordered[:25] for e in v["evidence"][:2])))
    flows = sorted(inv.flows_owned.get(p.id, []), key=lambda f: (-len(f["terminals"]), -f["depth"], f["view"].lower(), f["event"], f["id"] or ""))
    for f in flows[:MAX_PROJECT_FLOWS]:
        reach = f" y alcanza: {_names(f['terminals'], 4)}" if f["terminals"] else ""
        facts.append(Fact("", "flow", f["certainty"], _clip(f"En la vista {f['view']}, el evento {f['event'] or 'sin nombre'} ejecuta {f['handler'] or f['start'] or 'un manejador'}{reach}."),
                          (f["id"],) if f["id"] else ()))

    data = inv.data_by_project.get(p.id, [])
    sps = Counter(d["sp"] for d in data if d["sp"])
    if sps:
        top = [name for name, _ in sorted(sps.items(), key=lambda kv: (-kv[1], kv[0]))]
        facts.append(Fact("", "data", "confirmed", _clip(f"Procedimientos almacenados invocados: {_names(top, 20)}."),
                          tuple(d["id"] for d in data if d["sp"])[:20]))
    sql_ops = Counter(d["sql"] for d in data if d["sql"])
    if sql_ops:
        facts.append(Fact("", "data", "confirmed", "Operaciones SQL directas: " + ", ".join(sorted(sql_ops)) + ".", tuple(d["id"] for d in data if d["sql"])[:20]))
    if any(d["dynamic"] for d in data):
        facts.append(Fact("", "unresolved", "unresolved", "Existen consultas SQL construidas dinámicamente; su contenido no puede determinarse.",
                          tuple(d["id"] for d in data if d["dynamic"])[:10]))

    for label, table in (("Proyectos que lo invocan", inv.callers.get(p.id, {})), ("Proyectos a los que invoca", inv.callees.get(p.id, {}))):
        if table:
            rows = sorted(table.items(), key=lambda kv: (-len(kv[1]), inv.projects[kv[0]].display.lower()))
            text = ", ".join(f"{inv.projects[k].display} ({len(v)} llamadas)" for k, v in rows[:10]) + (f" y {len(rows) - 10} más" if len(rows) > 10 else "")
            cert = "confirmed" if any(c["status"] == "CONFIRMED" for v in table.values() for c in v) else "inferred"
            facts.append(Fact("", "relation", cert, _clip(f"{label}: {text}."), tuple(c["id"] for _, v in rows[:3] for c in v[:2] if c["id"])))
    unresolved = inv.unresolved_out.get(p.id, 0)
    if unresolved:
        facts.append(Fact("", "unresolved", "unresolved", f"{unresolved} llamadas salientes de este proyecto no pudieron resolverse a un destino.", ()))
    if not (ordered or data or inv.callers.get(p.id) or inv.callees.get(p.id) or p.reference_names):
        facts.append(Fact("", "unresolved", "unresolved", "El análisis no asoció eventos de interfaz, accesos a datos ni relaciones con otros proyectos.", ()))
    return bound_facts(facts)


def has_sufficient_evidence(facts: list[Fact]) -> bool:
    return any(f.kind in ("view", "flow", "data", "relation", "reference") for f in facts)


def view_chunks(inv: Inventory, p: Project) -> tuple[list[list[Fact]], int]:
    """Returns (chunks of view facts, number of views NOT interpreted because of the bounded context)."""
    views = sorted(project_views(inv, p.id).values(), key=lambda v: (-v["flows"], v["view"].lower()))
    base = Fact("", "name", "confirmed", f"Nombre del proyecto: {p.name}.", (p.id,))
    chunks: list[list[Fact]] = []
    limit = VIEW_CHUNK * MAX_VIEW_CHUNKS
    for start in range(0, min(len(views), limit), VIEW_CHUNK):
        facts = [base]
        for v in views[start:start + VIEW_CHUNK]:
            others = sorted(inv.projects[x].display for x in v["projects"] if x in inv.projects)
            parts = [f"Vista {v['view']}: eventos {_names(sorted(e for e in v['events'] if e), 8) or 'sin nombre'}",
                     f"manejadores {_names(sorted(h for h in v['handlers'] if h), 5) or 'no determinados'}"]
            if v["terminals"]:
                parts.append(f"alcanza {_names(sorted(v['terminals']), 5)}")
            if others:
                parts.append(f"recorre los proyectos {_names(others, 4)}")
            facts.append(Fact("", "view", v["certainty"], _clip("; ".join(parts) + "."), tuple(v["evidence"][:3])))
        chunks.append(_renumber(facts))
    return chunks, max(0, len(views) - limit)


def data_facts(inv: Inventory, p: Project) -> list[Fact]:
    data = inv.data_by_project.get(p.id, [])
    if not data:
        return []
    facts = [Fact("", "name", "confirmed", f"Nombre del proyecto: {p.name}.", (p.id,))]
    by_sp: dict[str, list] = defaultdict(list)
    for d in data:
        if d["sp"]:
            by_sp[d["sp"]].append(d)
    for sp, items in sorted(by_sp.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:MAX_DATA_FACTS]:
        where = sorted({f"{d['class']}.{d['method']}" for d in items if d["class"]})
        facts.append(Fact("", "data", "confirmed", _clip(f"El procedimiento {sp} se invoca desde {_names(where, 3) or 'un componente no determinado'}."),
                          tuple(d["id"] for d in items[:3] if d["id"])))
    by_sql: dict[str, list] = defaultdict(list)
    for d in data:
        if d["sql"]:
            by_sql[d["sql"]].append(d)
    for op, items in sorted(by_sql.items()):
        where = sorted({f"{d['class']}.{d['method']}" for d in items if d["class"]})
        facts.append(Fact("", "data", "confirmed", _clip(f"Operación SQL {op} ejecutada desde {_names(where, 4) or 'un componente no determinado'}."),
                          tuple(d["id"] for d in items[:3] if d["id"])))
    tx = sorted({d["class"] for d in data if d["kind"] == "transaction" and d["class"]})
    if tx:
        facts.append(Fact("", "data", "confirmed", _clip(f"Componentes con control de transacciones: {_names(tx, 12)}."), ()))
    if any(d["dynamic"] for d in data):
        facts.append(Fact("", "unresolved", "unresolved", "Existen consultas SQL construidas dinámicamente; su contenido no puede determinarse.", ()))
    return bound_facts(facts) if len(facts) > 1 else []


def flow_facts(inv: Inventory, s: Solution) -> list[Fact]:
    members = set(s.project_ids)
    rows = [(pair, rec) for pair, rec in inv.solution_pairs.items() if pair[0] in members or pair[1] in members]
    if not rows:
        return []
    rows.sort(key=lambda kv: (-(kv[1]["confirmed"] + kv[1]["inferred"]), inv.projects[kv[0][0]].display.lower(), inv.projects[kv[0][1]].display.lower()))
    facts = [Fact("", "name", "confirmed", f"Nombre de la solución: {s.name}.", (s.id,))]
    for (src, tgt), rec in rows[:MAX_PAIR_FACTS]:
        total = rec["confirmed"] + rec["inferred"]
        ex = "; ejemplos: " + ", ".join(f"{a} → {b}" for a, b in rec["samples"][:2]) if rec["samples"] else ""
        facts.append(Fact("", "relation", "confirmed" if rec["confirmed"] else "inferred",
                          _clip(f"El proyecto {inv.projects[src].display} invoca al proyecto {inv.projects[tgt].display} ({total} llamadas{ex})."), ()))
    return bound_facts(facts)


def semantic_fact_text(label: str, record: dict | None, reason: str = "") -> tuple[str, str]:
    """(text, certainty) of a child's accepted semantics, used as a fact for the parent level."""
    if not record:
        return _clip(f"{label}: sin interpretación disponible{(' (' + reason + ')') if reason else ''}."), "unresolved"
    claims = []
    for section in ("purpose", "summary", "responsibilities", "subsystems", "business_flow"):
        claims.extend(c for c in record["semantic"].get(section, []) if c["status"] != "UNRESOLVED")
    if not claims:
        return _clip(f"{label}: sin afirmaciones confirmadas ni inferidas."), "unresolved"
    first = claims[:2]
    cert = "confirmed" if all(c["status"] == "CONFIRMED" for c in first) else "inferred"
    return _clip(f"{label}: " + " ".join(f"[{HUMAN_STATUS[c['status']]}] {c['text']}" for c in first)), cert


def child_facts(parent_name_fact: Fact, children: list[tuple[str, str, str, tuple]]) -> list[Fact]:
    """children: (kind, text, certainty, evidence). Bounded; omissions are declared."""
    facts = [parent_name_fact] + [Fact("", k, c, t, e) for k, t, c, e in children[:MAX_CHILD_FACTS]]
    if len(children) > MAX_CHILD_FACTS:
        facts.append(Fact("", "unresolved", "unresolved", f"{len(children) - MAX_CHILD_FACTS} elementos adicionales no se incluyeron por el límite de contexto.", ()))
    return bound_facts(facts, MAX_CONTEXT_CHARS * 2)
