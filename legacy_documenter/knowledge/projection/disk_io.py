"""Isolated file-writing helper for the V4-R11 synthetic example Markdown tree.

Deliberately kept separate from `service.py` (projection decisions) and
`markdown_renderer.py` (pure rendering): this is the *only* module in the projection package
that touches the filesystem, and it performs no projection/mapping decisions of its own. No
projection semantics depend on filesystem state.
"""
from pathlib import Path


def write_markdown_tree(root: Path, documents: dict) -> list[str]:
    """Writes each `{document_path: markdown_text}` entry under `root`, returning sorted relative paths.

    `document_path` values originate only from the closed, validated `ProjectionTarget` set
    (see `legacy_documenter.knowledge.projection.models.validate_target_path`); this function
    performs no additional path acceptance of its own and never writes outside `root`.
    """
    written: list[str] = []
    for relative_path in sorted(documents):
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(documents[relative_path], encoding="utf-8", newline="\n")
        written.append(relative_path)
    return sorted(written)
