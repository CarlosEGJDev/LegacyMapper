"""Simple evidence-backed box-flow diagram per view (post-V5 template productization, text-contained since the final polish).

    [Vista] -> [Evento / manejador] -> [Negocio / servicio] -> [DAO / repositorio] -> [Procedimiento / SQL] -> [Base de datos / límite]

One row per important action. Only layers supported by the action's evidence are drawn (missing architectural layers are skipped,
never filled in); an unresolved business call or an unresolved data destination is drawn explicitly as UNRESOLVED. Ordering is fixed
(view order of actions, fixed column order), no force layout, no routing. Text is measured and wrapped (see `svgtext`): a box grows
to contain its text; nothing is truncated or clipped. SVG uses rect/text/path only.
"""
from __future__ import annotations

import re
from xml.sax.saxutils import escape

from . import svgtext
from .model import CONFIRMED, INFERRED, UNRESOLVED

COLUMNS = ("view", "event", "business", "dao", "procedure", "boundary")
COLUMN_ES = {"view": "Vista", "event": "Evento / manejador", "business": "Negocio / servicio", "dao": "DAO / repositorio",
             "procedure": "Procedimiento / SQL", "boundary": "Base de datos / límite"}
STYLE = {CONFIRMED: ("#1e3a8a", "#eef2ff", ""), INFERRED: ("#b45309", "#fffbeb", "7 4"), UNRESOLVED: ("#b91c1c", "#fef2f2", "2 3")}
STATUS_TAG = {CONFIRMED: "CONFIRMADO", INFERRED: "INFERIDO", UNRESOLVED: "NO RESUELTO"}
BW, GAP_X, GAP_Y, MARGIN_X, PAD = 150, 30, 18, 14, 9   # BW = default box width; it widens (up to MAX_BW) so one identifier is not split by characters
MAX_BW = 196
MIN_BH = 58
HEADER_H = 74
MAX_ROWS = 8
SIZE, SMALL, TAG = 11.0, 10.0, 9.0


def _human(label: str) -> str:
    """The label as the human reads it: deterministic support ids (`(DAO-0001)`) and evidence references stay in the model, not in the picture."""
    return re.sub(r"\s*\(DAO-\d+\)", "", label)


def action_layers(view, action) -> list[dict]:
    """Layers (in fixed column order) supported by the evidence of one action."""
    path = action.technical_path
    steps = path.steps if path else []
    layers: list[dict] = []
    ev_labels = [s["label"] for s in steps if s["kind"] in ("event", "handler")]
    own = [s for s in steps if s["kind"] == "method" and s["label"].split(".")[0].lower() == view.name.lower()]
    refs_ev = sorted({r for s in steps if s["kind"] in ("event", "handler") or s in own for r in s.get("source_refs", [])})
    if ev_labels or own:
        label = " → ".join(dict.fromkeys(ev_labels)) or action.handler
        layers.append({"layer": "event", "label": label, "status": CONFIRMED, "source_refs": refs_ev or action.source_refs})
    biz_steps = [s for s in steps if s["kind"] == "method" and s not in own]
    biz_unres = [u for u in (path.unresolved_calls if path else []) if not u.get("infrastructure") and u.get("business_call")]
    if biz_steps:
        names = list(dict.fromkeys(s["label"] for s in biz_steps))
        layers.append({"layer": "business", "label": ", ".join(names[:2]) + (f" (+{len(names) - 2})" if len(names) > 2 else ""),
                       "status": INFERRED, "source_refs": sorted({r for s in biz_steps for r in s.get("source_refs", [])})})
    elif biz_unres:
        names = list(dict.fromkeys(u["business_call"] for u in biz_unres))
        layers.append({"layer": "business", "label": "Lógica de negocio no seguida: " + ", ".join(names[:2]) + (f" (+{len(names) - 2})" if len(names) > 2 else ""),
                       "status": UNRESOLVED, "source_refs": list(action.source_refs)})
    daos = [s for s in steps if s["kind"] == "data_operation"]
    if daos:
        layers.append({"layer": "dao", "label": ", ".join(dict.fromkeys(s["label"] for s in daos[:2])), "status": CONFIRMED,
                       "source_refs": sorted({r for s in daos for r in s.get("source_refs", [])})})
    procs = [s for s in steps if s["kind"] == "procedure"]
    if procs:
        layers.append({"layer": "procedure", "label": ", ".join(dict.fromkeys(s["label"] for s in procs[:2])), "status": CONFIRMED,
                       "source_refs": sorted({r for s in procs for r in s.get("source_refs", [])})})
        layers.append({"layer": "boundary", "label": "Base de datos (el análisis no la sigue)", "status": INFERRED, "source_refs": list(action.source_refs)})
    elif not daos and layers:
        layers.append({"layer": "dao", "label": "Destino de datos no resuelto", "status": UNRESOLVED, "source_refs": list(action.source_refs)})
    return layers


def view_flow(view) -> dict | None:
    rows = []
    for a in view.actions:
        layers = action_layers(view, a)
        if layers:
            rows.append({"action": a.action, "handler": a.handler, "layers": layers})
    return {"view": view.name, "rows": rows} if rows else None


def _box_width(rows: list, view: str) -> int:
    need = max([svgtext.longest_unbreakable(view, 12, True)] + [svgtext.longest_unbreakable(_human(l["label"]), SIZE) for r in rows for l in r["layers"]]
               + [svgtext.longest_unbreakable(r["action"], SMALL) for r in rows]) + 2 * PAD + 2
    return int(min(MAX_BW, max(BW, need)))


def _box_content(layer: dict, row_action: str, bw: int = BW) -> dict:
    inner = bw - 2 * PAD
    caption = svgtext.wrap(row_action, inner, SMALL) if layer["layer"] == "event" else []
    body = svgtext.wrap(_human(layer["label"]), inner, SIZE, bold=False)
    height = PAD + len(caption) * svgtext.line_height(SMALL) + len(body) * svgtext.line_height(SIZE) + svgtext.line_height(TAG) + PAD
    return {"caption": caption, "body": body, "height": max(MIN_BH, round(height))}


def render(flow: dict) -> tuple[str, int, int]:
    """Returns (svg, width, height). The canvas grows with the content; text is always inside its box."""
    rows = flow["rows"][:MAX_ROWS]
    bw = _box_width(rows, flow["view"])
    used = [c for c in COLUMNS[1:] if any(l["layer"] == c for r in rows for l in r["layers"])]
    cols = ["view"] + used
    width = MARGIN_X * 2 + len(cols) * bw + (len(cols) - 1) * GAP_X
    x_of = {c: MARGIN_X + i * (bw + GAP_X) for i, c in enumerate(cols)}
    contents = [[_box_content(l, r["action"], bw) for l in r["layers"]] for r in rows]
    row_h = [max(c["height"] for c in cs) for cs in contents]
    body_h = sum(row_h) + GAP_Y * (len(rows) - 1)
    title_lines = svgtext.wrap("Flujo simple: " + flow["view"], width - 2 * MARGIN_X, 14, bold=True)
    head = 20 + len(title_lines) * svgtext.line_height(14) + 26
    footer = 22 if len(flow["rows"]) > MAX_ROWS else 8
    height = int(head + 20 + body_h + footer + 12)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Arial, Helvetica, sans-serif" font-size="11">',
           f"<title>{escape('Flujo de cajas: ' + flow['view'])}</title>", f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#1e3a8a"/></marker></defs>']
    y = 20.0
    for line in title_lines:
        y += svgtext.line_height(14)
        out.append(f'<text x="{width / 2:.0f}" y="{y:.0f}" font-size="14" font-weight="bold" text-anchor="middle">{escape(line)}</text>')
    out.append(f'<text x="{width / 2:.0f}" y="{y + 18:.0f}" font-size="10" fill="#4b5563" text-anchor="middle">Solo capas con evidencia; lo no resuelto se dibuja punteado. Cada caja indica su estado.</text>')
    top = head + 20
    for c in cols:
        out.append(f'<text x="{x_of[c] + bw / 2:.0f}" y="{top - 8:.0f}" font-size="10" font-weight="bold" fill="#374151" text-anchor="middle">{escape(COLUMN_ES[c])}</text>')
    stroke, fill, _dash = STYLE[CONFIRMED]
    view_h = max(MIN_BH, round(PAD * 2 + svgtext.line_height(10) + len(svgtext.wrap(flow["view"], bw - 2 * PAD, 12, bold=True)) * svgtext.line_height(12)))
    mid = top + body_h / 2 - view_h / 2
    out.append('<g data-role="view">')
    out.append(f'<rect x="{x_of["view"]}" y="{mid:.0f}" width="{bw}" height="{view_h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
    out.append(f'<text x="{x_of["view"] + PAD}" y="{mid + PAD + 9:.0f}" font-size="10" fill="#4b5563">Vista</text>')
    ty = mid + PAD + 9
    for line in svgtext.wrap(flow["view"], bw - 2 * PAD, 12, bold=True):
        ty += svgtext.line_height(12)
        out.append(f'<text x="{x_of["view"] + PAD}" y="{ty:.0f}" font-size="12" font-weight="bold">{escape(line)}</text>')
    out.append("</g>")
    y_row = top
    for row, cs, rh in zip(rows, contents, row_h):
        prev_right, prev_y = x_of["view"] + bw, mid + view_h / 2
        first = True
        for layer, content in zip(row["layers"], cs):
            if layer["layer"] not in x_of:
                continue
            stroke, fill, dash = STYLE[layer["status"]]
            x = x_of[layer["layer"]]
            d = f' stroke-dasharray="{dash}"' if dash else ""
            origin = ' data-from="view"' if first else ""
            first = False
            out.append(f'<g data-node="1"><title>{escape(_human(layer["label"]))} [{layer["status"]}]</title>'
                       f'<path{origin} d="M{prev_right:.0f} {prev_y:.0f} L{x} {y_row + rh / 2:.0f}" fill="none" stroke="#1e3a8a" stroke-width="1" marker-end="url(#a)"/>'
                       f'<rect x="{x}" y="{y_row:.0f}" width="{bw}" height="{rh}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>')
            ty = y_row + PAD
            for line in content["caption"]:
                ty += svgtext.line_height(SMALL)
                out.append(f'<text x="{x + PAD}" y="{ty:.0f}" font-size="10" fill="#4b5563">{escape(line)}</text>')
            for line in content["body"]:
                ty += svgtext.line_height(SIZE)
                out.append(f'<text x="{x + PAD}" y="{ty:.0f}" font-size="11">{escape(line)}</text>')
            out.append(f'<text x="{x + PAD}" y="{y_row + rh - PAD:.0f}" font-size="9" font-weight="bold" fill="{stroke}">{STATUS_TAG[layer["status"]]}</text></g>')
            prev_right, prev_y = x + bw, y_row + rh / 2
        y_row += rh + GAP_Y
    if len(flow["rows"]) > MAX_ROWS:
        out.append(f'<text x="{width / 2:.0f}" y="{height - 10}" font-size="10" fill="#4b5563" text-anchor="middle">+ {len(flow["rows"]) - MAX_ROWS} acciones más (ver el flujo técnico por acción)</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n", width, height


def render_svg(flow: dict) -> str:
    return render(flow)[0]
