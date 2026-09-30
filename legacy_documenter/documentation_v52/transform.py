"""Audience Transformation (R1 section 13): evidence -> `AudienceDocumentModel`.

Pure and deterministic: aggregates, summarizes, classifies (presentation category
and technical-noise category), orders and prepares navigation keys. It renders
no Markdown, decides no format, calls no AI and mutates nothing it reads.

Input is a plain mapping of evidence partitions (`EvidenceSource`, the same
shapes `evidence/` persists as passthrough partitions and `index/` exposes):
`repository, solutions, projects, entry_points, functional_flows, flow_unresolved,
data_access, stored_procedures, sql_operations, dependencies, configuration,
flow_summary, webforms, external_dependencies`. Missing partitions are treated
as empty (honest "nothing observed"), never invented.

"Module" == `Project` (GAP-M1: it is the only deterministic grouping the
evidence supports); `Solution` is shown as membership.

Ownership vs participation (V5.2 R3.1): a project *owns* the entry points whose
evidence names it as their project, the data access it declares and the
dependencies it declares. A flow that merely arrives at a project is recorded
there as an *incoming* flow with its origin; it never turns the origin's screens
into screens of the destination. A flow reaches *real* data only through an
operation the noise policy counts as data access (transaction control does not).
"""
from __future__ import annotations

import ntpath
import re
from collections import Counter, defaultdict

from legacy_documenter.exporters._documentation_partitioning import sanitize_label
from legacy_documenter.utils.sanitizer import sanitize_text

from .categories import (
    DETAIL_ON_DEMAND, KEEP_SIMPLE, KEEP_TECHNICAL, AudienceDocumentModel, ComponentModel, FileModel, Item,
    MethodModel, ModuleModel, SolutionModel,
)
from .noise import NoisePolicy, bare_name

MAX_SLUG = 48
TOP_MODULES = 30
TOP_LIBRARIES = 40
TOP_PACKAGES = 40
_WS = re.compile(r"\s+")
UNASSIGNED = ""
NO_NAME = "(sin nombre identificado)"
# V5.2 R3.4.1 section 4: an unresolved call whose original expression is
# also unavailable in the evidence must say so honestly, never fall back to
# a generic "(no resuelto)" placeholder that hides whether an expression
# existed at all.
NO_EXPRESSION = "(expresión no disponible)"
CALL_EXPRESSION_MAX_CHARS = 160
# Class-like Symbol kinds (V5.2 R3.3): the extractor's `Symbol.kind` values that
# denote a Component in Evidence Core terms (never a `.vb` file itself).
SYMBOL_COMPONENT_KINDS = {"class", "interface", "module", "structure", "enum"}


def _s(value: object) -> str:
    """Sanitized text (credentials/connection strings masked) -- every evidence
    string passes through here before it can reach a document."""
    return sanitize_text(str(value)) if value is not None else ""


def _origin(evidence: object) -> str:
    """`file:line` of the first evidence entry, or empty."""
    if isinstance(evidence, list) and evidence and isinstance(evidence[0], dict):
        first = evidence[0]
        if first.get("file"):
            line = first.get("line")
            return f"{_s(first['file'])}:{line}" if line else _s(first["file"])
    return ""


def _base_library_name(include: str) -> str:
    """Assembly name without the version/culture/token suffix."""
    return _s(include).split(",", 1)[0].strip()


def _resolve_solution_projects(solution: dict) -> list[str]:
    """Project paths a solution contains, resolved against the solution's own
    directory (deterministic path arithmetic, no heuristics)."""
    base = ntpath.dirname(solution.get("path", ""))
    resolved = []
    for project in solution.get("projects", []) or []:
        path = project.get("path")
        if path:
            resolved.append(ntpath.normpath(ntpath.join(base, path)) if base else ntpath.normpath(path))
    return resolved


def _activity(module: ModuleModel) -> int:
    return -(module.values["flows"] + module.values["incoming_flows"] + module.values["data_ops"])


def _norm_path(path: str) -> str:
    """Case/slash-insensitive comparison key (mirrors
    `legacy_documenter.cli.pipeline_stages._norm_path`, duplicated here rather
    than imported to keep Audience Transformation free of a `cli` dependency)."""
    return str(path or "").replace("\\", "/").strip("./").lower()


def _owner_index(projects: dict, item_key: str) -> dict[str, list[str]]:
    """normalized file path -> project paths declaring it under `item_key`
    (`compile_items`/`content_items`), resolved with the same deterministic
    path arithmetic as `apply_project_namespaces` (project directory + item).
    Real structural evidence only -- never a name/folder guess (round R3.3
    section 6)."""
    index: dict[str, list[str]] = defaultdict(list)
    for path, project in projects.items():
        base = ntpath.dirname(path)
        for item in project.get(item_key) or []:
            joined = ntpath.normpath(ntpath.join(base, item)) if base else ntpath.normpath(item)
            index[_norm_path(joined)].append(path)
    return index


def _resolve_owner(file_path: str, pre_resolved: str | None, projects: dict, index: dict[str, list[str]]) -> tuple[str, list[str]]:
    """(owner project path or `UNASSIGNED`, ambiguous-candidate project paths).

    `pre_resolved` is trusted only when it names a real project (the live
    pipeline already resolves it the same way, unambiguously, via
    `apply_project_namespaces`). Otherwise: exactly one structural match ->
    that project; zero matches -> no evidence (`UNASSIGNED`, no candidates);
    more than one match -> ambiguous, declared explicitly via the returned
    candidate list, never guessed."""
    if pre_resolved and pre_resolved in projects:
        return pre_resolved, []
    candidates = index.get(_norm_path(file_path), [])
    if len(candidates) == 1:
        return candidates[0], []
    return UNASSIGNED, sorted(set(candidates))


class AudienceTransformer:
    """Builds the neutral model. `noise_policy` classifies technical noise;
    `unassigned_label` names the module for elements with no project and
    `unknown_origin_label` names an origin the evidence does not identify."""

    def __init__(self, noise_policy: NoisePolicy, unassigned_label: str = "(sin proyecto asignado)",
                 unknown_origin_label: str = "(origen no identificado)",
                 shared_ownership_label: str = "(pertenencia compartida o ambigua)") -> None:
        self._noise = noise_policy
        self._unassigned_label = unassigned_label
        self._unknown_origin_label = unknown_origin_label
        # V5.2 R3.4 section 9: a file that structurally matches *several* real
        # projects (e.g. `img\aceptar.gif`) is genuinely ambiguous evidence --
        # distinct from a file with *zero* matching projects. Both routed to
        # the same unassigned bucket for directory purposes (R3.3), but the
        # ambiguous case must never read as if "sin proyecto asignado" were a
        # real project it belongs to.
        self._shared_ownership_label = shared_ownership_label

    def transform(self, source: dict) -> AudienceDocumentModel:
        projects = {p["path"]: p for p in source.get("projects", []) if p.get("path")}
        flows = source.get("functional_flows", [])
        data_access = source.get("data_access", [])
        accumulators: dict[str, dict] = {}
        display = self._display_names(projects)

        ep_owner = {
            ep.get("id"): (ep.get("project") if ep.get("project") in projects else UNASSIGNED)
            for ep in source.get("entry_points", [])
        }
        flow_origin = {f["id"]: ep_owner.get(f.get("entry_point_id"), UNASSIGNED) for f in flows}
        data_index = self._data_index(data_access)
        self._collect_entry_points(source.get("entry_points", []), ep_owner, accumulators)
        self._collect_flows(flows, flow_origin, projects, display, data_index, accumulators)
        self._collect_unresolved(source.get("flow_unresolved", []), flow_origin, accumulators)
        self._collect_data_access(data_access, projects, accumulators)
        edges, system_libs = self._collect_dependencies(source.get("dependencies", []), projects, accumulators)
        membership, solution_links = self._membership(source.get("solutions", []), projects)

        module_models = self._module_models(projects, accumulators, membership, display)
        module_by_path = {m.values["path"]: m for m in module_models}
        solution_models = self._solution_models(source.get("solutions", []), projects, display, module_by_path)
        calls_out_index, calls_in_index = self._build_calls_indexes(source.get("calls", []))
        data_access_by_method = self._build_data_access_by_method(data_access)
        file_models, component_models, method_models = self._build_files_and_components(
            source.get("symbols", []), source.get("webform_components", []), projects, module_models, module_by_path, display,
            calls_out_index, calls_in_index, data_access_by_method,
        )
        configs = self._configs(source.get("configuration", []))
        system = self._system_values(source, projects, module_models, configs, edges, solution_links)
        slots = self._global_slots(source, projects, module_models, system_libs, configs, solution_models)
        gaps = [
            "gap.no_business_purpose", "gap.no_module_grouping", "gap.no_external_services",
            # V5.2 R3.4 section 4/5/13: relations B (Method -> dependency) and D
            # (Method -> unresolved boundary) are not attributable at method
            # granularity with today's persisted evidence (dependencies only
            # carry Project-level source/target; flow_unresolved records as
            # consumed here carry no method field) -- declared as GAP rather
            # than guessed from project/component-level data.
            "gap.method_dependencies_not_available", "gap.method_unresolved_not_attributable",
            # No canonical per-signature method identity exists in V5.1 evidence
            # (GAP-M2): two same-named members of one component cannot be told
            # apart, so relations for that name are never attributed to a
            # single one of them.
            "gap.method_identity_no_signatures",
        ]
        if len(configs) > 1:
            gaps.append("gap.config_ambiguity")
        if any(m.values["path"] == UNASSIGNED for m in module_models):
            gaps.append("gap.flows_without_project")
        if slots["unclassified_libraries"]:
            gaps.append("gap.third_party_unclassified")
        if any(m.values["copy_marker"] for m in module_models):
            gaps.append("gap.project_copies")
        if any(f.values["ownership_note"] for f in file_models):
            gaps.append("gap.file_ownership_ambiguous")
        if any(c.slots.get("ambiguous_methods") for c in component_models):
            gaps.append("gap.method_overloads_ambiguous")
        return AudienceDocumentModel(
            system=system, slots=slots, modules=module_models, solutions=solution_models,
            files=file_models, components=component_models, methods=method_models, gaps=gaps,
        )

    # ------------------------------------------------------------------ evidence collection
    @staticmethod
    def _accumulator(accumulators: dict, key: str) -> dict:
        entry = accumulators.get(key)
        if entry is None:
            entry = accumulators[key] = {
                "webforms": defaultdict(lambda: {"events": 0, "real": 0}),
                "events": [], "flows": [], "data_targets": {}, "data_ops": [], "unres": {}, "unres_flows": set(),
                "refs_out": [], "refs_in": [], "libs": Counter(), "incoming": [], "indirect": Counter(),
                "real_flows": 0, "tx_flows": 0, "source_files": 0,
            }
        return entry

    @staticmethod
    def _display_names(projects: dict) -> dict[str, str]:
        """Visible project name. Projects sharing a name (typically `Backup`/copy
        folders) show their path so they can be told apart; the file-name suffix
        used to keep slugs unique never becomes part of the visible name."""
        counts = Counter(_s(p.get("name")).lower() for p in projects.values())
        return {
            path: (_s(p.get("name")) if counts[_s(p.get("name")).lower()] == 1 else f"{_s(p.get('name'))} ({_s(path)})")
            for path, p in projects.items()
        }

    @staticmethod
    def _data_index(data_access: list) -> dict:
        """DAO id -> label / kind / project, and target label -> projects declaring it."""
        index = {"label": {}, "kind": {}, "project": {}, "target_projects": defaultdict(set)}
        for op in data_access:
            kind = _s(op.get("operation_kind"))
            target = _s(op.get("stored_procedure") or op.get("sql_operation") or "")
            index["label"][op.get("id")] = target or NO_NAME
            index["kind"][op.get("id")] = kind
            index["project"][op.get("id")] = op.get("project")
            if target and op.get("project"):
                index["target_projects"][target].add(op["project"])
        return index

    @staticmethod
    def _build_calls_indexes(calls: list) -> tuple[dict, dict]:
        """(outgoing, incoming) built from the `calls` evidence partition
        (V5.2 R3.4, relation A: Method -> call; V5.2 R3.4.1 section 4: the
        original call expression is carried through instead of being
        collapsed into a generic marker).

        Outgoing key: `(normalized file of the calling code, caller class name
        lower, caller method name lower)` -> `[(resolved target or '', confidence,
        origin, expression)]`. This is exactly `CallIdentity.containing_symbol`
        (builder.py) re-keyed by file so a same-named class in a different file
        never collides. `resolved target` is the resolver's own
        `resolved_target` string (e.g. `"Class.Method"`) when it could resolve
        one, else empty -- the caller decides how to present an unresolved call
        (V5.2 R3.4.1: using the original `expression` when it exists, honestly
        declaring its absence otherwise; never guessed here).

        Incoming key: `"class.method"` lower -> `[(caller label, origin)]`,
        populated only when the resolver reports `confidence == "confirmed"`
        (i.e. it matched exactly one method by that name in that class --
        `call_resolver._resolve_method`; a homonym/overload never reaches
        "confirmed" there, so this index can never mix two callees of the
        same name)."""
        outgoing: dict[tuple, list] = defaultdict(list)
        incoming: dict[str, list] = defaultdict(list)
        for file_entry in calls or []:
            file_path = file_entry.get("file")
            norm_file = _norm_path(file_path)
            for call in file_entry.get("calls") or []:
                caller_class = call.get("containing_class")
                caller_method = call.get("containing_method")
                if not caller_class or not caller_method:
                    continue
                evidence = call.get("evidence") or {}
                line = evidence.get("line")
                origin = f"{_s(file_path)}:{line}" if line else _s(file_path)
                raw_target = _s(call.get("resolved_target") or "")
                confidence = _s(call.get("confidence")) or "unresolved"
                expression = _s(_WS.sub(" ", str(call.get("expression") or "")).strip())
                key = (norm_file, _s(caller_class).lower(), _s(caller_method).lower())
                outgoing[key].append((raw_target, confidence, origin, expression))
                if raw_target and confidence == "confirmed" and "." in raw_target:
                    caller_label = f"{_s(caller_class)}.{_s(caller_method)}"
                    incoming[raw_target.lower()].append((caller_label, origin))
        return dict(outgoing), dict(incoming)

    @staticmethod
    def _build_data_access_by_method(data_access: list) -> dict:
        """`(project path, class name lower, method name lower) -> [(kind,
        target, confidence, origin)]` (V5.2 R3.4, relation C). Every
        `data_access` record already carries `class`/`method` (unlike
        `dependencies`, which never does, GAP-M-B) -- this only re-keys the
        same records `_collect_data_access` aggregates by project, it never
        infers a class/method the record does not itself declare."""
        index: dict[tuple, list] = defaultdict(list)
        for op in data_access or []:
            cls, method = op.get("class"), op.get("method")
            if not cls or not method:
                continue
            kind = _s(op.get("operation_kind"))
            target = _s(op.get("stored_procedure") or op.get("sql_operation") or "") or NO_NAME
            confidence = _s(op.get("confidence")) or "confirmed"
            origin = _origin(op.get("evidence"))
            key = (op.get("project"), _s(cls).lower(), _s(method).lower())
            index[key].append((kind, target, confidence, origin))
        return dict(index)

    @staticmethod
    def _collect_entry_points(entry_points: list, ep_owner: dict, accumulators: dict) -> None:
        for ep in entry_points:
            entry = AudienceTransformer._accumulator(accumulators, ep_owner.get(ep.get("id"), UNASSIGNED))
            webform = _s(ep.get("webform"))
            entry["webforms"][webform]["events"] += 1
            entry["events"].append((webform, _s(ep.get("event")), _s(ep.get("handler")), _s(ep.get("type"))))

    def _terminals(self, flow: dict, index: dict) -> tuple[list, bool]:
        """(real targets [((label, kind), owner projects)], reaches_only_infrastructure).

        A terminal the policy says does not count as data access (transaction
        control) is not a real target. Owner projects are the projects that declare
        that operation; empty when the evidence does not say."""
        real: dict[tuple, set] = {}
        infrastructure = False
        for terminal in flow.get("terminal_operations", []):
            if not isinstance(terminal, str):
                continue
            if terminal in index["label"]:
                label, kind = index["label"][terminal], index["kind"][terminal]
                owners = {index["project"][terminal]} if index["project"].get(terminal) else set()
                category = self._noise.classify(name=label, kind=kind)
            else:
                label, kind = _s(terminal), "stored_procedure"
                owners = set(index["target_projects"].get(label, ()))
                category = self._noise.classify(name=label)
            if self._noise.counts_as_data_access(category):
                real.setdefault((label, kind), set()).update(owners)
            else:
                infrastructure = True
        return sorted(real.items(), key=lambda kv: (kv[0][0].lower(), kv[0][1])), infrastructure and not real

    def _collect_flows(self, flows: list, flow_origin: dict, projects: dict, display: dict, index: dict, accumulators: dict) -> None:
        for flow in flows:
            origin = flow_origin[flow["id"]]
            entry = self._accumulator(accumulators, origin)
            real, tx_only = self._terminals(flow, index)
            if real:
                state = "real"
            elif tx_only:
                state = "transaction"
            else:
                state = "unresolved" if flow.get("has_unresolved_boundary") else "dead_end"
            webform, event, handler = _s(flow.get("webform")), _s(flow.get("event")), _s(flow.get("handler"))
            entry["flows"].append((state, webform, event, handler, ", ".join(label for (label, _kind), _owners in real)))
            if state == "real":
                entry["real_flows"] += 1
                entry["webforms"][webform]["real"] += 1
                if origin != UNASSIGNED:
                    for (label, kind), owners in real:
                        if origin not in owners:
                            entry["indirect"][(label, kind)] += 1
            elif state == "transaction":
                entry["tx_flows"] += 1
            origin_label = display.get(origin) or self._unknown_origin_label
            for path in dict.fromkeys(flow.get("project_sequence") or []):
                if path in projects and path != origin:
                    self._accumulator(accumulators, path)["incoming"].append((origin_label, webform, event, handler, state))

    def _collect_unresolved(self, records: list, flow_origin: dict, accumulators: dict) -> None:
        """Aggregated per (module, label): never listed one record at a time."""
        for record in records:
            entry = self._accumulator(accumulators, flow_origin.get(record.get("flow_id"), UNASSIGNED))
            label = _s(_WS.sub(" ", str(record.get("terminal_target") or "")).strip()) or "(sin etiqueta)"
            entry["unres"][label] = entry["unres"].get(label, 0) + 1
            entry["unres_flows"].add(record.get("flow_id"))

    def _collect_data_access(self, data_access: list, projects: dict, accumulators: dict) -> None:
        for op in data_access:
            entry = self._accumulator(accumulators, op.get("project") if op.get("project") in projects else UNASSIGNED)
            kind = _s(op.get("operation_kind"))
            target = _s(op.get("stored_procedure") or op.get("sql_operation") or "") or NO_NAME
            confidence = _s(op.get("confidence"))
            origin = _origin(op.get("evidence"))
            where = f"{_s(op.get('class'))}.{_s(op.get('method'))}".strip(".")
            entry["data_ops"].append((where, kind, target, confidence, origin))
            agg = entry["data_targets"].setdefault((target, kind), {"count": 0, "origin": origin, "confidence": "confirmed"})
            agg["count"] += 1
            if confidence != "confirmed":
                agg["confidence"] = confidence or "unresolved"

    def _library_class(self, name: str, internal_names: set) -> str:
        """`internal` (an assembly built by a project of the same repository), a class the
        noise policy declares (e.g. `platform`) or `unclassified` (the evidence cannot tell more)."""
        if name.lower() in internal_names:
            return "internal"
        return self._noise.dependency_class(self._noise.classify(name=name)) or "unclassified"

    @staticmethod
    def _collect_dependencies(dependencies: list, projects: dict, accumulators: dict) -> tuple[int, dict]:
        system_libs: dict[str, set] = defaultdict(set)
        edges = 0
        for dep in dependencies:
            kind = dep.get("dependency_type")
            if kind == "Project -> Project" and dep.get("source") in projects and dep.get("target") in projects:
                AudienceTransformer._accumulator(accumulators, dep["source"])["refs_out"].append(dep["target"])
                AudienceTransformer._accumulator(accumulators, dep["target"])["refs_in"].append(dep["source"])
                edges += 1
            elif kind == "Project -> DLL" and dep.get("source") in projects:
                name = _base_library_name(dep.get("target", ""))
                if name:
                    AudienceTransformer._accumulator(accumulators, dep["source"])["libs"][name] += 1
                    system_libs[name].add(dep["source"])
            elif kind == "Project -> SourceFile" and dep.get("source") in projects:
                AudienceTransformer._accumulator(accumulators, dep["source"])["source_files"] += 1
        return edges, system_libs

    @staticmethod
    def _membership(solutions: list, projects: dict) -> tuple[dict, int]:
        """project path -> sorted solution names (via path arithmetic) and the link count."""
        membership: dict[str, list[str]] = defaultdict(list)
        links = 0
        for solution in solutions:
            for project_path in _resolve_solution_projects(solution):
                if project_path in projects:
                    membership[project_path].append(_s(solution.get("name")))
                    links += 1
        for names in membership.values():
            names[:] = sorted(set(names))
        return membership, links

    # ------------------------------------------------------------------ model assembly
    def _module_models(self, projects: dict, accumulators: dict, membership: dict, display: dict) -> list[ModuleModel]:
        keys = sorted(set(projects) | set(accumulators), key=lambda k: (k == UNASSIGNED, k.lower(), k))
        internal_names = self._internal_names(projects)
        used: set[str] = set()
        models = []
        for key in keys:
            project = projects.get(key, {})
            name = display.get(key, "") if key else self._unassigned_label
            stem = ntpath.splitext(ntpath.basename(key))[0] if key else "unassigned"
            slug = self._unique_slug(sanitize_label(stem)[:MAX_SLUG], used)
            entry = self._accumulator(accumulators, key)
            models.append(self._build_module(key, slug, name, project, entry, membership.get(key, []), projects, internal_names, display))
        return models

    @staticmethod
    def _internal_names(projects: dict) -> set:
        names = set()
        for project in projects.values():
            for field_name in ("name", "assembly_name"):
                if project.get(field_name):
                    names.add(_s(project[field_name]).lower())
        return names

    @staticmethod
    def _unique_slug(base: str, used: set) -> str:
        """Deterministic, case-insensitively unique file stem (Windows/macOS file
        systems treat `Web` and `web` as the same file)."""
        slug, ordinal = base, 1
        while slug.lower() in used:
            ordinal += 1
            slug = f"{base}-{ordinal}"
        used.add(slug.lower())
        return slug

    def _build_module(self, key: str, slug: str, name: str, project: dict, entry: dict, solution_names: list,
                      projects: dict, internal_names: set, display: dict) -> ModuleModel:
        flow_items = self._flow_items(entry["flows"])
        target_items = self._target_items(entry["data_targets"])
        indirect_items = self._indirect_items(entry["indirect"])
        counts = self._noise.counts_as_data_access
        values = {
            "name": name, "path": _s(key), "slug": slug, "solutions": ", ".join(solution_names),
            "output_type": _s(project.get("output_type")) or "n/d",
            "project_type": self._project_type(project),
            "copy_marker": (self._noise.path_marker(key) or "") if key else "",
            "source_files": entry["source_files"],
            "screens": len(entry["webforms"]), "events": len(entry["events"]),
            "flows": len(flow_items), "real_flows": entry["real_flows"], "tx_flows": entry["tx_flows"],
            "incoming_flows": len(entry["incoming"]),
            "incoming_screens": len({(row[0], row[1]) for row in entry["incoming"]}),
            "data_ops": sum(i.values["count"] for i in target_items if counts(i.noise_category)),
            "infra_ops": sum(i.values["count"] for i in target_items if not counts(i.noise_category)),
            "indirect_targets": len(indirect_items),
            "unresolved_total": sum(entry["unres"].values()), "unresolved_flows": len(entry["unres_flows"]),
        }
        return ModuleModel(slug=slug, values=values, slots={
            "entry_points": self._entry_point_items(entry["webforms"]),
            "entry_point_events": self._event_items(entry["events"]),
            "flows": flow_items,
            "incoming_summary": self._incoming_summary(entry["incoming"]),
            "incoming_flows": self._incoming_items(entry["incoming"]),
            "data_targets": target_items,
            "indirect_targets": indirect_items,
            "data_operations": self._operation_items(entry["data_ops"]),
            "unresolved": self._unresolved_items(entry["unres"]),
            "project_refs_out": self._ref_items(entry["refs_out"], display),
            "project_refs_in": self._ref_items(entry["refs_in"], display),
            "libraries": [
                Item({"name": n, "path": "", "class": self._library_class(n, internal_names)}, KEEP_TECHNICAL, level=3,
                     noise_category=self._noise.classify(name=n))
                for n in sorted(entry["libs"], key=str.lower)
            ],
        })

    @staticmethod
    def _flow_items(raw_flows: list) -> list[Item]:
        order = {"real": 0, "transaction": 1, "unresolved": 2, "dead_end": 3}
        flows = sorted(raw_flows, key=lambda f: (order[f[0]], f[1].lower(), f[2].lower(), f[3].lower()))
        return [
            Item({"state": s, "webform": w, "event": e, "handler": h, "terminal": t},
                 KEEP_TECHNICAL if s == "real" else DETAIL_ON_DEMAND, level=3 if s == "real" else 4)
            for s, w, e, h, t in flows
        ]

    @staticmethod
    def _incoming_summary(incoming: list) -> list[Item]:
        counts = Counter((row[0], row[1]) for row in incoming)
        return [Item({"origin": o, "webform": w, "flows": n}, KEEP_TECHNICAL, level=3)
                for (o, w), n in sorted(counts.items(), key=lambda kv: (kv[0][0].lower(), -kv[1], kv[0][1].lower()))]

    @staticmethod
    def _incoming_items(incoming: list) -> list[Item]:
        rows = sorted(incoming, key=lambda r: tuple(x.lower() for x in r))
        return [Item({"origin": o, "webform": w, "event": e, "handler": h, "state": s}, DETAIL_ON_DEMAND, level=4)
                for o, w, e, h, s in rows]

    @staticmethod
    def _indirect_items(indirect: Counter) -> list[Item]:
        return [Item({"target": t, "kind": k, "flows": n}, KEEP_TECHNICAL, level=3)
                for (t, k), n in sorted(indirect.items(), key=lambda kv: (-kv[1], kv[0][0].lower(), kv[0][1]))]

    @staticmethod
    def _entry_point_items(webforms: dict) -> list[Item]:
        return [
            Item({"webform": w, "events": v["events"], "real_flows": v["real"]}, KEEP_TECHNICAL, level=3)
            for w, v in sorted(webforms.items(), key=lambda kv: (-kv[1]["real"], -kv[1]["events"], kv[0].lower()))
        ]

    @staticmethod
    def _event_items(events: list) -> list[Item]:
        return [
            Item({"webform": w, "event": e, "handler": h, "kind": k}, DETAIL_ON_DEMAND, level=4)
            for w, e, h, k in sorted(events, key=lambda r: tuple(x.lower() for x in r))
        ]

    def _target_items(self, data_targets: dict) -> list[Item]:
        ordered = sorted(data_targets.items(), key=lambda kv: (-kv[1]["count"], kv[0][0].lower(), kv[0][1]))
        return [
            Item({"target": target, "kind": kind, "count": agg["count"], "confidence": agg["confidence"], "origin": agg["origin"]},
                 KEEP_TECHNICAL, level=3, noise_category=self._noise.classify(name=target, kind=kind))
            for (target, kind), agg in ordered
        ]

    def _operation_items(self, operations: list) -> list[Item]:
        return [
            Item({"where": w, "kind": k, "target": t, "confidence": c, "origin": o}, DETAIL_ON_DEMAND, level=4,
                 noise_category=self._noise.classify(name=t, kind=k))
            for w, k, t, c, o in sorted(operations, key=lambda r: (r[4].lower(), r[0].lower(), r[2].lower()))
        ]

    def _unresolved_items(self, unresolved: dict) -> list[Item]:
        items = []
        for label, count in sorted(unresolved.items(), key=lambda kv: (-kv[1], kv[0].lower())):
            category = self._noise.classify(name=bare_name(label), label=label)
            items.append(Item({"target": label, "count": count, "category": category or ""},
                              KEEP_TECHNICAL, level=3, noise_category=category))
        return items

    @staticmethod
    def _ref_items(paths: list, display: dict) -> list[Item]:
        return [Item({"name": display[p], "path": _s(p)}, KEEP_TECHNICAL, level=3)
                for p in sorted(set(paths), key=str.lower)]

    @staticmethod
    def _project_type(project: dict) -> str:
        """Project type from structural evidence already present in the project
        file itself (`Content` items the .vbproj/.csproj declares -- never the
        project's name, prefix or folder). `.aspx`/`Global.asax` is strong,
        unambiguous evidence of a Web application; `.ascx` alone (no `.aspx`)
        is a Web user-control library with no pages of its own. Empty when the
        evidence is insufficient -- never guessed from `output_type` alone,
        which only reports the technical compiler output (Library/Exe/WinExe)."""
        items = [_s(item).lower() for item in (project.get("content_items") or [])]
        if any(item.endswith(".aspx") or item.endswith("global.asax") for item in items):
            return "Aplicación Web (ASP.NET Web Forms: el proyecto declara archivos .aspx o Global.asax)"
        if any(item.endswith(".ascx") for item in items):
            return "Biblioteca de controles de usuario Web (ASP.NET Web Forms: declara .ascx, sin páginas .aspx propias)"
        return ""

    @staticmethod
    def _system_values(source: dict, projects: dict, module_models: list, configs: list, edges: int, solution_links: int) -> dict:
        flows = source.get("functional_flows", [])
        flow_summary = source.get("flow_summary") or {}
        total_flows = flow_summary.get("total_flows", len(flows))
        unresolved = flow_summary.get("flows_with_unresolved_boundary", sum(1 for f in flows if f.get("has_unresolved_boundary")))
        real = sum(m.values["real_flows"] for m in module_models)
        repository = source.get("repository") or {}
        root = str(repository.get("root", "")).rstrip("\\/")
        return {
            "name": _s(ntpath.basename(root) or "sistema"),
            "solutions": len(source.get("solutions", [])), "projects": len(projects),
            "source_files": repository.get("stats", {}).get("vb_source", 0),
            "screens": len(source.get("webforms", [])) or len({e.get("webform") for e in source.get("entry_points", [])}),
            "flows": total_flows, "real_flows": real,
            "infra_flows": sum(m.values["tx_flows"] for m in module_models), "unresolved_flows": unresolved,
            "percent": round(100 * real / total_flows, 1) if total_flows else 0,
            "objects": len(source.get("stored_procedures", [])), "sql": len(source.get("sql_operations", [])),
            "edges": edges, "solution_links": solution_links, "configs": len(configs),
            "connections": sum(1 for x in source.get("external_dependencies", []) if x.get("dependency_kind") == "database_connection"),
            "data_ops": sum(m.values["data_ops"] for m in module_models),
            "unowned_flows": sum(m.values["flows"] for m in module_models if m.values["path"] == UNASSIGNED),
        }

    def _global_slots(self, source: dict, projects: dict, module_models: list, system_libs: dict, configs: list,
                       solution_models: list | None = None) -> dict:
        active = [m for m in module_models if m.values["path"] and (m.values["flows"] or m.values["incoming_flows"] or m.values["data_ops"])]
        top = sorted(active, key=lambda m: (_activity(m), m.values["name"].lower(), m.values["path"]))
        top_fields = ("name", "solutions", "screens", "flows", "incoming_flows", "data_ops")
        all_fields = (*top_fields, "real_flows", "unresolved_total")
        ordered = sorted(module_models, key=lambda m: (m.values["path"] == UNASSIGNED, _activity(m), m.values["name"].lower(), m.values["path"]))
        internal_names = self._internal_names(projects)
        classified = {name: self._library_class(name, internal_names) for name in system_libs}

        def libraries(wanted: str) -> list[Item]:
            return [
                Item({"name": name, "projects_using": len(users), "class": wanted}, KEEP_SIMPLE, level=2)
                for name, users in sorted(system_libs.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))
                if classified[name] == wanted
            ]

        providers = Counter(_s(op.get("provider")) for op in source.get("data_access", []) if op.get("provider"))
        return {
            "modules_top": [Item({k: m.values[k] for k in top_fields} | {"slug": m.slug}, KEEP_SIMPLE, level=2) for m in top[:TOP_MODULES]],
            "modules_all": [Item({k: m.values[k] for k in all_fields} | {"slug": m.slug}, KEEP_TECHNICAL, level=3) for m in ordered],
            "solutions_top": self._solution_items(source.get("solutions", []), projects),
            "internal_libraries": libraries("internal"),
            "unclassified_libraries": libraries("unclassified"),
            "platform_libraries": libraries("platform"),
            "data_providers": [Item({"name": n, "count": c}, KEEP_SIMPLE, level=2)
                               for n, c in sorted(providers.items(), key=lambda kv: (-kv[1], kv[0]))],
            "data_packages": self._data_packages(source),
            "configs": configs,
            "solutions_all": [
                Item({"name": m.values["name"], "path": m.values["path"], "projects": m.values["project_count"], "slug": m.slug},
                     KEEP_TECHNICAL, level=3)
                for m in sorted(solution_models or (), key=lambda m: (-m.values["project_count"], m.values["name"].lower()))
            ],
        }

    @staticmethod
    def _solution_items(solutions: list, projects: dict) -> list[Item]:
        rows = [(_s(s.get("name")), _s(s.get("path")), sum(1 for p in _resolve_solution_projects(s) if p in projects)) for s in solutions]
        return [Item({"name": n, "path": p, "projects": c}, KEEP_SIMPLE, level=2)
                for n, p, c in sorted(rows, key=lambda r: (-r[2], r[0].lower(), r[1].lower()))]

    # ------------------------------------------------------------------ R3.3: Solution -> Project navigation
    def _solution_models(self, solutions: list, projects: dict, display: dict, module_by_path: dict) -> list[SolutionModel]:
        """One document per real `.sln`. A project shared between solutions keeps
        its single module identity; this only links to it, never duplicates it."""
        used: set[str] = set()
        models: list[SolutionModel] = []
        for solution in sorted(solutions, key=lambda s: _s(s.get("name")).lower()):
            proj_paths = sorted({p for p in _resolve_solution_projects(solution) if p in projects}, key=lambda p: display[p].lower())
            stem = self._unique_slug(sanitize_label(_s(solution.get("name")) or "solucion")[:MAX_SLUG], used)
            items = [Item({"name": display[p], "path": _s(p), "slug": module_by_path[p].slug}, KEEP_TECHNICAL, level=2)
                     for p in proj_paths if p in module_by_path]
            values = {"name": _s(solution.get("name")), "path": _s(solution.get("path")), "slug": stem, "project_count": len(items)}
            model = SolutionModel(slug=stem, values=values, slots={"projects": items})
            models.append(model)
            for item in items:
                module = module_by_path.get(item.values["path"])
                if module is not None:
                    module.slots.setdefault("solution_links", []).append(
                        Item({"name": model.values["name"], "path": model.values["path"], "slug": model.slug}, KEEP_TECHNICAL, level=3))
        for module in module_by_path.values():
            module.slots.setdefault("solution_links", [])
        return models

    # ------------------------------------------------------------------ R3.3: Project -> Component/Archivo navigation
    def _build_files_and_components(self, symbols: list, webforms: list, projects: dict, module_models: list,
                                      module_by_path: dict, display: dict, calls_out_index: dict, calls_in_index: dict,
                                      data_access_by_method: dict,
                                      ) -> tuple[list[FileModel], list[ComponentModel], list[MethodModel]]:
        """`SourceArtifact` (file) and `Component` (class-like symbol or WebForm)
        documents, grouped strictly by real evidence (`compile_items`/
        `content_items`, never name/folder). A file with zero or several
        candidate owners is declared as such, never guessed."""
        compile_index = _owner_index(projects, "compile_items")
        content_index = _owner_index(projects, "content_items")
        grouped: dict[tuple, dict] = {}
        for symbol in symbols:
            if symbol.get("kind") not in SYMBOL_COMPONENT_KINDS:
                continue
            owner, candidates = _resolve_owner(symbol.get("file"), symbol.get("project_path"), projects, compile_index)
            key = (owner, _s(symbol.get("file")))
            grouped.setdefault(key, {"kind": "vb_source", "candidates": candidates, "items": []})["items"].append(("symbol", symbol))
        for form in webforms:
            owner, candidates = _resolve_owner(form.get("path"), None, projects, content_index)
            key = (owner, _s(form.get("path")))
            entry = grouped.setdefault(key, {"kind": _s(form.get("kind")) or "web", "candidates": candidates, "items": []})
            entry["kind"] = _s(form.get("kind")) or entry["kind"]
            entry["items"].append(("webform", form))

        # A project's own `compile_items`/`content_items` may declare a file for
        # which the extractor found no class-like symbol or WebForm (e.g.
        # `AssemblyInfo.vb`, which contains only assembly attributes). It is
        # still a real, declared SourceArtifact of the project -- it must still
        # get a file document (zero components), not silently disappear.
        seen_normalized = {_norm_path(path) for _owner, path in grouped}
        declared: dict[str, str] = {}
        for project_path, project in projects.items():
            base = ntpath.dirname(project_path)
            for item_key in ("compile_items", "content_items"):
                for item in project.get(item_key) or []:
                    joined = ntpath.normpath(ntpath.join(base, item)) if base else ntpath.normpath(item)
                    declared.setdefault(_norm_path(joined), joined)
        for normalized, display_path in sorted(declared.items()):
            if normalized in seen_normalized:
                continue
            owner, candidates = _resolve_owner(display_path, None, projects, compile_index)
            if owner == UNASSIGNED and not candidates:
                owner, candidates = _resolve_owner(display_path, None, projects, content_index)
            lowered = display_path.lower()
            kind = "vb_source" if lowered.endswith(".vb") or lowered.endswith(".cs") else (
                "aspx" if lowered.endswith(".aspx") else "ascx" if lowered.endswith(".ascx") else
                "master" if lowered.endswith(".master") else "web"
            )
            grouped[(owner, _s(display_path))] = {"kind": kind, "candidates": candidates, "items": []}

        file_models: list[FileModel] = []
        component_models: list[ComponentModel] = []
        method_models: list[MethodModel] = []
        used_file_slugs: dict[str, set] = defaultdict(set)
        unassigned_module = module_by_path.get(UNASSIGNED)
        for (owner, file_path), info in sorted(grouped.items(), key=lambda kv: (kv[0][0] != UNASSIGNED, kv[0][0].lower(), kv[0][1].lower())):
            module = module_by_path.get(owner) or unassigned_module
            module_slug = module.slug if module is not None else "unassigned"
            candidate_names = sorted({display.get(c, c) for c in info["candidates"]})
            # V5.2 R3.4 section 9: zero candidates (`owner == UNASSIGNED`, no
            # `candidate_names`) is genuinely "no project declares this file";
            # two-or-more candidates is a *different*, real fact -- several
            # projects DO declare it -- and must never read as if the file had
            # no project at all (e.g. `img\aceptar.gif`, matched by 5 projects).
            if candidate_names:
                module_name = self._shared_ownership_label
                ownership_note = (
                    f"Coincide estructuralmente con {len(candidate_names)} proyectos ({', '.join(candidate_names)}); "
                    "no se asigna la propiedad exclusiva a ninguno de ellos."
                )
            else:
                module_name = module.values["name"] if module is not None else self._unassigned_label
                ownership_note = ""
            stem = ntpath.splitext(ntpath.basename(file_path))[0] or "archivo"
            file_stem_slug = self._unique_slug(sanitize_label(stem)[:MAX_SLUG] or "archivo", used_file_slugs[module_slug])
            file_slug = f"{module_slug}/files/{file_stem_slug}"
            used_component_slugs: set = set()
            component_items: list[Item] = []
            for kind_tag, record in info["items"]:
                component_items.append(self._one_component(
                    kind_tag, record, file_path, file_slug, module_slug, module_name, used_component_slugs, component_models,
                    owner, calls_out_index, calls_in_index, data_access_by_method, method_models,
                ))
            file_values = {
                "name": _s(ntpath.basename(file_path)) or _s(file_path), "path": _s(file_path), "kind": info["kind"],
                "module_name": module_name, "module_slug": module_slug, "slug": file_slug,
                "component_count": len(component_items), "ownership_note": ownership_note,
            }
            file_models.append(FileModel(slug=file_slug, values=file_values, slots={"components": component_items}))
            if module is not None:
                module.slots.setdefault("files", []).append(Item(
                    {"name": file_values["name"], "path": file_values["path"], "kind": file_values["kind"],
                     "component_count": file_values["component_count"], "slug": file_slug}, KEEP_TECHNICAL, level=3))
        for module in module_models:
            module.slots.setdefault("files", [])
            module.slots["files"].sort(key=lambda i: i.values["path"].lower())
        return file_models, component_models, method_models

    def _one_component(self, kind_tag: str, record: dict, file_path: str, file_slug: str, module_slug: str, module_name: str,
                        used_component_slugs: set, component_models: list, owner: str, calls_out_index: dict,
                        calls_in_index: dict, data_access_by_method: dict, method_models: list) -> Item:
        """Builds one `ComponentModel` (appended to `component_models`) and
        returns the summary `Item` for its owning file's "components" slot.

        V5.2 R3.4: for a class-like component, also builds one `MethodModel`
        per member whose name is unique within this component (no overload/
        homonym ambiguity, section 5) AND that has at least one individually
        verifiable relation (a call it makes, a call resolved to it by name,
        or a data-access operation attributed to it) -- see section 7 of the
        round prompt: no document-per-method explosion when the evidence only
        gives name/kind/accessibility/shared, already shown in the index."""
        if kind_tag == "symbol":
            name = _s(record.get("name"))
            comp_kind = _s(record.get("kind"))
            members = record.get("members") or []
            method_items = [
                Item({"name": _s(member.get("name")), "kind": _s(member.get("kind")),
                      "accessibility": _s(member.get("accessibility")) or "n/d",
                      "shared": "Sí" if member.get("shared") else "No", "slug": ""}, KEEP_TECHNICAL, level=3)
                for member in members if isinstance(member, dict) and member.get("name")
            ]
            values = {
                "name": name, "kind": comp_kind, "module_name": module_name, "module_slug": module_slug,
                "file_name": _s(ntpath.basename(file_path)), "file_path": _s(file_path), "file_slug": file_slug,
                "accessibility": _s(record.get("accessibility")) or "n/d",
                "modifiers": ", ".join(_s(m) for m in (record.get("modifiers") or [])),
                "namespace": _s(record.get("effective_namespace") or record.get("namespace")),
                "inherits": ", ".join(_s(x) for x in (record.get("inherits") or [])),
                "implements": ", ".join(_s(x) for x in (record.get("implements") or [])),
                "confidence": _s(record.get("namespace_confidence")) or "unresolved",
                "member_count": len(method_items), "codebehind": "", "master_page": "",
            }
        else:
            # WebForm/UserControl/MasterPage: Evidence Core's own `name` for this
            # kind of Component is its full path (guaranteed unique there), but
            # the file of origin is already the surrounding context here -- the
            # visible name is just the file's own basename, consistent with how
            # a class-like component shows its bare class name.
            name = _s(ntpath.basename(record.get("path") or "")) or _s(record.get("path"))
            comp_kind = _s(record.get("kind")) or "web"
            method_items = []
            values = {
                "name": name, "kind": comp_kind, "module_name": module_name, "module_slug": module_slug,
                "file_name": _s(ntpath.basename(file_path)), "file_path": _s(file_path), "file_slug": file_slug,
                "accessibility": "", "modifiers": "", "namespace": "",
                "inherits": _s(record.get("inherits")), "implements": "", "confidence": "confirmed",
                "member_count": 0, "codebehind": _s(record.get("codebehind") or record.get("codefile")),
                "master_page": _s(record.get("master_page")),
            }
        comp_stem = sanitize_label(name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] or "componente")[:MAX_SLUG] or "componente"
        comp_slug_local = AudienceTransformer._unique_slug(comp_stem, used_component_slugs)
        comp_slug = f"{file_slug}/{comp_slug_local}"
        values["slug"] = comp_slug
        ambiguous_items: list[Item] = []
        if kind_tag == "symbol" and method_items:
            self._build_methods_for_component(
                name, comp_slug, module_name, module_slug, file_path, values["file_name"], file_slug, owner,
                method_items, ambiguous_items, calls_out_index, calls_in_index, data_access_by_method, method_models,
            )
        component_models.append(ComponentModel(
            slug=comp_slug, values=values, slots={"methods": method_items, "ambiguous_methods": ambiguous_items}))
        return Item({"name": name, "kind": comp_kind, "member_count": values["member_count"], "slug": comp_slug}, KEEP_TECHNICAL, level=3)

    def _classify_call(self, resolved_target: str, expression: str) -> tuple[str, str | None]:
        """(display text, noise category or `None`) for one outgoing call.

        A resolved call is never noise-classified: the resolver already
        confirmed it names a real method. An unresolved call is classified by
        its original expression (V5.2 R3.4.1 section 4/5), reusing the same
        declarative noise policy already applied to module-level unresolved
        points (`_unresolved_items`) so framework/UI/infrastructure noise does
        not resurface here just because the expression is now visible. A call
        with no expression at all is declared honestly, never silently
        dropped nor mislabeled as noise (there is nothing to classify)."""
        if resolved_target:
            return resolved_target, None
        if not expression:
            return NO_EXPRESSION, None
        display = expression
        if len(display) > CALL_EXPRESSION_MAX_CHARS:
            display = display[: CALL_EXPRESSION_MAX_CHARS - 1].rstrip() + "…"
        return display, self._noise.classify(name=bare_name(expression), label=expression)

    def _classify_data_access(self, kind: str, target: str) -> tuple[str | None, bool]:
        """(noise category, counts as real data access) for one data-access
        record, reusing the same policy `_terminals`/`_target_items` already
        apply at flow/module level (V5.2 R3.4.1 section 6): a record the
        policy marks as transaction control is never presented as if it were
        a real data operation."""
        category = self._noise.classify(name=target, kind=kind)
        return category, self._noise.counts_as_data_access(category)

    def _build_methods_for_component(self, comp_name: str, comp_slug: str, module_name: str, module_slug: str, file_path: str,
                                       file_name: str, file_slug: str, project_path: str, method_items: list,
                                       ambiguous_items: list, calls_out_index: dict, calls_in_index: dict,
                                       data_access_by_method: dict, method_models: list) -> None:
        """Mutates `method_items` in place (sets `values["slug"]` on the ones
        that get a detail document) and appends to `ambiguous_items`/
        `method_models`. Never attributes a relation to one specific overload
        when the component declares the same member name more than once --
        that grouping is shown as a named limitation instead (section 5/9 of
        R3.3/R3.4), never split arbitrarily between the homonyms.

        V5.2 R3.4.1 section 7: a method earns its own document only when it
        has at least one relation that adds real, individual information --
        a resolved outgoing call, a confirmed incoming call, an unresolved
        outgoing call whose original expression is visible and not already
        classified as technical noise, or a data-access operation the noise
        policy counts as real (never transaction control alone). A method
        whose only evidence is noise-classified calls, expression-less
        unresolved calls or transactional-only data access stays exactly as
        R3.3 already showed it: a row in the component's method table, with
        no document and no information lost (it is still visible there)."""
        name_counts = Counter(item.values["name"].lower() for item in method_items)
        norm_file = _norm_path(file_path)
        used_method_slugs: set = set()
        ambiguous_names_added: set = set()
        for item in method_items:
            method_name = item.values["name"]
            key_lower = method_name.lower()
            outgoing = calls_out_index.get((norm_file, comp_name.lower(), key_lower), [])
            incoming = calls_in_index.get(f"{comp_name.lower()}.{key_lower}", [])
            data_ops = data_access_by_method.get((project_path, comp_name.lower(), key_lower), [])

            resolved_calls, unresolved_calls = [], []
            qualifies = False
            for target, confidence, origin, expression in sorted(set(outgoing), key=lambda t: (t[0].lower(), t[2], t[3])):
                display, noise_category = self._classify_call(target, expression)
                if target:
                    resolved_calls.append((display, confidence, origin, None))
                    qualifies = True
                else:
                    unresolved_calls.append((display, confidence, origin, noise_category))
                    if noise_category is None and display != NO_EXPRESSION:
                        qualifies = True
            if incoming:
                qualifies = True

            real_data, tx_data = [], []
            for kind, target, confidence, origin in sorted(set(data_ops), key=lambda t: (t[1].lower(), t[3])):
                _category, is_real = self._classify_data_access(kind, target)
                (real_data if is_real else tx_data).append((kind, target, confidence, origin))
                if is_real:
                    qualifies = True

            if name_counts[key_lower] > 1:
                # Overload/homonym within this component (GAP-M2): the
                # evidence names the group ONCE (not once per repeated member),
                # never a single member of it.
                if qualifies and key_lower not in ambiguous_names_added:
                    ambiguous_names_added.add(key_lower)
                    ambiguous_items.append(Item(
                        {"name": method_name, "overload_count": name_counts[key_lower]}, KEEP_TECHNICAL, level=3))
                continue
            if not qualifies:
                continue  # index-only (section 7): nothing individual to add over name/kind/accessibility/shared
            method_stem = sanitize_label(method_name)[:MAX_SLUG] or "metodo"
            method_slug_local = AudienceTransformer._unique_slug(method_stem, used_method_slugs)
            method_slug = f"{comp_slug}/{method_slug_local}"
            item.values["slug"] = method_slug
            calls_out_resolved = [
                Item({"target": target, "confidence": confidence, "origin": origin}, KEEP_TECHNICAL, level=3)
                for target, confidence, origin, _noise in resolved_calls
            ]
            calls_out_unresolved = [
                Item({"target": target, "confidence": confidence, "origin": origin}, KEEP_TECHNICAL, level=3,
                     noise_category=noise_category)
                for target, confidence, origin, noise_category in unresolved_calls
            ]
            calls_in_items = [
                Item({"caller": caller, "origin": origin}, KEEP_TECHNICAL, level=3)
                for caller, origin in sorted(set(incoming), key=lambda t: (t[0].lower(), t[1]))
            ]
            data_items = [
                Item({"kind": kind, "target": target, "confidence": confidence, "origin": origin}, KEEP_TECHNICAL, level=3)
                for kind, target, confidence, origin in real_data
            ]
            data_tx_items = [
                Item({"kind": kind, "target": target, "confidence": confidence, "origin": origin}, KEEP_TECHNICAL, level=3)
                for kind, target, confidence, origin in tx_data
            ]
            method_values = {
                "name": method_name, "kind": item.values["kind"], "accessibility": item.values["accessibility"],
                "shared": item.values["shared"], "slug": method_slug, "component_name": comp_name,
                "component_slug": comp_slug, "file_name": file_name, "file_slug": file_slug,
                "module_name": module_name, "module_slug": module_slug,
                "calls_out_count": len(calls_out_resolved) + len(calls_out_unresolved),
                "calls_in_count": len(calls_in_items),
                "data_access_count": len(data_items) + len(data_tx_items),
            }
            method_models.append(MethodModel(slug=method_slug, values=method_values, slots={
                "calls_out_resolved": calls_out_resolved, "calls_out_unresolved": calls_out_unresolved,
                "calls_in": calls_in_items,
                "data_access": data_items, "data_access_transactional": data_tx_items,
            }))

    @staticmethod
    def _data_packages(source: dict) -> list[Item]:
        counts: Counter = Counter()
        for sp in source.get("stored_procedures", []):
            package = _s(sp.get("package")) or (_s(sp.get("name")).split(".", 1)[0] if "." in _s(sp.get("name")) else "")
            counts[package or "(sin paquete)"] += 1
        return [Item({"package": p, "objects": c}, KEEP_SIMPLE, level=2)
                for p, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))[:TOP_PACKAGES]]

    def _configs(self, configuration: list[dict]) -> list[Item]:
        items = []
        for record in sorted(configuration, key=lambda r: str(r.get("path", "")).lower()):
            path = _s(record.get("path"))
            items.append(Item({"path": path, "marker": self._noise.path_marker(path) or ""}, KEEP_TECHNICAL, level=3))
        return items
