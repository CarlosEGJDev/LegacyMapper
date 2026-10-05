"""Cache controls of one run (V5.3-R2.8): the single object CLI and library both map to.

R1 vocabulary: `--cache-mode {auto,off,refresh}`, `--cache-dir`, `--verify-cache[=fast|hash]`, `--trust-mtime`,
`--incremental-max-changed-ratio`. They change *how much is reused*, never the analysis' meaning, so none of them
enters a config fingerprint (see `fingerprints.configuration`). Nothing here reads the disk except
`resolve_cache_dir`, which only inspects paths.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

from .manifest import CACHE_DIRNAME

CACHE_MODES = ("auto", "off", "refresh")
MODE_AUTO, MODE_OFF, MODE_REFRESH = CACHE_MODES
VERIFY_FAST, VERIFY_HASH = "fast", "hash"
VERIFY_LEVELS = (VERIFY_FAST, VERIFY_HASH)


class CacheOptionError(ValueError):
    """A cache control has an unusable value (never raised for a bad *cache*, only for bad *options*)."""


@dataclass(frozen=True)
class CacheOptions:
    """`verify` is `fast` (the normal checksum validation) or `hash` (strict deep verification, see `verify`).

    `max_changed_ratio=None` is R1's "disabled" default; otherwise a fraction in `[0, 1]`.
    """

    mode: str = MODE_AUTO
    cache_dir: str | Path | None = None
    verify: str = VERIFY_FAST
    trust_mtime: bool = False
    max_changed_ratio: float | None = None

    def validate(self) -> "CacheOptions":
        """Returns `self` or raises `CacheOptionError`."""
        if self.mode not in CACHE_MODES:
            raise CacheOptionError(f"modo desconocido {self.mode!r}")
        if self.verify not in VERIFY_LEVELS:
            raise CacheOptionError(f"nivel de verificación desconocido {self.verify!r}")
        if self.max_changed_ratio is not None:
            validate_ratio(self.max_changed_ratio)
        return self


def validate_ratio(value: float) -> float:
    """`value` as a float in `[0, 1]`; `CacheOptionError` for NaN, infinities or anything outside the range."""
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        raise CacheOptionError(f"ratio inválido {value!r}") from None
    if math.isnan(ratio) or not 0.0 <= ratio <= 1.0:
        raise CacheOptionError(f"el ratio debe estar entre 0 y 1 (recibido {value!r})")
    return ratio


def ratio_argument(text: str) -> float:
    """argparse `type=` for `--incremental-max-changed-ratio`."""
    try:
        return validate_ratio(text)
    except CacheOptionError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def _is_within(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def resolve_cache_dir(repo_root: str | Path, output_dir: str | Path, cache_dir: str | Path | None) -> Path:
    """The absolute cache directory: `<output>/_cache_v53` by default, else `cache_dir` (relative to the cwd).

    An explicit directory is resolved (symlinks/junctions followed) and refused when the cache could touch what is
    not its own: the repository (it would be scanned and mixed), the output directory itself or any ancestor of
    either (cache housekeeping would run over foreign files), or an existing regular file. Raises `CacheOptionError`.
    """
    output = Path(output_dir).resolve()
    if cache_dir is None or str(cache_dir) == "":
        return output / CACHE_DIRNAME
    target = Path(cache_dir).expanduser().resolve()
    repo = Path(repo_root).resolve()
    if target.is_file():
        raise CacheOptionError(f"--cache-dir apunta a un archivo: {target}")
    if _is_within(target, repo) or _is_within(repo, target):
        raise CacheOptionError("--cache-dir no puede estar dentro del repositorio ni contenerlo")
    if _is_within(output, target):  # the output itself or one of its ancestors
        raise CacheOptionError("--cache-dir no puede ser el directorio de salida ni un ancestro suyo")
    return target


def describe_location(target: Path, output_dir: str | Path) -> dict:
    """Where the cache lives, safe to persist: a path relative to the output when inside it, never an absolute path."""
    output = Path(output_dir).resolve()
    if _is_within(target, output):
        return {"location": "internal", "relative_dir": target.relative_to(output).as_posix() or "."}
    return {"location": "external", "relative_dir": None}
