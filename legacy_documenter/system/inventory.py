"""Complete project/solution inventory read ONLY from the persisted Evidence partitions of a baseline.

No source file is ever opened: every read is a JSON partition under `<baseline>/evidence/`. Integrity is checked against
`EVIDENCE_MANIFEST.json` while reading (hash mode) so a modified baseline is refused before any provider work.
"""
from __future__ import annotations

import hashlib
import json
import posixpath
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_EVIDENCE_SCHEMA = "1.0"
REQUIRED = ("solutions", "projects", "functional_flows", "data_access")
OPTIONAL = ("cross_project_calls", "ui_documents")
MANIFEST_NAME = "EVIDENCE_MANIFEST.json"


class SystemBaselineInvalid(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason, self.detail = reason, detail


def norm_key(path: str | None) -> str:
    return (path or "").replace("\\", "/").lower()


def _slug(text: str) -> str:
    return (re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item")[:48]


@dataclass
class Project:
    id: str
    name: str
    path: str                       # forward-slash, original case (logical, machine independent)
    key: str                        # lower-case join key
    namespace: str = ""
    output_type: str = ""
    reference_names: list = field(default_factory=list)
    solution_ids: list = field(default_factory=list)
    display: str = ""
    slug: str = ""

    @property
    def identity(self) -> str:
        return f"{self.id}|{self.path}"


@dataclass
class Solution:
    id: str
    name: str
    path: str
    project_ids: list
    display: str = ""
    slug: str = ""


@dataclass
class BaselineIdentity:
    manifest_sha256: str
    evidence_schema_version: str
    portable_evidence_sha256: str | None
    logical_snapshot_sha256: str | None
    verified: str
    partitions_read: dict

    def as_dict(self) -> dict:
        return {"evidence_manifest_sha256": self.manifest_sha256, "evidence_schema_version": self.evidence_schema_version,
                "portable_evidence_sha256": self.portable_evidence_sha256, "logical_snapshot_sha256": self.logical_snapshot_sha256,
                "verification": self.verified, "partitions_read": dict(sorted(self.partitions_read.items()))}


@dataclass
class Inventory:
    baseline: Path
    identity: BaselineIdentity
    solutions: list
    projects: dict
    by_key: dict
    flows_owned: dict                # project id -> [flow summary]
    data_by_project: dict            # project id -> [data access summary]
    callers: dict                    # project id -> {other project id: [call summary]}
    callees: dict
    unresolved_out: dict             # project id -> count of unresolved outgoing calls
    ui_paths: set
    solution_pairs: dict = field(default_factory=dict)

    def ordered_projects(self) -> list:
        return sorted(self.projects.values(), key=lambda p: (p.name.lower(), p.path.lower(), p.id))


def _read_partition(root: Path, name: str, manifest_hashes: dict, verify: str, required: bool):
    path = root / "evidence" / f"{name}.json"
    if name not in manifest_hashes or not path.is_file():
        if required:
            raise SystemBaselineInvalid("EVIDENCE_PARTITION_MISSING", name)
        return [], None
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if verify == "hash" and digest != manifest_hashes[name]:
        raise SystemBaselineInvalid("EVIDENCE_PARTITION_CORRUPT", name)
    try:
        value = json.loads(raw.decode("utf-8"))
    except ValueError:
        raise SystemBaselineInvalid("EVIDENCE_PARTITION_CORRUPT", name) from None
    if not isinstance(value, list):
        raise SystemBaselineInvalid("EVIDENCE_PARTITION_CORRUPT", f"{name}:not a list")
    return value, digest


def _dao_label(d: dict) -> str:
    if d.get("stored_procedure"):
        return f"procedimiento {d['stored_procedure']}"
    if d.get("sql_operation"):
        return f"SQL {d['sql_operation']}"
    return {"transaction": "control de transacción"}.get(d.get("operation_kind"), str(d.get("operation_kind") or "acceso a datos"))


def load_inventory(baseline: str | Path, verify: str = "hash") -> Inventory:
    root = Path(baseline)
    if not root.is_dir():
        raise SystemBaselineInvalid("BASELINE_NOT_FOUND", "not a directory")
    manifest_path = root / "evidence" / MANIFEST_NAME
    if not manifest_path.is_file():
        raise SystemBaselineInvalid("EVIDENCE_MANIFEST_MISSING", MANIFEST_NAME)
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except ValueError:
        raise SystemBaselineInvalid("EVIDENCE_MANIFEST_INVALID", "json") from None
    hashes = manifest.get("partition_sha256") if isinstance(manifest, dict) else None
    if not isinstance(hashes, dict) or not hashes:
        raise SystemBaselineInvalid("EVIDENCE_MANIFEST_INVALID", "partition_sha256")
    schema = str(manifest.get("evidence_schema_version"))
    if schema != SUPPORTED_EVIDENCE_SCHEMA:
        raise SystemBaselineInvalid("EVIDENCE_SCHEMA_UNSUPPORTED", f"{schema}!={SUPPORTED_EVIDENCE_SCHEMA}")

    read: dict[str, str] = {}
    data: dict[str, list] = {}
    for name in REQUIRED + OPTIONAL:
        value, digest = _read_partition(root, name, hashes, verify, name in REQUIRED)
        data[name] = value
        if digest:
            read[name] = digest

    provenance = manifest.get("source_provenance") or {}
    identity = BaselineIdentity(hashlib.sha256(manifest_bytes).hexdigest(), schema, provenance.get("portable_evidence_sha256"),
                                provenance.get("logical_snapshot_sha256"), verify, read)

    projects: dict[str, Project] = {}
    for rec in data["projects"]:
        ext = (rec.get("extensions") or {}).get(((rec.get("adapter") or {}).get("id")), {}) or {}
        path = (rec.get("path") or "").replace("\\", "/")
        projects[rec["id"]] = Project(
            id=rec["id"], name=rec.get("name") or posixpath.basename(path), path=path, key=norm_key(path),
            namespace=ext.get("root_namespace") or "", output_type=ext.get("output_type") or "",
            reference_names=sorted({r.get("name") for r in (ext.get("project_references") or []) if r.get("name")}))
    by_key = {p.key: p.id for p in projects.values()}

    solutions: list[Solution] = []
    for rec in data["solutions"]:
        pids = set(r for r in rec.get("project_refs", []) if r in projects)
        # A solution lists its projects relative to its own directory while projects are recorded relative to the analyzed root:
        # resolve the listed path against the solution directory (exact normalized match), as the behavior explainer does.
        sol_path = (rec.get("path") or "").replace("\\", "/")
        base = posixpath.dirname(sol_path)
        listed = ((rec.get("extensions") or {}).get(((rec.get("adapter") or {}).get("id")), {}) or {}).get("projects") or []
        for item in listed:
            raw = item.get("path") if isinstance(item, dict) else item
            if raw:
                key = norm_key(posixpath.normpath(posixpath.join(base, str(raw).replace("\\", "/"))))
                if key in by_key:
                    pids.add(by_key[key])
        pids = sorted(pids)
        solutions.append(Solution(rec["id"], rec.get("name") or rec["id"], (rec.get("path") or "").replace("\\", "/"), pids))
        for pid in pids:
            projects[pid].solution_ids.append(rec["id"])
    solutions.sort(key=lambda s: (s.name.lower(), s.path.lower(), s.id))
    for p in projects.values():
        p.solution_ids = sorted(set(p.solution_ids))

    # Distinguishable labels / unique slugs (duplicate names must stay apart).
    for items, label in ((list(projects.values()), "project"), (solutions, "solution")):
        counts: dict[str, int] = defaultdict(int)
        for it in items:
            counts[it.name.lower()] += 1
        used: set[str] = set()
        ordinal: dict[str, int] = defaultdict(int)
        for it in sorted(items, key=lambda x: (x.name.lower(), x.path.lower(), x.id)):
            ordinal[it.name.lower()] += 1
            # Duplicates stay distinguishable without exposing a source path in human text (the path lives in ai/).
            it.display = it.name if counts[it.name.lower()] == 1 else f"{it.name} (variante {ordinal[it.name.lower()]})"
            slug = _slug(it.name)
            if slug in used or counts[it.name.lower()] > 1:
                slug = f"{slug}-{hashlib.sha256(it.id.encode()).hexdigest()[:6]}"
            used.add(slug)
            it.slug = slug

    daos = {d["id"]: d for d in data["data_access"] if d.get("id")}
    flows_owned: dict[str, list] = defaultdict(list)
    for f in data["functional_flows"]:
        seq = [by_key.get(norm_key(x)) for x in (f.get("project_sequence") or [])]
        seq = [x for x in seq if x]
        owner = seq[0] if seq else None
        if not owner:
            continue
        webform = (f.get("webform") or "").replace("\\", "/")
        terminals = []
        for t in f.get("terminal_operations") or []:
            terminals.append(_dao_label(daos[t]) if t in daos else str(t))
        flows_owned[owner].append({
            "id": f.get("id"), "webform": webform, "view": posixpath.splitext(posixpath.basename(webform))[0] or webform,
            "event": f.get("event") or "", "handler": f.get("handler") or "", "start": f.get("start_method") or "",
            "terminals": sorted(set(terminals)), "depth": f.get("depth") or 0, "projects": seq,
            "certainty": ("confirmed" if f.get("has_confirmed_terminal") and not f.get("has_unresolved_boundary")
                          else "inferred" if f.get("has_confirmed_terminal") else "unresolved")})

    data_by_project: dict[str, list] = defaultdict(list)
    for d in data["data_access"]:
        pid = by_key.get(norm_key(d.get("project")))
        if pid:
            data_by_project[pid].append({"id": d.get("id"), "kind": d.get("operation_kind") or "", "sp": d.get("stored_procedure") or "",
                                         "sql": d.get("sql_operation") or "", "class": d.get("class") or "", "method": d.get("method") or "",
                                         "dynamic": bool(d.get("dynamic_sql")), "certainty": d.get("confidence") or "confirmed"})

    callers: dict[str, dict] = defaultdict(lambda: defaultdict(list))
    callees: dict[str, dict] = defaultdict(lambda: defaultdict(list))
    unresolved_out: dict[str, int] = defaultdict(int)
    pair_counts: dict[tuple, dict] = {}
    for x in data["cross_project_calls"]:
        src, tgt = by_key.get(norm_key(x.get("source_project"))), by_key.get(norm_key(x.get("target_project")))
        status = (x.get("status") or "").upper()
        if src and (not tgt or status == "UNRESOLVED"):
            unresolved_out[src] += 1
        if src and tgt and src != tgt and status in ("CONFIRMED", "INFERRED"):
            call = {"id": x.get("id"), "from": x.get("source_symbol") or "", "to": x.get("target_symbol") or "", "status": status}
            callees[src][tgt].append(call)
            callers[tgt][src].append(call)
            rec = pair_counts.setdefault((src, tgt), {"confirmed": 0, "inferred": 0, "samples": []})
            rec[status.lower()] += 1
            if len(rec["samples"]) < 3 and call["from"] and call["to"]:
                rec["samples"].append((call["from"], call["to"]))

    ui_paths = {norm_key(u.get("logical_source_path")) for u in data["ui_documents"]}
    return Inventory(root, identity, solutions, projects, by_key, dict(flows_owned), dict(data_by_project),
                     {k: dict(v) for k, v in callers.items()}, {k: dict(v) for k, v in callees.items()}, dict(unresolved_out),
                     ui_paths, pair_counts)
