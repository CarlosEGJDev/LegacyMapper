"""Renderer-neutral structured document: the contract between Template and Renderer.

No Markdown syntax appears here. `Text` keeps a catalog format string and its
parameters separate so the renderer alone decides how parameter values are
escaped for the physical format.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Text:
    fmt: str
    params: tuple = ()  # tuple of (name, value) pairs, order-stable

    @staticmethod
    def of(fmt: str, params: dict | None = None) -> "Text":
        return Text(fmt, tuple(sorted((params or {}).items())))


@dataclass(frozen=True)
class Code:
    text: str


@dataclass(frozen=True)
class LinkRef:
    text: str
    target: str  # path of another document, relative to the documentation root
    code: bool = False


@dataclass
class Heading:
    level: int
    text: Text


@dataclass
class Paragraph:
    text: Text


@dataclass
class Note:
    text: Text


@dataclass
class Bullets:
    items: list  # of Text


@dataclass
class Link:
    text: Text
    target: str


@dataclass
class Table:
    headers: list  # of str
    rows: list  # of list[str | Code | LinkRef]


@dataclass
class PartitionedTable:
    """A table the renderer may split into navigable parts. `stem` names the part
    files; `separate` forces separate part files even when everything fits in one."""

    name: str
    stem: str
    title: str
    headers: list
    rows: list
    separate: bool = False


@dataclass
class StructuredDocument:
    path: str  # relative to the documentation root, POSIX separators
    title: Text
    blocks: list = field(default_factory=list)
