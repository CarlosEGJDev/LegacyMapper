"""V4.3-R8 -- External pilot corrections: verification tests.

Covers, per `prompts/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS.md` and the real
external pilot's own anonymized findings (never real pilot data/output --
`AGENTS.md` "Legacy Source Repository", R8's own restriction against
incorporating real pilot artifacts into this repository; every fixture below
is synthetic):

- **P-01 (human partition scaling)**: grouping by owning `.vbproj` project
  (`legacy_documenter.exporters._documentation_partitioning.owning_project_group_key`,
  `legacy_documenter.documentation.human_documentation_scaling.flow_group_key`)
  instead of collapsing into a generic container folder such as `proyectos`,
  plus second-layer, size-controlled sub-partitioning
  (`MAX_FLOWS_PER_GROUP_FILE`) for an owner/project with too many flows --
  lossless and duplicate-free.
- **P-02 (human flow verbosity)**: `render_flow_document` is summary-first
  (sections 3/4 before the exhaustive detail in section 8), and the
  exhaustive detail is never lost, only reordered.
- **P-03 (technical noise vs. uncertainty)**: a known infrastructure/
  lifecycle call (e.g. `dbc.BeginTrans`/`Commit`/`Rollback`/`Close`) that is
  also an unresolved boundary is presentation-only separated from a
  functionally relevant unresolved boundary, without promoting it to
  confirmed and without touching `EvidenceHydrator`/confidence/`terminal_type`.
- **P-03 follow-up (human review of the R8 samples)**: the same
  presentation-technical classification must not depend solely on an
  opaque terminal's own id/name. `DesplegarError`/`LimpiaNullDataset` (both
  already in `PRESENTATION_TECHNICAL_METHOD_NAMES`) still appeared in
  section 5's main business-services list and section 7's main unresolved
  list when they were reached as a *node* on a path whose own *terminal* was
  a separate, opaque id (e.g. `unknown_noise_1`) -- because those two
  sections only inspected the terminal, never the path's own nodes.
  `OpaqueTerminalNodeEvidenceTests` below covers the correction: a path's
  own node evidence is now consulted whenever its terminal is opaque, in
  both sections, without inventing a name the terminal itself never had and
  without misclassifying a genuinely unknown functional node as technical.

`REAL_AI_RUNTIME_CALL_ALLOWED=false`: nothing here reaches a provider; this
round does not touch `legacy_documenter.llm`/`legacy_documenter.orchestration`
at all.
"""
from __future__ import annotations

import unittest

from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.documentation.human_documentation_scaling import (
    MAX_FLOWS_PER_GROUP_FILE,
    flow_group_key,
    render_human_documentation_partitions,
)
from legacy_documenter.documentation.human_flow_documentation import render_flow_document
from legacy_documenter.exporters._documentation_partitioning import owning_project_group_key


# ----------------------------------------------------------------------
# P-01: owning-project grouping (never a generic container folder).
# ----------------------------------------------------------------------


class OwningProjectGroupKeyTests(unittest.TestCase):
    """`owning_project_group_key` prefers a resolved `.vbproj` project over
    the WebForm path's first folder segment -- the exact real-pilot defect:
    `proyectos\\WebApplication1\\WebApplication1\\WebWPF\\...` and
    `proyectos\\slnInformesSubsidios\\Backup\\WebInformesSubsidios\\...` both
    collapsed into the single generic container key `"proyectos"`.
    """

    def test_deeply_nested_container_folder_uses_the_resolved_project_instead(self):
        webform = "proyectos\\WebApplication1\\WebApplication1\\WebWPF\\Formulario.ascx"
        project_path = "C:\\repo\\proyectos\\WebApplication1\\WebApplication1\\WebWPF\\WebWPF.vbproj"
        self.assertEqual(owning_project_group_key(project_path, webform), "WebWPF")
        self.assertNotEqual(owning_project_group_key(project_path, webform), "proyectos")

    def test_two_different_deeply_nested_projects_no_longer_collapse_into_one_container_key(self):
        # The real pilot's own two examples: same container ("proyectos"),
        # different real owning projects -- must land in different groups
        # once project evidence is available.
        key_a = owning_project_group_key(
            "C:\\repo\\proyectos\\WebApplication1\\WebApplication1\\WebWPF\\WebWPF.vbproj",
            "proyectos\\WebApplication1\\WebApplication1\\WebWPF\\Formulario.ascx",
        )
        key_b = owning_project_group_key(
            "C:\\repo\\proyectos\\slnInformesSubsidios\\Backup\\WebInformesSubsidios\\WebInformesSubsidios.vbproj",
            "proyectos\\slnInformesSubsidios\\Backup\\WebInformesSubsidios\\Reporte.aspx",
        )
        self.assertNotEqual(key_a, key_b)
        self.assertNotIn("proyectos", (key_a, key_b))

    def test_forward_slash_project_path_is_handled_identically(self):
        backslash = owning_project_group_key("C:\\repo\\proyectos\\WebWPF\\WebWPF.vbproj", "proyectos\\WebWPF\\F.ascx")
        forward = owning_project_group_key("C:/repo/proyectos/WebWPF/WebWPF.vbproj", "proyectos/WebWPF/F.ascx")
        self.assertEqual(backslash, forward)
        self.assertEqual(forward, "WebWPF")

    def test_falls_back_to_webform_owner_group_key_when_no_project_evidence(self):
        # No regression on R4's own rule when there is genuinely no resolved
        # `.vbproj` project -- the pre-existing three-tier WebForm rule still
        # applies exactly as before.
        self.assertEqual(owning_project_group_key(None, "webCobMorosidad\\cobCargaArcIntRea.ascx"), "webCobMorosidad")
        self.assertEqual(owning_project_group_key("", "webCobMorosidad\\cobCargaArcIntRea.ascx"), "webCobMorosidad")
        self.assertEqual(owning_project_group_key("   ", None), "unassigned")

    def test_flow_group_key_uses_the_hydrated_entry_point_project_field(self):
        record = {
            "entry_point": {
                "webform": "proyectos\\WebApplication1\\WebApplication1\\WebWPF\\Formulario.ascx",
                "project": "C:\\repo\\proyectos\\WebApplication1\\WebApplication1\\WebWPF\\WebWPF.vbproj",
            }
        }
        self.assertEqual(flow_group_key(record), "WebWPF")

    def test_flow_group_key_without_a_project_field_is_unaffected(self):
        # Backward compatible: a hydrated record predating V4.3-R8 (no
        # `project` key at all) still groups exactly as V4.3-R4 left it.
        record = {"entry_point": {"webform": "webCobMorosidad\\cobCargaArcIntRea.ascx"}}
        self.assertEqual(flow_group_key(record), "webCobMorosidad")

    def test_hydrate_flow_surfaces_the_entry_point_project_field(self):
        ix = {
            "functional_flows": [{"id": "FLOW-A", "entry_point_id": "EP-A", "confidence": "confirmed", "project_sequence": []}],
            "functional_paths": [],
            "entry_points": [
                {
                    "id": "EP-A",
                    "webform": "proyectos\\WebWPF\\Formulario.ascx",
                    "event": "Load",
                    "handler": "Page_Load",
                    "start_method": "Page_Load",
                    "project": "C:\\repo\\proyectos\\WebWPF\\WebWPF.vbproj",
                }
            ],
            "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": [],
        }
        record = EvidenceHydrator().hydrate_flow("FLOW-A", ix)
        self.assertEqual(record["entry_point"]["project"], "C:\\repo\\proyectos\\WebWPF\\WebWPF.vbproj")
        self.assertEqual(flow_group_key(record), "WebWPF")


# ----------------------------------------------------------------------
# P-01: second-layer, size-controlled sub-partitioning within one owner.
# ----------------------------------------------------------------------


def _synthetic_large_group_ix(flow_count: int, project_path: str = "C:\\repo\\proyectos\\WebWPF\\WebWPF.vbproj"):
    """Builds `flow_count` distinct flows that all resolve to the SAME owning
    project (`project_path`) -- reproducing the real pilot's own "proyectos"
    group with 2983 flows in a single owner, at a synthetic scale small
    enough to run fast in a unit test.
    """
    flows, paths, entry_points = [], [], []
    for i in range(flow_count):
        flow_id = f"FLOW-{i:05d}"
        ep_id = f"EP-{i:05d}"
        path_id = f"PATH-{i:05d}"
        flows.append({"id": flow_id, "entry_point_id": ep_id, "confidence": "confirmed", "project_sequence": []})
        entry_points.append({
            "id": ep_id, "webform": f"proyectos\\WebWPF\\Formulario{i}.ascx", "event": "Load",
            "handler": "Page_Load", "start_method": "Page_Load", "project": project_path,
        })
        paths.append({
            "path_id": path_id, "flow_id": flow_id, "nodes": [], "terminal_type": "unresolved_boundary",
            "terminal_target": f"unknown_{i}", "confidence": "unresolved", "evidence_refs": [],
        })
    return {
        "functional_flows": flows, "functional_paths": paths, "entry_points": entry_points,
        "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": [],
    }


class SecondLayerSubPartitioningTests(unittest.TestCase):
    """P-01's second requirement: a single owner/project group with too many
    flows is itself sub-partitioned, deterministically, without truncating or
    losing any flow, and without duplicating any flow across two files.
    """

    def _hydrated(self, flow_count: int):
        ix = _synthetic_large_group_ix(flow_count)
        hydrator = EvidenceHydrator()
        return [hydrator.hydrate_flow(f["id"], ix) for f in ix["functional_flows"]]

    def test_group_at_or_under_the_threshold_still_produces_a_single_file(self):
        flows = self._hydrated(MAX_FLOWS_PER_GROUP_FILE)
        partitions = render_human_documentation_partitions(flows)
        self.assertEqual(set(partitions), {"WebWPF.md"})
        self.assertEqual(partitions["WebWPF.md"].count("# Flujo FLOW-"), MAX_FLOWS_PER_GROUP_FILE)

    def test_group_over_the_threshold_becomes_a_sub_index_plus_numbered_parts(self):
        flow_count = MAX_FLOWS_PER_GROUP_FILE + 137
        flows = self._hydrated(flow_count)
        partitions = render_human_documentation_partitions(flows)
        self.assertIn("WebWPF.md", partitions)
        self.assertIn("WebWPF-part-000001.md", partitions)
        self.assertIn("WebWPF-part-000002.md", partitions)
        self.assertNotIn("WebWPF-part-000003.md", partitions)
        # The sub-index itself holds no per-flow detail (résumé-antes-que-detalle,
        # one level deeper than the top-level index).
        self.assertNotIn("# Flujo FLOW-", partitions["WebWPF.md"])
        self.assertIn("## Particiones", partitions["WebWPF.md"])
        self.assertIn(str(flow_count), partitions["WebWPF.md"])

    def test_sub_partitioning_never_truncates_or_loses_a_flow(self):
        flow_count = MAX_FLOWS_PER_GROUP_FILE * 2 + 41
        flows = self._hydrated(flow_count)
        partitions = render_human_documentation_partitions(flows)
        part_names = [name for name in partitions if name != "WebWPF.md"]
        self.assertEqual(len(part_names), 3)  # 500 + 500 + 41
        total_occurrences = sum(partitions[name].count("# Flujo FLOW-") for name in part_names)
        self.assertEqual(total_occurrences, flow_count)

    def test_sub_partitioning_never_duplicates_a_flow_across_two_part_files(self):
        flow_count = MAX_FLOWS_PER_GROUP_FILE + 5
        flows = self._hydrated(flow_count)
        partitions = render_human_documentation_partitions(flows)
        part_names = [name for name in partitions if name != "WebWPF.md"]
        seen = set()
        for name in part_names:
            for flow_id in (f["flow_id"] for f in flows):
                if f"# Flujo {flow_id}:" in partitions[name]:
                    self.assertNotIn(flow_id, seen, f"{flow_id} appears in more than one sub-partition")
                    seen.add(flow_id)
        self.assertEqual(seen, {f["flow_id"] for f in flows})

    def test_the_union_of_sub_partitions_reproduces_every_input_flow_exactly_once(self):
        flow_count = MAX_FLOWS_PER_GROUP_FILE + 250
        flows = self._hydrated(flow_count)
        partitions = render_human_documentation_partitions(flows)
        occurrences = {f["flow_id"]: 0 for f in flows}
        for name, content in partitions.items():
            if name == "WebWPF.md":
                continue  # sub-index: no flow detail, deliberately excluded from this count
            for flow_id in occurrences:
                occurrences[flow_id] += content.count(f"# Flujo {flow_id}:")
        self.assertEqual(occurrences, {f["flow_id"]: 1 for f in flows})

    def test_sub_partitions_are_deterministic_regardless_of_input_order(self):
        flows = self._hydrated(MAX_FLOWS_PER_GROUP_FILE + 10)
        forward = render_human_documentation_partitions(flows)
        backward = render_human_documentation_partitions(list(reversed(flows)))
        self.assertEqual(forward, backward)

    def test_sub_partition_links_back_to_the_top_level_index(self):
        flows = self._hydrated(MAX_FLOWS_PER_GROUP_FILE + 1)
        partitions = render_human_documentation_partitions(flows)
        self.assertIn("[Volver al índice](../HUMAN_DOCUMENTATION.md)", partitions["WebWPF-part-000001.md"])
        self.assertIn("[Volver al índice](../HUMAN_DOCUMENTATION.md)", partitions["WebWPF.md"])


# ----------------------------------------------------------------------
# P-02/P-03 fixture: a flow with many confirmed paths and heavy technical/
# infrastructure noise, reproducing the real pilot's own
# `CobLiquidacionDeudaPrev.ascx` / `Page_Load` shape (94 paths, several
# confirmed business chains, dozens of low-human-value technical calls, a
# transaction pair recognized as infrastructure).
# ----------------------------------------------------------------------


def _verbose_noisy_flow_ix():
    return {
        "functional_flows": [
            {"id": "FLOW-BIG", "entry_point_id": "EP-BIG", "confidence": "confirmed", "project_sequence": []},
        ],
        "functional_paths": [
            # Two confirmed, non-technical business chains -- belong in section 4.
            {"path_id": "PATH-BIZ-1", "flow_id": "FLOW-BIG", "nodes": ["DAO-BIZ-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-1"]},
            {"path_id": "PATH-BIZ-2", "flow_id": "FLOW-BIG", "nodes": ["DAO-BIZ-2"], "terminal_type": "sql", "terminal_target": "SQL-1", "confidence": "confirmed", "evidence_refs": ["EVR-2"]},
            # Several technical/infrastructure paths -- deferred to section 8.
            {"path_id": "PATH-NOISE-1", "flow_id": "FLOW-BIG", "nodes": ["DAO-NOISE-1"], "terminal_type": "unresolved_boundary", "terminal_target": "unknown_noise_1", "confidence": "unresolved", "evidence_refs": ["EVR-3"]},
            {"path_id": "PATH-NOISE-2", "flow_id": "FLOW-BIG", "nodes": ["DAO-NOISE-2"], "terminal_type": "unresolved_boundary", "terminal_target": "unknown_noise_2", "confidence": "unresolved", "evidence_refs": ["EVR-4"]},
            # A transaction pair: BeginTrans/Commit, both real infrastructure
            # calls that resolve to a data-access record but whose own path is
            # an unresolved boundary (P-03's exact real-pilot shape).
            {"path_id": "PATH-TX-BEGIN", "flow_id": "FLOW-BIG", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "DAO-TX-BEGIN", "confidence": "confirmed", "evidence_refs": ["EVR-5"]},
            {"path_id": "PATH-TX-COMMIT", "flow_id": "FLOW-BIG", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "DAO-TX-COMMIT", "confidence": "confirmed", "evidence_refs": ["EVR-6"]},
            # A genuinely, functionally relevant unresolved boundary -- must
            # stay in the MAIN unresolved subsection, never demoted to infra.
            {"path_id": "PATH-REAL-GAP", "flow_id": "FLOW-BIG", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "UnknownHelper.ProcesarAlgo", "confidence": "unresolved", "evidence_refs": ["EVR-7"]},
        ],
        "entry_points": [
            {"id": "EP-BIG", "webform": "webCobMorosidad\\CobLiquidacionDeudaPrev.ascx", "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
        ],
        "data_access": [
            {"id": "DAO-BIZ-1", "class": "Planilla", "method": "obtenerGastosCobEJ", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "Planilla.vb", "line": 1}]},
            {"id": "DAO-BIZ-2", "class": "Planilla", "method": "obtenerLiqDeudaPrev", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "Planilla.vb", "line": 2}]},
            {"id": "DAO-NOISE-1", "class": "Formulario", "method": "DesplegarError", "operation_kind": "call", "confidence": "unresolved", "evidence": []},
            {"id": "DAO-NOISE-2", "class": "Formulario", "method": "LimpiaNullDataset", "operation_kind": "call", "confidence": "unresolved", "evidence": []},
            {"id": "DAO-TX-BEGIN", "class": "dbc", "method": "BeginTrans", "operation_kind": "transaction", "confidence": "confirmed", "evidence": [{"file": "Cob.vb", "line": 3, "expression": "dbc.BeginTrans()"}]},
            {"id": "DAO-TX-COMMIT", "class": "dbc", "method": "Commit", "operation_kind": "transaction", "confidence": "confirmed", "evidence": [{"file": "Cob.vb", "line": 4, "expression": "dbc.Commit()"}]},
        ],
        "stored_procedures": [
            {"id": "SP-1", "name": "PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ", "package": None, "procedure": None, "confidence": "confirmed", "evidence": [{"file": "Planilla.vb", "line": 1}]},
        ],
        "sql_operations": [
            {"id": "SQL-1", "operation": "PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV", "confidence": "confirmed"},
        ],
        "data_parameters": [],
    }


class SummaryFirstOrderingTests(unittest.TestCase):
    """P-02: the document is summary-first -- a short deterministic summary
    and the confirmed main paths come before any exhaustive listing, and the
    exhaustive listing (including technical/infrastructure paths) is
    deferred to the final detail section, never duplicated up front.
    """

    def _doc(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-BIG", _verbose_noisy_flow_ix())
        return render_flow_document(record)

    def test_sections_appear_in_summary_first_order(self):
        doc = self._doc()
        headings = [
            "## 1. Qué es y dónde está", "## 2. Evento/entrada inicial",
            "## 3. Resumen funcional determinista", "## 4. Rutas confirmadas principales",
            "## 5. Servicios/capas", "## 6. Datos/SP/SQL", "## 7. Qué queda no resuelto",
            "## 8. Evidencia técnica detallada / trazabilidad",
        ]
        positions = [doc.index(h) for h in headings]
        self.assertEqual(positions, sorted(positions))

    def test_summary_section_reports_deterministic_counts_before_any_path_detail(self):
        doc = self._doc()
        section_3 = doc.split("## 3.")[1].split("## 4.")[0]
        self.assertIn("7 camino(s) de ejecución evidenciado(s) en total", section_3)
        # No resolved business name/terminal is dumped into the summary itself.
        self.assertNotIn("PCOB_DEUDAS_ENCABEZADO", section_3)

    def test_main_paths_section_shows_only_confirmed_non_technical_business_chains(self):
        doc = self._doc()
        section_4 = doc.split("## 4.")[1].split("## 5.")[0]
        self.assertIn("PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ", section_4)
        self.assertIn("PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV", section_4)
        self.assertNotIn("DesplegarError", section_4)
        self.assertNotIn("LimpiaNullDataset", section_4)
        self.assertNotIn("BeginTrans", section_4)

    def test_exhaustive_detail_section_still_contains_every_path_including_noise(self):
        doc = self._doc()
        section_8 = doc.split("## 8.")[1]
        for marker in (
            "PATH-BIZ-1", "PATH-BIZ-2", "PATH-NOISE-1", "PATH-NOISE-2",
            "PATH-TX-BEGIN", "PATH-TX-COMMIT", "PATH-REAL-GAP",
            "DesplegarError", "LimpiaNullDataset",
        ):
            self.assertIn(marker, section_8)

    def test_nothing_is_removed_only_reordered_relative_to_the_whole_document(self):
        doc = self._doc()
        for marker in (
            "PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ", "PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV",
            "DesplegarError", "LimpiaNullDataset", "BeginTrans", "Commit",
            "UnknownHelper.ProcesarAlgo", "EVR-1", "EVR-2", "EVR-3", "EVR-4", "EVR-5", "EVR-6", "EVR-7",
        ):
            self.assertIn(marker, doc)


class TechnicalNoiseVsUncertaintyTests(unittest.TestCase):
    """P-03: a known infrastructure/lifecycle boundary (BeginTrans/Commit) is
    presentation-only separated from a functionally relevant unresolved
    boundary, without changing confidence/`terminal_type`, and without
    hiding or promoting anything.
    """

    def _doc(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-BIG", _verbose_noisy_flow_ix())
        return render_flow_document(record)

    def test_functionally_relevant_gap_is_in_the_main_unresolved_list(self):
        doc = self._doc()
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        main_subsection = section_7.split("### Límites técnicos/infraestructura")[0]
        self.assertIn("UnknownHelper.ProcesarAlgo", main_subsection)

    def test_known_infrastructure_boundaries_are_in_a_separate_labeled_subsection(self):
        doc = self._doc()
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        self.assertIn("### Límites técnicos/infraestructura (no resueltos, de naturaleza conocida)", section_7)
        infra_subsection = section_7.split("### Límites técnicos/infraestructura")[1]
        self.assertIn("dbc.BeginTrans", infra_subsection)
        self.assertIn("dbc.Commit", infra_subsection)

    def test_infrastructure_boundaries_never_appear_in_the_main_unresolved_list(self):
        doc = self._doc()
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        main_subsection = section_7.split("### Límites técnicos/infraestructura")[0]
        self.assertNotIn("dbc.BeginTrans", main_subsection)
        self.assertNotIn("dbc.Commit", main_subsection)

    def test_infrastructure_boundaries_are_still_declared_unresolved_never_promoted_to_confirmed(self):
        # Presentation-only: the underlying hydrated record still carries
        # these as `unresolved_boundary` terminals -- this test asserts the
        # hydrated record itself, not just the rendered prose, to guard
        # against a future change silently promoting them.
        record = EvidenceHydrator().hydrate_flow("FLOW-BIG", _verbose_noisy_flow_ix())
        boundary_ids = {b["id"] for b in record["terminals"]["unresolved_boundaries"]}
        self.assertIn("DAO-TX-BEGIN", boundary_ids)
        self.assertIn("DAO-TX-COMMIT", boundary_ids)

    def test_infrastructure_boundaries_remain_fully_traceable(self):
        doc = self._doc()
        self.assertIn("EVR-5", doc)
        self.assertIn("EVR-6", doc)
        self.assertIn("PATH-TX-BEGIN", doc)
        self.assertIn("PATH-TX-COMMIT", doc)


def _opaque_terminal_with_unknown_functional_node_ix():
    """A path whose own terminal is opaque (`unknown_func_1`, no
    `resolved_name`) but whose single node is a genuinely unknown, non-noise
    business call (`Planilla.CalcularSaldoPendiente` -- not in
    `PRESENTATION_TECHNICAL_METHOD_NAMES`). Used to prove the P-03 follow-up
    correction never over-classifies a path as technical just because its
    terminal happens to be opaque.
    """
    return {
        "functional_flows": [
            {"id": "FLOW-OPAQUE", "entry_point_id": "EP-OPAQUE", "confidence": "confirmed", "project_sequence": []},
        ],
        "functional_paths": [
            {"path_id": "PATH-FUNC-UNKNOWN", "flow_id": "FLOW-OPAQUE", "nodes": ["DAO-FUNC-UNKNOWN"], "terminal_type": "unresolved_boundary", "terminal_target": "unknown_func_1", "confidence": "unresolved", "evidence_refs": ["EVR-100"]},
        ],
        "entry_points": [
            {"id": "EP-OPAQUE", "webform": "webCobMorosidad\\Opaque.ascx", "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
        ],
        "data_access": [
            {"id": "DAO-FUNC-UNKNOWN", "class": "Planilla", "method": "CalcularSaldoPendiente", "operation_kind": "call", "confidence": "unresolved", "evidence": []},
        ],
        "stored_procedures": [], "sql_operations": [], "data_parameters": [],
    }


class OpaqueTerminalNodeEvidenceTests(unittest.TestCase):
    """P-03 follow-up: a path's own node evidence is consulted, in both
    section 5 (servicios/capas) and section 7 (qué queda no resuelto), when
    its terminal is opaque -- so `DesplegarError`/`LimpiaNullDataset` are
    never presented as business services or as a functionally relevant gap
    just because the terminal they happen to precede has no resolved name.
    A genuinely unknown functional node must NOT be reclassified as
    technical merely because its own terminal is also opaque.
    """

    def _doc(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-BIG", _verbose_noisy_flow_ix())
        return render_flow_document(record)

    def test_opaque_terminal_with_desplegarerror_node_is_classified_infrastructure(self):
        doc = self._doc()
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        infra_subsection = section_7.split("### Límites técnicos/infraestructura")[1]
        main_subsection = section_7.split("### Límites técnicos/infraestructura")[0]
        self.assertIn("unknown_noise_1", infra_subsection)
        self.assertIn("DesplegarError", infra_subsection)
        self.assertNotIn("unknown_noise_1", main_subsection)

    def test_opaque_terminal_with_limpianulldataset_node_is_classified_infrastructure(self):
        doc = self._doc()
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        infra_subsection = section_7.split("### Límites técnicos/infraestructura")[1]
        main_subsection = section_7.split("### Límites técnicos/infraestructura")[0]
        self.assertIn("unknown_noise_2", infra_subsection)
        self.assertIn("LimpiaNullDataset", infra_subsection)
        self.assertNotIn("unknown_noise_2", main_subsection)

    def test_opaque_terminal_with_unknown_functional_node_is_not_classified_technical(self):
        record = EvidenceHydrator().hydrate_flow("FLOW-OPAQUE", _opaque_terminal_with_unknown_functional_node_ix())
        doc = render_flow_document(record)
        section_7 = doc.split("## 7.")[1].split("## 8.")[0]
        self.assertNotIn("### Límites técnicos/infraestructura", section_7)
        self.assertIn("unknown_func_1", section_7)
        section_5 = doc.split("## 5.")[1].split("## 6.")[0]
        self.assertNotIn("### Elementos técnicos/auxiliares", section_5)
        self.assertIn("`Planilla.CalcularSaldoPendiente`", section_5)

    def test_main_services_list_excludes_all_presentation_technical_callers(self):
        doc = self._doc()
        section_5 = doc.split("## 5.")[1].split("## 6.")[0]
        main_list = section_5.split("### Elementos técnicos/auxiliares")[0]
        noise_subsection = section_5.split("### Elementos técnicos/auxiliares")[1]
        self.assertNotIn("DesplegarError", main_list)
        self.assertNotIn("LimpiaNullDataset", main_list)
        self.assertIn("Planilla.obtenerGastosCobEJ", main_list)
        self.assertIn("Planilla.obtenerLiqDeudaPrev", main_list)
        self.assertIn("Formulario.DesplegarError", noise_subsection)
        self.assertIn("Formulario.LimpiaNullDataset", noise_subsection)

    def test_section_8_still_contains_every_reclassified_path_in_full(self):
        # The reclassification in sections 5/7 never removes anything from
        # the exhaustive detail section.
        doc = self._doc()
        section_8 = doc.split("## 8.")[1]
        for marker in (
            "PATH-NOISE-1", "PATH-NOISE-2", "DesplegarError", "LimpiaNullDataset",
            "unknown_noise_1", "unknown_noise_2", "EVR-3", "EVR-4",
        ):
            self.assertIn(marker, section_8)


# ----------------------------------------------------------------------
# Path/evidence-ref preservation across the full P-01/P-02/P-03 correction.
# ----------------------------------------------------------------------


class EvidencePreservationTests(unittest.TestCase):
    """None of this round's presentation/grouping corrections may drop or
    rewrite a `path_id`/`evidence_ref` -- `EvidenceHydrator` itself is
    unmodified by these findings (R8's own restriction).
    """

    def test_every_path_id_and_evidence_ref_survives_hydration_and_rendering_unchanged(self):
        ix = _verbose_noisy_flow_ix()
        record = EvidenceHydrator().hydrate_flow("FLOW-BIG", ix)
        input_path_ids = {p["path_id"] for p in ix["functional_paths"]}
        input_evidence_refs = {r for p in ix["functional_paths"] for r in p["evidence_refs"]}
        hydrated_path_ids = {pid for p in record["paths"] for pid in p["path_ids"]}
        hydrated_evidence_refs = {r for p in record["paths"] for r in p["evidence_refs"]}
        self.assertEqual(hydrated_path_ids, input_path_ids)
        self.assertEqual(hydrated_evidence_refs, input_evidence_refs)
        doc = render_flow_document(record)
        for path_id in input_path_ids:
            self.assertIn(path_id, doc)
        for evidence_ref in input_evidence_refs:
            self.assertIn(evidence_ref, doc)


if __name__ == "__main__":
    unittest.main()
