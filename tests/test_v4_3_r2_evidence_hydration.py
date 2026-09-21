import unittest
from pathlib import Path

from legacy_documenter.context.hydration import EvidenceHydrator, UnknownFlowError


def _ix():
    return {
        "functional_flows": [
            {"id": "FLOW-A", "entry_point_id": "EP-A", "confidence": "confirmed", "project_sequence": ["DAL", "WEB"]},
            {"id": "FLOW-B", "entry_point_id": "EP-B", "confidence": "unresolved", "project_sequence": ["WEB"]},
        ],
        "functional_paths": [
            # Two equivalent chains for FLOW-A (same terminal + nodes, different path_id): must dedup.
            {"path_id": "PATH-1", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-1"]},
            {"path_id": "PATH-2", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-2"]},
            # A genuinely distinct, unresolved path for FLOW-A: must be preserved, never dropped.
            {"path_id": "PATH-3", "flow_id": "FLOW-A", "nodes": ["DAO-2"], "terminal_type": "unresolved_boundary", "terminal_target": "UnknownHelper.Execute", "confidence": "unresolved", "evidence_refs": ["EVR-3"]},
            # FLOW-B: no confirmed terminal at all (case D of the R0 acceptance criteria).
            {"path_id": "PATH-4", "flow_id": "FLOW-B", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "unknown", "confidence": "unresolved", "evidence_refs": []},
        ],
        "entry_points": [
            {"id": "EP-A", "webform": "cobCargaArcIntRea.ascx", "event": "Click", "handler": "btnCargar_Click", "start_method": "btnCargar_Click"},
            {"id": "EP-B", "webform": "CobConsultaTransferencia.ascx", "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
        ],
        "data_access": [
            {"id": "DAO-1", "class": "CobDAO", "method": "Actualizar", "project": "DAL", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 5}]},
            {"id": "DAO-2", "class": "CobDAO", "method": "InitializeComponent", "project": "DAL", "operation_kind": "call", "confidence": "unresolved", "evidence": []},
        ],
        "stored_procedures": [
            {"id": "SP-1", "name": "spActualizarSaldo", "package": "PKG_COB", "procedure": "PR_SALDO", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 6}]},
        ],
        "sql_operations": [],
        "data_parameters": [
            {"class": "CobDAO", "method": "Actualizar", "name": "pIdCliente"},
            {"class": "CobDAO", "method": "Actualizar", "name": "pMonto"},
            {"class": "OtherDAO", "method": "Unrelated", "name": "pIgnored"},
        ],
    }


class SelectionAndDeduplicationTests(unittest.TestCase):
    def test_equivalent_chains_are_merged_without_losing_path_ids_or_evidence(self):
        groups = EvidenceHydrator().select_and_deduplicate_paths(_ix()["functional_paths"][:2])
        self.assertEqual(len(groups), 1)
        self.assertEqual(sorted(groups[0]["path_ids"]), ["PATH-1", "PATH-2"])
        self.assertEqual(groups[0]["evidence_refs"], ["EVR-1", "EVR-2"])

    def test_distinct_chains_are_not_merged(self):
        groups = EvidenceHydrator().select_and_deduplicate_paths(_ix()["functional_paths"])
        self.assertEqual(len(groups), 3)

    def test_confirmed_paths_are_prioritized_before_unresolved(self):
        groups = EvidenceHydrator().select_and_deduplicate_paths(_ix()["functional_paths"])
        self.assertEqual([g["confidence"] for g in groups], sorted((g["confidence"] for g in groups), key=lambda c: {"confirmed": 0, "inferred": 1, "unresolved": 2}[c]))

    def test_deterministic_ordering(self):
        a = EvidenceHydrator().select_and_deduplicate_paths(_ix()["functional_paths"])
        b = EvidenceHydrator().select_and_deduplicate_paths(list(reversed(_ix()["functional_paths"])))
        self.assertEqual(a, b)


class HydrateFlowTests(unittest.TestCase):
    def test_unknown_flow_raises(self):
        with self.assertRaises(UnknownFlowError):
            EvidenceHydrator().hydrate_flow("FLOW-MISSING", _ix())

    def test_flow_with_confirmed_stored_procedure_terminal_is_hydrated_with_resolved_names(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        self.assertEqual(record["entry_point"], {"id": "EP-A", "webform": "cobCargaArcIntRea.ascx", "event": "Click", "handler": "btnCargar_Click", "start_method": "btnCargar_Click", "project": None})
        self.assertEqual(record["terminals"]["stored_procedures"], [{"id": "SP-1", "resolved_name": "spActualizarSaldo", "package": "PKG_COB", "procedure": "PR_SALDO", "technical_noise_candidate": False}])
        self.assertEqual(record["selection"]["input_path_count"], 3)
        self.assertEqual(record["selection"]["output_path_count"], 2)
        self.assertEqual(record["selection"]["deduplicated_path_count"], 1)

    def test_flow_without_confirmed_terminal_preserves_unresolved_without_inventing_a_terminal(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-B", _ix())
        self.assertEqual(record["terminals"]["stored_procedures"], [])
        self.assertEqual(record["terminals"]["sql_operations"], [])
        self.assertEqual(len(record["terminals"]["unresolved_boundaries"]), 1)
        self.assertEqual(record["terminals"]["unresolved_boundaries"][0]["resolved_name"], None)
        self.assertEqual(record["unresolved"], ["PATH-4"])

    def test_significant_unresolved_path_is_preserved_alongside_a_confirmed_terminal(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        self.assertEqual(record["unresolved"], ["PATH-3"])
        self.assertTrue(any(p["terminal_type"] == "unresolved_boundary" for p in record["paths"]))

    def test_traceability_back_to_original_ids_and_indexes(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        confirmed_path = next(p for p in record["paths"] if p["terminal_type"] == "stored_procedure")
        self.assertEqual(sorted(confirmed_path["path_ids"]), ["PATH-1", "PATH-2"])
        self.assertEqual(confirmed_path["source_index_pointer"], "index/functional_paths.json#PATH-1")
        self.assertEqual(record["provenance"]["flow_source_index_pointer"], "index/functional_flows.json#FLOW-A")
        self.assertIn("index/functional_flows.json", record["provenance"]["source_indexes"])

    def test_deduplicated_path_group_preserves_a_source_index_pointer_for_every_merged_path_id(self):
        # V4.3-R3 correction (human review of the generated samples): `source_index_pointer` alone
        # only ever pointed at the *first* merged `path_id` -- PATH-1's pointer, never PATH-2's. This
        # silently dropped PATH-2's own provenance once the two equivalent chains were deduplicated
        # into a single group. `path_provenance` must carry a complete, ordered mapping instead.
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        confirmed_path = next(p for p in record["paths"] if p["terminal_type"] == "stored_procedure")
        self.assertEqual(confirmed_path["path_provenance"], [
            {"path_id": "PATH-1", "source_index_pointer": "index/functional_paths.json#PATH-1"},
            {"path_id": "PATH-2", "source_index_pointer": "index/functional_paths.json#PATH-2"},
        ])
        # No merged `path_id` is ever missing from `path_provenance`, regardless of how many were merged.
        self.assertEqual(
            {entry["path_id"] for entry in confirmed_path["path_provenance"]},
            set(confirmed_path["path_ids"]),
        )

    def test_undeduplicated_path_still_carries_its_own_path_provenance_entry(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        unresolved_path = next(p for p in record["paths"] if p["terminal_type"] == "unresolved_boundary")
        self.assertEqual(unresolved_path["path_provenance"], [
            {"path_id": "PATH-3", "source_index_pointer": "index/functional_paths.json#PATH-3"},
        ])

    def test_available_parameters_are_resolved_for_reached_callers_only(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        self.assertEqual(record["parameters"], [{"caller": "CobDAO.Actualizar", "names": ["pIdCliente", "pMonto"]}])

    def test_technical_noise_is_flagged_conservatively_without_being_dropped_or_promoted(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        noisy_path = next(p for p in record["paths"] if p["terminal_type"] == "unresolved_boundary")
        self.assertTrue(noisy_path["technical_noise_candidate"])
        self.assertEqual(noisy_path["terminal"]["resolved_name"], None)
        self.assertIn("PATH-3", [pid for p in record["paths"] for pid in p["path_ids"]])

    def test_deterministic_across_repeated_calls(self):
        ix = _ix()
        self.assertEqual(EvidenceHydrator().hydrate_flow("FLOW-A", ix), EvidenceHydrator().hydrate_flow("FLOW-A", ix))

    def test_no_llm_output_leaks_into_a_hydrated_record(self):
        import json
        self.assertNotIn("INTERPRETED", json.dumps(EvidenceHydrator().hydrate_flow("FLOW-A", _ix())))


def _ix_transactional():
    """A separate fixture (V4.3-R3, R0 acceptance case C) isolated from `_ix()` above so these new
    assertions never perturb the existing R2 path-count/dedup fixtures."""
    return {
        "functional_flows": [
            {"id": "FLOW-C", "entry_point_id": "EP-C", "confidence": "confirmed", "project_sequence": ["DAL"]},
        ],
        "functional_paths": [
            {"path_id": "PATH-10", "flow_id": "FLOW-C", "nodes": ["DAO-TX-BEGIN", "DAO-TX-INSERT", "DAO-TX-UNKNOWN"], "terminal_type": "stored_procedure", "terminal_target": "SP-2", "confidence": "confirmed", "evidence_refs": ["EVR-10"]},
        ],
        "entry_points": [
            {"id": "EP-C", "webform": "cobChqInsRen.ascx", "event": "Click", "handler": "HypGuardar_Click", "start_method": "HypGuardar_Click"},
        ],
        "data_access": [
            # A confirmed BeginTrans call: `operation_kind == "transaction"`, and the literal evidence
            # expression contains the verb -- never inferred from `method`/`class` naming.
            {"id": "DAO-TX-BEGIN", "class": "CobDAO", "method": "GuardarCheque", "operation_kind": "transaction", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 10, "expression": "dbc.BeginTrans()"}]},
            # A confirmed dynamic INSERT: `sql_operation == "INSERT"` already on the operation record
            # itself (R2's data_access shape), independent of the separate `sql_operations` catalog.
            {"id": "DAO-TX-INSERT", "class": "CobDAO", "method": "InsertarDetalle", "operation_kind": "sql", "sql_operation": "INSERT", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 11, "expression": 'cmd.CommandText = "INSERT INTO Detalle ..."'}]},
            # `operation_kind == "transaction"` but no matching keyword in the (missing) evidence: verb
            # must stay `None`, never guessed.
            {"id": "DAO-TX-UNKNOWN", "class": "CobDAO", "method": "Finalizar", "operation_kind": "transaction", "confidence": "unresolved", "evidence": []},
        ],
        "stored_procedures": [
            # Deliberately named like a write ("Insertar...") with zero transaction/SQL-verb evidence of
            # its own: resolving a terminal to this SP must never, by itself, produce a data-operation
            # entry -- that would be inferring "write" from a name.
            {"id": "SP-2", "name": "spInsertarRegistro", "package": "PKG_COB", "procedure": "PR_INSERTAR", "confidence": "confirmed", "evidence": []},
        ],
        "sql_operations": [],
        "data_parameters": [],
    }


class TransactionAndDataOperationEvidenceTests(unittest.TestCase):
    """V4.3-R3: extends R2's hydration with transaction/data-operation evidence (R0 acceptance case C)."""

    def test_confirmed_transaction_evidence_is_hydrated_with_its_verb(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        self.assertEqual(record["transactions"], [
            {"id": "DAO-TX-BEGIN", "verb": "BeginTrans", "confidence": "confirmed", "path_ids": ["PATH-10"], "source_index_pointer": "index/data_access.json#DAO-TX-BEGIN"},
            {"id": "DAO-TX-UNKNOWN", "verb": None, "confidence": "unresolved", "path_ids": ["PATH-10"], "source_index_pointer": "index/data_access.json#DAO-TX-UNKNOWN"},
        ])

    def test_absence_of_transaction_evidence_is_none_not_a_guess(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        node = next(n for p in record["paths"] for n in p["nodes"] if n["id"] == "DAO-1")
        self.assertIsNone(node["transaction_evidence"])
        self.assertEqual(record["transactions"], [])

    def test_confirmed_sql_write_operation_kind_is_hydrated_from_the_index(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        self.assertEqual(record["data_operations"], [
            {"id": "DAO-TX-INSERT", "operation": "INSERT", "confidence": "confirmed", "path_ids": ["PATH-10"], "source_index_pointer": "index/data_access.json#DAO-TX-INSERT"},
        ])

    def test_write_is_never_inferred_from_a_stored_procedure_name_alone(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        operation_ids = {op["id"] for op in record["data_operations"]}
        self.assertNotIn("SP-2", operation_ids)
        terminal = record["paths"][0]["terminal"]
        self.assertEqual(terminal["id"], "SP-2")
        self.assertNotIn("data_operation_kind", terminal)

    def test_transaction_and_data_operation_traceability(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        for entry in record["transactions"] + record["data_operations"]:
            self.assertEqual(entry["path_ids"], ["PATH-10"])
            self.assertTrue(entry["source_index_pointer"].startswith("index/data_access.json#"))
        self.assertIn("PATH-10", record["paths"][0]["path_ids"])

    def test_deterministic_across_repeated_calls(self):
        ix = _ix_transactional()
        self.assertEqual(EvidenceHydrator().hydrate_flow("FLOW-C", ix), EvidenceHydrator().hydrate_flow("FLOW-C", ix))


class RuntimeIndependenceTests(unittest.TestCase):
    def test_hydration_module_does_not_import_llm(self):
        import ast
        tree = ast.parse(Path("legacy_documenter/context/hydration.py").read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported_from = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(any(name and "llm" in name for name in imported | imported_from))

    def test_hydration_wiring_is_confined_to_pipeline_stages(self):
        # V4.3-R7 made the wiring decision R2/R3/R4 deliberately deferred
        # (docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md section 9):
        # `pipeline_stages.render_documentation` now hydrates every flow to
        # feed the Spanish `human_documentation_scaling` renderers, so it
        # legitimately references `hydration` now. `full_pipeline.py` and
        # `main.py` still never do -- they call into `pipeline_stages`,
        # which owns this responsibility, never reimplementing or
        # reaching around it.
        pipeline_stages_source = Path("legacy_documenter/cli/pipeline_stages.py").read_text(encoding="utf-8")
        self.assertIn("hydration", pipeline_stages_source)
        for module_path in ("legacy_documenter/cli/full_pipeline.py", "legacy_documenter/main.py"):
            path = Path(module_path)
            if path.exists():
                self.assertNotIn("hydration", path.read_text(encoding="utf-8"))

    def test_hydration_never_writes_to_disk(self):
        source = Path("legacy_documenter/context/hydration.py").read_text(encoding="utf-8")
        for forbidden in ("open(", "write_text", "Path(", "os.", "requests.", "urllib"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
