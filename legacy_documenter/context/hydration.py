"""Deterministic evidence selection and hydration (V4.3-R2, extended V4.3-R3).

Implements the `AI_HYDRATED_PROJECTION` contract fixed by V4.3-R1
(`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`): a hydrated FLOW
record carries its entry point, event, handler, projects/layers, a prioritized and
deduplicated set of paths, resolved terminals (stored procedure / SQL / unresolved
boundary), the parameters available on the callers it actually reaches, its
confidence, its preserved (never dropped) significant unresolved boundaries, and a
provenance pointer back to the exhaustive index -- never a bare ID.

This module is a pure function of the `ix` indexes dict already produced by the
deterministic pipeline (the same shape `legacy_documenter.context.system_context_builder
.SystemContextBuilder` consumes). It never imports `legacy_documenter.llm`, never
calls a provider, never re-reads a file from disk, and never deletes or mutates any
upstream evidence -- it only composes new, additive, in-memory hydrated records.
Nothing here is wired into `legacy_documenter.cli`: producing a hydrated record is a
capability a caller opts into explicitly, not a step the existing pipeline runs
automatically (see `docs/V4_3/V4_3_R2_EVIDENCE_HYDRATION_AND_SELECTION_RESULT.md`
section on runtime independence).

V4.3-R3 (`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md`, acceptance case C of R0)
extended this module, additively and minimally, to surface two more fields already
present on `index/data_access.json` entries but not previously hydrated: the raw
SQL verb (`INSERT`/`UPDATE`/`DELETE`/`SELECT`/`MERGE`, R2's `sql_operation` field on
the operation record itself, distinct from the separate `sql_operations` catalog)
and transaction evidence (`BeginTrans`/`BeginTransaction`/`Commit`/`Rollback`,
`operation_kind == "transaction"`). Both are read verbatim from fields
`legacy_documenter.extractors.database_extractor.DatabaseExtractor` already writes
deterministically -- this extension never inspects a stored procedure's resolved
*name* to guess its nature (see `_transaction_verb`: it matches literal keywords
already present in the recorded evidence *expression* text, not names).

V4.3-R8 (external pilot finding P-01, `docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md`)
added one more field, additively, to the hydrated `entry_point`: `project`, read verbatim from
`entry_points.json`'s own `project` field (the `.vbproj` path `WebEntryResolver` already resolves
structurally from the WebForm's code-behind symbol -- never a name-based heuristic over the WebForm
path itself). This exists so a documentation-scale caller can group flows by their real owning
project instead of the WebForm path's first folder segment, which collapses into a generic container
folder (e.g. `proyectos`) for a deeply nested repository layout. See
`legacy_documenter.exporters._documentation_partitioning.owning_project_group_key`.

A second, smaller V4.3-R3 correction (human review of the generated samples,
`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md` section 11) added `path_provenance`
to each hydrated path group: when `select_and_deduplicate_paths` merges several
equivalent `PATH`s into one group, `source_index_pointer` alone (first `path_id` only)
silently dropped the provenance of every other merged `path_id`. `path_provenance` is
the complete, ordered `path_id` -> `source_index_pointer` mapping for every merged
`path_id`, never just the first one; `source_index_pointer` itself is unchanged
(kept for backward compatibility with existing callers) and remains only the first
entry of that same list.
"""
from collections import defaultdict

#: Confirmed evidence is prioritized over inferred, which is prioritized over
#: genuinely unresolved -- never the reverse, and unresolved is never dropped.
CONFIDENCE_ORDER = {"confirmed": 0, "inferred": 1, "unresolved": 2}

#: Deterministic, name-based, conservative classification of designer/framework
#: boilerplate (V4.2 finding F-06, `InitializeComponent()` noise in
#: `UNRESOLVED_FINDINGS.md`). This only adds an explicit `technical_noise_candidate`
#: tag a later rendering stage may choose to de-emphasize; it never removes the
#: underlying evidence and never promotes or demotes it to/from business meaning.
TECHNICAL_NOISE_METHOD_NAMES = frozenset({"InitializeComponent", "Dispose", "InitializeCulture"})

#: The exact method names `legacy_documenter.extractors.database_extractor.TRANSACTION_RE`
#: already recognizes when extracting data-access evidence (V4.3-R3). Longest names
#: first so `BeginTransaction` is matched before the `BeginTrans` prefix it contains.
#: This is a literal match against the already-extracted evidence *expression* text
#: (the sanitized source line), never a guess derived from a name or identifier.
TRANSACTION_VERB_KEYWORDS = ("BeginTransaction", "BeginTrans", "Commit", "Rollback")

MODEL_VERSION = "V4.3-R3"


class UnknownFlowError(ValueError):
    """Raised when `hydrate_flow` is asked to hydrate a `flow_id` absent from `ix`.

    This is a caller-input error, not a report of missing evidence: hydrating a
    flow that genuinely exists but has gaps (e.g. an entry point without a
    resolved `start_method`) never raises -- it degrades to `None` fields, exactly
    like the rest of the deterministic pipeline.
    """


class EvidenceHydrator:
    """Selects, deduplicates and hydrates FLOW/PATH/DAO/SP evidence for one flow at a time."""

    MODEL_VERSION = MODEL_VERSION

    def hydrate_flow(self, flow_id: str, ix: dict) -> dict:
        """Builds one hydrated FLOW record for `flow_id`, using only evidence already in `ix`."""
        flows = {f["id"]: f for f in ix.get("functional_flows", [])}
        flow = flows.get(flow_id)
        if flow is None:
            raise UnknownFlowError(flow_id)
        entry_points = {e["id"]: e for e in ix.get("entry_points", [])}
        entry = entry_points.get(flow.get("entry_point_id"), {})
        data_access = {d["id"]: d for d in ix.get("data_access", []) if d.get("id")}
        stored_procedures = {p["id"]: p for p in ix.get("stored_procedures", []) if p.get("id")}
        sql_operations = {s["id"]: s for s in ix.get("sql_operations", []) if s.get("id")}
        data_parameters = ix.get("data_parameters", [])

        raw_paths = [p for p in ix.get("functional_paths", []) if p.get("flow_id") == flow_id]
        groups = self.select_and_deduplicate_paths(raw_paths)
        hydrated_paths = [self._hydrate_path_group(g, data_access, stored_procedures, sql_operations) for g in groups]

        return {
            "model_version": self.MODEL_VERSION,
            "flow_id": flow_id,
            "entry_point": {
                "id": flow.get("entry_point_id"),
                "webform": entry.get("webform"),
                "event": entry.get("event"),
                "handler": entry.get("handler"),
                "start_method": entry.get("start_method"),
                "project": entry.get("project"),
            },
            "projects": list(flow.get("project_sequence", [])),
            "paths": hydrated_paths,
            "terminals": self._terminals(hydrated_paths),
            "transactions": self._transactions(hydrated_paths),
            "data_operations": self._data_operations(hydrated_paths),
            "parameters": self._parameters(hydrated_paths, data_parameters),
            "confidence": flow.get("confidence"),
            "unresolved": [p["path_ids"][0] for p in hydrated_paths if p["terminal_type"] == "unresolved_boundary"],
            "provenance": {
                "source_indexes": [
                    "index/functional_flows.json", "index/functional_paths.json", "index/entry_points.json",
                    "index/data_access.json", "index/stored_procedures.json", "index/sql_operations.json",
                    "index/data_parameters.json",
                ],
                "flow_source_index_pointer": f"index/functional_flows.json#{flow_id}",
            },
            "selection": {
                "input_path_count": len(raw_paths),
                "output_path_count": len(hydrated_paths),
                "deduplicated_path_count": len(raw_paths) - len(hydrated_paths),
                "priority_policy": "confirmed_before_inferred_before_unresolved",
            },
        }

    def select_and_deduplicate_paths(self, paths: list[dict]) -> list[dict]:
        """Groups equivalent path chains, preserves all their `path_id`s, and orders confirmed first.

        Two paths are "equivalent" (deduplicated into one group) only when their
        `terminal_type`, `terminal_target` and `nodes` sequence are all identical --
        never by inspecting `path_id` or evidence content. Deduplication merges
        identity, never evidence: every merged `path_id` and every merged
        `evidence_refs` entry is preserved in the resulting group.
        """
        groups: dict[tuple, dict] = {}
        for path in sorted(paths, key=lambda p: p.get("path_id", "")):
            signature = (path.get("terminal_type"), path.get("terminal_target"), tuple(path.get("nodes", [])))
            group = groups.setdefault(signature, {
                "path_ids": [], "terminal_type": path.get("terminal_type"),
                "terminal_target": path.get("terminal_target"), "nodes": list(path.get("nodes", [])),
                "confidence": path.get("confidence"), "evidence_refs": set(),
            })
            group["path_ids"].append(path.get("path_id"))
            group["evidence_refs"].update(path.get("evidence_refs", []))
            if CONFIDENCE_ORDER.get(path.get("confidence"), 99) < CONFIDENCE_ORDER.get(group["confidence"], 99):
                group["confidence"] = path.get("confidence")
        ordered = sorted(groups.values(), key=lambda g: (CONFIDENCE_ORDER.get(g["confidence"], 99), g["path_ids"][0]))
        for group in ordered:
            group["evidence_refs"] = sorted(group["evidence_refs"])
        return ordered

    def _hydrate_path_group(self, group: dict, data_access: dict, stored_procedures: dict, sql_operations: dict) -> dict:
        nodes = [self._hydrate_node(node_id, data_access, stored_procedures, sql_operations) for node_id in group["nodes"]]
        terminal = self._resolve_terminal(group["terminal_type"], group["terminal_target"], data_access, stored_procedures, sql_operations)
        noise = bool(terminal.get("technical_noise_candidate")) or any(n.get("technical_noise_candidate") for n in nodes)
        return {
            "path_ids": group["path_ids"],
            "nodes": nodes,
            "terminal_type": group["terminal_type"],
            "terminal": terminal,
            "confidence": group["confidence"],
            "evidence_refs": group["evidence_refs"],
            "technical_noise_candidate": noise,
            "source_index_pointer": f"index/functional_paths.json#{group['path_ids'][0]}",
            "path_provenance": [
                {"path_id": pid, "source_index_pointer": f"index/functional_paths.json#{pid}"}
                for pid in group["path_ids"]
            ],
        }

    def _hydrate_node(self, node_id: object, data_access: dict, stored_procedures: dict, sql_operations: dict) -> dict:
        if node_id in data_access:
            d = data_access[node_id]
            return {
                "id": node_id, "type": "data_access", "caller": f"{d.get('class')}.{d.get('method')}",
                "operation_kind": d.get("operation_kind"), "confidence": d.get("confidence"),
                "technical_noise_candidate": d.get("method") in TECHNICAL_NOISE_METHOD_NAMES,
                "data_operation_kind": d.get("sql_operation"),
                "transaction_evidence": self._transaction_evidence(d),
                "source_index_pointer": f"index/data_access.json#{node_id}",
            }
        if node_id in stored_procedures:
            p = stored_procedures[node_id]
            return {
                "id": node_id, "type": "stored_procedure", "resolved_name": p.get("name"),
                "confidence": p.get("confidence"), "technical_noise_candidate": False,
            }
        if node_id in sql_operations:
            s = sql_operations[node_id]
            return {
                "id": node_id, "type": "sql_operation", "resolved_name": s.get("operation"),
                "confidence": s.get("confidence"), "technical_noise_candidate": False,
            }
        return {"id": node_id, "type": "unresolved_node", "technical_noise_candidate": False}

    def _resolve_terminal(self, terminal_type: object, terminal_target: object, data_access: dict, stored_procedures: dict, sql_operations: dict) -> dict:
        if terminal_type == "stored_procedure" and terminal_target in stored_procedures:
            p = stored_procedures[terminal_target]
            return {
                "id": terminal_target, "resolved_name": p.get("name"), "package": p.get("package"),
                "procedure": p.get("procedure"), "technical_noise_candidate": False,
            }
        if terminal_type == "sql" and terminal_target in sql_operations:
            s = sql_operations[terminal_target]
            return {"id": terminal_target, "resolved_name": s.get("operation"), "technical_noise_candidate": False}
        if terminal_target in data_access:
            d = data_access[terminal_target]
            return {
                "id": terminal_target, "resolved_name": f"{d.get('class')}.{d.get('method')}",
                "technical_noise_candidate": d.get("method") in TECHNICAL_NOISE_METHOD_NAMES,
                "data_operation_kind": d.get("sql_operation"),
                "transaction_evidence": self._transaction_evidence(d),
            }
        # `unresolved_boundary` (or any other unrecognized terminal type/target): the target is
        # preserved verbatim, never guessed and never silently promoted to a resolved name.
        return {"id": terminal_target, "resolved_name": None, "technical_noise_candidate": False}

    def _transaction_evidence(self, d: dict) -> dict | None:
        """Surfaces transaction evidence (V4.3-R3) already recorded on a data-access operation record.

        Returns `None` unless `operation_kind == "transaction"` -- the same
        deterministic flag `DatabaseExtractor` already sets for
        `BeginTrans(action)`/`Commit`/`Rollback` calls. When present, `verb` is a
        literal keyword match against the already-extracted evidence *expression*
        text (never a guess): `None` if the evidence is missing or none of the
        known keywords are found in it, exactly like the rest of this module never
        invents a name it cannot find in `ix`.
        """
        if d.get("operation_kind") != "transaction":
            return None
        evidence = d.get("evidence") or []
        expression = evidence[0].get("expression", "") if evidence else ""
        verb = next((kw for kw in TRANSACTION_VERB_KEYWORDS if kw in expression), None)
        return {"verb": verb, "confidence": d.get("confidence")}

    def _transactions(self, hydrated_paths: list[dict]) -> list[dict]:
        """Deduplicated, id-sorted list of transaction evidence (V4.3-R3) reached by this flow's paths.

        Collects every node/terminal carrying non-`None` `transaction_evidence`
        (see `_transaction_evidence`) across all hydrated paths -- never inferred
        from a name, only from the `operation_kind == "transaction"` flag and the
        literal evidence expression already present in `ix`.
        """
        found: dict[object, dict] = {}
        for path in hydrated_paths:
            candidates = [*path["nodes"], path["terminal"]]
            for item in candidates:
                evidence = item.get("transaction_evidence") if isinstance(item, dict) else None
                if evidence is not None and item.get("id") is not None:
                    found[item["id"]] = {
                        "id": item["id"], "verb": evidence["verb"], "confidence": evidence["confidence"],
                        "path_ids": path["path_ids"], "source_index_pointer": f"index/data_access.json#{item['id']}",
                    }
        return [found[k] for k in sorted(found, key=str)]

    def _data_operations(self, hydrated_paths: list[dict]) -> list[dict]:
        """Deduplicated, id-sorted list of confirmed data-operation kinds (V4.3-R3) reached by this flow.

        Only entries with a non-`None` `data_operation_kind` (the raw
        `INSERT`/`UPDATE`/`DELETE`/`SELECT`/`MERGE` verb `DatabaseExtractor` already
        recorded on the operation record's own `sql_operation` field) are included.
        A stored procedure resolved only by name, with no such field, never appears
        here -- this is the mechanism that keeps a flow from being classified as a
        "write" from a stored procedure's name alone (V4.3-R3, R0 acceptance case C).
        """
        found: dict[object, dict] = {}
        for path in hydrated_paths:
            candidates = [*path["nodes"], path["terminal"]]
            for item in candidates:
                kind = item.get("data_operation_kind") if isinstance(item, dict) else None
                if kind is not None and item.get("id") is not None:
                    found[item["id"]] = {
                        "id": item["id"], "operation": kind, "confidence": item.get("confidence"),
                        "path_ids": path["path_ids"], "source_index_pointer": f"index/data_access.json#{item['id']}",
                    }
        return [found[k] for k in sorted(found, key=str)]

    def _terminals(self, hydrated_paths: list[dict]) -> dict:
        stored, sql, unresolved = {}, {}, {}
        for path in hydrated_paths:
            terminal, kind = path["terminal"], path["terminal_type"]
            bucket = {"stored_procedure": stored, "sql": sql, "unresolved_boundary": unresolved}.get(kind)
            if bucket is not None and terminal.get("id") is not None:
                bucket[terminal["id"]] = terminal
        return {
            "stored_procedures": [stored[k] for k in sorted(stored)],
            "sql_operations": [sql[k] for k in sorted(sql)],
            "unresolved_boundaries": [unresolved[k] for k in sorted(unresolved)],
        }

    def _parameters(self, hydrated_paths: list[dict], data_parameters: list[dict]) -> list[dict]:
        callers = sorted({n["caller"] for p in hydrated_paths for n in p["nodes"] if n.get("type") == "data_access" and n.get("caller")})
        by_caller: dict[str, set] = defaultdict(set)
        for param in data_parameters:
            caller = f"{param.get('class')}.{param.get('method')}"
            if caller in callers:
                by_caller[caller].add(param.get("name") or "(unnamed)")
        return [{"caller": caller, "names": sorted(by_caller[caller])} for caller in callers if by_caller[caller]]
