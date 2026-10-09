"""Scope analysis (V5.3-R2.7): which inputs changed and which projects they can affect.

It *informs*; it never reduces correctness. R1 section 6.C/section 10: the resolvers are global and always recomputed,
`changed` is the incremental mode that still produces the complete output, and no stage is skipped from this result.
Rules are conservative -- when in doubt the scope is widened, never narrowed:

- no previous valid cache (cold / fallback_full): `mode = full` with the cache's reason;
- a changed analyzed file that no project lists (`Compile`/`Content`) or a changed `.sln`: `mode = full` (the unknown
  is named);
- a `.vbproj` change affects its whole project; any project impacted pulls its transitive dependents (reverse
  `Project -> Project` edges that resolve to a known project);
- files no extractor reads (`ANALYZED_FILE_TYPES` is guarded to equal the extractor map) cannot alter extraction or
  resolution: they are `INVENTORY_ONLY` (they still alter file inventories/evidence artifacts), plus their project when
  one lists them;
- a changed code file (`.vb`, `.aspx`, `.ascx`, `.master`), `.vbproj` or `.sln` can change *global* name resolution
  (R1 section 6.C: a rename crossed 3 projects; measured at R2.7: a `RootNamespace` change touched 5 projects while
  only 2 are reachable through project references). Its effects cannot be bounded by project dependencies, so such a
  change is `mode = full` and carries `GLOBAL_RESOLUTION_EFFECTS_NOT_BOUNDED`; `impacted_projects`/`transitive_projects`
  remain reported as the *known floor*, never as a bound;
- only `partial_candidate` scopes are bounded: no changes, a `web.config` listed by a project, or files no
  extractor reads (inventory only).

Output holds paths, counts and reasons only -- never source content, symbol payloads or secrets.
"""
from __future__ import annotations

import posixpath
from dataclasses import dataclass, field

from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES

from .diff import FileStateDiff

MODE_FULL = "full"
MODE_PARTIAL = "partial_candidate"
#: Lists in the persisted form are capped so a branch switch cannot bloat the metrics; counts are always exact.
LIST_LIMIT = 200
CODE_TYPES = frozenset({"vb_source", "aspx", "ascx", "master", "python_source"})
GLOBAL_RESOLUTION = "GLOBAL_RESOLUTION_EFFECTS_NOT_BOUNDED"
#: Change kinds whose effect on name resolution is global and therefore unbounded by project dependencies.
GLOBAL_TRIGGER_TYPES = CODE_TYPES | {"vb_project", "solution"}


@dataclass
class ScopeAnalysisResult:
    """Deterministic result (every list sorted). `unknowns` and any global-resolution trigger force `mode = full`."""

    mode: str
    changed_files: dict[str, list[str]] = field(default_factory=dict)
    impacted_projects: list[str] = field(default_factory=list)
    transitive_projects: list[str] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    fallback_reason: str | None = None
    unknowns: list[str] = field(default_factory=list)
    unassertable: list[str] = field(default_factory=list)
    inventory_only: list[str] = field(default_factory=list)
    external_project_references: int = 0
    symbols_in_changed_files: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """The persisted shape: exact counts plus lists capped at `LIST_LIMIT`."""
        def capped(items):
            return {"count": len(items), "items": list(items[:LIST_LIMIT]), "truncated": len(items) > LIST_LIMIT}
        return {
            "mode": self.mode,
            "fallback_reason": self.fallback_reason,
            "changed_files": {kind: capped(files) for kind, files in sorted(self.changed_files.items())},
            "impacted_projects": capped(self.impacted_projects),
            "transitive_projects": capped(self.transitive_projects),
            "inventory_only_files": capped(self.inventory_only),
            "external_project_references": self.external_project_references,
            "reasons": dict(sorted(self.reasons.items())),
            "unknowns": list(self.unknowns),
            "unassertable": list(self.unassertable),
            "reach": "global_resolution" if self.unassertable else "bounded",
            "symbols_in_changed_files": {
                "total": sum(self.symbols_in_changed_files.values()),
                "files": dict(sorted(self.symbols_in_changed_files.items())[:LIST_LIMIT]),
            },
        }


def _norm(path: str) -> str:
    return posixpath.normpath(str(path).replace("\\", "/"))


def _key(path: str) -> str:
    return _norm(path).lower()


def _project_membership(projects: list[dict]) -> dict[str, list[str]]:
    """`normalized lower path -> [project paths]` from each project's `Compile` and `Content` items."""
    members: dict[str, list[str]] = {}
    for project in projects:
        project_path = _norm(project["path"])
        directory = posixpath.dirname(project_path)
        for item in [*project.get("compile_items", []), *project.get("content_items", [])]:
            target = _key(posixpath.join(directory, str(item).replace("\\", "/")))
            if project_path not in members.setdefault(target, []):
                members[target].append(project_path)
    return members


def _reverse_project_edges(projects: list[dict], dependencies: list[dict]) -> tuple[dict[str, set[str]], int]:
    """`referenced project -> {projects that reference it}` from `Project -> Project` dependencies, and how many
    references match no project of the repository (external targets).

    A reference resolves by its path relative to the referencing project; if that does not hit a known project (old
    solutions write includes relative to the solution root), every known project with the same file name is taken --
    a deliberate *widening* (it can only add dependents, never remove one). Only a reference matching nothing at all
    is external: its target is not a project of this repository, so it can never be in the impacted set."""
    known = {_key(project["path"]): _norm(project["path"]) for project in projects}
    by_name: dict[str, list[str]] = {}
    for key, path in known.items():
        by_name.setdefault(posixpath.basename(key), []).append(path)
    dependents: dict[str, set[str]] = {}
    external = 0
    for dep in dependencies:
        if dep.get("dependency_type") != "Project -> Project":
            continue
        source = _norm(dep["source"])
        include = str(dep["target"]).replace("\\", "/")
        exact = known.get(_key(posixpath.join(posixpath.dirname(source), include)))
        targets = [exact] if exact else by_name.get(posixpath.basename(_key(include)), [])
        if not targets:
            external += 1
        for target in targets:
            dependents.setdefault(target, set()).add(source)
    return dependents, external


def analyze_scope(
    diff: FileStateDiff | None, fallback_reason: str | None, file_types: dict[str, str], projects: list[dict] | None,
    dependencies: list[dict] | None, symbols: list[dict] | None,
) -> ScopeAnalysisResult:
    """Scope of the changes in `diff` (`None` = no usable previous cache). Pure and deterministic."""
    if diff is None or projects is None:
        return ScopeAnalysisResult(
            mode=MODE_FULL, fallback_reason=fallback_reason or "NO_PREVIOUS_STATE", reasons={"NO_PREVIOUS_STATE": 1},
        )
    changed = {"modified": sorted(set(diff.modified)), "added": sorted(set(diff.added)), "deleted": sorted(set(diff.deleted))}
    changed = {kind: files for kind, files in changed.items() if files}
    all_changed = sorted({path for files in changed.values() for path in files})
    result = ScopeAnalysisResult(mode=MODE_PARTIAL, changed_files=changed)
    if not all_changed:
        result.reasons["NO_CHANGES"] = 1
        return result
    members = _project_membership(projects)
    project_paths = {_key(project["path"]): _norm(project["path"]) for project in projects}
    impacted: set[str] = set()
    unknowns: set[str] = set()
    reasons: dict[str, int] = {}

    def note(reason: str) -> None:
        reasons[reason] = reasons.get(reason, 0) + 1

    for path in all_changed:
        kind = file_types.get(path, "unknown")
        mapped = members.get(_key(path), [])
        if kind == "solution":
            note("SOLUTION_FILE")
            unknowns.add("SOLUTION_CHANGED")
            result.unassertable = [GLOBAL_RESOLUTION]
        elif kind == "vb_project":
            note("PROJECT_FILE")
            impacted.add(project_paths.get(_key(path), _norm(path)))
            result.unassertable = [GLOBAL_RESOLUTION]
        elif kind in ANALYZED_FILE_TYPES:
            if mapped:
                note("WEB_CONFIG_IN_PROJECT" if kind == "web_config" else "SOURCE_IN_PROJECT")
                impacted.update(mapped)
            else:
                note("UNMAPPED_WEB_CONFIG" if kind == "web_config" else "UNMAPPED_ANALYZED_FILE")
                unknowns.add("UNMAPPED_ANALYZED_FILE")
            if kind in CODE_TYPES:
                result.unassertable = [GLOBAL_RESOLUTION]
        elif kind == "unknown":
            note("UNKNOWN_FILE_TYPE")
            unknowns.add("UNKNOWN_FILE_TYPE")
        else:
            note("INVENTORY_ONLY")
            result.inventory_only.append(path)
            impacted.update(mapped)
    dependents, result.external_project_references = _reverse_project_edges(projects, dependencies or [])
    transitive: set[str] = set()
    frontier = list(impacted)
    while frontier:
        for dependent in dependents.get(frontier.pop(), ()):
            if dependent not in impacted and dependent not in transitive:
                transitive.add(dependent)
                frontier.append(dependent)
    wanted = {_key(path) for path in all_changed}
    for symbol in symbols or []:
        if _key(symbol.get("file", "")) in wanted:
            name = _norm(symbol["file"])
            result.symbols_in_changed_files[name] = result.symbols_in_changed_files.get(name, 0) + 1
    result.impacted_projects, result.transitive_projects = sorted(impacted), sorted(transitive)
    result.inventory_only.sort()
    result.reasons, result.unknowns = dict(sorted(reasons.items())), sorted(unknowns)
    if unknowns or result.unassertable:  # unbounded or unknown effects: never a partial candidate
        result.mode = MODE_FULL
    return result
