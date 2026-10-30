"""Global path/resource contract (post-V5 pre-H5 Gate A).

LegacyMapper depends on explicit inputs and packaged runtime resources, never on the machine or folder where it
was developed. This module is the single place that decides whether a user-supplied source/output path is usable
*before* any scanner, analyzer or provider runs:

* the source must exist, be a directory and be readable;
* the output must be creatable/writable (its parent may be missing: it is created later);
* source and output must not contradict each other (equal, or one inside the other).

A violation raises `PathContractError` with a stable `code`; callers turn it into the existing exit-code contract
(4 = FAILED). Nothing here scans, writes output or touches a provider; the only filesystem effect is a throw-away
probe file in the nearest existing output ancestor, removed immediately.

`runtime_resource_root()` answers where packaged resources (built-in templates) live: inside the package itself,
never relative to the current working directory or a repository checkout.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

SOURCE_NOT_FOUND = "SOURCE_PATH_NOT_FOUND"
SOURCE_NOT_DIRECTORY = "SOURCE_PATH_NOT_DIRECTORY"
SOURCE_NOT_READABLE = "SOURCE_PATH_NOT_READABLE"
OUTPUT_NOT_DIRECTORY = "OUTPUT_PATH_NOT_DIRECTORY"
OUTPUT_NOT_WRITABLE = "OUTPUT_PATH_NOT_WRITABLE"
OUTPUT_NO_EXISTING_PARENT = "OUTPUT_PATH_NOT_CREATABLE"
LAYOUT_CONTRADICTORY = "SOURCE_OUTPUT_LAYOUT_CONTRADICTORY"
OUTPUT_MANIFEST_INPUT_NOT_FOUND = "OUTPUT_MANIFEST_INPUT_NOT_FOUND"
OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY = "OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY"


class PathContractError(ValueError):
    """An input path violates the path contract; `code` is stable and machine-detectable."""

    def __init__(self, code: str, message: str, path: str | os.PathLike | None = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.path = str(path) if path is not None else None

    def to_dict(self) -> dict:
        payload = {"status": "PATH_CONTRACT_VIOLATION", "code": self.code, "message": self.message}
        if self.path is not None:
            payload["path"] = self.path
        return payload


def runtime_resource_root() -> Path:
    """The `legacy_documenter` package directory: the only anchor packaged resources may use."""
    return Path(__file__).resolve().parents[1]


def builtin_templates_root() -> Path:
    """Built-in templates travel inside the package (`legacy_documenter/templates/<kind>/<name>`)."""
    return runtime_resource_root() / "templates"


def _resolve(path: str | os.PathLike) -> Path:
    return Path(os.path.expanduser(os.fspath(path))).resolve()


def _same_or_inside(candidate: Path, container: Path) -> bool:
    cand, cont = os.path.normcase(str(candidate)), os.path.normcase(str(container))
    if cand == cont:
        return True
    try:
        return os.path.commonpath([cand, cont]) == cont
    except ValueError:  # different drives
        return False


def validate_source_directory(source: str | os.PathLike) -> Path:
    """Returns the resolved source directory or raises `PathContractError`; reads no file contents."""
    if source is None or str(source).strip() == "":
        raise PathContractError(SOURCE_NOT_FOUND, "the source path is empty")
    resolved = _resolve(source)
    if not resolved.exists():
        raise PathContractError(SOURCE_NOT_FOUND, f"the source path does not exist: {source}", source)
    if not resolved.is_dir():
        raise PathContractError(SOURCE_NOT_DIRECTORY, f"the source path is not a directory: {source}", source)
    try:
        with os.scandir(resolved) as entries:
            next(entries, None)
    except OSError as exc:
        raise PathContractError(SOURCE_NOT_READABLE, f"the source directory cannot be read: {source} ({exc.__class__.__name__})", source) from None
    return resolved


def validate_existing_output_directory(path: str | os.PathLike, *, not_found_code: str, not_directory_code: str, writable: bool = False) -> Path:
    """An already generated output directory that a command reads (and, with `writable`, writes into). Same error shape as the
    rest of the contract; reads no file contents."""
    if path is None or str(path).strip() == "":
        raise PathContractError(not_found_code, "the directory path is empty")
    resolved = _resolve(path)
    if not resolved.exists():
        raise PathContractError(not_found_code, f"the directory does not exist: {path}", path)
    if not resolved.is_dir():
        raise PathContractError(not_directory_code, f"the path is not a directory: {path}", path)
    if writable and not _probe_writable(resolved):
        raise PathContractError(OUTPUT_NOT_WRITABLE, f"the directory is not writable: {path}", path)
    return resolved


def _nearest_existing_ancestor(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.exists():
            return candidate
    return None


def _probe_writable(directory: Path) -> bool:
    """A real create/remove probe: `os.access` is unreliable for directories on Windows."""
    try:
        handle = tempfile.TemporaryFile(dir=directory)
    except OSError:
        return False
    handle.close()
    return True


def validate_output_directory(output: str | os.PathLike) -> Path:
    """Returns the resolved output directory (not created) or raises `PathContractError`."""
    if output is None or str(output).strip() == "":
        raise PathContractError(OUTPUT_NOT_WRITABLE, "the output path is empty")
    resolved = _resolve(output)
    if resolved.exists():
        if not resolved.is_dir():
            raise PathContractError(OUTPUT_NOT_DIRECTORY, f"the output path exists and is not a directory: {output}", output)
        if not _probe_writable(resolved):
            raise PathContractError(OUTPUT_NOT_WRITABLE, f"the output directory is not writable: {output}", output)
        return resolved
    ancestor = _nearest_existing_ancestor(resolved)
    if ancestor is None:
        raise PathContractError(OUTPUT_NO_EXISTING_PARENT, f"no existing parent for the output path: {output}", output)
    if not ancestor.is_dir():
        raise PathContractError(OUTPUT_NOT_DIRECTORY, f"a parent of the output path is not a directory: {ancestor}", output)
    if not _probe_writable(ancestor):
        raise PathContractError(OUTPUT_NOT_WRITABLE, f"the output location is not writable: {output}", output)
    return resolved


def validate_source_and_output(source: str | os.PathLike, output: str | os.PathLike) -> tuple[Path, Path]:
    """Validates both and rejects a contradictory layout; returns `(source, output)` resolved. Source is checked first."""
    src = validate_source_directory(source)
    out = validate_output_directory(output)
    if _same_or_inside(out, src):
        raise PathContractError(LAYOUT_CONTRADICTORY, "the output must not be the source directory or inside it (the source is read-only)", output)
    if _same_or_inside(src, out):
        raise PathContractError(LAYOUT_CONTRADICTORY, "the source must not be the output directory or inside it", source)
    return src, out
