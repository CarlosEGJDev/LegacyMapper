"""Deterministic documentary wireframe of a view (post-V5 H4-R4, style-aware since the template productization).

Built ONLY from controls present in the view markup: table/row/cell skeleton, labels, text boxes, drop-downs, buttons/links, grids
(with their declared column titles) and panels. When style evidence exists (stylesheet linked by the shell, CssClass/class/inline
style/Width attributes, icon files present in the repository) it is applied conservatively; nothing is invented and no script runs.
The drawing is labelled as a documentary reconstruction and never as a screenshot. Output is plain SVG (rect/text, plus `<image>`
for evidenced local icons) so the PDF writer can embed it as vectors.
"""
from __future__ import annotations

import base64
import os
import re
import struct
from xml.sax.saxutils import escape

from . import svgtext
from .model import WIREFRAME_UNAVAILABLE, UIControl, UIReconstruction
from .styles import STRUCTURE_ONLY, StyleCatalog, classify_fidelity

W = 760
PAD = 6
NOTICE = "RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE PANTALLA"
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
FIDELITY_ES = {"STRUCTURE_ONLY": "solo estructura", "STYLE_PARTIAL": "estilo parcial", "STYLE_HIGH_CONFIDENCE": "estilo con alta confianza"}


def _t(text: str) -> str:
    return escape(_CTRL.sub("", str(text)))


def _fit(text: str, width: float, size: float = 11.0) -> str:
    max_chars = max(3, int(width / (size * 0.56)))
    text = " ".join(str(text).split())
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


def _label_of(c) -> str:
    if c.label:
        return c.label
    icon = os.path.basename((c.attrs.get("imageurl") or "").replace("\\", "/"))
    if icon:
        return f"[icono {icon.rsplit('.', 1)[0]}]"
    return c.id


def is_glyph_icon(data_uri: str) -> bool:
    """True when an evidenced image is icon-shaped (about square). A wide bitmap (a legacy button face with its caption baked in) squeezed
    into the 16px icon slot is unreadable and repeats the label already drawn as text, so it is not drawn."""
    try:
        raw = base64.b64decode(data_uri.split(",", 1)[1][:64] + "=" * 4)
        if raw[:6] in (b"GIF87a", b"GIF89a"):
            w, h = struct.unpack("<HH", raw[6:10])
        elif raw[1:4] == b"PNG":
            w, h = struct.unpack(">II", raw[16:24])
        else:
            return True
    except Exception:
        return True
    return h > 0 and w / h <= 1.6


_ICON_PREFIX = re.compile(r"^(?:\[)?(?:icono|icon|ico|img|imagen|btn|boton|ibtn|lnk|hyp|hl)[\s_\-.:]*", re.I)
_CAMEL_SPLIT = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


def display_label(c) -> str:
    """Short, horizontal, human-readable caption of a control for the documentary reconstruction. The model keeps the raw label / id.

    Order: visible text -> icon / identifier normalised for humans (`iconoAsignar` -> `Asignar`, `[icono buscar]` -> `Buscar`) -> `Icono`."""
    if c.label and not re.match(r"^\[(?:icono|icon)", c.label, re.I):
        return c.label
    raw = c.label[1:-1] if c.label else ""
    if not raw:
        raw = os.path.basename((c.attrs.get("imageurl") or "").replace("\\", "/"))
        raw = raw.rsplit(".", 1)[0] if raw else (c.id or "")
    name = _ICON_PREFIX.sub("", raw.strip(" []"))
    if not name:
        return "Icono"
    words = _CAMEL_SPLIT.findall(name) if " " not in name else name.split()
    text = " ".join(w for w in words if w).strip()
    return (text[:1].upper() + text[1:]) if text else "Icono"


_MESSAGE_ID = re.compile(r"^lbl\w*(mensaje|msg|error)", re.I)


def is_symbol_label(c) -> bool:
    """A one/two/three-character label with no letters or digits (`<`, `>>`): a legacy arrow glyph, never a human word."""
    text = (c.label or "").strip()
    return c.kind == "label" and 0 < len(text) <= 3 and not any(ch.isalnum() for ch in text)


def build(view_path: str, markup, source_name: str, event_ids: set[str], styles: StyleCatalog | None = None, code=None) -> UIReconstruction:
    if markup is None or not markup.controls:
        return UIReconstruction(status=WIREFRAME_UNAVAILABLE, source=source_name,
                                reason="la evidencia de la vista no incluye marcado con controles (archivo no disponible o sin controles)")
    by_id: dict[str, object] = {}
    controls: list[UIControl] = []
    for c in markup.controls:
        key = c.id or f"{c.tag}@{c.line}"
        by_id[key] = c
        controls.append(UIControl(id=c.id or key, tag=c.tag, kind=c.kind, label=_label_of(c) if c.kind != "text" else c.label, visible_initially=c.visible,
                                  line=c.line, columns=list(c.columns), bound_to=c.bound_to, event_bound=c.id in event_ids))
    hidden = [c for c in markup.controls if not c.visible and c.kind in ("text", "dropdown", "other", "check")]
    hidden_ids = {c.id for c in hidden}

    # ---- documentary simplification of purely structural geometry (the controls themselves stay in the model)
    def leaves(item):
        if isinstance(item, dict):
            for row in item["rows"]:
                for cell in row["cells"]:
                    for sub in cell["items"]:
                        yield from leaves(sub)
        else:
            yield item

    def simplify(item):
        """A nested table made only of action buttons/links and legacy arrow glyphs (`<`, `>>`) becomes one clean column of buttons: the
        glyphs are layout debris and their direction cannot be established safely, so none is drawn. Message labels go below the actions."""
        if not isinstance(item, dict):
            return item
        ids = [i for i in leaves(item) if i in by_id and by_id[i].id not in hidden_ids]
        kinds = [by_id[i] for i in ids]
        if kinds and all(c.kind in ("button", "link") or is_symbol_label(c) for c in kinds) and any(c.kind in ("button", "link") for c in kinds):
            buttons = [c.id or f"{c.tag}@{c.line}" for c in kinds if c.kind in ("button", "link")]
            return {"rows": [{"cells": [{"items": buttons, "width": "", "attrs": {}}]}], "attrs": {}, "actions": buttons}
        rows = []
        for row in item["rows"]:
            cells = []
            for cell in row["cells"]:
                items = [simplify(i) for i in cell["items"]]
                if any(isinstance(i, dict) and i.get("actions") for i in items):
                    items = ([i for i in items if not (isinstance(i, str) and i in by_id and _MESSAGE_ID.match(by_id[i].id or ""))]
                             + [i for i in items if isinstance(i, str) and i in by_id and _MESSAGE_ID.match(by_id[i].id or "")])
                cells.append({**cell, "items": items})
            rows.append({**row, "cells": cells})
        has_actions = any(isinstance(i, dict) and i.get("actions") for row in rows for cell in row["cells"] for i in cell["items"])

        def message_row(row) -> bool:
            items = [i for cell in row["cells"] for i in cell["items"]]
            return bool(items) and all(isinstance(i, str) and i in by_id and _MESSAGE_ID.match(by_id[i].id or "") for i in items)
        if has_actions:                                    # message placeholders read below the action buttons
            rows = [r for r in rows if not message_row(r)] + [r for r in rows if message_row(r)]
        return {**item, "rows": rows}

    # ---- style evidence per control (never invented)
    resolved: dict[str, dict] = {}
    report = {"controls": len(markup.controls), "visible_controls": sum(1 for c in markup.controls if c.visible), "controls_with_style": 0,
              "controls_with_confirmed_style": 0, "controls_with_inferred_style_only": 0, "classes_resolved": {}, "classes_unresolved": [],
              "icons_total": 0, "icons_resolved": 0, "icons_unresolved": [], "css_sources": list(styles.css_files) if styles else [],
              "shell": styles.shell if styles else "", "dynamic_visibility_assignments": getattr(code, "visible_toggles", 0) if code else 0,
              "script_blocks": getattr(code, "script_blocks", 0) if code else 0}
    icons: dict[str, str] = {}
    if styles is not None:
        unresolved_names: set[str] = set()
        for c in markup.controls:
            key = c.id or f"{c.tag}@{c.line}"
            st, sources, unres = styles.resolve(c.attrs)
            resolved[key] = st
            unresolved_names.update(unres)
            if sources:
                report["controls_with_style"] += 1
                if any(not s.startswith("tipo:") for s in sources):
                    report["controls_with_confirmed_style"] += 1
                else:
                    report["controls_with_inferred_style_only"] += 1
                for s in sources:
                    if s.startswith(("css:", "tipo:")):
                        name = s.split(":", 1)[1].split()[0]
                        report["classes_resolved"][name] = report["classes_resolved"].get(name, 0) + 1
            image = c.attrs.get("imageurl", "")
            if image:
                report["icons_total"] += 1
                data, why = styles.icon(source_name, image)
                if data:
                    if is_glyph_icon(data):
                        icons[key] = data
                    report["icons_resolved"] += 1
                else:
                    report["icons_unresolved"].append(f"{os.path.basename(image.replace(chr(92), '/'))}: {why}")
        report["classes_unresolved"] = sorted(unresolved_names)
    report["classes_resolved"] = dict(sorted(report["classes_resolved"].items()))
    fidelity = classify_fidelity(report) if styles is not None else STRUCTURE_ONLY

    out: list[str] = []

    def rect(x, y, w, h, *, fill="#ffffff", stroke="#6b7280", sw=1, rx=3, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(x, y, s, *, size=11, bold=False, fill="#111827", anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        b = ' font-weight="bold"' if bold else ""
        out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{fill}"{b}{a}>{_t(s)}</text>')

    def sty(c) -> dict:
        return resolved.get(c.id or f"{c.tag}@{c.line}", {})

    def label_size(c) -> float:
        tipo = c.attrs.get("tipo", "").lower()
        return min(18, max(9, sty(c).get("font_size", 13 if tipo == "titulo" else 11)))

    def button_box(c, w: float) -> tuple[float, list[str]]:
        """Width and wrapped caption lines of a button/link: the box widens to its text, then wraps; never clips."""
        label = display_label(c)
        icon = 20 if (c.id or f"{c.tag}@{c.line}") in icons else 0
        want = svgtext.text_width(label, "F2", 11) + 20 + icon
        bw = min(w, max(60, uniform.get(c.id or f"{c.tag}@{c.line}") or sty(c).get("width") or want))
        lines = svgtext.wrap(label, bw - 16 - icon, 11, bold=True)
        return bw, lines

    def control_height(c, w: float | None = None) -> float:
        base = {"label": 20, "text": 26, "dropdown": 26, "button": 30, "link": 30, "grid": 54, "panel": 20, "check": 22, "image": 22, "validator": 18}.get(c.kind, 24)
        h = sty(c).get("height")
        if h and c.kind in ("button", "link", "text", "dropdown"):
            base = max(20, min(40, h + 6))
        if w is not None and c.kind == "label":
            lines = svgtext.wrap(_label_of(c), w, label_size(c), bold=label_bold(c))
            return max(base, 6 + len(lines) * svgtext.line_height(label_size(c)))
        if w is not None and c.kind in ("button", "link"):
            _bw, lines = button_box(c, w)
            return max(base, 10 + len(lines) * svgtext.line_height(11) + 4)
        return base

    def measure_item(item, w: float) -> float:
        if isinstance(item, dict):
            return measure_table(item, w)
        c = by_id.get(item)
        if c is None or c.id in hidden_ids:
            return 0.0
        return control_height(c, w) + 4

    def measure_cell(cell, w: float) -> float:
        return PAD * 2 + sum(measure_item(i, w - 2 * PAD) for i in cell["items"])

    uniform: dict[str, float] = {}                       # action buttons of one column share a width

    def label_bold(c) -> bool:
        return bool(c.label) and (c.attrs.get("tipo", "").lower() in ("titulo", "subtitulo") or sty(c).get("font_weight") == "bold")

    def item_min(item) -> float:
        if isinstance(item, dict):
            return max((sum(cell_min(cell) for cell in row["cells"]) for row in item["rows"] if row["cells"]), default=24.0)
        c = by_id.get(item)
        if c is None or c.id in hidden_ids:
            return 0.0
        if c.kind in ("button", "link"):
            key = c.id or f"{c.tag}@{c.line}"
            icon = 20 if key in icons else 0
            longest = max((svgtext.text_width(word, "F2", 11) for word in display_label(c).split()), default=0)
            return max(uniform.get(key, 0.0), longest + 16 + icon)
        if c.kind == "label":                                # human words keep their whole width: never one character per line
            size, bold = label_size(c), label_bold(c)
            return max((svgtext.text_width(word, "F2" if bold else "F1", size) for word in _label_of(c).split()), default=0) + 2
        if c.kind in ("text", "dropdown"):
            return 84.0
        return 24.0

    def cell_min(cell) -> float:
        """Smallest width in which every control of the cell keeps horizontal, whole-word captions."""
        return max([24.0] + [item_min(i) + 2 * PAD for i in cell["items"]])

    def cell_widths(row, w: float) -> list[float]:
        n = max(1, len(row["cells"]))
        fixed = []
        for cell in row["cells"]:
            m = re.match(r"(\d+)(px|%)", str(cell.get("width") or ""))
            if m:
                fixed.append(int(m.group(1)) if m.group(2) == "px" else w * int(m.group(1)) / 100)
            else:
                fixed.append(None)
        free = [i for i, f in enumerate(fixed) if f is None]
        used = sum(f for f in fixed if f is not None)
        if used > w * 0.9:
            widths = [w / n] * n
        else:
            share = (w - used) / len(free) if free else 0
            widths = [f if f is not None else share for f in fixed]
            if not free:
                scale = w / (sum(widths) or 1)
                widths = [x * scale for x in widths]
        mins = [cell_min(cell) for cell in row["cells"]]
        widths = [max(x, m) for x, m in zip(widths, mins)]
        excess = sum(widths) - w
        if excess > 0:                                   # rebalance: take the excess from cells that are wider than they need to be
            slack = [max(0.0, x - m) for x, m in zip(widths, mins)]
            total = sum(slack)
            if total > 0:
                take = min(excess, total)
                widths = [x - take * sl / total for x, sl in zip(widths, slack)]
        return widths

    def measure_table(table, w: float) -> float:
        total = 0.0
        for row in table["rows"]:
            if not row["cells"]:
                continue
            ws = cell_widths(row, w)
            total += max(measure_cell(c, cw) for c, cw in zip(row["cells"], ws))
        return total

    def draw_control(c, x, y, w):
        h = control_height(c, w)
        st = sty(c)
        label = _label_of(c)
        if c.kind in ("button", "link"):
            label = display_label(c)
        ink = st.get("color", "#111827")
        key = c.id or f"{c.tag}@{c.line}"
        if c.kind == "label":
            tipo = c.attrs.get("tipo", "").lower()
            size = label_size(c)
            bold = label_bold(c)
            ly = y
            for line in svgtext.wrap(label, w, size, bold=bold):
                ly += svgtext.line_height(size)
                # an empty message placeholder (`lblMensaje1`) is shown quietly, not as a title
                text(x, ly - 3, line, size=size, bold=bold, fill=(ink if st.get("color") else "#111827") if c.label else "#6b7280")
        elif c.kind in ("text", "check"):
            bw = min(w, st.get("width", 220))
            rect(x, y, bw, h - 4, stroke=st.get("border", "#6b7280"), sw=max(1, st.get("border_width", 1)), rx=st.get("radius", 3),
                 dash="" if c.visible else "3 3")
            text(x + 6, y + 15, _fit(f"[{c.id}]", bw - 10, 10), size=10, fill="#6b7280")
        elif c.kind == "dropdown":
            bw = min(w, st.get("width", 220))
            rect(x, y, bw, h - 4, stroke=st.get("border", "#6b7280"), sw=max(1, st.get("border_width", 1)), rx=st.get("radius", 3))
            text(x + 6, y + 15, _fit(f"[{c.id}]", bw - 24, 10), size=10, fill="#6b7280")
            text(x + bw - 12, y + 15, "v", size=10, bold=True)
        elif c.kind in ("button", "link"):
            fill = st.get("background")
            has_fill = bool(fill and fill != "none")
            bw, lines = button_box(c, w)
            rect(x, y, bw, h - 4, fill=fill if has_fill else "#eef2ff", stroke=st.get("border", "#1e3a8a" if not has_fill else fill),
                 sw=1.5 if not has_fill else 1, rx=st.get("radius", 5))
            tx = x + 8
            if key in icons:
                out.append(f'<image x="{x + 5:.0f}" y="{y + 4:.0f}" width="16" height="16" href="{icons[key]}"/>')
                tx += 20
            tcolor = ink if st.get("color") else ("#ffffff" if has_fill else "#1e3a8a")
            ly = y + 5
            for line in lines:
                ly += svgtext.line_height(11)
                text(tx, ly, line, size=11, bold=True, fill=tcolor)
        elif c.kind == "grid":
            cols = c.columns or []
            rect(x, y, w, h - 4, fill="#f9fafb", stroke="#374151")
            if cols:
                cw = w / max(1, min(len(cols), 8))
                for k, title in enumerate(cols[:8]):
                    rect(x + k * cw, y, cw, 22, fill="#e5e7eb", stroke="#374151", rx=0)
                    text(x + k * cw + 4, y + 15, _fit(title, cw - 6, 10), size=10, bold=True)
                if len(cols) > 8:
                    text(x + w - 4, y + 15, f"+{len(cols) - 8}", size=10, anchor="end")
            else:
                text(x + 6, y + 15, "grilla (sin columnas declaradas)", size=10, fill="#6b7280")
            text(x + 6, y + 40, _fit(f"Datos enlazados: {c.bound_to}" if c.bound_to else f"Grilla [{c.id}]", w - 12, 10), size=10, fill="#6b7280")
        elif c.kind == "panel":
            rect(x, y, w, h - 4, fill="#f3f4f6", stroke="#9ca3af", dash="4 3")
            text(x + 6, y + 14, _fit(f"Panel [{c.id}]", w - 12, 10), size=10, fill="#374151")
        else:
            rect(x, y, min(w, 220), h - 4, stroke="#9ca3af", dash="2 2")
            text(x + 6, y + 15, _fit(f"{c.tag} [{c.id}]", min(w, 220) - 10, 10), size=10, fill="#6b7280")

    def block_style(attrs: dict) -> dict:
        if styles is None or not attrs:
            return {}
        st, _src, _un = styles.resolve({"class": attrs.get("class", ""), "style": attrs.get("style", "")})
        if attrs.get("bgcolor"):
            from .styles import _color
            c = _color(attrs["bgcolor"])
            if c and c != "none":
                st["background"] = c
        return st

    def draw_item(item, x, y, w) -> float:
        if isinstance(item, dict):
            return draw_table(item, x, y, w)
        c = by_id.get(item)
        if c is None or c.id in hidden_ids:
            return 0.0
        draw_control(c, x, y, w)
        return control_height(c, w) + 4

    def draw_table(table, x, y, w) -> float:
        total = 0.0
        tstyle = block_style(table.get("attrs", {}))
        for row in table["rows"]:
            if not row["cells"]:
                continue
            ws = cell_widths(row, w)
            height = max(measure_cell(c, cw) for c, cw in zip(row["cells"], ws))
            cx = x
            for cell, cw in zip(row["cells"], ws):
                cst = {**tstyle, **block_style(cell.get("attrs", {}))}
                if cell["items"]:
                    bg = cst.get("background")
                    rect(cx, y + total, cw, height, fill=bg if bg and bg != "none" else "none", stroke=cst.get("border", "#d1d5db"), rx=0)
                iy = y + total + PAD
                for it in cell["items"]:
                    iy += draw_item(it, cx + PAD, iy, cw - 2 * PAD)
                cx += cw
            total += height
        return total

    original_root = markup.skeleton()
    root = [simplify(i) for i in original_root]

    def share_action_width(item) -> None:
        if not isinstance(item, dict):
            return
        if item.get("actions"):
            members = [by_id[i] for i in item["actions"]]
            width = max(svgtext.text_width(display_label(c), "F2", 11) + 20 + (20 if (c.id or f"{c.tag}@{c.line}") in icons else 0) for c in members)
            for c in members:
                uniform[c.id or f"{c.tag}@{c.line}"] = max(60.0, width)
        for row in item["rows"]:
            for cell in row["cells"]:
                for sub in cell["items"]:
                    share_action_width(sub)
    for it in root:
        share_action_width(it)
    top = 54
    body_height = sum(measure_item(i, W - 2 * PAD) for i in root) + 2 * PAD
    y = float(top)
    for it in root:
        y += draw_item(it, PAD, y + PAD, W - 2 * PAD)
    height = int(top + body_height + (28 if hidden else 0) + 18)
    note = FIDELITY_ES[fidelity]
    header = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="11">',
        f"<title>{_t('Reconstrucción documental de ' + os.path.basename(view_path.replace(chr(92), '/')).rsplit('.', 1)[0])}</title>",
        f'<rect x="0" y="0" width="{W}" height="{height}" fill="#ffffff"/>',
        f'<rect x="0" y="0" width="{W}" height="22" fill="#fef3c7" stroke="#b45309" stroke-width="1"/>',
        f'<text x="8" y="15" font-size="11" font-weight="bold" fill="#92400e">{_t(NOTICE)}</text>',
        f'<text x="8" y="40" font-size="11" fill="#4b5563">{_t(_fit("Aproximación desde el marcado persistido (" + note + ")", W - 16, 11))}</text>',
    ]
    if hidden:
        out.append(f'<text x="8" y="{height - 12}" font-size="10" fill="#6b7280">{_t(_fit("Campos ocultos inicialmente (no dibujados): " + ", ".join(sorted(hidden_ids)), W - 16, 10))}</text>')
    svg = "\n".join(header + out + ["</svg>"]) + "\n"
    rows = _skeleton_ids(original_root, hidden_ids)
    return UIReconstruction(status="DOCUMENTARY_RECONSTRUCTION", source=source_name, controls=controls, rows=rows, svg=svg, fidelity=fidelity,
                            style_report=report)


def _skeleton_ids(items, hidden_ids) -> list:
    rows: list = []

    def walk(item):
        if isinstance(item, dict):
            for row in item["rows"]:
                rows.append([[i for i in cell["items"] if isinstance(i, str) and i not in hidden_ids] for cell in row["cells"]])
                for cell in row["cells"]:
                    for sub in cell["items"]:
                        if isinstance(sub, dict):
                            walk(sub)
    for it in items:
        walk(it)
    return rows
