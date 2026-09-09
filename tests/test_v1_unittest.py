import tempfile
import unittest
from pathlib import Path

from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.extractors.solution_extractor import SolutionExtractor
from legacy_documenter.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.extractors.vbproj_extractor import VBProjExtractor
from legacy_documenter.extractors.webconfig_extractor import WebConfigExtractor
from legacy_documenter.extractors.webforms_extractor import WebFormsExtractor
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


if __name__ == "__main__":
    unittest.main()
