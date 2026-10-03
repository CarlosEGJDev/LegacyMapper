"""Template/profile fingerprint (V5.3-R2.3): SHA-256 over the effective `documentation_v52` configuration content.

Covers `defaults/{templates,profiles,i18n,noise}/**/*.json`, the `custom_dir` equivalents (labelled
`custom/...`), the active profiles and their effective languages. Read order, mtimes and absolute paths
do not matter; an unreadable file raises `OSError`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from ._common import FINGERPRINT_ALGORITHM, canonical_json, length_prefixed, normalize_newlines


def _defaults_dir(defaults_dir: str | Path | None) -> Path:
    """The defaults directory to fingerprint: the given one, else the installed `documentation_v52/defaults`."""
    if defaults_dir is not None:
        return Path(defaults_dir)
    from legacy_documenter.documentation_v52.config import DEFAULTS_DIR

    return DEFAULTS_DIR


def _default_profiles() -> tuple[str, ...]:
    """The profiles `generate_documentation_v52` renders when none are given."""
    from legacy_documenter.documentation_v52.engine import DEFAULT_PROFILES

    return DEFAULT_PROFILES


TEMPLATE_KINDS = ("templates", "profiles", "i18n", "noise")


def _effective_profile_language(profile_id: str, defaults: Path, custom: Path | None) -> str | None:
    """`language` of the profile file the registry would use (custom over default), or `None` if unreadable."""
    for base in (custom, defaults):
        if base is None:
            continue
        path = base / "profiles" / f"{profile_id}.json"
        if path.is_file():
            try:
                language = json.loads(path.read_text(encoding="utf-8")).get("language")
            except (OSError, ValueError, AttributeError):
                return None
            return language if isinstance(language, str) else None
    return None


def template_profile_fingerprint(
    profiles: Iterable[str] | None = None,
    custom_dir: str | Path | None = None,
    defaults_dir: str | Path | None = None,
) -> str:
    """SHA-256 over the content of `documentation_v52/defaults/{templates,profiles,i18n,noise}/**/*.json`,
    the `custom_dir` equivalents (labelled `custom/...`, so an override differs from the default), the active
    profiles (their order matters: it orders the output) and each profile's effective language.

    Order of reading, mtimes and absolute paths do not matter. An unreadable file raises `OSError`
    (the caller must not reuse anything derived from it).
    """
    defaults = _defaults_dir(defaults_dir)
    custom = Path(custom_dir) if custom_dir else None
    active = list(_default_profiles() if profiles is None else profiles)
    records: dict[str, bytes] = {}
    for source, base in (("default", defaults), ("custom", custom)):
        if base is None:
            continue
        for kind in TEMPLATE_KINDS:
            for path in sorted((base / kind).rglob("*.json")) if (base / kind).is_dir() else ():
                if path.is_file():
                    records[f"{source}/{path.relative_to(base).as_posix()}"] = normalize_newlines(path.read_bytes())
    digest = hashlib.sha256(f"TEMPLATE_PROFILE_FINGERPRINT/{FINGERPRINT_ALGORITHM}\n".encode("ascii"))
    for label in sorted(records):
        digest.update(length_prefixed(label, records[label]))
    meta = canonical_json({
        "profiles": active,
        "languages": {pid: _effective_profile_language(pid, defaults, custom) for pid in active},
        "custom_dir_present": bool(custom is not None and custom.is_dir()),
    })
    digest.update(length_prefixed("meta", meta.encode("ascii")))
    return digest.hexdigest()
