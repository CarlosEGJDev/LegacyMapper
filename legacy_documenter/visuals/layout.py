"""Deterministic layered (left-to-right) layout for `VisualProjection` (post-V5 H3).

No external layout engine: columns come from longest-path layering over the edge DAG (cycles are broken by ignoring the
back edges found by a DFS that visits nodes in `(label, id)` order), rows are ordered by group, then by the barycenter of
the neighbours in the previous column (two stable sweeps), then by `(label, id)`. All coordinates are integers, so the
same model always yields the same geometry.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .model import VisualProjection

NODE_W = 240
LINE_H = 15
PAD = 10
COL_GAP = 110
ROW_GAP = 18
GROUP_PAD = 14
GROUP_HEADER = 20
MARGIN = 28
TITLE_H = 58
WRAP = 26
MAX_LINES = 3
#: H3-R2: a layer-ordered diagram with more columns than this wraps into horizontal BANDS stacked vertically (reading order
#: stays left-to-right, top-to-bottom; an edge that crosses from the last column of a band to the first column of the next one
#: is routed orthogonally through the gap between bands). Diagrams with fewer columns are laid out exactly as before.
MAX_COLS = 4
BAND_GAP = 70


def wrap_label(text: str, width: int = WRAP, max_lines: int = MAX_LINES) -> tuple[list[str], bool]:
    """Greedy word wrap with hard breaks for over-long tokens (paths, identifiers). Returns (lines, truncated)."""
    tokens: list[str] = []
    for word in " ".join(str(text).split()).split(" "):
        while len(word) > width:
            tokens.append(word[:width])
            word = word[width:]
        tokens.append(word)
    lines: list[str] = []
    current = ""
    for token in tokens:
        if not current:
            current = token
        elif len(current) + 1 + len(token) <= width:
            current += " " + token
        else:
            lines.append(current)
            current = token
    if current:
        lines.append(current)
    lines = [ln for ln in lines if ln] or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: width - 1].rstrip() + "…"
        return lines, True
    return lines, False


@dataclass
class Placed:
    id: str
    x: int
    y: int
    w: int
    h: int
    lines: list[str]
    truncated: bool
    column: int
    band: int = 0


@dataclass
class Layout:
    width: int = 0
    height: int = 0
    nodes: dict[str, Placed] = field(default_factory=dict)
    group_boxes: list[tuple[str, int, int, int, int]] = field(default_factory=list)  # (group id, x, y, w, h)
    columns: int = 0
    bands: list[tuple[int, int]] = field(default_factory=list)  # (top y, bottom y) of each band; one entry when not wrapped


def _layers(projection: VisualProjection) -> dict[str, int]:
    nodes = {n.id: n for n in projection.nodes}
    order = sorted(nodes, key=lambda i: (nodes[i].label, i))
    out: dict[str, list[str]] = {i: [] for i in nodes}
    for e in sorted(projection.edges, key=lambda e: e.id):
        if e.source in nodes and e.target in nodes and e.source != e.target:
            out[e.source].append(e.target)
    for i in out:
        out[i].sort(key=lambda t: (nodes[t].label, t))
    state: dict[str, int] = {}
    back: set[tuple[str, str]] = set()

    def visit(start: str) -> None:
        stack = [(start, iter(out[start]))]
        state[start] = 1
        while stack:
            node, children = stack[-1]
            for child in children:
                if state.get(child, 0) == 0:
                    state[child] = 1
                    stack.append((child, iter(out[child])))
                    break
                if state.get(child) == 1:
                    back.add((node, child))
            else:
                state[node] = 2
                stack.pop()

    for i in order:
        if state.get(i, 0) == 0:
            visit(i)
    preds: dict[str, list[str]] = {i: [] for i in nodes}
    for s, targets in out.items():
        for t in targets:
            if (s, t) not in back:
                preds[t].append(s)
    column: dict[str, int] = {}

    def depth(i: str, seen: frozenset = frozenset()) -> int:
        if i in column:
            return column[i]
        hint = nodes[i].column
        value = hint if hint is not None else max((depth(p) + 1 for p in preds[i]), default=0)
        column[i] = value
        return value

    import sys
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(limit, 10000))
    try:
        for i in order:
            depth(i)
    finally:
        sys.setrecursionlimit(limit)
    return column


def layout(projection: VisualProjection, max_cols: int = MAX_COLS) -> Layout:
    result = Layout()
    if not projection.nodes:
        result.width, result.height = 2 * MARGIN + 3 * NODE_W // 2, TITLE_H + 2 * MARGIN
        return result
    nodes = {n.id: n for n in projection.nodes}
    column = _layers(projection)
    ncols = max(column.values()) + 1
    group_order = {g.id: i for i, g in enumerate(sorted(projection.groups, key=lambda g: (g.label, g.id)))}
    by_col: list[list[str]] = [[] for _ in range(ncols)]
    for i in nodes:
        by_col[column[i]].append(i)

    def base_key(i: str):
        return (group_order.get(nodes[i].group, -1) if nodes[i].group else -1, nodes[i].label, i)

    for col in by_col:
        col.sort(key=base_key)
    neighbours: dict[str, list[str]] = {i: [] for i in nodes}
    for e in projection.edges:
        if e.source in nodes and e.target in nodes:
            neighbours[e.source].append(e.target)
            neighbours[e.target].append(e.source)
    index = {i: pos for col in by_col for pos, i in enumerate(col)}
    for sweep in (range(1, ncols), range(ncols - 2, -1, -1)):
        for c in sweep:
            ref = c - 1 if sweep.step > 0 else c + 1

            def bary(i: str) -> float:
                near = [index[n] for n in neighbours[i] if column[n] == ref]
                return sum(near) / len(near) if near else float(index[i])
            by_col[c].sort(key=lambda i: (base_key(i)[0], bary(i), nodes[i].label, i))
            for pos, i in enumerate(by_col[c]):
                index[i] = pos

    heights: dict[str, tuple[list[str], bool, int]] = {}
    for i, n in nodes.items():
        lines, truncated = wrap_label(n.label)
        h = 2 * PAD + len(lines) * LINE_H + 2 * 13
        heights[i] = (lines, truncated, h)
    rel_y: dict[str, int] = {}
    col_heights: list[int] = []
    for ids in by_col:
        y = 0
        prev_group = object()
        for i in ids:
            g = nodes[i].group
            if g != prev_group and g:
                y += GROUP_HEADER + GROUP_PAD
            elif g != prev_group and prev_group:
                y += GROUP_PAD
            rel_y[i] = y
            y += heights[i][2] + ROW_GAP
            prev_group = g
        col_heights.append(y)
    cols_per_band = ncols if ncols <= max_cols else max_cols
    nbands = (ncols + cols_per_band - 1) // cols_per_band
    top = TITLE_H + MARGIN
    band_top: list[int] = []
    for b in range(nbands):
        band_top.append(top)
        band_h = max(col_heights[b * cols_per_band:(b + 1) * cols_per_band], default=0)
        result.bands.append((top, top + band_h))
        top += band_h + (BAND_GAP if b < nbands - 1 else 0)
    for i, n in nodes.items():
        lines, truncated, h = heights[i]
        c = column[i]
        band, col_in_band = divmod(c, cols_per_band)
        result.nodes[i] = Placed(i, MARGIN + GROUP_PAD + col_in_band * (NODE_W + COL_GAP), band_top[band] + rel_y[i], NODE_W, h, lines, truncated, c, band)
    boxes: dict[tuple[str, int], list[int]] = {}
    for i, n in nodes.items():
        if n.group:
            p = result.nodes[i]
            key = (n.group, p.column)
            box = boxes.setdefault(key, [p.x, p.y, p.x + p.w, p.y + p.h])
            box[1], box[3] = min(box[1], p.y), max(box[3], p.y + p.h)
    for (gid, _col), (x0, y0, x1, y1) in sorted(boxes.items(), key=lambda kv: (group_order.get(kv[0][0], 0), kv[0][1])):
        result.group_boxes.append((gid, x0 - GROUP_PAD // 2, y0 - GROUP_HEADER, (x1 - x0) + GROUP_PAD, (y1 - y0) + GROUP_HEADER + GROUP_PAD // 2))
    result.columns = ncols
    result.width = 2 * MARGIN + 2 * GROUP_PAD + cols_per_band * NODE_W + (cols_per_band - 1) * COL_GAP
    result.height = result.bands[-1][1] + MARGIN
    return result
