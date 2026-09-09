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


def test_repository_scanner_discovers_files_and_respects_exclusions(tmp_path):
    write(tmp_path / "App" / "Default.aspx", "<%@ Page Language=\"VB\" %>")
    write(tmp_path / "bin" / "ignored.dll", "")
    files = RepositoryScanner().scan(tmp_path)
    assert [f.relative_path for f in files] == ["App\\Default.aspx"] or [f.relative_path for f in files] == ["App/Default.aspx"]
    assert files[0].file_type == "aspx"


def test_solution_extractor_detects_projects(tmp_path):
    sln = write(
        tmp_path / "Sample.sln",
        'Project("{TYPE}") = "Web", "Web\\Web.vbproj", "{PROJECT}"\nEndProject\n',
    )
    result = SolutionExtractor().extract(sln, tmp_path)
    assert result["name"] == "Sample"
    assert result["projects"][0]["name"] == "Web"
    assert result["projects"][0]["path"] == "Web\\Web.vbproj"


def test_vbproj_extractor_reads_references_and_items(tmp_path):
    vbproj = write(
        tmp_path / "Web" / "Web.vbproj",
        """<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup><AssemblyName>Web</AssemblyName><RootNamespace>Company.Web</RootNamespace><TargetFrameworkVersion>v4.0</TargetFrameworkVersion><OutputType>Library</OutputType></PropertyGroup>
  <ItemGroup><ProjectReference Include="..\\BL\\BL.vbproj"><Name>BL</Name><Project>{BL}</Project></ProjectReference></ItemGroup>
  <ItemGroup><Reference Include="System.Web" /><Reference Include="Oracle.DataAccess"><HintPath>lib\\Oracle.DataAccess.dll</HintPath></Reference></ItemGroup>
  <ItemGroup><Compile Include="Default.aspx.vb" /><Content Include="Default.aspx" /></ItemGroup>
</Project>""",
    )
    project = VBProjExtractor().extract(vbproj, tmp_path)
    assert project.target_framework == "v4.0"
    assert project.project_references[0]["name"] == "BL"
    assert project.assembly_references[1]["hint_path"] == "lib\\Oracle.DataAccess.dll"
    assert "Default.aspx.vb" in project.compile_items
    assert "Default.aspx" in project.content_items


def test_vbnet_extractor_reads_symbols_and_members(tmp_path):
    vb = write(
        tmp_path / "Sample.vb",
        """Namespace Company.Web
Public Interface IFoo
End Interface
Public Module Helpers
End Module
Public Enum Status
End Enum
Public Partial Class CustomerPage
    Inherits BasePage
    Implements IFoo
    Public Property Name As String
    Public Shared Function Load(id As Integer) As String
    End Function
    Public Sub Save()
    End Sub
End Class
End Namespace
""",
    )
    symbols = VBNetExtractor().extract(vb, tmp_path)
    kinds = {s.kind for s in symbols}
    page = next(s for s in symbols if s.name == "CustomerPage")
    assert {"interface", "module", "enum", "class"} <= kinds
    assert page.namespace == "Company.Web"
    assert "Partial" in page.modifiers
    assert page.inherits == ["BasePage"]
    assert page.implements == ["IFoo"]
    assert {m["kind"] for m in page.members} == {"property", "function", "sub"}


def test_webforms_extractor_reads_directives_registers_assets(tmp_path):
    aspx = write(
        tmp_path / "Default.aspx",
        """<%@ Page Language="VB" CodeBehind="Default.aspx.vb" Inherits="Company.Web.CustomerPage" MasterPageFile="~/Site.master" %>
<%@ Register Src="~/Controls/Customer.ascx" TagPrefix="uc" TagName="Customer" %>
<%@ Register Namespace="Company.Controls" Assembly="Company.Web" TagPrefix="cc" %>
<script src="/app/site.js"></script>
<link rel="stylesheet" href="/app/site.css" />
""",
    )
    form = WebFormsExtractor().extract(aspx, tmp_path)
    assert form.codebehind == "Default.aspx.vb"
    assert form.inherits == "Company.Web.CustomerPage"
    assert form.registers[0]["Src"] == "~/Controls/Customer.ascx"
    assert form.registers[1]["Assembly"] == "Company.Web"
    assert form.scripts == ["/app/site.js"]
    assert form.stylesheets == ["/app/site.css"]


def test_webconfig_extractor_sanitizes_and_reads_assemblies(tmp_path):
    config = write(
        tmp_path / "web.config",
        """<configuration>
  <appSettings><add key="Mode" value="Prod" /></appSettings>
  <connectionStrings><add name="Main" providerName="Oracle" connectionString="User ID=scott;Password=tiger;Data Source=db" /></connectionStrings>
  <system.web><compilation targetFramework="4.0"><assemblies><add assembly="System.Web" /></assemblies></compilation></system.web>
</configuration>""",
    )
    result = WebConfigExtractor().extract(config, tmp_path)
    assert result["appSettings"][0]["key"] == "Mode"
    assert "Password=********" in result["connectionStrings"][0]["connectionString"]
    assert "User ID=********" in result["connectionStrings"][0]["connectionString"]
    assert result["assemblies"][0]["assembly"] == "System.Web"


def test_dependency_resolver_project_codebehind_inherits_register():
    deps = DependencyResolver().resolve(
        [],
        [{"path": "Web.vbproj", "project_references": [{"include": "BL.vbproj"}], "assembly_references": [], "compile_items": []}],
        [{"name": "CustomerPage", "namespace": "Company.Web", "kind": "class", "file": "Default.aspx.vb", "inherits": [], "implements": []}],
        [{"path": "Default.aspx", "kind": "aspx", "codebehind": "Default.aspx.vb", "inherits": "Company.Web.CustomerPage", "registers": [{"Src": "~/Control.ascx"}], "scripts": [], "stylesheets": []}],
    )
    types = {d.dependency_type for d in deps}
    assert "Project -> Project" in types
    assert "ASPX -> CodeBehind" in types
    assert "WebForm -> VBClass" in types
    assert "ASPX -> ASCX" in types


def test_integration_writes_indexes_and_docs(tmp_path):
    repo = tmp_path / "repo"
    write(repo / "Sample.sln", 'Project("{TYPE}") = "Web", "Web\\Web.vbproj", "{PROJECT}"\nEndProject\n')
    write(repo / "Web" / "Web.vbproj", "<Project><PropertyGroup><AssemblyName>Web</AssemblyName><TargetFrameworkVersion>v4.0</TargetFrameworkVersion></PropertyGroup><ItemGroup><Compile Include=\"Default.aspx.vb\" /><Content Include=\"Default.aspx\" /></ItemGroup></Project>")
    write(repo / "Web" / "Default.aspx", '<%@ Page Language="VB" CodeBehind="Default.aspx.vb" Inherits="Company.Web.CustomerPage" %>')
    write(repo / "Web" / "Default.aspx.vb", "Namespace Company.Web\nPublic Class CustomerPage\nEnd Class\nEnd Namespace\n")
    output = tmp_path / "out"
    indexes = analyze_repository(repo, output)
    assert indexes["repository"]["stats"]["total_files"] == 4
    assert (output / "index" / "dependencies.json").exists()
    assert (output / "documentation" / "PROJECT_OVERVIEW.md").exists()
