"""Human-prose polish applied only when the human document is composed (post-V5 H4 final screen/narrative micro-polish).

The shared knowledge model, `ai/` and `internal/` keep their exact wording and source locations. The human document explains the system
instead of narrating the Evidence engine, so at presentation time:

* source-location suffixes (`(línea 68)`, `(ventana emergente; línea 12)`) are dropped from prose;
* audit phrasing (`La evidencia muestra…`, `La evidencia no precisa…`) becomes direct documentary language, rule by rule and in context
  (never a blind word replacement).
Pure, deterministic, order-fixed rules.
"""
from __future__ import annotations

import re
from dataclasses import replace

from legacy_documenter.deliver.markdown import Bullets, Callout, Details, Heading, Para, Quote, Run, Table

_LINE_ONLY = re.compile(r"\s*\((?:línea|lineas?|linea) \d+(?:\s*[-–]\s*\d+)?\)")
_LINE_AFTER_NOTE = re.compile(r";\s*(?:línea|linea) \d+(?=\))")
_VIEW_FILE = re.compile(r"\b([A-Za-z_]\w*)\.(?:ascx|aspx)\b")      # a view is named, not located: `ucBusSuc.ascx` reads `ucBusSuc`

# (pattern, replacement) - applied in this order; capitalisation is handled by the explicit sentence-initial / mid-sentence pairs.
_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"No se especifica en la evidencia\b"), "No se especifica"),
    (re.compile(r"No se encontró en la evidencia\b"), "No se encontró"),
    (re.compile(r"\bLa evidencia también registra\b"), "También se registran"),
    (re.compile(r"\bla evidencia también registra\b"), "también se registran"),
    (re.compile(r"\bLa evidencia muestra\b"), "Se observa"),
    (re.compile(r"\bla evidencia muestra\b"), "se observa"),
    (re.compile(r"\bLa evidencia observable indica\b"), "El análisis indica"),
    (re.compile(r"\bLa evidencia (confirma|permite|no \w+)\b"), r"El análisis \1"),
    (re.compile(r"\bla evidencia (confirma|permite|no \w+)\b"), r"el análisis \1"),
    (re.compile(r"\bcon la evidencia estática\b"), "con el análisis estático"),
    (re.compile(r"\bcontra la evidencia disponible\b"), "contra el análisis disponible"),
    (re.compile(r"\bcon la evidencia disponible\b"), "con el análisis disponible"),
    (re.compile(r"\bsolo con evidencia positiva\b"), "solo con indicios positivos"),
    (re.compile(r"\bla ausencia de evidencia de uso\b"), "la ausencia de indicios de uso"),
    (re.compile(r"\bEvidencia de uso\b"), "Uso observable"),
    (re.compile(r"pero eso no es evidencia\b"), "pero eso no lo respalda el código"),
    (re.compile(r"\bNo se encontró evidencia observable de uso\b"), "No se observó uso"),
    (re.compile(r"\(evidencia, referencias y procedencia\)"), "(referencias y procedencia)"),
]


def humanize_text(text: str) -> str:
    out = _VIEW_FILE.sub(r"\1", _LINE_ONLY.sub("", text))
    out = _LINE_AFTER_NOTE.sub("", out)
    for pattern, repl in _RULES:
        out = pattern.sub(repl, out)
    return out


def _runs(runs: list[Run]) -> list[Run]:
    return [replace(r, text=_VIEW_FILE.sub(r"\1", r.text)) if r.code else replace(r, text=humanize_text(r.text)) for r in runs]


def humanize_blocks(blocks: list) -> list:
    """Same block tree with humanized prose. Code runs (identifiers, routes) and figures are never touched."""
    out: list = []
    for b in blocks:
        if isinstance(b, (Para, Heading)):
            out.append(replace(b, runs=_runs(b.runs)))
        elif isinstance(b, Bullets):
            out.append(Bullets([_runs(i) for i in b.items]))
        elif isinstance(b, Table):
            out.append(Table([_runs(h) for h in b.headers], [[_runs(c) for c in row] for row in b.rows], b.caption))
        elif isinstance(b, Callout):
            out.append(replace(b, title=humanize_text(b.title), blocks=humanize_blocks(b.blocks)))
        elif isinstance(b, Details):
            out.append(replace(b, summary=humanize_text(b.summary), blocks=humanize_blocks(b.blocks)))
        elif isinstance(b, Quote):
            out.append(replace(b, blocks=humanize_blocks(b.blocks)))
        else:
            out.append(b)
    return out
