"""Post-V5 H5: defects found validating the complete IST estate from persisted Evidence."""
import json
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.behavior.evidence import solution_has_project
from legacy_documenter.behavior.prototype import _view_projects
from legacy_documenter.product import package as K
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase


class SolutionMembershipResolution(unittest.TestCase):
    def test_project_in_subfolder_is_found_relative_to_the_solution_directory(self):
        sol = {"name": "WebAmbiente", "path": r"WebAmbiente\WebAmbiente.sln", "projects": [{"path": "WebAmbiente.vbproj"}]}
        self.assertTrue(solution_has_project(sol, r"WebAmbiente\WebAmbiente.vbproj"))

    def test_parent_relative_reference_is_resolved(self):
        sol = {"name": "s", "path": r"proyectos\slnX\slnX.sln", "projects": [{"path": r"..\..\bl\blX\blX.vbproj"}]}
        self.assertTrue(solution_has_project(sol, r"bl\blX\blX.vbproj"))

    def test_same_file_name_in_another_folder_is_not_a_member(self):
        sol = {"name": "s", "path": r"proyectos\slnX\slnX.sln", "projects": [{"path": r"..\..\WebX\WebX.vbproj"}]}
        self.assertFalse(solution_has_project(sol, r"WebX\WebX\WebX.vbproj"))
        self.assertFalse(solution_has_project(sol, "WebX.vbproj"))

    def test_root_level_project_still_matches(self):
        sol = {"name": "s", "path": "sln.sln", "projects": [{"path": "A.vbproj"}]}
        self.assertTrue(solution_has_project(sol, "A.vbproj"))

    def test_plain_string_project_entries_are_accepted(self):
        sol = {"name": "s", "path": "Sln.sln", "projects": [r"Web\Web.vbproj"]}
        self.assertTrue(solution_has_project(sol, r"Web\Web.vbproj"))

    def test_record_without_solution_path_keeps_the_legacy_fallback(self):
        self.assertTrue(solution_has_project({"projects": [{"path": "A.vbproj"}]}, "A.vbproj"))


class MachineOnlyPackageForProjectsWithoutViews(BehaviorBase):
    """H5: a project without UI gets a machine-only package; no screen/view model is forced onto it."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        src = cls.bc.ctx.source
        with_views = set(_view_projects(src))
        cls.project = next(p["name"] for p in src["projects"] if p["name"] not in with_views)
        cls.out = cls.tmp / "machine_only"
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider:
            cls.manifest = K.build_package(cls.baseline, cls.out, project=cls.project, solution="SampleLegacy")
            cls.provider_calls = provider.call_count

    def read(self, rel):
        return json.loads((self.out / rel).read_text(encoding="utf-8"))

    def test_package_is_machine_only_and_says_why(self):
        self.assertEqual({p.name for p in self.out.iterdir()}, {"ai", "internal", "KNOWLEDGE_PACKAGE.json"})
        self.assertIsNone(self.manifest["human_entry_point"])
        self.assertFalse(self.manifest["human_documentation"]["applicable"])
        self.assertEqual(self.provider_calls, 0)

    def test_no_view_or_flow_is_invented(self):
        self.assertEqual(self.read("ai/views.json"), {"views": []})
        self.assertEqual(self.read("ai/flows.json"), {"flows": []})
        self.assertEqual(self.read("ai/knowledge.json")["views"], [])

    def test_scope_limit_is_unresolved_and_manifest_hashes_match(self):
        claims = self.read("ai/unresolved.json")["unresolved"][0]["claims"]
        self.assertTrue(any(c["status"] == "UNRESOLVED" and "no views" in c["basis"] for c in claims))
        self.assertTrue(all(rel for rel in self.manifest["files"]))
        self.assertTrue(Path(self.out / "ai" / "cross_project_calls.json").is_file())


class KnowledgeReferencesResolve(BehaviorBase):
    """H5: every id that knowledge.json lists exists as an id in the projections (no dangling references)."""

    def test_knowledge_lists_stable_ids_that_resolve(self):
        out = self.tmp / "ui_package"
        K.build_package(self.baseline, out, project="Web", solution="SampleLegacy")
        ids = set()

        def walk(o):
            if isinstance(o, dict):
                if isinstance(o.get("id"), str):
                    ids.add(o["id"])
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        for f in (out / "ai").glob("*.json"):
            walk(json.loads(f.read_text(encoding="utf-8")))
        k = json.loads((out / "ai" / "knowledge.json").read_text(encoding="utf-8"))
        self.assertTrue(k["data"])
        for key in ("flows", "data", "unresolved"):
            for ref in k[key]:
                self.assertIn(ref, ids, f"knowledge.{key} -> {ref}")


class WireframeStaysInsideFrame(unittest.TestCase):
    def test_cells_whose_minimum_widths_exceed_the_frame_are_scaled_down(self):
        import re
        from legacy_documenter.behavior import wireframe
        from legacy_documenter.behavior.ui_evidence import PersistedMarkup
        from legacy_documenter.evidence.ui_model import MarkupControl
        ids = [f"txtCampoMuyLargoNumero{i}" for i in range(14)]
        ctls = [MarkupControl(id=i, tag="snt:textbox", kind="text", label="", line=n + 1, attrs={}) for n, i in enumerate(ids)]
        cells = [{"items": [i], "width": "", "attrs": {}} for i in ids]
        ui = wireframe.build("WebX" + chr(92) + "ucAncha.ascx", PersistedMarkup(ctls, [{"rows": [{"cells": cells}], "attrs": {}}], 1, []),
                             "ucAncha", set())
        xs = [float(x) for x in re.findall(r'<text[^>]*[ ]x="(-?[0-9.]+)"', ui.svg)]
        self.assertTrue(xs)
        self.assertGreaterEqual(min(xs), 0)
        self.assertLessEqual(max(xs), wireframe.W)


if __name__ == "__main__":
    unittest.main()
