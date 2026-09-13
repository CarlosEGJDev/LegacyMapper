"""File-system read/hash primitives for the readiness gate (DEBT-002, V4.1-R4)."""
import hashlib
from pathlib import Path


def _read(path: Path) -> str:
    """Reads a UTF-8 canonical artifact without modifying it."""
    return path.read_text(encoding="utf-8")


def _hash(path: Path) -> str:
    """Returns the SHA-256 used by immutability and repeatability checks."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
