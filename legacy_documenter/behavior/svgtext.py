"""Deterministic text measurement and wrapping for generated SVG diagrams (post-V5 final template polish).

Every box of every generated diagram measures its text with the same Helvetica metrics the PDF writer uses and wraps it to the box
width, so text can never leave its box: a long label makes the box taller (or wraps at path separators), it is never clipped.
Pure function of (text, width, size): no layout engine, no randomness.
"""
from __future__ import annotations

import re

from legacy_documenter.deliver.pdf import norm, text_width

_BREAK_AFTER = re.compile(r"(?<=[\\/._\-:,;()])|(?<=[a-z0-9])(?=[A-Z])")   # separators, then camelCase word boundaries
LINE_FACTOR = 1.28


def _fits(text: str, width: float, size: float, bold: bool) -> bool:
    return text_width(text, "F2" if bold else "F1", size) <= width


def _hard_split(token: str, width: float, size: float, bold: bool) -> list[str]:
    """Splits an over-long unbroken token: first after path/identifier separators, then by characters."""
    pieces = [p for p in _BREAK_AFTER.split(token) if p]
    lines: list[str] = []
    cur = ""
    for piece in pieces:
        if _fits(cur + piece, width, size, bold):
            cur += piece
            continue
        if cur:
            lines.append(cur)
            cur = ""
        if _fits(piece, width, size, bold):
            cur = piece
            continue
        for ch in piece:                                   # still too long: break by characters
            if _fits(cur + ch, width, size, bold) or not cur:
                cur += ch
            else:
                lines.append(cur)
                cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def wrap(text: str, width: float, size: float = 11.0, bold: bool = False) -> list[str]:
    """Wraps `text` to `width` (SVG user units). Always returns at least one line; every line fits in `width`."""
    text = " ".join(norm(str(text)).split())
    if not text:
        return [""]
    lines: list[str] = []
    cur = ""
    for word in text.split(" "):
        candidate = word if not cur else cur + " " + word
        if _fits(candidate, width, size, bold):
            cur = candidate
            continue
        if cur:
            lines.append(cur)
            cur = ""
        if _fits(word, width, size, bold):
            cur = word
        else:
            parts = _hard_split(word, width, size, bold)
            lines.extend(parts[:-1])
            cur = parts[-1]
    if cur:
        lines.append(cur)
    return lines


def longest_unbreakable(text: str, size: float, bold: bool = False) -> float:
    """Width of the widest piece of `text` that `wrap` could only split by characters (separators / camelCase boundaries are free breaks)."""
    widest = 0.0
    for word in norm(str(text)).split():
        for piece in (p for p in _BREAK_AFTER.split(word) if p):
            widest = max(widest, text_width(piece, "F2" if bold else "F1", size))
    return widest


def line_height(size: float) -> float:
    return round(size * LINE_FACTOR, 1)


def block_height(lines: int, size: float) -> float:
    return lines * line_height(size)
