"""Post-V5 H3: structured visual projections (model contract, builders, deterministic layout/SVG, CLI).

Networkless and deterministic. `visuals` never resolves a provider and never scans or analyzes a source tree.
"""
from __future__ import annotations

import contextlib
import io
import json
import random
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration import ai_interpretation
from legacy_documenter.orchestration.ai_only import run_ai_only
from legacy_documenter.review.service import ApprovalService
from legacy_documenter.visuals.builders import (
    build_data_interaction_map, build_dependency_map, build_observable_flow, build_project_layer_map, build_system_map,
)
from legacy_documenter.visuals.model import (
    AI_INTERPRETATION, CANONICAL, CONFIRMED, INFERRED, KINDS, UNRESOLVED, Edge, Group, Node, VisualModelError, VisualProjection, stable_id,
    validate_projection,
)
from legacy_documenter.visuals.package import generate_visuals, load_context, load_knowledge_refs, representative_flow
from legacy_documenter.visuals.svg import render_svg
from tests.test_post_v5_h1_ai_only import make_provider
from tests.test_post_v5_h2_audience_docs import H2Base, tree_digest
from tests.test_post_v5_h2_r2_functional import build_variant

SVG_NS = "{http://www.w3.org/2000/svg}"


def run_visuals(baseline: Path, out: Path, *extra: str) -> tuple[int, dict]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli_main(["visuals", str(baseline), "--output", str(out), *extra])
    text = buf.getvalue()
    return code, json.loads(text[text.index("{"):])


def small(kind="system-map", nodes=(), edges=(), groups=(), partial=None) -> VisualProjection:
    p = VisualProjection(kind, "t", "technical_overview", {"type": "x", "id": "x", "label": "x"}, list(nodes), list(edges), list(groups))
    if partial:
        p.partial = partial
    return p


def n(i, status=CONFIRMED, refs=("R",), label=None, **kw):
    return Node(i, label or i, kw.pop("type", "project"), status, list(refs), **kw)


class ModelContractTests(unittest.TestCase):
    def test_contract_shape_and_legend(self):
        d = small(nodes=[n("a")]).to_dict()
        for key in ("contract", "contract_version", "id", "kind", "title", "audience", "scope", "nodes", "edges", "groups", "legend", "provenance", "unresolved", "partial", "metadata"):
            self.assertIn(key, d)
        self.assertEqual([x["status"] for x in d["legend"]], ["CONFIRMED", "INFERRED", "UNRESOLVED", "AI_INTERPRETATION", "CANONICAL"])
        self.assertEqual(set(d["nodes"][0]), {"id", "label", "type", "status", "source_refs", "metadata"})
        self.assertEqual(KINDS, ("system-map", "project-layer-map", "dependency-map", "observable-flow", "data-interaction-map"))

    def test_validator_rejects_contract_violations(self):
        cases = {
            "invalid status": small(nodes=[n("a", status="MAYBE")]),
            "duplicate node": small(nodes=[n("a"), n("a")]),
            "dangling edge": small(nodes=[n("a")], edges=[Edge("a", "zz", "r", CONFIRMED, ["R"])]),
            "untraceable confirmed edge": small(nodes=[n("a"), n("b")], edges=[Edge("a", "b", "r", CONFIRMED, [])]),
            "inferred edge without a rule": small(nodes=[n("a"), n("b")], edges=[Edge("a", "b", "r", INFERRED, ["R"])]),
            "confirmed node without refs": small(nodes=[n("a", refs=())]),
            "partial without reason": small(nodes=[n("a")], partial={"partial": True, "included_count": 1, "omitted_count": 2, "reason": ""}),
            "unknown group": small(nodes=[n("a", group="G-x")]),
        }
        for name, projection in cases.items():
            with self.assertRaises(VisualModelError, msg=name):
                validate_projection(projection)

    def test_status_propagation_never_strengthens_an_edge(self):
        ai, unres, inf, ok = n("ai", AI_INTERPRETATION, refs=()), n("u", UNRESOLVED, refs=()), n("i", INFERRED, refs=()), n("c")
        with self.assertRaises(VisualModelError):   # nothing touching an AI interpretation is confirmed
            validate_projection(small(nodes=[ai, ok], edges=[Edge("ai", "c", "r", CONFIRMED, ["R"])]))
        with self.assertRaises(VisualModelError):   # nothing touching an unresolved node is confirmed
            validate_projection(small(nodes=[unres, ok], edges=[Edge("c", "u", "r", CONFIRMED, ["R"])]))
        with self.assertRaises(VisualModelError):   # an inferred endpoint cannot hang off a confirmed edge
            validate_projection(small(nodes=[inf, ok], edges=[Edge("c", "i", "r", CONFIRMED, ["R"])]))
        validate_projection(small(nodes=[ai, ok], edges=[Edge("ai", "c", "r", AI_INTERPRETATION, ["R"])]))
        validate_projection(small(nodes=[unres, ok], edges=[Edge("c", "u", "r", UNRESOLVED, ["R"])]))
        validate_projection(small(nodes=[inf, ok], edges=[Edge("c", "i", "r", INFERRED, ["R"], "regla")]))

    def test_empty_graph_is_valid_and_renders(self):
        p = small()
        validate_projection(p)
        root = ET.fromstring(render_svg(p))
        self.assertEqual(root.tag, SVG_NS + "svg")
        self.assertIn("Leyenda de estados", render_svg(p))

    def test_stable_ids_do_not_depend_on_insertion_order(self):
        self.assertEqual(stable_id("N", "a", "b"), stable_id("N", "a", "b"))
        nodes = [n(f"n{i}") for i in range(8)]
        edges = [Edge(f"n{i}", f"n{i + 1}", "r", CONFIRMED, ["R"]) for i in range(7)]
        a = small(nodes=nodes, edges=edges)
        shuffled_nodes, shuffled_edges = nodes[:], edges[:]
        random.Random(3).shuffle(shuffled_nodes)
        random.Random(4).shuffle(shuffled_edges)
        b = small(nodes=shuffled_nodes, edges=shuffled_edges)
        self.assertEqual(a.to_json(), b.to_json())
        self.assertEqual(render_svg(a), render_svg(b))


class RendererTests(unittest.TestCase):
    def test_svg_escaping_and_well_formedness(self):
        evil = "<script>alert(1)</script> & \"quotes\" 'x' \x07"
        p = small(nodes=[n("a", label=evil), n("b", label="ok")], edges=[Edge("a", "b", "r", CONFIRMED, ["R"], label="<b>&")])
        svg = render_svg(p)
        ET.fromstring(svg)  # well-formed XML
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertNotIn("\x07", svg)

    def test_long_labels_are_wrapped_truncated_and_kept_in_the_tooltip(self):
        label = "ProyectoConUnNombreEnormeSinEspacios_" * 8 + " palabra " * 20
        p = small(nodes=[n("a", label=label)])
        svg = render_svg(p)
        ET.fromstring(svg)
        self.assertIn("…", svg)
        self.assertIn(f"<title>{label.strip()[:30]}", svg)           # full label stays available as the tooltip
        self.assertLessEqual(svg.count('font-size="12">'), 3 + 8)    # at most 3 wrapped lines for the node (plus legend lines)

    def test_status_is_encoded_by_pattern_and_text_not_only_colour(self):
        p = small(nodes=[n("c"), n("i", INFERRED, refs=()), n("u", UNRESOLVED, refs=()), n("a", AI_INTERPRETATION, refs=()), n("k", CANONICAL)])
        svg = render_svg(p)
        for tag in ("CONFIRMADO", "INFERIDO", "! NO RESUELTO", "IA - NO APROBADA", "OK CANÓNICO"):
            self.assertIn(tag, svg)
        for dash in ('stroke-dasharray="7 4"', 'stroke-dasharray="2 3"', 'stroke-dasharray="8 3 2 3"'):
            self.assertIn(dash, svg)
        self.assertEqual(len({line.split('stroke="')[1].split('"')[0] for line in svg.splitlines() if line.startswith("<rect") and "rx=\"7\"" in line}), 5)

    def test_same_input_is_byte_identical(self):
        p = small(nodes=[n("a"), n("b", INFERRED, refs=())], edges=[Edge("a", "b", "r", INFERRED, ["R"], "regla")])
        self.assertEqual(render_svg(p), render_svg(p))
        self.assertEqual(p.to_json(), p.to_json())


class VisualsFixtureTests(H2Base):
    """Builders and package over a real (small) persisted baseline."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctx = load_context(cls.baseline)
        cls.area = next(iter(cls.ctx.solutions))
        cls.project = next(slug for slug, m in cls.ctx.modules.items() if m.values["screens"])
        cls.flows = sorted(cls.ctx.flows)

    @staticmethod
    def with_references(ctx):
        """The fixture declares no project references: add two as persisted-model items (Web -> CustomerService -> CustomerRepository)."""
        from legacy_documenter.documentation_v52.categories import KEEP_TECHNICAL, Item

        web, service, repo = (next(m for m in ctx.modules.values() if m.values["name"] == name) for name in ("Web", "CustomerService", "CustomerRepository"))
        for src, dst in ((web, service), (service, repo)):
            src.slots["project_refs_out"] = [Item({"name": dst.values["name"], "path": dst.values["path"]}, KEEP_TECHNICAL, level=3)]
            dst.slots["project_refs_in"] = [Item({"name": src.values["name"], "path": src.values["path"]}, KEEP_TECHNICAL, level=3)]
        return ctx

    def all_projections(self):
        c, a, pr = self.ctx, self.area, self.project
        out = [build_system_map(c), build_system_map(c, a), build_project_layer_map(c, area=a), build_project_layer_map(c, project=pr),
               build_dependency_map(c, area=a), build_dependency_map(c, project=pr), build_data_interaction_map(c, area=a),
               build_data_interaction_map(c, project=pr)]
        out += [build_observable_flow(c, f) for f in self.flows]
        return out

    def test_every_projection_validates_and_is_traceable(self):
        for p in self.all_projections():
            validate_projection(p)
            for e in p.edges:
                if e.status in (CONFIRMED, CANONICAL):
                    self.assertTrue(e.source_refs, (p.kind, e.relation))
            for node in p.nodes:
                if node.status == CONFIRMED and not node.metadata.get("aggregate"):
                    self.assertTrue(node.source_refs, (p.kind, node.label))
        refs = {r for p in self.all_projections() for node in p.nodes for r in node.source_refs}
        self.assertTrue(any(r.startswith("PRJ-") for r in refs))
        self.assertTrue(any(r.startswith("FLOW-") for r in refs))
        self.assertTrue(any(r.startswith("SOL-") for r in refs))
        self.assertTrue(any(r.startswith("DAO-") for r in refs))

    def test_stable_ids_across_independent_builds(self):
        again = load_context(self.baseline)
        a = [p.to_json() for p in self.all_projections()]
        self.ctx_b, self.ctx = self.ctx, again
        try:
            b = [p.to_json() for p in self.all_projections()]
        finally:
            self.ctx = self.ctx_b
        self.assertEqual(a, b)

    def test_system_map_shows_containment_and_inferred_layers(self):
        system = build_system_map(self.ctx)
        self.assertEqual({n_.type for n_ in system.nodes}, {"system", "area", "layer"})
        self.assertTrue(all(e.status == CONFIRMED for e in system.edges if e.relation == "contains"))
        self.assertTrue(all(e.status in (INFERRED, UNRESOLVED) for e in system.edges if e.relation == "has_layer"))
        area = build_system_map(self.ctx, self.area)
        names = {n_.label for n_ in area.nodes}
        self.assertTrue({"Web", "CustomerService", "CustomerRepository"} <= names)
        self.assertTrue(all(n_.status == INFERRED for n_ in area.nodes if n_.type == "layer"))     # layers are inferences
        self.assertNotIn("función de negocio", json.dumps(area.to_dict()))                         # no business grouping implied

    def test_project_layer_map_groups_by_inferred_layer(self):
        p = build_project_layer_map(self.with_references(load_context(self.baseline)), area=self.area)
        self.assertTrue(p.groups and all(g.status in (INFERRED, UNRESOLVED) and "Capa" in g.label for g in p.groups))
        svg = render_svg(p)
        self.assertIn("Capa (inferida)", svg)
        self.assertIn('stroke-dasharray="7 4"', svg)             # the inferred-layer swimlane is dashed
        self.assertTrue(any(e.relation == "references" and e.status == CONFIRMED for e in p.edges))

    def test_dependency_map_separates_internal_platform_and_unclassified(self):
        p = build_dependency_map(self.with_references(load_context(self.baseline)), area=self.area)
        refs = [e for e in p.edges if e.relation == "references"]
        self.assertEqual(len(refs), 2)
        self.assertTrue(all(e.status == CONFIRMED and e.source_refs and e.source_refs[0].startswith("PRJ-") for e in refs))
        for g in p.groups:
            self.assertEqual(g.status, {"Biblioteca interna del repositorio": CONFIRMED}.get(g.label, g.status))
        for g in p.groups:
            if g.label.startswith("Sin clasificar"):
                self.assertEqual(g.status, UNRESOLVED)           # unclassified is never treated as confirmed third-party
            if g.label.startswith("Biblioteca de la plataforma"):
                self.assertEqual(g.status, INFERRED)

    def test_observable_flow_shows_screen_event_handler_boundary_data_and_unresolved(self):
        flow = next(f for f in self.flows if "StoredProcedure" in {nd["type"] for nd in self.ctx.flows[f]["nodes"]})
        p = build_observable_flow(self.ctx, flow)
        types = {n_.type for n_ in p.nodes}
        self.assertTrue({"screen", "event", "handler", "method", "data_object"} <= types)
        self.assertNotIn("class", types)                         # component nodes are folded into method labels / groups
        self.assertTrue(p.groups and all(g.label.startswith("Proyecto:") for g in p.groups))
        self.assertEqual(p.metadata["flow"]["flow_id"], flow)
        self.assertTrue(any(n_.type == "data_object" and n_.label == "PKG_CUSTOMER.SAVE_CUSTOMER" for n_ in p.nodes))

    def test_unresolved_nodes_and_edges_are_rendered_distinctly(self):
        flow = next(f for f in self.flows if any(nd["type"] == "UnresolvedCall" for nd in self.ctx.flows[f]["nodes"]))
        p = build_observable_flow(self.ctx, flow)
        self.assertTrue(p.unresolved and all(u["label"] for u in p.unresolved))
        svg = render_svg(p)
        self.assertIn("! NO RESUELTO", svg)
        self.assertIn('data-status="UNRESOLVED"', svg)
        self.assertIn('stroke-dasharray="2 3"', svg)
        ET.fromstring(svg)

    def test_data_interaction_map_keeps_categories_as_inferred_groups_not_facts(self):
        p = build_data_interaction_map(self.ctx, area=self.area)
        self.assertTrue(p.edges and all(e.status == CONFIRMED for e in p.edges))             # screen -> object is the confirmed fact
        self.assertTrue(p.groups and all(g.status in (INFERRED, UNRESOLVED) for g in p.groups))  # the category is inferred from the name
        self.assertTrue(all("inferred from the operation name" in n_.metadata.get("action_rule", "") for n_ in p.nodes if n_.type == "data_object"))

    def test_large_graphs_are_aggregated_never_dropped_silently(self):
        small_ctx = load_context(self.baseline, max_nodes=2)
        area = build_system_map(small_ctx, self.area)
        self.assertTrue(area.partial["partial"])
        aggregate = next(n_ for n_ in area.nodes if n_.metadata.get("aggregate"))
        self.assertEqual(area.partial["omitted_count"], aggregate.metadata["count"])
        self.assertEqual(aggregate.metadata["count"], len(aggregate.metadata["items"]))      # every omitted name is kept in the model
        full = build_system_map(self.ctx, self.area)
        covered = {n_.label for n_ in area.nodes if n_.type == "project"} | set(aggregate.metadata["items"])
        self.assertEqual(covered, {n_.label for n_ in full.nodes if n_.type == "project"})
        flow = max(self.flows, key=lambda f: len(self.ctx.flows[f]["nodes"]))
        tight = build_observable_flow(small_ctx, flow)
        self.assertTrue(tight.partial["partial"] and tight.partial["reason"])
        validate_projection(tight)
        ET.fromstring(render_svg(tight))


class AiAndKnowledgeTests(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        copy = cls.tmp / "ai_baseline"
        shutil.copytree(cls.baseline, copy)
        cls.ai = run_ai_only(copy, provider=make_provider())
        assert cls.ai.status == "SUCCESS", cls.ai.reason
        cls.ai_dir = cls.ai.ai_run_dir

    def flow_with_note(self, ctx):
        for fid in sorted(ctx.flows):
            p = build_observable_flow(ctx, fid, include_ai=True)
            if any(n_.type in ("ai_note", "canonical_note") for n_ in p.nodes):
                return p
        return None

    def test_ai_interpretation_is_drawn_only_on_request_and_never_as_confirmed(self):
        plain = load_context(self.baseline)
        for fid in plain.flows:
            self.assertFalse(any(n_.type == "ai_note" for n_ in build_observable_flow(plain, fid).nodes))
        ctx = load_context(self.baseline, load_knowledge_refs(self.ai_dir))
        p = self.flow_with_note(ctx)
        self.assertIsNotNone(p)
        note = next(n_ for n_ in p.nodes if n_.type == "ai_note")
        self.assertEqual(note.status, AI_INTERPRETATION)
        self.assertTrue(all(e.status == AI_INTERPRETATION for e in p.edges if note.id in (e.source, e.target)))
        svg = render_svg(p)
        self.assertIn("IA - NO APROBADA", svg)
        self.assertNotIn("OK CANÓNICO", svg)
        self.assertNotIn(f'data-node="{note.id}" data-status="CONFIRMED"', svg)

    def test_canonical_is_distinct_after_explicit_human_approval(self):
        copy = self.tmp / "ai_run_approved"
        shutil.copytree(self.ai_dir, copy)
        proposal_id = json.loads((copy / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]["proposal_id"]
        service = ApprovalService(copy)
        service.prepare(proposal_id, "Test Reviewer")
        service.decide(proposal_id, "APPROVE", "Test Reviewer", rationale="explicit human approval in test")
        ctx = load_context(self.baseline, load_knowledge_refs(copy))
        self.assertEqual((len(ctx.knowledge["proposals"]), len(ctx.knowledge["canonical"])), (0, 1))   # moved from AI to canonical
        p = self.flow_with_note(ctx)
        note = next(n_ for n_ in p.nodes if n_.type == "canonical_note")
        self.assertEqual(note.status, CANONICAL)
        self.assertTrue(note.source_refs)
        self.assertIn("OK CANÓNICO", render_svg(p))
        self.assertNotIn("IA - NO APROBADA", render_svg(p))


class PackageAndCliTests(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vis = cls.tmp / "visuals"
        cls.code, cls.summary = run_visuals(cls.baseline, cls.vis)

    def test_default_package_manifest_and_files(self):
        self.assertEqual((self.code, self.summary["status"]), (0, "SUCCESS"))
        manifest = json.loads((self.vis / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contract"], "LegacyMapperVisualsManifest")
        kinds = {d["kind"] for d in manifest["diagrams"]}
        self.assertEqual(kinds, set(KINDS))                       # all five mandatory kinds are produced
        for d in manifest["diagrams"]:
            for rel in (d["svg"], d["model"]):
                self.assertFalse(Path(rel).is_absolute())        # relative, deterministic paths (H4-ready)
                self.assertTrue((self.vis / rel).is_file(), rel)
            self.assertEqual(json.loads((self.vis / d["model"]).read_text(encoding="utf-8"))["id"], d["id"])
            ET.parse(self.vis / d["svg"])                         # every SVG is well-formed XML
        self.assertEqual(self.summary["diagrams"], len(manifest["diagrams"]))

    def test_rerun_is_byte_identical(self):
        again = self.tmp / "visuals_again"
        code, _ = run_visuals(self.baseline, again)
        self.assertEqual(code, 0)
        self.assertEqual(tree_digest(again), tree_digest(self.vis))

    def test_baseline_unchanged_without_source_provider_or_analysis(self):
        from legacy_documenter.cli import full_pipeline, pipeline_stages

        def forbidden(*a, **k):
            raise AssertionError("analysis must not run")
        self.assertFalse((self.tmp / "source").exists())
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(pipeline_stages, "resolve_flows", forbidden), patch.object(full_pipeline, "run_full_pipeline", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            code, summary = run_visuals(self.baseline, self.tmp / "visuals_guarded")
        self.assertEqual((code, guard.call_count, summary["provider_calls"], summary["source_scanned"]), (0, 0, 0, False))
        self.assertEqual(tree_digest(self.baseline), self.before)

    def test_scope_selection_and_flags(self):
        out = self.tmp / "visuals_scoped"
        code, summary = run_visuals(self.baseline, out, "--project", "Web", "--kind", "dependency-map")
        self.assertEqual(code, 0)
        self.assertEqual(summary["diagrams"], 1)
        self.assertTrue((out / "projects" / "Web" / "dependency-map.svg").is_file())

    def test_invalid_inputs_are_refused_without_writing(self):
        out = self.tmp / "visuals_invalid"
        for args, reason in (([str(self.tmp / "missing")], "BASELINE_NOT_FOUND"), ([str(self.baseline), "--include-ai"], "INCLUDE_AI_REQUIRES_AI_RUN"),
                             ([str(self.baseline), "--area", "no-such-area"], "SCOPE_NOT_FOUND")):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = cli_main(["visuals", args[0], "--output", str(out), *args[1:]])
            self.assertEqual(code, 4)
            self.assertIn("VISUALS_INPUT_INVALID", buf.getvalue())
            self.assertIn(reason, buf.getvalue())
        self.assertFalse(out.exists())

    def test_cli_help_documents_behavior(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            cli_main(["visuals", "--help"])
        text = " ".join(buf.getvalue().split())
        for phrase in ("does NOT rescan", "NEVER calls an AI provider", "epistemic status", "system-map", "observable-flow", "data-interaction-map"):
            self.assertIn(phrase, text)

    def test_representative_flow_is_deterministic(self):
        ctx = load_context(self.baseline)
        area = next(iter(ctx.solutions))
        self.assertEqual(representative_flow(ctx, area), representative_flow(ctx, area))


class CategoryVariantTests(unittest.TestCase):
    def test_write_operation_is_grouped_as_inferred_from_the_name(self):
        tmp = Path(tempfile.mkdtemp(prefix="h3v_"))
        try:
            baseline, _ = build_variant(tmp, "write", "SAVE_CUSTOMER", "GRABA_CLIENTE")
            ctx = load_context(baseline)
            p = build_data_interaction_map(ctx, area=next(iter(ctx.solutions)))
            self.assertEqual([g.label for g in p.groups], ["Registro / creación (inferida del nombre)"])
            self.assertEqual(p.groups[0].status, INFERRED)
            node = next(n_ for n_ in p.nodes if n_.type == "data_object")
            self.assertEqual(node.metadata["action"], "create")
            self.assertIn("Registro / creación (inferida del nombre)", render_svg(p))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
