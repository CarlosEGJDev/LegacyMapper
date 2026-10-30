"""Post-V5 pre-H5 Gate B.1: Evidence Core closure (asset roots, menu/config navigation, usage parity, portable provenance, snapshot hash,
size reduction, acyclic behavior layer). Directed tests; no provider is ever resolved."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.adapters.vbnet_webforms_oracle.ui_extraction import UiEvidenceExtractor
from legacy_documenter.behavior.prototype import build, main as behavior_main
from legacy_documenter.behavior.ui_evidence import load_ui_evidence
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.evidence.ui_model import UI_PARTITIONS
from tests.test_post_v5_gate_b_ui_evidence_core import make_repo, quiet

PACKAGE = Path(__file__).resolve().parents[1] / "legacy_documenter"
MENU = """<NODES>
  <NODE Text="Clientes" NavigateUrl="default.aspx?url=Web/PickCustomer&amp;FUN=F1" />
  <NODE Text="Fantasma" NavigateUrl="default.aspx?url=Web/GhostView" />
  <NODE Text="Dinamico" NavigateUrl="default.aspx?url=Web/{0}" />
  <NODE Text="Inicio" url="~/HostOne.aspx" />
</NODES>
"""


def b1_repo(parent: Path, name: str = "repo") -> Path:
    repo = make_repo(parent, name)
    web = repo / "Web"
    pick = (web / "PickCustomer.ascx").read_text(encoding="utf-8")
    (web / "PickCustomer.ascx").write_text(
        pick + '<snt:HyperLink ID="icoTilde" runat="server" ImageUrl="~/img/ok.gif" /><snt:HyperLink ID="icoTildeMiss" runat="server" ImageUrl="~/img/none.gif" />\n',
        encoding="utf-8")
    two = (web / "HostTwo.aspx").read_text(encoding="utf-8")
    (web / "HostTwo.aspx").write_text(two + '<asp:Image ID="imgShared" ImageUrl="~/img/ok.gif" runat="server" />\n', encoding="utf-8")
    dup = repo / "Other" / "Area" / "Dup.ascx"
    dup.write_text(dup.read_text(encoding="utf-8") + '<asp:Image ID="imgLost" ImageUrl="~/x.gif" runat="server" />\n', encoding="utf-8")
    (repo / "Web2").mkdir()
    (repo / "Web2" / "Web2.vbproj").write_text(
        '<Project><PropertyGroup><RootNamespace>Web2</RootNamespace></PropertyGroup><ItemGroup><Content Include="..\\Web\\HostTwo.aspx" /></ItemGroup></Project>',
        encoding="utf-8")
    (web / "menu.xml").write_text(MENU, encoding="utf-8")
    return repo


def parts_of(baseline: Path) -> dict:
    return {n: json.loads((baseline / "evidence" / f"{n}.json").read_text(encoding="utf-8")) for n in UI_PARTITIONS}


class B1Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gateb1_"))
        cls.repo = b1_repo(cls.tmp / "one")
        cls.baseline = cls.tmp / "baseline"
        assert quiet(run_full_pipeline, cls.repo, cls.baseline, [], 12).status.value == "SUCCESS"
        cls.parts = parts_of(cls.baseline)
        cls.manifest = json.loads((cls.baseline / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
        cls.removed = cls.tmp / "removed"
        cls.repo.rename(cls.removed)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def asset(self, literal: str, doc_suffix: str) -> dict:
        docs = {d["id"]: d["logical_source_path"] for d in self.parts["ui_documents"]}
        return next(a for a in self.parts["ui_assets"] if a["properties"]["asset_kind"] == "asset_reference" and a["properties"]["literal"] == literal
                    and docs[a["relationships"]["document_id"]].endswith(doc_suffix))


class AssetRootTests(B1Base):
    def test_tilde_asset_resolves_against_the_single_application_root(self):
        ref = self.asset("~/img/ok.gif", "PickCustomer.ascx")
        self.assertEqual((ref["status"], ref["properties"]["resolved_logical_path"]), ("CONFIRMED", "Web/img/ok.gif"))
        self.assertEqual(ref["properties"]["resolution_basis"]["application_roots"], ["Web"])
        asset = next(a for a in self.parts["ui_assets"] if a["id"] == ref["relationships"]["asset_file"])
        self.assertEqual(len(asset["properties"]["sha256"]), 64)

    def test_missing_tilde_asset_stays_unresolved(self):
        ref = self.asset("~/img/none.gif", "PickCustomer.ascx")
        self.assertEqual((ref["status"], ref["properties"]["reason"]), ("UNRESOLVED", "ASSET_NOT_FOUND"))
        self.assertIsNone(ref["properties"]["resolved_logical_path"])

    def test_ambiguous_application_root_is_never_guessed(self):
        ref = self.asset("~/img/ok.gif", "HostTwo.aspx")
        self.assertEqual((ref["status"], ref["properties"]["reason"]), ("UNRESOLVED", "AMBIGUOUS_APPLICATION_ROOT"))
        self.assertEqual(ref["properties"]["resolution_basis"]["application_roots"], ["Web", "Web2"])

    def test_document_outside_any_project_has_no_application_root(self):
        ref = self.asset("~/x.gif", "Other/Area/Dup.ascx")
        self.assertEqual(ref["properties"]["reason"], "APPLICATION_ROOT_UNKNOWN")

    def test_wireframe_embeds_the_tilde_icon_from_evidence_with_source_removed(self):
        _doc, _bc, _v, explained = build(self.baseline, None, project="Web", solution="SampleLegacy", pilot_count=2)
        pick = next(v for v in explained.values() if v.name == "PickCustomer")
        report = pick.ui.style_report
        self.assertEqual((report["icons_total"], report["icons_resolved"]), (4, 2))           # img/ok.gif + ~/img/ok.gif resolve


class MenuConfigNavigationTests(B1Base):
    def entries(self):
        return [n for n in self.parts["ui_navigation"] if n["properties"]["relation"] == "menu_entry"]

    def test_literal_menu_targets_become_navigation_edges(self):
        by = {e["properties"]["label"]: e for e in self.entries()}
        clientes = by["Clientes"]
        self.assertEqual((clientes["status"], clientes["properties"]["mechanism"]), ("CONFIRMED", "config_url_literal"))
        self.assertEqual(clientes["properties"]["parameters"], ["FUN"])
        self.assertEqual(clientes["logical_source_path"], "Web/menu.xml")
        self.assertEqual(by["Inicio"]["status"], "CONFIRMED")
        self.assertEqual(by["Inicio"]["properties"]["mechanism"], "config_path_literal")

    def test_missing_and_dynamic_targets_remain_unresolved(self):
        by = {e["properties"]["label"]: e for e in self.entries()}
        self.assertEqual((by["Fantasma"]["status"], by["Fantasma"]["properties"]["reason"]), ("UNRESOLVED", "TARGET_NOT_FOUND"))
        self.assertEqual((by["Dinamico"]["status"], by["Dinamico"]["properties"]["reason"]), ("UNRESOLVED", "DYNAMIC_TARGET"))
        self.assertEqual(by["Dinamico"]["relationships"]["target_document_ids"], [])

    def test_menu_edges_do_not_change_invocation_semantics_and_reach_the_ai_context(self):
        ui = load_ui_evidence(self.baseline)
        self.assertTrue(all(h.mechanism != "config_url_literal" for h in ui.navigation_hits()))
        doc = ui.document("Web/PickCustomer.ascx")
        self.assertEqual([e["properties"]["label"] for e in ui.menu_entries_for(doc)], ["Clientes"])


class UsageParityTests(B1Base):
    def test_a_confirmed_incoming_view_always_has_name_references(self):
        """Regression guard for the historical H4 package: name_references 0 next to 25 confirmed incoming literals was an impossible state."""
        _d, _bc, _v, explained = build(self.baseline, None, project="Web", solution="SampleLegacy", pilot_count=2)
        pick = next(v for v in explained.values() if v.name == "PickCustomer")
        counts = pick.usage["counts"]
        self.assertGreaterEqual(counts["incoming_confirmed"], 1)
        self.assertGreaterEqual(counts["name_references"], 1)
        for v in explained.values():
            if v.usage["counts"]["incoming_confirmed"]:
                self.assertGreaterEqual(v.usage["counts"]["name_references"], 1, v.name)

    def test_unreadable_documents_are_reported_not_swallowed(self):
        files = [{"relative_path": "Web/HostOne.aspx"}, {"relative_path": "Web/Gone.ascx"}]
        extractor = UiEvidenceExtractor(self.removed, files, [], [])
        extractor.extract()
        self.assertEqual(extractor.summary["unreadable_documents"], ["Web/Gone.ascx"])
        self.assertEqual(extractor.summary["documents_extracted"], 1)
        summary = self.manifest["ui_evidence"]["extractor"]["summary"]
        self.assertEqual(summary["documents_listed"], summary["documents_extracted"])
        self.assertEqual(summary["unreadable_documents"], [])


class PortableProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gateb1_prov_"))
        cls.runs = {}
        for label, rel in (("a", "place one/ñ"), ("b", "second/deeper")):
            parent = cls.tmp / rel
            parent.mkdir(parents=True)
            repo = b1_repo(parent)
            base = cls.tmp / f"base_{label}"
            assert quiet(run_full_pipeline, repo, base, [], 12).status.value == "SUCCESS"
            out = cls.tmp / f"beh_{label}"
            with contextlib.redirect_stdout(io.StringIO()):
                assert behavior_main([str(base), "--output", str(out), "--no-pdf", "--project", "Web", "--solution", "SampleLegacy"]) == 0
            cls.runs[label] = (repo, base, out)
        changed = b1_repo(cls.tmp / "third")
        with (changed / "Web" / "PickCustomer.ascx.vb").open("a", encoding="utf-8") as fh:
            fh.write("' content change\n")
        cls.changed_base = cls.tmp / "base_c"
        assert quiet(run_full_pipeline, changed, cls.changed_base, [], 12).status.value == "SUCCESS"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def manifest(self, base):
        return json.loads((base / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))

    def test_same_source_two_roots_same_logical_identity_and_portable_hash(self):
        a, b = self.manifest(self.runs["a"][1]), self.manifest(self.runs["b"][1])
        self.assertEqual(a["source_provenance"], b["source_provenance"])
        for name in UI_PARTITIONS:
            self.assertEqual(a["partition_sha256"][name], b["partition_sha256"][name], name)

    def test_snapshot_hash_follows_content_not_location(self):
        a, c = self.manifest(self.runs["a"][1]), self.manifest(self.changed_base)
        self.assertNotEqual(a["source_provenance"]["logical_snapshot_sha256"], c["source_provenance"]["logical_snapshot_sha256"])

    def test_system_context_declares_honest_snapshot_semantics(self):
        meta = json.loads((self.runs["a"][1] / "ai_context" / "SYSTEM_CONTEXT.json").read_text(encoding="utf-8"))["metadata"]
        prov = self.manifest(self.runs["a"][1])["source_provenance"]
        self.assertEqual(meta["logical_snapshot_sha256"], prov["logical_snapshot_sha256"])
        self.assertEqual(meta["portable_evidence_sha256"], prov["portable_evidence_sha256"])
        self.assertEqual(meta["source_snapshot_sha256_semantics"], "legacy_contract_constant_not_a_content_hash")
        self.assertTrue(meta["source_snapshot_sha256"])                      # legacy field preserved for compatibility

    def test_behavioral_package_is_identical_across_roots_and_has_no_physical_path(self):
        (ra, _ba, oa), (rb, _bb, ob) = self.runs["a"], self.runs["b"]
        names = sorted(p.name for p in oa.iterdir() if p.is_file())
        self.assertEqual(names, sorted(p.name for p in ob.iterdir() if p.is_file()))
        for name in names:
            if name.endswith((".html", ".json", ".svg")):
                self.assertEqual((oa / name).read_bytes(), (ob / name).read_bytes(), name)
        needles = [str(ra), str(rb), str(ra).replace("\\", "/"), str(self.tmp), str(self.tmp).replace("\\", "/")]
        for path in list(oa.rglob("*")):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                for needle in needles:
                    self.assertNotIn(needle, text, path.name)
        baseline = json.loads((oa / "explanations.json").read_text(encoding="utf-8"))["baseline"]
        self.assertEqual(baseline["portable_evidence_sha256"], self.manifest(self.runs["a"][1])["source_provenance"]["portable_evidence_sha256"])


class SizeAndDeterminismTests(B1Base):
    def test_children_do_not_repeat_their_documents_envelope(self):
        for name in ("ui_controls", "ui_event_bindings", "ui_messages", "ui_parameters"):
            for rec in self.parts[name]:
                self.assertNotIn("source_refs", rec)
                self.assertNotIn("logical_source_path", rec)
                self.assertIn(rec["relationships"]["source_scope"], ("markup", "code_behind"))

    def test_style_profiles_are_shared_and_resolvable(self):
        profiles = {r["id"]: r for r in self.parts["ui_style_references"] if r["properties"]["style_kind"] == "style_profile"}
        styled = [c for c in self.parts["ui_controls"] if c["relationships"].get("style_profile")]
        self.assertTrue(styled)
        self.assertLess(len(profiles), len(styled) + 1)
        for c in styled:
            self.assertIn(c["relationships"]["style_profile"], profiles)
        self.assertFalse([r for r in self.parts["ui_style_references"] if r["properties"].get("style_kind") == "control_style"])

    def test_extraction_is_deterministic_after_deduplication(self):
        files = json.loads((self.baseline / "index" / "files.json").read_text(encoding="utf-8"))
        webforms = json.loads((self.baseline / "index" / "webforms.json").read_text(encoding="utf-8"))
        projects = json.loads((self.baseline / "index" / "projects.json").read_text(encoding="utf-8"))
        first = UiEvidenceExtractor(self.removed, files, webforms, projects).extract()
        second = UiEvidenceExtractor(self.removed, files, webforms, projects).extract()
        self.assertEqual(first, second)
        self.assertEqual(first, self.parts)

    def test_downstream_succeeds_with_the_source_removed(self):
        out = self.tmp / "after_removal"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(behavior_main([str(self.baseline), "--output", str(out), "--no-pdf", "--project", "Web", "--solution", "SampleLegacy"]), 0)
        self.assertTrue((out / "index.html").is_file())


class DependencyGraphTests(unittest.TestCase):
    def test_behavior_package_import_graph_is_acyclic(self):
        modules = {p.stem for p in (PACKAGE / "behavior").glob("*.py")}
        graph: dict[str, set[str]] = {m: set() for m in modules}
        for path in (PACKAGE / "behavior").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom):
                    if node.level == 1 and node.module and node.module in modules:
                        graph[path.stem].add(node.module)
                    elif node.level == 1 and node.module is None:
                        graph[path.stem].update(a.name for a in node.names if a.name in modules)
                    elif node.module and node.module.startswith("legacy_documenter.behavior."):
                        tail = node.module.rsplit(".", 1)[-1]
                        if tail in modules:
                            graph[path.stem].add(tail)
        state: dict[str, int] = {}

        def visit(n: str, trail: list[str]) -> None:
            if state.get(n) == 2:
                return
            self.assertNotEqual(state.get(n), 1, "cycle: " + " -> ".join(trail + [n]))
            state[n] = 1
            for m in sorted(graph[n]):
                visit(m, trail + [n])
            state[n] = 2

        for m in sorted(graph):
            visit(m, [])
        self.assertNotIn("ui_evidence", graph["styles"])
        self.assertIn("styles", graph["ui_evidence"])


if __name__ == "__main__":
    unittest.main()
