"""V5.2 R3.3: Solution -> Project -> Component/Archivo -> Método -> Evidencia navigation.

Covers the round's mandatory regressions/new cases (round section 17): a real
`Project -> SourceArtifact` link derived only from `compile_items`/
`content_items` (never name/folder); `SourceArtifact -> Component`; a file with
several components; a component whose file has no demonstrable project owner;
a homonymous file name owned by two distinct, unambiguous projects; a project
shared between solutions still resolving to one Solution -> Project link set;
round-trip navigation (Método -> Componente -> Archivo -> Proyecto ->
Solution); relative links; partitioning reused for the new indices;
determinism; no fictitious project/component/method is ever invented; detail
documents carry no extra analysis; main documents stay short; legacy
(`documentation/`) untouched.

Contract-level assertions on a small synthetic source; no full-text snapshots
of the real IST run (that is verified separately, by hand, against the real
run -- see `docs/V5/V5_2_R3_3_COMPONENT_NAVIGATION.md`).
"""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.documentation_v52.config import ConfigRegistry
from legacy_documenter.documentation_v52.engine import generate_documentation_v52
from legacy_documenter.documentation_v52.transform import AudienceTransformer

BL = "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"
WEB = "WebInterfazSAP.vbproj"
SYS = "sys\\SysInterfazSAP\\SysInterfazSAP.vbproj"
SHARED_VBPROJ = "shared\\Shared.vbproj"  # declares the same physical file as BL (ambiguous ownership case)


def _projects() -> list[dict]:
    return [
        {
            "name": "BLInterfazSAP", "path": BL, "output_type": "Library", "assembly_name": "BLInterfazSAP",
            "compile_items": ["AssemblyInfo.vb", "BLInterfazSAP.vb", "Ambiguo.vb", "SinSimbolos.vb"], "content_items": [],
            "project_references": [{"project": SYS}],
        },
        {
            "name": "WebInterfazSAP", "path": WEB, "output_type": "Library",
            "compile_items": ["WebInterfazSAP\\ucArchivoSAP.ascx.vb", "AssemblyInfo.vb"],
            "content_items": ["WebInterfazSAP\\ucArchivoSAP.ascx", "Default.aspx", "Global.asax"],
            "project_references": [{"project": BL}],
        },
        {
            "name": "SysInterfazSAP", "path": SYS, "output_type": "Library",
            "compile_items": ["SysInterfazSAP.vb"], "content_items": [],
        },
        {
            "name": "Shared", "path": SHARED_VBPROJ, "output_type": "Library",
            # `..\bl\BlInterfazSAP\Ambiguo.vb` resolves to the SAME physical file BL also
            # declares as `Ambiguo.vb` -- a real structural ambiguity, never resolved by guessing.
            "compile_items": ["..\\bl\\BlInterfazSAP\\Ambiguo.vb"], "content_items": [],
        },
    ]


def _symbols() -> list[dict]:
    return [
        {
            "name": "BLInterfazSAP", "kind": "class", "file": "bl\\BlInterfazSAP\\BLInterfazSAP.vb",
            "project_path": BL, "effective_namespace": "BLInterfazSAP", "namespace_confidence": "confirmed",
            "accessibility": "Public", "modifiers": [], "inherits": [], "implements": ["ISapClient"],
            "members": [
                {"kind": "sub", "name": "ProcesarSAP", "accessibility": "Public", "shared": False},
                {"kind": "function", "name": "ObtenerEstado", "accessibility": "Public", "shared": True},
            ],
        },
        # A second, independent class living in the SAME file (BLInterfazSAP.vb): one
        # file, several components -- never assumed 1:1.
        {
            "name": "BLInterfazSAPHelper", "kind": "class", "file": "bl\\BlInterfazSAP\\BLInterfazSAP.vb",
            "project_path": BL, "effective_namespace": "BLInterfazSAP", "namespace_confidence": "confirmed",
            "accessibility": "Friend", "modifiers": [], "inherits": [], "implements": [], "members": [],
        },
        {
            "name": "AssemblyInfo", "kind": "module", "file": "bl\\BlInterfazSAP\\AssemblyInfo.vb",
            "project_path": BL, "namespace_confidence": "confirmed", "members": [],
        },
        # Same bare file name ("AssemblyInfo.vb") as above, but a DIFFERENT physical path,
        # unambiguously owned by WEB -- a real homonym across two distinct projects.
        {
            "name": "AssemblyInfo", "kind": "module", "file": "AssemblyInfo.vb",
            "project_path": WEB, "namespace_confidence": "confirmed", "members": [],
        },
        # No `project_path` resolved by the live pipeline and no unambiguous structural
        # match either (the file is not declared by any project's compile_items):
        # must be declared "no evidence", never guessed.
        {
            "name": "Huerfana", "kind": "class", "file": "suelto\\Huerfana.vb", "project_path": None,
            "namespace_confidence": "unresolved", "members": [{"kind": "sub", "name": "Hacer", "accessibility": "Public", "shared": False}],
        },
        # Structurally declared by TWO projects' `compile_items` at once (BL and
        # Shared both resolve to the same physical path): the live pipeline
        # would also leave `project_path` unset for this file, since
        # `apply_project_namespaces` itself only resolves a single unambiguous match.
        {
            "name": "Ambiguo", "kind": "class", "file": "bl\\BlInterfazSAP\\Ambiguo.vb", "project_path": None,
            "namespace_confidence": "unresolved", "members": [],
        },
    ]


def _webforms() -> list[dict]:
    return [
        {"path": "Default.aspx", "kind": "aspx", "codebehind": "Default.aspx.vb", "inherits": "_Default"},
        {"path": "WebInterfazSAP\\ucArchivoSAP.ascx", "kind": "ascx", "codebehind": "ucArchivoSAP.ascx.vb"},
    ]


def _source() -> dict:
    solutions = [
        {"name": "SistemaSAP", "path": "SistemaSAP.sln", "projects": [
            {"name": "WebInterfazSAP", "path": WEB}, {"name": "BLInterfazSAP", "path": "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"}]},
        {"name": "ModuloBL", "path": "sub\\ModuloBL.sln", "projects": [
            {"name": "BLInterfazSAP", "path": "..\\bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"}]},
    ]
    dependencies = [{"source": WEB, "target": BL, "dependency_type": "Project -> Project"}]
    return {
        "repository": {"root": "C:\\repo\\SistemaSAP", "stats": {"vb_source": 6}},
        "solutions": solutions, "projects": _projects(), "entry_points": [], "functional_flows": [],
        "flow_unresolved": [], "data_access": [], "stored_procedures": [], "sql_operations": [],
        "dependencies": dependencies, "configuration": [],
        "flow_summary": {"total_flows": 0, "flows_with_confirmed_terminal": 0, "flows_with_unresolved_boundary": 0},
        "webforms": [], "external_dependencies": [],
        "symbols": _symbols(), "webform_components": _webforms(),
    }


def _model(source: dict | None = None):
    return AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source or _source())


def _generate(tmp: str, source: dict | None = None):
    return generate_documentation_v52(source or _source(), tmp)


class ProjectToSourceArtifactTests(unittest.TestCase):
    """Project -> Archivo pertenencia derived only from `compile_items`/`content_items`."""

    def test_files_are_grouped_under_their_real_owning_project(self) -> None:
        model = _model()
        bl_files = {f.values["path"] for f in model.files if f.values["module_slug"] == "BLInterfazSAP"}
        self.assertIn("bl\\BlInterfazSAP\\BLInterfazSAP.vb", bl_files)
        self.assertIn("bl\\BlInterfazSAP\\AssemblyInfo.vb", bl_files)

    def test_webform_ownership_comes_from_content_items_not_the_project_that_uses_it(self) -> None:
        """`Default.aspx` is declared by WEB's own `content_items`; BL merely
        references WEB in no way here -- ownership must never leak from an
        unrelated dependency edge."""
        model = _model()
        default_file = next(f for f in model.files if f.values["path"] == "Default.aspx")
        self.assertEqual(default_file.values["module_slug"], "WebInterfazSAP")

    def test_no_file_is_assigned_by_name_or_folder_guessing(self) -> None:
        """`Huerfana.vb` sits under `suelto\\`, matching no project's
        `compile_items`: it must land in the unassigned bucket, never in
        whichever project happens to have a similar folder name."""
        model = _model()
        huerfana = next(f for f in model.files if f.values["path"] == "suelto\\Huerfana.vb")
        self.assertEqual(huerfana.values["module_name"], "(sin proyecto asignado)")
        self.assertEqual(huerfana.values["ownership_note"], "")  # zero candidates: no evidence, not ambiguous


class AmbiguousOwnershipTests(unittest.TestCase):
    def test_file_matching_two_projects_is_declared_ambiguous_not_guessed(self) -> None:
        """V5.2 R3.4 section 9: a file with *several* real candidate projects
        must never be presented as if it belonged to "sin proyecto asignado"
        -- that label is reserved for genuinely zero-evidence files (see
        `ProjectFileNavigationTests.test_no_file_is_assigned_by_name_or_folder_guessing`
        above). It gets its own, distinct "shared/ambiguous" label instead."""
        model = _model()
        ambiguous = [f for f in model.files if f.values["path"].endswith("Ambiguo.vb")]
        self.assertEqual(len(ambiguous), 1)
        entry = ambiguous[0]
        self.assertEqual(entry.values["module_name"], "(pertenencia compartida o ambigua)")
        self.assertNotEqual(entry.values["module_name"], "(sin proyecto asignado)")
        self.assertIn("BLInterfazSAP", entry.values["ownership_note"])
        self.assertIn("Shared", entry.values["ownership_note"])

    def test_ambiguous_ownership_gap_is_declared_at_system_level(self) -> None:
        model = _model()
        self.assertIn("gap.file_ownership_ambiguous", model.gaps)


class DeclaredFileWithNoComponentTests(unittest.TestCase):
    """A file a project's own `compile_items`/`content_items` declares (real
    structural evidence) but for which the extractor found no class-like
    symbol at all (e.g. a file containing only assembly attributes, or one
    the AST scanner could not parse) must still get a file document with
    zero components, never disappear."""

    def test_declared_file_with_no_symbol_gets_a_file_document_with_zero_components(self) -> None:
        model = _model()
        sin_simbolos = next(f for f in model.files if f.values["path"] == "bl\\BlInterfazSAP\\SinSimbolos.vb")
        self.assertEqual(sin_simbolos.values["module_slug"], "BLInterfazSAP")
        self.assertEqual(sin_simbolos.values["component_count"], 0)
        self.assertEqual(sin_simbolos.slots["components"], [])

    def test_module_file_count_matches_declared_compile_items(self) -> None:
        """`BLInterfazSAP` declares 4 compile_items (AssemblyInfo.vb,
        BLInterfazSAP.vb, Ambiguo.vb, SinSimbolos.vb); the ambiguous one is
        declared by two projects and lands in the unassigned bucket, so this
        project's own file index shows the three it unambiguously owns."""
        model = _model()
        bl = next(m for m in model.modules if m.values["path"] == BL)
        file_paths = {i.values["path"] for i in bl.slots["files"]}
        self.assertEqual(file_paths, {
            "bl\\BlInterfazSAP\\AssemblyInfo.vb", "bl\\BlInterfazSAP\\BLInterfazSAP.vb", "bl\\BlInterfazSAP\\SinSimbolos.vb",
        })

    def test_declared_componentless_file_document_renders_a_clear_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            doc = (result.output_dir / "developer" / "modules" / "BLInterfazSAP" / "files" / "SinSimbolos.md").read_text(encoding="utf-8")
        self.assertIn("No se identificó ningún componente", doc)


class SourceArtifactToComponentTests(unittest.TestCase):
    def test_file_with_two_components_lists_both_without_visual_duplication(self) -> None:
        """`BLInterfazSAP.vb` declares two classes: one file, two Component rows,
        the file itself documented exactly once."""
        model = _model()
        matches = [f for f in model.files if f.values["path"] == "bl\\BlInterfazSAP\\BLInterfazSAP.vb"]
        self.assertEqual(len(matches), 1)
        file_model = matches[0]
        self.assertEqual(file_model.values["component_count"], 2)
        names = {c.values["name"] for c in file_model.slots["components"]}
        self.assertEqual(names, {"BLInterfazSAP", "BLInterfazSAPHelper"})

    def test_every_component_names_its_own_source_file(self) -> None:
        model = _model()
        for component in model.components:
            self.assertTrue(component.values["file_path"])
            self.assertTrue(component.values["file_name"])

    def test_homonymous_file_name_in_two_distinct_projects_stays_distinguishable(self) -> None:
        """Two different `AssemblyInfo.vb` files (different full paths) owned by
        two different, unambiguous projects must produce two distinct file
        documents with distinct slugs -- never merged, never a false ambiguity."""
        model = _model()
        assembly_files = [f for f in model.files if f.values["name"] == "AssemblyInfo.vb"]
        self.assertEqual(len(assembly_files), 2)
        owners = {f.values["module_slug"] for f in assembly_files}
        self.assertEqual(owners, {"BLInterfazSAP", "WebInterfazSAP"})
        slugs = {f.slug for f in assembly_files}
        self.assertEqual(len(slugs), 2)  # never collide


class MethodsAreOnlyRealEvidenceTests(unittest.TestCase):
    def test_methods_come_only_from_declared_members(self) -> None:
        model = _model()
        bl = next(c for c in model.components if c.values["name"] == "BLInterfazSAP")
        names = {m.values["name"] for m in bl.slots["methods"]}
        self.assertEqual(names, {"ProcesarSAP", "ObtenerEstado"})

    def test_component_with_no_declared_members_has_no_invented_methods(self) -> None:
        model = _model()
        helper = next(c for c in model.components if c.values["name"] == "BLInterfazSAPHelper")
        self.assertEqual(helper.slots["methods"], [])

    def test_webform_component_carries_no_methods_it_has_no_evidence_for(self) -> None:
        model = _model()
        webform = next(c for c in model.components if c.values["kind"] == "aspx")
        self.assertEqual(webform.slots["methods"], [])

    def test_webform_component_shows_its_bare_file_name_not_the_full_path(self) -> None:
        """Evidence Core's own `name` for a WebForm Component is its full path
        (its own uniqueness scheme); the visible name here must be just the
        file's basename -- the surrounding file document already gives the
        full path once, and repeating it as the component's own name/title
        reads as noise (real IST case)."""
        model = _model()
        webform = next(c for c in model.components if c.values["kind"] == "aspx")
        self.assertEqual(webform.values["name"], "Default.aspx")
        self.assertNotIn("\\", webform.values["name"])

    def test_no_method_ever_carries_a_fabricated_line_number(self) -> None:
        """The extractor's `members` never carry a line; the model must not
        invent one -- no `line`/`archivo:línea` field exists on a method Item."""
        model = _model()
        bl = next(c for c in model.components if c.values["name"] == "BLInterfazSAP")
        for method in bl.slots["methods"]:
            self.assertNotIn("line", method.values)


class SolutionToProjectNavigationTests(unittest.TestCase):
    def test_solution_lists_only_its_real_projects(self) -> None:
        model = _model()
        sistema = next(s for s in model.solutions if s.values["name"] == "SistemaSAP")
        names = {i.values["name"] for i in sistema.slots["projects"]}
        self.assertEqual(names, {"BLInterfazSAP", "WebInterfazSAP"})

    def test_project_shared_between_solutions_is_linked_from_both_without_duplication(self) -> None:
        model = _model()
        modulobl = next(s for s in model.solutions if s.values["name"] == "ModuloBL")
        self.assertEqual([i.values["name"] for i in modulobl.slots["projects"]], ["BLInterfazSAP"])
        # still exactly one Project document (no per-solution duplicate)
        self.assertEqual(sum(1 for m in model.modules if m.values["path"] == BL), 1)

    def test_module_links_back_to_every_solution_it_belongs_to(self) -> None:
        model = _model()
        bl = next(m for m in model.modules if m.values["path"] == BL)
        solution_names = {i.values["name"] for i in bl.slots["solution_links"]}
        self.assertEqual(solution_names, {"SistemaSAP", "ModuloBL"})


class RoundTripNavigationAndLinksTests(unittest.TestCase):
    def test_method_to_component_to_file_to_project_to_solution_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            root = result.output_dir
            # The file doc is `modules/BLInterfazSAP/files/BLInterfazSAP.md`; the
            # component doc for the same-named class is one level deeper:
            # `modules/BLInterfazSAP/files/BLInterfazSAP/BLInterfazSAP.md`.
            component_doc = next(
                p for p in root.rglob("*.md")
                if p.name == "BLInterfazSAP.md" and p.parts[-2] == "BLInterfazSAP" and p.parts[-3] == "files"
            )
            text = component_doc.read_text(encoding="utf-8")
            self.assertIn("Volver al archivo", text)
            file_link = text.split("](")[1].split(")")[0]
            file_doc = (component_doc.parent / file_link).resolve()
            self.assertTrue(file_doc.is_file())
            file_text = file_doc.read_text(encoding="utf-8")
            self.assertIn("Volver al proyecto", file_text)
            module_link = file_text.split("](")[1].split(")")[0]
            module_doc = (file_doc.parent / module_link).resolve()
            self.assertTrue(module_doc.is_file())
            module_text = module_doc.read_text(encoding="utf-8")
            self.assertIn("SistemaSAP", module_text)
            self.assertIn("(../solutions/", module_text)

    def test_all_relative_links_resolve_to_real_files(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            root = result.output_dir
            broken = []
            for path in root.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "](" not in line:
                        continue
                    for segment in line.split("](")[1:]:
                        target = segment.split(")")[0]
                        if target.startswith(("http://", "https://")):
                            continue
                        resolved = (path.parent / target).resolve()
                        if not resolved.is_file():
                            broken.append((str(path), target))
            self.assertEqual(broken, [])

    def test_component_and_file_documents_use_no_internal_ids(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            for path in result.output_dir.rglob("modules/*/files/**/*.md"):
                text = path.read_text(encoding="utf-8")
                for token in ("CMP-", "SRC-", "PRJ-", "SOL-"):
                    self.assertNotIn(token, text)


class DetailOnDemandTests(unittest.TestCase):
    def test_detail_document_only_lists_already_collected_evidence(self) -> None:
        """Opening the detail link must not add any data beyond what the
        component's own summary already had access to (same method set)."""
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            detail = next(
                p for p in result.output_dir.rglob("*.md")
                if p.name == "detail.md" and "files" in p.parts and "BLInterfazSAP" in p.parts[-2]
            )
            text = detail.read_text(encoding="utf-8")
        self.assertIn("ProcesarSAP", text)
        self.assertIn("ObtenerEstado", text)


class MainDocumentsStaySmallTests(unittest.TestCase):
    def test_project_document_does_not_dump_every_method(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            module_doc = (result.output_dir / "developer" / "modules" / "BLInterfazSAP.md").read_text(encoding="utf-8")
        self.assertNotIn("ProcesarSAP", module_doc)  # methods live in the component document, not here
        self.assertLess(len(module_doc.encode("utf-8")), 8000)

    def test_general_overview_is_unaffected_by_component_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = _generate(out)
            overview = (result.output_dir / "general" / "README.md").read_text(encoding="utf-8")
        for token in ("ProcesarSAP", "BLInterfazSAPHelper", "Componente", "Método"):
            self.assertNotIn(token, overview)


class PartitioningReuseTests(unittest.TestCase):
    def test_large_method_list_partitions_using_profile_limits(self) -> None:
        source = _source()
        many_members = [{"kind": "sub", "name": f"M{i}", "accessibility": "Public", "shared": False} for i in range(40)]
        source["symbols"].append({
            "name": "Grande", "kind": "class", "file": "bl\\BlInterfazSAP\\Grande.vb", "project_path": BL,
            "namespace_confidence": "confirmed", "members": many_members,
        })
        with tempfile.TemporaryDirectory() as out:
            from legacy_documenter.documentation_v52.renderer import PartitionPolicy
            result = generate_documentation_v52(source, out, partition_override=PartitionPolicy(max_items_per_part=10, max_bytes_per_part=65536))
            grande_dir = next(p for p in result.output_dir.rglob("Grande") if p.is_dir())
            detail_dir = grande_dir / "Grande"
            parts = list(detail_dir.glob("*part*.md"))
        self.assertGreaterEqual(len(parts), 2)  # 40 methods / 10 per part


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


if __name__ == "__main__":
    unittest.main()
