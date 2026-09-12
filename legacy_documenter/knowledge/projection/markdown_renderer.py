"""Deterministic pure-function Markdown rendering for V4-R11 `DocumentProjection`s.

Traceability marker format (documented here and in the R11 contract artifact):

    <!-- knowledge_id: KNO-... -->

placed immediately after each rendered canonical item. It is a plain HTML comment, inert in
rendered Markdown/HTML previews, non-invasive to normal reading, and stable/deterministic.

All canonical `statement`/`metadata` content is treated as untrusted **display** data only:
this module never `eval`s, `exec`s, dynamically imports, shell-executes, or template-executes
any of it. A statement shaped like a prompt injection or like HTML/Markdown markup is written
out verbatim as inert text — this module has no template engine and no execution path, so
such content can never do anything beyond being displayed.

This module performs no file I/O: it only turns `DocumentProjection` objects into Markdown
strings. Writing those strings to disk is deliberately kept in a separate module
(`disk_io.py`).
"""
from legacy_documenter.knowledge.canonical.models import CanonicalKnowledgeEntry
from legacy_documenter.knowledge.projection.models import DocumentProjection

EMPTY_DOCUMENT_MARKER = "No approved canonical knowledge is currently projected to this document."

#: Human-readable Spanish label per `TemporalState` value, used only for display; the
#: underlying `TemporalState` value is never altered, inferred, or auto-converted.
_TEMPORAL_LABEL = {
    "AS_IS": "Estado actual (AS_IS)",
    "TO_BE": "Estado objetivo (TO_BE)",
    "HISTORICAL": "Histórico (HISTORICAL)",
}


def _render_item(entry: CanonicalKnowledgeEntry) -> list[str]:
    """Renders one canonical entry as a deterministic Markdown block, verbatim and inert.

    The canonical statement is written out unchanged: never paraphrased, summarized, executed,
    or reinterpreted. `AS_IS`/`TO_BE`/`HISTORICAL` are rendered as-is and are never relabeled
    as conflicting or superseded.
    """
    lines = [f"### {entry.knowledge_id}", ""]
    lines.append(f"> {entry.statement}")
    lines.append("")
    lines.append(
        f"- Naturaleza: `{entry.nature.value}` | Tipo de fuente: `{entry.source_type.value}` "
        f"| Estado: `{entry.status.value}`"
    )
    if entry.temporal_state is not None:
        label = _TEMPORAL_LABEL.get(entry.temporal_state.value, entry.temporal_state.value)
        lines.append(f"- Contexto temporal: {label}")
    lines.append(f"<!-- knowledge_id: {entry.knowledge_id} -->")
    lines.append("")
    return lines


def render_document(projection: DocumentProjection) -> str:
    """Renders one `DocumentProjection` as a byte-deterministic Markdown string.

    Identical `DocumentProjection` input always renders to byte-identical output: item order
    is already fixed by the caller (`ProjectionService`), and this function performs no
    additional non-deterministic sorting, timestamping, or randomness. An empty projection
    renders the fixed `EMPTY_DOCUMENT_MARKER` instead of any invented filler content.
    """
    target = projection.target
    lines = [f"# {target.title}", ""]
    lines += [
        "```text",
        f"document_path={target.document_path}",
        f"family={target.family}",
        f"purpose={target.purpose}",
        "projection_kind=HUMAN_READABLE_DOCUMENT_PROJECTION",
        "canonical_knowledge_source=R10_CANONICAL_KNOWLEDGE_COLLECTION",
        "is_canonical_knowledge_source=false",
        "```",
        "",
        "## Conocimiento canónico proyectado",
        "",
    ]
    if projection.is_empty:
        lines.append(f"_{EMPTY_DOCUMENT_MARKER}_")
        lines.append("")
    else:
        for entry in projection.entries:
            lines += _render_item(entry)
    return "\n".join(lines).rstrip() + "\n"


def render_documents(documents: dict) -> dict:
    """Renders every `DocumentProjection` in `documents` (path -> projection) to Markdown text.

    Returns a plain `{document_path: markdown_text}` dict; iteration order of the input never
    affects the returned mapping's content (each value is rendered independently and
    deterministically).
    """
    return {path: render_document(projection) for path, projection in documents.items()}
