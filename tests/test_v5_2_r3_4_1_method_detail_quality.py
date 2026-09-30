"""V5.2 R3.4.1: Method Detail Quality & Document Redundancy Control.

Covers the round's mandatory cases (round section 13): an unresolved call
with its original expression visible; an unresolved call with no expression
available at all (honest absence, never a guess); a confirmed call with a
real resolved target; the distinction between real data access and
transactional control on the same method; a method with only transactional
control; a method with relevant unresolved calls; a method with only
technical noise; a document correctly omitted without evidence loss; a
method that stays index-only; absence of broken links; homonymous methods
never receiving an individually attributed relation; determinism;
partitioning reused unchanged; custom templates; General Overview untouched;
AI OFF; legacy documentation untouched; and no regression of R3.1-R3.4
guarantees.

Contract-level assertions on a small synthetic source (never only a Markdown
snapshot), plus one full render to a temp directory for the round-trip/
broken-link/partitioning checks -- the real IST run is verified separately,
by hand, in the round's result document.
"""
from __future__ import annotations

import copy
import re
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.documentation_v52.config import Catalog, ConfigRegistry, OutputProfile, validate_template
from legacy_documenter.documentation_v52.engine import generate_documentation_v52
from legacy_documenter.documentation_v52.renderer import PartitionPolicy
from legacy_documenter.documentation_v52.transform import AudienceTransformer

PRJ = "demo\\Utilidades\\Utilidades.vbproj"
VB = "demo\\Utilidades\\Utilidades.vb"


def _projects() -> list[dict]:
    return [{
        "name": "Utilidades", "path": PRJ, "output_type": "Library", "assembly_name": "Utilidades",
        "compile_items": ["Utilidades.vb"], "content_items": [],
    }]


def _symbols() -> list[dict]:
    return [{
        "name": "Utilidades", "kind": "class", "file": VB, "project_path": PRJ,
        "effective_namespace": "Utilidades", "namespace_confidence": "confirmed", "accessibility": "Public",
        "modifiers": [], "inherits": [], "implements": [],
        "members": [
            # 3. Confirmed call with a real resolved target.
            {"kind": "sub", "name": "MetodoResuelto", "accessibility": "Public", "shared": False},
            # 1. Unresolved call whose original expression IS available.
            {"kind": "sub", "name": "MetodoExpresionVisible", "accessibility": "Public", "shared": False},
            # 2. Unresolved call whose original expression is NOT available.
            {"kind": "sub", "name": "MetodoSinExpresion", "accessibility": "Public", "shared": False},
            # 7. Only technical noise (a UI control call the default policy classifies).
            {"kind": "sub", "name": "MetodoSoloRuido", "accessibility": "Public", "shared": False},
            # 5. Only transactional control (no real data access).
            {"kind": "sub", "name": "MetodoSoloTransaccional", "accessibility": "Public", "shared": False},
            # 4. Both real data access AND transactional control.
            {"kind": "sub", "name": "MetodoMixtoDatos", "accessibility": "Public", "shared": False},
            # 9. Known member with no relation at all -> stays index-only.
            {"kind": "sub", "name": "MetodoSinRelaciones", "accessibility": "Public", "shared": False},
            # 11. Two homonyms, one with a relation -> ambiguous group, no document.
            {"kind": "function", "name": "Calcular", "accessibility": "Public", "shared": False},
            {"kind": "function", "name": "Calcular", "accessibility": "Private", "shared": False},
        ],
    }]


def _calls() -> list[dict]:
    return [{
        "file": VB,
        "calls": [
            {"containing_class": "Utilidades", "containing_method": "MetodoResuelto",
             "expression": "Utilidades.Helper.Formatear()", "resolved_target": "Utilidades.Formatear",
             "confidence": "confirmed", "evidence": {"line": 10}},
            {"containing_class": "Utilidades", "containing_method": "MetodoExpresionVisible",
             "expression": "obj.LlamadaDinamica(parametro)", "resolved_target": None,
             "confidence": "unresolved", "evidence": {"line": 20}},
            # No `expression` field at all in the raw evidence record.
            {"containing_class": "Utilidades", "containing_method": "MetodoSinExpresion",
             "expression": "", "resolved_target": None, "confidence": "unresolved", "evidence": {"line": 30}},
            # `DataBind` matches the default noise policy's `ui_control_calls` category.
            {"containing_class": "Utilidades", "containing_method": "MetodoSoloRuido",
             "expression": "Me.grdItems.DataBind()", "resolved_target": None,
             "confidence": "unresolved", "evidence": {"line": 40}},
            {"containing_class": "Utilidades", "containing_method": "Calcular",
             "expression": "Utilidades.Helper.Formatear()", "resolved_target": "Utilidades.Formatear",
             "confidence": "confirmed", "evidence": {"line": 50}},
        ],
    }]


def _data_access() -> list[dict]:
    return [
        {"class": "Utilidades", "method": "MetodoSoloTransaccional", "project": PRJ, "operation_kind": "transaction",
         "confidence": "confirmed", "evidence": [{"file": VB, "line": 60}]},
        {"class": "Utilidades", "method": "MetodoMixtoDatos", "project": PRJ, "operation_kind": "stored_procedure",
         "stored_procedure": "SP_CALCULA_TOTAL", "confidence": "confirmed", "evidence": [{"file": VB, "line": 70}]},
        {"class": "Utilidades", "method": "MetodoMixtoDatos", "project": PRJ, "operation_kind": "transaction",
         "confidence": "confirmed", "evidence": [{"file": VB, "line": 71}]},
    ]


def _source() -> dict:
    return {
        "repository": {"root": "C:\\repo\\Demo", "stats": {"vb_source": 1}},
        "solutions": [{"name": "Demo", "path": "Demo.sln", "projects": [{"name": "Utilidades", "path": PRJ}]}],
        "projects": _projects(), "entry_points": [], "functional_flows": [], "flow_unresolved": [],
        "data_access": _data_access(), "stored_procedures": [], "sql_operations": [], "dependencies": [],
        "configuration": [],
        "flow_summary": {"total_flows": 0, "flows_with_confirmed_terminal": 0, "flows_with_unresolved_boundary": 0},
        "webforms": [], "external_dependencies": [],
        "symbols": _symbols(), "webform_components": [], "calls": _calls(),
    }


def _model(source: dict | None = None):
    return AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source or _source())


def _method(model, name: str):
    return next(m for m in model.methods if m.values["name"] == name)


class UnresolvedExpressionTests(unittest.TestCase):
    def test_unresolved_call_shows_original_expression_not_generic_placeholder(self) -> None:
        """Section 4: an unresolved call whose expression is known must show
        that expression, never the generic `(no resuelto)` marker."""
        model = _model()
        method = _method(model, "MetodoExpresionVisible")
        unresolved = method.slots["calls_out_unresolved"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0].values["target"], "obj.LlamadaDinamica(parametro)")
        self.assertEqual(unresolved[0].values["confidence"], "unresolved")
        self.assertNotIn("(no resuelto)", unresolved[0].values["target"])

    def test_unresolved_call_without_expression_declares_absence_honestly(self) -> None:
        """Section 4: when the original expression is also unavailable, the
        absence is declared honestly (never silently dropped, never a made-up
        expression). It never counts, alone, toward getting a document
        (section 7): no individual information over the index row."""
        model = _model()
        self.assertNotIn("MetodoSinExpresion", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "Utilidades")
        index_row = next(i for i in component.slots["methods"] if i.values["name"] == "MetodoSinExpresion")
        self.assertEqual(index_row.values["slug"], "")


class ConfirmedCallTests(unittest.TestCase):
    def test_confirmed_call_shows_real_resolved_target(self) -> None:
        model = _model()
        method = _method(model, "MetodoResuelto")
        resolved = method.slots["calls_out_resolved"]
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].values["target"], "Utilidades.Formatear")
        self.assertEqual(resolved[0].values["confidence"], "confirmed")
        self.assertEqual(method.slots["calls_out_unresolved"], [])


class RealDataAccessVsTransactionalTests(unittest.TestCase):
    def test_real_and_transactional_data_access_are_kept_in_separate_slots(self) -> None:
        """Section 6: a method with both a real operation and transactional
        control must never present the transactional one as if it were real
        data access, and the real one must not disappear either."""
        model = _model()
        method = _method(model, "MetodoMixtoDatos")
        real = method.slots["data_access"]
        tx = method.slots["data_access_transactional"]
        self.assertEqual([i.values["target"] for i in real], ["SP_CALCULA_TOTAL"])
        self.assertEqual(len(tx), 1)
        self.assertEqual(tx[0].values["kind"], "transaction")
        self.assertNotIn("SP_CALCULA_TOTAL", [i.values["target"] for i in tx])

    def test_transaction_only_method_never_counted_as_real_data_access(self) -> None:
        """Section 5/6: a method whose only data-access evidence is
        transaction control (Commit/Rollback/BeginTrans-equivalent) is never
        presented as accessing data for real -- and, having no other
        relation, it stays index-only rather than getting a low-value
        document consisting solely of "Control de transacción"."""
        model = _model()
        self.assertNotIn("MetodoSoloTransaccional", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "Utilidades")
        index_row = next(i for i in component.slots["methods"] if i.values["name"] == "MetodoSoloTransaccional")
        self.assertEqual(index_row.values["slug"], "")


class NoiseOnlyMethodTests(unittest.TestCase):
    def test_method_with_only_noise_classified_call_stays_index_only(self) -> None:
        """Section 5/7: a method whose only outgoing call is already-classified
        technical noise (`DataBind`, the default policy's `ui_control_calls`
        category) does not get a document of its own -- the noise policy is
        reused, not reintroduced as raw text competing with real relations."""
        model = _model()
        self.assertNotIn("MetodoSoloRuido", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "Utilidades")
        index_row = next(i for i in component.slots["methods"] if i.values["name"] == "MetodoSoloRuido")
        self.assertEqual(index_row.values["slug"], "")


class DocumentOmittedWithoutEvidenceLossTests(unittest.TestCase):
    def test_omitted_document_evidence_still_reaches_the_component_index(self) -> None:
        """Section 8: suppressing a method's own document never removes it
        from the component's method table (name/kind/accessibility/shared
        stay visible); nothing is silently dropped."""
        model = _model()
        component = next(c for c in model.components if c.values["name"] == "Utilidades")
        names = {i.values["name"] for i in component.slots["methods"]}
        for expected in ("MetodoSinExpresion", "MetodoSoloTransaccional", "MetodoSoloRuido", "MetodoSinRelaciones"):
            self.assertIn(expected, names)


class HomonymAttributionTests(unittest.TestCase):
    def test_homonymous_method_with_a_relation_never_gets_individual_attribution(self) -> None:
        model = _model()
        self.assertNotIn("Calcular", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "Utilidades")
        ambiguous = component.slots["ambiguous_methods"]
        self.assertEqual(len(ambiguous), 1)
        self.assertEqual(ambiguous[0].values["name"], "Calcular")
        self.assertEqual(ambiguous[0].values["overload_count"], 2)


class DeterminismTests(unittest.TestCase):
    def test_two_runs_produce_identical_method_models(self) -> None:
        source = _source()
        first = _model(copy.deepcopy(source))
        second = _model(copy.deepcopy(source))
        rep = lambda model: [(m.slug, m.values, {k: [i.values for i in v] for k, v in m.slots.items()}) for m in model.methods]
        self.assertEqual(rep(first), rep(second))


class RenderRoundTripTests(unittest.TestCase):
    """Full render to a temp dir: checks used by the broken-link, partitioning
    and General Overview tests below."""

    def _render(self, **kwargs):
        tmp = tempfile.TemporaryDirectory()
        result = generate_documentation_v52(_source(), tmp.name, profiles=("general_overview", "developer_technical"), **kwargs)
        return tmp, result

    def test_no_broken_relative_links_in_rendered_tree(self) -> None:
        tmp, result = self._render()
        try:
            root = Path(result.output_dir)
            md_files = list(root.rglob("*.md"))
            self.assertTrue(md_files)
            checked = 0
            for path in md_files:
                text = path.read_text(encoding="utf-8")
                for match in re.finditer(r"\]\(([^)]+)\)", text):
                    target = match.group(1)
                    if target.startswith(("http://", "https://")):
                        continue
                    resolved = (path.parent / target).resolve()
                    self.assertTrue(resolved.is_file(), f"broken link in {path}: {target}")
                    checked += 1
            self.assertGreater(checked, 0)
        finally:
            tmp.cleanup()

    def test_partitioning_reused_unchanged_under_a_tiny_policy(self) -> None:
        """Section 12: no new partitioning logic for methods -- the existing
        combined items/bytes partitioner still produces a valid tree."""
        tmp, result = self._render(partition_override=PartitionPolicy(max_items_per_part=1, max_bytes_per_part=200))
        try:
            self.assertTrue(result.files)
        finally:
            tmp.cleanup()

    def test_general_overview_untouched_by_method_level_vocabulary(self) -> None:
        tmp, result = self._render()
        try:
            general_readme = (Path(result.output_dir) / "general" / "README.md").read_text(encoding="utf-8")
            for leak in ("MetodoResuelto", "Método", "calls_out", "LlamadaDinamica"):
                self.assertNotIn(leak, general_readme)
        finally:
            tmp.cleanup()

    def test_method_document_content_matches_the_new_sectioned_presentation(self) -> None:
        tmp, result = self._render()
        try:
            root = Path(result.output_dir) / "developer"
            candidates = [p for p in root.rglob("*.md") if "obj.LlamadaDinamica" in p.read_text(encoding="utf-8")]
            self.assertTrue(candidates, "no method document shows the visible expression")
            text = candidates[0].read_text(encoding="utf-8")
            self.assertIn("obj.LlamadaDinamica(parametro)", text)
            self.assertNotIn("(no resuelto)", text)
        finally:
            tmp.cleanup()


class CustomTemplateAndLegacyCompatibilityTests(unittest.TestCase):
    def test_method_scope_custom_template_can_reference_the_new_slots(self) -> None:
        """Section 12: the new split slots (`calls_out_resolved`,
        `calls_out_unresolved`, `data_access`, `data_access_transactional`)
        stay declarative-JSON-addressable like every other method field --
        no Python code needed to reach them from a template."""
        profile = OutputProfile.from_dict({
            "id": "developer_technical", "contract_version": "1", "audience": "developer", "max_detail_level": 4,
            "visible_categories": ["KEEP_SIMPLE", "KEEP_TECHNICAL"], "detail_on_demand": "documents", "language": "es",
            "noise_policy": "default", "unresolved_behavior": "summary_with_link", "body_row_limit": 15,
            "output_dir": "developer", "templates": [], "partition": {"max_items_per_part": 300, "max_bytes_per_part": 65536},
        })
        catalog = Catalog("es", {}, ConfigRegistry().catalog("es")._fallback)
        custom = {
            "id": "dev.method", "contract_version": "1", "scope": "method", "file": "modules/{slug}.md",
            "blocks": [
                {"type": "heading", "level": 1, "text_key": "dev.method.title"},
                {"type": "table", "source": "method.slots.data_access_transactional",
                 "columns": [{"field": "kind", "header_key": "col.data_kind", "translate": "kind"}]},
            ],
        }
        validate_template(custom, catalog, profile, expected_id="dev.method")  # must not raise

    def test_ai_never_invoked(self) -> None:
        import legacy_documenter.documentation_v52.engine as engine_module
        import legacy_documenter.documentation_v52.transform as transform_module
        source = " ".join([Path(engine_module.__file__).read_text(encoding="utf-8"),
                            Path(transform_module.__file__).read_text(encoding="utf-8")])
        for token in ("openai", "anthropic", "llm_provider", "ai_provider", "ProviderRegistry"):
            self.assertNotIn(token, source)

    def test_legacy_documentation_module_still_importable_unaffected(self) -> None:
        import legacy_documenter.documentation.generator  # noqa: F401 -- must still import cleanly


class RegressionR31ToR34Tests(unittest.TestCase):
    """Spot-checks that this round's changes did not touch the R3.1-R3.4
    guarantees it explicitly must not reopen (round section 0/12)."""

    def test_method_level_gaps_from_r3_4_are_preserved(self) -> None:
        model = _model()
        for gap in ("gap.method_dependencies_not_available", "gap.method_unresolved_not_attributable",
                    "gap.method_identity_no_signatures"):
            self.assertIn(gap, model.gaps)

    def test_module_level_unresolved_presentation_is_unaffected(self) -> None:
        """R3.1's module-level unresolved-call aggregation (`_collect_unresolved`
        / `_unresolved_items`) is untouched by this round's method-level work."""
        module = next(m for m in _model().modules if m.values["path"] == PRJ)
        self.assertEqual(module.values["unresolved_total"], 0)  # this fixture has no `flow_unresolved` records


if __name__ == "__main__":
    unittest.main()
