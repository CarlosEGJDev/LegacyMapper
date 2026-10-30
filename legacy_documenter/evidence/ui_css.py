"""Pure CSS fact parsing (post-V5 Gate B): whitelisted declarations and top-level `.class` rules.

Shared by the deterministic extractor (which persists the resolved declarations as UI style Evidence) and by the downstream
documentary reconstruction (which only resolves classes over the persisted declarations). No file access happens here.
"""
from __future__ import annotations

import re

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "blue": "#0000ff", "green": "#008000", "gray": "#808080", "grey": "#808080",
          "silver": "#c0c0c0", "navy": "#000080", "teal": "#008080", "maroon": "#800000", "purple": "#800080", "yellow": "#ffff00", "orange": "#ffa500",
          "transparent": "none"}


def _color(v: str) -> str | None:
    v = v.strip().lower()
    if v in _NAMED:
        return _NAMED[v]
    if _HEX.match(v):
        return v if len(v) == 7 else "#" + "".join(c * 2 for c in v[1:])
    m = re.fullmatch(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", v)
    if m and all(int(x) <= 255 for x in m.groups()):
        return "#%02x%02x%02x" % tuple(int(x) for x in m.groups())
    return None


def _px(v: str) -> int | None:
    m = re.fullmatch(r"\s*(\d{1,4})(?:px)?\s*", v)
    return int(m.group(1)) if m else None


def parse_declarations(body: str) -> dict:
    """Whitelisted visual properties only; everything else is ignored."""
    out: dict = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        k, _, v = part.partition(":")
        k, v = k.strip().lower(), v.strip().rstrip("!important").strip()
        if k in ("color", "background-color", "background", "border-color"):
            c = _color(v.split()[0]) if v else None
            if c:
                out["border" if k == "border-color" else ("color" if k == "color" else "background")] = c
        elif k == "font-size":
            px = _px(v)
            if px:
                out["font_size"] = px
        elif k == "font-weight":
            out["font_weight"] = "bold" if v.lower() in ("bold", "bolder", "600", "700", "800", "900") else "normal"
        elif k == "font":
            m = re.match(r"(?:(bold|bolder|normal)\s+)?(\d{1,2})px\b", v, re.I)
            if m:
                out["font_size"] = int(m.group(2))
                if m.group(1):
                    out["font_weight"] = "bold" if m.group(1).lower() != "normal" else "normal"
        elif k == "border":
            m = re.match(r"(\d)px\s+solid\s+(\S+)", v) or re.match(r"solid\s+(\d)px\s+(\S+)", v)
            if m:
                c = _color(m.group(2))
                if c and c != "none":
                    out["border"], out["border_width"] = c, int(m.group(1))
            elif v.lower() == "none":
                out["border_width"] = 0
        elif k == "border-width":
            px = _px(v)
            if px is not None:
                out["border_width"] = px
        elif k == "border-radius":
            px = _px(v.split()[0])
            if px is not None:
                out["radius"] = min(px, 12)
        elif k in ("width", "height"):
            px = _px(v)
            if px:
                out[k] = px
        elif k == "text-decoration":
            out["underline"] = "underline" in v.lower()
        elif k == "text-align" and v.lower() in ("left", "center", "right"):
            out["align"] = v.lower()
    return out


def parse_css(text: str) -> dict[str, dict]:
    """Top-level `.class` rules only (no @media, no pseudo-classes, no compound selectors)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    rules: dict[str, dict] = {}
    i, n = 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j == -1:
            break
        selector = text[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        body = text[j + 1:k - 1]
        i = k
        if selector.startswith("@") or "{" in body:
            continue
        for sel in selector.split(","):
            sel = sel.strip()
            if re.fullmatch(r"\.[A-Za-z0-9_\-]+", sel):
                rules.setdefault(sel[1:], {}).update(parse_declarations(body))
    return rules
