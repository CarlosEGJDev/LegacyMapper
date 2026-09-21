import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from legacy_documenter.cli.pipeline_stages import render_documentation
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.documentation.human_documentation_scaling import (
    PARTITIONS_SUBDIR,
    UNASSIGNED_GROUP_KEY,
    flow_group_key,
    render_human_documentation_index,
    render_human_documentation_partitions,
)
from legacy_documenter.exporters._documentation_partitioning import (
    build_partition_filenames,
    sanitize_label,
    webform_owner_group_key,
)
from legacy_documenter.exporters.markdown_exporter import MarkdownExporter
from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer


def _ix():
    """Three flows, grouped (post V4.3-R4 correction) by their entry point's
    WebForm-owning folder -- never by `project_sequence` -- plus one with no
    WebForm evidence at all (`webform=None`), reusing R0's acceptance cases
    B/D and adding an unassigned-group flow -- enough to exercise grouping,
    ordering, and the unassigned fallback without duplicating R3's own
    fixture set verbatim.

    `project_sequence` is deliberately set to a *different* layer than the
    WebForm folder for FLOW-A/FLOW-B (e.g. FLOW-A's WebForm lives under
    `DAL\\`, matching its group, while its own `project_sequence` starts
    with `WEB`) to prove the group key is never read from `projects` --
    exactly the defect this round's correction fixes (see
    `docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md` section 12).
    """
    return {
        "functional_flows": [
            {"id": "FLOW-A", "entry_point_id": "EP-A", "confidence": "confirmed", "project_sequence": ["WEB", "DAL"]},
            {"id": "FLOW-B", "entry_point_id": "EP-B", "confidence": "unresolved", "project_sequence": ["DAL"]},
            {"id": "FLOW-C", "entry_point_id": "EP-C", "confidence": "confirmed", "project_sequence": []},
        ],
        "functional_paths": [
            {"path_id": "PATH-1", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-1"]},
            {"path_id": "PATH-4", "flow_id": "FLOW-B", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "unknown", "confidence": "unresolved", "evidence_refs": []},
            {"path_id": "PATH-5", "flow_id": "FLOW-C", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-5"]},
        ],
        "entry_points": [
            {"id": "EP-A", "webform": "DAL\\cobCargaArcIntRea.ascx", "event": "Click", "handler": "btnCargar_Click", "start_method": "btnCargar_Click"},
            {"id": "EP-B", "webform": "WEB\\CobConsultaTransferencia.ascx", "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
            {"id": "EP-C", "webform": None, "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
        ],
        "data_access": [
            {"id": "DAO-1", "class": "CobDAO", "method": "Actualizar", "project": "DAL", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 5}]},
        ],
        "stored_procedures": [
            {"id": "SP-1", "name": "spActualizarSaldo", "package": "PKG_COB", "procedure": "PR_SALDO", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 6}]},
        ],
        "sql_operations": [],
        "data_parameters": [],
    }


def _hydrated_flows():
    hydrator = EvidenceHydrator()
    ix = _ix()
    return [hydrator.hydrate_flow(fid, ix) for fid in ("FLOW-A", "FLOW-B", "FLOW-C")]


class FlowGroupKeyTests(unittest.TestCase):
    """V4.3-R4 correction: the group key comes exclusively from
    `entry_point.webform`, never from `projects`/`project_sequence` (the
    defect that put `cobCargaArcIntRea.ascx`/`cobChqInsRen.ascx`, both under
    `webCobMorosidad\\`, into a `DAL` group instead of `webCobMorosidad`,
    because their resolved call chains happened to reach the `DAL` layer
    first).
    """

    def test_uses_the_first_path_segment_of_the_entry_point_webform(self):
        record = {
            "entry_point": {"webform": "webCobMorosidad\\cobCargaArcIntRea.ascx"},
            "projects": ["DAL"],  # first-reached layer -- must NOT be used as the group key
        }
        self.assertEqual(flow_group_key(record), "webCobMorosidad")

    def test_a_second_webform_in_the_same_folder_produces_the_same_key(self):
        record = {
            "entry_point": {"webform": "webCobMorosidad\\cobChqInsRen.ascx"},
            "projects": ["DAL"],
        }
        self.assertEqual(flow_group_key(record), "webCobMorosidad")

    def test_forward_slash_separator_produces_the_same_folder_key(self):
        backslash = flow_group_key({"entry_point": {"webform": "webCobMorosidad\\cobCargaArcIntRea.ascx"}})
        forward_slash = flow_group_key({"entry_point": {"webform": "webCobMorosidad/cobCargaArcIntRea.ascx"}})
        self.assertEqual(backslash, forward_slash)
        self.assertEqual(forward_slash, "webCobMorosidad")

    def test_webform_without_a_path_separator_falls_back_to_the_filename_stem(self):
        # Tier 2: a rootless WebForm still gets direct entry-point evidence,
        # just at coarser (filename, not folder) granularity.
        self.assertEqual(flow_group_key({"entry_point": {"webform": "cobSinProyecto.ascx"}}), "cobSinProyecto")

    def test_falls_back_to_the_unassigned_key_when_webform_is_missing_even_with_known_projects(self):
        # `projects` being non-empty must never be used as a substitute for
        # missing WebForm evidence -- this is the exact substitution the
        # correction forbids.
        self.assertEqual(flow_group_key({"projects": ["DAL", "WEB"]}), UNASSIGNED_GROUP_KEY)
        self.assertEqual(
            flow_group_key({"entry_point": {"webform": None}, "projects": ["DAL"]}), UNASSIGNED_GROUP_KEY
        )
        self.assertEqual(
            flow_group_key({"entry_point": {"webform": "  "}, "projects": ["DAL"]}), UNASSIGNED_GROUP_KEY
        )

    def test_falls_back_to_the_unassigned_key_when_entry_point_is_missing(self):
        self.assertEqual(flow_group_key({}), UNASSIGNED_GROUP_KEY)

    def test_two_flows_under_the_same_webform_folder_land_in_the_same_partition(self):
        # End-to-end regression for the exact defect fixed this round: two
        # real R0 acceptance-case flows under `webCobMorosidad\\`, whose
        # resolved call chains reach `DAL` first, must still land in the
        # SAME partition (`webCobMorosidad.md`), never a `DAL.md` partition.
        ix = {
            "functional_flows": [
                {"id": "FLOW-X", "entry_point_id": "EP-X", "confidence": "confirmed", "project_sequence": ["DAL"]},
                {"id": "FLOW-Y", "entry_point_id": "EP-Y", "confidence": "confirmed", "project_sequence": ["DAL"]},
            ],
            "functional_paths": [
                {"path_id": "PATH-X", "flow_id": "FLOW-X", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-X"]},
                {"path_id": "PATH-Y", "flow_id": "FLOW-Y", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-Y"]},
            ],
            "entry_points": [
                {"id": "EP-X", "webform": "webCobMorosidad\\cobCargaArcIntRea.ascx", "event": "Click", "handler": "btnCargar_Click", "start_method": "btnCargar_Click"},
                {"id": "EP-Y", "webform": "webCobMorosidad\\cobChqInsRen.ascx", "event": "Click", "handler": "HypGuardar_Click", "start_method": "HypGuardar_Click"},
            ],
            "data_access": [
                {"id": "DAO-1", "class": "CobDAO", "method": "Actualizar", "project": "DAL", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 5}]},
            ],
            "stored_procedures": [
                {"id": "SP-1", "name": "spActualizarSaldo", "package": "PKG_COB", "procedure": "PR_SALDO", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 6}]},
            ],
            "sql_operations": [],
            "data_parameters": [],
        }
        hydrator = EvidenceHydrator()
        flows = [hydrator.hydrate_flow(fid, ix) for fid in ("FLOW-X", "FLOW-Y")]
        partitions = render_human_documentation_partitions(flows)
        webcob_filename = build_partition_filenames(["webCobMorosidad"])["webCobMorosidad"]
        self.assertIn(webcob_filename, partitions)
        self.assertNotIn(build_partition_filenames(["DAL"])["DAL"], partitions)
        content = partitions[webcob_filename]
        self.assertIn("# Flujo FLOW-X:", content)
        self.assertIn("# Flujo FLOW-Y:", content)


class NavigationIndexTests(unittest.TestCase):
    def test_index_is_in_spanish_and_lists_every_group(self):
        doc = render_human_documentation_index(_hydrated_flows())
        self.assertIn("# Documentación humana de flujos — Índice", doc)
        self.assertIn("## Grupos de flujos", doc)
        self.assertIn("DAL", doc)
        self.assertIn("WEB", doc)
        self.assertIn("Sin asignar", doc)

    def test_index_never_repeats_full_flow_detail(self):
        # Résumé-antes-que-detalle (V4.3-R1 5.1): the index must never contain
        # the seven-section detail render_flow_document produces.
        doc = render_human_documentation_index(_hydrated_flows())
        self.assertNotIn("## 3. Resumen funcional determinista", doc)
        self.assertNotIn("## 8. Evidencia técnica detallada / trazabilidad", doc)

    def test_index_declares_an_explicit_unconditional_size_policy(self):
        doc = render_human_documentation_index(_hydrated_flows())
        self.assertIn("Política de tamaño", doc)
        self.assertIn("incondicional", doc)

    def test_index_counts_match_input_totals(self):
        flows = _hydrated_flows()
        doc = render_human_documentation_index(flows)
        self.assertIn(f"{len(flows)} flujo(s) hidratado(s)", doc)

    def test_index_links_point_at_the_partitions_subdir_and_match_actual_filenames(self):
        flows = _hydrated_flows()
        doc = render_human_documentation_index(flows)
        partitions = render_human_documentation_partitions(flows)
        for filename in partitions:
            self.assertIn(f"[{filename}]({PARTITIONS_SUBDIR}/{filename})", doc)

    def test_index_over_empty_flow_list_declares_no_flows_without_error(self):
        doc = render_human_documentation_index([])
        self.assertIn("No se hidrataron flujos", doc)

    def test_index_is_deterministic_regardless_of_input_order(self):
        flows = _hydrated_flows()
        reversed_flows = list(reversed(flows))
        self.assertEqual(render_human_documentation_index(flows), render_human_documentation_index(reversed_flows))


class PartitionDocumentTests(unittest.TestCase):
    def test_partitions_group_flows_by_webform_folder_and_unassigned_flows_get_their_own_partition(self):
        # `_ix()`'s flows have `project_sequence` values that deliberately
        # differ from their WebForm folder (see `_ix()` docstring); grouping
        # by DAL/WEB here reflects each flow's `entry_point.webform` folder,
        # never `project_sequence`.
        partitions = render_human_documentation_partitions(_hydrated_flows())
        filenames = build_partition_filenames(sorted({"DAL", "WEB", UNASSIGNED_GROUP_KEY}))
        self.assertIn(filenames["DAL"], partitions)
        self.assertIn(filenames["WEB"], partitions)
        self.assertIn(filenames[UNASSIGNED_GROUP_KEY], partitions)

    def test_partition_filenames_are_produced_via_the_shared_partitioning_helper_not_reinvented(self):
        flows = _hydrated_flows()
        groups = sorted({"DAL", "WEB", UNASSIGNED_GROUP_KEY})
        expected = build_partition_filenames(groups)
        partitions = render_human_documentation_partitions(flows)
        self.assertEqual(set(partitions), set(expected.values()))

    def test_partition_contains_full_eight_section_detail_for_each_flow_in_its_group(self):
        partitions = render_human_documentation_partitions(_hydrated_flows())
        dal_filename = build_partition_filenames(["DAL"])["DAL"]
        content = partitions[dal_filename]
        self.assertIn("## 1. Qué es y dónde está", content)
        self.assertIn("## 8. Evidencia técnica detallada / trazabilidad", content)
        self.assertIn("spActualizarSaldo", content)

    def test_every_input_flow_is_preserved_exactly_once_across_all_partitions(self):
        flows = _hydrated_flows()
        partitions = render_human_documentation_partitions(flows)
        occurrences = {r["flow_id"]: 0 for r in flows}
        for content in partitions.values():
            for flow_id in occurrences:
                occurrences[flow_id] += content.count(f"# Flujo {flow_id}:")
        self.assertEqual(occurrences, {r["flow_id"]: 1 for r in flows})

    def test_empty_flow_list_produces_no_partitions(self):
        self.assertEqual(render_human_documentation_partitions([]), {})

    def test_partition_flow_order_within_a_group_is_stable_and_sorted(self):
        flows = _hydrated_flows()
        forward = render_human_documentation_partitions(flows)
        backward = render_human_documentation_partitions(list(reversed(flows)))
        self.assertEqual(forward, backward)

    def test_partition_links_back_to_the_top_level_index_with_a_relative_link(self):
        partitions = render_human_documentation_partitions(_hydrated_flows())
        dal_filename = build_partition_filenames(["DAL"])["DAL"]
        self.assertIn("[Volver al índice](../HUMAN_DOCUMENTATION.md)", partitions[dal_filename])

    def test_interpretations_are_passed_through_per_flow_only(self):
        flows = _hydrated_flows()
        flow_a = next(r for r in flows if r["flow_id"] == "FLOW-A")
        evidence_ref = flow_a["paths"][0]["evidence_refs"][0]
        partitions = render_human_documentation_partitions(
            flows,
            interpretations_by_flow={
                "FLOW-A": [{"statement": "Interpretación de prueba.", "evidence_refs": [evidence_ref]}],
            },
        )
        dal_filename = build_partition_filenames(["DAL"])["DAL"]
        wf_filename = build_partition_filenames(["WEB"])["WEB"]
        self.assertIn("[INTERPRETED]", partitions[dal_filename])
        self.assertIn("Interpretación de prueba.", partitions[dal_filename])
        # FLOW-B (the only flow in the WEB-only group) got no interpretation.
        self.assertNotIn("[INTERPRETED]", partitions[wf_filename])

    def test_no_interpretations_argument_means_no_interpreted_section_anywhere(self):
        partitions = render_human_documentation_partitions(_hydrated_flows())
        for content in partitions.values():
            self.assertNotIn("[INTERPRETED]", content)


class MachineProjectionIntactTests(unittest.TestCase):
    """Neither rendering function may mutate the hydrated records it receives --
    the machine-readable `AI_HYDRATED_PROJECTION 1.0` projection stays intact
    for any other consumer holding the same list/dicts.
    """

    def test_render_human_documentation_index_does_not_mutate_its_input(self):
        flows = _hydrated_flows()
        before = copy.deepcopy(flows)
        render_human_documentation_index(flows)
        self.assertEqual(flows, before)

    def test_render_human_documentation_partitions_does_not_mutate_its_input(self):
        flows = _hydrated_flows()
        before = copy.deepcopy(flows)
        render_human_documentation_partitions(flows)
        self.assertEqual(flows, before)


class DeterminismTests(unittest.TestCase):
    def test_index_is_deterministic_across_repeated_calls(self):
        flows = _hydrated_flows()
        self.assertEqual(render_human_documentation_index(flows), render_human_documentation_index(flows))

    def test_partitions_are_deterministic_across_repeated_calls(self):
        flows = _hydrated_flows()
        self.assertEqual(render_human_documentation_partitions(flows), render_human_documentation_partitions(flows))


class SanitizeLabelReuseTests(unittest.TestCase):
    """Filenames must reuse `sanitize_label`/`build_partition_filenames`
    (V4.2-R8) unmodified -- never a locally reinvented sanitizer.
    """

    def test_unsafe_group_label_characters_are_sanitized_by_the_shared_helper(self):
        # This module never reimplements sanitization: it calls
        # `build_partition_filenames` directly, so an unsafe key (path
        # separators, `..`) is made filesystem-safe by the same shared
        # helper the technical renderer already relies on.
        self.assertEqual(sanitize_label("DAL/Web"), "DAL_Web")
        self.assertEqual(sanitize_label("../etc"), "etc")


class RuntimeIndependenceTests(unittest.TestCase):
    def test_module_does_not_import_llm(self):
        import ast
        tree = ast.parse(Path("legacy_documenter/documentation/human_documentation_scaling.py").read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported_from = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(any(name and "llm" in name for name in imported | imported_from))

    def test_module_wiring_is_confined_to_pipeline_stages(self):
        # V4.3-R7 made the wiring decision R4 deliberately deferred (section 9
        # of docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md: "no decidir
        # en qué punto del pipeline full/analyze se invoca... corresponde a
        # una ronda posterior"): `pipeline_stages.render_documentation` now
        # calls `render_human_documentation_index`/`_partitions` to produce
        # `documentation/HUMAN_DOCUMENTATION.md` + `documentation/flujos_humanos/`.
        # `full_pipeline.py` and `main.py` still never reference this module
        # directly -- they call into `pipeline_stages`, which owns it.
        pipeline_stages_source = Path("legacy_documenter/cli/pipeline_stages.py").read_text(encoding="utf-8")
        self.assertIn("human_documentation_scaling", pipeline_stages_source)
        for module_path in ("legacy_documenter/cli/full_pipeline.py", "legacy_documenter/main.py"):
            path = Path(module_path)
            if path.exists():
                self.assertNotIn("human_documentation_scaling", path.read_text(encoding="utf-8"))

    def test_module_never_writes_to_disk(self):
        source = Path("legacy_documenter/documentation/human_documentation_scaling.py").read_text(encoding="utf-8")
        for forbidden in ("open(", "write_text", "os.", "requests.", "urllib"):
            self.assertNotIn(forbidden, source)


class WebformOwnerGroupKeySharedHelperTests(unittest.TestCase):
    """The shared `webform_owner_group_key` (`_documentation_partitioning.py`)
    is the single source of truth for the three-tier rule -- verified
    directly here, and via `flow_group_key`/`_web_entry_point_group_key`
    elsewhere, so the rule is never duplicated.
    """

    def test_folder_rule(self):
        self.assertEqual(webform_owner_group_key("webCobMorosidad\\cobCargaArcIntRea.ascx"), "webCobMorosidad")
        self.assertEqual(webform_owner_group_key("webCobMorosidad/cobCargaArcIntRea.ascx"), "webCobMorosidad")

    def test_rootless_file_falls_back_to_filename_stem(self):
        self.assertEqual(webform_owner_group_key("Default.aspx"), "Default")

    def test_missing_or_blank_falls_back_to_unassigned(self):
        self.assertEqual(webform_owner_group_key(None), "unassigned")
        self.assertEqual(webform_owner_group_key(""), "unassigned")
        self.assertEqual(webform_owner_group_key("   "), "unassigned")


# ----------------------------------------------------------------------
# Correction 2 (V4.3-R4, section 12): WEB_ENTRY_POINTS.md and
# PROJECT_DEPENDENCIES.md are reopened for the same navigation/partition
# split V4.2-R8 already applied to FUNCTIONAL_FLOWS.md/DATABASE_ACCESS.md/
# UNRESOLVED_FINDINGS.md -- WEBFORMS_MAP.md is deliberately left
# unpartitioned (see the result document's section 12 for the evidence and
# decision behind each of the three).
# ----------------------------------------------------------------------


def _entry_point(entry_id, webform, control="btn", event="Click", handler="H", confidence="confirmed"):
    return {
        "id": entry_id, "webform": webform, "control": control, "event": event,
        "type": "server_control", "handler": handler, "confidence": confidence,
    }


class WebEntryPointsPartitioningTests(unittest.TestCase):
    """Section 12: WEB_ENTRY_POINTS.md becomes navigation; detail is
    partitioned by WebForm-owning folder (never by project name).
    """

    def _indexes(self):
        return {
            "entry_points": [
                _entry_point("EP-1", "webCobMorosidad\\cobCargaArcIntRea.ascx", handler="btnCargar_Click"),
                _entry_point("EP-2", "webCobMorosidad\\cobChqInsRen.ascx", handler="HypGuardar_Click"),
                _entry_point("EP-3", "webOtro\\Otro.ascx", handler="Otro_Click", confidence="unresolved"),
                _entry_point("EP-4", None, handler="NoWebform_Click"),
            ],
            "event_bindings": [{"id": "EB-1"}, {"id": "EB-2"}, {"id": "EB-3"}, {"id": "EB-4"}],
        }

    def test_navigation_links_to_one_file_per_webform_owner_group(self):
        indexes = self._indexes()
        renderer = TechnicalDocumentationRenderer()
        nav = renderer.web_entry_points_navigation(indexes)
        partitions = renderer.web_entry_points_partitions(indexes)
        self.assertEqual(set(partitions), {
            build_partition_filenames(["webCobMorosidad"])["webCobMorosidad"],
            build_partition_filenames(["webOtro"])["webOtro"],
            build_partition_filenames(["unassigned"])["unassigned"],
        })
        for filename in partitions:
            self.assertIn(f"web_entry_points/{filename}", nav)

    def test_two_entries_in_the_same_folder_land_in_the_same_partition(self):
        partitions = TechnicalDocumentationRenderer().web_entry_points_partitions(self._indexes())
        webcob_filename = build_partition_filenames(["webCobMorosidad"])["webCobMorosidad"]
        text = partitions[webcob_filename]
        self.assertIn("btnCargar_Click", text)
        self.assertIn("HypGuardar_Click", text)

    def test_union_of_partitions_reproduces_the_flat_document_content_without_duplication(self):
        # An unresolved entry point legitimately appears twice within its own
        # single partition (once in "Por WebForm", once in "Puntos de entrada
        # no resueltos") -- exactly like the flat `web_entry_points()` document
        # already does for the same entry; "without duplication" means never
        # split across two *different* partitions, and the per-handler count
        # must match the flat document's own count exactly.
        indexes = self._indexes()
        renderer = TechnicalDocumentationRenderer()
        flat = renderer.web_entry_points(indexes)
        partitions = renderer.web_entry_points_partitions(indexes)
        for entry in indexes["entry_points"]:
            handler = entry["handler"]
            self.assertIn(handler, flat)
            flat_occurrences = flat.count(handler)
            partitions_with_handler = [text for text in partitions.values() if handler in text]
            self.assertEqual(len(partitions_with_handler), 1, handler)  # never split across two partitions
            self.assertEqual(partitions_with_handler[0].count(handler), flat_occurrences, handler)

    def test_unresolved_entry_stays_visible_within_its_own_group(self):
        partitions = TechnicalDocumentationRenderer().web_entry_points_partitions(self._indexes())
        webotro_filename = build_partition_filenames(["webOtro"])["webOtro"]
        self.assertIn("Puntos de entrada no resueltos", partitions[webotro_filename])
        self.assertIn("Otro_Click", partitions[webotro_filename])

    def test_partitions_are_deterministic_regardless_of_input_order(self):
        indexes = self._indexes()
        reversed_indexes = {**indexes, "entry_points": list(reversed(indexes["entry_points"]))}
        renderer = TechnicalDocumentationRenderer()
        self.assertEqual(renderer.web_entry_points_partitions(indexes), renderer.web_entry_points_partitions(reversed_indexes))

    def test_no_entry_points_produces_no_partitions(self):
        indexes = {"entry_points": [], "event_bindings": []}
        renderer = TechnicalDocumentationRenderer()
        self.assertEqual(renderer.web_entry_points_partitions(indexes), {})
        self.assertIn("No se descubrieron puntos de entrada web.", renderer.web_entry_points_navigation(indexes))

    def test_flat_method_is_unchanged_and_still_available(self):
        indexes = self._indexes()
        text = TechnicalDocumentationRenderer().web_entry_points(indexes)
        self.assertIn("# Web Entry Points", text)
        self.assertIn("## By WebForm", text)


class ProjectDependenciesPartitioningTests(unittest.TestCase):
    """Section 12: PROJECT_DEPENDENCIES.md becomes navigation; detail is
    partitioned by source project (`MarkdownExporter`, a different
    class/write path than `TechnicalDocumentationRenderer`).
    """

    def _indexes(self):
        return {
            "dependencies": [
                {"source": "WebApp", "target": "BusinessLogic", "dependency_type": "ProjectReference"},
                {"source": "WebApp", "target": "DataAccess", "dependency_type": "ProjectReference"},
                {"source": "BusinessLogic", "target": "DataAccess", "dependency_type": "ProjectReference"},
                # Non-project dependency types are excluded, same as the flat renderer.
                {"source": "WebApp", "target": "System.Web", "dependency_type": "AssemblyReference"},
            ],
        }

    def test_navigation_links_to_one_file_per_source_project(self):
        indexes = self._indexes()
        exporter = MarkdownExporter()
        nav = exporter.project_dependencies_navigation(indexes)
        partitions = exporter.project_dependencies_partitions(indexes)
        self.assertEqual(set(partitions), {
            build_partition_filenames(["WebApp"])["WebApp"],
            build_partition_filenames(["BusinessLogic"])["BusinessLogic"],
        })
        for filename in partitions:
            self.assertIn(f"project_dependencies/{filename}", nav)

    def test_union_of_partitions_reproduces_the_flat_document_content_without_duplication(self):
        indexes = self._indexes()
        exporter = MarkdownExporter()
        partitions = exporter.project_dependencies_partitions(indexes)
        project_edges = [d for d in indexes["dependencies"] if d["dependency_type"].startswith("Project")]
        total_edges_in_partitions = sum(text.count(" -> ") for text in partitions.values())
        self.assertEqual(total_edges_in_partitions, len(project_edges))
        webapp_filename = build_partition_filenames(["WebApp"])["WebApp"]
        self.assertEqual(partitions[webapp_filename].count(" -> "), 2)

    def test_non_project_dependency_types_are_excluded_same_as_the_flat_renderer(self):
        indexes = self._indexes()
        exporter = MarkdownExporter()
        for text in exporter.project_dependencies_partitions(indexes).values():
            self.assertNotIn("System.Web", text)

    def test_partitions_are_deterministic_regardless_of_input_order(self):
        indexes = self._indexes()
        reversed_indexes = {"dependencies": list(reversed(indexes["dependencies"]))}
        exporter = MarkdownExporter()
        self.assertEqual(
            exporter.project_dependencies_partitions(indexes), exporter.project_dependencies_partitions(reversed_indexes)
        )

    def test_no_dependencies_produces_no_partitions(self):
        indexes = {"dependencies": []}
        exporter = MarkdownExporter()
        self.assertEqual(exporter.project_dependencies_partitions(indexes), {})
        self.assertIn(
            "No se descubrieron dependencias de proyectos.", exporter.project_dependencies_navigation(indexes)
        )

    def test_flat_method_is_unchanged_and_still_available(self):
        indexes = self._indexes()
        text = MarkdownExporter().project_dependencies(indexes)
        self.assertIn("# Project Dependencies", text)
        self.assertIn("`WebApp` -> `BusinessLogic`", text)


class WebEntryPointsSpanishByDefaultTests(unittest.TestCase):
    """V4.3-R4 correction: WEB_ENTRY_POINTS.md's navigation/partitions (R4-authored)
    render in Spanish by default, per the project-wide human-documentation-in-
    Spanish requirement. Only the surrounding prose/headers are translated --
    WebForm paths, control ids, handler names and confidence values (real
    technical identifiers) are preserved verbatim. `web_entry_points()` (the
    pre-existing flat renderer, not R4-authored) is untouched and stays English --
    see `test_flat_method_is_unchanged_and_still_available` above.
    """

    def _indexes(self):
        return {
            "entry_points": [
                _entry_point("EP-1", "webCobMorosidad\\cobCargaArcIntRea.ascx", handler="btnCargar_Click"),
                _entry_point("EP-2", "webOtro\\Otro.ascx", handler="Otro_Click", confidence="unresolved"),
            ],
            "event_bindings": [{"id": "EB-1"}, {"id": "EB-2"}],
        }

    def test_navigation_is_in_spanish(self):
        nav = TechnicalDocumentationRenderer().web_entry_points_navigation(self._indexes())
        for spanish_text in (
            "# Puntos de entrada web", "## Grupos de puntos de entrada",
            "Grupo", "Confirmados", "No resueltos", "Detalle",
        ):
            self.assertIn(spanish_text, nav)
        for english_only_text in ("# Web Entry Points", "Entry Point Groups", "Confirmed |", "Detail |"):
            self.assertNotIn(english_only_text, nav)

    def test_partitions_are_in_spanish(self):
        partitions = TechnicalDocumentationRenderer().web_entry_points_partitions(self._indexes())
        for text in partitions.values():
            self.assertTrue(text.startswith("# Puntos de entrada web"))
            self.assertIn("## Por WebForm", text)
        webotro_filename = build_partition_filenames(["webOtro"])["webOtro"]
        text = partitions[webotro_filename]
        self.assertIn("| Control | Evento | Tipo | Manejador | Confianza |", text)
        self.assertIn("## Puntos de entrada no resueltos", text)
        self.assertIn("| WebForm | Control | Evento | Manejador |", text)
        for english_only_text in ("By WebForm", "Unresolved Entry Points", "Event |", "Handler |"):
            self.assertNotIn(english_only_text, text)

    def test_technical_names_are_preserved_intact(self):
        indexes = self._indexes()
        renderer = TechnicalDocumentationRenderer()
        nav = renderer.web_entry_points_navigation(indexes)
        partitions = renderer.web_entry_points_partitions(indexes)
        self.assertIn("webCobMorosidad", nav)
        self.assertIn("webOtro", nav)
        webcob_filename = build_partition_filenames(["webCobMorosidad"])["webCobMorosidad"]
        webcob_text = partitions[webcob_filename]
        self.assertIn("webCobMorosidad\\cobCargaArcIntRea.ascx", webcob_text)
        self.assertIn("btnCargar_Click", webcob_text)
        webotro_filename = build_partition_filenames(["webOtro"])["webOtro"]
        self.assertIn("Otro_Click", partitions[webotro_filename])
        self.assertIn("unresolved", partitions[webotro_filename])  # confidence value, a real identifier


class ProjectDependenciesSpanishByDefaultTests(unittest.TestCase):
    """V4.3-R4 correction: PROJECT_DEPENDENCIES.md's navigation/partitions
    (R4-authored) render in Spanish by default. Project names, `dependency_type`
    values (e.g. `ProjectReference`) and paths are preserved verbatim.
    `project_dependencies()` (the pre-existing flat renderer) is untouched.
    """

    def _indexes(self):
        return {
            "dependencies": [
                {"source": "WebApp", "target": "BusinessLogic", "dependency_type": "ProjectReference"},
                {"source": "WebApp", "target": "DataAccess", "dependency_type": "ProjectReference"},
            ],
        }

    def test_navigation_is_in_spanish(self):
        nav = MarkdownExporter().project_dependencies_navigation(self._indexes())
        for spanish_text in ("# Dependencias de proyectos", "Proyecto origen", "Dependencias", "Detalle"):
            self.assertIn(spanish_text, nav)
        for english_only_text in ("# Project Dependencies", "Source Project", "Detail |"):
            self.assertNotIn(english_only_text, nav)

    def test_partitions_are_in_spanish(self):
        partitions = MarkdownExporter().project_dependencies_partitions(self._indexes())
        webapp_filename = build_partition_filenames(["WebApp"])["WebApp"]
        text = partitions[webapp_filename]
        self.assertTrue(text.startswith("# Dependencias de proyectos"))
        self.assertNotIn("# Project Dependencies", text)

    def test_technical_names_are_preserved_intact(self):
        indexes = self._indexes()
        exporter = MarkdownExporter()
        nav = exporter.project_dependencies_navigation(indexes)
        partitions = exporter.project_dependencies_partitions(indexes)
        self.assertIn("WebApp", nav)
        webapp_filename = build_partition_filenames(["WebApp"])["WebApp"]
        text = partitions[webapp_filename]
        self.assertIn("`WebApp` -> `BusinessLogic`", text)
        self.assertIn("`WebApp` -> `DataAccess`", text)
        self.assertIn("ProjectReference", text)


class MarkdownExporterExportWritesProjectDependenciesPartitionsTests(unittest.TestCase):
    """`MarkdownExporter.export()` must write the PROJECT_DEPENDENCIES.md
    index plus its partition directory, and clean up stale partitions left
    by a previous run into the same output directory (same guarantee
    `sync_generated_partition_directory` already gives the other three
    partitioned documents).
    """

    def _base_indexes(self, dependencies):
        return {
            "repository": {"root": "C:\\repo", "stats": {}},
            "solutions": [],
            "dependencies": dependencies,
            "webforms": [],
            "configuration": [],
            "errors": [],
        }

    def test_export_writes_index_and_partition_directory(self):
        with TemporaryDirectory() as out:
            indexes = self._base_indexes([
                {"source": "WebApp", "target": "BusinessLogic", "dependency_type": "ProjectReference"},
                {"source": "Other", "target": "DataAccess", "dependency_type": "ProjectReference"},
            ])
            MarkdownExporter().export(out, indexes)
            doc_dir = Path(out) / "documentation"
            self.assertTrue((doc_dir / "PROJECT_DEPENDENCIES.md").is_file())
            index_text = (doc_dir / "PROJECT_DEPENDENCIES.md").read_text(encoding="utf-8")
            self.assertIn("project_dependencies/", index_text)
            part_dir = doc_dir / "project_dependencies"
            self.assertEqual(len(list(part_dir.glob("*.md"))), 2)

    def test_export_cleans_stale_partitions_from_a_previous_run(self):
        with TemporaryDirectory() as out:
            first = self._base_indexes([
                {"source": "WebApp", "target": "BusinessLogic", "dependency_type": "ProjectReference"},
                {"source": "Other", "target": "DataAccess", "dependency_type": "ProjectReference"},
            ])
            MarkdownExporter().export(out, first)
            part_dir = Path(out) / "documentation" / "project_dependencies"
            self.assertEqual(len(list(part_dir.glob("*.md"))), 2)

            second = self._base_indexes([
                {"source": "WebApp", "target": "BusinessLogic", "dependency_type": "ProjectReference"},
            ])
            MarkdownExporter().export(out, second)
            self.assertEqual(len(list(part_dir.glob("*.md"))), 1)


class RenderDocumentationWebEntryPointsWiringTests(unittest.TestCase):
    """`render_documentation` (pipeline_stages) writes WEB_ENTRY_POINTS.md as
    navigation and its partitions via the same
    `_PARTITIONED_DOCUMENTATION_RENDERERS` mechanism already exercised for
    FUNCTIONAL_FLOWS.md/etc. (V4.2-R8's own test pattern, reused here).
    """

    def _full_indexes(self, entry_points):
        return {
            "entry_points": entry_points, "event_bindings": [],
            "functional_flows": [], "functional_paths": [], "flow_summary": {}, "flow_unresolved": [],
            "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": [],
            "errors": [], "repository": {"root": "C:\\repo", "stats": {}},
        }

    def test_end_to_end_writes_navigation_and_partitions_and_removes_stale_ones_on_rerun(self):
        with TemporaryDirectory() as out:
            first = self._full_indexes([
                _entry_point("EP-1", "webA\\A.ascx", handler="A_Click"),
                _entry_point("EP-2", "webB\\B.ascx", handler="B_Click"),
            ])
            outcome = render_documentation(out, first)
            self.assertIn("WEB_ENTRY_POINTS.md", outcome.written)
            doc_dir = Path(out) / "documentation"
            self.assertTrue((doc_dir / "WEB_ENTRY_POINTS.md").is_file())
            wep_dir = doc_dir / "web_entry_points"
            self.assertEqual(len(list(wep_dir.glob("*.md"))), 2)
            nav_text = (doc_dir / "WEB_ENTRY_POINTS.md").read_text(encoding="utf-8")
            for filename in list(wep_dir.glob("*.md")):
                self.assertIn(filename.name, nav_text)

            second = self._full_indexes([_entry_point("EP-1", "webA\\A.ascx", handler="A_Click")])
            render_documentation(out, second)
            self.assertEqual(len(list(wep_dir.glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
