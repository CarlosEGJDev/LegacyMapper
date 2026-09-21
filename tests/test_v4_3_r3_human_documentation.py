import unittest
from pathlib import Path

from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.documentation.human_flow_documentation import (
    InvalidInterpretationError,
    render_flow_document,
)


def _ix():
    return {
        "functional_flows": [
            {"id": "FLOW-A", "entry_point_id": "EP-A", "confidence": "confirmed", "project_sequence": ["DAL", "WEB"]},
            {"id": "FLOW-B", "entry_point_id": "EP-B", "confidence": "unresolved", "project_sequence": ["WEB"]},
        ],
        "functional_paths": [
            {"path_id": "PATH-1", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-1"]},
            {"path_id": "PATH-2", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-2"]},
            {"path_id": "PATH-3", "flow_id": "FLOW-A", "nodes": ["DAO-2"], "terminal_type": "unresolved_boundary", "terminal_target": "UnknownHelper.Execute", "confidence": "unresolved", "evidence_refs": ["EVR-3"]},
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
        ],
    }


def _ix_transactional():
    """R0 acceptance case C (write/transaction): `cobChqInsRen.ascx` -> `Click` -> `HypGuardar_Click`."""
    return {
        "functional_flows": [
            {"id": "FLOW-C", "entry_point_id": "EP-C", "confidence": "confirmed", "project_sequence": ["DAL"]},
        ],
        "functional_paths": [
            {"path_id": "PATH-10", "flow_id": "FLOW-C", "nodes": ["DAO-TX-BEGIN", "DAO-TX-INSERT"], "terminal_type": "stored_procedure", "terminal_target": "SP-2", "confidence": "confirmed", "evidence_refs": ["EVR-10"]},
        ],
        "entry_points": [
            {"id": "EP-C", "webform": "cobChqInsRen.ascx", "event": "Click", "handler": "HypGuardar_Click", "start_method": "HypGuardar_Click"},
        ],
        "data_access": [
            {"id": "DAO-TX-BEGIN", "class": "CobDAO", "method": "GuardarCheque", "operation_kind": "transaction", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 10, "expression": "dbc.BeginTrans()"}]},
            {"id": "DAO-TX-INSERT", "class": "CobDAO", "method": "InsertarDetalle", "operation_kind": "sql", "sql_operation": "INSERT", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 11, "expression": 'cmd.CommandText = "INSERT INTO Detalle ..."'}]},
        ],
        "stored_procedures": [
            # Named like a write, with zero transaction/SQL-verb evidence of its own -- must never, by
            # itself, be presented as a confirmed write.
            {"id": "SP-2", "name": "spInsertarRegistro", "package": "PKG_COB", "procedure": "PR_INSERTAR", "confidence": "confirmed", "evidence": []},
        ],
        "sql_operations": [],
        "data_parameters": [],
    }


class TransactionAndDataOperationRenderingTests(unittest.TestCase):
    """V4.3-R3 correction: R0 acceptance case C without narrative inference in the renderer."""

    def test_confirmed_transaction_evidence_is_presented_in_spanish(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        doc = render_flow_document(record)
        self.assertIn("evidencia transaccional confirmada", doc)
        self.assertIn("`BeginTrans`", doc)
        self.assertIn("### Evidencia transaccional", doc)

    def test_confirmed_data_operation_kind_is_presented_when_available(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        doc = render_flow_document(record)
        self.assertIn("### Operaciones de datos confirmadas", doc)
        self.assertIn("operación de datos confirmada `INSERT`", doc)

    def test_write_is_never_inferred_from_a_stored_procedure_name_alone(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        doc = render_flow_document(record)
        self.assertIn("spInsertarRegistro", doc)
        section_6 = doc.split("## 6.")[1].split("## 7.")[0]
        # The SP appears (procedure section) but is never labelled as a confirmed write/INSERT --
        # only the two data-access nodes with real index evidence are.
        sp_lines = [line for line in section_6.splitlines() if "spInsertarRegistro" in line]
        self.assertTrue(sp_lines)
        for line in sp_lines:
            self.assertNotIn("operación de datos confirmada", line)
            self.assertNotIn("`INSERT`", line)

    def test_absence_of_transaction_evidence_produces_no_transactional_section(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertNotIn("### Evidencia transaccional", doc)
        self.assertNotIn("### Operaciones de datos confirmadas", doc)

    def test_traceability_covers_transaction_and_data_operation_evidence(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-C", _ix_transactional())
        doc = render_flow_document(record)
        self.assertIn("DAO-TX-BEGIN", doc)
        self.assertIn("DAO-TX-INSERT", doc)
        self.assertIn("PATH-10", doc)


class RenderFlowDocumentTests(unittest.TestCase):
    def test_document_is_in_spanish_with_required_sections(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        for heading in (
            "## 1. Qué es y dónde está",
            "## 2. Evento/entrada inicial",
            "## 3. Resumen funcional determinista",
            "## 4. Rutas confirmadas principales",
            "## 5. Servicios/capas",
            "## 6. Datos/SP/SQL",
            "## 7. Qué queda no resuelto",
            "## 8. Evidencia técnica detallada / trazabilidad",
            "## Límites de esta documentación",
        ):
            self.assertIn(heading, doc)

    def test_resolved_names_are_the_primary_explanation_not_bare_ids(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("spActualizarSaldo", doc)
        self.assertIn("CobDAO.Actualizar", doc)
        section_4 = doc.split("## 4.")[1].split("## 5.")[0]
        self.assertNotIn("SP-1", section_4)

    def test_technical_names_are_preserved_intact(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("`CobDAO.Actualizar`", doc)
        self.assertIn("`spActualizarSaldo`", doc)
        self.assertIn("PKG_COB", doc)
        self.assertIn("PR_SALDO", doc)

    def test_unresolved_path_is_declared_not_hidden(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("UnknownHelper.Execute", doc)
        self.assertIn("PATH-3", doc)
        self.assertIn("no resuelto", doc.lower())

    def test_flow_without_confirmed_terminal_declares_uncertainty_without_inventing_a_terminal(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-B", _ix())
        doc = render_flow_document(record)
        self.assertIn("No se confirmó acceso a procedimientos almacenados", doc)
        self.assertNotIn("spActualizarSaldo", doc)
        self.assertIn("PATH-4", doc)

    def test_technical_noise_candidate_is_flagged_but_never_removed(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("UnknownHelper.Execute", doc)
        self.assertIn("no confirmado como lógica de negocio", doc)

    def test_traceability_section_lists_path_ids_evidence_refs_and_provenance(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        section_8 = doc.split("## 8.")[1]
        self.assertIn("PATH-1", section_8)
        self.assertIn("PATH-2", section_8)
        self.assertIn("EVR-1", section_8)
        self.assertIn("EVR-2", section_8)
        self.assertIn("index/functional_flows.json#FLOW-A", section_8)

    def test_deduplicated_path_shows_a_source_pointer_for_every_merged_path_id(self):
        # V4.3-R3 correction (human review): PATH-1/PATH-2 merge into one hydrated path group (same
        # terminal/nodes). Section 8 must show BOTH origins explicitly, never only PATH-1's.
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        section_8 = doc.split("## 8.")[1].split("Puntero de origen del flujo")[0]
        self.assertIn("`PATH-1` → `index/functional_paths.json#PATH-1`", section_8)
        self.assertIn("`PATH-2` → `index/functional_paths.json#PATH-2`", section_8)

    def test_undeduplicated_path_also_shows_its_own_source_pointer(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        section_8 = doc.split("## 8.")[1]
        self.assertIn("`PATH-3` → `index/functional_paths.json#PATH-3`", section_8)

    def test_technical_noise_caller_is_separated_from_the_business_services_list(self):
        # V4.3-R3 correction (human review): section 5 must never mix a technical/auxiliary caller
        # (InitializeComponent) into the main business-services list without distinction.
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        section_5 = doc.split("## 5.")[1].split("## 6.")[0]
        self.assertIn("### Elementos técnicos/auxiliares (no lógica de negocio)", section_5)
        main_list = section_5.split("### Elementos técnicos/auxiliares")[0]
        noise_subsection = section_5.split("### Elementos técnicos/auxiliares")[1]
        self.assertIn("`CobDAO.Actualizar`", main_list)
        self.assertNotIn("CobDAO.InitializeComponent", main_list)
        self.assertIn("`CobDAO.InitializeComponent`", noise_subsection)

    def test_technical_noise_caller_still_fully_traceable_elsewhere(self):
        # The separated presentation in section 5 never removes the noise caller's PATH/evidence/
        # provenance elsewhere in the document.
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("UnknownHelper.Execute", doc)
        self.assertIn("`PATH-3` → `index/functional_paths.json#PATH-3`", doc)
        self.assertIn("EVR-3", doc)

    def test_deterministic_document_is_useful_without_any_ai(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertNotIn("[INTERPRETED]", doc)
        self.assertNotIn("## Interpretación de IA", doc)
        self.assertIn("no se invoca ningún proveedor de IA", doc)

    def test_deterministic_across_repeated_calls(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        self.assertEqual(render_flow_document(record), render_flow_document(record))

    def test_document_is_not_a_mechanical_json_dump(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertNotIn("{'", doc)
        self.assertNotIn('": "', doc)

    def test_limits_are_declared_explicitly(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertIn("Límites de esta documentación", doc)
        self.assertIn("determinista", doc)


class InterpretedSectionTests(unittest.TestCase):
    def test_valid_interpretation_is_rendered_in_a_separate_tagged_section(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record, interpretations=[
            {"statement": "Este flujo actualiza el saldo del cliente.", "evidence_refs": ["EVR-1"]},
        ])
        self.assertIn("## Interpretación de IA (`INTERPRETED`)", doc)
        self.assertIn("[INTERPRETED]", doc)
        self.assertIn("Este flujo actualiza el saldo del cliente.", doc)

    def test_interpretation_without_evidence_refs_is_rejected(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        with self.assertRaises(InvalidInterpretationError):
            render_flow_document(record, interpretations=[{"statement": "x", "evidence_refs": []}])

    def test_interpretation_referencing_unknown_evidence_is_rejected(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        with self.assertRaises(InvalidInterpretationError):
            render_flow_document(record, interpretations=[{"statement": "x", "evidence_refs": ["EVR-NOPE"]}])

    def test_interpretation_cannot_claim_confirmed_status(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        with self.assertRaises(InvalidInterpretationError):
            render_flow_document(record, interpretations=[{"statement": "x", "evidence_refs": ["EVR-1"], "status": "CONFIRMED"}])

    def test_no_interpretation_means_no_interpreted_section(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-A", _ix())
        doc = render_flow_document(record)
        self.assertNotIn("[INTERPRETED]", doc)
        self.assertNotIn("## Interpretación de IA", doc)


class RuntimeIndependenceTests(unittest.TestCase):
    def test_module_does_not_import_llm(self):
        import ast
        tree = ast.parse(Path("legacy_documenter/documentation/human_flow_documentation.py").read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported_from = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(any(name and "llm" in name for name in imported | imported_from))

    def test_module_is_not_wired_into_the_cli_pipeline(self):
        for module_path in ("legacy_documenter/cli/full_pipeline.py", "legacy_documenter/cli/pipeline_stages.py", "legacy_documenter/main.py"):
            path = Path(module_path)
            if path.exists():
                self.assertNotIn("human_flow_documentation", path.read_text(encoding="utf-8"))

    def test_module_never_writes_to_disk(self):
        source = Path("legacy_documenter/documentation/human_flow_documentation.py").read_text(encoding="utf-8")
        for forbidden in ("open(", "write_text", "Path(", "os.", "requests.", "urllib"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
