"""Deterministic SVG renderer for `VisualProjection` (post-V5 H3).

Reads only the validated model. Every number is an integer, every label is XML-escaped and control characters are
stripped, so the same model always renders the same bytes. Epistemic status is never encoded by colour alone: each
status has its own stroke pattern AND a text tag inside the node, and the legend is part of every diagram.
"""
from __future__ import annotations

import re
from collections import Counter
from xml.sax.saxutils import escape, quoteattr

from .layout import LINE_H, MARGIN, NODE_W, PAD, TITLE_H, Layout, layout
from .model import AI_INTERPRETATION, CANONICAL, CONFIRMED, INFERRED, LEGEND, UNRESOLVED, VisualProjection, validate_projection

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
FONT = "Arial, Helvetica, sans-serif"

#: stroke colour, fill colour, dash pattern, stroke width, text tag
STYLE = {
    CONFIRMED: ("#1e3a8a", "#eef2ff", "", 2, "CONFIRMADO"),
    INFERRED: ("#b45309", "#fffbeb", "7 4", 2, "INFERIDO"),
    UNRESOLVED: ("#b91c1c", "#fef2f2", "2 3", 2, "! NO RESUELTO"),
    AI_INTERPRETATION: ("#6d28d9", "#f5f3ff", "8 3 2 3", 2, "IA - NO APROBADA"),
    CANONICAL: ("#047857", "#ecfdf5", "", 4, "OK CANÓNICO"),
}
TYPE_LABEL = {
    "system": "Sistema", "area": "Área (solución)", "project": "Proyecto", "layer": "Capa (inferida)", "library": "Biblioteca",
    "aggregate": "Agrupación", "screen": "Pantalla", "event": "Evento", "handler": "Manejador", "class": "Componente",
    "method": "Método", "data_operation": "Operación de datos", "data_object": "Objeto de datos", "unresolved_call": "Llamada no resuelta",
    "ai_note": "Interpretación", "canonical_note": "Conocimiento aprobado",
}


def clean(text: object) -> str:
    return _CONTROL.sub("", str(text))


def _t(text: object) -> str:
    return escape(clean(text))


def _edge_path(src, dst, lay: Layout | None = None) -> tuple[str, int, int]:
    x1, y1 = src.x + src.w, src.y + src.h // 2
    x2, y2 = dst.x, dst.y + dst.h // 2
    if lay is not None and src.band != dst.band and dst.band > src.band:
        # continuation into a lower band: right, down into the gap under the source band, left, down, right (orthogonal, unambiguous)
        gap_y = lay.bands[src.band][1] + 30 + 6 * (src.column % 4)
        xa, xb = x1 + 24, x2 - 24
        return f"M{x1} {y1} L{xa} {y1} L{xa} {gap_y} L{xb} {gap_y} L{xb} {y2} L{x2} {y2}", (xa + xb) // 2, gap_y
    if x2 > x1:
        dx = max(40, (x2 - x1) // 2)
        path = f"M{x1} {y1} C{x1 + dx} {y1} {x2 - dx} {y2} {x2} {y2}"
    else:  # same column or backwards: loop around to the left side of the target
        path = f"M{x1} {y1} C{x1 + 70} {y1} {x2 - 70} {y2} {x2} {y2}"
    return path, (x1 + x2) // 2, (y1 + y2) // 2


def render_svg(projection: VisualProjection) -> str:
    validate_projection(projection)
    lay: Layout = layout(projection)
    legend_h = 40 + 22 * ((len(LEGEND) + 1) // 2)
    note = ""
    if projection.partial.get("partial"):
        note = (f"Parcial: {projection.partial['included_count']} elementos mostrados y {projection.partial['omitted_count']} agregados en nodos de "
                f"resumen; ninguno se descarta (el detalle completo está en el modelo JSON).")
    # H3-R2: in a dense diagram (13-60 edges) a relation wording that repeats on more than 6 edges is not printed on every edge; the omission
    # is declared under the diagram (counts such as "3" are data, never suppressed). Diagrams with <=12 edges render exactly as before.
    label_counts = Counter(e.label for e in projection.edges if e.label and not e.label.isdigit())
    hidden_labels = {lbl for lbl, cnt in label_counts.items() if 12 < len(projection.edges) <= 60 and cnt > 6}
    width = max(lay.width, 820)
    repeated_note = ("Etiquetas repetidas no impresas en cada relación: " + "; ".join(f"«{lbl}» × {label_counts[lbl]}" for lbl in sorted(hidden_labels))) if hidden_labels else ""
    height = lay.height + legend_h + (22 if note else 0) + (20 if repeated_note else 0)
    out: list[str] = []
    add = out.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-labelledby="t d" font-family={quoteattr(FONT)} font-size="12">')
    add(f"<title id=\"t\">{_t(projection.title)}</title>")
    add(f"<desc id=\"d\">{_t(projection.kind)} - {len(projection.nodes)} nodos, {len(projection.edges)} relaciones. "
        f"Cada nodo y relación indica su estado (confirmado, inferido, no resuelto, interpretación de IA o canónico).</desc>")
    add("<defs>")
    for status, (stroke, _fill, _dash, _w, _tag) in STYLE.items():
        add(f'<marker id="a-{status}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{stroke}"/></marker>')
    add("</defs>")
    add(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
    add(f'<text x="{MARGIN}" y="28" font-size="18" font-weight="bold">{_t(projection.title)}</text>')
    add(f'<text x="{MARGIN}" y="46" font-size="11" fill="#4b5563">{_t(projection.kind)} · {_t(projection.scope.get("type", ""))}: '
        f'{_t(projection.scope.get("label", ""))} · {len(projection.nodes)} nodos · {len(projection.edges)} relaciones</text>')
    if len(lay.bands) > 1:
        for k, (btop, _bbottom) in enumerate(lay.bands):
            add(f'<text x="{MARGIN}" y="{btop - 12}" font-size="11" fill="#6b7280">Sección {k + 1} de {len(lay.bands)}'
                f'{" (continúa en la sección siguiente)" if k < len(lay.bands) - 1 else ""}</text>')
    groups = {g.id: g for g in projection.groups}
    for gid, x, y, w, h in lay.group_boxes:
        g = groups[gid]
        stroke, _fill, dash, _w, _tag = STYLE.get(g.status, STYLE[CONFIRMED])
        add(f'<g data-group={quoteattr(gid)}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#f9fafb" stroke="{stroke}" '
            f'stroke-width="1" stroke-dasharray="{dash or "none"}"/><text x="{x + 8}" y="{y + 14}" font-size="11" fill="#374151" font-weight="bold">'
            f'{_t(clean(g.label)[:38] + ("…" if len(clean(g.label)) > 38 else ""))}<title>{_t(g.label)}</title></text></g>')
    for edge in sorted(projection.edges, key=lambda e: e.id):
        src, dst = lay.nodes[edge.source], lay.nodes[edge.target]
        stroke, _fill, dash, width_, _tag = STYLE[edge.status]
        path, mx, my = _edge_path(src, dst, lay)
        add(f'<g data-edge={quoteattr(edge.id)} data-status="{edge.status}"><path d="{path}" fill="none" stroke="{stroke}" '
            f'stroke-width="{max(1, width_ - 1)}" stroke-dasharray="{dash or "none"}" marker-end="url(#a-{edge.status})"><title>'
            f'{_t(edge.relation)} [{edge.status}] {_t(", ".join(sorted(set(edge.source_refs))[:4]))}</title></path>')
        if edge.label and len(projection.edges) <= 60 and edge.label not in hidden_labels:
            label = clean(edge.label)[:34]
            add(f'<rect x="{mx - len(label) * 3 - 3}" y="{my - 11}" width="{len(label) * 6 + 6}" height="14" fill="#ffffff" opacity="0.9"/>'
                f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="10" fill="{stroke}">{_t(label)}</text>')
        add("</g>")
    nodes = {n.id: n for n in projection.nodes}
    for nid in sorted(lay.nodes, key=lambda i: (lay.nodes[i].column, lay.nodes[i].y, i)):
        node, p = nodes[nid], lay.nodes[nid]
        stroke, fill, dash, sw, tag = STYLE[node.status]
        add(f'<g data-node={quoteattr(nid)} data-status="{node.status}" data-type={quoteattr(node.type)}>')
        add(f"<title>{_t(node.label)} [{node.status}] {_t(', '.join(sorted(set(node.source_refs))[:4]))}</title>")
        if node.status == AI_INTERPRETATION:  # double outline
            add(f'<rect x="{p.x - 4}" y="{p.y - 4}" width="{p.w + 8}" height="{p.h + 8}" rx="9" fill="none" stroke="{stroke}" stroke-width="1"/>')
        add(f'<rect x="{p.x}" y="{p.y}" width="{p.w}" height="{p.h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-dasharray="{dash or "none"}"/>')
        y = p.y + PAD + 11
        for line in p.lines:
            add(f'<text x="{p.x + PAD}" y="{y}" font-size="12">{_t(line)}</text>')
            y += LINE_H
        sub = node.sublabel or TYPE_LABEL.get(node.type, node.type)
        add(f'<text x="{p.x + PAD}" y="{y + 1}" font-size="10" fill="#4b5563">{_t(sub)}</text>')
        add(f'<text x="{p.x + PAD}" y="{y + 14}" font-size="10" font-weight="bold" fill="{stroke}">{_t(tag)}</text>')
        add("</g>")
    ly = lay.height + 4
    if note:
        add(f'<text x="{MARGIN}" y="{ly + 12}" font-size="11" fill="#b45309">{_t(note)}</text>')
        ly += 22
    if repeated_note:
        add(f'<text x="{MARGIN}" y="{ly + 12}" font-size="11" fill="#4b5563">{_t(repeated_note)}</text>')
        ly += 20
    add(f'<text x="{MARGIN}" y="{ly + 14}" font-size="12" font-weight="bold">Leyenda de estados</text>')
    for k, (status, label, style) in enumerate(LEGEND):
        stroke, fill, dash, sw, tag = STYLE[status]
        col, row = k % 2, k // 2
        x, y = MARGIN + col * 340, ly + 24 + row * 22
        add(f'<g data-legend="{status}"><rect x="{x}" y="{y}" width="36" height="14" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-dasharray="{dash or "none"}"/><text x="{x + 44}" y="{y + 11}" font-size="11">{_t(label)} - {_t(style)}</text></g>')
    add("</svg>")
    return "\n".join(out) + "\n"
