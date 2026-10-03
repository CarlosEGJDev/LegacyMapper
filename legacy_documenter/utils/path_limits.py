"""Output-path length preflight for Windows (V5.3-R2.2, contract V5.3-R1 section 14).

Windows limits a path to MAX_PATH = 260 characters *including* the terminating NUL, i.e.
259 usable characters, unless long paths are enabled. LegacyMapper writes files atomically
through a temporary sibling (`.{name}.{8 random chars}.tmp`), so the real constraint on a
final path is `len(final) + ATOMIC_TEMP_OVERHEAD <= 259`: a path that fits on its own can
still make the temp file fail with an ambiguous `FileNotFoundError` halfway through a stage
(observed at V5.3-R0.1: the `.tmp` of a v52 document measured exactly 260).

`check_output_paths` is a pure function over lengths, so it never touches the disk and can
run *before* a stage writes anything. Standard library only.
"""
from __future__ import annotations

import os
from pathlib import Path

#: MAX_PATH counts the terminating NUL: usable characters on a default Windows installation.
WINDOWS_MAX_USABLE_PATH = 259

#: Usable characters with the extended-length prefix (`\\?\`): 32,767 including the NUL.
WINDOWS_EXTENDED_MAX_USABLE_PATH = 32766

#: Extra characters of the atomic temp name over the final name: `.{name}.` + 8 random + `.tmp`
#: is `len(name) + 14` (see `tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp")`).
ATOMIC_TEMP_OVERHEAD = 14

ERROR_CODE = "OUTPUT_PATH_TOO_LONG"

_EXTENDED_PREFIX = "\\\\?\\"
_EXTENDED_UNC_PREFIX = "\\\\?\\UNC\\"


class OutputPathTooLongError(ValueError):
    """A path a stage is about to write exceeds the platform limit. Raised before anything is written."""

    code = ERROR_CODE

    def __init__(
        self, message: str, *, worst_path: str, worst_length: int, limit: int,
        output_root: str, suggested_max_output_length: int | None, offending_count: int,
    ) -> None:
        super().__init__(message)
        self.worst_path = worst_path
        self.worst_length = worst_length
        self.limit = limit
        self.output_root = output_root
        self.suggested_max_output_length = suggested_max_output_length
        self.offending_count = offending_count


def windows_long_paths_enabled() -> bool:
    """Whether the OS has long paths enabled (`LongPathsEnabled` = 1). Read-only; never changes the OS."""
    if os.name != "nt":
        return False
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem") as key:
            return winreg.QueryValueEx(key, "LongPathsEnabled")[0] == 1
    except OSError:
        return False


def applicable_path_limit(long_paths: bool = False, os_name: str | None = None) -> int | None:
    """The usable path length a stage must respect, or `None` when no practical limit applies.

    `None` off Windows (POSIX `PATH_MAX` is far above anything LegacyMapper writes). On Windows:
    259, unless the OS has long paths enabled or the caller opted in with `long_paths` (the stage
    then writes through extended-length paths, see `to_extended_path`).
    """
    if (os_name or os.name) != "nt":
        return None
    if long_paths:
        return WINDOWS_EXTENDED_MAX_USABLE_PATH
    return WINDOWS_EXTENDED_MAX_USABLE_PATH if windows_long_paths_enabled() else WINDOWS_MAX_USABLE_PATH


def to_extended_path(path: str | Path) -> Path:
    """The extended-length (`\\\\?\\`) form of an absolute Windows path; unchanged elsewhere.

    Only the filesystem handle changes: callers keep their logical/relative paths (manifests,
    links, slugs) exactly as they are.
    """
    if os.name != "nt":
        return Path(path)
    absolute = os.path.abspath(str(path))
    if absolute.startswith(_EXTENDED_PREFIX):
        return Path(absolute)
    if absolute.startswith("\\\\"):
        return Path(_EXTENDED_UNC_PREFIX + absolute[2:])
    return Path(_EXTENDED_PREFIX + absolute)


def suggested_max_output_length(limit: int, longest_relative_to_output: int, temp_overhead: int = ATOMIC_TEMP_OVERHEAD) -> int:
    """Longest `--output` (characters) for which the longest relative path still fits under `limit`."""
    return limit - temp_overhead - 1 - longest_relative_to_output


def check_output_paths(
    base: str | Path,
    relative_paths: list[str],
    limit: int | None,
    *,
    output_root: str | Path | None = None,
    temp_overhead: int = ATOMIC_TEMP_OVERHEAD,
    platform_label: str = "Windows",
) -> None:
    """Raises `OutputPathTooLongError` if any `base/relative` (plus the atomic temp name) exceeds `limit`.

    Pure: measures lengths only. `limit=None` means no limit applies (no-op). `output_root` is the
    user's `--output` (defaults to `base`); `base` may sit below it (e.g. `<output>/documentation_v52`),
    and the suggestion accounts for that. Reports the *worst* path, how many exceed the limit and the
    longest `--output` that would make every path fit.
    """
    if limit is None or not relative_paths:
        return
    base_text = os.path.abspath(str(base))
    base_len = len(base_text)
    worst_relative = max(relative_paths, key=len)
    worst_final = base_len + 1 + len(worst_relative)
    worst_needed = worst_final + temp_overhead
    if worst_needed <= limit:
        return
    offending = sum(1 for rel in relative_paths if base_len + 1 + len(rel) + temp_overhead > limit)
    output_text = os.path.abspath(str(output_root if output_root is not None else base))
    below_output = max(base_len - len(output_text), 0)  # separator + the subfolder(s) between --output and base
    longest_relative_to_output = below_output + len(worst_relative)
    suggested = suggested_max_output_length(limit, longest_relative_to_output, temp_overhead)
    worst_path = base_text + os.sep + worst_relative.replace("/", os.sep)
    message = (
        f"{ERROR_CODE}: {offending} ruta(s) de salida exceden el límite de {limit} caracteres de {platform_label}; "
        f"la peor mide {worst_final} caracteres ({worst_needed} contando el archivo temporal de escritura atómica, "
        f"+{temp_overhead}): {worst_path} . "
        f"--output actual: {output_text} ({len(output_text)} caracteres). "
        f"Longitud máxima sugerida para --output: {suggested} caracteres. "
        f"No se escribió nada de esta etapa. Use un --output más corto"
        f"{' o --long-paths' if platform_label == 'Windows' else ''}."
    )
    raise OutputPathTooLongError(
        message, worst_path=worst_path, worst_length=worst_needed, limit=limit, output_root=output_text,
        suggested_max_output_length=suggested, offending_count=offending,
    )
