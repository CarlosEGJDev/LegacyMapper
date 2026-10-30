"""Block model + a small, strict parser for the Markdown subset the H2 renderer emits (post-V5 H4).

The H2 renderer escapes every Markdown special (`\\ ` * [ ] < > |` and word-boundary `_`) and only emits headings,
paragraphs, `>` quotes, flat `-` lists, pipe tables, code spans, bold/italic and links. This parser reads exactly that and
produces plain blocks that both the HTML and the PDF renderer consume, so the two outputs can never diverge in content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_PUNCT = set("\\`*_{}[]()#+-.!|<>~\"'&:;,/=@$%^?")


@dataclass(frozen=True)
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    href: str | None = None      # site-relative target (after link resolution) or an unresolved/external raw target
    missing: bool = False        # a link whose target is not part of the package: rendered as plain text, never as a dead link


@dataclass
class Heading:
    level: int
    runs: list[Run]
    anchor: str = ""
    cls: str = ""          # presentation role ("view-title" | "section-title" | ""); styling lives in the template


@dataclass
class Para:
    runs: list[Run]
    cls: str = ""          # presentation role chosen by the document builder ("technical" | "evidence" | "caption" | ""); styling lives in the template


@dataclass
class Quote:
    blocks: list


@dataclass
class Bullets:
    items: list[list[Run]]


@dataclass
class Table:
    headers: list[list[Run]]
    rows: list[list[list[Run]]]
    caption: str = ""


@dataclass
class Code:
    text: str


@dataclass
class Rule:
    pass


@dataclass
class Figure:
    """A diagram reference (H3 SVG). `svg`/`model`/`page` are package-relative paths."""
    title: str
    svg: str
    model: str
    page: str
    kind: str
    scope_label: str
    nodes: int
    edges: int
    width: int
    height: int
    status_counts: dict
    partial: dict
    unresolved_nodes: int
    role: str = ""
    children: list = field(default_factory=list)   # [(title, page)] detail diagrams


@dataclass
class Callout:
    kind: str                  # note | unresolved | semantic | status
    title: str
    blocks: list


@dataclass
class Details:
    summary: str
    blocks: list
    open: bool = False


def plain(runs: list[Run]) -> str:
    return "".join(r.text for r in runs)


def slugify(text: str) -> str:
    import unicodedata
    base = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:60] or "seccion"


# ---------------------------------------------------------------- inline
def _skip_code(s: str, i: int) -> int:
    """`i` is at a backtick; returns the index after the closing run (or i+1 when unterminated)."""
    n = 0
    while i + n < len(s) and s[i + n] == "`":
        n += 1
    close = s.find("`" * n, i + n)
    while close != -1 and close + n < len(s) and s[close + n] == "`":  # run longer than ours is not a closer
        j = close
        while j < len(s) and s[j] == "`":
            j += 1
        close = s.find("`" * n, j)
    return close + n if close != -1 else i + n


def _find_close(s: str, start: int, token: str) -> int:
    i = start
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "`":
            i = _skip_code(s, i)
            continue
        if s.startswith(token, i):
            if token == "*" and s.startswith("**", i):
                i += 2
                continue
            return i
        i += 1
    return -1


def _match_bracket(s: str, start: int) -> int:
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "`":
            i = _skip_code(s, i)
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def parse_inline(s: str, *, bold: bool = False, italic: bool = False, href: str | None = None) -> list[Run]:
    out: list[Run] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            out.append(Run("".join(buf), bold, italic, False, href))
            buf.clear()

    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] in _PUNCT:
            buf.append(s[i + 1])
            i += 2
        elif c == "`":
            end = _skip_code(s, i)
            n = 0
            while i + n < len(s) and s[i + n] == "`":
                n += 1
            if end - i >= 2 * n and s[end - n:end] == "`" * n:
                flush()
                inner = s[i + n:end - n]
                if len(inner) > 1 and inner.startswith(" ") and inner.endswith(" "):
                    inner = inner[1:-1]
                if inner.strip():
                    out.append(Run(inner.replace("\\|", "|"), bold, italic, True, href))
                else:  # the evidence carries an empty name: say so instead of drawing an empty code box
                    out.append(Run("(nombre vacío en la evidencia)", bold, True, False, href))
                i = end
            elif n == 2 and not s.startswith("`", i + 2):  # the H2 renderer writes an empty evidence name as a bare pair of backticks
                flush()
                out.append(Run("(nombre vacío en la evidencia)", bold, True, False, href))
                i += 2
            else:
                buf.append(s[i:i + n])
                i += n
        elif c == "[" and href is None:
            close = _match_bracket(s, i)
            if close != -1 and s.startswith("(", close + 1):
                end = s.find(")", close + 2)
                if end != -1:
                    flush()
                    target = s[close + 2:end].strip()
                    out.extend(parse_inline(s[i + 1:close], bold=bold, italic=italic, href=target or None))
                    i = end + 1
                    continue
            buf.append(c)
            i += 1
        elif s.startswith("**", i):
            close = _find_close(s, i + 2, "**")
            if close != -1:
                flush()
                out.extend(parse_inline(s[i + 2:close], bold=True, italic=italic, href=href))
                i = close + 2
            else:
                buf.append("**")
                i += 2
        elif c == "*":
            close = _find_close(s, i + 1, "*")
            if close != -1 and close > i + 1:
                flush()
                out.extend(parse_inline(s[i + 1:close], bold=bold, italic=True, href=href))
                i = close + 1
            else:
                buf.append(c)
                i += 1
        else:
            buf.append(c)
            i += 1
    flush()
    return out


# ---------------------------------------------------------------- blocks
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_BULLET = re.compile(r"^[-*]\s+(.*)$")
_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    cells: list[str] = []
    buf: list[str] = []
    i = 0
    in_code = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            buf.append(line[i:i + 2])
            i += 2
            continue
        if c == "`":
            n = 0
            while i + n < len(line) and line[i + n] == "`":
                n += 1
            in_code = 0 if in_code == n else (n if not in_code else in_code)
            buf.append(line[i:i + n])
            i += n
            continue
        if c == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail or not line.endswith("|"):
        cells.append(tail)
    return cells


def parse_markdown(text: str) -> list:
    lines = text.replace("\r\n", "\n").split("\n")
    blocks: list = []
    para: list[str] = []
    seen: dict[str, int] = {}

    def flush_para() -> None:
        if para:
            blocks.append(Para(parse_inline(" ".join(p.strip() for p in para))))
            para.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para()
            i += 1
            continue
        if stripped.startswith("```"):
            flush_para()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(Code("\n".join(code)))
            continue
        m = _HEADING.match(stripped)
        if m:
            flush_para()
            runs = parse_inline(m.group(2))
            base = slugify(plain(runs))
            seen[base] = seen.get(base, 0) + 1
            anchor = base if seen[base] == 1 else f"{base}-{seen[base]}"
            blocks.append(Heading(len(m.group(1)), runs, anchor))
            i += 1
            continue
        if stripped.startswith(">"):
            flush_para()
            inner: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                inner.append(lines[i].strip()[1:].lstrip(" ") if lines[i].strip()[1:2] == " " else lines[i].strip()[1:])
                i += 1
            blocks.append(Quote(parse_markdown("\n".join(inner))))
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and _SEP.match(lines[i + 1].strip()):
            flush_para()
            headers = [parse_inline(c) for c in split_row(stripped)]
            i += 2
            rows: list[list[list[Run]]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [parse_inline(c) for c in split_row(lines[i])]
                cells = (cells + [[] for _ in headers])[:len(headers)]
                rows.append(cells)
                i += 1
            blocks.append(Table(headers, rows))
            continue
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush_para()
            blocks.append(Rule())
            i += 1
            continue
        b = _BULLET.match(stripped)
        if b:
            flush_para()
            items: list[list[str]] = []
            while i < len(lines):
                bm = _BULLET.match(lines[i].strip())
                if bm and not lines[i].startswith(" "):
                    items.append([bm.group(1)])
                    i += 1
                elif lines[i].strip() and lines[i].startswith(" ") and items:
                    items[-1].append(lines[i].strip())
                    i += 1
                else:
                    break
            blocks.append(Bullets([parse_inline(" ".join(it)) for it in items]))
            continue
        para.append(line)
        i += 1
    flush_para()
    return blocks


# ---------------------------------------------------------------- block utilities
def title_of(blocks: list, default: str = "") -> str:
    for b in blocks:
        if isinstance(b, Heading) and b.level == 1:
            return plain(b.runs)
    return default


def walk_runs(blocks: list):
    """Yields every Run in `blocks` (recursing into quotes, callouts and details)."""
    for b in blocks:
        if isinstance(b, (Heading, Para)):
            yield from b.runs
        elif isinstance(b, Bullets):
            for item in b.items:
                yield from item
        elif isinstance(b, Table):
            for cell in b.headers:
                yield from cell
            for row in b.rows:
                for cell in row:
                    yield from cell
        elif isinstance(b, (Quote, Callout, Details)):
            yield from walk_runs(b.blocks)


def map_runs(blocks: list, fn) -> list:
    """Returns a copy of `blocks` with `fn(run) -> run` applied to every Run (structure preserved)."""
    def cells(runs: list[Run]) -> list[Run]:
        return [fn(r) for r in runs]

    out: list = []
    for b in blocks:
        if isinstance(b, Heading):
            out.append(Heading(b.level, cells(b.runs), b.anchor))
        elif isinstance(b, Para):
            out.append(Para(cells(b.runs)))
        elif isinstance(b, Bullets):
            out.append(Bullets([cells(i) for i in b.items]))
        elif isinstance(b, Table):
            out.append(Table([cells(h) for h in b.headers], [[cells(c) for c in row] for row in b.rows], b.caption))
        elif isinstance(b, Quote):
            out.append(Quote(map_runs(b.blocks, fn)))
        elif isinstance(b, Callout):
            out.append(Callout(b.kind, b.title, map_runs(b.blocks, fn)))
        elif isinstance(b, Details):
            out.append(Details(b.summary, map_runs(b.blocks, fn), b.open))
        else:
            out.append(b)
    return out


def demote(blocks: list, by: int = 1) -> list:
    out = []
    for b in blocks:
        out.append(Heading(min(6, b.level + by), b.runs, b.anchor) if isinstance(b, Heading) else b)
    return out


def section(blocks: list, heading_prefix: str, level: int = 2) -> list:
    """Blocks under the first heading (of `level`) whose text starts with `heading_prefix`, up to the next heading of <= level."""
    out: list = []
    taking = False
    for b in blocks:
        if isinstance(b, Heading):
            if taking and b.level <= level:
                break
            if not taking and b.level == level and plain(b.runs).startswith(heading_prefix):
                taking = True
                continue
        if taking:
            out.append(b)
    return out
