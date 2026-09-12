import tempfile
import unittest
from pathlib import Path

from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver
from legacy_documenter.extractors.solution_extractor import SolutionExtractor
from legacy_documenter.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.extractors.vbproj_extractor import VBProjExtractor
from legacy_documenter.extractors.webconfig_extractor import WebConfigExtractor
from legacy_documenter.extractors.webforms_extractor import WebFormsExtractor
from legacy_documenter.extractors.call_extractor import CallExtractor
from legacy_documenter.extractors.database_extractor import DatabaseExtractor
from legacy_documenter.main import analyze_repository
from legacy_documenter.scanner.repository_scanner import RepositoryScanner


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class V1Tests(unittest.TestCase):
    def test_repository_scanner(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App" / "Default.aspx", '<%@ Page Language="VB" %>')
            write(root / "bin" / "ignored.dll", "")
            files = RepositoryScanner().scan(root)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].file_type, "aspx")

    def test_solution_extractor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sln = write(root / "Sample.sln", 'Project("{TYPE}") = "Web", "Web\\Web.vbproj", "{PROJECT}"\nEndProject\n')
            result = SolutionExtractor().extract(sln, root)
            self.assertEqual(result["projects"][0]["name"], "Web")

    def test_vbproj_extractor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vbproj = write(root / "Web.vbproj", """<Project><PropertyGroup><AssemblyName>Web</AssemblyName><TargetFrameworkVersion>v4.0</TargetFrameworkVersion></PropertyGroup><ItemGroup><ProjectReference Include="BL.vbproj"><Name>BL</Name></ProjectReference><Reference Include="System.Web" /></ItemGroup><ItemGroup><Compile Include="A.vb" /><Content Include="A.aspx" /></ItemGroup></Project>""")
            project = VBProjExtractor().extract(vbproj, root)
            self.assertEqual(project.target_framework, "v4.0")
            self.assertEqual(project.project_references[0]["name"], "BL")
            self.assertIn("A.vb", project.compile_items)
            self.assertIn("A.aspx", project.content_items)

    def test_vbnet_extractor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "A.vb", """Namespace N
Public Interface IFoo
End Interface
Public Module M
End Module
Public Enum E
End Enum
Public Partial Class C
Inherits B
Implements IFoo
Public Property P As String
Public Function F() As String
End Function
Public Sub S()
End Sub
End Class
End Namespace""")
            symbols = VBNetExtractor().extract(vb, root)
            cls = next(item for item in symbols if item.name == "C")
            self.assertEqual(cls.namespace, "N")
            self.assertEqual(cls.inherits, ["B"])
            self.assertEqual(cls.implements, ["IFoo"])
            self.assertEqual({m["kind"] for m in cls.members}, {"property", "function", "sub"})

    def test_webforms_extractor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            aspx = write(root / "Default.aspx", '<%@ Page Language="VB" CodeBehind="Default.aspx.vb" Inherits="N.C" %><%@ Register Src="~/C.ascx" TagPrefix="uc" TagName="C" %><script src="/a.js"></script><link rel="stylesheet" href="/a.css" />')
            form = WebFormsExtractor().extract(aspx, root)
            self.assertEqual(form.codebehind, "Default.aspx.vb")
            self.assertEqual(form.registers[0]["Src"], "~/C.ascx")
            self.assertEqual(form.scripts, ["/a.js"])
            self.assertEqual(form.stylesheets, ["/a.css"])

    def test_webconfig_extractor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = write(root / "web.config", '<configuration><appSettings><add key="Mode" value="Prod" /></appSettings><connectionStrings><add name="Main" connectionString="User ID=scott;Password=tiger;Data Source=db" /></connectionStrings><system.web><compilation><assemblies><add assembly="System.Web" /></assemblies></compilation></system.web></configuration>')
            result = WebConfigExtractor().extract(config, root)
            self.assertIn("User ID=********", result["connectionStrings"][0]["connectionString"])
            self.assertIn("Password=********", result["connectionStrings"][0]["connectionString"])
            self.assertEqual(result["assemblies"][0]["assembly"], "System.Web")

    def test_dependency_resolver(self):
        deps = DependencyResolver().resolve(
            [],
            [{"path": "Web.vbproj", "project_references": [{"include": "BL.vbproj"}], "assembly_references": [], "compile_items": []}],
            [{"name": "C", "namespace": "N", "kind": "class", "file": "A.vb", "inherits": [], "implements": []}],
            [{"path": "A.aspx", "kind": "aspx", "codebehind": "A.aspx.vb", "inherits": "N.C", "registers": [{"Src": "~/C.ascx"}], "scripts": [], "stylesheets": []}],
        )
        self.assertIn("Project -> Project", {d.dependency_type for d in deps})
        self.assertIn("WebForm -> VBClass", {d.dependency_type for d in deps})

    def test_integration(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            repo = base / "repo"
            write(repo / "Sample.sln", 'Project("{TYPE}") = "Web", "Web\\Web.vbproj", "{PROJECT}"\nEndProject\n')
            write(repo / "Web" / "Web.vbproj", '<Project><PropertyGroup><AssemblyName>Web</AssemblyName><TargetFrameworkVersion>v4.0</TargetFrameworkVersion></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(repo / "Web" / "Default.aspx", '<%@ Page Language="VB" CodeBehind="Default.aspx.vb" Inherits="Company.Web.CustomerPage" %>')
            write(repo / "Web" / "Default.aspx.vb", "Namespace Company.Web\nPublic Class CustomerPage\nEnd Class\nEnd Namespace\n")
            output = base / "out"
            indexes = analyze_repository(repo, output)
            self.assertEqual(indexes["repository"]["stats"]["total_files"], 4)
            self.assertTrue((output / "index" / "dependencies.json").exists())

    def test_r1_01_webforms_attributes_are_case_insensitive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            variants = [
                ("A.aspx", "CodeBehind", "Inherits", "Src", "Namespace", "Assembly"),
                ("B.aspx", "Codebehind", "inherits", "src", "namespace", "assembly"),
                ("C.aspx", "codebehind", "INHERITS", "SRC", "NAMESPACE", "ASSEMBLY"),
            ]
            for file_name, codebehind, inherits, src, namespace, assembly in variants:
                form_path = write(
                    root / file_name,
                    f'<%@ Page {codebehind}="Page.aspx.vb" {inherits}="N.Page" %>'
                    f'<%@ Register {src}="~/Controls/C.ascx" TagPrefix="uc" TagName="C" %>'
                    f'<%@ Register {namespace}="N.Controls" {assembly}="N.Web" TagPrefix="cc" %>',
                )
                form = WebFormsExtractor().extract(form_path, root)
                self.assertEqual(form.codebehind, "Page.aspx.vb")
                self.assertEqual(form.inherits, "N.Page")
                deps = DependencyResolver().resolve([], [], [], [form.to_dict()])
                targets = {dep.target for dep in deps}
                self.assertIn("~/Controls/C.ascx", targets)
                self.assertIn("N.Controls,N.Web", targets)

    def test_r1_02_scanner_ignores_vti_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Real.vbproj", "<Project />")
            write(root / "_vti_cnf" / "Real.vbproj", "not xml")
            output = root / "out"
            indexes = analyze_repository(root, output)
            self.assertEqual(indexes["repository"]["stats"]["vb_project"], 1)
            self.assertEqual(indexes["errors"], [])
            self.assertIn("_vti_cnf", indexes["repository"]["ignored"])

    def test_r1_03_effective_namespace_uses_project_compile_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(
                root / "App.vbproj",
                '<Project><PropertyGroup><RootNamespace>Empresa.Modulo</RootNamespace></PropertyGroup>'
                '<ItemGroup><Compile Include="Cliente.vb" /><Compile Include="Cobranza.vb" /></ItemGroup></Project>',
            )
            write(root / "Cliente.vb", "Public Class Cliente\nEnd Class\n")
            write(root / "Cobranza.vb", "Namespace Cobranza\nPublic Class Cliente\nEnd Class\nEnd Namespace\n")
            write(root / "CercanoNoIncluido.vb", "Public Class Suelto\nEnd Class\n")
            indexes = analyze_repository(root, root / "out")
            by_file = {symbol["file"].replace("\\", "/"): symbol for symbol in indexes["symbols"]}
            self.assertEqual(by_file["Cliente.vb"]["root_namespace"], "Empresa.Modulo")
            self.assertEqual(by_file["Cliente.vb"]["effective_namespace"], "Empresa.Modulo")
            self.assertEqual(by_file["Cobranza.vb"]["declared_namespace"], "Cobranza")
            self.assertEqual(by_file["Cobranza.vb"]["effective_namespace"], "Empresa.Modulo.Cobranza")
            self.assertIsNone(by_file["CercanoNoIncluido.vb"]["root_namespace"])
            self.assertIsNone(by_file["CercanoNoIncluido.vb"]["effective_namespace"])

    def test_r1_04_partial_classes_are_consolidated_without_losing_physical_symbols(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(
                root / "Web.vbproj",
                '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup>'
                '<ItemGroup><Compile Include="Cliente.ascx.vb" /><Compile Include="Cliente.ascx.designer.vb" /></ItemGroup></Project>',
            )
            write(root / "Cliente.ascx.vb", "Partial Class Cliente\nEnd Class\n")
            write(root / "Cliente.ascx.designer.vb", "Partial Class Cliente\nEnd Class\n")
            write(root / "Cliente.ascx", '<%@ Control CodeBehind="Cliente.ascx.vb" Inherits="Empresa.Web.Cliente" %>')
            indexes = analyze_repository(root, root / "out")
            physical = [symbol for symbol in indexes["symbols"] if symbol["name"] == "Cliente"]
            self.assertEqual(len(physical), 2)
            logical = [symbol for symbol in indexes["logical_symbols"] if symbol["name"] == "Cliente"]
            self.assertEqual(len(logical), 1)
            self.assertEqual(len(logical[0]["parts"]), 2)

    def test_v2_r1_extracts_imports_instantiation_and_instance_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(
                root / "A.vb",
                """Imports Empresa.BL
Imports Repo = Empresa.Data.Repositorio
Public Class Page
Public Sub Run()
Dim servicio As New Servicio()
servicio.Procesar()
End Sub
End Class""",
            )
            result = CallExtractor().extract(vb, root)
            self.assertEqual(result["imports"][0]["name"], "Empresa.BL")
            self.assertEqual(result["imports"][1]["alias"], "Repo")
            self.assertEqual(result["instantiations"][0]["type_name"], "Servicio")
            self.assertEqual(result["instantiations"][0]["variable_name"], "servicio")
            self.assertEqual(result["calls"][0]["receiver"], "servicio")
            self.assertEqual(result["calls"][0]["method_name"], "Procesar")
            self.assertEqual(result["calls"][0]["containing_method"], "Run")

    def test_v2_r1_resolves_instance_shared_and_internal_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.vb" /><Compile Include="Servicio.vb" /></ItemGroup></Project>')
            write(
                root / "A.vb",
                """Public Class Page
Public Sub Run()
Dim servicio As New Servicio()
servicio.Procesar()
Servicio.SharedProcesar()
Local()
End Sub
Public Sub Local()
End Sub
End Class""",
            )
            write(root / "Servicio.vb", "Public Class Servicio\nPublic Sub Procesar()\nEnd Sub\nPublic Shared Sub SharedProcesar()\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            resolved = [call for file_calls in indexes["calls"] for call in file_calls["calls"] if call["confidence"] == "confirmed"]
            targets = {call["resolved_target"] for call in resolved}
            self.assertIn("Empresa.Servicio.procesar", targets)
            self.assertIn("Empresa.Servicio.sharedprocesar", targets)
            self.assertIn("Empresa.Page.local", targets)
            dep_types = {dep["dependency_type"] for dep in indexes["functional_dependencies"]}
            self.assertIn("Method -> Method", dep_types)
            self.assertIn("Method -> InstantiatesClass", dep_types)
            self.assertIn("Class -> UsesClass", dep_types)

    def test_v2_r1_cross_project_call_keeps_project_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web" / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Page.vb" /></ItemGroup></Project>')
            write(root / "BL" / "BL.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.BL</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Servicio.vb" /></ItemGroup></Project>')
            write(root / "Web" / "Page.vb", "Public Class Page\nPublic Sub Run()\nDim svc As New Servicio()\nsvc.Procesar()\nEnd Sub\nEnd Class")
            write(root / "BL" / "Servicio.vb", "Public Class Servicio\nPublic Sub Procesar()\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            call = next(call for file_calls in indexes["calls"] for call in file_calls["calls"] if call["method_name"] == "Procesar")
            self.assertEqual(call["confidence"], "confirmed")
            self.assertEqual(call["resolved_project"].replace("\\", "/"), "BL/BL.vbproj")

    def test_v2_r1_ambiguous_call_is_not_confirmed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.vb" /><Compile Include="Uno.vb" /><Compile Include="Dos.vb" /></ItemGroup></Project>')
            write(root / "A.vb", "Public Class Page\nPublic Sub Run()\nDim x As New Servicio()\nx.Procesar()\nEnd Sub\nEnd Class")
            write(root / "Uno.vb", "Public Class Servicio\nPublic Sub Procesar()\nEnd Sub\nEnd Class")
            write(root / "Dos.vb", "Public Class Servicio\nPublic Sub Procesar()\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            call = next(call for file_calls in indexes["calls"] for call in file_calls["calls"] if call["method_name"] == "Procesar")
            self.assertEqual(call["confidence"], "unresolved")
            self.assertIsNone(call["resolved_target"])

    def test_v2_r1_1_filters_vb_intrinsics_before_call_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "A.vb", """Public Class Page
Public Sub Run()
If Not IsNothing(dbc) Then CStr(CInt(1))
Dim d = CDate("2020-01-01")
Dim x = IIf(True, Format(Now, "00"), DateAdd(DateInterval.Day, 1, Now))
Dim y = CType(obj, Object)
End Sub
End Class""")
            result = CallExtractor().extract(vb, root)
            self.assertEqual(result["calls"], [])

    def test_v2_r1_1_does_not_extract_calls_from_string_literals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "A.vb", """Public Class Page
Public Sub Run()
Dim script = "javascript:OnClickWindowOpen('x');"
Dim mixed = "NoCall()" & RealCall()
End Sub
Public Sub RealCall()
End Sub
End Class""")
            result = CallExtractor().extract(vb, root)
            self.assertEqual([call["method_name"] for call in result["calls"]], ["RealCall"])

    def test_v2_r1_1_ignores_indexed_default_property_access(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "A.vb", """Public Class Page
Public Sub Run()
Dim a = ds.Tables(0).Rows(0).Item("ID")
Dim b = Me.btn.Attributes("href")
Dim c = Session("ID_ADM")
RealCall()
End Sub
Public Sub RealCall()
End Sub
End Class""")
            result = CallExtractor().extract(vb, root)
            self.assertEqual([call["method_name"] for call in result["calls"]], ["RealCall"])

    def test_v2_r1_1_local_call_without_member_is_unresolved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.vb" /></ItemGroup></Project>')
            write(root / "A.vb", "Public Class Page\nPublic Sub Run()\nMissingLocal()\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            call = next(call for file_calls in indexes["calls"] for call in file_calls["calls"])
            self.assertEqual(call["confidence"], "unresolved")
            self.assertIsNone(call["resolved_target"])

    def test_v2_r1_1_deduplicates_functional_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.vb" /><Compile Include="Servicio.vb" /></ItemGroup></Project>')
            write(root / "A.vb", """Public Class Page
Public Sub Run()
Dim a As New Servicio()
Dim b As New Servicio()
End Sub
End Class""")
            write(root / "Servicio.vb", "Public Class Servicio\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            uses = [dep for dep in indexes["functional_dependencies"] if dep["dependency_type"] == "Class -> UsesClass"]
            self.assertEqual(len(uses), 1)
            self.assertEqual(uses[0]["evidence_count"], 2)

    def test_v2_r1_1_preserves_full_qualifier_for_fully_qualified_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "A.vb", """Public Class Page
Public Sub Run()
Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(2)
End Sub
End Class""")
            result = CallExtractor().extract(vb, root)
            self.assertEqual(len(result["calls"]), 1)
            self.assertEqual(result["calls"][0]["receiver"], "blADHds67")
            self.assertEqual(result["calls"][0]["receiver_path"], "Bl.ADHAdmCalculoDs67.blADHds67")
            self.assertEqual(result["calls"][0]["method_name"], "txtraerPereva")

    def test_v2_r2_handles_button_click_entry_point(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs) Handles btnBuscar.Click\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            entry = indexes["entry_points"][0]
            self.assertEqual(entry["webform"], "Default.aspx")
            self.assertEqual(entry["control"], "btnBuscar")
            self.assertEqual(entry["event"], "Click")
            self.assertEqual(entry["handler"], "btnBuscar_Click")
            self.assertEqual(entry["confidence"], "confirmed")

    def test_v2_r2_handles_me_and_mybase_load_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.aspx.vb" /><Compile Include="B.aspx.vb" /><Content Include="A.aspx" /><Content Include="B.aspx" /></ItemGroup></Project>')
            write(root / "A.aspx", '<%@ Page CodeBehind="A.aspx.vb" Inherits="Empresa.Web.APage" %>')
            write(root / "A.aspx.vb", "Public Class APage\nPrivate Sub Page_Load(sender As Object, e As EventArgs) Handles Me.Load\nEnd Sub\nEnd Class")
            write(root / "B.aspx", '<%@ Page CodeBehind="B.aspx.vb" Inherits="Empresa.Web.BPage" %>')
            write(root / "B.aspx.vb", "Public Class BPage\nPrivate Sub Page_Load(sender As Object, e As EventArgs) Handles MyBase.Load\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            controls = {entry["control"] for entry in indexes["entry_points"]}
            self.assertEqual(controls, {"Me", "MyBase"})
            self.assertEqual({entry["type"] for entry in indexes["entry_points"]}, {"web_lifecycle"})

    def test_v2_r2_multiple_handles_events(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub Guardar(sender As Object, e As EventArgs) Handles btnAceptar.Click, btnGuardar.Click\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual({entry["control"] for entry in indexes["entry_points"]}, {"btnAceptar", "btnGuardar"})

    def test_v2_r2_markup_onclick_and_generic_onevent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnBuscar" OnClick="btnBuscar_Click" runat="server" /><asp:DropDownList ID="ddl" OnSelectedIndexChanged="ddl_Changed" runat="server" />')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs)\nEnd Sub\nProtected Sub ddl_Changed(sender As Object, e As EventArgs)\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            events = {(entry["control"], entry["event"], entry["handler"], entry["confidence"]) for entry in indexes["entry_points"]}
            self.assertIn(("btnBuscar", "Click", "btnBuscar_Click", "confirmed"), events)
            self.assertIn(("ddl", "SelectedIndexChanged", "ddl_Changed", "confirmed"), events)

    def test_v2_r2_handler_entry_has_outgoing_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Compile Include="Servicio.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs) Handles btnBuscar.Click\nDim svc As New Servicio()\nsvc.Procesar()\nEnd Sub\nEnd Class")
            write(root / "Servicio.vb", "Public Class Servicio\nPublic Sub Procesar()\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            entry = indexes["entry_points"][0]
            self.assertEqual(entry["handler_method"], "DefaultPage.btnBuscar_Click")
            self.assertEqual(entry["outgoing_calls"][0]["method_name"], "Procesar")

    def test_v2_r2_handler_name_without_binding_is_not_entry_point(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs)\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(indexes["entry_points"], [])

    def test_v2_r2_missing_markup_handler_is_unresolved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnBuscar" OnClick="MissingHandler" runat="server" />')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(indexes["entry_points"][0]["confidence"], "unresolved")
            self.assertIsNone(indexes["entry_points"][0]["handler_method"])

    def test_v2_r2_javascript_string_is_not_event_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><script>var x="OnClick=\\"btnBuscar_Click\\"";</script>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs)\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(indexes["event_bindings"], [])

    def test_v2_r2_duplicate_event_binding_deduplicates_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnBuscar" OnClick="btnBuscar_Click" runat="server" />')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs) Handles btnBuscar.Click\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(len(indexes["entry_points"]), 1)
            event_edges = [dep for dep in indexes["functional_dependencies"] if dep["dependency_type"] == "WebForm -> Event"]
            self.assertEqual(len(event_edges), 1)
            self.assertEqual(event_edges[0]["evidence_count"], 2)

    def test_v2_r2_lifecycle_name_without_evidence_is_not_confirmed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub Page_Load(sender As Object, e As EventArgs)\nEnd Sub\nProtected Overrides Sub OnLoad(e As EventArgs)\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(len(indexes["entry_points"]), 1)
            self.assertEqual(indexes["entry_points"][0]["event"], "Load")
            self.assertEqual(indexes["entry_points"][0]["handler"], "OnLoad")

    def test_v2_r3_direct_oracle_stored_proc_execute_and_parameter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Data</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Repo.vb" /></ItemGroup></Project>')
            write(root / "Repo.vb", """Public Class Repo
Public Sub Save(id As Integer)
Dim conn As New OracleConnection(ConfigurationManager.ConnectionStrings("Main").ConnectionString)
Dim cmd As New OracleCommand("PKG_CLIENTE.SAVE", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.Parameters.Add("P_ID", OracleDbType.Int32).Value = id
cmd.ExecuteNonQuery()
End Sub
End Class""")
            indexes = analyze_repository(root, root / "out")
            self.assertIn("data_access", indexes)
            self.assertTrue(any(op["stored_procedure"] == "PKG_CLIENTE.SAVE" for op in indexes["data_access"]))
            self.assertTrue(any(param["name"] == "P_ID" for param in indexes["data_parameters"]))
            dep_types = {dep["dependency_type"] for dep in indexes["functional_dependencies"]}
            self.assertIn("Method -> DataAccessOperation", dep_types)
            self.assertIn("DataAccessOperation -> StoredProcedure", dep_types)

    def test_v2_r3_adapter_fill_and_static_sql_operations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Load()
Dim da As New OracleDataAdapter("SELECT * FROM CLIENTE", conn)
da.Fill(ds)
Dim cmd As New OracleCommand("MERGE INTO T USING S ON (T.ID=S.ID)", conn)
cmd.ExecuteScalar()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            sql = {op["sql_operation"] for op in result["operations"] if op["sql_operation"]}
            self.assertEqual(sql, {"SELECT", "MERGE"})
            self.assertTrue(any(op["operation_kind"] == "fill" for op in result["operations"]))

    def test_v2_r3_detects_dynamic_sql_conservatively(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Load(id As Integer)
Dim cmd As New OracleCommand()
cmd.CommandText = "UPDATE CLIENTE SET NOMBRE = " & nombre
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            op = next(item for item in result["operations"] if item["sql_operation"] == "UPDATE")
            self.assertTrue(op["dynamic_sql"])
            self.assertEqual(op["confidence"], "confirmed")

    def test_v2_r3_oraconn_execproc_transactions_and_wrapper_parameters(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim dbc As New OraConn()
dbc.BeginTrans()
dbc.ExecProc("PKG.PRC", "P_ID,P_NAME", id, name)
dbc.Commit()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(any(op["provider"] == "OraConn" and op["stored_procedure"] == "PKG.PRC" for op in result["operations"]))
            self.assertTrue(any(op["operation_kind"] == "transaction" and op["operation_kind"] for op in result["operations"]))
            self.assertEqual({param["name"] for param in result["parameters"]}, {"P_ID", "P_NAME"})

    def test_v2_r3_ignores_comments_strings_and_untyped_wrappers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Run()
' Dim cmd As New OracleCommand("DELETE FROM X", conn)
Dim s = "SELECT * FROM CLIENTE"
Dim x = "javascript:ExecProc(""PKG.BAD"")"
helper.ExecProc("PKG.BAD")
helper.Commit()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])
            self.assertEqual(result["parameters"], [])

    def test_v2_r3_deduplicates_data_access_dependencies_preserving_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Data</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Repo.vb" /></ItemGroup></Project>')
            write(root / "Repo.vb", """Public Class Repo
Public Sub Save()
Dim cmd As New OracleCommand("PKG.SAVE", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
cmd.ExecuteNonQuery()
End Sub
End Class""")
            indexes = analyze_repository(root, root / "out")
            edges = [dep for dep in indexes["functional_dependencies"] if dep["dependency_type"] == "DataAccessOperation -> StoredProcedure"]
            keys = {(dep["source"], dep["target"], dep["dependency_type"]) for dep in edges}
            self.assertEqual(len(edges), len(keys))
            self.assertTrue(any(dep["evidence_count"] >= 1 for dep in edges))

    def test_v2_r3_ambiguous_stored_proc_expression_remains_unresolved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Save(procName As String)
Dim cmd As New OracleCommand(procName, conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            unresolved = [op for op in result["operations"] if op["command_type"] == "StoredProcedure" and not op["stored_procedure"]]
            self.assertTrue(unresolved)
            self.assertTrue(all(op["confidence"] == "unresolved" for op in unresolved))

    def test_v2_r3_preserves_v2_r2_entry_points(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnBuscar" OnClick="btnBuscar_Click" runat="server" />')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Sub btnBuscar_Click(sender As Object, e As EventArgs)\nEnd Sub\nEnd Class")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(len(indexes["entry_points"]), 1)
            self.assertEqual(indexes["entry_points"][0]["confidence"], "confirmed")

    def test_v2_r3_1_oraconn_byref_parameter_execproc_links_method(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Sys</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Sys.vb" /></ItemGroup></Project>')
            write(root / "Sys.vb", """Public Class Sys
Public Shared Function Buscar(ByRef dbc As OraConn, ByVal idAdm As Integer) As DataSet
Return dbc.ExecProc("PSYS.BUSCAR", "ID_ADM,THISCURSOR", values, "in,out", "int,cursor")
End Function
End Class""")
            indexes = analyze_repository(root, root / "out")
            op = next(op for op in indexes["data_access"] if op["stored_procedure"] == "PSYS.BUSCAR")
            self.assertEqual(op["method"], "Buscar")
            self.assertEqual(op["class"], "Sys")
            self.assertTrue(any(dep["dependency_type"] == "Method -> DataAccessOperation" and dep["target"] == op["id"] for dep in indexes["functional_dependencies"]))
            params = {p["name"]: p for p in indexes["data_parameters"]}
            self.assertEqual(params["ID_ADM"]["direction"], "Input")
            self.assertEqual(params["THISCURSOR"]["db_type"], "cursor")

    def test_v2_r3_1_oraconn_byval_parameter_execprocds_and_transactions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Sys.vb", """Public Class Sys
Public Shared Sub Crear(ByVal dbc As OraConn, ByVal ds As Object)
dbc.BeginTrans()
dbc.ExecProcDS("PSYS.CREAR", "ID_ADM", ds, "in", "decimal")
dbc.Commit()
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(any(op["stored_procedure"] == "PSYS.CREAR" and op["method"] == "Crear" for op in result["operations"]))
            self.assertEqual(len([op for op in result["operations"] if op["operation_kind"] == "transaction"]), 2)
            self.assertEqual(result["parameters"][0]["wrapper"], "ExecProcDS")
            self.assertEqual(result["parameters"][0]["db_type"], "decimal")

    def test_v2_r3_1_public_shared_sub_attribute_and_multiline_signature(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Sys.vb", """Public Class Sys
<Obsolete()>
Public Shared Sub Crear( _
ByRef dbc As OraConn, _
ByVal idAdm As Integer)
dbc.ExecProc("PSYS.CREAR", "ID_ADM", values, "in", "int")
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            op = next(op for op in result["operations"] if op["stored_procedure"] == "PSYS.CREAR")
            self.assertEqual(op["method"], "Crear")
            self.assertEqual(op["class"], "Sys")

    def test_v2_r3_1_direct_oracle_class_field_commandtext_execute_fill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Private cmd As OracleCommand
Private da As OracleDataAdapter
Public Function Load() As DataSet
Dim sql As String = "SELECT * FROM CLIENTE WHERE ID = " & id
cmd.CommandText = sql
cmd.ExecuteReader()
da.Fill(ds)
End Function
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertTrue(any(op["sql_operation"] == "SELECT" and op["dynamic_sql"] for op in result["operations"]))
            self.assertTrue(any(op["command_variable"] == "cmd" and op["method"] == "Load" for op in result["operations"]))
            self.assertTrue(any(op["operation_kind"] == "fill" and op["method"] == "Load" for op in result["operations"]))

    def test_v2_r3_1_execprocds_dynamic_and_non_oraconn_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Sys.vb", """Public Class Sys
Public Sub Run(ByRef dbc As OraConn, helper As Object, procName As String)
dbc.ExecProcDS(procName, "ID_ADM", values)
helper.ExecProcDS("P.BAD", "ID")
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(len(result["operations"]), 1)
            self.assertEqual(result["operations"][0]["confidence"], "unresolved")
            self.assertIsNone(result["operations"][0]["stored_procedure"])

    def test_v2_r3_1_unrelated_sql_string_false_positive_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vb = write(root / "Repo.vb", """Public Class Repo
Public Sub Run()
Dim text As String = "SELECT * FROM CLIENTE"
End Sub
End Class""")
            result = DatabaseExtractor().extract(vb, root)
            self.assertEqual(result["operations"], [])

    def test_v2_r3_1_sanitizes_nested_evidence_and_dependency_samples(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Data</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Repo.vb" /></ItemGroup></Project>')
            write(root / "Repo.vb", """Public Class Repo
Public Sub Run()
Dim conn As New OracleConnection("Data Source=db;User ID=scott;Password=tiger;Pwd=t;UID=u;Username=admin;Token=abc")
Dim cmd As New OracleCommand("PKG.SECRET", conn)
cmd.CommandType = CommandType.StoredProcedure
cmd.ExecuteNonQuery()
End Sub
End Class""")
            analyze_repository(root, root / "out")
            for name in ["data_access.json", "stored_procedures.json", "data_parameters.json", "functional_dependencies.json"]:
                text = (root / "out" / "index" / name).read_text(encoding="utf-8").lower()
                self.assertNotIn("scott", text)
                self.assertNotIn("tiger", text)
                self.assertNotIn("token=abc", text)

    def test_v2_r3_1_dedup_and_r1_r2_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Compile Include="Servicio.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnBuscar" OnClick="btnBuscar_Click" runat="server" />')
            write(root / "Default.aspx.vb", """Public Class DefaultPage
Protected Sub btnBuscar_Click(sender As Object, e As EventArgs)
Dim svc As New Servicio()
svc.Buscar()
End Sub
End Class""")
            write(root / "Servicio.vb", """Public Class Servicio
Public Sub Buscar()
Dim dbc As New OraConn()
dbc.ExecProc("P.BUSCAR", "ID", values, "in", "int")
dbc.ExecProc("P.BUSCAR", "ID", values, "in", "int")
End Sub
End Class""")
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(len(indexes["entry_points"]), 1)
            self.assertTrue(any(call["method_name"] == "Buscar" and call["confidence"] == "confirmed" for file_calls in indexes["calls"] for call in file_calls["calls"]))
            keys = [(dep["source"], dep["target"], dep["dependency_type"], dep["source_file"], dep["confidence"]) for dep in indexes["functional_dependencies"]]
            self.assertEqual(len(keys), len(set(keys)))

    def test_v2_r4_builds_deterministic_branching_flows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "Web.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Compile Include="Servicio.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %><asp:Button ID="btnGuardar" OnClick="btnGuardar_Click" runat="server" />')
            write(root / "Default.aspx.vb", """Public Class DefaultPage
Protected Sub btnGuardar_Click(sender As Object, e As EventArgs)
Dim svc As New Servicio()
svc.Guardar()
End Sub
End Class""")
            write(root / "Servicio.vb", """Public Class Servicio
Public Sub Guardar()
Proc()
Sql()
NoResuelto().Llamar()
End Sub
Public Sub Proc()
Dim dbc As New OraConn()
dbc.ExecProc("P.GUARDAR", "ID", values, "in", "int")
End Sub
Public Sub Sql()
Dim cmd As New OracleCommand("SELECT * FROM CLIENTE", conn)
cmd.ExecuteReader()
End Sub
End Class""")
            first = analyze_repository(root, root / "out")
            second = analyze_repository(root, root / "out2")
            self.assertEqual(len(first["functional_flows"]), 1)
            terminals = {item["terminal_type"] for item in first["functional_paths"]}
            self.assertTrue({"stored_procedure", "sql", "unresolved_boundary"}.issubset(terminals))
            self.assertIn("P.GUARDAR", {item["terminal_target"] for item in first["functional_paths"]})
            self.assertEqual(first["functional_flows"], second["functional_flows"])
            self.assertTrue((root / "out" / "index" / "flow_summary.json").exists())

    def test_v2_r4_1_path_ids_use_complete_canonical_identity_and_guard_collisions(self):
        resolver = FunctionalFlowResolver()
        first_id, first_canonical = resolver._path_id("EP-A", ["P::a.start", "DAO-1", "SP-1"], ["Method -> Method", "Method -> DataAccessOperation", "DataAccessOperation -> StoredProcedure"], "stored_procedure", "P.SAVE")
        repeated_id, repeated_canonical = resolver._path_id("EP-A", ["P::a.start", "DAO-1", "SP-1"], ["Method -> Method", "Method -> DataAccessOperation", "DataAccessOperation -> StoredProcedure"], "stored_procedure", "P.SAVE")
        self.assertEqual((first_id, first_canonical), (repeated_id, repeated_canonical))
        variants = [
            ("EP-B", ["P::a.start", "DAO-1", "SP-1"], ["Method -> Method", "Method -> DataAccessOperation", "DataAccessOperation -> StoredProcedure"], "stored_procedure", "P.SAVE"),
            ("EP-A", ["P::a.start", "P::b.next", "DAO-1", "SP-1"], ["Method -> Method", "Method -> Method", "Method -> DataAccessOperation", "DataAccessOperation -> StoredProcedure"], "stored_procedure", "P.SAVE"),
            ("EP-A", ["P::a.start", "DAO-1", "SP-2"], ["Method -> Method", "Method -> DataAccessOperation", "DataAccessOperation -> StoredProcedure"], "stored_procedure", "P.DELETE"),
            ("EP-A", ["P::a.start", "UNRES-1"], ["Method -> UnresolvedCall"], "unresolved_boundary", "x.Call"),
        ]
        self.assertTrue(all(resolver._path_id(*variant)[0] != first_id for variant in variants))
        resolver._path_identities = {}
        paths = {}
        resolver._add_path(paths, {"id": "EP-A"}, ["P::a.start"], [], "dead_end", "P::a.start", "confirmed", [])
        self.assertEqual(len(paths), 1)
        resolver._path_id = lambda *args: ("PATH-forced", "one")
        resolver._path_identities = {"PATH-forced": "one"}
        resolver._add_path(paths, {"id": "EP-B"}, ["P::b.start"], [], "dead_end", "P::b.start", "confirmed", [])
        resolver._path_id = lambda *args: ("PATH-forced", "different")
        with self.assertRaisesRegex(ValueError, "collision"):
            resolver._add_path(paths, {"id": "EP-C"}, ["P::c.start"], [], "dead_end", "P::c.start", "confirmed", [])

    def test_v2_r5_generates_compact_ai_context_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa.Web</RootNamespace></PropertyGroup><ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup></Project>')
            write(root / "Default.aspx", '<%@ Page CodeBehind="Default.aspx.vb" Inherits="Empresa.Web.DefaultPage" %>')
            write(root / "Default.aspx.vb", "Public Class DefaultPage\nProtected Overrides Sub OnLoad(e As EventArgs)\nEnd Sub\nEnd Class")
            output = root / "out"
            analyze_repository(root, output)
            context = output / "ai_context"
            for name in ["SYSTEM_CONTEXT.json", "SYSTEM_CONTEXT.md", "ARCHITECTURE_GRAPH.json", "FUNCTIONAL_FLOWS.json", "TRACEABILITY.json"]:
                self.assertTrue((context / name).exists())
            model = __import__("json").loads((context / "SYSTEM_CONTEXT.json").read_text(encoding="utf-8"))
            self.assertEqual(model["metadata"]["model_version"], "V2-R5")
            graph = __import__("json").loads((context / "ARCHITECTURE_GRAPH.json").read_text(encoding="utf-8"))
            node_ids = {node["id"] for node in graph["nodes"]}
            self.assertTrue(all(edge["source"] in node_ids and edge["target"] in node_ids for edge in graph["edges"]))
            self.assertEqual(graph["statistics"]["orphan_edge_sources"], 0)
            self.assertEqual(graph["statistics"]["orphan_edge_targets"], 0)


if __name__ == "__main__":
    unittest.main()
