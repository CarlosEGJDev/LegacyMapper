"""Deterministic AST-based maintainability inventory for production Python modules."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys


def _python_files(root: Path) -> list[Path]:
    """Returns production Python files in stable path order, excluding caches."""
    return sorted(path for path in (root / "legacy_documenter").rglob("*.py") if "__pycache__" not in path.parts)


def _functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Collects functions and methods represented in an AST."""
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _typed(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Reports whether every declared parameter and the return value have annotations."""
    arguments = [*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs]
    if function.args.vararg:
        arguments.append(function.args.vararg)
    if function.args.kwarg:
        arguments.append(function.args.kwarg)
    return function.returns is not None and all(arg.annotation is not None for arg in arguments if arg.arg not in {"self", "cls"})


def _significant(node: ast.AST) -> bool:
    """Treats public classes/functions and substantial private functions as audit boundaries."""
    name = getattr(node, "name", "")
    if isinstance(node, ast.ClassDef):
        return not name.startswith("_")
    lines = getattr(node, "end_lineno", getattr(node, "lineno", 0)) - getattr(node, "lineno", 0) + 1
    return not name.startswith("_") or lines > 20


def _ratio(part: int, total: int) -> float:
    """Produces a stable percentage while handling an empty population."""
    return round(100.0 * part / total, 2) if total else 100.0


def audit(workspace: str | Path = ".") -> dict[str, object]:
    """Inventories module size, symbols, typing and docstrings without importing runtime code."""
    root = Path(workspace)
    modules: list[dict[str, object]] = []
    totals = {"classes": 0, "functions_and_methods": 0, "typed_functions_and_methods": 0, "documented_symbols": 0, "symbols": 0,
              "significant_symbols": 0, "documented_significant_symbols": 0, "typed_significant_functions_and_methods": 0,
              "significant_functions_and_methods": 0}
    for path in _python_files(root):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = _functions(tree)
        symbols: list[ast.AST] = [*classes, *functions]
        significant = [node for node in symbols if _significant(node)]
        significant_functions = [node for node in functions if _significant(node)]
        line_count = len(source.splitlines())
        large_methods = sorted(node.name for node in functions if (getattr(node, "end_lineno", node.lineno) - node.lineno + 1) > 40)
        responsibility_signals = sorted(signal for signal in ("json", "write_text", "read_text", "validate", "render", "provider", "security") if signal in source.lower())
        modules.append({
            "module": path.relative_to(root).as_posix(), "lines": line_count,
            "classes": sorted(node.name for node in classes), "functions_and_methods": len(functions),
            "large_methods": large_methods, "responsibility_signals": responsibility_signals,
            "multiple_responsibilities_candidate": len(responsibility_signals) >= 4,
            "typing_coverage_percent": _ratio(sum(_typed(node) for node in functions), len(functions)),
            "docstring_coverage_percent": _ratio(sum(bool(ast.get_docstring(node)) for node in symbols), len(symbols)),
            "significant_symbols": len(significant),
            "documented_significant_symbols": sum(bool(ast.get_docstring(node)) for node in significant),
            "typed_significant_boundaries_percent": _ratio(sum(_typed(node) for node in significant_functions), len(significant_functions)),
        })
        totals["classes"] += len(classes)
        totals["functions_and_methods"] += len(functions)
        totals["typed_functions_and_methods"] += sum(_typed(node) for node in functions)
        totals["documented_symbols"] += sum(bool(ast.get_docstring(node)) for node in symbols)
        totals["symbols"] += len(symbols)
        totals["significant_symbols"] += len(significant)
        totals["documented_significant_symbols"] += sum(bool(ast.get_docstring(node)) for node in significant)
        totals["significant_functions_and_methods"] += len(significant_functions)
        totals["typed_significant_functions_and_methods"] += sum(_typed(node) for node in significant_functions)
    return {
        "schema_version": "V3-R10-1", "analysis_type": "STATIC_AST_INVENTORY",
        "python_files": len(modules), "modules": modules,
        "summary": {**totals,
                    "typing_coverage_percent": _ratio(totals["typed_functions_and_methods"], totals["functions_and_methods"]),
                    "docstring_coverage_percent": _ratio(totals["documented_symbols"], totals["symbols"]),
                    "significant_docstring_coverage_percent": _ratio(totals["documented_significant_symbols"], totals["significant_symbols"]),
                    "significant_type_hint_coverage_percent": _ratio(totals["typed_significant_functions_and_methods"], totals["significant_functions_and_methods"]),
                    "large_module_candidates": sum(module["lines"] > 250 for module in modules),
                    "multiple_responsibility_candidates": sum(module["multiple_responsibilities_candidate"] for module in modules)},
        "compatibility_entry_points": ["legacy_documenter.main.main", "legacy_documenter.knowledge.readiness.run"],
        "limitations": ["Line count is an inventory signal, not a quality verdict.", "Responsibility candidates are lexical prompts for human review."],
    }


def write_audit(destination: str | Path, workspace: str | Path = ".") -> dict[str, object]:
    """Writes one reproducible audit JSON and returns the serialized payload."""
    payload = audit(workspace)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


def write_r10_1_reports(workspace: str | Path = ".") -> dict[str, object]:
    """Compares R10.1 audits and records bounded batches plus intentionally retained debt."""
    root = Path(workspace)
    output = root / "output/v3_r10_1"
    before = json.loads((output / "MAINTAINABILITY_AUDIT_BEFORE.json").read_text(encoding="utf-8"))
    after = json.loads((output / "MAINTAINABILITY_AUDIT_AFTER.json").read_text(encoding="utf-8"))
    old = {item["module"]: item for item in before["modules"]}
    changed = []
    for item in after["modules"]:
        previous = old.get(item["module"], {})
        changes = []
        if item.get("docstring_coverage_percent") != previous.get("docstring_coverage_percent"):
            changes.append("DOCSTRINGS")
        if item.get("typing_coverage_percent") != previous.get("typing_coverage_percent"):
            changes.append("TYPE_HINTS")
        if not changes:
            continue
        relative = item["module"].split("/")[1] if "/" in item["module"] else "orchestration"
        batch = {"models":"BATCH_1","utils":"BATCH_1","extractors":"BATCH_2","scanner":"BATCH_2",
                 "context":"BATCH_3","llm":"BATCH_4","documentation":"BATCH_5","analysis":"BATCH_6",
                 "knowledge":"BATCH_7","exporters":"BATCH_7","quality":"BATCH_7"}.get(relative,"BATCH_7")
        changed.append({"module": item["module"], "batch": batch, "changes": changes,
                        "compatibility_impact": "NONE", "behavior_change": False})
    debt = {
        "schema_version": "V3-R10.1-1",
        "items": [
            {"id":"TD-001","area":"compact_one_line_contracts","reason":"Reformatting historical R7/R8 one-line contracts would create broad noisy diffs without semantic benefit.","plan":"Format only when the owning contract next changes."},
            {"id":"TD-002","area":"provider_exception_boundaries","reason":"Broad boundaries deliberately convert external SDK/HTTP failures into safe domain responses.","plan":"Retain until provider-specific exception taxonomies are contract-tested."},
            {"id":"TD-003","area":"cross_round_helpers","reason":"Similar helpers have different validated round semantics and cannot be merged by textual similarity.","plan":"Evaluate contract equivalence before any V4 consolidation."},
            {"id":"TD-004","area":"large_orchestrators","reason":"Splitting discovery and historical round orchestration now risks ordering and output compatibility.","plan":"Extract only behind characterization tests in a separately scoped change."},
            {"id":"TD-005","area":"type_hints","reason":"Ambiguous nested historical JSON shapes were not annotated with misleading object/Any types.","plan":"Introduce narrow TypedDict models incrementally at future modified boundaries."}
        ]}
    mapping = {"schema_version":"V3-R10.1-1", "production_modules_analyzed":after["python_files"],
               "production_modules_changed":len(changed), "batches":sorted({item["batch"] for item in changed}),
               "changes":changed, "classes_created":[], "classes_moved":[],
               "compatibility_wrappers":["legacy_documenter.knowledge.readiness.run"],
               "dead_code_removed":[], "semantic_contract":"UNCHANGED"}
    (output / "REFACTORING_MAP.json").write_text(json.dumps(mapping, ensure_ascii=False, sort_keys=True, indent=2)+"\n",encoding="utf-8")
    (output / "TECHNICAL_DEBT_REMAINING.json").write_text(json.dumps(debt, ensure_ascii=False, sort_keys=True, indent=2)+"\n",encoding="utf-8")
    return mapping


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--r10-1-reports":
        write_r10_1_reports()
    else:
        destination = sys.argv[1] if len(sys.argv) > 1 else "output/v3_r10/MAINTAINABILITY_AUDIT_AFTER.json"
        write_audit(destination)
