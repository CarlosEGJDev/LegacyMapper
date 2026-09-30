"""V5.2 R3.2: real project identity and human documentation clarity.

Covers: only a real `.vbproj`/`.csproj` (a `Project` evidence record) ever
becomes a "project" document; a homonymous file/class never becomes a
fictitious project; Solution -> Project membership and a project shared
between solutions keeping a single identity; homonym paths distinguishable;
technical output type separated from project type (never guessed from name
or prefix); outgoing vs incoming project dependencies (the
BLInterfazSAP/WebInterfazSAP direction specifically); declarative noise
classification for `System.Web.UI.WebControls.Unit(...)`,
`Response.Write(...)` and `GetColumnByDataField(...)` without ever declaring
them resolved; determinism; legacy documentation untouched.

Contract-level assertions on a small synthetic source shaped like the real
BLInterfazSAP/WebInterfazSAP evidence (see
`docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md` section 2 for the
real evidence this fixture is modeled on); no full-text snapshots.
"""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.documentation_v52.config import ConfigError, ConfigRegistry, validate_template
from legacy_documenter.documentation_v52.engine import generate_documentation_v52
from legacy_documenter.documentation_v52.noise import bare_name
from legacy_documenter.documentation_v52.transform import AudienceTransformer

# Paths shaped exactly like the real IST evidence for BLInterfazSAP/WebInterfazSAP.
BL = "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"
WEB = "WebInterfazSAP.vbproj"
SYS = "sys\\SysInterfazSAP\\SysInterfazSAP.vbproj"
WEB_HOMONYM = "proyectos\\SlnB\\Backup\\WebInterfazSAP\\WebInterfazSAP.vbproj"
ASCX_LIB = "web\\ucLib\\ucLib.vbproj"


def _projects() -> list[dict]:
    return [
        {
            "name": "BLInterfazSAP", "path": BL, "output_type": "Library", "assembly_name": "BLInterfazSAP",
            "compile_items": ["AssemblyInfo.vb", "BLInterfazSAP.vb"],  # the homonymous class lives INSIDE the project
            "content_items": [], "project_references": [{"project": SYS}],
        },
        {
            "name": "WebInterfazSAP", "path": WEB, "output_type": "Library",
            "compile_items": ["WebInterfazSAP\\ucArchivoSAP.ascx.vb"],
            "content_items": ["WebInterfazSAP\\ucArchivoSAP.ascx", "Default.aspx", "Global.asax"],
            "project_references": [{"project": BL}],
        },
        {
            "name": "SysInterfazSAP", "path": SYS, "output_type": "Library",
            "compile_items": ["SysInterfazSAP.vb"], "content_items": [],
        },
        {
            "name": "WebInterfazSAP", "path": WEB_HOMONYM, "output_type": "Library",
            "compile_items": [], "content_items": ["Default.aspx"],
        },
        {
            "name": "ucLib", "path": ASCX_LIB, "output_type": "Library",
            "compile_items": ["ucFoo.ascx.vb"], "content_items": ["ucFoo.ascx"],
        },
    ]


def _source() -> dict:
    dependencies = [
        {"source": WEB, "target": BL, "dependency_type": "Project -> Project"},
        {"source": BL, "target": SYS, "dependency_type": "Project -> Project"},
    ]
    solutions = [
        {"name": "SistemaSAP", "path": "SistemaSAP.sln", "projects": [
            {"name": "WebInterfazSAP", "path": WEB}, {"name": "BLInterfazSAP", "path": "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"}]},
        {"name": "ModuloBL", "path": "sub\\ModuloBL.sln", "projects": [
            {"name": "BLInterfazSAP", "path": "..\\bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"}]},
    ]
    unresolved = [
        {"flow_id": "FLOW-0000000001", "path_id": "PATH-a", "terminal_target": "System.Web.UI.WebControls.Unit(10, UnitType.Percentage)"},
        {"flow_id": "FLOW-0000000001", "path_id": "PATH-b", "terminal_target": "dgrPagos.GetColumnByDataField(              )"},
        {"flow_id": "FLOW-0000000001", "path_id": "PATH-c", "terminal_target": "Response.Write(tw.ToString())"},
        {"flow_id": "FLOW-0000000001", "path_id": "PATH-d", "terminal_target": "Foo.RealBusinessCall(x)"},
    ]
    entry_points = [{"id": "EP-0000000001", "type": "web_event", "webform": "Default.aspx", "event": "Click",
                     "handler": "btn_Click", "project": WEB, "confidence": "confirmed"}]
    flows = [{"id": "FLOW-0000000001", "entry_point_id": "EP-0000000001", "webform": "Default.aspx", "event": "Click",
              "handler": "btn_Click", "project_sequence": [WEB], "terminal_operations": [],
              "has_confirmed_terminal": False, "has_unresolved_boundary": True}]
    return {
        "repository": {"root": "C:\\repo\\SistemaSAP", "stats": {"vb_source": 6}},
        "solutions": solutions, "projects": _projects(), "entry_points": entry_points, "functional_flows": flows,
        "flow_unresolved": unresolved, "data_access": [], "stored_procedures": [], "sql_operations": [],
        "dependencies": dependencies, "configuration": [],
        "flow_summary": {"total_flows": 1, "flows_with_confirmed_terminal": 0, "flows_with_unresolved_boundary": 1},
        "webforms": [], "external_dependencies": [],
    }


def _model(source: dict | None = None):
    return AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source or _source())


def _module(model, path: str):
    return next(m for m in model.modules if m.values["path"] == path)


def _generate(tmp: str, source: dict | None = None):
    return generate_documentation_v52(source or _source(), tmp)


def _module_doc(result, path: str) -> str:
    slug = _module(_model(), path).slug
    return (result.output_dir / "developer" / "modules" / f"{slug}.md").read_text(encoding="utf-8")


class RealProjectIdentityTests(unittest.TestCase):
    """Only a real Project (a `.vbproj`/`.csproj` evidence record) becomes a module."""

    def test_every_module_path_is_a_real_project_path(self) -> None:
        model = _model()
        project_paths = {p["path"] for p in _projects()}
        module_paths = {m.values["path"] for m in model.modules if m.values["path"]}
        self.assertEqual(module_paths, project_paths)

    def test_blinterfazsap_is_a_real_project_with_visible_identity(self) -> None:
        model = _model()
        bl = _module(model, BL)
        self.assertEqual(bl.values["name"], "BLInterfazSAP")
        self.assertEqual(bl.values["path"], BL)
        self.assertIn("SistemaSAP", bl.values["solutions"])
        self.assertIn("ModuloBL", bl.values["solutions"])

    def test_homonymous_class_file_does_not_create_a_fictitious_project(self) -> None:
        """`BLInterfazSAP.vb` (a Component/SourceArtifact inside the project's own
        `compile_items`) never becomes its own module: there is exactly one
        module for the BL path, none for the bare file name."""
        model = _model()
        matches = [m for m in model.modules if "BLInterfazSAP" in m.values["name"]]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].values["path"], BL)
        self.assertNotIn("BLInterfazSAP.vb", [m.values["path"] for m in model.modules])

    def test_no_module_is_built_from_a_prefix_or_folder_name(self) -> None:
        """`bl`, `sys`, `web` alone (the folder/prefix) are never module paths;
        only the exact `.vbproj` path from the projects partition is."""
        model = _model()
        for module in model.modules:
            if module.values["path"]:
                self.assertTrue(module.values["path"].lower().endswith((".vbproj", ".csproj")))


class SolutionProjectMembershipTests(unittest.TestCase):
    def test_solution_to_project_membership_resolved_by_path(self) -> None:
        model = _model()
        web = _module(model, WEB)
        self.assertIn("SistemaSAP", web.values["solutions"])

    def test_project_shared_between_solutions_keeps_a_single_identity(self) -> None:
        """BLInterfazSAP belongs to two solutions; it must still be exactly one
        module, not duplicated once per solution."""
        model = _model()
        matches = [m for m in model.modules if m.values["path"] == BL]
        self.assertEqual(len(matches), 1)
        names = sorted(n.strip() for n in matches[0].values["solutions"].split(","))
        self.assertEqual(names, ["ModuloBL", "SistemaSAP"])

    def test_navigating_from_solution_to_its_projects(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            modules_index = (result.output_dir / "general" / "modules.md").read_text(encoding="utf-8")
        self.assertIn("SistemaSAP", modules_index)


class HomonymVisibleIdentityTests(unittest.TestCase):
    def test_homonymous_projects_are_distinguished_by_path(self) -> None:
        model = _model()
        names = {m.values["path"]: m.values["name"] for m in model.modules if m.values["path"]}
        self.assertEqual(names[WEB], f"WebInterfazSAP ({WEB})")
        self.assertEqual(names[WEB_HOMONYM], f"WebInterfazSAP ({WEB_HOMONYM})")

    def test_visible_name_never_uses_an_artificial_numeric_suffix(self) -> None:
        model = _model()
        for module in model.modules:
            self.assertNotRegex(module.values["name"], r"-\d+$")


class TechnicalOutputTypeVsProjectTypeTests(unittest.TestCase):
    def test_document_uses_technical_output_type_wording(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            bl = _module_doc(result, BL)
        self.assertIn("Tipo técnico de salida: Library.", bl)
        self.assertNotIn("Tipo de salida:", bl)

    def test_web_project_gets_a_separate_project_type_from_structural_evidence(self) -> None:
        model = _model()
        web = _module(model, WEB)
        self.assertIn("Aplicación Web", web.values["project_type"])
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            doc = _module_doc(result, WEB)
        self.assertIn("Tipo de proyecto (según la evidencia estructural del propio proyecto): Aplicación Web", doc)

    def test_project_type_is_not_guessed_from_output_type_or_name_alone(self) -> None:
        """BLInterfazSAP is `output_type: Library` and has no web content items:
        it must NOT be classified as a project type just because it compiled
        to a library, and its `BL` prefix must not be read as "business logic"."""
        model = _model()
        bl = _module(model, BL)
        self.assertEqual(bl.values["project_type"], "")
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            doc = _module_doc(result, BL)
        self.assertIn("Tipo de proyecto: no pudo determinarse", doc)

    def test_ascx_only_project_is_a_web_user_control_library_not_a_full_web_app(self) -> None:
        model = _model()
        lib = _module(model, ASCX_LIB)
        self.assertIn("Biblioteca de controles de usuario Web", lib.values["project_type"])
        self.assertNotIn("Aplicación Web", lib.values["project_type"])


class DependencyDirectionTests(unittest.TestCase):
    """The mandatory BLInterfazSAP / WebInterfazSAP case (round section 7)."""

    def test_outgoing_and_incoming_are_separate_slots(self) -> None:
        model = _model()
        web, bl = _module(model, WEB), _module(model, BL)
        self.assertEqual([i.values["name"] for i in web.slots["project_refs_out"]], ["BLInterfazSAP"])
        self.assertEqual(web.slots["project_refs_in"], [])
        self.assertEqual([i.values["name"] for i in bl.slots["project_refs_in"]], ["WebInterfazSAP (WebInterfazSAP.vbproj)"])
        # BL -> SYS is also a real, declared outgoing dependency of BL
        self.assertEqual([i.values["name"] for i in bl.slots["project_refs_out"]], ["SysInterfazSAP"])

    def test_direction_is_not_inverted(self) -> None:
        """WebInterfazSAP uses BLInterfazSAP -- never the other way around."""
        model = _model()
        bl = _module(model, BL)
        out_names = [i.values["name"] for i in bl.slots["project_refs_out"]]
        self.assertNotIn("WebInterfazSAP (WebInterfazSAP.vbproj)", out_names)

    def test_documents_show_two_separate_headings_with_real_direction(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            web_doc = _module_doc(result, WEB)
            bl_doc = _module_doc(result, BL)
        self.assertIn("### Proyectos que este proyecto utiliza", web_doc)
        self.assertIn("BLInterfazSAP", web_doc.split("### Proyectos que este proyecto utiliza")[1].split("###")[0])
        self.assertIn("### Proyectos que utilizan este proyecto", bl_doc)
        self.assertIn("WebInterfazSAP", bl_doc.split("### Proyectos que utilizan este proyecto")[1].split("##")[0])
        self.assertNotIn("Proyectos referenciados", web_doc)
        self.assertNotIn("Proyectos referenciados", bl_doc)

    def test_unproven_dependency_stays_unclassified_not_invented(self) -> None:
        """A project with no declared `Project -> Project` edge has empty
        outgoing/incoming slots -- no dependency is fabricated."""
        model = _model()
        sys_ = _module(model, SYS)
        self.assertEqual(sys_.slots["project_refs_out"], [])
        self.assertEqual([i.values["name"] for i in sys_.slots["project_refs_in"]], ["BLInterfazSAP"])


class UnresolvedNoiseDeclarativePolicyTests(unittest.TestCase):
    """`System.Web.UI.WebControls.Unit(...)`, `Response.Write(...)` and
    `GetColumnByDataField(...)` are relegated to detail through the noise
    policy DATA (JSON), never declared resolved."""

    def test_policy_classifies_the_three_named_calls(self) -> None:
        policy = ConfigRegistry().noise_policy("default")
        label_unit = "System.Web.UI.WebControls.Unit(10, UnitType.Percentage)"
        label_col = "dgrPagos.GetColumnByDataField(              )"
        label_write = "Response.Write(tw.ToString())"
        self.assertEqual(policy.classify(name=bare_name(label_unit), label=label_unit), "ui_control_calls")
        self.assertEqual(policy.classify(name=bare_name(label_col), label=label_col), "ui_control_calls")
        self.assertEqual(policy.classify(name=bare_name(label_write), label=label_write), "ui_control_calls")
        self.assertEqual(policy.visibility("ui_control_calls"), "hide")

    def test_unrelated_write_and_parse_calls_are_not_swept_into_noise(self) -> None:
        """`sw.Write(...)` (real file I/O) and `Integer.Parse(...)` are not
        `Response.Write`/`Unit.Parse`: the policy must not classify them as
        noise just because their bare name coincides."""
        policy = ConfigRegistry().noise_policy("default")
        self.assertIsNone(policy.classify(name=bare_name("sw.Write(x)"), label="sw.Write(x)"))
        self.assertIsNone(policy.classify(name=bare_name("Integer.Parse(x)"), label="Integer.Parse(x)"))

    def test_unresolved_body_hides_the_three_calls_but_keeps_a_real_one(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            doc = _module_doc(result, WEB)
            detail_dir = result.output_dir / "developer" / "modules"
            detail = "\n".join(p.read_text(encoding="utf-8") for p in detail_dir.rglob("detail*.md"))
        body = doc.split("## Información no resuelta")[1]
        for noisy in ("WebControls.Unit(", "GetColumnByDataField(", "Response.Write("):
            self.assertNotIn(noisy, body)
        self.assertIn("Foo.RealBusinessCall", body)
        self.assertIn("Se omiten del cuerpo 3 elementos", body)
        # never declared resolved -- still present, verbatim, in the detail document
        self.assertIn("WebControls.Unit(", detail)
        self.assertIn("GetColumnByDataField(", detail)
        self.assertIn("Response.Write(", detail)

    def test_reduced_prominence_never_means_fewer_unresolved_points_counted(self) -> None:
        model = _model()
        web = _module(model, WEB)
        self.assertEqual(web.values["unresolved_total"], 4)  # all 4 still counted, none silently dropped


class TemplateContractTests(unittest.TestCase):
    def test_old_combined_project_refs_source_no_longer_validates(self) -> None:
        registry = ConfigRegistry()
        profile = registry.profile("developer_technical")
        catalog = registry.catalog(profile.language)
        template = {
            "id": "custom.bad", "contract_version": "1", "scope": "module", "file": "modules/{slug}.md",
            "profile_compat": ["developer_technical"],
            "blocks": [{"type": "table", "source": "module.slots.project_refs",
                        "columns": [{"field": "name", "header_key": "col.module"}]}],
        }
        with self.assertRaises(ConfigError):
            validate_template(template, catalog, profile, expected_id="custom.bad")

    def test_split_sources_validate(self) -> None:
        registry = ConfigRegistry()
        profile = registry.profile("developer_technical")
        catalog = registry.catalog(profile.language)
        for source in ("module.slots.project_refs_out", "module.slots.project_refs_in"):
            template = {
                "id": "custom.ok", "contract_version": "1", "scope": "module", "file": "modules/{slug}.md",
                "profile_compat": ["developer_technical"],
                "blocks": [{"type": "table", "source": source,
                            "columns": [{"field": "name", "header_key": "col.module"},
                                        {"field": "path", "header_key": "col.path"}]}],
            }
            validate_template(template, catalog, profile, expected_id="custom.ok")  # must not raise


class R31RegressionSpotCheckTests(unittest.TestCase):
    """R3.2 must not regress R3.1's corrections; spot-checked on this round's
    own fixture (the full R3.1 suite runs unchanged in the same discovery)."""

    def test_ownership_vs_participation_still_holds(self) -> None:
        model = _model()
        bl = _module(model, BL)
        self.assertEqual(bl.values["screens"], 0)  # BL owns no screens; WEB's screen only arrives here indirectly

    def test_direct_vs_indirect_language_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            doc = _module_doc(result, BL)
        self.assertIn("Acceso directo a datos: ninguno.", doc)

    def test_documentation_v52_directory_generated(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            self.assertTrue((result.output_dir / "README.md").is_file())


class DeterminismAndLegacyTests(unittest.TestCase):
    def test_same_input_same_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = _generate(a)
            second = _generate(b, copy.deepcopy(_source()))
            self.assertEqual(first.files, second.files)
            for name in first.files:
                self.assertEqual((first.output_dir / name).read_bytes(), (second.output_dir / name).read_bytes())

    def test_legacy_documentation_directory_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "documentation"
            legacy.mkdir()
            (legacy / "kept.md").write_text("unchanged", encoding="utf-8")
            _generate(tmp)
            self.assertEqual([p.name for p in legacy.iterdir()], ["kept.md"])
            self.assertEqual((legacy / "kept.md").read_text(encoding="utf-8"), "unchanged")


if __name__ == "__main__":
    unittest.main()
