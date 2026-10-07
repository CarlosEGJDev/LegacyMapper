"""Logical-line reassembly and comment stripping for VB.NET source scanning (V4.1-R6)."""
from pathlib import Path


def scan_logical_lines(path: Path) -> list[tuple[int, str]]:
    """Joins VB `_` line-continuations and strips blank/comment-only lines."""
    result = []
    pending = ""
    start_line = 0
    for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = strip_comment(raw).strip()
        if not line:
            continue
        if line.endswith("_"):
            if not pending:
                start_line = idx
            pending += line[:-1].rstrip() + " "
            continue
        result.append((start_line or idx, pending + line))
        pending = ""
        start_line = 0
    if pending:
        result.append((start_line, pending))
    return result


def strip_comment(line: str) -> str:
    """Removes a trailing `'` comment while respecting quoted string literals."""
    in_string = False
    idx = 0
    while idx < len(line):
        if line[idx] == '"':
            if idx + 1 < len(line) and line[idx + 1] == '"':
                idx += 2
                continue
            in_string = not in_string
        if line[idx] == "'" and not in_string:
            return line[:idx]
        idx += 1
    return line
