"""Markdown Renderer (R1 section 11, D-52-04).

Turns `StructuredDocument`s into Markdown files. It owns: Markdown syntax,
escaping, relative links, file names, combined items/bytes partitioning
(D-52-01) and deterministic output. It decides nothing about content,
audience, importance, noise or interpretation.
"""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field

from .structure import (
    Bullets, Code, Heading, Link, LinkRef, Note, Paragraph, PartitionedTable, StructuredDocument, Table, Text,
)

# `_` only matters at a word boundary in GFM; intraword underscores stay readable.
_MD_SPECIAL = re.compile(r"([\\`*\[\]<>|]|(?<![A-Za-z0-9])_|_(?![A-Za-z0-9]))")
# Fixed per-part cost estimate (title, navigation header/footer, table header), in bytes.
PART_OVERHEAD_BYTES = 700
# A partitioned table is inlined in its parent document only when it is small
# relative to the size limit, so several inlined tables cannot push the parent past it.
INLINE_FRACTION = 8


@dataclass(frozen=True)
class PartitionPolicy:
    max_items_per_part: int
    max_bytes_per_part: int


@dataclass
class RenderResult:
    files: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    parts: int = 0


def escape_text(value: object) -> str:
    return _MD_SPECIAL.sub(r"\\\1", " ".join(str(value).split()))


def code_span(value: object) -> str:
    text = " ".join(str(value).split()).replace("|", "\\|")
    if "`" in text:
        return "`` " + text + " ``"
    return f"`{text}`"


def format_text(text: Text) -> str:
    """Formats a catalog string. Backtick segments in the format are code spans:
    parameter values there are inserted raw (no escaping possible inside code);
    elsewhere they are escaped as plain text."""
    params = dict(text.params)
    segments = text.fmt.split("`")
    out = []
    for index, segment in enumerate(segments):
        inside_code = index % 2 == 1
        rendered = _Formatter(params, inside_code).format(segment)
        out.append(rendered)
    return "`".join(out)


class _Formatter:
    def __init__(self, params: dict, raw: bool) -> None:
        self._params = params
        self._raw = raw

    def format(self, segment: str) -> str:
        def replace(match: re.Match) -> str:
            name = match.group(1)
            if name not in self._params:
                return match.group(0)
            value = str(self._params[name])
            return " ".join(value.replace("`", "'").split()) if self._raw else escape_text(value)

        return re.sub(r"\{([A-Za-z0-9_]+)\}", replace, segment)


def partition_ranges(row_sizes: list[int], policy: PartitionPolicy, overhead: int = PART_OVERHEAD_BYTES) -> list[tuple[int, int]]:
    """Deterministic (start, end) ranges; a part closes when items or bytes would
    exceed the policy. A row is never split; an oversize row gets a part of its own."""
    ranges: list[tuple[int, int]] = []
    start = 0
    used = overhead
    for index, size in enumerate(row_sizes):
        count = index - start
        if count > 0 and (count >= policy.max_items_per_part or used + size > policy.max_bytes_per_part):
            ranges.append((start, index))
            start, used = index, overhead
        used += size
    if start < len(row_sizes):
        ranges.append((start, len(row_sizes)))
    return ranges


class MarkdownRenderer:
    def __init__(self, policy: PartitionPolicy, labels: dict[str, str]) -> None:
        """`labels` carries the fixed navigation words (from the language catalog):
        keys `nav.index`, `nav.previous`, `nav.next`, `nav.part`, `nav.rows`, `nav.parts_list`,
        `nav.oversize_warning`."""
        self._policy = policy
        self._labels = labels

    def render(self, documents: list[StructuredDocument]) -> RenderResult:
        result = RenderResult()
        for document in sorted(documents, key=lambda d: d.path):
            self._render_document(document, result)
        return result

    # ------------------------------------------------------------------ helpers
    def _label(self, key: str, **params) -> str:
        return self._labels.get(key, key).format_map(_Safe(params))

    @staticmethod
    def _link(text: str, from_path: str, to_path: str) -> str:
        rel = posixpath.relpath(to_path, posixpath.dirname(from_path) or ".")
        return f"[{text}]({rel})"

    def _cell(self, cell: object, from_path: str) -> str:
        if isinstance(cell, LinkRef):
            text = code_span(cell.text) if cell.code else escape_text(cell.text)
            return self._link(text, from_path, cell.target)
        if isinstance(cell, Code):
            return code_span(cell.text)
        return escape_text(cell)

    def _table_lines(self, headers: list[str], rows: list[list], from_path: str) -> list[str]:
        lines = ["| " + " | ".join(escape_text(h) for h in headers) + " |",
                 "| " + " | ".join("---" for _ in headers) + " |"]
        lines.extend("| " + " | ".join(self._cell(c, from_path) for c in row) + " |" for row in rows)
        return lines

    def _row_line(self, row: list, from_path: str) -> str:
        return "| " + " | ".join(self._cell(c, from_path) for c in row) + " |"

    # ------------------------------------------------------------------ documents
    def _render_document(self, document: StructuredDocument, result: RenderResult) -> None:
        lines: list[str] = []
        if document.title.fmt:
            lines += [f"# {format_text(document.title)}", ""]
        in_links = False
        for block in document.blocks:
            is_link = isinstance(block, Link)
            if in_links and not is_link:
                lines.append("")
                in_links = False
            if isinstance(block, Heading):
                lines += ["", f"{'#' * block.level} {format_text(block.text)}", ""]
            elif isinstance(block, Paragraph):
                lines += [format_text(block.text), ""]
            elif isinstance(block, Note):
                lines += [f"> {format_text(block.text)}", ""]
            elif isinstance(block, Bullets):
                lines += [f"- {format_text(item)}" for item in block.items] + [""]
            elif is_link:
                if not in_links and lines and lines[-1] != "":
                    lines.append("")
                in_links = True
                lines.append(f"- {self._link(format_text(block.text), document.path, block.target)}")
            elif isinstance(block, Table):
                lines += self._table_lines(block.headers, block.rows, document.path) + [""]
            elif isinstance(block, PartitionedTable):
                lines += self._partitioned(document, block, result)
        content = self._finish(lines)
        result.files[document.path] = content
        size = len(content.encode("utf-8"))
        if size > self._policy.max_bytes_per_part:
            result.warnings.append(
                f"{document.path}: documento de {size} bytes supera el límite de {self._policy.max_bytes_per_part} (no se trunca)."
            )

    @staticmethod
    def _finish(lines: list[str]) -> str:
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text).strip("\n")
        return text + "\n"

    def _partitioned(self, document: StructuredDocument, block: PartitionedTable, result: RenderResult) -> list[str]:
        row_lines = [self._row_line(row, document.path) for row in block.rows]
        sizes = [len(line.encode("utf-8")) + 1 for line in row_lines]
        ranges = partition_ranges(sizes, self._policy)
        inline_limit = self._policy.max_bytes_per_part // INLINE_FRACTION
        if len(ranges) <= 1 and not block.separate and sum(sizes) <= inline_limit:
            return self._table_lines(block.headers, block.rows, document.path) + [""]
        doc_dir = posixpath.dirname(document.path)
        stem = block.stem or f"{posixpath.splitext(posixpath.basename(document.path))[0]}-{block.name}"
        names = [posixpath.join(doc_dir, f"{stem}-part-{number:06d}.md") for number in range(1, len(ranges) + 1)]
        total = len(block.rows)
        header = self._table_lines(block.headers, [], document.path)[:2]
        for index, (start, end) in enumerate(ranges):
            number = index + 1
            path = names[index]
            nav = [self._link(self._label("nav.index"), path, document.path)]
            if index > 0:
                nav.append(self._link(self._label("nav.previous"), path, names[index - 1]))
            if index + 1 < len(ranges):
                nav.append(self._link(self._label("nav.next"), path, names[index + 1]))
            nav_line = " · ".join(nav)
            body = [f"# {escape_text(block.title)} — {self._label('nav.part', number=number, total=len(ranges))}", "", nav_line, "",
                    self._label("nav.rows", first=start + 1, last=end, total=total), ""]
            body += header + row_lines[start:end] + ["", nav_line]
            if end - start == 1 and sizes[start] + PART_OVERHEAD_BYTES > self._policy.max_bytes_per_part:
                result.warnings.append(f"{path}: un único elemento ({sizes[start]} bytes) supera el límite de tamaño; se escribe solo y sin truncar.")
                body += ["", f"> {self._label('nav.oversize_warning')}"]
            content = self._finish(body)
            result.files[path] = content
            result.parts += 1
        listing = [self._label("nav.parts_list"), ""]
        for index, (start, end) in enumerate(ranges):
            text = self._label("nav.part", number=index + 1, total=len(ranges)) + " — " + self._label(
                "nav.rows", first=start + 1, last=end, total=total)
            listing.append(f"- {self._link(text, document.path, names[index])}")
        return listing + [""]


class _Safe(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"
