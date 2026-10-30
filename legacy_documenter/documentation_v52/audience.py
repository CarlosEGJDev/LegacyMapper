"""H2 audience enrichment: abstraction-level facts for the executive / functional / technical-overview profiles.

Pure projection over the already transformed `AudienceDocumentModel`: it adds values and slots, never changes or
removes existing ones, reads no source code and calls no provider. Every added fact carries an explicit epistemic
status (`CONFIRMED`, `INFERRED`, `UNRESOLVED`, `AI_INTERPRETATION`, `CANONICAL`):

* counts and containment read from persisted Evidence -> `CONFIRMED`;
* the architectural *layer* of a project is a structural rule over that Evidence -> `INFERRED` (or `UNRESOLVED` when no
  rule applies); it is never a business conclusion;
* a functional "area" is a real Solution (`.sln` membership); business grouping is not deducible (existing GAP) and is
  not invented;
* unapproved AI proposals -> `AI_INTERPRETATION`; human-approved canonical knowledge -> `CANONICAL`. Precedence:
  deterministic Evidence > canonical knowledge > AI interpretation. An AI proposal is never rendered as confirmed.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .categories import KEEP_SIMPLE, KEEP_TECHNICAL, AudienceDocumentModel, Item

CONFIRMED, INFERRED, UNRESOLVED = "CONFIRMED", "INFERRED", "UNRESOLVED"
AI_INTERPRETATION, CANONICAL = "AI_INTERPRETATION", "CANONICAL"
LAYERS = ("presentation", "logic", "data_access", "unclassified")
STATEMENT_LIMIT = 400
TOP_PROCESSES = 12

# H2-R2: conservative, presentation-only classification of the *technical operation name* an interaction ends in.
# It reads only the name tokens (never business intent) and is deterministic: a token matches a stem when it equals
# it or, for stems of 4+ letters, starts with it. Anything not matched stays "unknown"; several different kinds
# (or a known kind plus an unknown target) are reported as "mixed", never collapsed.
ACTIONS = ("read", "create", "update", "delete", "mixed", "unknown")
_READ = ("TRAER", "TRAE", "LEE", "LEER", "BUSCA", "BUSCAR", "CONSULT", "SELECT", "GET", "CARGA", "LISTA", "OBTEN", "SEL", "CON")
_CREATE = ("GRABA", "GRABAR", "INSERT", "INS", "CREA", "CREAR", "REGISTRA", "AGREGA", "ALTA")
_UPDATE = ("UPDATE", "UPD", "MODIF", "MOD", "ACTUALIZ")
_DELETE = ("DELETE", "DEL", "ELIMIN", "BORRA", "QUITA")
_STEMS = {"read": _READ, "create": _CREATE, "update": _UPDATE, "delete": _DELETE}
_EXACT_ONLY = {"CON", "SEL", "INS", "UPD", "DEL", "MOD", "GET", "ALTA"}


def _tokens(name: str) -> list[str]:
    out, current = [], ""
    for ch in str(name).upper():
        if ch.isalnum():
            current += ch
        elif current:
            out.append(current)
            current = ""
    if current:
        out.append(current)
    return out


def _matches(token: str, stem: str) -> bool:
    if token == stem:
        return True
    return stem not in _EXACT_ONLY and len(stem) >= 4 and token.startswith(stem)


def classify_target(name: str) -> str:
    """Category of ONE technical operation name: `read|create|update|delete|mixed|unknown`."""
    # Only the operation name counts, not the package/schema before the last dot (e.g. PPRE_CONSULTAS.ACTUALIZAR_X is an update).
    operation = str(name).rsplit(".", 1)[-1]
    kinds = {kind for token in _tokens(operation) for kind, stems in _STEMS.items() if any(_matches(token, st) for st in stems)}
    if not kinds:
        return "unknown"
    return kinds.pop() if len(kinds) == 1 else "mixed"


def classify_action(terminal: str) -> str:
    """Category of an interaction whose terminal is a (possibly comma-separated) list of technical operation names."""
    targets = [t.strip() for t in str(terminal).split(",") if t.strip()]
    if not targets:
        return "unknown"
    kinds = {classify_target(t) for t in targets}
    known = kinds - {"unknown"}
    if not known:
        return "unknown"
    if len(known) == 1 and "unknown" not in kinds and "mixed" not in known:
        return next(iter(known))
    return "mixed"


def classify_layer(values: dict, has_references: bool) -> tuple[str, str, str]:
    """(layer, rule, epistemic status). Structural rules only, evaluated in order; no name/prefix heuristics."""
    if values["screens"] > 0 or values["project_type"]:
        return "presentation", "owns_screens", INFERRED
    if values["data_ops"] > 0:
        return "data_access", "direct_data_access", INFERRED
    if values["incoming_flows"] > 0 or has_references:
        return "logic", "receives_flows_or_referenced", INFERRED
    return "unclassified", "no_rule_applies", UNRESOLVED


def _short(value: object, limit: int = STATEMENT_LIMIT) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def enrich_for_audiences(
    model: AudienceDocumentModel, source: dict, knowledge: dict | None = None, deep_reference: bool = False,
) -> None:
    """Adds the H2 values/slots to `model` in place. Idempotent for a given model."""
    real_modules = [m for m in model.modules if m.values["path"]]
    refs_by_path = {m.values["path"]: bool(m.slots.get("project_refs_out") or m.slots.get("project_refs_in")) for m in real_modules}
    layer_counts: Counter = Counter()
    for module in model.modules:
        if module.values["path"]:
            layer, rule, status = classify_layer(module.values, refs_by_path[module.values["path"]])
        else:  # elements with no identifiable project: never given a layer
            layer, rule, status = "unclassified", "no_project", UNRESOLVED
        module.values.update(
            layer=layer, layer_rule=rule, layer_status=status,
            refs_out=len(module.slots.get("project_refs_out", [])), refs_in=len(module.slots.get("project_refs_in", [])),
            deep_path=f"documentation_v52/developer/modules/{module.slug}.md" if deep_reference and module.values["path"] else "",
        )
        if module.values["path"]:
            layer_counts[layer] += 1

    module_by_path = {m.values["path"]: m for m in real_modules}
    area_rows: list[dict] = []
    for solution in model.solutions:
        members = [module_by_path[i.values["path"]] for i in solution.slots.get("projects", []) if i.values["path"] in module_by_path]
        totals = {
            "screens": sum(m.values["screens"] for m in members), "real_flows": sum(m.values["real_flows"] for m in members),
            "data_ops": sum(m.values["data_ops"] for m in members), "unresolved_total": sum(m.values["unresolved_total"] for m in members),
        }
        layers = Counter(m.values["layer"] for m in members)
        solution.values.update(totals, **{f"layer_{name}": layers.get(name, 0) for name in LAYERS})
        ranked = sorted(members, key=lambda m: (-(m.values["real_flows"] + m.values["screens"] + m.values["data_ops"]), m.values["name"].lower()))
        solution.slots["module_rows"] = [
            Item({k: m.values[k] for k in ("name", "slug", "layer", "layer_status", "screens", "real_flows", "data_ops", "unresolved_total")},
                 KEEP_SIMPLE, level=2) for m in ranked
        ]
        processes = [
            Item({"project": m.values["name"], "webform": f.values["webform"], "event": f.values["event"], "terminal": f.values["terminal"],
                  "action": classify_action(f.values["terminal"]), "status": CONFIRMED}, KEEP_SIMPLE, level=2)
            for m in ranked for f in m.slots.get("flows", []) if f.values["state"] == "real"
        ]
        solution.slots["processes"] = processes
        for action in ACTIONS:
            solution.slots[f"interactions_{action}"] = [i for i in processes if i.values["action"] == action]
        solution.slots["action_summary"] = _action_summary(processes)
        solution.slots["screens_active"] = _screens_active(processes)
        solution.values["interactions"] = len(processes)
        targets: Counter = Counter()
        kinds: dict = {}
        for m in members:
            for t in m.slots.get("data_targets", []):
                if t.noise_category is None:
                    key = (t.values["target"], t.values["kind"])
                    targets[key] += t.values["count"]
        solution.slots["data_top"] = [Item({"target": t, "kind": k, "count": n}, KEEP_SIMPLE, level=2)
                                      for (t, k), n in sorted(targets.items(), key=lambda kv: (-kv[1], kv[0][0].lower()))]
        if members:
            area_rows.append({"name": solution.values["name"], "slug": solution.slug, "projects": len(members), **totals})

    model.slots["areas"] = [
        Item(r, KEEP_SIMPLE, level=2)
        for r in sorted(area_rows, key=lambda r: (-r["real_flows"], -r["screens"], -r["projects"], r["name"].lower()))
    ]
    model.slots["layer_summary"] = [
        Item({"layer": name, "projects": layer_counts.get(name, 0),
              "screens": sum(m.values["screens"] for m in real_modules if m.values["layer"] == name),
              "real_flows": sum(m.values["real_flows"] for m in real_modules if m.values["layer"] == name),
              "data_ops": sum(m.values["data_ops"] for m in real_modules if m.values["layer"] == name),
              "status": UNRESOLVED if name == "unclassified" else INFERRED}, KEEP_SIMPLE, level=2)
        for name in LAYERS if layer_counts.get(name, 0)
    ]
    ranked_all = sorted(real_modules, key=lambda m: (m.values["layer"], -(m.values["real_flows"] + m.values["screens"] + m.values["data_ops"]), m.values["name"].lower()))
    fields = ("name", "slug", "solutions", "layer", "layer_status", "screens", "real_flows", "data_ops", "refs_out", "refs_in", "unresolved_total")
    model.slots["projects_layers"] = [Item({k: m.values[k] for k in fields}, KEEP_TECHNICAL, level=3) for m in ranked_all]
    model.slots["screens_by_project"] = [
        Item({k: m.values[k] for k in ("name", "slug", "screens", "real_flows")}, KEEP_SIMPLE, level=2)
        for m in sorted((m for m in real_modules if m.values["screens"]), key=lambda m: (-m.values["screens"], m.values["name"].lower()))
    ]
    processes_all = [
        Item({"project": m.values["name"], "webform": f.values["webform"], "event": f.values["event"], "terminal": f.values["terminal"],
              "action": classify_action(f.values["terminal"]), "status": CONFIRMED}, KEEP_SIMPLE, level=2)
        # every module, including the bucket of screens the analysis could not assign to a project (declared, not hidden)
        for m in sorted(model.modules, key=lambda m: m.values["name"].lower())
        for f in m.slots.get("flows", []) if f.values["state"] == "real"
    ]
    model.slots["processes_all"] = processes_all
    model.slots["action_summary"] = _action_summary(processes_all)
    model.slots["screens_active"] = _screens_active(processes_all)[:30]
    by_project: Counter = Counter()
    kinds_by_project: dict = {}
    for item in processes_all:
        by_project[item.values["project"]] += 1
        kinds_by_project.setdefault(item.values["project"], set()).add(item.values["action"])
    model.slots["interactions_by_project"] = [
        Item({"project": name, "interactions": n, "kinds": len(kinds_by_project[name])}, KEEP_SIMPLE, level=2)
        for name, n in sorted(by_project.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    ]
    model.slots["areas_unresolved"] = [
        Item({"name": r["name"], "slug": r["slug"], "unresolved_total": r["unresolved_total"], "projects": r["projects"]}, KEEP_SIMPLE, level=2)
        for r in sorted((r for r in area_rows if r["unresolved_total"]), key=lambda r: (-r["unresolved_total"], r["name"].lower()))
    ]
    targets_all: Counter = Counter()
    users: dict = {}
    for m in real_modules:
        for t in m.slots.get("data_targets", []):
            if t.noise_category is None:
                key = (t.values["target"], t.values["kind"])
                targets_all[key] += t.values["count"]
                users.setdefault(key, set()).add(m.slug)
    model.slots["data_top"] = [
        Item({"target": t, "kind": k, "count": n, "projects": len(users[(t, k)])}, KEEP_SIMPLE, level=2)
        for (t, k), n in sorted(targets_all.items(), key=lambda kv: (-kv[1], kv[0][0].lower()))
    ]
    connections = [x for x in source.get("external_dependencies", []) if x.get("dependency_kind") == "database_connection"]
    model.slots["integrations"] = [
        Item({"name": _short((x.get("extensions") or {}).get(((x.get("adapter") or {}).get("id")), {}).get("name") or x.get("name") or "conexión", 120),
              "kind": "database_connection", "status": CONFIRMED}, KEEP_SIMPLE, level=2)
        for x in connections
    ]
    unresolved_targets: Counter = Counter()
    for m in model.modules:
        for u in m.slots.get("unresolved", []):
            unresolved_targets[u.values["target"]] += u.values["count"]
    model.slots["unresolved_top"] = [
        Item({"target": t, "count": n, "status": UNRESOLVED}, KEEP_SIMPLE, level=2)
        for t, n in sorted(unresolved_targets.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    ]
    model.slots["unresolved_by_project"] = [
        Item({"name": m.values["name"], "slug": m.slug, "unresolved_total": m.values["unresolved_total"],
              "unresolved_flows": m.values["unresolved_flows"], "status": UNRESOLVED}, KEEP_SIMPLE, level=2)
        for m in sorted(model.modules, key=lambda m: (-m.values["unresolved_total"], m.values["name"].lower())) if m.values["unresolved_total"]
    ]

    ai_items, canonical_items = _knowledge_items(knowledge)
    model.slots["ai_interpretations"] = ai_items
    model.slots["canonical_knowledge"] = canonical_items
    model.system.update(
        areas=len(area_rows), layer_presentation=layer_counts.get("presentation", 0), layer_logic=layer_counts.get("logic", 0),
        layer_data_access=layer_counts.get("data_access", 0), layer_unclassified=layer_counts.get("unclassified", 0),
        ai_proposals=len(ai_items), canonical_records=len(canonical_items), integrations=len(connections),
        unresolved_distinct=len(unresolved_targets), unresolved_projects=len(model.slots["unresolved_by_project"]),
        processes_listed=len(processes_all), deep_reference=bool(deep_reference),
        interactions=len(processes_all), interaction_screens=len({(i.values["webform"]) for i in processes_all}),
        interaction_projects=len(by_project), unresolved_share=round(100 * model.system["unresolved_flows"] / model.system["flows"], 1) if model.system["flows"] else 0,
    )


def _action_summary(interactions: list[Item]) -> list[Item]:
    """One row per non-empty action category (empty categories are omitted)."""
    rows = []
    for action in ACTIONS:
        group = [i for i in interactions if i.values["action"] == action]
        if group:
            rows.append(Item({"action": action, "interactions": len(group), "screens": len({i.values["webform"] for i in group}),
                              "projects": len({i.values["project"] for i in group}), "status": CONFIRMED}, KEEP_SIMPLE, level=2))
    return rows


def _screens_active(interactions: list[Item]) -> list[Item]:
    """Screens ranked by observed interactions (screen name, project, count and number of distinct action categories)."""
    counts: Counter = Counter()
    meta: dict = {}
    for i in interactions:
        key = (i.values["webform"], i.values["project"])
        counts[key] += 1
        meta.setdefault(key, set()).add(i.values["action"])
    return [
        Item({"webform": w, "project": proj, "interactions": n, "kinds": len(meta[(w, proj)])}, KEEP_SIMPLE, level=2)
        for (w, proj), n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0].lower(), kv[0][1].lower()))
    ]


def _knowledge_items(knowledge: dict | None) -> tuple[list[Item], list[Item]]:
    if not knowledge:
        return [], []
    ai = [
        Item({"statement": _short(p.get("statement")), "confidence": _short(p.get("confidence"), 20), "evidence_count": int(p.get("evidence_count", 0)),
              "origin": _short(p.get("origin"), 120), "status": AI_INTERPRETATION}, KEEP_SIMPLE, level=2)
        for p in knowledge.get("proposals", [])
    ]
    canonical = [
        Item({"statement": _short(c.get("statement")), "reviewer": _short(c.get("reviewer"), 120), "evidence_count": int(c.get("evidence_count", 0)),
              "status": CANONICAL}, KEEP_SIMPLE, level=2)
        for c in knowledge.get("canonical", [])
    ]
    return ai, canonical


def _read_json_files(directory: Path) -> list[dict]:
    out = []
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else ():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            out.append(data)
    return out


def load_knowledge_overlay(ai_run_dir: str | Path) -> dict:
    """Reads an AI run directory (H1 `interpret` output or any run dir with `proposals/` and `knowledge/`).

    Returns `{"proposals": [...], "canonical": [...]}`. READ-ONLY and file-level: the persisted JSON of the
    V5.7 proposals/decisions/canonical artifacts is parsed directly, so documentation never imports the review
    service (the mutating review layer stays reachable only from the explicit human `review` command) and no
    provider is ever resolved or called. A proposal that was canonicalized is listed only as canonical; a
    rejected one is not listed as an interpretation.
    """
    run_dir = Path(ai_run_dir)
    envelope: dict = {}
    proposals: list = []
    proposals_file = run_dir / "proposals" / "AI_PROPOSALS.json"
    if proposals_file.is_file():
        try:
            envelope = json.loads(proposals_file.read_text(encoding="utf-8"))
            proposals = envelope.get("proposals") or []
        except (OSError, ValueError, AttributeError):
            envelope, proposals = {}, []
    origin = " / ".join(str(envelope.get(k)) for k in ("provider_id", "model_id") if envelope.get(k)) or "IA (origen no registrado)"
    decisions = _read_json_files(run_dir / "knowledge" / "decisions")
    records = [r for r in _read_json_files(run_dir / "knowledge" / "canonical") if r.get("status", "ACTIVE") == "ACTIVE"]
    canonical_proposals = {r.get("source_proposal_id") for r in records}
    rejected = {d.get("proposal_id") for d in decisions if d.get("action") == "REJECT"}
    reviewers = {d.get("decision_id"): d.get("reviewer", "") for d in decisions}
    pending = [
        {"statement": p.get("statement"), "confidence": (p.get("rationale") or "").replace("AI-proposed interpretation (confidence: ", "").rstrip(").").strip(),
         "evidence_count": len(p.get("evidence_refs") or []), "origin": origin}
        for p in proposals if isinstance(p, dict) and p.get("proposal_id") not in canonical_proposals and p.get("proposal_id") not in rejected
    ]
    canonical = [
        {"statement": (r.get("content") or {}).get("statement", ""), "reviewer": reviewers.get(r.get("decision_id"), ""),
         "evidence_count": len(r.get("evidence_refs") or [])}
        for r in records
    ]
    return {"proposals": pending, "canonical": canonical}
