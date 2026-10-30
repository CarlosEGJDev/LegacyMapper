"""Human-facing rendering of a `BehavioralDocument` (post-V5 H4-R4): HTML (primary) and PDF (secondary) from one block model.

Pure function of the structured explanation: the same explanation always renders to the same bytes. Reading order follows the
macro -> micro hierarchy; technical detail sits in collapsible blocks (progressive disclosure).
"""
from __future__ import annotations

import re
from collections import Counter
from xml.sax.saxutils import escape

from legacy_documenter.deliver import html as H
from legacy_documenter.deliver.markdown import Bullets, Callout, Details, Figure, Heading, Para, Run, Table, plain
from legacy_documenter.deliver.pdf import PdfDocument

from . import svgtext
from .humanize import humanize_blocks
from .explain import EFFECT_ES
from .template import HumanTemplate, discover
from .usage import USAGE_ES
from .model import (
    CONFIRMED, INFERRED, MODULE_NONE, UNRESOLVED, WIREFRAME_UNAVAILABLE, ActionExplanation, BehavioralDocument, Claim, ViewExplanation, ViewInvocation,
)

STATUS_ES = H.STATUS_TEXT
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def esc(text: object) -> str:
    return escape(_CTRL.sub("", str(text)))


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def claims_table(claims: list[Claim], *, with_basis: bool = False) -> list:
    if not claims:
        return []
    header = [[Run("Afirmación")], [Run("Estado")]] + ([[Run("Base")]] if with_basis else [])
    rows = []
    for c in claims:
        row = [[Run(c.text)], [Run(STATUS_ES.get(c.status, c.status))]]
        if with_basis:
            row.append([Run(c.basis or "—")])
        rows.append(row)
    return [Table(header, rows)]


_CARD_KIND = {CONFIRMED: "note", INFERRED: "semantic", UNRESOLVED: "unresolved"}
_CARD_ORDER = (CONFIRMED, INFERRED, UNRESOLVED)
_CARD_TITLE = {CONFIRMED: "Confirmado", INFERRED: "Inferido", UNRESOLVED: "No resuelto"}


def claim_cards(claims: list[Claim]) -> list:
    """Human reading of claims: one coloured card per state (blue Confirmado / orange Inferido / red No resuelto), known behaviour first.
    The basis and source references of each claim stay in the model (ai/, internal/); they are never rendered here."""
    out: list = []
    for status in _CARD_ORDER:
        texts = list(dict.fromkeys(c.text for c in claims if c.status == status))
        if texts:
            out.append(Callout(_CARD_KIND[status], _CARD_TITLE[status], [Para([Run(t)]) for t in texts]))
    rest = [c for c in claims if c.status not in _CARD_ORDER]
    if rest:
        out.append(Callout("note", STATUS_ES.get(rest[0].status, rest[0].status), [Para([Run(c.text)]) for c in rest]))
    return out


def claims_with_backing(claims: list[Claim], backing: bool = True) -> list:
    """Human document: the claims as state cards only. Their basis is machine traceability and lives in ai/ and internal/."""
    return claim_cards(claims)


def step_label(label: str) -> str:
    """A path step as the human reads it: the symbol name without the deterministic support id (`(DAO-0001)`)."""
    return re.sub(r"\s*\(DAO-\d+\)", "", label)


def _path_svg(action: ActionExplanation) -> tuple[str, int, int]:
    """Vertical chain of the confirmed technical path. Boxes grow to contain their (wrapped) labels."""
    steps = action.technical_path.steps if action.technical_path else []
    if not steps:
        return "", 0, 0
    kind_es = {"view": "Vista", "event": "Evento", "handler": "Manejador", "method": "Método", "data_operation": "Operación de datos",
               "procedure": "Procedimiento / destino de datos", "class": "Clase"}
    w, gap, pad = 700, 22, 10
    inner = w - 24 - 20 - 20
    title = svgtext.wrap(action.action, w - 24, 14, bold=True)
    y = 18.0 + len(title) * svgtext.line_height(14)
    head = y + 30
    boxes = []
    for st in steps:
        lines = svgtext.wrap(step_label(st["label"]), inner, 12)
        h = round(pad + svgtext.line_height(10) + len(lines) * svgtext.line_height(12) + pad)
        boxes.append((st, lines, max(46, h)))
    height = int(head + sum(h for _s, _l, h in boxes) + gap * (len(boxes) - 1) + 24)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{height}" viewBox="0 0 {w} {height}" font-family="Arial, Helvetica, sans-serif" font-size="11">',
           f"<title>{esc('Ruta técnica: ' + action.action)}</title>", f'<rect x="0" y="0" width="{w}" height="{height}" fill="#ffffff"/>',
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#1e3a8a"/></marker></defs>']
    ty = 18.0
    for line in title:
        ty += svgtext.line_height(14)
        out.append(f'<text x="{w // 2}" y="{ty:.0f}" font-size="14" font-weight="bold" text-anchor="middle">{esc(line)}</text>')
    out.append(f'<text x="{w // 2}" y="{ty + 18:.0f}" font-size="11" fill="#4b5563" text-anchor="middle">Ruta técnica (cada caja indica su estado)</text>')
    y = head
    for i, (st, lines, h) in enumerate(boxes):
        status = st.get("status", CONFIRMED)
        stroke, fill, dash = {"CONFIRMED": ("#1e3a8a", "#eef2ff", ""), "INFERRED": ("#b45309", "#fffbeb", "7 4"), "UNRESOLVED": ("#b91c1c", "#fef2f2", "2 3")}.get(
            status, ("#1e3a8a", "#eef2ff", ""))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="12" y="{y:.0f}" width="{w - 24}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>')
        out.append(f'<text x="22" y="{y + pad + 9:.0f}" font-size="10" fill="#4b5563">{esc(kind_es.get(st["kind"], st["kind"]))}</text>')
        out.append(f'<text x="{w - 22}" y="{y + pad + 9:.0f}" font-size="10" font-weight="bold" fill="{stroke}" text-anchor="end">'
                   f'{esc(STATUS_ES.get(status, status).split(" (")[0].upper())}</text>')
        ly = y + pad + 9
        for line in lines:
            ly += svgtext.line_height(12)
            out.append(f'<text x="22" y="{ly:.0f}" font-size="12">{esc(line)}</text>')
        if i < len(boxes) - 1:
            out.append(f'<path d="M{w // 2} {y + h:.0f} L{w // 2} {y + h + gap:.0f}" fill="none" stroke="#1e3a8a" stroke-width="1" marker-end="url(#a)"/>')
        y += h + gap
    out.append("</svg>")
    return "\n".join(out) + "\n", w, height


def _cross_svg(view: ViewExplanation) -> tuple[str, int, int]:
    left_all = sorted({i.source_view.rsplit("\\", 1)[-1] for i in view.reached_by})
    right_all = sorted({i.target_view.rsplit("\\", 1)[-1] for i in view.reaches})
    left, right = left_all[:6], right_all[:6]
    if not left and not right:
        return "", 0, 0
    bw, gap = 236, 12

    def side(names):
        return [(n, svgtext.wrap(n, bw - 20, 11)) for n in names]

    def heights(items):
        return [max(36, round(20 + len(lines) * svgtext.line_height(11))) for _n, lines in items]
    lbox, rbox = side(left), side(right)
    lh, rh = heights(lbox), heights(rbox)
    col = max(sum(lh) + gap * max(0, len(lh) - 1), sum(rh) + gap * max(0, len(rh) - 1), 48)
    w = 12 + bw + 70 + 230 + 70 + bw + 12
    top = 78
    height = int(top + col + 46)
    cx = 12 + bw + 70
    center_lines = svgtext.wrap(view.name, 230 - 20, 12, bold=True)
    ch = max(48, round(24 + len(center_lines) * svgtext.line_height(12)))
    mid = top + col / 2 - ch / 2
    title = svgtext.wrap(f"Quién abre «{view.name}» y qué abre", w - 24, 13, bold=True)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{height}" viewBox="0 0 {w} {height}" font-family="Arial, Helvetica, sans-serif" font-size="11">',
           f"<title>{esc('Invocaciones de ' + view.name)}</title>", f'<rect x="0" y="0" width="{w}" height="{height}" fill="#ffffff"/>',
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#1e3a8a"/></marker></defs>']
    ty = 14.0
    for line in title:
        ty += svgtext.line_height(13)
        out.append(f'<text x="{w // 2}" y="{ty:.0f}" font-size="13" font-weight="bold" text-anchor="middle">{esc(line)}</text>')
    out.append(f'<text x="{w // 2}" y="{ty + 17:.0f}" font-size="10" fill="#4b5563" text-anchor="middle">Invocaciones por literal url=… (confirmadas en el código): a la izquierda quienes la abren, a la derecha lo que abre</text>')
    out.append(f'<rect x="{cx}" y="{mid:.0f}" width="230" height="{ch}" rx="6" fill="#eef2ff" stroke="#1e3a8a" stroke-width="3"/>')
    out.append(f'<text x="{cx + 10}" y="{mid + 16:.0f}" font-size="10" fill="#4b5563">Esta vista</text>')
    cy = mid + 16
    for line in center_lines:
        cy += svgtext.line_height(12)
        out.append(f'<text x="{cx + 10}" y="{cy:.0f}" font-size="12" font-weight="bold">{esc(line)}</text>')

    def column(items, heights_, x0, to_center):
        y0 = top + (col - (sum(heights_) + gap * max(0, len(heights_) - 1))) / 2
        for (name, lines), h in zip(items, heights_):
            out.append(f'<rect x="{x0}" y="{y0:.0f}" width="{bw}" height="{h}" rx="6" fill="#ffffff" stroke="#1e3a8a" stroke-width="2"/>')
            ly = y0 + 10
            for line in lines:
                ly += svgtext.line_height(11)
                out.append(f'<text x="{x0 + 10}" y="{ly:.0f}" font-size="11">{esc(line)}</text>')
            if to_center:
                out.append(f'<path d="M{x0 + bw} {y0 + h / 2:.0f} L{cx} {mid + ch / 2:.0f}" fill="none" stroke="#1e3a8a" stroke-width="1" marker-end="url(#a)"/>')
            else:
                out.append(f'<path d="M{cx + 230} {mid + ch / 2:.0f} L{x0} {y0 + h / 2:.0f}" fill="none" stroke="#1e3a8a" stroke-width="1" marker-end="url(#a)"/>')
            y0 += h + gap
    column(lbox, lh, 12, True)
    column(rbox, rh, w - 12 - bw, False)
    notes = []
    if len(left_all) > 6:
        notes.append(f"+ {len(left_all) - 6} vistas más la abren (ver la tabla de invocaciones)")
    if len(right_all) > 6:
        notes.append(f"+ {len(right_all) - 6} destinos más")
    for k, note in enumerate(notes):
        out.append(f'<text x="{w // 2}" y="{height - 10 - 14 * (len(notes) - 1 - k)}" font-size="10" fill="#4b5563" text-anchor="middle">{esc(note)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n", w, height


def _fig(title: str, rel: str, w: int, h: int, kind: str, nodes: int = 0) -> Figure:
    return Figure(title=title, svg=rel, model=rel, page=rel, kind=kind, scope_label="", nodes=nodes, edges=0, width=w, height=h,
                  status_counts={}, partial={"partial": False}, unresolved_nodes=0)


class _Marker:
    """AI narrative without a per-block label: the single opening notice says the document is an AI-assisted interpretation."""

    def __init__(self, enabled: bool = True) -> None:
        pass

    def callout(self, claims: list[Claim]) -> list:
        return ai_callout(claims)


AI_BASIS_SENTENCE = "La documentación se construyó a partir del análisis de IST y de una interpretación de IA validada contra el análisis disponible."
NO_AI_SENTENCE = ("Este documento no incluye interpretaciones de IA: no se ejecutó una corrida de IA para esta generación y el texto proviene solo de "
                  "evidencia determinista.")


def provenance_sentence(manifest: dict, brief: bool = False) -> str:
    """One sentence on where the text comes from. Provider, model and request details belong to ai/ and internal/, not to the human reader."""
    return "" if manifest.get("status") == "COMPLETED" else NO_AI_SENTENCE      # with AI the single "Interpretación asistida por IA" note says it


def ai_callout(claims: list[Claim], title: str = "") -> list:
    """AI narrative as readable paragraphs with no badge: the notice at the start of the document says it once. The underlying status
    stays AI_INTERPRETATION (data-status in HTML, status in the structured model)."""
    if not claims:
        return []
    return [Callout("ai", title, [Para([Run(c.text)]) for c in claims])]


SECTION_TITLES = {
    "solution": "La solución", "project": "El proyecto", "modules": "Estructura de módulos", "important_views": "Vistas importantes",
    "view_chapters": "Vistas explicadas", "cross_view": "Comportamiento entre vistas", "data": "Datos y persistencia",
    "usage": "Uso observable de los componentes", "unresolved": "Limitaciones conocidas", "appendix": "Apéndice",
}


_PURPOSE_SHORT = {"Con acciones que llaman a lógica de negocio no resuelta (propósito no determinado)": "Con acciones que llaman a lógica de negocio",
                  "Con acciones; destino de datos no resuelto": "Con acciones",
                  "Sin eventos propios; propósito no determinado": "Sin eventos propios"}


def catalog_purpose(row: dict) -> str:
    """Catalogue wording for humans: what the view appears to do, without restating what could not be determined."""
    return _PURPOSE_SHORT.get(row["purpose"], row["purpose"])


def catalog_reached(row: dict) -> str:
    return "—" if row["reached"].startswith("no resuelto") else row["reached"]


def _short(name: str) -> str:
    return name.rsplit("\\", 1)[-1]


def _names(names: list[str], limit: int = 8) -> str:
    uniq = list(dict.fromkeys(names))
    return ", ".join(uniq[:limit]) + (" y otras" if len(uniq) > limit else "")


def _one_line(v: ViewExplanation, mk: _Marker) -> list:
    if v.ai_narrative.get("simple_summary"):
        return mk.callout(v.ai_narrative["simple_summary"])
    det = next((c for c in v.what_it_does if c.status == INFERRED), None) or next((c for c in v.what_it_does if c.status == CONFIRMED), None)
    return (claim_cards([det]) if det else []) + [Para([Run("No hay interpretación de IA para esta vista (no se ejecutó o fue rechazada por la validación).")], cls="technical")]


def _what_it_does(v: ViewExplanation, mk: _Marker, executive: bool) -> list:
    b: list = []
    ai = v.ai_narrative
    if ai.get("observable_purpose"):
        b += mk.callout(ai["observable_purpose"])
    if ai.get("inputs") and not executive:
        b += [Heading(5, [Run("Qué información recibe")], "")] + mk.callout(ai["inputs"])
    if not executive:
        b.append(Details("Afirmaciones deterministas sobre la vista", claim_cards(v.what_it_does + v.receives)))
    return b


def _usage(v: ViewExplanation, mk: _Marker, executive: bool) -> list:
    u = v.usage
    if not u:
        return []
    b: list = [Para([Run(u["label"], bold=True), Run(". " + u["wording"])])]
    openers = _names([_short(i.source_view) for i in v.reached_by if i.target_exists and "backup" not in i.source_view.lower()])
    if openers and not executive:
        b.append(Para([Run("La abren: " + openers + ".")]))
    return b


def _ui(v: ViewExplanation, assets: dict) -> list:
    b: list = []
    if v.ui and v.ui.status == "DOCUMENTARY_RECONSTRUCTION":
        rel = f"assets/{slug(v.name)}-wireframe.svg"
        assets[rel] = (v.ui.svg, "wireframe")
        fidelity_es = {"STRUCTURE_ONLY": "solo estructura", "STYLE_PARTIAL": "estilo parcial", "STYLE_HIGH_CONFIDENCE": "estilo con alta confianza"}[v.ui.fidelity]
        b.append(Para([Run(f"RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE PRODUCCIÓN. Fidelidad visual: {fidelity_es}.", bold=True)], cls="caption"))
        b.append(_fig(f"Reconstrucción documental de {v.name}", rel, 760, 500, "wireframe", len(v.ui.controls)))
    else:
        b.append(Para([Run(WIREFRAME_UNAVAILABLE + (": " + v.ui.reason if v.ui else ""), code=True)]))
    return b


def _flow(v: ViewExplanation, assets: dict) -> list:
    from . import flowboxes
    b: list = []
    flow = flowboxes.view_flow(v)
    if flow:
        rel = f"assets/{slug(v.name)}-flujo.svg"
        svg, fw, fh = flowboxes.render(flow)
        assets[rel] = (svg, "flow")
        b.append(_fig(f"Flujo simple de {v.name}", rel, fw, fh, "box-flow", len(flow["rows"])))
    for a in v.actions:
        if a.technical_path and len(a.technical_path.steps) > 2:
            rel = f"assets/{slug(v.name)}-{slug(a.action)}-ruta.svg"
            psvg, pw, ph = _path_svg(a)
            assets[rel] = (psvg, "path")
            fig = _fig(f"Ruta: {a.action}", rel, pw, ph, "behavior-path", len(a.technical_path.steps))
            fig.children = [(step_label(st["label"]), st.get("status", CONFIRMED), st["kind"]) for st in a.technical_path.steps]
            b.append(Details(f"Ruta técnica detallada — {a.action}", [fig]))
    return b


def route_text(a: ActionExplanation) -> str:
    """`a → b → c` with the real symbol names of the confirmed path; an open end is written as `destino posterior indeterminado`."""
    steps = a.technical_path.steps if a.technical_path else []
    handler = (a.handler or "").lower()
    trigger = f"{a.trigger}.{a.event}" if a.trigger and a.trigger != "MyBase" else ""
    chain: list[str] = [x for x in (trigger, a.handler) if x]
    for st in steps:
        label = step_label(st["label"]) if st["kind"] != "view" else ""
        low = label.lower()
        if not label or low.startswith("mybase.") or (handler and low.endswith("." + handler)) or low in {c.lower() for c in chain}:
            continue
        chain.append(label)
    if not any(st["kind"] in ("procedure", "data_operation") for st in steps):
        chain.append("destino posterior indeterminado")
    return " → ".join(chain)


def _actions(v: ViewExplanation, mk: _Marker, executive: bool) -> list:
    b: list = []
    if executive:
        notes = [n for a in v.actions for n in v.ai_action_notes.get(a.handler, [])]
        if notes:
            return mk.callout(notes)
        return [Bullets([[Run(a.action)] for a in v.actions[:8]])] if v.actions else []
    if v.actions:
        b.append(Table([[Run("Acción")], [Run("Ruta")]], [[[Run(a.action)], [Run(route_text(a), code=True)]] for a in v.actions]))
    for a in v.actions:
        notes = v.ai_action_notes.get(a.handler)
        if notes:
            b.append(Heading(5, [Run(a.action)], ""))
            b += mk.callout(notes)
        for r in a.result:
            b.append(Para([Run(r.text)]))
    return b


def _data(v: ViewExplanation, mk: _Marker, executive: bool) -> list:
    b: list = []
    if v.ai_narrative.get("data_behavior"):
        b += mk.callout(v.ai_narrative["data_behavior"])
    all_data = [d for a in v.actions for d in a.data]
    if all_data and not b:
        reads = list(dict.fromkeys(d.object_name for d in all_data if d.effect == "read"))
        writes = list(dict.fromkeys(d.object_name for d in all_data if d.effect in ("create", "update", "delete", "mixed")))
        parts = []
        if reads:
            parts.append("consulta datos con " + ", ".join(f"«{x}»" for x in reads))
        if writes:
            parts.append("persiste cambios con " + ", ".join(f"«{x}»" for x in writes))
        if parts:
            b.append(Para([Run("Esta vista " + " y ".join(parts) + " (tipo de efecto deducido del nombre técnico).")]))
    if all_data and not executive:
        uniq = {x.object_name: x for x in all_data}
        b.append(Table([[Run("Dato / operación")], [Run("Efecto")], [Run("Alcanzado por")]],
                       [[[Run(k, code=True)], [Run(EFFECT_ES.get(d.effect, d.effect))], [Run(d.via or "—", code=True)]] for k, d in uniq.items()]))
    return b


def _classes(v: ViewExplanation, mk: _Marker) -> list:
    b: list = []
    if v.classes:
        role_es = {"ui_code_behind": "UI / code-behind", "business_or_data_access": "negocio o acceso a datos"}
        b.append(Table([[Run("Clase")], [Run("Rol observado")]], [[[Run(c.name, code=True)], [Run(role_es.get(c.role, c.role))]] for c in v.classes]))
    if v.ai_narrative.get("related_classes"):
        b += mk.callout(v.ai_narrative["related_classes"])
    return b


def _invocations(v: ViewExplanation, assets: dict) -> list:
    b: list = []
    live = [i for i in v.reached_by if i.target_exists]
    if live:
        b.append(Para([Run("La abren: " + _names([_short(i.source_view) for i in live]) + ".")]))
    elif not v.reached_by:
        b.append(Para([Run("Ninguna otra vista la abre mediante un literal de URL.")]))
    if v.reaches:
        b.append(Para([Run("Abre: " + _names(sorted({_short(i.target_view) for i in v.reaches})) + ".")]))
    svg, cw, ch = _cross_svg(v)
    if svg:
        rel = f"assets/{slug(v.name)}-invocaciones.svg"
        assets[rel] = (svg, "cross")
        b.append(_fig(f"Invocaciones de {v.name}", rel, cw, ch, "view-invocations"))
    return b


def _messages(v: ViewExplanation, mk: _Marker) -> list:
    b: list = []
    literal = [m for m in v.messages if m.kind in ("msgbox", "alert")]
    errors = [m for m in v.messages if m.kind == "error_display"]
    if literal:
        b.append(Table([[Run("Tipo")], [Run("Texto literal en el código")], [Run("Evento / método")]],
                       [[[Run("MsgBox" if m.kind == "msgbox" else "alert")], [Run(m.text or "(sin literal)")], [Run(m.event, code=True)]] for m in literal[:12]]))
    if errors:
        b.append(Para([Run("También puede mostrar errores al usuario (texto no estático).")]))
    if v.ai_narrative.get("messages_popups"):
        b += mk.callout(v.ai_narrative["messages_popups"])
    return b


_GENERIC_BASIS = {"análisis estático", "ninguna evidencia declara el propósito de negocio"}


def _knowledge(v: ViewExplanation, mk: _Marker) -> list:
    """Known behaviour is told in the chapter itself; what is known / inferred / undetermined about this view is kept, collapsed (HTML only)."""
    def specific(cs):
        return [c for c in cs if c.basis not in _GENERIC_BASIS]
    inner: list = claim_cards([c for c in specific(v.unresolved.known) if "tienen una ruta confirmada" not in c.text]
                              + specific(v.unresolved.inferred) + specific(v.unresolved.unresolved))
    extra = specific(v.ai_narrative.get("known", []) + v.ai_narrative.get("inferred", []) + v.ai_narrative.get("unresolved", []))
    if extra:
        inner += ai_callout(extra)
    return [Details("Detalle de lo conocido y lo indeterminado de esta vista", inner)] if inner else []


def _evidence(v: ViewExplanation, mk: _Marker) -> list:
    """Evidence references and markup controls are machine traceability: they live in ai/ and internal/, never in the human document."""
    return []


PART_TITLES = {"one_line": "En una frase", "what_it_does": "Qué hace y cómo se usa", "usage": "Uso observable", "ui": "Reconstrucción visual aproximada",
               "flow": "Flujo técnico simple", "actions": "Acciones principales", "data": "Datos y persistencia", "classes": "Clases relacionadas",
               "invocations": "Vistas y ventanas relacionadas (quién la abre, qué abre)", "messages": "Mensajes",
               "knowledge": "Lo conocido y lo indeterminado", "evidence": "Evidencia técnica"}


def view_chapter(v: ViewExplanation, assets: dict, n: int, template: HumanTemplate, section_no: int = 4) -> list:
    """One detailed view in the template's chapter order: simple explanation first, technical evidence last."""
    b: list = []
    mk = _Marker(template.layout.get("ai_marker") != "none")
    ex = template.manifest.get("audience") == "executive"
    makers = {"one_line": lambda: _one_line(v, mk), "what_it_does": lambda: _what_it_does(v, mk, ex), "usage": lambda: _usage(v, mk, ex),
              "ui": lambda: _ui(v, assets), "flow": lambda: [] if ex else _flow(v, assets), "actions": lambda: _actions(v, mk, ex),
              "data": lambda: _data(v, mk, ex), "classes": lambda: _classes(v, mk), "invocations": lambda: _invocations(v, assets),
              "messages": lambda: _messages(v, mk), "knowledge": lambda: _knowledge(v, mk)}
    bodies = {part: makers[part]() for part in template.chapter_parts if part in makers}     # the backing block is built last, after the AI blocks
    if "evidence" in template.chapter_parts:
        bodies["evidence"] = _evidence(v, mk)
    for part in template.chapter_parts:
        if part == "title":
            b.append(Heading(3, [Run(f"{section_no}.{n} {v.name}" + (f" — {v.title}" if v.title else ""))], f"vista-{slug(v.name)}", "view-title"))
            b.append(Para([Run(f"{'Pantalla (control de usuario)' if v.kind == 'user_control' else 'Página'}")], cls="caption"))
            continue
        body = bodies.get(part)
        if body:
            b.append(Heading(4, [Run(template.label(f"part_{part}", PART_TITLES[part]))], ""))
            b += body
    return b


def compose(doc: BehavioralDocument, template: HumanTemplate | None = None) -> tuple[list, dict]:
    """Returns (blocks, assets). Section order and visibility come from the template; content comes from the validated model only."""
    template = template or discover("human/default")
    assets: dict[str, tuple[str, str]] = {}
    sol, proj, mod = doc.solution, doc.project, doc.module
    ran = doc.ai_manifest.get("status") == "COMPLETED"
    executive = template.manifest.get("audience") == "executive"
    blocks: list = []
    number = 0
    for sec in template.sections:
        if sec == "cover":
            blocks += [Heading(1, [Run(f"Entendiendo {proj.name}")], "portada", "doc-title"),
                       Para([Run(f"Guía del comportamiento de las vistas del proyecto «{proj.name}» dentro de la solución «{sol.name}»")], cls="subtitle"),
                       *([Para([Run(provenance_sentence(doc.ai_manifest, brief=executive))], cls="provenance")] if provenance_sentence(doc.ai_manifest) else [])]
            continue
        if sec == "ai_notice":
            ai_ran = doc.ai_manifest.get("status") == "COMPLETED"
            blocks.append(Callout("ai-notice", template.label("ai_notice_title", "Interpretación asistida por IA"), [Para([Run(
                template.label("ai_notice_text", "Este documento presenta una interpretación generada a partir del análisis de IST. Las afirmaciones "
                               "se distinguen como Confirmadas, Inferidas o No resueltas.") if ai_ran else NO_AI_SENTENCE)])]))
            for status in _CARD_ORDER:      # the colour legend: explained once, here
                blocks.append(Callout(_CARD_KIND[status], _CARD_TITLE[status], [Para([Run(H.STATUS_MEANING[status])])]))
            continue
        if sec == "toc":
            continue                      # rendered by the shell (HTML sidebar) / contents page (PDF) from the headings below
        if sec == "modules" and mod is None:
            continue
        number += 1
        title = template.label(f"section_{sec}", SECTION_TITLES[sec])
        head = Heading(2, [Run(f"{number}. {title}")], f"s-{sec.replace('_', '-')}", "section-title")
        if sec == "solution":
            blocks += [head] + claims_with_backing(sol.summary + sol.not_inferable, not executive)
            if sol.projects:
                blocks.append(Table([[Run("Proyecto")], [Run("Capa (inferida)")], [Run("Estado")]],
                                    [[[Run(p["name"], code=True)], [Run({"presentation": "presentación", "logic": "lógica / servicios", "data_access": "acceso a datos",
                                                                      "unclassified": "sin clasificar"}.get(p["layer"], p["layer"]))],
                                      [Run(STATUS_ES.get(p["layer_status"], p["layer_status"]))]] for p in sol.projects]))
        elif sec == "project":
            blocks.append(head)
            if proj.ai_summary:
                blocks += ai_callout(proj.ai_summary)
            elif ran:
                blocks.append(Para([Run("La interpretación de IA del proyecto no produjo texto válido tras la validación.")], cls="technical"))
            blocks += claims_with_backing(proj.summary + proj.role_in_solution + proj.structural_areas + proj.dependencies + proj.data_patterns, not executive)
            if doc.domain_knowledge:
                from legacy_documenter.product import domain as _dk
                where = _dk.appears_in(doc.domain_knowledge, [r["name"] for r in doc.catalog] + [proj.name])
                blocks += [Heading(3, [Run("Terminología confirmada por una persona")], "terminologia"),
                           Para([Run("Significados aportados explícitamente por una persona; no provienen del código y no se infieren de los nombres.")], cls="caption"),
                           Table([[Run("Término")], [Run("Significado")], [Run("Estado")], [Run("Aparece en")]],
                                 [[[Run(t["term"], code=True)], [Run(t["meaning"])], [Run(STATUS_ES.get("CANONICAL", "Canónico"))],
                                   [Run(_names(where.get(t["term"], []), 6) or "—")]] for t in doc.domain_knowledge])]
        elif sec == "modules":
            blocks += [head] + claims_with_backing([mod.claim], not executive)
            if mod.classification == MODULE_NONE:
                blocks.append(Para([Run("Por eso la documentación sigue el camino directo: Solución → Proyecto → Vistas.")]))
        elif sec == "important_views":
            blocks += [head, Para([Run("Vistas explicadas en detalle en este documento:")]),
                       Table([[Run("Vista")], [Run("Título visible")], [Run("Uso observable")]],
                             [[[Run(v.name, code=True)], [Run(v.title or "—")], [Run(v.usage.get("label", "—") if v.usage else "—")]] for v in doc.views])]
        elif sec == "view_chapters":
            blocks += [head, Para([Run("Cada capítulo va de lo simple a lo técnico. El catálogo completo está en el apéndice.")], cls="caption")]
            for i, v in enumerate(doc.views, 1):
                blocks += view_chapter(v, assets, i, template, number)
        elif sec == "cross_view":
            blocks += [head, Para([Run("Invocaciones confirmadas entre vistas del proyecto (literal de URL en el código).")])]
            cross = doc.cross_view[:40]
            if cross:
                blocks.append(Table([[Run("Origen")], [Run("Abre")], [Run("Cómo")], [Run("Parámetros")], [Run("Estado")]],
                                    [[[Run(i.source_view.rsplit("\\", 1)[-1], code=True)], [Run(i.target_view.rsplit("\\", 1)[-1], code=True)],
                                      [Run({"window_open": "ventana emergente", "navigate_url": "enlace", "url_literal": "literal de URL"}.get(i.mechanism, i.mechanism))],
                                      [Run(", ".join(i.parameters) or "—")], [Run(STATUS_ES[i.status] if i.target_exists else "No resuelto")]] for i in cross]))
                if len(doc.cross_view) > len(cross):
                    blocks.append(Para([Run(f"Se muestran {len(cross)} de {len(doc.cross_view)} invocaciones; el resto está en el detalle de cada vista.")], cls="caption"))
        elif sec == "data":
            blocks.append(head)
            seen: dict[str, tuple] = {}
            for v in doc.views:
                for a in v.actions:
                    for d in a.data:
                        seen.setdefault(d.object_name, (d, v.name))
            if seen and executive:
                by_effect: dict[str, list[str]] = {}
                for _k, (d, vn) in sorted(seen.items()):
                    by_effect.setdefault(EFFECT_ES.get(d.effect, d.effect), []).append(vn)
                blocks.append(Table([[Run("Qué hacen con los datos (inferido)")], [Run("Vistas")]],
                                    [[[Run(eff)], [Run(_names(vs, 10))]] for eff, vs in sorted(by_effect.items())]))
            elif seen:
                blocks.append(Table([[Run("Dato / procedimiento")], [Run("Efecto (inferido)")], [Run("Vista")], [Run("Alcanzado por")]],
                                    [[[Run(k, code=True)], [Run(EFFECT_ES.get(d.effect, d.effect))], [Run(vn, code=True)], [Run(d.via or "—", code=True)]]
                                     for k, (d, vn) in sorted(seen.items())]))
        elif sec == "usage":
            blocks += [head, Para([Run("Existir en el código no implica uso en producción. Cada vista se clasifica solo con indicios positivos; la ausencia de indicios "
                                       "de uso no se interpreta como obsolescencia.")])]
            meaning = {"ACTIVE_OBSERVABLE": "invocación entrante confirmada desde otra pantalla", "POSSIBLY_ACTIVE": "comportamiento propio y referencias por nombre, sin invocación confirmada",
                       "UNRESOLVED_USAGE": "puede cargarse por nombre desde el shell; no hay conclusión posible", "ISOLATED": "sin relación entrante observable (no implica obsolescencia)",
                       "LEGACY_CANDIDATE": "varios indicadores alineados; solo candidata a revisión"}
            by_label: dict[str, list[str]] = {}
            for r in doc.catalog:
                by_label.setdefault(r["usage_label"], []).append(r["name"])
            labels = {USAGE_ES.get(k, k): meaning.get(k, "") for k in meaning}
            blocks.append(Table([[Run("Clasificación")], [Run("Qué significa")], [Run("Vistas")]],
                                [[[Run(lab)], [Run(labels.get(lab, ""))], [Run(_names(vs, 10))]] for lab, vs in by_label.items()]))
        elif sec == "unresolved":
            blocks.append(head)
            generic: list[Claim] = list(sol.not_inferable) + ([mod.claim] if mod and mod.claim.status == UNRESOLVED else [])
            scope = next((c for c in proj.unresolved.unresolved + [c for v in doc.views for c in v.unresolved.unresolved] if c.basis in _GENERIC_BASIS), None)
            if scope:
                generic.append(scope)
            pending = [(v.name, a.action, u["business_call"] or u["label"]) for v in doc.views for a in v.actions if a.technical_path
                       for u in a.technical_path.unresolved_calls if not u["infrastructure"] and u["business_call"]]
            pending = list(dict.fromkeys(pending))
            missing = sorted({i.target_view for v in doc.views for i in v.reaches if not i.target_exists} | {i.target_view for i in doc.cross_view if not i.target_exists})
            if executive:
                notes = ["El propósito funcional exacto de las pantallas requiere conocimiento del negocio; el análisis estático describe qué hacen, no por qué."]
                if any(v.usage.get("status") == "UNRESOLVED_USAGE" for v in doc.views) or any(r["usage_label"] == "Uso no resuelto" for r in doc.catalog):
                    notes.append("Algunas pantallas se cargan dinámicamente y su uso no puede confirmarse solo con análisis estático.")
                if pending or missing:
                    notes.append("Algunas rutas terminan en componentes externos o llamadas cuyo destino no está disponible.")
                blocks += [Bullets([[Run(n)] for n in notes[:4]])]
            else:
                blocks += claim_cards(generic)
                if pending:
                    blocks.append(Details("Acciones cuyo destino posterior es indeterminado", [
                        Table([[Run("Vista")], [Run("Acción")], [Run("Llamada sin destino")], [Run("Estado")]],
                              [[[Run(vn, code=True)], [Run(ac)], [Run(call, code=True)], [Run("No resuelto")]] for vn, ac, call in pending[:60]])]))
                specific = [c for v in doc.views for c in v.unresolved.unresolved if c.basis not in _GENERIC_BASIS]
                if specific:
                    blocks.append(Details("Detalle de las afirmaciones no resueltas", claim_cards(specific)))
                if missing:
                    blocks.append(Details("Destinos de invocación inexistentes", [Para([Run(
                        "Destinos que no existen como vista en el repositorio (se mantienen sin enlace): " + ", ".join(missing) + ".")])]))
        elif sec == "appendix":
            blocks += [head, Heading(3, [Run("Catálogo completo de vistas")], "catalogo"),
                       Para([Run("Navegación, no narrativa. Las vistas con capítulo están marcadas con ●.")], cls="caption")]
            def short_row(r):
                return [[Run(("● " if r["detailed"] else "") + r["name"], code=True)], [Run(r["title"] or "—")], [Run(catalog_purpose(r))], [Run(r["usage_label"])]]
            head4 = [[Run("Vista")], [Run("Título visible")], [Run("Qué parece hacer")], [Run("Uso observable")]]
            if executive:
                blocks.append(Details("Catálogo de vistas del proyecto", [Table(head4, [short_row(r) for r in doc.catalog])]))
            else:
                blocks.append(Table(head4, [short_row(r) for r in doc.catalog]))
            blocks.append(Para([Run(f"Plantilla: {template.template_id} {template.manifest['template_version']} (LegacyMapperHumanTemplate {template.manifest['contract_version']}).")],
                               cls="technical"))
    return humanize_blocks(blocks), assets


def toc_entries(blocks: list) -> list[tuple[int, str, str]]:
    return [(b.level, plain(b.runs), b.anchor) for b in blocks if isinstance(b, Heading) and b.level in (2, 3) and b.anchor]


def html_document(blocks: list, title: str, template: HumanTemplate | None = None) -> str:
    template = template or discover("human/default")
    body: list[str] = []
    for blk in blocks:
        if isinstance(blk, Figure):
            body.append(f'<figure class="diagram"><a href="{esc(blk.svg)}" target="_blank" rel="noopener"><img src="{esc(blk.svg)}" width="{blk.width}" '
                        f'height="{blk.height}" alt="{esc(blk.title)}" loading="lazy"></a><figcaption><strong>{esc(blk.title)}</strong> · '
                        f'<a href="{esc(blk.svg)}" target="_blank" rel="noopener">Abrir a tamaño completo</a></figcaption></figure>')
        elif isinstance(blk, Details):
            inner = []
            for x in blk.blocks:
                if isinstance(x, Figure):
                    inner.append(f'<figure class="diagram"><a href="{esc(x.svg)}" target="_blank" rel="noopener"><img src="{esc(x.svg)}" '
                                 f'width="{x.width}" height="{x.height}" alt="{esc(x.title)}" loading="lazy"></a></figure>')
                else:
                    H._render_block(x, "index.html", inner)
            body.append(f'<details><summary>{esc(blk.summary)}</summary>{"".join(inner)}</details>')
        elif isinstance(blk, Heading) and blk.level == 1:
            body.append(f'<h1 class="doc-title" id="{esc(blk.anchor)}">{esc(plain(blk.runs))}</h1>')
        elif isinstance(blk, Para) and blk.cls == "subtitle":
            body.append(f'<p class="doc-subtitle">{esc(plain(blk.runs))}</p>')
        elif isinstance(blk, Para) and blk.cls == "provenance":
            body.append(f'<p class="provenance">{esc(plain(blk.runs))}</p>')
        elif isinstance(blk, Callout) and blk.kind == "ai-notice":
            text = "".join(f"<p>{esc(plain(b2.runs))}</p>" for b2 in blk.blocks if isinstance(b2, Para))
            body.append(f'<aside class="ai-notice" data-status="AI_INTERPRETATION"><h3>{esc(blk.title)}</h3>{text}</aside>')
        else:
            H._render_block(blk, "index.html", body)
    entries = toc_entries(blocks)
    toc_items = "".join(f'<li class="lv{lv}"><a href="#{esc(a)}">{esc(t)}</a></li>' for lv, t, a in entries)
    toc = f'<p class="toc-title">{esc(template.label("toc_title", "Contenido"))}</p><ul>{toc_items}</ul>'
    return template.fill(
        title=esc(title), subtitle="Documentación conductual", lang=template.language, style=template.styles_css, toc=toc, ai_notice="", content="\n".join(body),
        legend="",
        footer='<p class="muted">Documento estático y portable. La trazabilidad técnica (referencias y procedencia) está en los artefactos ai/ e internal/ del paquete.</p>',
        script=f"<script>{H.JS}</script>", template_id=esc(template.template_id), template_version=esc(template.manifest["template_version"])) + "\n"


PDF_SKIP_DETAILS = {"Evidencia considerada y convenciones de nombre observadas", "Afirmaciones deterministas sobre la vista", "Referencias y controles",
                    "Respaldo de la interpretación", "Base de las afirmaciones", "Base del uso observable", "Por qué se eligieron estas vistas",
                    "Fidelidad de la reconstrucción", "Detalle de las afirmaciones no resueltas", "Detalle de las afirmaciones no resueltas de la vista",
                    "Acciones cuyo destino posterior es indeterminado", "Destinos de invocación inexistentes", "Catálogo de vistas del proyecto", "Metadatos del análisis (diagnóstico)", "Detalle de lo conocido y lo indeterminado de esta vista", "Invocaciones entrantes (detalle)", "Invocaciones salientes (detalle)"}


def build_pdf(blocks: list, title: str, assets_root, meta: list[str], template: HumanTemplate | None = None) -> tuple[bytes, dict]:
    template = template or discover("human/default")
    pdf = PdfDocument(title, footer_title=title, row_cap=140)
    pdf.assets_root = assets_root
    style = dict(template.pdf_style)
    sizes = style.get("heading_sizes", {})
    colors = style.get("heading_colors", {})
    # template classes h1/h2/h3 style the document's section / view / sub-section headings (markdown levels 2 / 3 / 4)
    style["heading_sizes"] = {2: sizes.get(1, 15), 3: sizes.get(2, 12.5), 4: sizes.get(3, 11), 5: 10}
    style["heading_colors"] = {2: colors.get(1, (0.1, 0.1, 0.15)), 3: colors.get(2, (0.1, 0.1, 0.15)), 4: colors.get(3, (0.1, 0.1, 0.15))}
    for key in ("heading_align", "heading_before", "heading_after"):
        style[key] = {lvl + 1: val for lvl, val in (template.pdf_style.get(key) or {}).items()}
    style["heading_rule"] = False
    pdf.style = style
    pdf.legend_labels = ("Confirmado", "Inferido (regla estructural)", "No resuelto")   # governance states live in ai/ and internal/, not in the human legend
    pdf.LEGEND_TEXT = "Estados: CONFIRMADO (borde continuo, azul) · INFERIDO (discontinuo, naranja) · NO RESUELTO (punteado, marca !, rojo)"
    pdf.toc_levels = (2, 3)
    pdf.outline_levels = (2, 3)
    pdf.reserve_front()
    kind_es = {"view": "vista", "event": "evento", "handler": "manejador", "method": "método", "data_operation": "operación de datos",
               "procedure": "destino de datos", "class": "clase"}

    def flatten(items):
        for x in items:
            if isinstance(x, Details) and x.summary in PDF_SKIP_DETAILS:
                continue                      # technical backing that the HTML keeps collapsed
            if isinstance(x, Details):
                yield Para([Run(x.summary, bold=True)])
                yield from flatten(x.blocks)
            elif isinstance(x, Figure) and x.kind == "behavior-path" and x.children:
                yield Bullets([[Run(f"{kind_es.get(k, k)}: ", italic=True), Run(label, code=True), Run(f"  [{STATUS_ES.get(st, st)}]")] for label, st, k in x.children])
            elif isinstance(x, Callout) and x.kind == "ai-notice":
                yield Callout("ai-notice", x.title, x.blocks)
            elif isinstance(x, Callout) and x.kind == "ai" and not x.title:
                yield from x.blocks               # AI prose reads as plain paragraphs; the opening notice already says so
            else:
                yield x
    flat = [x for x in flatten(blocks) if not (isinstance(x, Heading) and x.level == 1)]
    kept: list = []
    for i, x in enumerate(flat):                  # a sub-heading whose content was left out of the PDF is dropped, not left orphaned
        nxt = flat[i + 1] if i + 1 < len(flat) else None
        if isinstance(x, Heading) and x.level >= 4 and (nxt is None or (isinstance(nxt, Heading) and nxt.level <= x.level)):
            continue
        kept.append(x)
    pdf.blocks(kept)
    pdf.fill_front("Guía de comportamiento: solución → proyecto → vistas → acciones → datos", meta)
    return pdf.render()
