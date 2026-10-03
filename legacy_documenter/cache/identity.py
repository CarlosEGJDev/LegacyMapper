"""Repository identity and informative Git metadata for the V5.3 cache (R2.4).

Identity is the normalized absolute root path (and its SHA-256): same path with different content is the same
repository (the File State detects the content change); a different path is a different repository. Git
HEAD/branch are informative only and never part of identity or of any key. Standard library only; Git is read
from `.git/HEAD` as plain files (no subprocess).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path


def normalize_root(root: str | Path) -> str:
    """Absolute, `/`-separated path without trailing slash; lowercased on Windows (case-insensitive file systems)."""
    text = str(Path(root).resolve()).replace("\\", "/")
    if len(text) > 1:
        text = text.rstrip("/") or "/"
    return text.lower() if os.name == "nt" else text


def repository_identity(root: str | Path) -> dict:
    """`{"root_normalized", "root_fingerprint"}` for the analyzed repository root."""
    normalized = normalize_root(root)
    return {"root_normalized": normalized, "root_fingerprint": hashlib.sha256(normalized.encode("utf-8")).hexdigest()}


def git_metadata(root: str | Path) -> dict:
    """Best-effort `{"git_head", "git_branch"}` (each `None` when unavailable); never raises."""
    info: dict = {"git_head": None, "git_branch": None}
    try:
        git_dir = Path(root) / ".git"
        if not git_dir.is_dir():
            return info
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref = head[4:].strip()
            info["git_branch"] = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
            info["git_head"] = _resolve_ref(git_dir, ref)
        elif head:
            info["git_head"] = head
    except (OSError, UnicodeDecodeError):
        pass
    return info


def _resolve_ref(git_dir: Path, ref: str) -> str | None:
    """The commit a ref points to, from the loose ref file or `packed-refs`."""
    ref_file = git_dir / ref
    if ref_file.is_file():
        return ref_file.read_text(encoding="utf-8").strip() or None
    packed = git_dir / "packed-refs"
    if packed.is_file():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if line.endswith(" " + ref):
                return line.split(" ", 1)[0]
    return None
