"""V5.2 R3.4: Componente -> Método -> Relaciones técnicas disponibles.

Covers the round's mandatory cases (round section 15): a method relation
sustained by real evidence (calls, data access); no project/component-to-
method attribution invented when the evidence does not give it; homonymous/
overloaded methods within one component never get individually attributed
relations or a fabricated detail document; a method with no known calls stays
index-only; a method with real data access; an unresolved call kept as such
(never silently dropped nor promoted); back-references to owning file/
component; round-trip links; ambiguous file ownership presented as "shared/
ambiguous", never as "sin proyecto asignado"; no redundant detail documents;
determinism; partitioning; General Overview unaffected; legacy untouched;
AI OFF (documentation_v52 never invokes any LLM).

Contract-level assertions on a small synthetic source, plus one full render
to a temp directory to check real link round-trips -- no full-text snapshot
of the real IST run (verified separately, by hand, in the round's result
document).
"""
from __future__ import annotations

import copy
import re
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.documentation_v52.config import ConfigRegistry
from legacy_documenter.documentation_v52.engine import generate_documentation_v52
from legacy_documenter.documentation_v52.renderer import PartitionPolicy
from legacy_documenter.documentation_v52.transform import AudienceTransformer

BL = "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"
SYS = "sys\\SysInterfazSAP\\SysInterfazSAP.vbproj"
SHARED_VBPROJ = "shared\\Shared.vbproj"  # declares the same physical file as BL (ambiguous ownership case)
BL_VB = "bl\\BlInterfazSAP\\BLInterfazSAP.vb"


def _projects() -> list[dict]:
    return [
        {
            "name": "BLInterfazSAP", "path": BL, "output_type": "Library", "assembly_name": "BLInterfazSAP",
            "compile_items": ["BLInterfazSAP.vb", "Ambiguo.vb"], "content_items": [],
        },
        {
            "name": "SysInterfazSAP", "path": SYS, "output_type": "Library",
            "compile_items": ["SysInterfazSAP.vb"], "content_items": [],
        },
        {
            "name": "Shared", "path": SHARED_VBPROJ, "output_type": "Library",
            "compile_items": ["..\\bl\\BlInterfazSAP\\Ambiguo.vb"], "content_items": [],
        },
    ]


def _symbols() -> list[dict]:
    return [
        {
            "name": "BLInterfazSAP", "kind": "class", "file": BL_VB, "project_path": BL,
            "effective_namespace": "BLInterfazSAP", "namespace_confidence": "confirmed", "accessibility": "Public",
            "modifiers": [], "inherits": [], "implements": [],
            "members": [
                # Has an outgoing (resolved) call AND real data access -> gets a detail document.
                {"kind": "sub", "name": "ProcesarSAP", "accessibility": "Public", "shared": False},
                # Known member, but neither a call nor data access is attributed to it
                # -> must stay index-only (no fabricated relation, no detail document).
                {"kind": "function", "name": "ObtenerEstado", "accessibility": "Public", "shared": True},
                # Two members sharing the same name (overload/homonym V5.1 cannot
                # distinguish by signature, GAP-M2): one of them has an outgoing
                # call in the evidence, but it must never be attributed to either
                # specific one.
                {"kind": "sub", "name": "Validar", "accessibility": "Public", "shared": False},
                {"kind": "sub", "name": "Validar", "accessibility": "Private", "shared": False},
            ],
        },
        {
            "name": "SysInterfazSAP", "kind": "class", "file": "sys\\SysInterfazSAP\\SysInterfazSAP.vb",
            "project_path": SYS, "effective_namespace": "SysInterfazSAP", "namespace_confidence": "confirmed",
            "members": [{"kind": "sub", "name": "Procesar", "accessibility": "Public", "shared": False}],
        },
        {
            "name": "Ambiguo", "kind": "class", "file": "bl\\BlInterfazSAP\\Ambiguo.vb", "project_path": None,
            "namespace_confidence": "unresolved", "members": [],
        },
    ]


def _calls() -> list[dict]:
    return [
        {
            "file": BL_VB,
            "calls": [
                # ProcesarSAP -> SysInterfazSAP.Procesar: resolved, confirmed.
                {"containing_class": "BLInterfazSAP", "containing_method": "ProcesarSAP",
                 "expression": "SysInterfazSAP.Procesar()", "resolved_target": "SysInterfazSAP.Procesar",
                 "confidence": "confirmed", "evidence": {"line": 42}},
                # ProcesarSAP also makes a call the resolver could NOT resolve
                # (e.g. a dynamic/late-bound target): kept as an unresolved
                # relation, never silently dropped nor guessed.
                {"containing_class": "BLInterfazSAP", "containing_method": "ProcesarSAP",
                 "expression": "obj.MetodoDinamico()", "resolved_target": None,
                 "confidence": "unresolved", "evidence": {"line": 44}},
                # A call made by one of the two homonymous "Validar" members --
                # V5.1 cannot say which -- must never become an individual
                # method-level relation.
                {"containing_class": "BLInterfazSAP", "containing_method": "Validar",
                 "expression": "SysInterfazSAP.Procesar()", "resolved_target": "SysInterfazSAP.Procesar",
                 "confidence": "confirmed", "evidence": {"line": 60}},
            ],
        },
    ]


def _data_access() -> list[dict]:
    return [
        {
            "class": "BLInterfazSAP", "method": "ProcesarSAP", "project": BL, "operation_kind": "stored_procedure",
            "stored_procedure": "SP_PROCESAR_SAP", "confidence": "confirmed",
            "evidence": [{"file": BL_VB, "line": 46, "expression": "SP_PROCESAR_SAP"}],
        },
    ]


def _source() -> dict:
    solutions = [{"name": "SistemaSAP", "path": "SistemaSAP.sln", "projects": [
        {"name": "BLInterfazSAP", "path": "bl\\BlInterfazSAP\\BLInterfazSAP.vbproj"},
        {"name": "SysInterfazSAP", "path": "sys\\SysInterfazSAP\\SysInterfazSAP.vbproj"}]}]
    return {
        "repository": {"root": "C:\\repo\\SistemaSAP", "stats": {"vb_source": 3}},
        "solutions": solutions, "projects": _projects(), "entry_points": [], "functional_flows": [],
        "flow_unresolved": [], "data_access": _data_access(), "stored_procedures": [], "sql_operations": [],
        "dependencies": [], "configuration": [],
        "flow_summary": {"total_flows": 0, "flows_with_confirmed_terminal": 0, "flows_with_unresolved_boundary": 0},
        "webforms": [], "external_dependencies": [],
        "symbols": _symbols(), "webform_components": [], "calls": _calls(),
    }


def _model(source: dict | None = None):
    return AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source or _source())


class MethodRelationsFromEvidenceTests(unittest.TestCase):
    def test_method_with_call_and_data_access_gets_a_detail_document(self) -> None:
        model = _model()
        procesar = next(m for m in model.methods if m.values["name"] == "ProcesarSAP")
        self.assertTrue(procesar.slug)
        targets = {i.values["target"] for i in procesar.slots["calls_out_resolved"]}
        self.assertIn("SysInterfazSAP.Procesar", targets)
        self.assertEqual(len(procesar.slots["data_access"]), 1)
        self.assertEqual(procesar.slots["data_access"][0].values["target"], "SP_PROCESAR_SAP")

    def test_unresolved_call_is_kept_not_dropped_and_not_guessed(self) -> None:
        """V5.2 R3.4.1 section 4: an unresolved call whose original expression
        is available shows that expression, never the generic `(no resuelto)`
        placeholder (which hid which expression actually produced the call)."""
        model = _model()
        procesar = next(m for m in model.methods if m.values["name"] == "ProcesarSAP")
        unresolved = [i for i in procesar.slots["calls_out_unresolved"] if i.values["confidence"] == "unresolved"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0].values["target"], "obj.MetodoDinamico()")
        self.assertNotEqual(unresolved[0].values["target"], "(no resuelto)")

    def test_method_with_no_relations_stays_index_only_no_project_to_method_fabrication(self) -> None:
        """`ObtenerEstado` is a real, known member (shows up in the component's
        methods index) but has no call or data-access evidence attributed to
        it specifically -- it must NOT get a `MethodModel`/detail document,
        and nothing from its owning project is invented for it."""
        model = _model()
        self.assertNotIn("ObtenerEstado", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "BLInterfazSAP")
        index_row = next(i for i in component.slots["methods"] if i.values["name"] == "ObtenerEstado")
        self.assertEqual(index_row.values["slug"], "")

    def test_homonymous_methods_never_get_individually_attributed_relations(self) -> None:
        """Two members named `Validar` in the same component: V5.1 cannot tell
        them apart (no signature/line for members), so even though one of
        them made a real, resolved call, NEITHER gets a `MethodModel` -- the
        ambiguity is declared at the component level instead."""
        model = _model()
        self.assertNotIn("Validar", {m.values["name"] for m in model.methods})
        component = next(c for c in model.components if c.values["name"] == "BLInterfazSAP")
        ambiguous = component.slots["ambiguous_methods"]
        self.assertEqual(len(ambiguous), 1)
        self.assertEqual(ambiguous[0].values["name"], "Validar")
        self.assertEqual(ambiguous[0].values["overload_count"], 2)
        self.assertIn("gap.method_overloads_ambiguous", model.gaps)

    def test_method_references_its_owning_component_and_file(self) -> None:
        model = _model()
        procesar = next(m for m in model.methods if m.values["name"] == "ProcesarSAP")
        self.assertEqual(procesar.values["component_name"], "BLInterfazSAP")
        self.assertEqual(procesar.values["file_name"], "BLInterfazSAP.vb")
        self.assertEqual(procesar.values["module_name"], "BLInterfazSAP")

    def test_incoming_calls_are_the_only_relations_sysinterfazsap_gets(self) -> None:
        """SysInterfazSAP.Procesar has no outgoing calls/data-access of its own
        in this fixture -- its only real relations are being the confirmed
        target of two callers (relation A, reverse direction): ProcesarSAP,
        and the ambiguous `Validar` homonym group (named honestly by its
        caller label, never resolved to a single specific overload). It must
        never inherit ProcesarSAP's own data access or unresolved call,
        which belong to ProcesarSAP alone."""
        model = _model()
        procesar_target = next(m for m in model.methods if m.values["name"] == "Procesar")
        self.assertEqual(procesar_target.values["component_name"], "SysInterfazSAP")
        callers = {i.values["caller"] for i in procesar_target.slots["calls_in"]}
        self.assertEqual(callers, {"BLInterfazSAP.ProcesarSAP", "BLInterfazSAP.Validar"})
        self.assertEqual(procesar_target.slots["calls_out_resolved"], [])
        self.assertEqual(procesar_target.slots["calls_out_unresolved"], [])
        self.assertEqual(procesar_target.slots["data_access"], [])
        self.assertEqual(procesar_target.slots["data_access_transactional"], [])


class NoDocumentExplosionTests(unittest.TestCase):
    def test_only_methods_with_individual_relations_get_documents(self) -> None:
        model = _model()
        names = sorted(m.values["name"] for m in model.methods)
        # ProcesarSAP (real outgoing call + data access) and Procesar (real
        # incoming call) get documents; ObtenerEstado (no relation) and both
        # `Validar` homonyms (ambiguous) are excluded, by design.
        self.assertEqual(names, ["Procesar", "ProcesarSAP"])

    def test_index_row_carries_no_fabricated_line_number(self) -> None:
        model = _model()
        component = next(c for c in model.components if c.values["name"] == "BLInterfazSAP")
        for item in component.slots["methods"]:
            self.assertNotIn("line", item.values)


class DeterminismTests(unittest.TestCase):
    def test_two_runs_produce_identical_method_models(self) -> None:
        source = _source()
        first = _model(copy.deepcopy(source))
        second = _model(copy.deepcopy(source))
        first_repr = [(m.slug, m.values, {k: [i.values for i in v] for k, v in m.slots.items()}) for m in first.methods]
        second_repr = [(m.slug, m.values, {k: [i.values for i in v] for k, v in m.slots.items()}) for m in second.methods]
        self.assertEqual(first_repr, second_repr)


class AmbiguousFileOwnershipPresentationTests(unittest.TestCase):
    def test_shared_file_presented_as_shared_not_as_unassigned(self) -> None:
        """V5.2 R3.4 section 9 (`img\\aceptar.gif` case, reproduced structurally
        here as `Ambiguo.vb`): a file matching several real projects must read
        as shared/ambiguous ownership, never as if "sin proyecto asignado"
        were itself the (nonexistent) project it belongs to."""
        model = _model()
        ambiguous = next(f for f in model.files if f.values["path"].endswith("Ambiguo.vb"))
        self.assertEqual(ambiguous.values["module_name"], "(pertenencia compartida o ambigua)")
        self.assertNotEqual(ambiguous.values["module_name"], "(sin proyecto asignado)")
        self.assertIn("BLInterfazSAP", ambiguous.values["ownership_note"])
        self.assertIn("Shared", ambiguous.values["ownership_note"])


class RoundTripLinksAndRenderTests(unittest.TestCase):
    """Renders a full `developer_technical` tree to a temp dir and follows the
    real relative links Component -> Método -> Componente, checking the
    target files actually exist on disk (not merely referenced)."""

    def _render(self):
        tmp = tempfile.TemporaryDirectory()
        result = generate_documentation_v52(_source(), tmp.name, profiles=("developer_technical",))
        return tmp, result

    def test_component_document_links_to_method_and_back(self) -> None:
        tmp, result = self._render()
        try:
            root = Path(result.output_dir) / "developer"
            component_doc = next(p for p in root.rglob("*.md") if p.stem.lower() == "procesarsap".lower()
                                  or "ProcesarSAP" in p.read_text(encoding="utf-8"))
            # Locate the component doc (BLInterfazSAP) and the method doc (ProcesarSAP) precisely.
            comp_candidates = [p for p in root.rglob("*.md") if p.parent.name != "files" and "Volver al archivo" in p.read_text(encoding="utf-8")]
            self.assertTrue(comp_candidates, "no component document found")
            comp_path = next(p for p in comp_candidates if "ProcesarSAP" in p.read_text(encoding="utf-8"))
            comp_text = comp_path.read_text(encoding="utf-8")
            link_match = re.search(r"\[`ProcesarSAP`\]\(([^)]+)\)", comp_text)
            self.assertIsNotNone(link_match, "no link to the method document found in the component page")
            method_path = (comp_path.parent / link_match.group(1)).resolve()
            self.assertTrue(method_path.is_file(), f"linked method document does not exist: {method_path}")
            method_text = method_path.read_text(encoding="utf-8")
            self.assertIn("SysInterfazSAP.Procesar", method_text)
            self.assertIn("SP_PROCESAR_SAP", method_text)
            back_match = re.search(r"\[Volver al componente\]\(([^)]+)\)", method_text)
            self.assertIsNotNone(back_match, "method document has no back-link to its component")
            back_path = (method_path.parent / back_match.group(1)).resolve()
            self.assertEqual(back_path, comp_path.resolve())
        finally:
            tmp.cleanup()

    def test_no_method_scope_vocabulary_leaks_into_general_overview(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        try:
            result = generate_documentation_v52(_source(), tmp.name, profiles=("general_overview", "developer_technical"))
            general_readme = (Path(result.output_dir) / "general" / "README.md").read_text(encoding="utf-8")
            self.assertNotIn("ProcesarSAP", general_readme)
            self.assertNotIn("Método", general_readme)
        finally:
            tmp.cleanup()

    def test_partitioning_applies_to_method_documents_like_any_other(self) -> None:
        """Reuses the existing partition machinery (no new partitioning logic
        introduced for methods, per round section 10/12): a tiny partition
        policy still produces a valid, non-empty tree."""
        tmp = tempfile.TemporaryDirectory()
        try:
            result = generate_documentation_v52(
                _source(), tmp.name, profiles=("developer_technical",),
                partition_override=PartitionPolicy(max_items_per_part=1, max_bytes_per_part=200),
            )
            self.assertTrue(result.files)
        finally:
            tmp.cleanup()


class CustomTemplateAndLegacyCompatibilityTests(unittest.TestCase):
    def test_method_scope_is_a_valid_custom_template_scope(self) -> None:
        """A custom `templates/dev.method.json` validates through the same
        contract as any other scope (round section 12: templates stay
        declarative JSON, no code)."""
        from legacy_documenter.documentation_v52.config import Catalog, OutputProfile, validate_template

        profile = OutputProfile.from_dict({
            "id": "developer_technical", "contract_version": "1", "audience": "developer", "max_detail_level": 4,
            "visible_categories": ["KEEP_SIMPLE", "KEEP_TECHNICAL"], "detail_on_demand": "documents", "language": "es",
            "noise_policy": "default", "unresolved_behavior": "summary_with_link", "body_row_limit": 15,
            "output_dir": "developer", "templates": [], "partition": {"max_items_per_part": 300, "max_bytes_per_part": 65536},
        })
        catalog = Catalog("es", {}, ConfigRegistry().catalog("es")._fallback)
        custom = {
            "id": "dev.method", "contract_version": "1", "scope": "method", "file": "modules/{slug}.md",
            "blocks": [{"type": "heading", "level": 1, "text_key": "dev.method.title"}],
        }
        validate_template(custom, catalog, profile, expected_id="dev.method")  # must not raise

    def test_ai_never_invoked_documentation_v52_has_no_llm_dependency(self) -> None:
        import legacy_documenter.documentation_v52.engine as engine_module
        import legacy_documenter.documentation_v52.transform as transform_module
        source = " ".join([Path(engine_module.__file__).read_text(encoding="utf-8"),
                            Path(transform_module.__file__).read_text(encoding="utf-8")])
        for token in ("openai", "anthropic", "llm_provider", "ai_provider", "ProviderRegistry"):
            self.assertNotIn(token, source)

    def test_legacy_documentation_module_still_importable_unaffected(self) -> None:
        import legacy_documenter.documentation.generator  # noqa: F401 -- must still import cleanly


if __name__ == "__main__":
    unittest.main()
