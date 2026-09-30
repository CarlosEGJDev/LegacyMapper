"""V5.2 R3.1: human semantic corrections (ownership vs participation, direct vs
indirect data access, honest data metric, dependency classes, terminology,
duplicate project names, noise policy data, RUN_SUMMARY location).

Contract-level assertions on a small synthetic source; no full-text snapshots.
"""
from __future__ import annotations

import copy
import json
import re
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageResult, StageStatus
from legacy_documenter.cli.run_summary_presenter import compute_output_locations
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.documentation_v52.config import DEFAULTS_DIR, ConfigRegistry
from legacy_documenter.documentation_v52.engine import OUTPUT_DIRNAME, generate_documentation_v52
from legacy_documenter.documentation_v52.transform import AudienceTransformer

WEB = "WebA.vbproj"
BL = "bl\\blA\\blA.vbproj"
SYS = "sys\\sysA\\sysA.vbproj"
BACKUP = "proyectos\\slnA\\Backup\\WebA\\WebA.vbproj"
RAW_TECHNICAL = ("stored_procedure", "web_event", "web_lifecycle")


def _source() -> dict:
    projects = [
        {"name": "WebA", "path": WEB, "output_type": "Library"},
        {"name": "blA", "path": BL, "output_type": "Library", "assembly_name": "blA"},
        {"name": "sysA", "path": SYS, "output_type": "Library"},
        {"name": "WebA", "path": BACKUP, "output_type": "Library"},
    ]

    def ep(index: int, project: str | None, kind: str = "web_event") -> dict:
        return {"id": f"EP-{index:010d}", "type": kind, "webform": f"webA\\f{index}.ascx", "event": "Click",
                "handler": f"btn{index}_Click", "project": project, "confidence": "confirmed"}

    def flow(index: int, sequence: list, terminals: list, unresolved: bool = False) -> dict:
        return {"id": f"FLOW-{index:010d}", "entry_point_id": f"EP-{index:010d}", "webform": f"webA\\f{index}.ascx",
                "event": "Click", "handler": f"btn{index}_Click", "project_sequence": sequence,
                "terminal_operations": terminals, "has_confirmed_terminal": bool(terminals),
                "has_unresolved_boundary": unresolved}

    entry_points = [ep(0, WEB), ep(1, WEB), ep(2, WEB), ep(3, None), ep(4, WEB, "web_lifecycle")]
    flows = [
        flow(0, [WEB, BL, SYS], ["DAO-0000000001"]),       # reaches a real procedure through bl and sys
        flow(1, [WEB, BL], ["DAO-0000000002"]),           # reaches only transaction control
        flow(2, [WEB], [], unresolved=True),              # stops at an unresolved call
        flow(3, [BL], ["DAO-0000000001"]),                # webform whose project is unknown
        flow(4, [WEB], []),
    ]
    data_access = [
        {"id": "DAO-0000000001", "operation_kind": "stored_procedure", "stored_procedure": "PKG_X.PROC_A", "provider": "OraConn",
         "class": "D", "method": "m", "project": SYS, "confidence": "confirmed", "evidence": [{"file": "D.vb", "line": 7}]},
        {"id": "DAO-0000000002", "operation_kind": "transaction", "provider": "OraConn", "class": "D", "method": "t",
         "project": BL, "confidence": "confirmed", "evidence": [{"file": "T.vb", "line": 9}]},
    ]
    return {
        "repository": {"root": "C:\\repo\\Sample", "stats": {"vb_source": 10}},
        "solutions": [{"name": "SlnA", "path": "SlnA\\SlnA.sln", "projects": [
            {"name": "WebA", "path": "..\\WebA.vbproj"}, {"name": "blA", "path": "..\\bl\\blA\\blA.vbproj"}]}],
        "projects": projects, "entry_points": entry_points, "functional_flows": flows,
        "flow_unresolved": [{"flow_id": "FLOW-0000000002", "path_id": "PATH-x", "terminal_target": "Me.grd.DataBind()"},
                            {"flow_id": "FLOW-0000000002", "path_id": "PATH-y", "terminal_target": "Foo.Bar(  x )"}],
        "data_access": data_access, "stored_procedures": [{"name": "PKG_X.PROC_A", "package": "PKG_X"}],
        "sql_operations": [],
        "dependencies": [
            {"source": WEB, "target": BL, "dependency_type": "Project -> Project"},
            {"source": WEB, "target": "blA, Version=1.0.0.0", "dependency_type": "Project -> DLL"},
            {"source": WEB, "target": "ThirdPartyGrid", "dependency_type": "Project -> DLL"},
            {"source": WEB, "target": "System.Data", "dependency_type": "Project -> DLL"},
            {"source": WEB, "target": "AssemblyInfo.vb", "dependency_type": "Project -> SourceFile"},
        ],
        "configuration": [], "flow_summary": {"total_flows": 5, "flows_with_confirmed_terminal": 3,
                                              "flows_with_unresolved_boundary": 1},
        "webforms": [], "external_dependencies": [],
    }


def _model(source: dict | None = None):
    return AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source or _source())


def _module(model, path: str):
    return next(m for m in model.modules if m.values["path"] == path)


def _module_doc(result, path: str) -> str:
    slug = _module(_model(), path).slug
    return (result.output_dir / "developer" / "modules" / f"{slug}.md").read_text(encoding="utf-8")


class OwnershipVsParticipationTests(unittest.TestCase):
    def test_project_owns_only_screens_whose_evidence_names_it(self) -> None:
        model = _model()
        web, bl = _module(model, WEB), _module(model, BL)
        self.assertEqual(web.values["screens"], 4)  # f0, f1, f2, f4
        self.assertEqual(bl.values["screens"], 0)
        self.assertEqual(bl.values["events"], 0)
        self.assertEqual(bl.slots["entry_points"], [])

    def test_flows_that_only_arrive_are_incoming_not_owned(self) -> None:
        model = _model()
        bl, sys_ = _module(model, BL), _module(model, SYS)
        self.assertEqual(bl.values["flows"], 0)
        self.assertEqual(bl.values["incoming_flows"], 3)  # f0 and f1 from WebA, f3 from an unknown origin
        origins = {i.values["origin"] for i in bl.slots["incoming_summary"]}
        self.assertEqual(origins, {"WebA (WebA.vbproj)", "(origen no identificado)"})
        self.assertEqual(sys_.values["incoming_flows"], 1)

    def test_originated_and_incoming_flows_are_different_slots(self) -> None:
        model = _model()
        web = _module(model, WEB)
        self.assertEqual(web.values["flows"], 5 - 1)  # f3 has an unknown origin
        self.assertEqual(web.values["incoming_flows"], 0)
        self.assertEqual({i.values["state"] for i in web.slots["flows"]}, {"real", "transaction", "unresolved", "dead_end"})

    def test_unknown_origin_screens_are_not_attributed_to_the_first_project_in_the_sequence(self) -> None:
        model = _model()
        unassigned = _module(model, "")
        self.assertEqual(unassigned.values["flows"], 1)
        self.assertEqual(unassigned.values["screens"], 1)
        self.assertIn("gap.flows_without_project", model.gaps)

    def test_module_document_separates_owned_from_arriving(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            bl = _module_doc(result, BL)
        self.assertIn("## Flujos que llegan aquí", bl)
        self.assertIn("no pertenecen a este proyecto", bl)
        self.assertIn("Este proyecto no tiene puntos de entrada propios.", bl)
        self.assertIn("No se inician flujos en este proyecto.", bl)


class DirectVsIndirectDataTests(unittest.TestCase):
    def test_web_project_has_no_direct_access_but_reaches_data_indirectly(self) -> None:
        model = _model()
        web = _module(model, WEB)
        self.assertEqual(web.values["data_ops"], 0)
        self.assertEqual([(i.values["target"], i.values["flows"]) for i in web.slots["indirect_targets"]], [("PKG_X.PROC_A", 1)])

    def test_owner_project_of_the_operation_has_direct_access_and_no_indirect_entry(self) -> None:
        model = _model()
        sys_ = _module(model, SYS)
        self.assertEqual(sys_.values["data_ops"], 1)
        self.assertEqual(sys_.slots["indirect_targets"], [])

    def test_document_states_none_direct_and_lists_indirect_without_contradiction(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            web = _module_doc(result, WEB)
        self.assertIn("Acceso directo a datos: ninguno.", web)
        self.assertIn("## Datos alcanzados indirectamente", web)
        self.assertIn("PKG_X.PROC_A", web)


class HonestDataMetricTests(unittest.TestCase):
    def test_transaction_only_flows_are_not_real_data_access(self) -> None:
        model = _model()
        self.assertEqual(model.system["real_flows"], 2)   # f0 and f3
        self.assertEqual(model.system["infra_flows"], 1)  # f1 only BeginTrans/Commit
        self.assertEqual(model.system["percent"], 40.0)

    def test_transaction_flow_shows_no_identified_result_and_its_own_state(self) -> None:
        web = _module(_model(), WEB)
        transactional = [i for i in web.slots["flows"] if i.values["state"] == "transaction"]
        self.assertEqual(len(transactional), 1)
        self.assertEqual(transactional[0].values["terminal"], "")
        self.assertNotIn("(transaction)", json.dumps([i.values for i in web.slots["flows"]]))

    def test_overview_separates_real_data_from_transaction_control(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            text = (result.output_dir / "general" / "README.md").read_text(encoding="utf-8")
        self.assertIn("2 (40.0%) llegan a una operación real de datos", text)
        self.assertIn("otros 1 llegan solo a operaciones de control de transacciones", text)

    def test_metric_comes_from_policy_not_a_hardcoded_kind(self) -> None:
        """A policy that does not declare transaction control as non-data counts it as data."""
        with tempfile.TemporaryDirectory() as custom:
            policy = json.loads((DEFAULTS_DIR / "noise" / "default.json").read_text(encoding="utf-8"))
            policy["categories"]["transaction_control"].pop("counts_as_data_access")
            (Path(custom) / "noise").mkdir()
            (Path(custom) / "noise" / "default.json").write_text(json.dumps(policy), encoding="utf-8")
            model = AudienceTransformer(ConfigRegistry(custom).noise_policy("default")).transform(_source())
        self.assertEqual(model.system["real_flows"], 3)


class DependencyClassificationTests(unittest.TestCase):
    def test_internal_platform_and_unclassified_are_not_mixed(self) -> None:
        model = _model()
        names = {key: [i.values["name"] for i in model.slots[key]]
                 for key in ("internal_libraries", "platform_libraries", "unclassified_libraries")}
        self.assertEqual(names["internal_libraries"], ["blA"])
        self.assertEqual(names["platform_libraries"], ["System.Data"])
        self.assertEqual(names["unclassified_libraries"], ["ThirdPartyGrid"])
        self.assertIn("gap.third_party_unclassified", model.gaps)

    def test_module_libraries_carry_a_class_and_the_document_names_it(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            dev = _module_doc(result, WEB)
            external = (result.output_dir / "general" / "external-systems.md").read_text(encoding="utf-8")
        self.assertIn("Dependencia no clasificada", dev)
        self.assertIn("Biblioteca interna del repositorio", dev)
        self.assertIn("## Dependencias no clasificadas", external)
        self.assertIn("## Bibliotecas internas compartidas", external)
        self.assertIn("no se afirma su existencia ni su ausencia", external)  # external services are never invented


class DuplicateProjectNameTests(unittest.TestCase):
    def test_duplicate_visible_names_include_their_path(self) -> None:
        model = _model()
        names = {m.values["path"]: m.values["name"] for m in model.modules if m.values["path"]}
        self.assertEqual(names[WEB], f"WebA ({WEB})")
        self.assertEqual(names[BACKUP], f"WebA ({BACKUP})")
        self.assertEqual(names[BL], "blA")  # unique names stay clean

    def test_file_suffix_never_becomes_a_visible_name(self) -> None:
        model = _model()
        for module in model.modules:
            self.assertNotRegex(module.values["name"], r"-\d+$")
        self.assertTrue(any(m.slug.endswith("-2") for m in model.modules))  # the suffix only lives in the file name

    def test_backup_path_is_declared_as_a_possible_copy_without_picking_production(self) -> None:
        model = _model()
        self.assertEqual(_module(model, BACKUP).values["copy_marker"], "Backup")
        self.assertEqual(_module(model, WEB).values["copy_marker"], "")
        self.assertIn("gap.project_copies", model.gaps)


class TerminologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.result = generate_documentation_v52(_source(), cls._tmp.name)
        cls.general = "\n".join(p.read_text(encoding="utf-8") for p in sorted((cls.result.output_dir / "general").rglob("*.md")))
        cls.developer = "\n".join(p.read_text(encoding="utf-8") for p in sorted((cls.result.output_dir / "developer").rglob("*.md")))
        cls.root = (cls.result.output_dir / "README.md").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_no_raw_technical_values_where_a_label_exists(self) -> None:
        for raw in RAW_TECHNICAL:
            self.assertNotIn(raw, self.general)
            self.assertNotIn(raw, self.developer)
        self.assertIn("Procedimiento almacenado", self.developer)

    def test_general_documents_drop_product_and_engine_jargon(self) -> None:
        for text in (self.general, self.root):
            for jargon in ("LegacyMapper", "evidencia estática", "INTERPRETED", "destino confirmado", "Destino confirmado"):
                self.assertNotIn(jargon, text)
        self.assertNotIn("LegacyMapper", self.developer)
        self.assertIn("Resultado identificado", self.developer)

    def test_module_word_is_defined_as_dotnet_project(self) -> None:
        self.assertIn("«módulo» significa «proyecto .NET (.vbproj / .csproj)»", self.general)
        self.assertIn("Una **solución**", self.general)
        self.assertIn("Un **proyecto**", self.general)

    def test_overview_explains_structure_beyond_an_inventory(self) -> None:
        for heading in ("## Qué se analizó", "## Cómo está organizado", "## Cómo se comunican los proyectos",
                        "## Recorridos observados", "## Acceso a datos", "## Dependencias externas", "## Qué no pudo determinarse"):
            self.assertIn(heading, self.general)

    def test_no_internal_ids_reach_the_new_documents(self) -> None:
        text = self.general + self.developer + self.root
        self.assertIsNone(re.search(r"\b(?:FLOW|DAO|EP|UNRES|PATH)-[0-9a-zA-Z]{6,}\b", text))


class NoisePolicyDataTests(unittest.TestCase):
    def test_databind_is_hidden_from_body_but_kept_in_detail(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(), out)
            body = _module_doc(result, WEB)
            detail_dir = result.output_dir / "developer" / "modules"
            detail = "\n".join(p.read_text(encoding="utf-8") for p in detail_dir.rglob("detail*.md"))
        unresolved = body.split("## Información no resuelta")[1]
        self.assertNotIn("DataBind", unresolved)
        self.assertIn("Foo.Bar", unresolved)
        self.assertIn("Se omiten del cuerpo 1 elementos", unresolved)
        self.assertIn("DataBind", detail)

    def test_new_category_is_declared_in_data_not_code(self) -> None:
        policy = ConfigRegistry().noise_policy("default")
        self.assertEqual(policy.classify(name="DataBind"), "ui_control_calls")
        self.assertEqual(policy.visibility("ui_control_calls"), "hide")
        self.assertFalse(policy.counts_as_data_access("transaction_control"))
        self.assertTrue(policy.counts_as_data_access(None))
        self.assertEqual(policy.dependency_class("platform_library"), "platform")


class RunSummaryLocationTests(unittest.TestCase):
    def test_documentation_v52_listed_when_documentation_stage_succeeds(self) -> None:
        result = RunResult(command="full", status=RunStatus.SUCCESS,
                           stages=(StageResult(stage=StageId.DOCUMENTATION, status=StageStatus.SUCCESS),))
        self.assertIn("documentation_v52", compute_output_locations(result))

    def test_documentation_v52_not_listed_when_the_stage_did_not_succeed(self) -> None:
        failed = RunResult(command="full", status=RunStatus.FAILED,
                           stages=(StageResult(stage=StageId.DOCUMENTATION, status=StageStatus.FAILED),))
        self.assertNotIn("documentation_v52", compute_output_locations(failed))
        self.assertEqual(compute_output_locations(RunResult(command="full", status=RunStatus.FAILED)), [])


class LegacyAndDeterminismTests(unittest.TestCase):
    def test_same_input_same_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = generate_documentation_v52(_source(), a)
            second = generate_documentation_v52(copy.deepcopy(_source()), b)
            self.assertEqual(first.files, second.files)
            for name in first.files:
                self.assertEqual((first.output_dir / name).read_bytes(), (second.output_dir / name).read_bytes())

    def test_legacy_documentation_directory_stays_intact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "documentation"
            legacy.mkdir()
            (legacy / "X.md").write_text("keep", encoding="utf-8")
            generate_documentation_v52(_source(), tmp)
            self.assertEqual([p.name for p in legacy.iterdir()], ["X.md"])
            self.assertEqual((legacy / "X.md").read_text(encoding="utf-8"), "keep")
            self.assertTrue((Path(tmp) / OUTPUT_DIRNAME / "README.md").is_file())

    def test_transformer_does_not_mutate_the_evidence(self) -> None:
        source = _source()
        snapshot = json.dumps(source, sort_keys=True)
        _model(source)
        self.assertEqual(json.dumps(source, sort_keys=True), snapshot)


if __name__ == "__main__":
    unittest.main()
