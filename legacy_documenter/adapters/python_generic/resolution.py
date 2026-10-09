"""python-generic CALL / ENTRY resolution over extracted symbols and imports (static, conservative).

A call is `confirmed` only when module-level scoping, imports and class structure identify its target without guessing.
Known external callees (builtins, standard library, third-party imports) are `confirmed` as *external* with no internal
target. Anything else -- attribute calls on values of unknown type, dynamic callees, re-exports that cannot be followed --
stays `unresolved`: no fuzzy name matching, no invented relationships.
"""
from __future__ import annotations

from legacy_documenter.evidence.identity import poly33_id

from ._names import BUILTIN_NAMES, STDLIB_MODULES

MAX_FOLLOW = 5


class SymbolIndex:
    """Module / class / import tables built once from the extraction outputs (`symbols` and the per-file `calls` groups)."""

    def __init__(self, groups: list[dict], symbols: list[dict]) -> None:
        self.modules: dict[str, dict] = {}
        self.classes: dict[str, dict] = {}
        self.module_of_file: dict[str, str] = {}
        for symbol in symbols:
            if symbol["kind"] == "module":
                self.modules[symbol["name"]] = {"file": symbol["file"], "project": symbol["project_path"],
                                                "functions": {m["name"] for m in symbol["members"] if m["kind"] == "function"}}
                self.module_of_file[symbol["file"]] = symbol["name"]
            else:
                self.classes[symbol["name"]] = {"module": symbol["namespace"], "project": symbol["project_path"], "file": symbol["file"],
                                                "methods": {m["name"] for m in symbol["members"]}, "bases": symbol["inherits"]}
        self.tops = {name.split(".")[0] for name in self.modules}
        self.bindings: dict[str, dict] = {}
        self.package_of: dict[str, bool] = {}
        for group in groups:
            module = self.module_of_file.get(group["file"])
            if module is None:
                continue
            self.package_of[group["file"]] = bool(group.get("package_init"))
            self.bindings[group["file"]] = self._bind(module, bool(group.get("package_init")), group["imports"])

    def _bind(self, module: str, is_package: bool, imports: list[dict]) -> dict:
        bound: dict[str, tuple] = {}
        base_parts = module.split(".") if is_package else module.split(".")[:-1]
        for record in imports:
            if record["kind"] == "import":
                if record["asname"]:
                    bound[record["asname"]] = ("module", record["module"])
                else:
                    top = record["module"].split(".")[0]
                    bound.setdefault(top, ("module", top))
                continue
            if record["level"]:
                keep = len(base_parts) - (record["level"] - 1)
                if keep < 0:
                    continue
                absolute = ".".join(base_parts[:keep] + ([record["module"]] if record["module"] else []))
            else:
                absolute = record["module"]
            if not absolute or record["name"] == "*":
                continue
            alias = record["asname"] or record["name"]
            bound[alias] = ("module", f"{absolute}.{record['name']}") if f"{absolute}.{record['name']}" in self.modules else ("object", absolute, record["name"])
        return bound

    # -- classification ---------------------------------------------------------------------------
    def external_kind(self, top: str) -> str | None:
        if top in self.tops:
            return None
        return "stdlib" if top in STDLIB_MODULES else "third_party"

    def lookup(self, file: str, name: str, depth: int = 0) -> tuple | None:
        """What a bare name means in `file`: function / class / module / external / builtin / unknown_internal / None."""
        module = self.module_of_file[file]
        if name in self.modules[module]["functions"]:
            return ("function", module, name)
        if f"{module}.{name}" in self.classes:
            return ("class", f"{module}.{name}")
        binding = self.bindings.get(file, {}).get(name)
        if binding is None:
            return ("builtin", name) if name in BUILTIN_NAMES else None
        if binding[0] == "module":
            top = binding[1].split(".")[0]
            kind = self.external_kind(top)
            return ("external", top, kind) if kind else ("module", binding[1])
        _, source, attr = binding
        kind = self.external_kind(source.split(".")[0])
        if kind:
            return ("external", source.split(".")[0], kind)
        if source in self.modules and attr in self.modules[source]["functions"]:
            return ("function", source, attr)
        if f"{source}.{attr}" in self.classes:
            return ("class", f"{source}.{attr}")
        if source in self.modules and depth < MAX_FOLLOW:  # re-export from a package `__init__`
            followed = self.lookup(self.modules[source]["file"], attr, depth + 1)
            if followed is not None and followed[0] in {"function", "class", "external", "module"}:
                return followed
        return ("unknown_internal", source, attr)

    def method_target(self, class_full: str, method: str, depth: int = 0) -> str | None:
        """The class (itself or a statically known base) that defines `method`, or None."""
        info = self.classes.get(class_full)
        if info is None or depth > MAX_FOLLOW:
            return None
        if method in info["methods"]:
            return class_full
        for base in info["bases"]:
            chain = base.split(".")
            first = self.lookup(info["file"], chain[0])
            resolved = None
            if first and first[0] == "class" and len(chain) == 1:
                resolved = first[1]
            elif first and first[0] == "module":
                dotted = ".".join([first[1], *chain[1:-1]])
                resolved = f"{dotted}.{chain[-1]}" if f"{dotted}.{chain[-1]}" in self.classes else None
            found = self.method_target(resolved, method, depth + 1) if resolved else None
            if found:
                return found
        return None

    def project_of(self, owner: str) -> str | None:
        return (self.classes.get(owner) or self.modules.get(owner) or {}).get("project")

    # -- chain resolution -------------------------------------------------------------------------
    def resolve_chain(self, file: str, owner: str, chain: list[str] | None, receiver_type: list[str] | None = None,
                      method_name: str | None = None) -> dict:
        """-> {"kind": internal|instantiation|external|unresolved, ...}; never raises."""
        if file not in self.module_of_file or (not chain and not receiver_type):
            return {"kind": "unresolved"}
        if receiver_type:  # receiver provably built by `Cls(...)`: the method is looked up on that class (and its known bases)
            built = self.resolve_chain(file, owner, receiver_type)
            klass = built.get("instantiates")
            method = chain[-1] if chain else method_name
            defining = self.method_target(klass, method) if klass and method else None
            if defining:
                return {**self._internal(defining, method), "basis": "receiver_instantiation"}
            if built["kind"] == "external":
                return built
            return {"kind": "unresolved"}
        if not chain:
            return {"kind": "unresolved"}
        root = chain[0]
        if len(chain) == 1:
            return self._from_binding(self.lookup(file, root), None)
        if root in {"self", "cls"} and owner in self.classes:
            if len(chain) == 2:
                defining = self.method_target(owner, chain[1])
                return self._internal(defining, chain[1]) if defining else {"kind": "unresolved"}
            return {"kind": "unresolved"}
        binding = self.lookup(file, root)
        if binding is None:
            return {"kind": "unresolved"}
        if binding[0] == "module":
            dotted = ".".join([binding[1], *chain[1:-1]])
            final = chain[-1]
            if dotted not in self.modules:
                return {"kind": "unresolved"}
            return self._from_binding(self._in_module(dotted, final), None)
        if binding[0] == "class" and len(chain) == 2:
            defining = self.method_target(binding[1], chain[1])
            return self._internal(defining, chain[1]) if defining else {"kind": "unresolved"}
        if binding[0] in {"external", "builtin"}:
            return self._from_binding(binding if binding[0] == "external" else ("external", root, "builtin"), None)
        return {"kind": "unresolved"}

    def _in_module(self, module: str, name: str) -> tuple | None:
        if name in self.modules[module]["functions"]:
            return ("function", module, name)
        if f"{module}.{name}" in self.classes:
            return ("class", f"{module}.{name}")
        return self.lookup(self.modules[module]["file"], name) if name in self.bindings.get(self.modules[module]["file"], {}) else None

    def _from_binding(self, binding: tuple | None, _unused) -> dict:
        if binding is None:
            return {"kind": "unresolved"}
        if binding[0] == "function":
            return self._internal(binding[1], binding[2])
        if binding[0] == "class":
            init = self.method_target(binding[1], "__init__")
            result = self._internal(init, "__init__") if init else {"kind": "instantiation_without_init"}
            return {**result, "instantiates": binding[1], "kind": "instantiation" if init else "instantiation_without_init"}
        if binding[0] in {"external", "builtin"}:
            return {"kind": "external", "external_module": binding[1], "external_kind": binding[2] if binding[0] == "external" else "builtin"}
        return {"kind": "unresolved"}

    def _internal(self, owner: str, member: str) -> dict:
        return {"kind": "internal", "owner": owner, "member": member, "target": f"{owner}.{member}", "project": self.project_of(owner)}


def resolve_calls(groups: list[dict], symbols: list[dict]) -> tuple[list[dict], list[dict]]:
    """Resolves every call; returns the resolved per-file groups and the aggregated `Method -> ...` dependencies."""
    index = SymbolIndex(groups, symbols)
    resolved_groups: list[dict] = []
    aggregated: dict[tuple, dict] = {}
    for group in groups:
        calls, instantiations = [], []
        for call in group["calls"]:
            rooted = call["receiver"] is None or call["receiver_path"] is not None  # `f().g()` / `x[0].g()` have no plain-name root
            chain = [*(call["receiver_path"].split(".") if call["receiver_path"] else []), call["method_name"]] if call["method_name"] and rooted else None
            outcome = index.resolve_chain(group["file"], call["containing_class"], chain, call.get("receiver_type"), call["method_name"])
            record = dict(call)
            record["resolution_kind"] = outcome["kind"]
            if outcome.get("basis"):
                record["resolution_basis"] = outcome["basis"]
            if outcome["kind"] in {"internal", "instantiation"}:
                record.update(resolved_target=outcome["target"], resolved_owner=outcome["owner"], resolved_member=outcome["member"],
                              resolved_project=outcome["project"], confidence="confirmed")
            elif outcome["kind"] in {"external", "instantiation_without_init"}:
                record["confidence"] = "confirmed"
                if outcome["kind"] == "external":
                    record.update(external_module=outcome["external_module"], external_kind=outcome["external_kind"])
            if outcome.get("instantiates"):
                evidence = call["evidence"]
                instantiations.append({"type_name": outcome["instantiates"], "variable_name": None, "containing_class": call["containing_class"],
                                       "containing_method": call["containing_method"], "resolved_type": outcome["instantiates"],
                                       "confidence": "confirmed", "evidence": evidence})
            calls.append(record)
            source = f"{call['containing_class']}.{call['containing_method']}"
            for target, kind in ((record.get("resolved_target"), "Method -> Method"), (outcome.get("instantiates"), "Method -> InstantiatesClass")):
                if target:
                    _aggregate(aggregated, source, target, kind, group["file"], call["expression"], "confirmed")
            if outcome["kind"] == "unresolved" and call["method_name"]:
                _aggregate(aggregated, source, call["expression"], "Method -> Method", group["file"], call["expression"], "unresolved")
        resolved_groups.append({**group, "calls": calls, "instantiations": instantiations})
    return resolved_groups, sorted(aggregated.values(), key=lambda d: (d["source"], d["target"], d["dependency_type"]))


def _aggregate(table: dict, source: str, target: str, kind: str, file: str, expression: str, confidence: str) -> None:
    entry = table.setdefault((source, target, kind), {
        "source": source, "target": target, "dependency_type": kind, "source_file": file, "evidence": expression,
        "confidence": confidence, "evidence_samples": [], "evidence_count": 0})
    entry["evidence_count"] += 1
    if len(entry["evidence_samples"]) < 3 and expression not in entry["evidence_samples"]:
        entry["evidence_samples"].append(expression)


def resolve_entries(groups: list[dict], symbols: list[dict], web_events: list[dict], resolved_groups: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Entry points from `if __name__ == "__main__"` blocks: confirmed only when the callee statically resolves to an internal function."""
    index = SymbolIndex(resolved_groups or groups, symbols)
    entry_points, bindings = [], []
    seen: dict[str, int] = {}
    for group in web_events:
        module = index.module_of_file.get(group["file"])
        if module is None:
            continue
        project = index.modules[module]["project"]
        for entry in group["entries"]:
            chosen = entry
            outcome = index.resolve_chain(group["file"], module, entry["callee_chain"])
            if outcome["kind"] != "internal":
                for candidate in entry.get("candidates", []):
                    attempt = index.resolve_chain(group["file"], module, candidate["callee_chain"])
                    if attempt["kind"] == "internal":
                        chosen, outcome = {**entry, **candidate}, attempt
                        break
            confirmed = outcome["kind"] == "internal"
            handler = (chosen["callee_chain"] or [None])[-1]
            entry = {**entry, "expression": chosen["expression"]}
            parts = ("EP", group["file"], entry["kind"], entry["line"], entry["expression"])
            ordinal = seen[parts] = seen.get(parts, -1) + 1
            entry_id = poly33_id("EP", group["file"], entry["kind"], entry["line"], entry["expression"], ordinal or None)
            evidence = [{"file": group["file"], "line": entry["line"], "expression": entry["expression"] or "__main__ guard", "project": project,
                         "class_name": module, "method": handler}]
            entry_points.append({
                "id": entry_id, "type": "cli_main", "webform": group["file"], "control": None, "event": "main", "handler": handler,
                "class_name": module, "project": project, "confidence": "confirmed" if confirmed else "unresolved", "evidence": evidence,
                "handler_method": outcome["target"] if confirmed else None, "outgoing_calls": [],
            })
            bindings.append({"id": "EVB-" + entry_id[3:], "webform": group["file"], "control": None, "control_type": None, "event": "main",
                             "handler": handler, "class_name": module, "project": project,
                             "confidence": "confirmed" if confirmed else "unresolved", "evidence": evidence})
    return entry_points, bindings, []
