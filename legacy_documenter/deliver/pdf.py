"""Dependency-free, deterministic PDF writer for the H4 package (post-V5 H4).

Why hand-written: the core runtime has no third-party dependencies and the H4 contract forbids a browser/network service.
This writer uses only the 14 standard PDF fonts (Helvetica / Courier, WinAnsi), so it renders anywhere offline, and it draws
the H3 SVG diagrams as vector graphics (rect / text / bezier path -- the only elements the H3 renderer emits).

Determinism: no timestamps, no random ids; object order and content are a pure function of the input blocks. Streams are
deflated with zlib, which is stable for one Python/zlib build; a toolchain-independent `content_sha256` over the
UNCOMPRESSED page streams is reported as well.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass, field
from pathlib import Path

from .markdown import Bullets, Callout, Code, Details, Figure, Heading, Para, Quote, Rule, Run, Table, plain

# ---------------------------------------------------------------- font metrics (Adobe AFM, 1/1000 em)
_ASCII = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
_HELV = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556,
         278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778, 667, 778, 722, 667,
         611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
         556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]
_HELV_B = [278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556,
           333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778, 667, 778, 722, 667,
           611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556, 333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889,
           611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584]
assert len(_ASCII) == len(_HELV) == len(_HELV_B) == 95
_WIDTH = {"F1": dict(zip(_ASCII, _HELV)), "F2": dict(zip(_ASCII, _HELV_B))}
_WIDTH["F3"] = _WIDTH["F1"]
_WIDTH["F5"] = _WIDTH["F2"]
_EXTRA = {"«": 556, "»": 556, "·": 278, "—": 1000, "–": 556, "…": 1000, "“": 333, "”": 333, "‘": 222, "’": 222, "•": 350, "€": 556,
          "¿": 611, "¡": 333, "º": 365, "ª": 370, "×": 584, "°": 400, "§": 556, "©": 737, "®": 737, "±": 584, "µ": 556, "¶": 537}
_REPLACE = {"→": "->", "←": "<-", "↔": "<->", "✓": "OK", "✔": "OK", "✗": "x", "≥": ">=", "≤": "<=", "≠": "!=", " ": " ", "‑": "-",
            " ": " ", "​": "", "•": "•", "−": "-", "’": "’"}
FONT_NAMES = {"F1": "Helvetica", "F2": "Helvetica-Bold", "F3": "Helvetica-Oblique", "F4": "Courier", "F5": "Helvetica-BoldOblique"}

_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _identifier_parts(piece: str) -> list[str]:
    """Long identifiers (`ucPreCargaArchivoAsignacion`) may wrap at camelCase word boundaries -- never in the middle of a word."""
    if len(piece) < 14 or piece.isspace():
        return [piece]
    return [p for p in _CAMEL.split(piece) if p] or [piece]


def norm(text: str) -> str:
    """Characters outside WinAnsi are transliterated (documented in the manifest as `pdf_text_replacements`)."""
    text = _CTRL.sub("", text)
    out = []
    for ch in text:
        if ch in _REPLACE:
            out.append(_REPLACE[ch])
            continue
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            base = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode("ascii")
            out.append(base or "?")
    return "".join(out)


def char_width(ch: str, font: str) -> int:
    if font == "F4":
        return 600
    w = _WIDTH[font].get(ch)
    if w is not None:
        return w
    if ch in _EXTRA:
        return _EXTRA[ch]
    base = unicodedata.normalize("NFKD", ch)[:1]
    return _WIDTH[font].get(base, 556)


def text_width(text: str, font: str, size: float) -> float:
    return sum(char_width(c, font) for c in text) * size / 1000.0


def _pdf_str(text: str) -> str:
    data = norm(text).encode("cp1252", "replace").decode("latin-1")
    return "(" + data.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ")"


def _num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


# ---------------------------------------------------------------- status look (same patterns as the H3 SVG)
STATUS = {  # text label -> (stroke RGB, dash, width, prefix)
    "Confirmado": ((0.118, 0.227, 0.541), "", 1.0, ""),
    "Inferido (regla estructural)": ((0.706, 0.325, 0.035), "4 2", 1.0, ""),
    "Inferido (regla)": ((0.706, 0.325, 0.035), "4 2", 1.0, ""),
    "No resuelto": ((0.725, 0.110, 0.110), "1 2", 1.0, "! "),
    "Interpretación de IA (no aprobada)": ((0.427, 0.157, 0.851), "5 2 1 2", 1.0, "IA - "),
    "Canónico (aprobado por una persona)": ((0.016, 0.471, 0.341), "", 2.0, "OK - "),
}
INK = (0.07, 0.09, 0.15)
MUTED = (0.29, 0.33, 0.39)
LINE = (0.62, 0.64, 0.68)
SOFT = (0.95, 0.96, 0.97)


def _rgb(c: tuple) -> str:
    return " ".join(_num(x) for x in c)


def _hex(c: str, default=(0, 0, 0)):
    if c and c.startswith("#") and len(c) == 7:
        return tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return default


@dataclass
class _Page:
    width: float
    height: float
    ops: list[str] = field(default_factory=list)
    footer: bool = True


@dataclass
class _Outline:
    title: str
    level: int
    page: int
    y: float


# ---------------------------------------------------------------- the document builder
class PdfDocument:
    def __init__(self, title: str, *, footer_title: str = "", row_cap: int = 30) -> None:
        self.title = title
        self.footer_title = footer_title or title
        self.row_cap = row_cap
        self.pages: list[_Page] = []
        self.outlines: list[_Outline] = []
        self.stats = {"tables_truncated": 0, "figures_drawn": 0, "figures_as_text": 0, "figure_pages": 0, "text_replacements": 0}
        self.toc: list[tuple[str, int, int]] = []
        self._seen_figures: dict[str, int] = {}
        self.style: dict = {}              # template-provided presentation (sizes/colours); {} keeps the built-in defaults
        self.legend_labels: tuple | None = None   # state labels explained on the cover; None = all five
        self.toc_levels: tuple = (1,)      # heading levels listed in the contents page
        self.outline_levels: tuple = (1, 2)
        self._cur: _Page | None = None
        self._y = 0.0
        self.M = 48.0
        self.R = 48.0
        self.PW, self.PH = 595.0, 842.0

    # -- page management
    @property
    def content_width(self) -> float:
        return self.PW - self.M - self.R

    def new_page(self, *, landscape: bool = False, footer: bool = True) -> _Page:
        w, h = (842.0, 595.0) if landscape else (595.0, 842.0)
        page = _Page(w, h, footer=footer)
        self.pages.append(page)
        self._cur = page
        self._y = h - self.M
        return page

    def _ensure(self, needed: float) -> None:
        if self._cur is None or self._cur.width != self.PW or self._y - needed < 48.0 + 14:
            self.new_page()

    def _emit(self, op: str) -> None:
        assert self._cur is not None
        self._cur.ops.append(op)

    # -- low-level drawing
    def _text_at(self, x: float, y: float, text: str, font: str, size: float, color=INK) -> None:
        if not text:
            return
        self._emit(f"BT {_rgb(color)} rg /{font} {_num(size)} Tf {_num(x)} {_num(y)} Td {_pdf_str(text)} Tj ET")

    def _rect(self, x: float, y: float, w: float, h: float, *, stroke=None, fill=None, width: float = 0.6, dash: str = "") -> None:
        ops = ["q"]
        if fill is not None:
            ops.append(f"{_rgb(fill)} rg")
        if stroke is not None:
            ops.append(f"{_rgb(stroke)} RG {_num(width)} w [{dash}] 0 d")
        paint = "B" if fill is not None and stroke is not None else ("f" if fill is not None else "S")
        ops.append(f"{_num(x)} {_num(y)} {_num(w)} {_num(h)} re {paint} Q")
        self._emit(" ".join(ops))

    def _line(self, x1: float, y1: float, x2: float, y2: float, color=LINE, width: float = 0.5) -> None:
        self._emit(f"q {_rgb(color)} RG {_num(width)} w {_num(x1)} {_num(y1)} m {_num(x2)} {_num(y2)} l S Q")

    # -- text layout
    @staticmethod
    def _font_of(run: Run, base_bold: bool = False) -> str:
        if run.code:
            return "F4"
        bold = run.bold or base_bold
        if bold and run.italic:
            return "F5"
        if bold:
            return "F2"
        return "F3" if run.italic else "F1"

    def _tokens(self, runs: list[Run], size: float, base_bold: bool = False) -> list[tuple[str, str, float, float]]:
        """(text, font, size, width) pieces; breakable after spaces and after path/identifier separators."""
        tokens: list[tuple[str, str, float, float]] = []
        for run in runs:
            font = self._font_of(run, base_bold)
            fsize = size * (0.92 if run.code else 1.0)
            text = norm(run.text)
            for piece in re.findall(r"\s+|[^\s\\/._,;:()\-]+[\\/._,;:()\-]?|[\\/._,;:()\-]", text):
                for part in _identifier_parts(piece):
                    tokens.append((part, font, fsize, text_width(part, font, fsize)))
        return tokens

    def _wrap(self, tokens: list[tuple[str, str, float, float]], width: float) -> list[list[tuple[str, str, float, float]]]:
        lines: list[list[tuple[str, str, float, float]]] = []
        cur: list[tuple[str, str, float, float]] = []
        used = 0.0
        for tok in tokens:
            text, font, size, w = tok
            if text.isspace():
                if cur:
                    cur.append((" ", font, size, text_width(" ", font, size)))
                    used += cur[-1][3]
                continue
            if used + w <= width or not cur and w <= width:
                cur.append(tok)
                used += w
                continue
            if cur:  # break before this token
                while cur and cur[-1][0] == " ":
                    used -= cur[-1][3]
                    cur.pop()
                lines.append(cur)
                cur, used = [], 0.0
            if w <= width:
                cur, used = [tok], w
                continue
            chunk, cw = "", 0.0  # hard-break an over-long unbroken token by characters
            for ch in text:
                chw = char_width(ch, font) * size / 1000.0
                if cw + chw > width and chunk:
                    lines.append([(chunk, font, size, cw)])
                    chunk, cw = "", 0.0
                chunk += ch
                cw += chw
            cur, used = ([(chunk, font, size, cw)] if chunk else []), cw
        if cur:
            while cur and cur[-1][0] == " ":
                cur.pop()
            if cur:
                lines.append(cur)
        return lines or [[]]

    def _draw_line(self, x: float, y: float, line: list[tuple[str, str, float, float]], color=INK) -> None:
        cx = x
        for text, font, size, w in line:
            if text != " ":
                self._text_at(cx, y, text, font, size, color)
            cx += w

    @staticmethod
    def _justify(line: list, width: float) -> list:
        """Spreads the spare width over the inter-word spaces of a full line (never over-stretches)."""
        spaces = [i for i, t in enumerate(line) if t[0] == " "]
        used = sum(t[3] for t in line)
        extra = width - used
        if not spaces or extra <= 0:
            return line
        per = extra / len(spaces)
        if per > 2.2 * line[spaces[0]][3]:
            return line
        return [(t[0], t[1], t[2], t[3] + per) if t[0] == " " else t for t in line]

    def paragraph(self, runs: list[Run], *, size: float = 9.5, indent: float = 0.0, width: float | None = None, color=INK,
                  bold: bool = False, space_after: float | None = None, leading: float = 1.28, prefix: str = "", justify: bool = False) -> None:
        width = (width if width is not None else self.content_width) - indent
        tokens = self._tokens(([Run(prefix)] if prefix else []) + runs, size, bold)
        lines = self._wrap(tokens, width)
        lead = size * leading
        after = float(self.style.get("paragraph_space", 6)) if space_after is None else space_after
        for index, line in enumerate(lines):
            self._ensure(lead)
            self._y -= lead
            if justify and index < len(lines) - 1:
                line = self._justify(line, width)
            self._draw_line(self.M + indent, self._y, line, color)
        self._y -= after

    def heading(self, level: int, runs: list[Run]) -> None:
        sizes = {1: 16, 2: 12.5, 3: 11, 4: 10, 5: 10, 6: 10}
        sizes.update({int(k): v for k, v in (self.style.get("heading_sizes") or {}).items()})
        size = sizes.get(level, 10)
        before = {1: 14, 2: 12, 3: 9}.get(level, 6)
        before = float((self.style.get("heading_before") or {}).get(level, before))
        after = float((self.style.get("heading_after") or {}).get(level, 4))
        align = (self.style.get("heading_align") or {}).get(level, "left")
        color = tuple(self.style.get("heading_colors", {}).get(level, INK)) if isinstance(self.style.get("heading_colors"), dict) else INK
        text = plain(runs)
        hlines = self._wrap(self._tokens(runs, size, True), self.content_width) if text else [[]]
        self._ensure(size * (1.25 * len(hlines) + 1) + before)
        self._y -= before
        outline_page = len(self.pages) - 1
        first_top = self._y
        for k, hl in enumerate(hlines):
            self._y -= size * (1.0 if k == 0 else 1.25)
            if align == "center":
                width_line = sum(t[3] for t in hl)
                self._draw_line(self.M + (self.content_width - width_line) / 2, self._y, [(a, "F2", c, d) for a, _b, c, d in hl], color)
            else:
                self._draw_line(self.M, self._y, [(a, "F2", c, d) for a, _b, c, d in hl], color)
        if level in self.outline_levels:
            top = min(self.outline_levels)
            self.outlines.append(_Outline(norm(text), 0 if level == top else 1, outline_page, first_top))
        if level in self.toc_levels:
            self.toc.append((norm(text), outline_page, level))
        if level <= 2 and self.style.get("heading_rule", level == 1):
            self._line(self.M, self._y - 3, self.M + self.content_width, self._y - 3, INK, 0.8 if level == 1 else 0.5)
            self._y -= 6
        self._y -= after

    def bullets(self, items: list[list[Run]], size: float = 9.5) -> None:
        for item in items:
            tokens = self._tokens(item, size)
            lines = self._wrap(tokens, self.content_width - 14)
            lead = size * 1.28
            for k, line in enumerate(lines):
                self._ensure(lead)
                self._y -= lead
                if k == 0:
                    self._text_at(self.M + 3, self._y, "•", "F1", size)
                self._draw_line(self.M + 14, self._y, line)
            self._y -= 2
        self._y -= 4

    def _box(self, blocks: list, *, stroke, dash: str, width: float, title: str = "") -> None:
        """Draws `blocks` indented, with a left bar on every page piece it spans (page-break safe)."""
        self._ensure(30)
        if title:
            self.paragraph([Run(title, bold=True)], size=9.5, color=stroke, space_after=3)
        top_page, top_y = len(self.pages) - 1, self._y
        self.M += 10
        for block in blocks:
            self._block(block)
        self.M -= 10
        for pi in range(top_page, len(self.pages)):
            page = self.pages[pi]
            if page.width != self.PW:
                continue
            y_top = top_y + 4 if pi == top_page else page.height - 48.0
            y_bot = self._y + 2 if pi == len(self.pages) - 1 else 48.0 + 14
            page.ops.append(f"q {_rgb(stroke)} RG {_num(width * 2.5)} w [{dash}] 0 d {_num(self.M + 3)} {_num(y_top)} m {_num(self.M + 3)} {_num(y_bot)} l S Q")
        self._y -= 4

    # -- tables
    def table(self, tbl: Table) -> None:
        headers = [plain(h) for h in tbl.headers]
        n = len(headers)
        rows = tbl.rows
        total = len(rows)
        if total > self.row_cap:
            rows = rows[:self.row_cap]
            self.stats["tables_truncated"] += 1
        size = 8.0
        pad = 3.0
        avail = self.content_width
        cells_tokens = [[self._tokens(h, size, True) for h in tbl.headers]]
        for row in rows:
            cells_tokens.append([self._tokens(c, size) for c in row])
        natural = [0.0] * n
        longest = [0.0] * n
        for row in cells_tokens:
            for ci, toks in enumerate(row):
                natural[ci] = max(natural[ci], sum(t[3] for t in toks))
                longest[ci] = max([longest[ci]] + [min(t[3], 70.0) for t in toks if not t[0].isspace()])
        natural = [w + 2 * pad for w in natural]
        longest = [max(w + 2 * pad, 28.0) for w in longest]
        if sum(natural) <= avail:
            widths = natural[:]
            spare = avail - sum(widths)
            widths = [w + spare * (w / sum(natural)) for w in widths] if sum(natural) else widths
        else:
            widths = longest[:]
            spare = avail - sum(widths)
            if spare < 0:  # even the minimum widths do not fit: scale down evenly
                widths = [w * avail / sum(widths) for w in widths]
            else:
                want = [max(0.0, natural[i] - longest[i]) for i in range(n)]
                total_want = sum(want) or 1.0
                widths = [widths[i] + spare * want[i] / total_want for i in range(n)]
        x_edges = [self.M]
        for w in widths:
            x_edges.append(x_edges[-1] + w)

        def row_lines(tokens_row, bold_first=False):
            lines = [self._wrap(toks, widths[ci] - 2 * pad) for ci, toks in enumerate(tokens_row)]
            return lines, max(len(l) for l in lines)

        lead = size * 1.25

        def draw_row(tokens_row, texts, header: bool) -> None:
            lines, count = row_lines(tokens_row)
            count = min(count, 40)
            height = count * lead + 2 * pad
            if self._y - height < self.M + 14:
                self.new_page()
                if not header:
                    draw_row(header_tokens, headers, True)
            top = self._y
            if header:
                self._rect(self.M, top - height, sum(widths), height, fill=SOFT)
            for ci, cell_lines in enumerate(lines):
                label = texts[ci] if ci < len(texts) else ""
                st = STATUS.get(label.strip())
                x0 = x_edges[ci]
                if st and not header:
                    color, dash, lw, _prefix = st
                    self._rect(x0 + 1.5, top - height + 1.5, widths[ci] - 3, height - 3, stroke=color, width=lw, dash=dash)
                    if label.strip() == "Interpretación de IA (no aprobada)":
                        self._rect(x0 + 3.5, top - height + 3.5, widths[ci] - 7, height - 7, stroke=color, width=0.6)
                yy = top - pad
                for line in cell_lines[:count]:
                    yy -= lead
                    self._draw_line(x0 + pad, yy + 2.2, line, st[0] if (st and not header) else INK)
                if len(cell_lines) > count:
                    self._text_at(x0 + pad, top - height + 2, "…", "F1", size)
            self._line(self.M, top - height, self.M + sum(widths), top - height)
            if header:
                self._line(self.M, top, self.M + sum(widths), top, INK, 0.8)
            self._y = top - height

        header_tokens = cells_tokens[0]
        # keep the header together with the first rows (no header + one row at a page bottom); short tables stay whole when they fit a page
        row_heights = [min(row_lines(t)[1], 40) * lead + 2 * pad for t in cells_tokens]
        need = row_heights[0] + sum(row_heights[1:4] if len(row_heights) > 5 else row_heights[1:])
        self._ensure(min(need, 330.0) + 8)
        draw_row(header_tokens, headers, True)
        for tokens_row, row in zip(cells_tokens[1:], rows):
            draw_row(tokens_row, [plain(c) for c in row], False)
        # vertical rules are intentionally omitted: wrapped text + row rules keep the page uncluttered and never clipped
        if total > self.row_cap:
            self._y -= 3
            self.paragraph([Run(f"Se muestran {self.row_cap} de {total} filas en este PDF; la lista completa está en el paquete HTML.", italic=True)],
                           size=8.5, color=MUTED)
        self._y -= 6

    # -- blocks
    def _block(self, b) -> None:
        if isinstance(b, Heading):
            self.heading(b.level, b.runs)
        elif isinstance(b, Para):
            role = {"technical": ("technical_size", 8.5, MUTED), "evidence": ("evidence_size", 7.5, MUTED), "caption": ("caption_size", 8.0, MUTED)}.get(b.cls)
            if role:
                key, default, color = role
                self.paragraph(b.runs, size=float(self.style.get(key, default)), color=color, space_after=3)
            else:
                self.paragraph(b.runs, size=float(self.style.get("body_size", 9.5)), justify=bool(self.style.get("justify", False)))
        elif isinstance(b, Quote):
            self._box(b.blocks, stroke=LINE, dash="", width=1.2)
        elif isinstance(b, Callout):
            style = {"semantic": ((0.706, 0.325, 0.035), "4 2"), "unresolved": ((0.725, 0.110, 0.110), "1 2"),
                     "note": ((0.118, 0.227, 0.541), ""), "ai": ((0.427, 0.157, 0.851), "5 2 1 2"), "ai-notice": ((0.427, 0.157, 0.851), "5 2 1 2")}.get(b.kind, (INK, ""))
            self._box(b.blocks, stroke=style[0], dash=style[1], width=1.4, title=b.title)
        elif isinstance(b, Details):
            self.paragraph([Run(b.summary, bold=True)], size=9.5, space_after=2)
            for x in b.blocks:
                self._block(x)
        elif isinstance(b, Bullets):
            self.bullets(b.items)
        elif isinstance(b, Table):
            self.table(b)
        elif isinstance(b, Code):
            self.paragraph([Run(b.text, code=True)], size=8.5)
        elif isinstance(b, Rule):
            self._ensure(10)
            self._y -= 5
            self._line(self.M, self._y, self.M + self.content_width, self._y)
            self._y -= 5
        elif isinstance(b, Figure):
            self.figure(b)

    def blocks(self, blocks: list) -> None:
        for index, b in enumerate(blocks):
            nxt = blocks[index + 1] if index + 1 < len(blocks) else None
            if isinstance(b, Heading) and b.level >= 2 and isinstance(nxt, Figure):
                continue  # the diagram pages carry their own title; avoids an orphaned heading at a page bottom
            nxt2 = blocks[index + 2] if index + 2 < len(blocks) else None
            if isinstance(b, Heading) and b.level >= 3 and isinstance(nxt, Para) and nxt.cls == "caption" and isinstance(nxt2, Figure):
                continue  # heading + caption of a figure: the figure page carries its own title and disclaimer
            if isinstance(b, Para) and b.cls == "caption" and isinstance(nxt, Figure) and index > 0 and isinstance(blocks[index - 1], Heading):
                continue
            if isinstance(b, Heading) and b.level >= 3 and nxt is not None:
                self._ensure(78)          # a heading is never the last thing on a page
            elif isinstance(b, Heading) and nxt is not None:
                self._ensure(110)         # a section heading keeps at least a few lines of its content with it
            self._block(b)

    # -- figures (vector SVG on landscape pages, sliced between nodes when tall)
    assets_root: Path | None = None

    def figure(self, fig: Figure) -> None:
        svg_text = None
        if self.assets_root is not None:
            try:
                svg_text = (self.assets_root / fig.svg).read_text(encoding="utf-8")
            except OSError:
                svg_text = None
        if fig.svg in self._seen_figures:  # the same diagram is not drawn twice in one PDF
            self.stats["figures_referenced"] = self.stats.get("figures_referenced", 0) + 1
            self.paragraph([Run(f"[Diagrama] {fig.title}: ya incluido en la página {self._seen_figures[fig.svg]} de este documento.", italic=True)],
                           size=8.5, color=MUTED)
            return
        first_page = len(self.pages) + 1
        if svg_text is not None and fig.kind == "wireframe":
            placed = self._wireframe_pages(fig, svg_text)
        else:
            placed = svg_text is not None and self._figure_pages(fig, svg_text)
        if placed:
            self._seen_figures[fig.svg] = first_page
            self.stats["figures_drawn"] += 1
            self._cur = None  # text continues on a fresh portrait page
            return
        self.stats["figures_as_text"] += 1
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(fig.status_counts.items()))
        self.paragraph([Run(f"[Diagrama] {fig.title}", bold=True)], space_after=1)
        self.paragraph([Run(f"{fig.kind} · {fig.nodes} nodos · {fig.edges} relaciones · estados ({counts}). Demasiado denso para imprimirse de forma "
                            f"legible: consulte el SVG «{fig.svg}» en el paquete HTML.", italic=True)], size=8.5, color=MUTED)

    MIN_SCALE = 0.5

    LEGEND_TEXT = ("Estados: CONFIRMADO (borde continuo) · INFERIDO (discontinuo) · NO RESUELTO (punteado, marca !) · "
                   "IA - NO APROBADA (doble borde) · CANÓNICO (borde grueso, marca OK)")

    @staticmethod
    def _fit(sw: float, sh: float, landscape: bool) -> tuple[float, float, float]:
        """(scale, avail_w, avail_h) of a diagram on a landscape / portrait page: never enlarged, aspect ratio kept."""
        pw, ph = (842.0, 595.0) if landscape else (595.0, 842.0)
        avail_w, avail_h = pw - 72.0, ph - 36 - 62 - 46 - (0 if landscape else 10)   # portrait: the state legend wraps to two lines
        scale = min(1.0, avail_w / sw)
        if sh * scale > avail_h and avail_h / sh >= 0.62:
            scale = avail_h / sh                      # one page at a still-readable scale beats a split
        return scale, avail_w, avail_h

    def _figure_pages(self, fig: Figure, svg_text: str) -> bool:
        try:
            root = ET.fromstring(svg_text)
        except ET.ParseError:
            return False
        sw, sh = float(root.get("width", "0")), float(root.get("height", "0"))
        if sw <= 0 or sh <= 0:
            return False
        # orientation: the one that needs fewer pages, then the larger (more readable) scale
        options = []
        for landscape in (True, False):
            scale, avail_w, avail_h = self._fit(sw, sh, landscape)
            parts = max(1, -(-int(sh * scale * 100) // int(avail_h * 100)))
            if scale >= self.MIN_SCALE:
                options.append((parts, -scale, not landscape, landscape))
        if not options:
            return False
        landscape = min(options)[3]
        scale, avail_w, avail_h = self._fit(sw, sh, landscape)
        if scale < self.MIN_SCALE:
            return False
        cuts = _slice_positions(root, sh, avail_h / scale)
        if len(cuts) - 1 > 6:
            return False
        pw, ph = (842.0, 595.0) if landscape else (595.0, 842.0)
        view = _view_group(root)
        for index in range(len(cuts) - 1):
            page = self.new_page(landscape=landscape)
            part = f" — parte {index + 1} de {len(cuts) - 1}" if len(cuts) > 2 else ""
            self._text_at(36, ph - 36 - 12, norm(fig.title)[:120] + part, "F2", 11)
            self._text_at(36, ph - 36 - 26, norm(f"{fig.kind} · {fig.nodes} nodos · {fig.edges} relaciones · {fig.scope_label}")[:150], "F1", 8.5, MUTED)
            top_pdf = ph - 36 - 38
            ox = 36 + (avail_w - sw * scale) / 2
            y0, y1 = cuts[index], cuts[index + 1]
            clip_h = (y1 - y0) * scale
            page.ops.append(f"q {_num(36)} {_num(top_pdf - clip_h)} {_num(avail_w)} {_num(clip_h)} re W n")
            drawer = _SvgDrawer(page.ops, ox, top_pdf, scale, y0, y1)
            if view is not None and len(cuts) > 2:
                drawer.pin_view(view)  # every part repeats the origin node so no connector dangles from a previous page
            drawer.walk(root)
            page.ops.append("Q")
            legend = self._wrap(self._tokens([Run(self.LEGEND_TEXT)], 7.5), avail_w)
            for k, line in enumerate(reversed(legend)):
                self._text_at(36, 36 + 22 + 9 * k, "".join(t[0] for t in line), "F1", 7.5, MUTED)
            self._text_at(36, 36 + 11, norm(f"Fuente: {fig.svg} (SVG completo y modelo JSON en el paquete HTML)")[:170], "F1", 7.5, MUTED)
            self.stats["figure_pages"] += 1
        return True

    WIREFRAME_MIN_SCALE = 0.62

    def _wireframe_pages(self, fig: Figure, svg_text: str) -> bool:
        """Documentary reconstruction on portrait pages: one page scaled to fit when still readable; otherwise cut only between controls /
        groups (never through a button, icon, label or row), keeping every part at the same scale."""
        try:
            root = ET.fromstring(svg_text)
        except ET.ParseError:
            return False
        sw, sh = float(root.get("width", "0")), float(root.get("height", "0"))
        if sw <= 0 or sh <= 0:
            return False
        avail_w, avail_h = 595.0 - 72.0, 842.0 - 36 - 38 - 62
        scale = min(1.0, avail_w / sw)
        if sh * scale > avail_h:
            fit = avail_h / sh
            if fit >= self.WIREFRAME_MIN_SCALE:
                scale = fit                       # whole wireframe on one page
        cuts = _safe_cuts(root, sh, avail_h / scale)
        if cuts is None:
            return False
        for index in range(len(cuts) - 1):
            page = self.new_page()
            part = f" — parte {index + 1} de {len(cuts) - 1}" if len(cuts) > 2 else ""
            self._text_at(36, 842 - 36 - 12, norm(fig.title)[:100] + part, "F2", 11)
            self._text_at(36, 842 - 36 - 26, norm("Reconstrucción documental — no es una captura de producción"), "F1", 8.5, MUTED)
            top_pdf = 842 - 36 - 38
            ox = 36 + (avail_w - sw * scale) / 2
            y0, y1 = cuts[index], cuts[index + 1]
            clip_h = (y1 - y0) * scale
            page.ops.append(f"q {_num(36)} {_num(top_pdf - clip_h)} {_num(avail_w)} {_num(clip_h)} re W n")
            _SvgDrawer(page.ops, ox, top_pdf, scale, y0, y1).walk(root)
            page.ops.append("Q")
            self._text_at(36, 36 + 11, norm(f"Fuente: {fig.svg} (SVG completo en la guía HTML)")[:120], "F1", 7.5, MUTED)
            self.stats["figure_pages"] += 1
        return True

    # -- front matter (cover + contents are reserved first, filled after the body is laid out)
    def reserve_front(self) -> None:
        self.new_page()
        self.new_page()
        self._cur = None

    def fill_front(self, subtitle: str, meta_lines: list[str]) -> None:
        self._cur, self._y = self.pages[0], self.PH - 150
        self._text_at(self.M, self._y, "LegacyMapper", "F2", 12, MUTED)
        self._y -= 34
        tsize = float(self.style.get("title_size", 24))
        centred = self.style.get("title_align") == "center"
        title_color = tuple(self.style.get("title_color", INK))
        for line in self._wrap(self._tokens([Run(self.title, bold=True)], tsize, True), self.content_width):
            x = self.M + ((self.content_width - sum(t[3] for t in line)) / 2 if centred else 0)
            self._draw_line(x, self._y, line, title_color)
            self._y -= tsize * 1.25
        self._y -= 8
        for line in self._wrap(self._tokens([Run(subtitle)], 12), self.content_width):
            x = self.M + ((self.content_width - sum(t[3] for t in line)) / 2 if centred else 0)
            self._draw_line(x, self._y, line, MUTED)
            self._y -= 16
        self._y -= 16
        for meta in meta_lines:
            self.paragraph([Run(meta)], size=9, color=MUTED, space_after=2)
        self._y -= 18
        self._text_at(self.M, self._y, "Cómo leer las etiquetas de estado", "F2", 11)
        self._y -= 8
        meanings = [("Confirmado", "Lo demuestra el código analizado."),
                    ("Inferido (regla estructural)", "Deducido con una regla estructural; no es una afirmación de negocio."),
                    ("No resuelto", "El análisis no pudo determinarlo. No significa ausencia."),
                    ("Interpretación de IA (no aprobada)", "Propuesta de IA que ninguna persona ha aprobado. No es un hecho."),
                    ("Canónico (aprobado por una persona)", "Aprobado explícitamente por una persona.")]
        for label, meaning in meanings:
            if self.legend_labels is not None and label not in self.legend_labels:
                continue
            color, dash, lw, _prefix = STATUS[label]
            self._y -= 22
            self._rect(self.M, self._y - 4, 190, 17, stroke=color, width=lw, dash=dash)
            if label.startswith("Interpretación"):
                self._rect(self.M + 2, self._y - 2, 186, 13, stroke=color, width=0.6)
            self._text_at(self.M + 5, self._y, label, "F2", 8, color)
            self._text_at(self.M + 200, self._y, meaning, "F1", 8.5)
        self._y -= 30
        self.paragraph([Run("Este PDF es un artefacto secundario: el paquete HTML es la experiencia navegable completa (enlaces, diagramas "
                            "interactivos y listas íntegras). Las tablas largas se acortan aquí y se declara cuántas filas se muestran.", italic=True)],
                       size=9, color=MUTED)
        self._cur, self._y = self.pages[1], self.PH - self.M
        self._text_at(self.M, self._y - 14, "Contenido", "F2", 16)
        self._y -= 40
        low = min((lv for _t, _p, lv in self.toc), default=1)
        for title, page, lv in self.toc[:48]:
            indent = 14.0 * (lv - low)
            font, size = ("F2", 10.0) if lv == low else ("F1", 9.5)
            self._text_at(self.M + indent, self._y, title[: 90 - int(indent / 4)], font, size)
            label = str(page + 1)
            self._text_at(self.PW - self.M - text_width(label, "F1", 9.5), self._y, label, "F1", 9.5)
            self._y -= 14.5
        self._cur = None

    # -- serialization
    def render(self) -> tuple[bytes, dict]:
        pages = self.pages
        total = len(pages)
        for index, page in enumerate(pages):
            if page.footer:
                label = norm(f"LegacyMapper · {self.footer_title}")[:110]
                page.ops.append(
                    f"BT {_rgb(MUTED)} rg /F1 7.5 Tf {_num(self.M)} 24 Td {_pdf_str(label)} Tj ET "
                    f"BT {_rgb(MUTED)} rg /F1 7.5 Tf {_num(page.width - self.M - 70)} 24 Td {_pdf_str(f'Página {index + 1} de {total}')} Tj ET")
        objects: dict[int, bytes] = {}
        # object ids: 1 catalog, 2 pages, 3..7 fonts, 8 outlines root, then per page (page, content), then outline items
        font_ids = {k: 3 + i for i, k in enumerate(sorted(FONT_NAMES))}
        first_page = 9
        page_ids = [first_page + 2 * i for i in range(total)]
        content_ids = [pid + 1 for pid in page_ids]
        next_id = first_page + 2 * total
        outline_ids = list(range(next_id, next_id + len(self.outlines)))
        raw_hash = hashlib.sha256()
        for i, page in enumerate(pages):
            stream = "\n".join(page.ops).encode("latin-1", "replace")
            raw_hash.update(stream)
            packed = zlib.compress(stream, 9)
            objects[content_ids[i]] = (f"<< /Length {len(packed)} /Filter /FlateDecode >>\nstream\n".encode() + packed + b"\nendstream")
            objects[page_ids[i]] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_num(page.width)} {_num(page.height)}] "
                                    f"/Resources << /Font << " + " ".join(f"/{k} {font_ids[k]} 0 R" for k in sorted(font_ids)) +
                                    f" >> >> /Contents {content_ids[i]} 0 R >>").encode()
        for key, fid in font_ids.items():
            objects[fid] = f"<< /Type /Font /Subtype /Type1 /BaseFont /{FONT_NAMES[key]} /Encoding /WinAnsiEncoding >>".encode()
        objects[2] = ("<< /Type /Pages /Count %d /Kids [%s] >>" % (total, " ".join(f"{p} 0 R" for p in page_ids))).encode()
        # outlines: flat list with levels 0/1 -> tree
        parents: list[int | None] = []
        last_top = None
        for o in self.outlines:
            if o.level == 0 or last_top is None:
                parents.append(None)
                last_top = len(parents) - 1
            else:
                parents.append(last_top)
        children: dict[int | None, list[int]] = {}
        for idx, parent in enumerate(parents):
            children.setdefault(parent, []).append(idx)
        for idx, o in enumerate(self.outlines):
            oid = outline_ids[idx]
            parent = parents[idx]
            siblings = children[parent]
            pos = siblings.index(idx)
            parts = [f"/Title {_pdf_str(o.title)}", f"/Parent {(outline_ids[parent] if parent is not None else 8)} 0 R",
                     f"/Dest [{page_ids[min(o.page, total - 1)]} 0 R /XYZ 0 {_num(o.y)} 0]"]
            if pos > 0:
                parts.append(f"/Prev {outline_ids[siblings[pos - 1]]} 0 R")
            if pos < len(siblings) - 1:
                parts.append(f"/Next {outline_ids[siblings[pos + 1]]} 0 R")
            kids = children.get(idx, [])
            if kids:
                parts += [f"/First {outline_ids[kids[0]]} 0 R", f"/Last {outline_ids[kids[-1]]} 0 R", f"/Count {len(kids)}"]
            objects[oid] = ("<< " + " ".join(parts) + " >>").encode("latin-1")
        tops = children.get(None, [])
        if tops:
            objects[8] = (f"<< /Type /Outlines /First {outline_ids[tops[0]]} 0 R /Last {outline_ids[tops[-1]]} 0 R /Count {len(tops)} >>").encode()
            catalog = "<< /Type /Catalog /Pages 2 0 R /Outlines 8 0 R /PageMode /UseOutlines /Lang (es) >>"
        else:
            objects[8] = b"<< /Type /Outlines /Count 0 >>"
            catalog = "<< /Type /Catalog /Pages 2 0 R /Lang (es) >>"
        objects[1] = catalog.encode()
        info_id = max(objects) + 1
        objects[info_id] = f"<< /Title {_pdf_str(self.title)} /Producer (LegacyMapper deliver) /Creator (LegacyMapper) >>".encode("latin-1")
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: dict[int, int] = {}
        for oid in sorted(objects):
            offsets[oid] = len(out)
            out += f"{oid} 0 obj\n".encode() + objects[oid] + b"\nendobj\n"
        xref = len(out)
        size = max(objects) + 1
        out += f"xref\n0 {size}\n".encode() + b"0000000000 65535 f \n"
        for oid in range(1, size):
            out += f"{offsets[oid]:010d} 00000 n \n".encode()
        doc_id = hashlib.md5(raw_hash.copy().digest()).hexdigest()
        out += (f"trailer\n<< /Size {size} /Root 1 0 R /Info {info_id} 0 R /ID [<{doc_id}> <{doc_id}>] >>\nstartxref\n{xref}\n%%EOF\n").encode()
        return bytes(out), {"pages": total, "content_sha256": raw_hash.hexdigest(), **self.stats, "outline_entries": len(self.outlines)}


# ---------------------------------------------------------------- SVG slicing + drawing
def _node_intervals(root: ET.Element) -> list[tuple[float, float]]:
    out = []
    for g in root.iter("{http://www.w3.org/2000/svg}g"):
        if g.get("data-node") is not None:
            for r in g.findall("{http://www.w3.org/2000/svg}rect"):
                y, h = float(r.get("y", "0")), float(r.get("height", "0"))
                out.append((y - 5, y + h + 5))
    return out


def _slice_positions(root: ET.Element, height: float, slice_h: float) -> list[float]:
    if height <= slice_h:
        return [0.0, height]
    intervals = _node_intervals(root)
    cuts = [0.0]
    while height - cuts[-1] > slice_h:
        y0 = cuts[-1]
        target = y0 + slice_h
        best = None
        for _lo, hi in sorted(intervals, key=lambda t: t[1], reverse=True):
            if hi <= target and hi >= y0 + 0.45 * slice_h and not any(lo < hi < h2 for lo, h2 in intervals):
                best = hi
                break
        cuts.append(best if best is not None else target)
    cuts.append(height)
    return cuts


def _blocked_intervals(root: ET.Element, height: float, page_h: float) -> list[tuple[float, float]]:
    """Vertical extents of every drawn element a cut must not cross: controls, labels, icons and small groups. Large containers
    (taller than half a page) and the page background are not protected, so a cut may fall between their children."""
    ns = "{http://www.w3.org/2000/svg}"
    out = []
    for el in root.iter():
        tag = el.tag.replace(ns, "")
        if tag == "rect":
            y, h = float(el.get("y", "0")), float(el.get("height", "0"))
            if h >= height * 0.98 or h > page_h * 0.5:
                continue
            out.append((y, y + h))
        elif tag == "text":
            y = float(el.get("y", "0"))
            size = float(el.get("font-size", "11"))
            out.append((y - size, y + size * 0.3))
        elif tag in ("image", "line", "path", "circle", "ellipse", "polygon", "polyline"):
            ys = [float(el.get(k, "0")) for k in ("y", "y1", "y2", "cy") if el.get(k) is not None]
            if ys:
                out.append((min(ys) - float(el.get("height", "0")) * 0, max(ys) + float(el.get("height", "0"))))
    return out


def _safe_cuts(root: ET.Element, height: float, page_h: float) -> list[float] | None:
    """Cut positions between controls/groups. The parts are balanced (no short orphan part at the end) and none exceeds `page_h`."""
    if height <= page_h:
        return [0.0, height]
    blocked = _blocked_intervals(root, height, page_h)

    def allowed(y: float) -> bool:
        return not any(lo + 0.5 < y < hi - 0.5 for lo, hi in blocked)
    parts = -(-int(height * 100) // int(page_h * 100))
    cuts = [0.0]
    for k in range(1, parts):
        y0 = cuts[-1]
        target = min(height * k / parts, y0 + page_h)
        lowest = max(y0 + 0.3 * page_h, height - (parts - k) * page_h)
        highest = min(y0 + page_h, height - 0.2 * page_h)
        best = None
        for step in range(0, int(page_h)):
            for y in (target - step, target + step):
                if lowest <= y <= highest and allowed(y):
                    best = y
                    break
            if best is not None:
                break
        if best is None:
            return None                           # no logical boundary: caller falls back to the generic slicer
        cuts.append(best)
    cuts.append(height)
    if any(b - a > page_h + 0.5 for a, b in zip(cuts, cuts[1:])):
        return None
    return cuts


def _view_group(root: ET.Element) -> dict | None:
    """The origin node of a box-flow diagram (`data-role="view"`), when the diagram declares one."""
    for g in root.iter("{http://www.w3.org/2000/svg}g"):
        if g.get("data-role") == "view":
            rect = g.find("{http://www.w3.org/2000/svg}rect")
            if rect is not None:
                y, h = float(rect.get("y", "0")), float(rect.get("height", "0"))
                return {"mid": y + h / 2, "h": h}
    return None


class _SvgDrawer:
    NS = "{http://www.w3.org/2000/svg}"

    def __init__(self, ops: list[str], ox: float, top: float, scale: float, y0: float, y1: float) -> None:
        self.ops, self.ox, self.top, self.s, self.y0, self.y1 = ops, ox, top, scale, y0, y1
        self.pin_dy: float | None = None

    def pin_view(self, view: dict) -> None:
        """Draws the origin node at the vertical centre of this slice (and re-anchors its connectors there)."""
        half = view["h"] / 2 + 6
        target = min(max((self.y0 + self.y1) / 2, self.y0 + half), self.y1 - half)
        self.pin_dy = target - view["mid"]

    def X(self, x: float) -> float:
        return self.ox + self.s * x

    def Y(self, y: float) -> float:
        return self.top - self.s * (y - self.y0)

    def _visible(self, ya: float, yb: float) -> bool:
        return not (yb < self.y0 - 2 or ya > self.y1 + 2)

    def walk(self, el: ET.Element) -> None:
        tag = el.tag.replace(self.NS, "")
        if tag in ("title", "desc", "defs", "marker"):
            return
        if tag == "g" and el.get("data-role") == "view" and self.pin_dy is not None:
            self.y0 -= self.pin_dy
            self.y1 -= self.pin_dy
            for child in el:
                self.walk(child)
            self.y0 += self.pin_dy
            self.y1 += self.pin_dy
            return
        if tag == "rect":
            self._rect(el)
        elif tag == "text":
            self._text(el)
        elif tag == "path":
            self._path(el)
        for child in el:
            self.walk(child)

    def _style(self, el: ET.Element):
        dash = el.get("stroke-dasharray", "none")
        dash_ops = "" if dash in ("none", "") else " ".join(_num(float(p) * self.s) for p in dash.split())
        return dash_ops

    def _rect(self, el: ET.Element) -> None:
        x, y, w, h = (float(el.get(k, "0")) for k in ("x", "y", "width", "height"))
        if el.get("fill") == "#ffffff" and el.get("stroke") is None and x == 0 and y == 0:
            return  # page background
        if not self._visible(y, y + h):
            return
        fill = el.get("fill", "none")
        stroke = el.get("stroke")
        ops = ["q"]
        if fill != "none":
            ops.append(f"{_rgb(_hex(fill))} rg")
        if stroke and stroke != "none":
            ops.append(f"{_rgb(_hex(stroke))} RG {_num(max(0.4, float(el.get('stroke-width', '1')) * self.s))} w [{self._style(el)}] 0 d")
        r = min(float(el.get("rx", "0")) * self.s, w * self.s / 2)
        px, py, pw, ph = self.X(x), self.Y(y + h), w * self.s, h * self.s
        if r > 0.3:
            k = 0.5523 * r
            path = (f"{_num(px + r)} {_num(py)} m {_num(px + pw - r)} {_num(py)} l "
                    f"{_num(px + pw - r + k)} {_num(py)} {_num(px + pw)} {_num(py + r - k)} {_num(px + pw)} {_num(py + r)} c "
                    f"{_num(px + pw)} {_num(py + ph - r)} l "
                    f"{_num(px + pw)} {_num(py + ph - r + k)} {_num(px + pw - r + k)} {_num(py + ph)} {_num(px + pw - r)} {_num(py + ph)} c "
                    f"{_num(px + r)} {_num(py + ph)} l "
                    f"{_num(px + r - k)} {_num(py + ph)} {_num(px)} {_num(py + ph - r + k)} {_num(px)} {_num(py + ph - r)} c "
                    f"{_num(px)} {_num(py + r)} l "
                    f"{_num(px)} {_num(py + r - k)} {_num(px + r - k)} {_num(py)} {_num(px + r)} {_num(py)} c h")
        else:
            path = f"{_num(px)} {_num(py)} {_num(pw)} {_num(ph)} re"
        has_fill, has_stroke = fill != "none", bool(stroke and stroke != "none")
        paint = "B" if has_fill and has_stroke else ("f" if has_fill else ("S" if has_stroke else "n"))
        ops.append(f"{path} {paint} Q")
        self.ops.append(" ".join(ops))

    def _text(self, el: ET.Element) -> None:
        content = (el.text or "").strip()
        if not content:
            return
        y = float(el.get("y", "0"))
        if not self._visible(y - 14, y + 4):
            return
        size = float(el.get("font-size", "12"))
        font = "F2" if el.get("font-weight") == "bold" else "F1"
        text = norm(content)
        x = float(el.get("x", "0"))
        width = text_width(text, font, size)
        if el.get("text-anchor") == "middle":
            x -= width / 2
        elif el.get("text-anchor") == "end":
            x -= width
        color = _hex(el.get("fill", "#000000"), INK) if el.get("fill") else INK
        self.ops.append(f"BT {_rgb(color)} rg /{font} {_num(size * self.s)} Tf {_num(self.X(x))} {_num(self.Y(y))} Td {_pdf_str(text)} Tj ET")

    def _path(self, el: ET.Element) -> None:
        d = el.get("d", "")
        from_view = self.pin_dy is not None and el.get("data-from") == "view"
        if from_view:
            d = re.sub(r"^M(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)", lambda m: f"M{m.group(1)} {float(m.group(2)) + self.pin_dy}", d)
        tokens = re.findall(r"[MLC]|-?\d+(?:\.\d+)?", d)
        pts: list[tuple[float, float]] = []
        cmds: list[str] = []
        i = 0
        last = None
        while i < len(tokens):
            t = tokens[i]
            if t in "MLC":
                i += 1
                n = 3 if t == "C" else 1
                coords = [(float(tokens[i + 2 * k]), float(tokens[i + 2 * k + 1])) for k in range(n)]
                i += 2 * n
                if t == "M":
                    cmds.append(f"{_num(self.X(coords[0][0]))} {_num(self.Y(coords[0][1]))} m")
                elif t == "L":
                    cmds.append(f"{_num(self.X(coords[0][0]))} {_num(self.Y(coords[0][1]))} l")
                else:
                    cmds.append(" ".join(f"{_num(self.X(x))} {_num(self.Y(y))}" for x, y in coords) + " c")
                pts.extend(coords)
                prev = last
                last = (t, coords, prev)
            else:
                i += 1
        if not cmds or not pts:
            return
        ys = [p[1] for p in pts]
        if not self._visible(min(ys), max(ys)):
            return
        if from_view and not self.y0 <= pts[-1][1] <= self.y1:
            return  # the target row belongs to another part
        stroke = _hex(el.get("stroke", "#000000"))
        lw = max(0.4, float(el.get("stroke-width", "1")) * self.s)
        self.ops.append(f"q {_rgb(stroke)} RG {_num(lw)} w [{self._style(el)}] 0 d {' '.join(cmds)} S Q")
        if el.get("marker-end"):
            ex, ey = pts[-1]
            if last and last[0] == "C":
                fx, fy = last[1][1]  # second control point: tangent at the end
            else:
                fx, fy = pts[-2] if len(pts) > 1 else (ex - 1, ey)
            tx, ty = self.X(ex), self.Y(ey)
            dx, dy = tx - self.X(fx), ty - self.Y(fy)
            norm_ = (dx * dx + dy * dy) ** 0.5 or 1.0
            ux, uy = dx / norm_, dy / norm_
            length = 8 * max(1.0, float(el.get("stroke-width", "1"))) * self.s * 0.9  # marker: 8 x stroke-width user units
            half = length * 0.45
            bx, by = tx - ux * length, ty - uy * length
            nx, ny = -uy, ux
            self.ops.append(f"q {_rgb(stroke)} rg {_num(tx)} {_num(ty)} m {_num(bx + nx * half)} {_num(by + ny * half)} l "
                            f"{_num(bx - nx * half)} {_num(by - ny * half)} l h f Q")
