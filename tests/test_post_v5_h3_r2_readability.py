"""Post-V5 H3-R2: visual readability by deterministic decomposition + band wrapping (layout/decomposition only).

Dense data is injected into an in-memory visual context (persisted baseline untouched): extra libraries on the fixture projects,
extra flows reaching stored procedures, and a long linear flow.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.documentation_v52.categories import KEEP_TECHNICAL, Item
from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration import ai_interpretation
from legacy_documenter.visuals.builders import build_observable_flow, build_project_layer_map, build_system_map
from legacy_documenter.visuals.decompose import DENSE_EDGES, build_data_interaction_maps, build_dependency_maps
from legacy_documenter.visuals.layout import MAX_COLS, layout
from legacy_documenter.visuals.model import CONFIRMED, INFERRED, UNRESOLVED, Edge, Node, VisualProjection, validate_projection
from legacy_documenter.visuals.package import generate_visuals, load_context
from legacy_documenter.visuals.svg import render_svg
from tests.test_post_v5_h2_audience_docs import H2Base, tree_digest


def lib(name: str, cls: str) -> Item:
    return Item({"name": name, "path": "", "class": cls}, KEEP_TECHNICAL, level=3)


def densify(ctx):
    """Dependencies: project references + many libraries per class on the fixture projects."""
    mods = {m.values["name"]: m for m in ctx.modules.values()}
    web, service, repo = mods["Web"], mods["CustomerService"], mods["CustomerRepository"]
    for src, dst in ((web, service), (service, repo)):
        src.slots["project_refs_out"] = [Item({"name": dst.values["name"], "path": dst.values["path"]}, KEEP_TECHNICAL, level=3)]
        dst.slots["project_refs_in"] = [Item({"name": src.values["name"], "path": src.values["path"]}, KEEP_TECHNICAL, level=3)]
    web.slots["libraries"] = [lib(f"Plat{i:02d}", "platform") for i in range(17)] + [lib(f"Unc{i:02d}", "unclassified") for i in range(6)] + [lib(f"Int{i}", "internal") for i in range(3)]
    service.slots["libraries"] = [lib(f"Plat{i:02d}", "platform") for i in range(4)] + [lib("Unc00", "unclassified")]
    repo.slots["libraries"] = [lib(f"Plat{i:02d}", "platform") for i in range(2)]
    return ctx


def add_flows(ctx, n_screens=14, per_screen=3):
    """Extra screens of the Web project, each reaching several stored procedures with recognisable (and unrecognisable) verbs."""
    web_path = next(m.values["path"] for m in ctx.modules.values() if m.values["name"] == "Web")
    verbs = ["TRAER", "GRABAR", "ELIMINAR", "ACTUALIZAR", "PROCESAR", "BUSCAR_Y_GRABAR"]
    for s in range(n_screens):
        for j in range(per_screen):
            fid, ep = f"FLOW-T{s:02d}{j}", f"EP-T{s:02d}{j}"
            name = f"PKG_T.{verbs[(s + j) % len(verbs)]}_OBJ{(s * 3 + j) % 17:02d}"
            ctx.ep_project[ep] = web_path
            ctx.flows[fid] = {"id": fid, "entry_point_id": ep, "webform": f"Web\\Screen{s:02d}.aspx", "event": "Click", "handler": "h", "nodes": [
                {"id": f"{fid}-sp", "type": "StoredProcedure", "label": name, "project": None}], "edges": [], "terminal_operations": [f"DAO-T{s:02d}{j}"]}
    return ctx


def long_flow(ctx, steps=11) -> str:
    """A synthetic linear flow: screen -> event -> handler -> method chain -> stored procedure (+ one unresolved call)."""
    fid = "FLOW-LONG"
    nodes = [{"id": "scr", "type": "WebForm", "label": "Web\\Long.aspx", "project": None}, {"id": "ev", "type": "Event", "label": "Web\\Long.aspx::b.Click", "project": None},
             {"id": "hd", "type": "Handler", "label": "b_Click", "project": None}]
    edges = [{"source": "scr", "target": "ev", "type": "WebForm -> Event", "confidence": "confirmed", "evidence_refs": ["EP-L"]},
             {"source": "ev", "target": "hd", "type": "Event -> Handler", "confidence": "confirmed", "evidence_refs": ["EP-L"]}]
    prev = "hd"
    for i in range(steps):
        nodes.append({"id": f"m{i}", "type": "Method", "label": f"Web\\Web.vbproj::c{i}.m{i}", "project": None})
        edges.append({"source": prev, "target": f"m{i}", "type": "Handler -> Method" if i == 0 else "Method -> Method", "confidence": "confirmed", "evidence_refs": [f"CALL-{i}"]})
        prev = f"m{i}"
    nodes += [{"id": "sp", "type": "StoredProcedure", "label": "PKG.TRAER_X", "project": None}, {"id": "dao", "type": "DataAccessOperation", "label": "DAO-1", "project": None},
              {"id": "un", "type": "UnresolvedCall", "label": "dbc.Rollback()", "project": None}]
    edges += [{"source": prev, "target": "dao", "type": "Method -> DataAccessOperation", "confidence": "confirmed", "evidence_refs": ["DAO-1"]},
              {"source": "dao", "target": "sp", "type": "DataAccessOperation -> StoredProcedure", "confidence": "confirmed", "evidence_refs": ["DAO-1"]},
              {"source": prev, "target": "un", "type": "Method -> UnresolvedCall", "confidence": "unresolved", "evidence_refs": ["CALL-U"]}]
    ctx.flows[fid] = {"id": fid, "entry_point_id": "EP-L", "webform": "Web\\Long.aspx", "event": "Click", "handler": "b_Click", "nodes": nodes, "edges": edges, "terminal_operations": ["DAO-1"]}
    return fid


class DecompositionBase(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.area = next(iter(load_context(cls.baseline).solutions))

    def ctx(self, **kw):
        return add_flows(densify(load_context(self.baseline, **kw)))


class DependencyDecompositionTests(DecompositionBase):
    def test_small_scope_is_returned_unchanged(self):
        plain = load_context(self.baseline)
        maps = build_dependency_maps(plain, area=self.area)
        self.assertEqual(len(maps), 1)
        self.assertIsNone(maps[0].decomposition)
        self.assertNotIn("decomposition", maps[0].to_dict())

    def test_dense_map_decomposes_deterministically(self):
        a = [p.to_json() for p in build_dependency_maps(self.ctx(), area=self.area)]
        b = [p.to_json() for p in build_dependency_maps(self.ctx(), area=self.area)]
        self.assertGreater(len(a), 3)
        self.assertEqual(a, b)

    def test_summary_is_small_and_details_are_bounded(self):
        maps = build_dependency_maps(self.ctx(), area=self.area)
        summary, details = maps[0], maps[1:]
        self.assertEqual(summary.decomposition["role"], "summary")
        self.assertLessEqual(len(summary.edges), DENSE_EDGES)
        self.assertFalse(summary.partial["partial"])             # decomposed, not partial: the detail exists in the children
        for child in details:
            validate_projection(child)
            max_out = max((sum(1 for e in child.edges if e.source == n.id) for n in child.nodes), default=0)
            self.assertLessEqual(max_out, 14)                      # bounded fan-out per rendered panel

    def test_summary_and_details_preserve_every_relationship(self):
        ctx = self.ctx()
        expected_libs = {(m.values["name"], l.values["name"], l.values["class"]) for m in ctx.modules.values() for l in m.slots.get("libraries", [])}
        expected_refs = {(m.values["name"], i.values["name"]) for m in ctx.modules.values() for i in m.slots.get("project_refs_out", [])}
        maps = build_dependency_maps(ctx, area=self.area)
        summary, details = maps[0], maps[1:]
        # summary metadata keeps the exact members per project and class
        from_summary = {(proj, name, n.metadata["class"]) for n in summary.nodes if n.metadata.get("aggregate") for proj, names in n.metadata["by_project"].items() for name in names}
        self.assertEqual(from_summary, expected_libs)
        # details carry the same relations as concrete edges
        from_details = set()
        refs_details = set()
        for child in details:
            labels = {n.id: n for n in child.nodes}
            focal = child.scope["label"]
            for e in child.edges:
                if e.relation == "uses_library":
                    from_details.add((focal, labels[e.target].label, labels[e.target].metadata["class"]))
                if e.relation == "references":
                    refs_details.add((labels[e.source].label, labels[e.target].label))
        self.assertEqual(from_details, expected_libs)
        self.assertEqual(refs_details, expected_refs)
        # project references are also in the summary
        names = {n.id: n.label for n in summary.nodes}
        self.assertEqual({(names[e.source], names[e.target]) for e in summary.edges if e.relation == "references"}, expected_refs)

    def test_parent_child_metadata_is_stable_and_consistent(self):
        maps = build_dependency_maps(self.ctx(), area=self.area)
        again = build_dependency_maps(self.ctx(), area=self.area)
        summary, details = maps[0], maps[1:]
        self.assertEqual(summary.decomposition["children"], [c.id for c in details])
        self.assertEqual(summary.decomposition["child_count"], len(details))
        self.assertEqual([c.id for c in details], [c.id for c in again[1:]])
        by_focal = {}
        for c in details:
            self.assertEqual(c.decomposition["role"], "detail")
            self.assertEqual(c.decomposition["parent_projection_id"], summary.id)
            by_focal.setdefault(c.decomposition["focal_project"], []).append(c.decomposition)
        for parts in by_focal.values():
            self.assertEqual([d["part_index"] for d in parts], list(range(1, len(parts) + 1)))
            self.assertTrue(all(d["part_count"] == len(parts) for d in parts))

    def test_statuses_and_refs_are_unchanged_by_decomposition(self):
        maps = build_dependency_maps(self.ctx(), area=self.area)
        for p in maps:
            for g in p.groups:
                if g.label.startswith("Sin clasificar"):
                    self.assertEqual(g.status, UNRESOLVED)
                if g.label.startswith("Biblioteca de la plataforma"):
                    self.assertEqual(g.status, INFERRED)
            for e in p.edges:
                self.assertEqual(e.status, CONFIRMED)
                self.assertTrue(e.source_refs and all(r.startswith("PRJ-") for r in e.source_refs))

    def test_children_bound_is_recorded_not_silent(self):
        maps = build_dependency_maps(self.ctx(max_children=2), area=self.area)
        summary = maps[0]
        self.assertLessEqual(len(maps) - 1, 2)
        self.assertGreater(summary.decomposition["omitted_count"], 0)
        self.assertTrue(summary.decomposition["unexpanded_projects"])
        members = {(proj, n_) for n in summary.nodes if n.metadata.get("aggregate") for proj, ns in n.metadata["by_project"].items() for n_ in ns}
        self.assertTrue(members)                                     # the libraries of unexpanded projects are still listed in the summary


class DataInteractionDecompositionTests(DecompositionBase):
    def test_small_scope_is_returned_unchanged(self):
        maps = build_data_interaction_maps(load_context(self.baseline), area=self.area)
        self.assertEqual(len(maps), 1)
        self.assertIsNone(maps[0].decomposition)

    def test_dense_map_decomposes_deterministically_and_counts_add_up(self):
        a = build_data_interaction_maps(self.ctx(), area=self.area)
        b = build_data_interaction_maps(self.ctx(), area=self.area)
        self.assertEqual([p.to_json() for p in a], [p.to_json() for p in b])
        summary, details = a[0], a[1:]
        self.assertGreater(len(details), 1)
        dec = summary.decomposition
        summary_relations = sum(e.metadata["relations"] for e in summary.edges)
        detail_relations = sum(1 for c in details for e in c.edges)
        self.assertEqual(summary_relations, dec["relation_total"])
        self.assertEqual(detail_relations, dec["relation_total"])      # summary counts equal the detailed relationship totals
        self.assertEqual(dec["relation_pairs"], dec["relation_total"])

    def test_no_relationship_disappears(self):
        ctx = self.ctx()
        maps = build_data_interaction_maps(ctx, area=self.area)
        summary, details = maps[0], maps[1:]
        from_summary = {tuple(pair) for e in summary.edges for pair in e.metadata["members"]}
        from_details = set()
        for c in details:
            names = {n.id: n for n in c.nodes}
            from_details |= {(names[e.source].label, names[e.target].label) for e in c.edges}
        self.assertEqual(from_summary, from_details)
        self.assertTrue(any(o.startswith("PKG_T.") for _s, o in from_details))

    def test_categories_stay_inferred_and_edges_traceable(self):
        maps = build_data_interaction_maps(self.ctx(), area=self.area)
        summary, details = maps[0], maps[1:]
        self.assertTrue(all(n.status in (INFERRED, UNRESOLVED) for n in summary.nodes if n.type == "data_category"))
        self.assertTrue(all(e.status in (INFERRED, UNRESOLVED) and e.source_refs for e in summary.edges))
        for c in details:
            validate_projection(c)
            self.assertTrue(all(g.status in (INFERRED, UNRESOLVED) for g in c.groups))
            self.assertTrue(all(e.status == CONFIRMED and e.source_refs for e in c.edges))
            self.assertTrue(all("inferred from the operation name" in n.metadata.get("action_rule", "") for n in c.nodes if n.type == "data_object"))

    def test_detail_parts_have_consistent_metadata(self):
        maps = build_data_interaction_maps(self.ctx(), area=self.area)
        summary, details = maps[0], maps[1:]
        self.assertEqual(summary.decomposition["children"], [c.id for c in details])
        for c in details:
            self.assertEqual(c.decomposition["parent_projection_id"], summary.id)
            self.assertTrue(1 <= c.decomposition["part_index"] <= c.decomposition["part_count"])


class FlowWrappingTests(DecompositionBase):
    def test_long_flow_wraps_into_bands_keeping_logical_order(self):
        ctx = self.ctx()
        p = build_observable_flow(ctx, long_flow(ctx))
        lay = layout(p)
        self.assertGreater(len(lay.bands), 1)
        self.assertLessEqual(lay.width, 1500)                         # fits a normal browser viewport
        id_of = {n.metadata["evidence_node"]: n.id for n in p.nodes if "evidence_node" in n.metadata}
        by_edge = [(lay.nodes[e.source], lay.nodes[e.target]) for e in p.edges if e.source in lay.nodes and e.target in lay.nodes]
        for src, dst in by_edge:
            self.assertLessEqual(src.column, dst.column)              # logical layer order is never reversed
            self.assertLessEqual(src.band, dst.band)                  # execution order never runs upwards
            if src.band == dst.band and src.column < dst.column:
                self.assertLess(src.x, dst.x)                         # inside a band the flow reads left to right
        screen, handler = lay.nodes[id_of["scr"]], lay.nodes[id_of["hd"]]
        self.assertEqual((screen.band, screen.column), (0, 0))
        self.assertLess(screen.x, handler.x)
        columns = sorted({pl.column for pl in lay.nodes.values()})
        self.assertEqual(columns, list(range(len(columns))))          # the original layer order is preserved column by column
        rects = [(pl.x, pl.y, pl.x + pl.w, pl.y + pl.h) for pl in lay.nodes.values()]
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1], "nodes overlap")

    def test_wrapped_svg_is_well_formed_orthogonal_and_keeps_statuses(self):
        ctx = self.ctx()
        svg = render_svg(build_observable_flow(ctx, long_flow(ctx)))
        ET.fromstring(svg)
        self.assertIn("Sección 1 de", svg)
        self.assertRegex(svg, r'd="M\d+ \d+ L\d+ \d+ L\d+ \d+ L\d+ \d+ L\d+ \d+ L\d+ \d+"')   # continuation edge: right, down, left, down, right
        self.assertIn("! NO RESUELTO", svg)                           # unresolved stays unresolved
        self.assertIn('data-status="UNRESOLVED"', svg)

    def test_short_flows_are_not_wrapped(self):
        ctx = load_context(self.baseline)
        for fid in ctx.flows:
            p = build_observable_flow(ctx, fid)
            lay = layout(p)
            self.assertLessEqual(lay.columns, MAX_COLS + 8)
            if lay.columns <= MAX_COLS:
                self.assertEqual(len(lay.bands), 1)


class AcceptedDiagramsUnchangedTests(DecompositionBase):
    def test_system_map_and_project_layer_map_have_no_r2_artifacts(self):
        ctx = self.ctx()
        for p in (build_system_map(ctx), build_system_map(ctx, self.area), build_project_layer_map(ctx, area=self.area)):
            self.assertNotIn("decomposition", p.to_dict())
            svg = render_svg(p)
            self.assertNotIn("Sección", svg)
            self.assertNotIn("Etiquetas repetidas", svg)
            self.assertEqual(len(layout(p).bands), 1)

    def test_label_suppression_only_in_dense_diagrams_and_never_hides_counts(self):
        def chain(n, label):
            nodes = [Node(f"n{i}", f"n{i}", "project", CONFIRMED, ["R"]) for i in range(n + 1)]
            edges = [Edge("n0", f"n{i}", f"r{i}", CONFIRMED, ["R"], label) for i in range(1, n + 1)]
            return VisualProjection("dependency-map", "t", "technical_overview", {"type": "x", "id": "x", "label": "x"}, nodes, edges)
        few = render_svg(chain(8, "usa"))
        self.assertEqual(few.count(">usa<"), 8)                       # <= 12 edges: printed exactly as before
        many = render_svg(chain(20, "usa"))
        self.assertEqual(many.count(">usa<"), 0)
        self.assertIn("Etiquetas repetidas no impresas en cada relación: «usa» × 20", many)
        counts = render_svg(chain(20, "3"))
        self.assertEqual(counts.count(">3<"), 20)                      # numeric labels are data, never suppressed


class PackageDecompositionTests(DecompositionBase):
    def test_package_has_stable_filenames_manifest_links_and_is_byte_identical(self):
        outs = []
        for name in ("a", "b"):
            out = self.tmp / f"vis_{name}"
            result = generate_visuals(self.ctx(), out, areas=[self.area], kinds=["dependency-map", "data-interaction-map", "system-map"])
            outs.append((out, result))
        self.assertEqual(tree_digest(outs[0][0]), tree_digest(outs[1][0]))
        manifest = json.loads((outs[0][0] / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        rels = [d["svg"] for d in manifest["diagrams"]]
        self.assertEqual(rels, sorted(rels))                            # stable ordering
        by_id = {d["id"]: d for d in manifest["diagrams"]}
        summaries = [d for d in manifest["diagrams"] if d.get("decomposition", {}).get("role") == "summary"]
        self.assertEqual(len(summaries), 2)
        self.assertEqual(manifest["selection"]["decomposed_diagrams"], 2)
        for s_ in summaries:
            for cid in s_["decomposition"]["children"]:
                child = by_id[cid]
                self.assertEqual(child["parent_id"], s_["id"])
                self.assertIn(".details/", child["svg"])               # children live under <kind>.details/ next to their summary
                self.assertTrue((outs[0][0] / child["svg"]).is_file() and (outs[0][0] / child["model"]).is_file())
                ET.parse(outs[0][0] / child["svg"])
        for d in manifest["diagrams"]:
            self.assertEqual(set(d["metrics"]), {"canvas_width", "canvas_height", "edges_per_node", "max_out_degree"})

    def test_generation_needs_no_provider_source_scan_and_leaves_the_baseline_untouched(self):
        from legacy_documenter.cli import full_pipeline, pipeline_stages

        def forbidden(*a, **k):
            raise AssertionError("analysis must not run")
        ctx = self.ctx()
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(full_pipeline, "run_full_pipeline", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            generate_visuals(ctx, self.tmp / "vis_guard", areas=[self.area])
        self.assertEqual(guard.call_count, 0)
        self.assertEqual(tree_digest(self.baseline), self.before)

    def test_cli_exposes_max_children(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            cli_main(["visuals", "--help"])
        self.assertIn("--max-children", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
