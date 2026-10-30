"""Deterministic cross-project call resolution refinement (post-V5 Gate C, DT-04).

Runs INSIDE the existing CALL_RESOLUTION stage, over the already-extracted symbols / calls / projects: no compilation, no assembly
loading, no source reads. It only refines calls the base resolver left unresolved (or resolved ambiguously), with a conservative
precedence and explicit statuses:

    1. fully-qualified symbol           -> CONFIRMED  (basis fully_qualified_symbol)
    2. reachable by DIRECT project/assembly reference + namespace evidence (import / same namespace) -> CONFIRMED
    3. reachable by direct reference, unique, no namespace evidence                                   -> INFERRED
    4. otherwise                                                                                      -> UNRESOLVED_* (never guessed)

Never used as a basis: same method name, same class basename, same file name, proximity in the solution.
Overloads are resolved only by declared-parameter arity (`ByVal/ByRef/Optional` evidence from the declaration);
interface/base dispatch is CONFIRMED only for a declaring base type, INFERRED for a unique implementer, otherwise
`UNRESOLVED_DYNAMIC_DISPATCH`. Types owned by a referenced assembly that is not analyzed are `EXTERNAL_ASSEMBLY_BOUNDARY`.
"""
from __future__ import annotations

import posixpath
from collections import defaultdict

CONFIRMED, INFERRED, UNRESOLVED = "CONFIRMED", "INFERRED", "UNRESOLVED"
TYPE_KINDS = {"class", "module", "interface", "structure"}
SCHEMA_VERSION = "1.0"


def _posix(path: str | None) -> str:
    return str(path or "").replace("\\", "/")


def _norm(path: str) -> str:
    parts: list[str] = []
    for piece in _posix(path).split("/"):
        if piece in ("", "."):
            continue
        if piece == "..":
            if parts:
                parts.pop()
            continue
        parts.append(piece)
    return "/".join(parts)


class CrossProjectResolver:
    def __init__(self, symbols: list[dict], projects: list[dict] | None, call_groups: list[dict]) -> None:
        self.projects = {_norm(p.get("path", "")): p for p in projects or []}
        self.has_project_graph = bool(projects)
        by_assembly = {str(p.get("assembly_name") or p.get("name") or "").lower(): key for key, p in self.projects.items()}
        by_name = {str(p.get("name") or "").lower(): key for key, p in self.projects.items()}
        self.direct_refs: dict[str, set[str]] = {}
        self.missing_refs: dict[str, list[dict]] = {}         # project -> references whose target project is not analyzed
        self.assembly_names: dict[str, set[str]] = {}           # project -> lowercase referenced assembly names (DLL references)
        for key, project in self.projects.items():
            pdir = posixpath.dirname(key)
            reach, missing = set(), []
            for ref in project.get("project_references") or []:
                target = _norm(posixpath.join(pdir, _posix(ref.get("include"))))
                found = target if target in self.projects else by_name.get(str(ref.get("name") or "").lower())
                if found:
                    reach.add(found)
                else:
                    missing.append({"kind": "project_reference", "name": ref.get("name") or ref.get("include")})
            names = set()
            for ref in project.get("assembly_references") or []:
                name = str(ref.get("include") or "").split(",")[0].strip().lower()
                if not name:
                    continue
                names.add(name)
                if name in by_assembly and by_assembly[name] != key:
                    reach.add(by_assembly[name])
            self.direct_refs[key] = reach
            self.missing_refs[key] = missing
            self.assembly_names[key] = names
        self.types: dict[str, list[dict]] = defaultdict(list)
        self.file_project: dict[str, str] = {}
        self.known_namespaces: set[str] = set()
        for symbol in symbols:
            project = _norm(symbol.get("project_path") or "") or None
            if symbol.get("file") and project:
                self.file_project.setdefault(_posix(symbol["file"]).lower(), project)
            namespace = symbol.get("effective_namespace") or symbol.get("namespace")
            if namespace:
                self.known_namespaces.add(namespace.lower())
            if symbol.get("kind") not in TYPE_KINDS:
                continue
            full = f"{namespace}.{symbol['name']}" if namespace else symbol["name"]
            for name in {symbol["name"].lower(), full.lower()}:
                if symbol not in self.types[name]:
                    self.types[name].append(symbol)
        self.imports: dict[str, set[str]] = {}
        for group in call_groups:
            self.imports[_posix(group.get("file")).lower()] = {str(i.get("name") or "").lower() for i in group.get("imports", [])}

    # ---- helpers
    def project_of(self, call: dict) -> str | None:
        return self.file_project.get(_posix((call.get("evidence") or {}).get("file")).lower())

    @staticmethod
    def _project_of_symbol(symbol: dict) -> str | None:
        return _norm(symbol.get("project_path") or "") or None

    @staticmethod
    def _full(symbol: dict) -> str:
        namespace = symbol.get("effective_namespace") or symbol.get("namespace")
        return f"{namespace}.{symbol['name']}" if namespace else symbol["name"]

    def _reachable(self, candidates: list[dict], call_project: str | None) -> list[dict]:
        if call_project is None or not self.has_project_graph:
            return []
        allowed = self.direct_refs.get(call_project, set()) | {call_project}
        return [c for c in candidates if self._project_of_symbol(c) in allowed]

    def _namespace_evidence(self, candidate: dict, call: dict, call_project: str | None) -> bool:
        ns = (candidate.get("effective_namespace") or candidate.get("namespace") or "").lower()
        if not ns:
            return False
        if ns in self.imports.get(_posix((call.get("evidence") or {}).get("file")).lower(), set()):
            return True
        owner = self.projects.get(call_project or "") or {}
        root = str(owner.get("root_namespace") or "").lower()
        return bool(root) and (ns == root or ns.startswith(root + "."))

    # ---- member / overload level
    def _members(self, symbol: dict, method: str) -> list[dict]:
        return [m for m in symbol.get("members", []) if m.get("kind") in {"sub", "function"} and str(m.get("name", "")).lower() == method]

    def _pick_overload(self, members: list[dict], arguments: int) -> tuple[dict | None, str]:
        if len(members) == 1:
            return members[0], "single_declaration"
        fits = []
        for member in members:
            params = member.get("parameters")
            if params is None:
                return None, "overloads_without_signature"
            required = sum(1 for p in params if not p.get("optional") and not p.get("param_array"))
            maximum = None if any(p.get("param_array") for p in params) else len(params)
            if required <= arguments and (maximum is None or arguments <= maximum):
                fits.append(member)
        return (fits[0], "overload_arity") if len(fits) == 1 else (None, "overload_ambiguous")

    def _target(self, symbol: dict, method: str) -> dict:
        return {"target": f"{self._full(symbol)}.{method}", "project": symbol.get("project_path")}

    def check_confirmed(self, call: dict, resolution: dict) -> dict | None:
        """Second look at a call the base rules CONFIRMED (class+method unique): flags unresolvable overloads and targets in a project the
        call site does not directly reference. Returns a refinement record only when there is something to say."""
        target = str(resolution.get("target") or "")
        if "." not in target:
            return None
        class_full, method = target.rsplit(".", 1)
        project = _norm(resolution.get("project") or "") or None
        owners = [c for c in self.types.get(class_full.lower(), []) if self._project_of_symbol(c) == project] or self.types.get(class_full.lower(), [])
        if len(owners) != 1:
            return None
        owner = owners[0]
        call_project = self.project_of(call)
        record = {"schema_version": SCHEMA_VERSION, "source_project": call_project, "type_name": class_full, "target": target,
                  "project": resolution.get("project")}
        members = self._members(owner, method)
        if len(members) > 1:
            member, why = self._pick_overload(members, int(call.get("arguments_count") or 0))
            if member is None:
                return {**record, "status": UNRESOLVED, "code": "UNRESOLVED_AMBIGUOUS_CALL", "basis": why, "candidate_count": len(members),
                        "candidates": [target] * len(members), "target_project": project, "target": None, "project": None}
        if call_project and self.has_project_graph and project and project != call_project and project not in self.direct_refs.get(call_project, set()):
            return {**record, "status": INFERRED, "code": "INFERRED_UNREFERENCED_PROJECT", "basis": "unique_global_type_no_direct_reference",
                    "candidate_count": 1, "candidates": [target], "target_project": project}
        return None

    # ---- main entry
    def refine(self, call: dict, receiver_type: str | None, base: dict) -> dict | None:
        """Returns a refinement record (always JSON-able) for an unresolved/ambiguous call, or None when this layer has nothing to add."""
        method = str(call.get("method_name") or "").lower()
        if not receiver_type or not method:
            return None
        call_project = self.project_of(call)
        candidates = list(self.types.get(receiver_type.lower(), []))
        arguments = int(call.get("arguments_count") or 0)
        record = {"schema_version": SCHEMA_VERSION, "source_project": call_project, "type_name": receiver_type}

        if not candidates:
            return self._external(call, receiver_type, call_project, record)
        basis = None
        chosen: list[dict] = candidates
        if len(candidates) > 1:
            exact = [c for c in candidates if self._full(c).lower() == receiver_type.lower()]
            if len(exact) == 1 and "." in receiver_type:
                chosen, basis = exact, "fully_qualified_symbol"
            else:
                reach = self._reachable(candidates, call_project)
                with_ns = [c for c in reach if self._namespace_evidence(c, call, call_project)]
                if len(with_ns) == 1:
                    chosen, basis = with_ns, "reference_and_namespace"
                elif len(reach) == 1:
                    chosen, basis = reach, "project_reference_unique"
                else:
                    return {**record, "status": UNRESOLVED, "code": "UNRESOLVED_AMBIGUOUS_CALL", "basis": "multiple_reachable_candidates"
                            if len(reach) > 1 else "no_reachable_candidate", "candidate_count": len(candidates),
                            "candidates": sorted(f"{self._full(c)}.{method}" for c in candidates), "target_project": None}
        symbol = chosen[0]
        if symbol.get("kind") == "interface":
            impls = sorted((c for c in self._implementers(symbol) if not self.has_project_graph or call_project is None
                            or c in self._reachable([c], call_project)), key=self._full)
            if len(impls) == 1:
                return {**record, "status": INFERRED, "code": "INFERRED_UNIQUE_IMPLEMENTER", "basis": "unique_implementer", "candidate_count": 1,
                        "candidates": [f"{self._full(impls[0])}.{method}"], **self._target(impls[0], method)}
            return {**record, "status": UNRESOLVED, "code": "UNRESOLVED_DYNAMIC_DISPATCH", "basis": "interface_dispatch",
                    "candidate_count": len(impls), "candidates": [f"{self._full(c)}.{method}" for c in impls], "target_project": None,
                    "declared_target": f"{self._full(symbol)}.{method}"}
        members = self._members(symbol, method)
        owner = symbol
        if not members:                                            # declared in a base type?
            for base_name in symbol.get("inherits", []):
                bases = self.types.get(str(base_name).lower().split("(")[0], [])
                bases = bases if len(bases) == 1 else self._reachable(bases, call_project)
                if len(bases) == 1 and self._members(bases[0], method):
                    owner, members, basis = bases[0], self._members(bases[0], method), "base_declaration"
                    break
        if not members:
            return {**record, "status": UNRESOLVED, "code": "UNRESOLVED_MEMBER_NOT_DECLARED", "basis": "member_not_in_declaring_type",
                    "candidate_count": 0, "candidates": [], "target_project": None}
        member, why = self._pick_overload(members, arguments)
        if member is None:
            return {**record, "status": UNRESOLVED, "code": "UNRESOLVED_AMBIGUOUS_CALL", "basis": why, "candidate_count": len(members),
                    "candidates": [f"{self._full(owner)}.{method}"] * len(members), "target_project": owner.get("project_path")}
        if basis is None:
            basis = "declared_type_member"                         # unique declaring type found by the base resolver's own rules
        status = CONFIRMED if basis in {"fully_qualified_symbol", "reference_and_namespace", "base_declaration", "declared_type_member"} else INFERRED
        return {**record, "status": status, "code": "RESOLVED" if status == CONFIRMED else "INFERRED_PROJECT_REFERENCE", "basis": f"{basis}+{why}",
                "candidate_count": len(candidates), "candidates": [f"{self._full(c)}.{method}" for c in candidates],
                **self._target(owner, method)}

    def _implementers(self, interface: dict) -> list[dict]:
        name = interface["name"].lower()
        full = self._full(interface).lower()
        out = []
        seen = set()
        for items in self.types.values():
            for symbol in items:
                if id(symbol) in seen:
                    continue
                seen.add(id(symbol))
                if any(str(i).lower().split("(")[0] in {name, full} or str(i).lower().rsplit(".", 1)[-1] == name for i in symbol.get("implements", [])):
                    out.append(symbol)
        return out

    def _external(self, call: dict, receiver_type: str, call_project: str | None, record: dict) -> dict | None:
        """EXTERNAL_ASSEMBLY_BOUNDARY: the type is not declared in analyzed source and a referenced assembly/project that is not
        analyzed is the only candidate owner (qualified-name prefix or imported namespace equals a referenced assembly name)."""
        if call_project is None:
            return None
        lowered = receiver_type.lower()
        head = lowered.split(".")[0]
        imported = self.imports.get(_posix((call.get("evidence") or {}).get("file")).lower(), set())
        names = self.assembly_names.get(call_project, set()) - {"system", "microsoft.visualbasic"}
        if "." in lowered:
            owners = sorted(n for n in names if head == n or lowered.startswith(n + "."))
        else:
            owners = sorted(n for n in names if any(i == n or i.startswith(n + ".") for i in imported))
        absent = [m for m in self.missing_refs.get(call_project, []) if str(m.get("name") or "").lower() == head]
        if not owners and not absent:
            return None
        return {**record, "status": UNRESOLVED, "code": "EXTERNAL_ASSEMBLY_BOUNDARY", "basis": "referenced_assembly_not_analyzed",
                "candidate_count": 0, "candidates": [], "target_project": None,
                "external": {"assemblies": owners, "absent_project_references": absent, "known_symbol": f"{receiver_type}.{call.get('method_name')}"}}
