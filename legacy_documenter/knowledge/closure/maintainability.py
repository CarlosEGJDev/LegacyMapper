"""Deterministic pre-refactor maintainability baseline (V4-R14, section G).

Diagnostic only. Computes simple, reproducible counts (module counts, line
counts, docstring/type-hint presence) over the repository tree using only
`os.walk`/`ast` from the standard library — no new dependency, no heuristic
"code quality score". This baseline exists to help a later, explicitly
scoped post-V4 maintainability refactor prove it did not change behavior;
it does not itself recommend or perform any refactor.
"""
from __future__ import annotations

import ast
from pathlib import Path

_EXCLUDED_DIR_NAMES = {"__pycache__"}


def _iter_py_files(root: Path) -> list[Path]:
    """Returns every `.py` file under `root`, excluding caches, sorted for
    determinism (independent of filesystem enumeration order)."""
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in _EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.as_posix())


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def _docstring_and_type_hint_gaps(path: Path) -> tuple[int, int, int, int]:
    """Returns (public_defs, missing_docstring, functions, missing_return_annotation)
    for one module, via `ast` — a function/class starting with `_` is treated
    as private and excluded from the "public" counts."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return (0, 0, 0, 0)

    public_defs = 0
    missing_docstring = 0
    functions = 0
    missing_return_annotation = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            is_public = not node.name.startswith("_")
            if is_public:
                public_defs += 1
                if ast.get_docstring(node) is None:
                    missing_docstring += 1
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
                if node.returns is None:
                    missing_return_annotation += 1

    return (public_defs, missing_docstring, functions, missing_return_annotation)


def build_maintainability_baseline(repo_root: Path) -> dict:
    """Builds the deterministic maintainability diagnostic snapshot.

    All counts are computed live from the current repository tree so the
    baseline stays accurate as long as it is regenerated from the same
    checkout; nothing here is hardcoded from memory.
    """
    knowledge_root = repo_root / "legacy_documenter" / "knowledge"
    production_root = repo_root / "legacy_documenter"
    tests_root = repo_root / "tests"

    production_files = _iter_py_files(production_root)
    knowledge_files = _iter_py_files(knowledge_root)
    test_files = _iter_py_files(tests_root)

    package_inventory = sorted(
        p.name
        for p in knowledge_root.iterdir()
        if p.is_dir() and p.name not in _EXCLUDED_DIR_NAMES
    )

    module_lines = [
        {"path": p.relative_to(repo_root).as_posix(), "lines": _line_count(p)}
        for p in knowledge_files
    ]
    largest_modules = sorted(
        module_lines, key=lambda item: (-item["lines"], item["path"])
    )[:10]

    total_public_defs = 0
    total_missing_docstring = 0
    total_functions = 0
    total_missing_return_annotation = 0
    for path in knowledge_files:
        public_defs, missing_docstring, functions, missing_return = (
            _docstring_and_type_hint_gaps(path)
        )
        total_public_defs += public_defs
        total_missing_docstring += missing_docstring
        total_functions += functions
        total_missing_return_annotation += missing_return

    return {
        "production_python_module_count": len(production_files),
        "knowledge_package_python_module_count": len(knowledge_files),
        "test_python_module_count": len(test_files),
        "knowledge_package_inventory": package_inventory,
        "largest_knowledge_modules_by_line_count": largest_modules,
        "docstring_observations": {
            "public_classes_and_functions_scanned": total_public_defs,
            "missing_docstring_count": total_missing_docstring,
            "note": (
                "Spot-checked in V4-R13 across domain/canonical/plugin_projection/"
                "projection and found consistent with "
                "docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md; this count is "
                "a deterministic full-tree re-check, not a new quality gate."
            ),
        },
        "type_hint_observations": {
            "functions_scanned": total_functions,
            "missing_return_annotation_count": total_missing_return_annotation,
            "note": (
                "A missing return annotation is not automatically a defect "
                "(e.g. `-> None` is sometimes omitted); this is a diagnostic "
                "count for the post-V4 refactor, not a lint failure."
            ),
        },
        "duplicated_report_serialization_pattern": {
            "observation": (
                "Every R7-R13 knowledge sub-package repeats the same "
                "plain-dict-builder + sorted-key JSON-renderer pattern in its "
                "own contract_report.py/example_report.py."
            ),
            "tracked_as": "DEBT-001",
        },
        "known_mixed_responsibility_modules": [
            {
                "path": "legacy_documenter/knowledge/readiness.py",
                "observation": (
                    "Mixes document parsing, evidence-closure computation, "
                    "and file I/O in one module. Unmodified V3 code; left "
                    "as-is per AGENTS.md rather than silently changing an "
                    "approved upstream semantic contract."
                ),
                "tracked_as": "DEBT-002",
            }
        ],
        "known_maintainability_debt": [
            "TD-001",
            "TD-002",
            "TD-003",
            "TD-004",
            "TD-005",
            "DEBT-001",
            "DEBT-002",
            "DEBT-003",
        ],
    }
