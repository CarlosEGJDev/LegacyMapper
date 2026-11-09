"""Deterministic human projection: navigable static HTML + one indexed PDF. Never calls a provider, never reads source.

Human prose shows only the states Confirmado / Inferido / No resuelto. Evidence identifiers, raw paths, line numbers and provider
diagnostics never appear here: they live in `ai/` and `internal/`.
"""
from __future__ import annotations

import posixpath
from html import escape
from pathlib import Path

from legacy_documenter.deliver import html as H
from legacy_documenter.deliver.markdown import Bullets, Callout, Heading, Para, Run, Table, slugify
from legacy_documenter.deliver.pdf import PdfDocument
from legacy_documenter.utils.atomic_write import atomic_write_bytes, atomic_write_text

from . import context as C
from . import planner as P
from .inventory import Inventory
from .models import CONTROLLED_ERROR, HUMAN_AND_MACHINE, HUMAN_STATUS, MACHINE_ONLY, PENDING, SECTIONS, UNRESOLVED_NO_SOLUTION, has_leak

STATE_LABEL = {
    HUMAN_AND_MACHINE: "Documentado", MACHINE_ONLY: "Solo conocimiento de máquina",
    UNRESOLVED_NO_SOLUTION: "Sin solución resoluble", CONTROLLED_ERROR: "Error controlado", PENDING: "Pendiente de interpretar",
    "DOCUMENTED": "Documentado"}
STATE_NOTE = {
    HUMAN_AND_MACHINE: "Este proyecto tiene documentación humana y conocimiento estructurado.",
    MACHINE_ONLY: "No hay suficientes afirmaciones respaldadas para documentación humana; el conocimiento estructurado sí existe.",
    UNRESOLVED_NO_SOLUTION: "El proyecto no figura en ninguna solución resoluble, por lo que no se interpretó. Se conserva y se declara como no resuelto.",
    CONTROLLED_ERROR: "La interpretación de este proyecto falló de forma controlada y no se inventó contenido.",
    PENDING: "La interpretación de este proyecto está pendiente; se completará al reanudar.",
}
SECTION_TITLE = {
    "purpose": "Qué hace", "responsibilities": "Responsabilidades", "consumers": "Quién lo usa", "dependencies": "De qué depende",
    "business_flow": "Flujo de negocio", "data_interactions": "Interacción con datos", "unresolved": "No resuelto", "behavior": "Comportamiento",
    "interactions": "Interacciones", "relations": "Relaciones entre proyectos", "summary": "Resumen", "subsystems": "Subsistemas",
    "data": "Datos", "solutions": "Soluciones principales", "interaction_paths": "Rutas de interacción", "cross_project": "Relaciones entre proyectos"}
FACT_LABEL = {"name": "Nombre", "structure": "Estructura", "reference": "Referencias", "view": "Vistas", "flow": "Flujo observado",
              "data": "Datos", "relation": "Relaciones", "unresolved": "No resuelto", "child": "Resumen"}
REASON_LABEL = {"NO_RESOLVABLE_SOLUTION": "ninguna solución resoluble lo incluye", "INSUFFICIENT_EVIDENCE": "evidencia insuficiente para interpretar",
                "NO_CONFIRMED_OR_INFERRED_CLAIMS": "no hubo afirmaciones respaldadas", "CHILD_REQUESTS_PENDING": "quedan solicitudes pendientes"}
CERT_LABEL = {"confirmed": "Confirmado", "inferred": "Inferido", "unresolved": "No resuelto"}
NAV = (("index.html", "Inicio", "home"), ("executive/index.html", "Ejecutivo", "executive"), ("system/index.html", "Sistema", "system"),
       ("solutions/index.html", "Soluciones", "solutions"), ("projects/index.html", "Proyectos", "projects"), ("views/index.html", "Vistas", "views"),
       ("flows/index.html", "Flujos", "flows"), ("data/index.html", "Datos", "data"), ("unresolved/index.html", "No resuelto", "unresolved"),
       ("technical/index.html", "Técnico", "technical"))


def _h(level: int, text: str) -> Heading:
    return Heading(level, [Run(text)], slugify(text))


def _p(text: str) -> Para:
    return Para([Run(text)])


def _safe(text: str) -> str:
    return "(contenido omitido: contiene identificadores internos)" if has_leak(text) else text


def claims_table(claims: list, caption: str = "") -> Table:
    rows = [[[Run(HUMAN_STATUS[c["status"]])], [Run(_safe((f"{c['subject']}: " if c.get("subject") else "") + c["text"]))]] for c in claims]
    return Table([[Run("Estado")], [Run("Afirmación")]], rows, caption)


def sections_blocks(record: dict | None, level: int = 2) -> list:
    out: list = []
    if not record:
        return out
    for section in SECTIONS.get(record["kind"], tuple(record["semantic"])):
        claims = record["semantic"].get(section) or []
        if claims:
            out += [_h(level, SECTION_TITLE.get(section, section)), claims_table(claims)]
    return out


class Site:
    def __init__(self, inv: Inventory, a: P.Assessment, records: list, synthetic: bool) -> None:
        self.inv, self.a, self.synthetic = inv, a, synthetic
        self.pages: dict[str, tuple[str, list, str, str]] = {}      # path -> (title, blocks, section key, extra html)
        self.pdf_blocks: list = []
        self.records = records

    def add(self, path: str, title: str, blocks: list, section: str, extra_before: str = "", extra_after: str = "") -> None:
        self.pages[path] = (title, blocks, section, (extra_before, extra_after))

    # ---------------------------------------------------------------- rendering
    def render_html(self, path: str) -> str:
        title, blocks, section, (before, after) = self.pages[path]
        root = posixpath.relpath(".", posixpath.dirname(path) or ".")
        root = "" if root == "." else root + "/"
        nav = "".join(f'<li><a href="{root}{href}"{" aria-current=page" if key == section else ""}>{label}</a></li>' for href, label, key in NAV)
        crumbs = f'<a href="{root}index.html">Inicio</a>' + ("" if path == "index.html" else f" › <span aria-current=\"page\">{escape(title)}</span>")
        banner = ""
        if self.synthetic:
            banner = ('<aside class="callout callout-unresolved"><p class="callout-title">Interpretación sintética de prueba</p>'
                      "<p>Esta documentación fue generada con un proveedor de pruebas sin IA: repite hechos del análisis y no es una interpretación real.</p></aside>")
        body = before + H.render_blocks(blocks, path) + after
        return (
            "<!doctype html>\n<html lang=\"es\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{escape(title)} · Conocimiento del sistema</title><link rel=\"stylesheet\" href=\"{root}assets/style.css\"></head>\n"
            f"<body><a class=\"skip\" href=\"#main\">Saltar al contenido</a>\n<header class=\"site\"><div class=\"brand\"><a href=\"{root}index.html\">LegacyMapper</a>"
            f"<span>Conocimiento del sistema legado</span></div><nav aria-label=\"Principal\"><ul>{nav}</ul></nav></header>\n"
            f"<nav class=\"crumbs\" aria-label=\"Ruta de navegación\">{crumbs}</nav>\n<div class=\"layout\"><main id=\"main\">\n{banner}{body}\n</main></div>\n"
            "<footer class=\"site\"><p class=\"muted\">Documentación generada de forma determinista a partir de conocimiento persistido; no se leyó código fuente "
            "ni se llamó a ningún proveedor para producir estas páginas. Estados: Confirmado, Inferido, No resuelto.</p></footer></body></html>\n")


def _project_link(inv: Inventory, a: P.Assessment, pid: str) -> Run:
    p = inv.projects[pid]
    return Run(p.display, href=f"projects/{p.slug}.html")


def system_map_svg(inv: Inventory, a: P.Assessment) -> str:
    cols, bw, gap, lh = 3, 300, 20, 16
    boxes, y_rows = [], []
    for s in inv.solutions:
        names = [inv.projects[pid].display for pid in s.project_ids]
        lines = names[:10] + ([f"… y {len(names) - 10} más"] if len(names) > 10 else [])
        boxes.append((s, lines))
    rows = [boxes[i:i + cols] for i in range(0, len(boxes), cols)]
    y, parts = 20, []
    for row in rows:
        h = 44 + max((len(l) for _, l in row), default=1) * lh
        for i, (s, lines) in enumerate(row):
            x = 20 + i * (bw + gap)
            parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{h}" rx="6" fill="#f3f4f6" stroke="#111827" stroke-width="1.5"/>')
            parts.append(f'<text x="{x + 10}" y="{y + 22}" font-family="Arial" font-size="14" font-weight="bold">{escape(s.display[:38])}</text>')
            for j, line in enumerate(lines):
                parts.append(f'<text x="{x + 14}" y="{y + 42 + j * lh}" font-family="Arial" font-size="11">{escape(line[:46])}</text>')
        y += h + gap
    width, height = 40 + cols * bw + (cols - 1) * gap, max(y, 60)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">'
            f'<title>Mapa del sistema</title><desc>Soluciones del sistema y los proyectos que contienen.</desc>' + "".join(parts) + "</svg>\n")


def build_site(inv: Inventory, a: P.Assessment, records: list, synthetic: bool) -> Site:
    site = Site(inv, a, records, synthetic)
    srec = a.system.item.record if a.system.item else None
    counts = {st: sum(1 for c in a.projects.values() if c.state == st) for st in (HUMAN_AND_MACHINE, MACHINE_ONLY, UNRESOLVED_NO_SOLUTION, CONTROLLED_ERROR, PENDING)}

    legend = Table([[Run("Estado")], [Run("Significado")]], [
        [[Run("Confirmado")], [Run("Lo respalda evidencia confirmada del análisis del código.")]],
        [[Run("Inferido")], [Run("Es una deducción razonable; no se presenta como hecho.")]],
        [[Run("No resuelto")], [Run("El análisis no pudo determinarlo. No significa ausencia ni obsolescencia.")]]])
    coverage_rows = [[[Run(STATE_LABEL[st])], [Run(str(n))]] for st, n in counts.items() if n or st != PENDING]
    coverage_table = Table([[Run("Cobertura de proyectos")], [Run("Cantidad")]], coverage_rows)

    # ---- index
    idx = [_h(1, "Conocimiento del sistema legado"),
           _p("Punto de entrada a la documentación del sistema completo. Primero lo general (resumen ejecutivo, mapa del sistema, soluciones) "
              "y después el detalle (proyectos, vistas, flujos, datos y lo que quedó sin resolver)."),
           _h(2, "Cómo leer los estados"), legend, _h(2, "Cobertura"), coverage_table,
           _h(2, "Secciones"), Bullets([[Run(label, href=href), Run(f" — {desc}")] for (href, label, _), desc in zip(NAV[1:], (
               "qué hace el sistema, en pocas líneas", "mapa y comportamiento general", "catálogo de soluciones", "catálogo de proyectos (todos)",
               "comportamiento de las pantallas", "relaciones entre proyectos", "interacción con datos y procedimientos",
               "lo que el análisis no pudo determinar", "detalle técnico y cobertura"))])]
    if not a.complete:
        idx.insert(2, Callout("unresolved", "Documentación parcial", [_p("Hay interpretación pendiente; esta documentación se completará al reanudar.")]))
    site.add("index.html", "Inicio", idx, "home")

    # ---- executive
    ex = [_h(1, "Resumen ejecutivo")]
    if srec:
        ex += sections_blocks(srec, 2)
    else:
        ex += [Callout("unresolved", "Sin interpretación del sistema", [_p("La interpretación a nivel de sistema no está disponible (pendiente o con error controlado).")])]
    ex += [_h(2, "Alcance de esta documentación"), coverage_table]
    site.add("executive/index.html", "Resumen ejecutivo", ex, "executive")

    # ---- system
    sysb = [_h(1, "Mapa del sistema"), _p("Cada recuadro es una solución y enumera los proyectos que contiene.")]
    after = [_h(2, "Interpretación del sistema")] + (sections_blocks(srec, 3) if srec else [_p("No disponible.")])
    fig = '<figure class="diagram"><img src="../diagrams/system-map.svg" alt="Mapa del sistema: soluciones y sus proyectos"><figcaption>Mapa del sistema</figcaption></figure>'
    site.add("system/index.html", "Sistema", sysb, "system", extra_after=fig + H.render_blocks(after, "system/index.html"))

    # ---- solutions
    rows = []
    for s in inv.solutions:
        u = a.solutions[s.id]
        rec = u.item.record if u.item else None
        first = next((c for sec in ("summary", "subsystems") for c in (rec["semantic"].get(sec, []) if rec else []) if c["status"] != "UNRESOLVED"), None)
        rows.append([[Run(s.display, href=f"solutions/{s.slug}.html")], [Run(str(len(s.project_ids)))], [Run(STATE_LABEL.get(u.state, u.state))],
                     [Run(_safe(first["text"]) if first else "—")]])
        blocks = [_h(1, f"Solución {s.display}"), Callout("note", "Estado", [_p(STATE_LABEL.get(u.state, u.state) + (f" ({u.reason})" if u.reason and u.state != "DOCUMENTED" else ""))])]
        blocks += sections_blocks(rec, 2)
        blocks += [_h(2, "Proyectos de la solución"), Table([[Run("Proyecto")], [Run("Cobertura")]], [
            [[_project_link(inv, a, pid)], [Run(STATE_LABEL[a.projects[pid].state])]] for pid in s.project_ids])]
        if u.flow:
            blocks.append(Bullets([[Run("Relaciones entre proyectos de esta solución", href=f"flows/{s.slug}.html")]]))
        site.add(f"solutions/{s.slug}.html", f"Solución {s.display}", blocks, "solutions")
    site.add("solutions/index.html", "Soluciones", [_h(1, "Catálogo de soluciones"),
             Table([[Run("Solución")], [Run("Proyectos")], [Run("Estado")], [Run("Resumen")]], rows)], "solutions")

    # ---- projects (every project, always)
    prow, vrows, drows = [], [], []
    for pc in a.projects.values():
        p = pc.project
        main = (pc.record("PROJECT") or [None])[0]
        sols = [inv.solutions[[x.id for x in inv.solutions].index(sid)] for sid in p.solution_ids]
        purpose = next((c for c in (main["semantic"].get("purpose", []) if main else []) if c["status"] != "UNRESOLVED"), None)
        prow.append([[Run(p.display, href=f"projects/{p.slug}.html")], [Run(", ".join(s.display for s in sols) or "—")],
                     [Run(STATE_LABEL[pc.state])], [Run(_safe(purpose["text"]) if purpose else "—")]])
        b = [_h(1, p.display), Callout("note", "Estado de cobertura: " + STATE_LABEL[pc.state], [_p(STATE_NOTE[pc.state] + (f" Motivo: {REASON_LABEL.get(pc.reason, pc.reason)}." if pc.reason else ""))])]
        if sols:
            b.append(Bullets([[Run("Solución: "), Run(s.display, href=f"solutions/{s.slug}.html")] for s in sols]))
        b += sections_blocks(main, 2)
        vrecs, drec = pc.record("VIEW"), (pc.record("DATA") or [None])[0]
        links = []
        if vrecs:
            links.append([Run("Comportamiento de las vistas", href=f"views/{p.slug}.html")])
        if drec:
            links.append([Run("Interacción con datos", href=f"data/{p.slug}.html")])
        if links:
            b += [_h(2, "Detalle por área"), Bullets(links)]
        rel = []
        for label, table in (("Proyectos que lo invocan", inv.callers.get(p.id, {})), ("Proyectos a los que invoca", inv.callees.get(p.id, {}))):
            if table:
                rel.append([Run(label + ": ")] + [r for pid in sorted(table, key=lambda x: inv.projects[x].display.lower())[:15] for r in (_project_link(inv, a, pid), Run("  "))])
        if rel:
            b += [_h(2, "Relaciones con otros proyectos"), Bullets(rel)]
        facts = C.project_facts(inv, p)
        b += [_h(2, "Detalle técnico"), Table([[Run("Tipo")], [Run("Certeza")], [Run("Hecho observado")]],
              [[[Run(FACT_LABEL.get(f.kind, f.kind))], [Run(CERT_LABEL[f.certainty])], [Run(_safe(f.text))]] for f in facts])]
        site.add(f"projects/{p.slug}.html", p.display, b, "projects")
        if vrecs:
            vb = [_h(1, f"Vistas de {p.display}")]
            for v in vrecs:
                vb += sections_blocks(v, 2)
            if pc.omitted_views:
                vb.append(Callout("unresolved", "Vistas sin interpretar", [_p(f"{pc.omitted_views} vistas no se interpretaron por el límite de contexto; no se omiten del análisis.")]))
            vb.append(Bullets([[Run("Volver al proyecto", href=f"projects/{p.slug}.html")]]))
            site.add(f"views/{p.slug}.html", f"Vistas de {p.display}", vb, "views")
            vrows.append([[Run(p.display, href=f"views/{p.slug}.html")], [Run(str(sum(len(x) for v in vrecs for x in v['semantic'].values())))]])
        if drec:
            site.add(f"data/{p.slug}.html", f"Datos de {p.display}", [_h(1, f"Interacción con datos de {p.display}")] + sections_blocks(drec, 2)
                     + [Bullets([[Run("Volver al proyecto", href=f"projects/{p.slug}.html")]])], "data")
            drows.append([[Run(p.display, href=f"data/{p.slug}.html")]])
    site.add("projects/index.html", "Proyectos", [_h(1, "Catálogo de proyectos"), _p("Todos los proyectos descubiertos aparecen aquí con su estado de cobertura."),
             Table([[Run("Proyecto")], [Run("Solución")], [Run("Cobertura")], [Run("Qué hace")]], prow)], "projects")
    site.add("views/index.html", "Vistas", [_h(1, "Comportamiento de las vistas"), _p("Proyectos con interfaz y la explicación de sus pantallas.")]
             + ([Table([[Run("Proyecto")], [Run("Afirmaciones")]], vrows)] if vrows else [_p("No hay vistas interpretadas.")]), "views")
    site.add("data/index.html", "Datos", [_h(1, "Interacción con datos y procedimientos")]
             + ([Table([[Run("Proyecto")]], drows)] if drows else [_p("No hay interacciones de datos interpretadas.")]), "data")

    # ---- flows
    frows = []
    for s in inv.solutions:
        u = a.solutions[s.id]
        frec = u.flow.record if u.flow else None
        if frec:
            frows.append([[Run(s.display, href=f"flows/{s.slug}.html")]])
            site.add(f"flows/{s.slug}.html", f"Flujos de {s.display}", [_h(1, f"Relaciones entre proyectos de {s.display}")] + sections_blocks(frec, 2), "flows")
    site.add("flows/index.html", "Flujos", [_h(1, "Flujos entre proyectos")] + ([Table([[Run("Solución")]], frows)] if frows else [_p("No hay relaciones entre proyectos interpretadas.")]), "flows")

    # ---- unresolved
    ub: list = [_h(1, "Áreas no resueltas"), _p("Lo que el análisis no pudo determinar. Ausencia de evidencia no significa que algo no exista ni que esté obsoleto.")]
    claims = [(rec["label"], c) for rec in records for sec, cs in rec["semantic"].items() for c in cs if c["status"] == "UNRESOLVED"]
    if claims:
        ub += [_h(2, "Afirmaciones no resueltas"), Table([[Run("Ámbito")], [Run("Afirmación")]], [[[Run(label)], [Run(_safe(c["text"]))]] for label, c in claims])]
    exc = [pc for pc in a.projects.values() if pc.state != HUMAN_AND_MACHINE]
    if exc:
        ub += [_h(2, "Proyectos sin documentación humana completa"), Table([[Run("Proyecto")], [Run("Estado")], [Run("Motivo")]],
               [[[Run(pc.project.display, href=f"projects/{pc.project.slug}.html")], [Run(STATE_LABEL[pc.state])], [Run(REASON_LABEL.get(pc.reason, pc.reason) or "—")]] for pc in exc])]
    site.add("unresolved/index.html", "No resuelto", ub, "unresolved")

    # ---- technical
    site.add("technical/index.html", "Técnico", [_h(1, "Detalle técnico"), _p("Cada página de proyecto termina con su tabla «Detalle técnico» (hechos observados con su certeza). "
             "El conocimiento estructurado completo, con trazabilidad a la evidencia, está en la carpeta de conocimiento para máquinas."),
             Table([[Run("Proyecto")], [Run("Cobertura")]], [[[Run(pc.project.display, href=f"projects/{pc.project.slug}.html")], [Run(STATE_LABEL[pc.state])]] for pc in a.projects.values()])], "technical")

    # ---- PDF source blocks (macro first, micro second)
    site.pdf_blocks = (site.pages["executive/index.html"][1] + [_h(1, "Sistema")] + after
                       + [_h(1, "Catálogo de soluciones")] + [x for s in inv.solutions for x in site.pages[f"solutions/{s.slug}.html"][1][:2] + sections_blocks(
                           a.solutions[s.id].item.record if a.solutions[s.id].item else None, 3)]
                       + [_h(1, "Catálogo de proyectos")] + [x for pc in a.projects.values() for x in (_h(2, pc.project.display), _p(STATE_LABEL[pc.state] + ". " + STATE_NOTE[pc.state]))
                                                             + tuple(sections_blocks((pc.record("PROJECT") or [None])[0], 3)[:4])]
                       + site.pages["unresolved/index.html"][1])
    return site


def write_site(site: Site, out: Path, title: str = "Conocimiento del sistema legado") -> list[str]:
    human = out / "human"
    written: list[str] = []
    for path in sorted(site.pages):
        target = human / path
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(target, site.render_html(path))
        written.append(f"human/{path}")
    atomic_write_text(human / "assets" / "style.css", H.CSS)
    atomic_write_text(human / "diagrams" / "system-map.svg", system_map_svg(site.inv, site.a))
    written += ["human/assets/style.css", "human/diagrams/system-map.svg"]
    pdf = PdfDocument(title, footer_title=title)
    pdf.reserve_front()
    pdf.blocks(site.pdf_blocks)
    pdf.fill_front("Documentación generada de forma determinista", [f"Proyectos: {len(site.a.projects)}", f"Soluciones: {len(site.inv.solutions)}"])
    data, _stats = pdf.render()
    atomic_write_bytes(human / "IST_Complete.pdf", data)
    written.append("human/IST_Complete.pdf")
    return written
