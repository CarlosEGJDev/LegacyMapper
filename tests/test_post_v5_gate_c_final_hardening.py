"""Post-V5 pre-H5 Gate C: cross-project call resolution (DT-04), template independence (DT-07), consumer-CLI decision (UX-03) and the
final dependency/exception sweep. Directed tests; no provider is ever resolved or called."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.adapters.vbnet_webforms_oracle.analysis.call_resolver import CallResolver
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.main import main as cli_main

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "legacy_documenter"


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def proj(root_ns: str, compile_items: list[str], refs: list[tuple[str, str]] = (), dlls: list[str] = (), content: list[str] = ()) -> str:
    items = "".join(f'<Compile Include="{c}" />' for c in compile_items) + "".join(f'<Content Include="{c}" />' for c in content)
    refs_xml = "".join(f'<ProjectReference Include="{inc}"><Name>{name}</Name></ProjectReference>' for inc, name in refs)
    dll_xml = "".join(f'<Reference Include="{d}"><HintPath>dll\\{d}.dll</HintPath></Reference>' for d in dlls)
    return (f"<Project><PropertyGroup><RootNamespace>{root_ns}</RootNamespace></PropertyGroup>"
            f"<ItemGroup>{items}{refs_xml}{dll_xml}</ItemGroup></Project>")


WEB_VB = """Imports Acme.Bl
Partial Public Class Home
    Inherits System.Web.UI.Page

    Protected Sub btnSave_Click(ByVal sender As Object, ByVal e As System.EventArgs)
        Dim svc As New CustomerService()
        svc.Save(1)
        svc.Save(1, 2)
        svc.Load(7)
        Dim fq As New Acme.Dal.Helper()
        fq.Touch()
        Dim helper As New Helper()
        helper.Touch()
        Dim shared As New Audit()
        shared.Run()
        Dim repo As ICustomerRepository
        repo.Persist(1)
        Dim mail As New Vendor.Lib.Mailer()
        mail.Send("x")
        Dim ghost As New Missing.Thing.Service()
        ghost.Do()
        Dim other As New OtherService()
        other.Run()
    End Sub
End Class
"""
BL_VB = """    Public Class CustomerService
        Public Sub Save(ByVal id As Integer)
            Dim dao As New CustomerDao()
            dao.Persist(id)
        End Sub
        Public Sub Save(ByVal id As Integer, ByVal mode As Integer)
            Dim dao As New CustomerDao()
            dao.Persist(id)
        End Sub
        Public Sub Load(ByVal id As Integer)
        End Sub
        Public Sub Load(ByVal id As String)
        End Sub
    End Class
    Public Class Helper
        Public Sub Touch()
        End Sub
    End Class
"""
DAL_VB = """    Public Class CustomerDao
        Public Sub Persist(ByVal id As Integer)
            Dim conn As New OracleConnection()
            Dim cmd As New OracleCommand("PKG_CUSTOMER.SAVE_CUSTOMER", conn)
            cmd.CommandType = CommandType.StoredProcedure
            cmd.ExecuteNonQuery()
        End Sub
    End Class
    Public Class Helper
        Public Sub Touch()
        End Sub
    End Class
    Public Class Audit
        Public Sub Run()
        End Sub
    End Class
    Public Interface ICustomerRepository
        Sub Persist(ByVal id As Integer)
    End Interface
    Public Class OracleRepo
        Implements ICustomerRepository
        Public Sub Persist(ByVal id As Integer)
        End Sub
    End Class
    Public Class FileRepo
        Implements ICustomerRepository
        Public Sub Persist(ByVal id As Integer)
        End Sub
    End Class
"""
DAL2_VB = """    Public Class Audit
        Public Sub Run()
        End Sub
    End Class
"""
OTHER_VB = """    Public Class CustomerService
        Public Sub Save(ByVal id As Integer)
        End Sub
    End Class
    Public Class OtherService
        Public Sub Run()
        End Sub
    End Class
"""
SLN = """Microsoft Visual Studio Solution File, Format Version 12.00
Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "Web", "Web\\Web.vbproj", "{11111111-1111-1111-1111-111111111111}"
EndProject
Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "Bl", "Bl\\Bl.vbproj", "{22222222-2222-2222-2222-222222222222}"
EndProject
Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "Dal", "Dal\\Dal.vbproj", "{33333333-3333-3333-3333-333333333333}"
EndProject
Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "Other", "Other\\Other.vbproj", "{44444444-4444-4444-4444-444444444444}"
EndProject
Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "Dal2", "Dal2\\Dal2.vbproj", "{55555555-5555-5555-5555-555555555555}"
EndProject
"""


def make_solution(parent: Path, name: str = "repo") -> Path:
    repo = parent / name
    for folder in ("Web", "Bl", "Dal", "Dal2", "Other"):
        (repo / folder).mkdir(parents=True)
    (repo / "Acme.sln").write_text(SLN, encoding="utf-8")
    (repo / "Web" / "Web.vbproj").write_text(
        proj("Acme.Web", ["Home.aspx.vb"], [("..\\Bl\\Bl.vbproj", "Bl"), ("..\\Dal\\Dal.vbproj", "Dal"), ("..\\Dal2\\Dal2.vbproj", "Dal2")], ["Vendor.Lib"], ["Home.aspx"]), encoding="utf-8")
    (repo / "Bl" / "Bl.vbproj").write_text(proj("Acme.Bl", ["Bl.vb"], [("..\\Dal\\Dal.vbproj", "Dal")]), encoding="utf-8")
    (repo / "Dal" / "Dal.vbproj").write_text(proj("Acme.Dal", ["Dal.vb"]), encoding="utf-8")
    (repo / "Other" / "Other.vbproj").write_text(proj("Other.Bl", ["Other.vb"]), encoding="utf-8")
    (repo / "Web" / "Home.aspx").write_text(
        '<%@ Page Language="VB" CodeBehind="Home.aspx.vb" Inherits="Acme.Web.Home" %>\n'
        '<asp:Button ID="btnSave" runat="server" OnClick="btnSave_Click" Text="Save" />\n', encoding="utf-8")
    (repo / "Web" / "Home.aspx.vb").write_text(WEB_VB, encoding="utf-8")
    (repo / "Bl" / "Bl.vb").write_text(BL_VB, encoding="utf-8")
    (repo / "Dal" / "Dal.vb").write_text(DAL_VB, encoding="utf-8")
    (repo / "Other" / "Other.vb").write_text(OTHER_VB, encoding="utf-8")
    (repo / "Dal2" / "Dal2.vbproj").write_text(proj("Acme.Dal2", ["Dal2.vb"]), encoding="utf-8")
    (repo / "Dal2" / "Dal2.vb").write_text(DAL2_VB, encoding="utf-8")
    return repo


class GateCBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gatec_"))
        cls.repo = make_solution(cls.tmp)
        cls.baseline = cls.tmp / "baseline"
        assert quiet(run_full_pipeline, cls.repo, cls.baseline, [], 12).status.value == "SUCCESS"
        cls.records = json.loads((cls.baseline / "evidence" / "cross_project_calls.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((cls.baseline / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
        cls.calls = [c for g in json.loads((cls.baseline / "index" / "calls.json").read_text(encoding="utf-8")) for c in g["calls"]]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def call(self, expression: str, cls_name: str = "Home") -> dict:
        return next(c for c in self.calls if c["expression"].startswith(expression) and c["containing_class"] == cls_name)

    def record(self, expression: str) -> dict:
        return next(r for r in self.records if r["expression"].startswith(expression))


class ParameterExtractionTests(unittest.TestCase):
    def test_declared_parameters_are_extracted(self):
        params = VBNetExtractor._parameters("(ByVal a As String, Optional ByRef b As Integer = 0, ParamArray c() As Object) As Integer")
        self.assertEqual([(p["name"], p["type"], p["passing"], p["optional"], p["param_array"]) for p in params],
                         [("a", "String", "ByVal", False, False), ("b", "Integer", "ByRef", True, False), ("c", "Object", "ByVal", False, True)])
        self.assertEqual(VBNetExtractor._parameters("()"), [])


class CrossProjectResolutionTests(GateCBase):
    def test_same_class_name_in_two_projects_resolves_only_through_the_project_reference_graph(self):
        call = self.call("svc.Save(1)")
        self.assertEqual(call["confidence"], "confirmed")
        self.assertEqual(call["resolved_target"], "Acme.Bl.CustomerService.save")
        self.assertTrue(call["resolved_project"].endswith("Bl.vbproj"))
        record = self.record("svc.Save(1)")
        self.assertIn("reference_and_namespace", record["resolution_basis"])
        self.assertEqual(record["candidate_count"], 2)                       # Other.Bl.CustomerService is not referenced: never chosen

    def test_overloads_are_disambiguated_by_declared_arity_and_never_by_name(self):
        self.assertEqual(self.record("svc.Save(1, 2)")["resolution_basis"].split("+")[-1], "overload_arity")
        self.assertEqual(self.call("svc.Save(1, 2)")["confidence"], "confirmed")

    def test_same_arity_overloads_stay_ambiguous(self):
        rec = self.record("svc.Load(7)")
        self.assertEqual((rec["status"], rec["resolution_code"]), ("UNRESOLVED", "UNRESOLVED_AMBIGUOUS_CALL"))
        self.assertEqual(self.call("svc.Load(7)")["confidence"], "unresolved")
        self.assertIsNone(self.call("svc.Load(7)").get("resolved_target"))

    def test_fully_qualified_type_wins_without_imports(self):
        rec = self.record("fq.Touch")
        self.assertEqual((rec["status"], rec["target_symbol"]), ("CONFIRMED", "Acme.Dal.Helper.touch"))
        self.assertIn(rec["resolution_basis"], ("unique_declaring_type", "fully_qualified_symbol+declared_type_member"))

    def test_imported_namespace_disambiguates_two_reachable_candidates(self):
        rec = self.record("helper.Touch")
        self.assertEqual((rec["status"], rec["target_symbol"]), ("CONFIRMED", "Acme.Bl.Helper.touch"))

    def test_two_reachable_candidates_without_namespace_evidence_stay_ambiguous(self):
        rec = self.record("shared.Run")
        self.assertEqual((rec["status"], rec["resolution_code"]), ("UNRESOLVED", "UNRESOLVED_AMBIGUOUS_CALL"))
        self.assertEqual(rec["candidate_count"], 2)
        self.assertIsNone(rec["target_project"])

    def test_interface_dispatch_with_several_implementers_is_dynamic(self):
        rec = self.record("repo.Persist")
        self.assertEqual((rec["status"], rec["resolution_code"]), ("UNRESOLVED", "UNRESOLVED_DYNAMIC_DISPATCH"))
        self.assertEqual(rec["candidate_count"], 2)
        self.assertEqual(rec["declared_target"], "Acme.Dal.ICustomerRepository.persist")

    def test_referenced_assembly_without_source_is_an_external_boundary(self):
        rec = self.record("mail.Send")
        self.assertEqual((rec["status"], rec["resolution_code"]), ("UNRESOLVED", "EXTERNAL_ASSEMBLY_BOUNDARY"))
        self.assertEqual(rec["external"]["assemblies"], ["vendor.lib"])
        self.assertEqual(rec["external"]["known_symbol"], "Vendor.Lib.Mailer.Send")

    def test_unreferenced_project_and_unknown_namespace_are_never_guessed(self):
        self.assertFalse([r for r in self.records if r["expression"].startswith("ghost.Do") and r["status"] != "UNRESOLVED"])
        rec = self.record("other.Run")      # unique global type, but the Web project does not reference Other: flagged, not silently trusted
        self.assertEqual((rec["status"], rec["resolution_code"]), ("INFERRED", "INFERRED_UNREFERENCED_PROJECT"))

    def test_resolved_cross_project_route_continues_to_the_existing_database_resolver(self):
        flows = json.loads((self.baseline / "index" / "functional_flows.json").read_text(encoding="utf-8"))
        paths = json.loads((self.baseline / "index" / "functional_paths.json").read_text(encoding="utf-8"))
        reaching = [p for p in paths if p.get("terminal_type") == "stored_procedure" and "SAVE_CUSTOMER" in json.dumps(p).upper()]
        self.assertTrue(reaching, "Web -> Bl -> Dal -> stored procedure must be reachable")
        self.assertTrue(any(p["confidence"] == "confirmed" for p in reaching))
        self.assertTrue(flows)

    def test_records_are_evidence_with_provenance_and_manifest_declares_the_partition(self):
        self.assertIn("cross_project_calls", self.manifest["partition_sha256"])
        self.assertEqual(self.manifest["cross_project_evidence_schema_version"], "1.0")
        source_ids = {a["id"] for a in json.loads((self.baseline / "evidence" / "source_artifacts.json").read_text(encoding="utf-8"))}
        for rec in self.records:
            self.assertIn(rec["status"], ("CONFIRMED", "INFERRED", "UNRESOLVED"))
            self.assertTrue(rec["source_refs"] and set(rec["source_refs"]) <= source_ids)
            for key in ("source_symbol", "source_project", "resolution_basis", "candidate_count"):
                self.assertIn(key, rec)

    def test_resolution_is_deterministic(self):
        again = self.tmp / "again"
        again_repo = make_solution(self.tmp, "repo2")
        self.assertEqual(quiet(run_full_pipeline, again_repo, again, [], 12).status.value, "SUCCESS")
        other = json.loads((again / "evidence" / "cross_project_calls.json").read_text(encoding="utf-8"))
        self.assertEqual(other, self.records)


class SourceOfflineTests(GateCBase):
    def test_persisted_relationships_survive_source_removal_and_feed_downstream(self):
        moved = self.tmp / "repo.removed"
        self.repo.rename(moved)
        try:
            with mock.patch("legacy_documenter.scanner.repository_scanner.RepositoryScanner.scan") as scan, \
                    mock.patch("legacy_documenter.cli.pipeline_stages.extract_repository") as extract:
                codes = {name: quiet(cli_main, [name, str(self.baseline), "--output", str(self.tmp / f"out_{name}")]) for name in ("docs", "visuals", "deliver")}
            self.assertEqual(codes, {"docs": 0, "visuals": 0, "deliver": 0})
            scan.assert_not_called()
            extract.assert_not_called()
            records = json.loads((self.baseline / "evidence" / "cross_project_calls.json").read_text(encoding="utf-8"))
            self.assertEqual(records, self.records)
        finally:
            moved.rename(self.repo)


def _claims(node, out=None):
    """Every {text, status, source_refs} claim dict of a serialized behavioral document."""
    out = [] if out is None else out
    if isinstance(node, dict):
        if {"text", "status", "source_refs"} <= set(node):
            out.append((node["text"], node["status"], tuple(node["source_refs"])))
        for v in node.values():
            _claims(v, out)
    elif isinstance(node, list):
        for v in node:
            _claims(v, out)
    return out


class TemplateIndependenceTests(GateCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from legacy_documenter.behavior.prototype import build, write_package
        from legacy_documenter.behavior.template import discover
        cls.doc, cls.bc, cls.violations, cls.explained = build(cls.baseline, None, project="Web", solution="Acme", pilot_count=2)
        cls.out = {}
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider:
            for name in ("human/default", "human/executive"):
                target = cls.tmp / ("out_" + name.split("/")[1])
                write_package(cls.doc, target, cls.violations, make_pdf=False, template=discover(name), bc=cls.bc, explained=cls.explained)
                cls.out[name] = target
            cls.provider_calls = provider.call_count

    def test_second_template_uses_the_same_semantic_model_and_zero_provider_calls(self):
        self.assertEqual(self.provider_calls, 0)
        for name in ("explanations.json", "validation_report.json", "wireframe_models.json", "AI_INTERPRETATION_MANIFEST.json"):
            self.assertEqual((self.out["human/default"] / name).read_bytes(), (self.out["human/executive"] / name).read_bytes(), name)
        manifest = json.loads((self.out["human/executive"] / "TEMPLATE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["template_id"], "human/executive")
        self.assertEqual(manifest["provider_calls"], 0)

    def test_ai_context_carries_persisted_cross_project_facts(self):
        from legacy_documenter.behavior import ai as A
        home = next(v for v in self.explained.values() if v.name == "Home")
        context, scope = A.view_context(self.bc, home, {"solution": "Acme", "project": "Web", "path": self.bc.project_path, "refs": []})
        facts = [f for f in context["facts"] if f["kind"] == "cross_project_call"]
        self.assertTrue(any("UNRESOLVED_DYNAMIC_DISPATCH" in f["fact"] for f in facts) or any("UNRESOLVED" in f["fact"] for f in facts))
        for f in facts:
            self.assertIn(f["ref"], scope["allowed_refs"])

    def test_presentation_is_materially_different(self):
        a = (self.out["human/default"] / "index.html").read_text(encoding="utf-8")
        b = (self.out["human/executive"] / "index.html").read_text(encoding="utf-8")
        self.assertNotEqual(a, b)
        order = lambda html: [m for m in ("s-solution", "s-project", "s-important-views", "s-data", "s-view-chapters", "s-unresolved", "s-appendix") if m in html]
        self.assertEqual(order(b), ["s-solution", "s-project", "s-important-views", "s-data", "s-view-chapters", "s-unresolved", "s-appendix"])
        self.assertLess(b.index("s-view-chapters"), b.index("s-unresolved"))      # the short limitations note closes the executive reading
        self.assertLess(a.index("s-view-chapters"), a.index("s-unresolved"))

    def test_template_never_hides_unresolved_nor_promotes_statuses(self):
        import html
        text = (self.out["human/executive"] / "index.html").read_text(encoding="utf-8")
        claims = _claims(json.loads((self.out["human/default"] / "explanations.json").read_text(encoding="utf-8")))
        unresolved = [c for c in claims if c[1] == "UNRESOLVED" and c[0]]
        self.assertTrue(unresolved)
        # H4 noise polish: the executive reading carries a short «Limitaciones conocidas» note (2-4 bullets, no call tables); the full
        # UNRESOLVED claims stay in the shared semantic model (byte-identical explanations.json for every template) and in ai/unresolved.json
        section = text[text.index('id="s-unresolved"'):text.index('id="s-appendix"')]
        self.assertIn("Limitaciones conocidas", section)
        self.assertLessEqual(section.count("<li>"), 4)
        self.assertNotIn("<table", section)
        self.assertEqual((self.out["human/default"] / "explanations.json").read_bytes(), (self.out["human/executive"] / "explanations.json").read_bytes())
        default_text = (self.out["human/default"] / "index.html").read_text(encoding="utf-8")
        for status in ("AI_INTERPRETATION", "CANONICAL"):
            self.assertEqual(status in text, status in default_text)       # a template cannot introduce or promote a status

    def test_a_template_that_removes_unresolved_or_actions_is_rejected(self):
        from legacy_documenter.behavior.template import TemplateError, discover
        base = PACKAGE / "templates" / "human" / "executive"
        for label, old, new in (("no_unresolved", "  - unresolved\n", ""), ("no_actions", "  - actions\n", "")):
            root = self.tmp / "tpl" / label
            tdir = root / "human" / "bad"
            shutil.copytree(base, tdir)
            yaml = (tdir / "template.yaml").read_text(encoding="utf-8").replace("human/executive", "human/bad")
            self.assertIn(old, yaml)
            (tdir / "template.yaml").write_text(yaml.replace(old, new, 1), encoding="utf-8")
            with self.assertRaises(TemplateError):
                discover("human/bad", str(root))


class ConsumerCliDecisionTests(unittest.TestCase):
    def test_ux03_is_an_explicit_deferred_decision_and_h5_does_not_depend_on_it(self):
        from legacy_documenter.cli import parser as cli_parser
        text = Path(cli_parser.__file__).read_text(encoding="utf-8")
        self.assertNotIn('add_parser("consumer"', text)                     # deferred (FUTURE_CAPABILITY): no public consumer CLI exists
        for module in ("docs_command.py", "visuals_command.py", "deliver_command.py", "interpret_command.py"):
            self.assertNotIn("legacy_documenter.consumers", (PACKAGE / "cli" / module).read_text(encoding="utf-8"), module)
        result = (REPO / "docs" / "POST_V5" / "PRE_H5_GATE_C_FINAL_HARDENING_RESULT.md")
        if result.is_file():
            body = result.read_text(encoding="utf-8")
            self.assertIn("UX-03", body)
            self.assertIn("FUTURE_CAPABILITY", body)


class SelfCheckSweepTests(unittest.TestCase):
    def test_new_resolver_has_no_io_and_no_broad_exception_handlers(self):
        path = PACKAGE / "adapters" / "vbnet_webforms_oracle" / "analysis" / "cross_project.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                self.fail("broad/unneeded exception handler in the cross-project resolver")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, {"read_text", "read_bytes", "open", "scandir", "listdir"})
        text = path.read_text(encoding="utf-8")
        for needle in ("C:\\", "/Users/", "COPILOT", "provider"):
            self.assertNotIn(needle, text)

    def test_unresolved_call_without_projects_graph_does_not_resolve_by_name(self):
        symbols = [
            {"name": "Svc", "kind": "class", "file": "a.vb", "effective_namespace": "A", "project_path": "a.vbproj",
             "members": [{"kind": "sub", "name": "Run", "parameters": []}], "inherits": [], "implements": []},
            {"name": "Svc", "kind": "class", "file": "b.vb", "effective_namespace": "B", "project_path": "b.vbproj",
             "members": [{"kind": "sub", "name": "Run", "parameters": []}], "inherits": [], "implements": []},
        ]
        groups = [{"file": "c.vb", "imports": [], "instantiations": [{"type_name": "Svc", "variable_name": "s", "containing_class": "C",
                                                                       "containing_method": "M", "evidence": {"file": "c.vb", "line": 1, "expression": "x"}}],
                   "calls": [{"expression": "s.Run()", "method_name": "Run", "receiver": "s", "receiver_path": "s", "arguments_count": 0,
                              "containing_class": "C", "containing_method": "M", "candidates": [], "evidence": {"file": "c.vb", "line": 2, "expression": "s.Run()"}}]}]
        out, _deps = CallResolver().resolve(groups, symbols, None)
        call = out[0]["calls"][0]
        self.assertEqual(call["confidence"], "unresolved")
        self.assertEqual(call["cross_project"]["code"], "UNRESOLVED_AMBIGUOUS_CALL")


if __name__ == "__main__":
    unittest.main()
