"""Static, side-effect-free parsing of one Python source file (V5.9 python-generic adapter).

Only `ast.parse` is used: the target is data. It is never imported, compiled for execution, evaluated or run, and
nothing here touches the file system beyond the text handed in. Output is plain JSON-able data per file.
"""
from __future__ import annotations

import ast
import warnings
from collections import Counter
from pathlib import PurePosixPath

MAX_EXPRESSION_CHARS = 160
MODULE_SCOPE = "<module>"
CLASS_SCOPE = "<class>"

#: Receiver type is unknown, only the method name is characteristic of pathlib -> `inferred`, never `confirmed`.
PATH_METHODS = {
    "read_text": "file_read", "read_bytes": "file_read", "write_text": "file_write", "write_bytes": "file_write",
    "touch": "file_write", "rename": "file_write", "unlink": "file_delete", "rmdir": "file_delete",
    "mkdir": "directory_create", "iterdir": "directory_list", "rglob": "directory_list", "glob": "directory_list",
}
#: Module-qualified calls whose module is known from the file's own imports -> `confirmed`.
MODULE_FUNCTIONS = {
    "os": {"remove": "file_delete", "unlink": "file_delete", "rmdir": "file_delete", "removedirs": "file_delete",
           "makedirs": "directory_create", "mkdir": "directory_create", "listdir": "directory_list",
           "scandir": "directory_list", "walk": "directory_list", "rename": "file_write", "replace": "file_write"},
    "shutil": {"copy": "file_write", "copy2": "file_write", "copyfile": "file_write", "copytree": "file_write",
               "move": "file_write", "rmtree": "file_delete"},
    "glob": {"glob": "directory_list", "iglob": "directory_list"},
    "tempfile": {"mkdtemp": "directory_create", "mkstemp": "file_write", "NamedTemporaryFile": "file_write",
                 "TemporaryDirectory": "directory_create"},
}
#: Callees that only wrap the real entry call of a `__main__` block.
ENTRY_WRAPPERS = frozenset({("sys", "exit"), ("exit",), ("quit",), ("SystemExit",), ("asyncio", "run"), ("print",)})


def module_name(relative_path: str) -> str:
    """Dotted module name implied by the path relative to the scan root (`pkg/__init__.py` -> `pkg`)."""
    parts = list(PurePosixPath(relative_path.replace("\\", "/")).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) or "__init__"


def is_package_init(relative_path: str) -> bool:
    """True for `__init__.py` (relative imports resolve against the package itself, not its parent)."""
    return PurePosixPath(relative_path.replace("\\", "/")).name == "__init__.py"


def _expression(node: ast.AST) -> str:
    text = " ".join(ast.unparse(node).split())
    return text if len(text) <= MAX_EXPRESSION_CHARS else text[:MAX_EXPRESSION_CHARS - 3] + "..."


def _chain(node: ast.AST) -> list[str] | None:
    """`a.b.c` -> ['a','b','c']; None when the root is not a plain name (call, subscript, literal...)."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return parts[::-1]
    return None


def _imports(tree: ast.AST) -> list[dict]:
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend({"kind": "import", "module": a.name, "name": None, "asname": a.asname, "level": 0, "line": node.lineno} for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.extend({"kind": "from", "module": node.module, "name": a.name, "asname": a.asname, "level": node.level, "line": node.lineno}
                         for a in node.names)
    return sorted(found, key=lambda i: (i["line"], i["kind"], i["module"] or "", i["name"] or "", i["asname"] or ""))


def _bound_names(node: ast.AST) -> list[str]:
    """Every name this single node (re)binds, in any form; used to prove a local has exactly one binding."""
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return [node.id]
    if isinstance(node, ast.arg):
        return [node.arg]
    if isinstance(node, (ast.Global, ast.Nonlocal)):
        return [n for name in node.names for n in (name, name)]  # a declared name can be rebound elsewhere: never inferable
    if isinstance(node, ast.ExceptHandler) and node.name:
        return [node.name]
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return [(a.asname or a.name).split(".")[0] for a in node.names]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
        return [node.name]
    return []


def _local_instantiations(function: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, list[str]]:
    """`name = Callee(...)` locals bound exactly once in the whole function (nested scopes included, conservatively).

    Statically this proves what `name` is when it is used, so `name.method()` can be resolved without guessing; any other
    binding form (parameter, loop/with/except target, import, `global`/`nonlocal`, second assignment, `del`) disables it.
    """
    counts: Counter[str] = Counter()
    assigned: dict[str, list[str]] = {}
    for node in ast.walk(function):
        for name in _bound_names(node):
            counts[name] += 1
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call):
            chain = _chain(node.value.func)
            if chain:
                assigned[node.targets[0].id] = chain
    return {name: chain for name, chain in assigned.items() if counts[name] == 1}


def _is_main_guard(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.If) or not isinstance(stmt.test, ast.Compare) or len(stmt.test.ops) != 1:
        return False
    left, right = stmt.test.left, stmt.test.comparators[0]
    names = {n.id for n in (left, right) if isinstance(n, ast.Name)}
    consts = {n.value for n in (left, right) if isinstance(n, ast.Constant)}
    return isinstance(stmt.test.ops[0], ast.Eq) and names == {"__name__"} and consts == {"__main__"}


def _decorator_names(decorators: list[ast.expr]) -> list[str]:
    names = []
    for decorator in decorators:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        chain = _chain(target)
        if chain:
            names.append(".".join(chain))
    return sorted(set(names))


def _open_mode(call: ast.Call) -> str:
    mode = call.args[1] if len(call.args) > 1 else next((k.value for k in call.keywords if k.arg == "mode"), None)
    return mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else "r"


class _Collector:
    def __init__(self, module: str, file: str, imports: list[dict]) -> None:
        self.module, self.file = module, file
        self.module_aliases = {i["asname"] or i["module"].split(".")[0]: (i["module"] if i["asname"] else i["module"].split(".")[0])
                               for i in imports if i["kind"] == "import"}
        self.from_names = {i["asname"] or i["name"]: (i["module"], i["name"]) for i in imports if i["kind"] == "from" and i["level"] == 0 and i["module"]}
        self.functions: list[dict] = []
        self.classes: list[dict] = []
        self.calls: list[dict] = []
        self.file_operations: list[dict] = []
        self.entries: list[dict] = []

    # -- structure --------------------------------------------------------------------------------
    def run(self, tree: ast.Module) -> None:
        self._body(tree.body, self.module, MODULE_SCOPE, None)

    def _body(self, statements: list[ast.stmt], owner: str, member: str, klass: dict | None) -> None:
        for stmt in statements:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._function(stmt, owner, member, klass)
            elif isinstance(stmt, ast.ClassDef):
                self._class(stmt, owner, member, klass)
            elif klass is None and owner == self.module and _is_main_guard(stmt):
                self._main_guard(stmt)
                self._scan(stmt, owner, member)
            elif isinstance(stmt, (ast.If, ast.Try, ast.TryStar, ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)):
                self._compound(stmt, owner, member, klass)
            else:
                self._scan(stmt, owner, member)

    def _compound(self, stmt: ast.stmt, owner: str, member: str, klass: dict | None) -> None:
        blocks = [getattr(stmt, f) for f in ("body", "orelse", "finalbody") if isinstance(getattr(stmt, f, None), list)]
        handlers = list(getattr(stmt, "handlers", []))
        nested = {id(s) for block in blocks for s in block} | {id(h) for h in handlers}
        for child in ast.iter_child_nodes(stmt):
            if id(child) not in nested:
                self._scan(child, owner, member)
        for block in blocks:
            self._body(block, owner, member, klass)
        for handler in handlers:
            if handler.type is not None:
                self._scan(handler.type, owner, member)
            self._body(handler.body, owner, member, klass)

    def _function(self, stmt: ast.FunctionDef | ast.AsyncFunctionDef, owner: str, member: str, klass: dict | None) -> None:
        for decorator in stmt.decorator_list:
            self._scan(decorator, owner, member)
        decorators = _decorator_names(stmt.decorator_list)
        entry = {
            "kind": "method" if klass is not None else "function", "name": stmt.name, "line": stmt.lineno,
            "accessibility": "Private" if stmt.name.startswith("_") and not stmt.name.startswith("__") else "Public",
            "shared": any(d.split(".")[-1] in {"staticmethod", "classmethod"} for d in decorators),
            "async": isinstance(stmt, ast.AsyncFunctionDef),
        }
        (klass["members"] if klass is not None else self.functions).append(entry)
        types = _local_instantiations(stmt)
        for child in stmt.body:
            self._scan(child, owner, stmt.name, types)

    def _class(self, stmt: ast.ClassDef, owner: str, member: str, outer: dict | None) -> None:
        for decorator in stmt.decorator_list:
            self._scan(decorator, owner, member)
        qualname = f"{outer['qualname']}.{stmt.name}" if outer else stmt.name
        klass = {
            "qualname": qualname, "name": f"{self.module}.{qualname}", "kind": "class", "line": stmt.lineno, "members": [],
            "accessibility": "Private" if stmt.name.startswith("_") else "Public",
            "modifiers": _decorator_names(stmt.decorator_list), "inherits": [_expression(b) for b in stmt.bases],
        }
        self.classes.append(klass)
        for base in stmt.bases:
            self._scan(base, owner, member)
        self._body(stmt.body, klass["name"], CLASS_SCOPE, klass)

    def _main_guard(self, stmt: ast.If) -> None:
        """Entry candidates of an `if __name__ == "__main__"` block: every non-wrapper callee in source order (the resolver
        takes the first one that statically resolves to an internal function, so `print(json.dumps(run()))` still finds `run`)."""
        candidates: list[tuple[list[str] | None, str]] = []
        for node in self._calls_in(stmt.body):
            chain = _chain(node.func)
            if chain is not None and tuple(chain) in ENTRY_WRAPPERS:
                continue
            if (chain, _expression(node.func)) not in candidates:
                candidates.append((chain, _expression(node.func)))
        first = candidates[0] if candidates else (None, None)
        self.entries.append({"kind": "main_guard", "line": stmt.lineno, "callee_chain": first[0], "expression": first[1],
                             "candidates": [{"callee_chain": c, "expression": e} for c, e in candidates[:8]]})

    @staticmethod
    def _calls_in(statements: list[ast.stmt]) -> list[ast.Call]:
        found = [n for s in statements for n in ast.walk(s) if isinstance(n, ast.Call)]
        return sorted(found, key=lambda n: (n.lineno, n.col_offset))

    # -- calls and file operations ----------------------------------------------------------------
    def _scan(self, node: ast.AST, owner: str, member: str, types: dict | None = None) -> None:
        stack = [node]
        while stack:
            current = stack.pop()
            if isinstance(current, ast.Call):
                self._call(current, owner, member, types or {})
            stack.extend(reversed(list(ast.iter_child_nodes(current))))

    def _call(self, call: ast.Call, owner: str, member: str, types: dict) -> None:
        chain = _chain(call.func)
        method_name = chain[-1] if chain else (call.func.attr if isinstance(call.func, ast.Attribute) else None)
        expression = _expression(call.func) + "(...)"
        receiver = None if isinstance(call.func, ast.Name) else (_expression(call.func.value) if isinstance(call.func, ast.Attribute) else None)
        self.calls.append({
            "expression": expression, "method_name": method_name, "receiver": receiver,
            "receiver_path": ".".join(chain[:-1]) if chain and len(chain) > 1 else None,
            "arguments_count": len(call.args) + len(call.keywords), "containing_class": owner, "containing_method": member,
            "evidence": {"file": self.file, "line": call.lineno, "expression": expression, "project": None, "class_name": owner, "method": member},
            "receiver_type": self._receiver_type(call, chain, types),
            "resolved_target": None, "resolved_project": None, "confidence": "unresolved", "candidates": [],
        })
        operation = self._file_operation(call, chain)
        if operation:
            self.file_operations.append({**operation, "file": self.file, "line": call.lineno, "expression": expression, "class": owner, "method": member})

    @staticmethod
    def _receiver_type(call: ast.Call, chain: list[str] | None, types: dict) -> list[str] | None:
        """The callee chain of the class instantiation that provably produced the receiver, if any:
        `Cls(...).m()` or `x.m()` where `x = Cls(...)` is `x`'s only binding in this function."""
        if chain and len(chain) == 2 and chain[0] in types:
            return types[chain[0]]
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Call):
            return _chain(call.func.value.func)
        return None

    def _file_operation(self, call: ast.Call, chain: list[str] | None) -> dict | None:
        if not chain:  # e.g. `Path(p).write_text(...)`: the root is a call, so only the method name is known
            if isinstance(call.func, ast.Attribute) and call.func.attr in PATH_METHODS:
                return {"operation_kind": PATH_METHODS[call.func.attr], "provider": "pathlib_method_name", "confidence": "inferred"}
            return None
        if chain == ["open"]:
            mode = _open_mode(call)
            kind = "file_write" if any(c in mode for c in "wax+") else "file_read"
            return {"operation_kind": kind, "provider": "builtins.open", "confidence": "confirmed"}
        if len(chain) == 1 and chain[0] in self.from_names:
            module, name = self.from_names[chain[0]]
            kind = MODULE_FUNCTIONS.get(module.split(".")[0], {}).get(name)
            return {"operation_kind": kind, "provider": module.split(".")[0], "confidence": "confirmed"} if kind else None
        module = self.module_aliases.get(chain[0])
        if module and len(chain) == 2:
            kind = MODULE_FUNCTIONS.get(module, {}).get(chain[1])
            return {"operation_kind": kind, "provider": module, "confidence": "confirmed"} if kind else None
        if len(chain) >= 2 and chain[-1] in PATH_METHODS:
            return {"operation_kind": PATH_METHODS[chain[-1]], "provider": "pathlib_method_name", "confidence": "inferred"}
        return None


def parse_python_source(source: str | bytes, relative_path: str) -> dict:
    """Parses one file into plain data. Raises `SyntaxError`/`ValueError` for unparseable input (callers record an error)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # the target is data: its own SyntaxWarnings are not ours to print
        tree = ast.parse(source, filename=relative_path)
    module = module_name(relative_path)
    imports = _imports(tree)
    collector = _Collector(module, relative_path, imports)
    collector.run(tree)

    def symbol(name: str, kind: str, line: int, accessibility: str, modifiers: list, inherits: list, members: list) -> dict:
        return {
            "name": name, "kind": kind, "file": relative_path, "namespace": module, "declared_namespace": module, "root_namespace": None,
            "effective_namespace": module, "project_path": None, "namespace_confidence": "confirmed", "accessibility": accessibility,
            "modifiers": modifiers, "inherits": inherits, "implements": [], "members": members, "line": line,
        }
    symbols = [symbol(module, "module", 1, "Public", [], [], collector.functions)]
    symbols.extend(symbol(c["name"], "class", c["line"], c["accessibility"], c["modifiers"], c["inherits"], c["members"]) for c in collector.classes)
    collector.calls.sort(key=lambda c: (c["evidence"]["line"], c["expression"]))
    return {
        "module": module, "file": relative_path, "package_init": is_package_init(relative_path), "symbols": symbols, "imports": imports,
        "calls": collector.calls, "entries": collector.entries,
        "file_operations": sorted(collector.file_operations, key=lambda o: (o["line"], o["expression"])),
    }
