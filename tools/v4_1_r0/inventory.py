"""Deterministic AST-based production-file inventory for V4.1-R0.

Read-only static analysis over `legacy_documenter/` (every historical V1-V4
package, not only the V4 `knowledge` sub-tree). Uses only the Python
standard library (`ast`, `pathlib`). No file is imported/executed; every
finding comes from parsing source text, so the analysis itself cannot
trigger a provider call or any side effect.

This module intentionally lives under `tools/`, outside the
`legacy_documenter` production package: it is V4.1-R0 planning tooling, not
a new knowledge-domain capability, and placing it under
`legacy_documenter/knowledge/` would blur that boundary (see the R0 result
document for the placement rationale).
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

EXCLUDED_DIR_NAMES = {"__pycache__"}

FILESYSTEM_NAMES = {
    "open", "Path", "read_text", "write_text", "read_bytes", "write_bytes",
    "mkdir", "iterdir", "rglob", "glob", "exists", "unlink", "rmtree",
    "makedirs", "listdir",
}
FILESYSTEM_MODULES = {"pathlib", "shutil", "os", "os.path", "tempfile", "glob"}
NETWORK_PROVIDER_MODULES = {
    "urllib", "urllib.request", "urllib.error", "http", "http.client",
    "socket", "requests", "asyncio",
}
NETWORK_PROVIDER_NAME_HINTS = ("provider", "gemini", "copilot", "llm")

PARSING_HINTS = ("ast.parse", "tokenize", "re.compile", "xml.", "ElementTree", "parse(")
SERIALIZATION_HINTS = ("json.dumps", "json.loads", "sort_keys", "render_", "to_dict", "as_dict")
VALIDATION_HINTS = ("validate", "raise ValueError", "raise TypeError", "assert ")
ORCHESTRATION_HINTS = ("def main(", "def run(", "argparse", "sys.argv")
DOMAIN_HINTS = ("dataclass", "Enum", "@dataclass")


def iter_production_files(root: Path) -> list[Path]:
    """Returns every production `.py` file under `legacy_documenter/`.

    Excludes `__pycache__`. Sorted by repository-relative POSIX path so
    results are independent of filesystem enumeration order (determinism).
    """
    base = root / "legacy_documenter"
    files = [
        p for p in base.rglob("*.py")
        if not any(part in EXCLUDED_DIR_NAMES for part in p.parts)
    ]
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _module_dotted_name(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _all_functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _all_classes(tree: ast.AST) -> list[ast.ClassDef]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def _fully_typed(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    args = [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]
    if fn.args.vararg:
        args.append(fn.args.vararg)
    if fn.args.kwarg:
        args.append(fn.args.kwarg)
    relevant = [a for a in args if a.arg not in {"self", "cls"}]
    return fn.returns is not None and all(a.annotation is not None for a in relevant)


def _span(node: ast.AST) -> int:
    return getattr(node, "end_lineno", getattr(node, "lineno", 0)) - getattr(node, "lineno", 0) + 1


def _imports(tree: ast.AST) -> tuple[list[str], list[str]]:
    """Returns (all_imported_module_names, internal_legacy_documenter_imports)."""
    modules: set[str] = set()
    internal: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
                if alias.name.startswith("legacy_documenter"):
                    internal.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # Relative import; recorded distinctly since the dotted
                # target depends on the importing module's own package.
                target = ("." * node.level) + (node.module or "")
                modules.add(target)
                internal.add(target)
            elif node.module:
                modules.add(node.module)
                if node.module.startswith("legacy_documenter"):
                    internal.add(node.module)
    return sorted(modules), sorted(internal)


def _exception_observations(tree: ast.AST) -> dict[str, int]:
    bare = 0
    broad_exception = 0
    total_handlers = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            total_handlers += 1
            if node.type is None:
                bare += 1
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                broad_exception += 1
    return {"total_handlers": total_handlers, "bare_except": bare, "except_exception": broad_exception}


def _source_hints(source: str) -> set[str]:
    lowered = source.lower()
    hits: set[str] = set()
    if any(h in source for h in PARSING_HINTS):
        hits.add("parsing")
    if any(h in source for h in SERIALIZATION_HINTS):
        hits.add("serialization")
    if any(h in source for h in VALIDATION_HINTS):
        hits.add("validation")
    if any(h in source for h in ORCHESTRATION_HINTS):
        hits.add("orchestration")
    if any(h in source for h in DOMAIN_HINTS):
        hits.add("domain_modeling")
    if any(name in lowered for name in ("open(", "read_text", "write_text", "path(", "mkdir", "rglob")):
        hits.add("filesystem")
    if any(hint in lowered for hint in NETWORK_PROVIDER_NAME_HINTS):
        hits.add("provider_or_network")
    return hits


def _filesystem_access(modules: Iterable[str], source: str) -> bool:
    if any(m in FILESYSTEM_MODULES or m.startswith("pathlib") for m in modules):
        return True
    return any(name in source for name in ("open(", ".read_text(", ".write_text(", ".mkdir(", ".rglob(", ".iterdir("))


def _network_or_provider_access(modules: Iterable[str], path_str: str) -> bool:
    if any(m in NETWORK_PROVIDER_MODULES for m in modules):
        return True
    return any(hint in path_str.lower() for hint in ("providers/", "llm/"))


def _risk_category(line_count: int, responsibility_count: int, exc: dict[str, int], path_str: str) -> str:
    """Refactor-risk (not security) classification.

    Diagnostic heuristic, not a mechanical verdict: a historical V1-V3
    orchestrator with many responsibilities and broad exception handling is
    VERY_HIGH risk to touch without characterization; a small single-purpose
    module is LOW risk regardless of exact line count.
    """
    historical = any(seg in path_str for seg in (
        "legacy_documenter/documentation/", "legacy_documenter/analysis/",
        "legacy_documenter/scanner/", "legacy_documenter/context/",
    ))
    score = 0
    if line_count > 400:
        score += 2
    elif line_count > 200:
        score += 1
    score += max(0, responsibility_count - 2)
    if exc["except_exception"] or exc["bare_except"]:
        score += 1
    if historical:
        score += 1
    if score >= 5:
        return "VERY_HIGH"
    if score >= 3:
        return "HIGH"
    if score >= 1:
        return "MEDIUM"
    return "LOW"


def analyze_file(path: Path, root: Path) -> dict[str, object]:
    """Builds one file's inventory record. Never raises on parse failure --
    a `SyntaxError` (none expected in this repository) is reported as a
    finding rather than crashing the whole inventory."""
    rel = _rel(path, root)
    source = path.read_text(encoding="utf-8", errors="replace")
    line_count = len(source.splitlines())
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:  # pragma: no cover - not expected in this repo
        return {
            "path": rel, "line_count": line_count, "parse_error": str(exc),
            "class_count": 0, "function_count": 0, "public_symbol_count": 0,
            "docstring_coverage_percent": 0.0, "typed_functions_percent": 0.0,
            "imports": [], "internal_dependencies": [], "filesystem_access": False,
            "network_or_provider_access": False, "exception_boundary_observations": {},
            "responsibility_count": 0, "responsibility_signals": [], "risk_category": "HIGH",
        }

    classes = _all_classes(tree)
    functions = _all_functions(tree)
    symbols = [*classes, *functions]
    public_symbols = [s for s in symbols if _is_public(s.name)]
    documented = sum(1 for s in symbols if ast.get_docstring(s))
    typed = sum(1 for f in functions if _fully_typed(f))
    modules, internal = _imports(tree)
    exc_obs = _exception_observations(tree)
    signals = sorted(_source_hints(source))
    fs_access = _filesystem_access(modules, source)
    net_access = _network_or_provider_access(modules, rel)
    module_docstring = ast.get_docstring(tree) is not None

    return {
        "path": rel,
        "line_count": line_count,
        "class_count": len(classes),
        "function_count": len(functions),
        "public_symbol_count": len(public_symbols),
        "module_docstring_present": module_docstring,
        "docstring_coverage_percent": round(100.0 * documented / len(symbols), 2) if symbols else 100.0,
        "typed_functions_percent": round(100.0 * typed / len(functions), 2) if functions else 100.0,
        "imports": modules,
        "internal_dependencies": internal,
        "filesystem_access": fs_access,
        "network_or_provider_access": net_access,
        "exception_boundary_observations": exc_obs,
        "responsibility_count": len(signals),
        "responsibility_signals": signals,
        "risk_category": _risk_category(line_count, len(signals), exc_obs, rel),
    }


def largest_classes(root: Path, files: list[Path], top_n: int = 20) -> list[dict[str, object]]:
    """Top classes by method count (ties broken by line span, then path)."""
    records: list[dict[str, object]] = []
    for path in files:
        rel = _rel(path, root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=rel)
        except SyntaxError:  # pragma: no cover
            continue
        for node in _all_classes(tree):
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            records.append({
                "path": rel, "class_name": node.name, "method_count": len(methods),
                "line_count": _span(node),
            })
    records.sort(key=lambda r: (-r["method_count"], -r["line_count"], r["path"], r["class_name"]))
    return records[:top_n]


def largest_functions(root: Path, files: list[Path], top_n: int = 20) -> list[dict[str, object]]:
    """Top functions/methods by line span."""
    records: list[dict[str, object]] = []
    for path in files:
        rel = _rel(path, root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=rel)
        except SyntaxError:  # pragma: no cover
            continue
        class_of: dict[int, str] = {}
        for cls in _all_classes(tree):
            for n in cls.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_of[id(n)] = cls.name
        for fn in _all_functions(tree):
            qualified = f"{class_of[id(fn)]}.{fn.name}" if id(fn) in class_of else fn.name
            records.append({"path": rel, "qualified_name": qualified, "line_count": _span(fn)})
    records.sort(key=lambda r: (-r["line_count"], r["path"], r["qualified_name"]))
    return records[:top_n]


def dependency_edges(root: Path, files: list[Path]) -> dict[str, list[str]]:
    """Module-dotted-name -> sorted list of internal module dependencies it
    imports (relative imports are resolved to an absolute dotted module
    where practical)."""
    edges: dict[str, set[str]] = {}
    for path in files:
        rel = _rel(path, root)
        module_name = _module_dotted_name(path, root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=rel)
        except SyntaxError:  # pragma: no cover
            edges.setdefault(module_name, set())
            continue
        deps: set[str] = set()
        package_parts = module_name.split(".")
        package = ".".join(package_parts[:-1]) if path.name != "__init__.py" else module_name
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("legacy_documenter"):
                        deps.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    base_parts = package.split(".") if package else []
                    trim = node.level - 1
                    base_parts = base_parts[: len(base_parts) - trim] if trim else base_parts
                    target = ".".join([*base_parts, node.module]) if node.module else ".".join(base_parts)
                    if target:
                        deps.add(target)
                elif node.module and node.module.startswith("legacy_documenter"):
                    deps.add(node.module)
        edges.setdefault(module_name, set()).update(deps)
    return {k: sorted(v) for k, v in sorted(edges.items())}


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    """Simple DFS-based cycle detection over the module-dependency graph.

    Deterministic: neighbours are visited in sorted order and the result is
    itself sorted, so repeated runs over the same tree produce the same
    cycle list in the same order.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in edges}
    cycles: list[list[str]] = []
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = GRAY
        stack.append(node)
        for neighbour in edges.get(node, []):
            if neighbour not in color:
                continue
            if color[neighbour] == GRAY:
                idx = stack.index(neighbour)
                cycles.append(stack[idx:] + [neighbour])
            elif color[neighbour] == WHITE:
                visit(neighbour)
        stack.pop()
        color[node] = BLACK

    for node in sorted(edges):
        if color[node] == WHITE:
            visit(node)
    unique = sorted({tuple(c) for c in cycles})
    return [list(c) for c in unique]
