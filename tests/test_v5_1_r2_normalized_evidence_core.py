"""V5.1 R2 -- Normalized Evidence Core: implementation verification.

Covers, per `docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION_PROMPT.md`
section 12 and `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md` section 15:
unit tests (entities/ids/serialization), contract tests (the 5 resolved open
decisions + the CAL- ordinal correction + cardinalities), identity tests
(uniqueness/determinism/reproducibility/stability, especially CAL-/CMP-/
PRJ-/XDP-/UnresolvedBoundary), traceability tests, unresolved tests,
determinism tests (including the specific insertion-stability example from
the R2 prompt), and compatibility tests (legacy projection byte-equivalence).
Real IST regression against the actual target repository is a separate,
longer-running validation performed manually for the R2 result document
(scanning `C:\\Users\\cgalianj\\source\\IST_40\\Operacional` end to end is
minutes long and not suitable for the unit test suite's runtime budget);
this module instead uses `tests/fixtures/v4_2_r7_full_sample`, the same
fixture already covering V4.2/V4.3 regression, run through the full,
unmodified deterministic pipeline (`analyze_repository`) so every entity
covered here is a real resolver output, not a hand-built double.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.evidence.builder import REFERENCE_ADAPTER_ID, NormalizedEvidence, NormalizedEvidenceBuilder
from legacy_documenter.evidence.entities import SourceArtifact, UnresolvedBoundary
from legacy_documenter.evidence.identity import (
    Collision,
    DuplicateOrdinalAssigner,
    collision_summary,
    detect_collisions,
    poly33_id,
    sha256_id,
)
from legacy_documenter.evidence.invariants import (
    CANONICAL_ID_KINDS,
    IDENTITY_PRESERVING_KINDS,
    PROVENANCE_KINDS,
    InvariantViolation,
    build_reference_store,
    check_i1_id_unique_per_kind,
    check_i2_no_legacy_ref_as_identity,
    check_i3_entry_point_to_flow_cardinality,
    check_i6_no_invented_relations,
    check_i9_legacy_projection_byte_equivalence,
    check_i10_determinism,
    check_i11_segmentation_fields_consistent,
    identity_report,
    provenance_report,
    validate_evidence,
    validate_provenance,
)
from legacy_documenter.evidence.persistence import PARTITIONS, write_evidence
from legacy_documenter.evidence.projection import LegacyIndexProjector
from legacy_documenter.evidence.reference import (
    BrokenEvidenceReferenceError,
    EvidenceReference,
    EvidenceReferenceStore,
    resolve_against,
)
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"


def _build_fixture_indexes(output_dir: str) -> dict:
    return analyze_repository(FIXTURE, output_dir)


# ---------------------------------------------------------------------------
# Unit tests: identity primitives
# ---------------------------------------------------------------------------
class IdentityPrimitiveTests(unittest.TestCase):
    def test_sha256_id_is_deterministic(self) -> None:
        first = sha256_id("PRJ", "a/b.vbproj")
        second = sha256_id("PRJ", "a/b.vbproj")
        self.assertEqual(first, second)

    def test_sha256_id_format(self) -> None:
        result = sha256_id("PRJ", "x")
        self.assertTrue(result.startswith("PRJ-"))
        self.assertEqual(len(result), len("PRJ-") + 64)

    def test_sha256_id_distinguishes_part_order(self) -> None:
        self.assertNotEqual(sha256_id("CMP", "a", "b"), sha256_id("CMP", "b", "a"))

    def test_poly33_id_matches_legacy_flow_resolver_formula(self) -> None:
        from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver

        resolver = FunctionalFlowResolver()
        legacy = resolver._stable_id("CALL", "file.vb", 12, "Foo()", None)
        reimplemented = poly33_id("CALL", "file.vb", 12, "Foo()", None)
        self.assertEqual(legacy, reimplemented)

    def test_poly33_id_matches_legacy_database_resolver_formula(self) -> None:
        from legacy_documenter.analysis.database_resolver import DatabaseResolver

        resolver = DatabaseResolver()
        legacy = resolver._stable_id("DAO", "p", "c", "m", "read")
        reimplemented = poly33_id("DAO", "p", "c", "m", "read")
        self.assertEqual(legacy, reimplemented)


class CollisionDetectionTests(unittest.TestCase):
    def test_no_collision_for_unique_ids(self) -> None:
        records = [{"id": "A", "x": 1}, {"id": "B", "x": 2}]
        self.assertEqual(detect_collisions(records), [])

    def test_byte_identical_duplicates_are_a_collision(self) -> None:
        """V5.1 R3.1 D-1: same kind + same id on two records is a collision
        even when both records are byte-identical."""
        records = [{"id": "A", "x": 1}, {"id": "A", "x": 1}]
        self.assertEqual(detect_collisions(records), [Collision(id="A", count=2)])

    def test_collision_summary_reports_ids_and_records(self) -> None:
        records = [{"id": "A"}, {"id": "A"}, {"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "C"}]
        collisions = detect_collisions(records)
        self.assertEqual(collisions, [Collision(id="A", count=3), Collision(id="C", count=2)])
        self.assertEqual(collision_summary(collisions), {"duplicate_ids": 2, "records_involved": 5, "extra_records": 3})

    def test_check_i1_rejects_identical_and_different_duplicates_and_accepts_distinct_ids(self) -> None:
        with self.assertRaises(InvariantViolation):
            check_i1_id_unique_per_kind([{"id": "A", "x": 1}, {"id": "A", "x": 2}], "XDP")
        with self.assertRaises(InvariantViolation):
            check_i1_id_unique_per_kind([{"id": "A", "x": 1}, {"id": "A", "x": 1}], "XDP")
        check_i1_id_unique_per_kind([{"id": "A"}, {"id": "B"}], "XDP")  # must not raise

    def test_collision_for_same_id_different_content(self) -> None:
        records = [{"id": "A", "x": 1}, {"id": "A", "x": 2}]
        collisions = detect_collisions(records)
        self.assertEqual(collisions, [Collision(id="A", count=2)])


class DuplicateOrdinalAssignerTests(unittest.TestCase):
    def test_ordinals_within_one_group_are_sequential(self) -> None:
        assigner = DuplicateOrdinalAssigner()
        self.assertEqual(assigner.assign(("A",)), 0)
        self.assertEqual(assigner.assign(("B",)), 0)
        self.assertEqual(assigner.assign(("B",)), 1)

    def test_insertion_of_unrelated_record_does_not_shift_existing_ordinals(self) -> None:
        """The exact example from the R2 prompt section 4.1: A, B, B then
        X, A, B, B -- the two B's ordinals must stay 0 and 1 in both runs."""
        before = DuplicateOrdinalAssigner()
        ordinals_before = [before.assign(("A",)), before.assign(("B",)), before.assign(("B",))]

        after = DuplicateOrdinalAssigner()
        after.assign(("X",))
        ordinals_after = [after.assign(("A",)), after.assign(("B",)), after.assign(("B",))]

        self.assertEqual(ordinals_before, ordinals_after)
        self.assertEqual(ordinals_after, [0, 0, 1])


# ---------------------------------------------------------------------------
# Unit tests: EvidenceReference
# ---------------------------------------------------------------------------
class EvidenceReferenceTests(unittest.TestCase):
    def test_entity_reference_requires_kind_and_id(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceReference(ref_type="entity")

    def test_source_reference_requires_source_id(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceReference(ref_type="source")

    def test_textual_reference_requires_text(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceReference(ref_type="textual")

    def test_invalid_ref_type_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceReference(ref_type="not_a_real_type")

    def test_valid_entity_reference_round_trips_to_dict(self) -> None:
        ref = EvidenceReference.entity("FunctionalFlow", "FLOW-0000000001", legacy_ref=None)
        data = ref.to_dict()
        self.assertEqual(data["ref_type"], "entity")
        self.assertEqual(data["entity_id"], "FLOW-0000000001")
        self.assertNotIn("text", data)  # None fields are dropped, not serialized as null

    def test_resolve_against_succeeds_when_entity_present(self) -> None:
        store = EvidenceReferenceStore(entity_ids={("Component", "CMP-1")}, source_ids=set())
        resolve_against(EvidenceReference.entity("Component", "CMP-1"), store)  # must not raise

    def test_resolve_against_raises_for_broken_entity_reference(self) -> None:
        store = EvidenceReferenceStore(entity_ids=set(), source_ids=set())
        with self.assertRaises(BrokenEvidenceReferenceError):
            resolve_against(EvidenceReference.entity("Component", "CMP-missing"), store)

    def test_resolve_against_raises_for_broken_source_reference(self) -> None:
        store = EvidenceReferenceStore(entity_ids=set(), source_ids=set())
        with self.assertRaises(BrokenEvidenceReferenceError):
            resolve_against(EvidenceReference.source("SRC-missing"), store)

    def test_textual_reference_always_resolves(self) -> None:
        store = EvidenceReferenceStore(entity_ids=set(), source_ids=set())
        resolve_against(EvidenceReference.textual("some evidence text"), store)  # must not raise


# ---------------------------------------------------------------------------
# Unit tests: entities
# ---------------------------------------------------------------------------
class UnresolvedBoundaryStateTests(unittest.TestCase):
    def test_default_state_is_unresolved(self) -> None:
        boundary = UnresolvedBoundary(id="UNB-1", path_id="PATH-1", boundary_target="x", reason_code="unresolved_boundary")
        self.assertEqual(boundary.state, "unresolved")

    def test_state_cannot_be_anything_but_unresolved(self) -> None:
        with self.assertRaises(ValueError):
            UnresolvedBoundary(id="UNB-1", path_id="PATH-1", boundary_target="x", reason_code="unresolved_boundary", state="confirmed")


# ---------------------------------------------------------------------------
# Contract tests: R1's 5 open decisions, resolved in R2
# ---------------------------------------------------------------------------
class OpenDecisionResolutionTests(unittest.TestCase):
    """Each test asserts the concrete, code-level shape of one R2 resolution
    of an R1 `V5_1_R1_OPEN_DECISION` -- see the R2 result document for the
    evidence-based justification of each."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_3_1_solution_gets_sol_identity(self) -> None:
        for solution in self.evidence.solutions:
            self.assertTrue(solution.id.startswith("SOL-"))

    def test_3_3_component_discriminator_present_and_zero_based(self) -> None:
        for component in self.evidence.components:
            self.assertGreaterEqual(component.discriminator, 0)

    def test_3_4_conn_becomes_external_dependency_not_a_new_prefix(self) -> None:
        connections = [d for d in self.evidence.external_dependencies if d.dependency_kind == "database_connection"]
        for dependency in connections:
            self.assertTrue(dependency.id.startswith("XDP-"))
            self.assertIsNotNone(dependency.legacy_ref)

    def test_3_5_no_unknown_state_anywhere_in_normalized_evidence(self) -> None:
        for component in self.evidence.components:
            self.assertIn(component.state, ("confirmed", "unresolved"))
        for boundary in self.evidence.unresolved_boundaries:
            self.assertEqual(boundary.state, "unresolved")


# ---------------------------------------------------------------------------
# Identity tests over real resolver output (fixture, full pipeline)
# ---------------------------------------------------------------------------
class FixtureBackedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_i1_legacy_preserved_kinds_have_no_collisions(self) -> None:
        index_by_kind = {
            "EP": self.indexes["entry_points"],
            "EVB": self.indexes["event_bindings"],
            "FLOW": self.indexes["functional_flows"],
            "DAO": self.indexes["data_access"],
            "SP": self.indexes["stored_procedures"],
            "SQL": self.indexes["sql_operations"],
        }
        for kind in IDENTITY_PRESERVING_KINDS:
            if kind == "PATH":
                check_i1_id_unique_per_kind(self.indexes["functional_paths"], "PATH", id_field="path_id")
                continue
            check_i1_id_unique_per_kind(index_by_kind[kind], kind)  # must not raise

    def test_i1_new_v5_identities_have_no_collisions(self) -> None:
        check_i1_id_unique_per_kind(self.evidence.projects, "PRJ")
        check_i1_id_unique_per_kind([c.to_dict() for c in self.evidence.components], "CMP")
        check_i1_id_unique_per_kind([d.to_dict() for d in self.evidence.external_dependencies], "XDP")
        check_i1_id_unique_per_kind([c.to_dict() for c in self.evidence.call_identities], "CAL")
        check_i1_id_unique_per_kind([b.to_dict() for b in self.evidence.unresolved_boundaries], "UnresolvedBoundary")

    def test_i2_par_call_unres_never_used_as_canonical_id(self) -> None:
        check_i2_no_legacy_ref_as_identity([d.to_dict() for d in self.evidence.external_dependencies])
        check_i2_no_legacy_ref_as_identity([c.to_dict() for c in self.evidence.call_identities])
        check_i2_no_legacy_ref_as_identity([b.to_dict() for b in self.evidence.unresolved_boundaries])
        # And directly: legacy_ref values may start with CALL-, but `id` never does.
        for call in self.evidence.call_identities:
            self.assertFalse(call.id.startswith("CALL-"))
            self.assertTrue(call.id.startswith("CAL-"))

    def test_i3_entry_point_to_flow_cardinality(self) -> None:
        check_i3_entry_point_to_flow_cardinality(self.indexes["entry_points"], self.indexes["functional_flows"])

    def test_component_discriminator_disambiguates_the_one_known_real_duplicate(self) -> None:
        """Regression for the one real (file, name, kind) duplicate R0/R1
        measured on IST (`cc\\cc\\ccTMP.vb` / `ccRma1` / `class`); reproduced
        here with a synthetic pair sharing the same key, proving the two
        resulting CMP- ids differ."""
        symbols = [
            {"name": "ccRma1", "kind": "class", "file": "cc/cc/ccTMP.vb", "namespace_confidence": "confirmed"},
            {"name": "ccRma1", "kind": "class", "file": "cc/cc/ccTMP.vb", "namespace_confidence": "confirmed"},
        ]
        components = NormalizedEvidenceBuilder()._build_components(symbols, [])
        self.assertEqual([c.discriminator for c in components], [0, 1])
        self.assertNotEqual(components[0].id, components[1].id)


class CallIdentityStabilityTests(unittest.TestCase):
    """Direct, minimal reproduction of the CAL- insertion-stability
    requirement (R2 prompt section 4.1), independent of any fixture."""

    def _calls_payload(self, expressions: list[str]) -> list[dict]:
        return [
            {
                "file": "f.vb",
                "calls": [
                    {
                        "expression": expr,
                        "containing_class": "C",
                        "containing_method": "M",
                        "resolved_target": None,
                        "confidence": "unresolved",
                        "evidence": {"line": 10},
                    }
                    for expr in expressions
                ],
            }
        ]

    def test_unrelated_insertion_does_not_change_existing_call_ids(self) -> None:
        # Two calls with the identical base tuple (same file/line/expression/target) -- "B", "B".
        before = self._calls_payload(["B()", "B()"])
        ids_before = [c.id for c in NormalizedEvidenceBuilder()._build_call_identities(before)]

        # Insert an unrelated call "X()" first; the two "B()" calls must keep their ids.
        after = [
            {
                "file": "f.vb",
                "calls": [
                    {"expression": "X()", "containing_class": "C", "containing_method": "M", "resolved_target": None, "confidence": "unresolved", "evidence": {"line": 5}},
                    {"expression": "B()", "containing_class": "C", "containing_method": "M", "resolved_target": None, "confidence": "unresolved", "evidence": {"line": 10}},
                    {"expression": "B()", "containing_class": "C", "containing_method": "M", "resolved_target": None, "confidence": "unresolved", "evidence": {"line": 10}},
                ],
            }
        ]
        ids_after = [c.id for c in NormalizedEvidenceBuilder()._build_call_identities(after)]
        # ids_after[1:] corresponds to the two B() calls -- must equal ids_before exactly.
        self.assertEqual(ids_before, ids_after[1:])

    def test_duplicate_ordinal_is_part_of_the_id(self) -> None:
        calls = NormalizedEvidenceBuilder()._build_call_identities(self._calls_payload(["B()", "B()"]))
        self.assertEqual([c.duplicate_ordinal for c in calls], [0, 1])
        self.assertNotEqual(calls[0].id, calls[1].id)


# ---------------------------------------------------------------------------
# Determinism tests (I-10)
# ---------------------------------------------------------------------------
class DeterminismTests(unittest.TestCase):
    def test_same_indexes_produce_identical_normalized_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = _build_fixture_indexes(out)
        builder = NormalizedEvidenceBuilder()
        first = builder.build(indexes)
        second = builder.build(indexes)
        first_dump = _dump_evidence(first)
        second_dump = _dump_evidence(second)
        check_i10_determinism(first_dump, second_dump)  # must not raise
        self.assertEqual(first_dump, second_dump)


def _dump_evidence(evidence: NormalizedEvidence) -> dict:
    return {
        "source_artifacts": [a.to_dict() for a in evidence.source_artifacts],
        "solutions": [s.to_dict() for s in evidence.solutions],
        "projects": evidence.projects,
        "components": [c.to_dict() for c in evidence.components],
        "external_dependencies": [d.to_dict() for d in evidence.external_dependencies],
        "data_objects": [d.to_dict() for d in evidence.data_objects],
        "call_identities": [c.to_dict() for c in evidence.call_identities],
        "unresolved_boundaries": [b.to_dict() for b in evidence.unresolved_boundaries],
    }


# ---------------------------------------------------------------------------
# Compatibility tests: legacy projection byte-equivalence (I-9)
# ---------------------------------------------------------------------------
class LegacyProjectionCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name)
        cls.indexes = _build_fixture_indexes(str(cls.output))
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)
        cls.projected = LegacyIndexProjector(REFERENCE_ADAPTER_ID).project(cls.evidence)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_passthrough_indexes_are_identical(self) -> None:
        for key in (
            "entry_points", "event_bindings", "functional_flows", "functional_paths",
            "flow_unresolved", "data_access", "data_parameters", "calls", "dependencies",
            "functional_dependencies", "configuration", "errors", "logical_symbols", "flow_summary",
        ):
            with self.subTest(key=key):
                self.assertEqual(self.projected[key], self.indexes[key])

    def test_transformed_indexes_project_back_exactly(self) -> None:
        for key in ("files", "solutions", "projects", "symbols", "webforms", "stored_procedures", "sql_operations", "repository"):
            with self.subTest(key=key):
                self.assertEqual(self.projected[key], self.indexes[key])

    def test_i9_against_actual_on_disk_index_json(self) -> None:
        index_dir = self.output / "index"
        for key in ("files.json", "solutions.json", "projects.json", "symbols.json", "webforms.json", "entry_points.json"):
            with self.subTest(key=key):
                on_disk = json.loads((index_dir / key).read_text(encoding="utf-8"))
                projected_key = key[: -len(".json")]
                check_i9_legacy_projection_byte_equivalence({projected_key: self.projected[projected_key]}, {projected_key: on_disk})

    def test_i6_projection_cites_no_ids_absent_from_evidence(self) -> None:
        evidence_project_ids = {record["id"] for record in self.evidence.projects}
        projected_project_paths = {record["path"] for record in self.projected["projects"]}
        # Every projected project path must trace back to a project the evidence actually holds.
        evidence_paths = {record["extensions"][REFERENCE_ADAPTER_ID]["path"] for record in self.evidence.projects}
        check_i6_no_invented_relations(projected_project_paths, evidence_paths)
        self.assertTrue(evidence_project_ids)  # sanity: fixture actually has projects


# ---------------------------------------------------------------------------
# Traceability tests (I-4/I-5)
# ---------------------------------------------------------------------------
class TraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_every_component_source_ref_resolves_to_a_known_source_artifact(self) -> None:
        source_ids = {artifact.id for artifact in self.evidence.source_artifacts}
        store = EvidenceReferenceStore(entity_ids={("SourceArtifact", sid) for sid in source_ids}, source_ids=set())
        for component in self.evidence.components:
            if component.source_ref is None:
                continue
            resolve_against(EvidenceReference.entity("SourceArtifact", component.source_ref), store)  # must not raise


# ---------------------------------------------------------------------------
# Unresolved semantics tests
# ---------------------------------------------------------------------------
class UnresolvedSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_unresolved_boundaries_are_never_silently_confirmed(self) -> None:
        for boundary in self.evidence.unresolved_boundaries:
            self.assertEqual(boundary.state, "unresolved")

    def test_unresolved_boundary_count_matches_flow_unresolved_index(self) -> None:
        self.assertEqual(len(self.evidence.unresolved_boundaries), len(self.indexes["flow_unresolved"]))

    def test_absence_of_call_evidence_is_not_fabricated_as_confirmed(self) -> None:
        for call in self.evidence.call_identities:
            if call.resolved_target is None:
                self.assertEqual(call.state, "unresolved")


# ---------------------------------------------------------------------------
# Segmentation reserved-field consistency (I-11) -- fields not yet populated
# with real logic in V5.1, but their consistency rule must already hold.
# ---------------------------------------------------------------------------
class SegmentationFieldConsistencyTests(unittest.TestCase):
    def test_default_neutral_flow_has_no_segmentation_conflict(self) -> None:
        flow = {"id": "FLOW-1", "partial": False, "included_paths": [], "omitted_paths": []}
        check_i11_segmentation_fields_consistent(flow)  # must not raise

    def test_overlapping_included_and_omitted_is_rejected(self) -> None:
        flow = {"id": "FLOW-1", "partial": True, "included_paths": ["PATH-1"], "omitted_paths": ["PATH-1"]}
        with self.assertRaises(InvariantViolation):
            check_i11_segmentation_fields_consistent(flow)

    def test_partial_true_without_omitted_is_rejected(self) -> None:
        flow = {"id": "FLOW-1", "partial": True, "included_paths": ["PATH-1"], "omitted_paths": []}
        with self.assertRaises(InvariantViolation):
            check_i11_segmentation_fields_consistent(flow)


# ---------------------------------------------------------------------------
# Persistence round trip
# ---------------------------------------------------------------------------
class PersistenceTests(unittest.TestCase):
    def test_write_evidence_produces_manifest_and_readable_partitions(self) -> None:
        with tempfile.TemporaryDirectory() as fixture_out, tempfile.TemporaryDirectory() as persist_out:
            indexes = _build_fixture_indexes(fixture_out)
            evidence = NormalizedEvidenceBuilder().build(indexes)
            evidence_dir = write_evidence(evidence, persist_out)

            manifest = json.loads((evidence_dir / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertIn("entity_counts", manifest)
            self.assertIn("partition_sha256", manifest)
            for partition in PARTITIONS:
                self.assertTrue((evidence_dir / f"{partition}.json").exists())
                self.assertIn(partition, manifest["entity_counts"])

            reloaded_projects = json.loads((evidence_dir / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(len(reloaded_projects), len(evidence.projects))


# ---------------------------------------------------------------------------
# V5.1 R2.1 -- Instantiation as its own partition (R2.1-04)
# ---------------------------------------------------------------------------
class InstantiationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_instantiation_count_matches_calls_json_embedded_lists(self) -> None:
        expected = sum(len(entry.get("instantiations", [])) for entry in self.indexes["calls"])
        self.assertEqual(len(self.evidence.instantiations), expected)

    def test_instantiations_have_no_canonical_id_field(self) -> None:
        for item in self.evidence.instantiations:
            self.assertNotIn("id", item.to_dict())

    def test_instantiation_position_is_deterministic_per_source_artifact(self) -> None:
        by_artifact: dict[str, list[int]] = {}
        for item in self.evidence.instantiations:
            by_artifact.setdefault(item.source_artifact, []).append(item.position)
        for positions in by_artifact.values():
            self.assertEqual(positions, sorted(positions))
            self.assertEqual(positions, list(range(len(positions))))

    def test_instantiation_traces_back_to_a_known_source_artifact(self) -> None:
        source_ids = {a.id for a in self.evidence.source_artifacts}
        store = EvidenceReferenceStore(entity_ids={("SourceArtifact", sid) for sid in source_ids}, source_ids=set())
        for item in self.evidence.instantiations:
            resolve_against(EvidenceReference.entity("SourceArtifact", item.source_artifact), store)  # must not raise

    def test_instantiation_persists_as_its_own_partition(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            evidence_dir = write_evidence(self.evidence, out)
            self.assertTrue((evidence_dir / "instantiations.json").exists())
            reloaded = json.loads((evidence_dir / "instantiations.json").read_text(encoding="utf-8"))
            self.assertEqual(len(reloaded), len(self.evidence.instantiations))


# ---------------------------------------------------------------------------
# V5.1 R2.1 -- Runtime independence (R2.1-02)
# ---------------------------------------------------------------------------
class RuntimeIndependenceTests(unittest.TestCase):
    """The Evidence Core (production code) must never import development-only
    paths -- verified by AST, not by convention alone."""

    _FORBIDDEN_MODULE_PREFIXES = ("tools", "tests", "docs", "prompts", "PROJECT_STATE")
    _EVIDENCE_DIR = ROOT / "legacy_documenter" / "evidence"

    def _imported_module_names(self, path: Path) -> set[str]:
        import ast

        tree = ast.parse(path.read_text(encoding="utf-8"))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)
        return names

    def test_evidence_package_imports_no_development_only_paths(self) -> None:
        for path in sorted(self._EVIDENCE_DIR.glob("*.py")):
            with self.subTest(file=path.name):
                imports = self._imported_module_names(path)
                for forbidden in self._FORBIDDEN_MODULE_PREFIXES:
                    offending = {name for name in imports if name == forbidden or name.startswith(forbidden + ".")}
                    self.assertEqual(offending, set(), f"{path.name} imports development-only module(s): {offending}")

    # A blunt substring scan for "PROJECT_STATE.json"/"docs/"/"codex/" was
    # tried here and dropped: this module's own docstrings *explain* the
    # runtime-independence rule using those exact strings (e.g. `__init__.py`
    # states "It never reads docs/, prompts/, tests/, PROJECT_STATE.json"),
    # so a naive text scan flags the explanation, not a violation. The AST
    # import check above is the real, precise guarantee -- nothing here
    # imports from those paths, which is what would make a value from them
    # reachable at runtime in the first place.


# ---------------------------------------------------------------------------
# V5.1 R2.1 -- AI independence (R2.1-06)
# ---------------------------------------------------------------------------
class AiIndependenceTests(unittest.TestCase):
    _EVIDENCE_DIR = ROOT / "legacy_documenter" / "evidence"
    _FORBIDDEN_SUBSTRINGS = ("legacy_documenter.llm", "copilot", "openai", "anthropic", "ollama", "gemini")

    def test_evidence_package_never_imports_or_mentions_a_provider(self) -> None:
        for path in sorted(self._EVIDENCE_DIR.glob("*.py")):
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(file=path.name):
                for forbidden in self._FORBIDDEN_SUBSTRINGS:
                    self.assertNotIn(forbidden, text)

    def test_evidence_build_is_identical_whether_or_not_a_provider_would_be_available(self) -> None:
        # The Evidence Core takes only the already-computed `indexes` dict; it
        # has no branch, flag, or code path that could consult a provider.
        # This is a structural guarantee (proven above by import absence),
        # exercised here end to end: two builds from the same input are
        # identical, with no AI/provider involved in either.
        with tempfile.TemporaryDirectory() as out:
            indexes = _build_fixture_indexes(out)
        first = NormalizedEvidenceBuilder().build(indexes)
        second = NormalizedEvidenceBuilder().build(indexes)
        self.assertEqual(_dump_evidence(first), _dump_evidence(second))


# ---------------------------------------------------------------------------
# V5.1 R2.1 -- Technology Adapter boundary (R2.1-05)
# ---------------------------------------------------------------------------
class TechnologyAdapterBoundaryTests(unittest.TestCase):
    """The Core (`entities.py`, `reference.py`, `identity.py`, `invariants.py`,
    `projection.py`) must not hardcode or depend on VB.NET/WebForms/Oracle
    specifics; only `builder.py` -- the reference adapter's own wrapping
    layer -- may know which adapter it is."""

    _CORE_MODULES = ("entities.py", "reference.py", "identity.py", "invariants.py", "projection.py", "persistence.py")
    _EVIDENCE_DIR = ROOT / "legacy_documenter" / "evidence"

    # A blunt substring scan for "vbnet"/"webforms"/"aspx"/etc. across these
    # files was tried here and dropped: `entities.py` legitimately *names*
    # these technologies in its own docstrings while explaining exactly why
    # the core stays agnostic to them (e.g. describing `Component` as fusing
    # `Symbol`+`WebForm`, or listing `aspx`/`ascx` as example
    # `component_kind` *values* an adapter may produce into a neutral
    # field). The two tests below are the real, precise enforcement: no
    # module-level adapter constant exists to hardcode (every entity takes
    # `adapter_id` at construction), and no core module imports
    # `extractors`/`analysis` directly.

    def test_adapter_id_is_a_constructor_parameter_not_a_module_constant(self) -> None:
        builder = NormalizedEvidenceBuilder(adapter_id="future-adapter", adapter_version="0.1")
        with tempfile.TemporaryDirectory() as out:
            indexes = _build_fixture_indexes(out)
        evidence = builder.build(indexes)
        for artifact in evidence.source_artifacts:
            self.assertEqual(artifact.to_dict()["adapter"]["id"], "future-adapter")
        for component in evidence.components:
            self.assertEqual(component.to_dict()["adapter"]["id"], "future-adapter")

    def test_core_does_not_import_extractors_or_analysis_directly(self) -> None:
        import ast

        for name in self._CORE_MODULES:
            path = self._EVIDENCE_DIR / name
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
            with self.subTest(file=name):
                forbidden = {m for m in imports if m.startswith("legacy_documenter.extractors") or m.startswith("legacy_documenter.analysis")}
                self.assertEqual(forbidden, set())


# ---------------------------------------------------------------------------
# V5.1 R2.1 -- Production pipeline integration (R2.1-01)
# ---------------------------------------------------------------------------
class ProductionPipelineIntegrationTests(unittest.TestCase):
    """`evidence/` must be produced by the real `full`/`analyze` product
    flow, additively, without a second scan/analysis."""

    def test_full_pipeline_produces_evidence_directory(self) -> None:
        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "SUCCESS")
            evidence_dir = Path(out) / "evidence"
            self.assertTrue(evidence_dir.exists())
            self.assertTrue((evidence_dir / "EVIDENCE_MANIFEST.json").exists())

    def test_analyze_repository_also_produces_evidence_directory(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out)
            self.assertTrue((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())

    def test_run_summary_json_shape_is_unaffected_by_evidence_generation(self) -> None:
        """D-01: adding evidence/ must not change RUN_SUMMARY.json's field
        set or `output_locations` contents -- evidence/ is not one of the
        `StageId`-tracked writers."""
        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertNotIn("evidence", payload["output_locations"])
        stage_names = {s["stage"] for s in payload["stages"]}
        self.assertNotIn("EVIDENCE", stage_names)

    def test_evidence_build_failure_fails_export_and_the_run(self) -> None:
        """V5.1 R3.1 D-3: an Evidence Core failure is a run FAILURE, visible
        in RUN_SUMMARY.json; legacy artifacts already written are kept."""
        from unittest.mock import patch

        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        with tempfile.TemporaryDirectory() as out:
            with patch(
                "legacy_documenter.cli.pipeline_stages.NormalizedEvidenceBuilder.build",
                side_effect=RuntimeError("boom"),
            ):
                result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "FAILED")
            export = next(stage for stage in result.stages if stage.stage.value == "EXPORT")
            self.assertEqual(export.status.value, "FAILED")
            self.assertEqual((export.error.category, export.error.message), ("RuntimeError", "boom"))
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "FAILED")
            self.assertTrue((Path(out) / "index" / "entry_points.json").exists())
            self.assertFalse((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())

    def test_evidence_validation_failure_fails_the_run(self) -> None:
        from unittest.mock import patch

        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        with tempfile.TemporaryDirectory() as out:
            with patch(
                "legacy_documenter.cli.pipeline_stages.validate_evidence",
                side_effect=InvariantViolation("I-1: injected"),
            ):
                result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "FAILED")
            self.assertFalse((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())

    def test_evidence_failure_exits_non_zero_through_the_cli(self) -> None:
        from unittest.mock import patch

        from legacy_documenter.main import main

        with tempfile.TemporaryDirectory() as out:
            with patch(
                "legacy_documenter.cli.pipeline_stages.NormalizedEvidenceBuilder.build",
                side_effect=RuntimeError("boom"),
            ), self.assertLogs("legacy_documenter", level="ERROR"):
                exit_code = main(["full", str(FIXTURE), "--output", out])
            self.assertNotEqual(exit_code, 0)

    def test_evidence_failure_aborts_analyze(self) -> None:
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as out:
            with patch(
                "legacy_documenter.cli.pipeline_stages.NormalizedEvidenceBuilder.build",
                side_effect=RuntimeError("boom"),
            ):
                with self.assertRaises(RuntimeError):
                    analyze_repository(FIXTURE, out)

    def test_rerun_failure_never_leaves_a_stale_manifest(self) -> None:
        from unittest.mock import patch

        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(run_full_pipeline(FIXTURE, out, None, 12).status.value, "SUCCESS")
            self.assertTrue((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())
            with patch(
                "legacy_documenter.cli.pipeline_stages.NormalizedEvidenceBuilder.build",
                side_effect=RuntimeError("boom"),
            ):
                self.assertEqual(run_full_pipeline(FIXTURE, out, None, 12).status.value, "FAILED")
            self.assertFalse((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())


# ---------------------------------------------------------------------------
# V5.1 R3.1 -- XDP identity (D-1)
# ---------------------------------------------------------------------------
class ExternalDependencyIdentityTests(unittest.TestCase):
    def _projects(self, refs: list[dict], path: str = "p/a.vbproj") -> list[dict]:
        return [{"name": "a", "path": path, "assembly_references": refs}]

    def _ids(self, projects: list[dict]) -> list[str]:
        return [d.id for d in NormalizedEvidenceBuilder()._build_external_dependencies(projects, [])]

    def test_repeated_identical_references_get_distinct_ids(self) -> None:
        """Real IST shape: several `<Reference>` with empty Include in one project."""
        refs = [{"include": "", "hint_path": None} for _ in range(5)]
        dependencies = NormalizedEvidenceBuilder()._build_external_dependencies(self._projects(refs), [])
        self.assertEqual([d.duplicate_ordinal for d in dependencies], [0, 1, 2, 3, 4])
        self.assertEqual(len({d.id for d in dependencies}), 5)
        check_i1_id_unique_per_kind([d.to_dict() for d in dependencies], "XDP")

    def test_xdp_identity_is_deterministic(self) -> None:
        refs = [{"include": "System", "hint_path": None}, {"include": "", "hint_path": None}, {"include": "", "hint_path": None}]
        self.assertEqual(self._ids(self._projects(refs)), self._ids(self._projects(refs)))

    def test_xdp_identity_formula(self) -> None:
        ids = self._ids(self._projects([{"include": "X", "hint_path": "dll\\X.dll"}]))
        self.assertEqual(ids, [sha256_id("XDP", "assembly", "p/a.vbproj", "X", "dll\\X.dll", 0)])

    def test_unrelated_reference_insertion_does_not_change_existing_ids(self) -> None:
        refs = [{"include": "", "hint_path": None}, {"include": "", "hint_path": None}]
        before = self._ids(self._projects(refs))
        after = self._ids(self._projects([{"include": "New", "hint_path": None}] + refs))
        self.assertEqual(after[1:], before)

    def test_same_reference_in_different_projects_differs(self) -> None:
        ref = [{"include": "System", "hint_path": None}]
        self.assertNotEqual(self._ids(self._projects(ref, "p/a.vbproj")), self._ids(self._projects(ref, "p/b.vbproj")))


# ---------------------------------------------------------------------------
# V5.1 R3.1 -- mandatory SourceArtifact.sha256 (D-2) and I-1 gate
# ---------------------------------------------------------------------------
class MandatorySourceArtifactSha256Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_every_source_artifact_has_the_real_content_sha256(self) -> None:
        import hashlib

        self.assertEqual(len(self.evidence.source_artifacts), len(self.indexes["files"]))
        for artifact, record in zip(self.evidence.source_artifacts, self.indexes["files"]):
            expected = hashlib.sha256((FIXTURE / record["relative_path"]).read_bytes()).hexdigest()
            self.assertEqual(artifact.sha256, expected)

    def test_sha256_is_reproducible(self) -> None:
        again = NormalizedEvidenceBuilder().build(self.indexes)
        self.assertEqual([a.sha256 for a in again.source_artifacts], [a.sha256 for a in self.evidence.source_artifacts])

    def test_source_artifact_rejects_missing_or_malformed_sha256(self) -> None:
        for bad in (None, "", "abc", "A" * 64):
            with self.subTest(sha256=bad), self.assertRaises(ValueError):
                SourceArtifact(id="SRC-x", path="a.vb", size_bytes=1, artifact_kind="vb_source", adapter_id="a", adapter_version="1", sha256=bad)

    def test_build_fails_without_a_repository_root(self) -> None:
        indexes = {"repository": {}, "files": [{"relative_path": "a.vb", "size": 1, "file_type": "vb_source"}]}
        with self.assertRaises(ValueError):
            NormalizedEvidenceBuilder().build(indexes)

    def test_build_fails_when_a_listed_file_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            indexes = {"repository": {"root": root}, "files": [{"relative_path": "missing.vb", "size": 1, "file_type": "vb_source"}]}
            with self.assertRaises(OSError):
                NormalizedEvidenceBuilder().build(indexes)

    def test_production_evidence_partition_has_no_null_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out)
            artifacts = json.loads((Path(out) / "evidence" / "source_artifacts.json").read_text(encoding="utf-8"))
        self.assertTrue(artifacts)
        self.assertTrue(all(isinstance(a["sha256"], str) and len(a["sha256"]) == 64 for a in artifacts))

    def test_identity_report_covers_every_canonical_kind_with_zero_collisions(self) -> None:
        report = validate_evidence(self.evidence)
        self.assertEqual(set(report), set(CANONICAL_ID_KINDS))
        for kind, figures in report.items():
            with self.subTest(kind=kind):
                self.assertEqual(figures["records"], figures["unique_ids"])
                self.assertEqual(figures["duplicate_ids"], 0)

    def test_validate_evidence_rejects_a_duplicated_canonical_id(self) -> None:
        import copy

        evidence = copy.copy(self.evidence)
        evidence.external_dependencies = list(self.evidence.external_dependencies)
        self.assertTrue(evidence.external_dependencies)
        evidence.external_dependencies.append(evidence.external_dependencies[0])  # byte-identical duplicate
        self.assertEqual(identity_report(evidence)["ExternalDependency"]["duplicate_ids"], 1)
        with self.assertRaises(InvariantViolation):
            validate_evidence(evidence)


# ---------------------------------------------------------------------------
# V5.1 R3.2 -- D-4: provenance / EvidenceReference traceability (I-4/I-5)
# ---------------------------------------------------------------------------
class ProvenanceTraceabilityTests(unittest.TestCase):
    """Every entity `PROVENANCE_KINDS` names (every canonical kind except
    `SourceArtifact`, the root exception) must carry real, resolvable
    `provenance`, checked over the fixture's actual resolver output --
    never a hand-built double standing in for the whole entity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.indexes = _build_fixture_indexes(cls.tmp.name)
        cls.evidence = NormalizedEvidenceBuilder().build(cls.indexes)
        cls.store = build_reference_store(cls.evidence)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_1_entity_with_valid_provenance_passes(self) -> None:
        component = self.evidence.components[0]
        self.assertTrue(component.provenance)
        for ref in component.provenance:
            resolve_against(ref, self.store)  # must not raise

    def test_2_provenance_to_nonexistent_entity_fails(self) -> None:
        broken = EvidenceReference.entity("Project", "PRJ-does-not-exist")
        with self.assertRaises(BrokenEvidenceReferenceError):
            resolve_against(broken, self.store)

    def test_3_provenance_to_nonexistent_source_artifact_fails(self) -> None:
        broken = EvidenceReference.source("SRC-does-not-exist")
        with self.assertRaises(BrokenEvidenceReferenceError):
            resolve_against(broken, self.store)

    def test_4_valid_source_span_passes(self) -> None:
        artifact = self.evidence.source_artifacts[0]
        span = EvidenceReference.source_span(artifact.id, start_line=1, start_column=0, end_line=1, end_column=20)
        resolve_against(span, self.store)  # must not raise

    def test_5_invalid_source_span_fails(self) -> None:
        span = EvidenceReference.source_span("SRC-does-not-exist", start_line=1, start_column=0, end_line=1, end_column=20)
        with self.assertRaises(BrokenEvidenceReferenceError):
            resolve_against(span, self.store)

    def test_6_evidence_reference_serializes_deterministically(self) -> None:
        first = EvidenceReference.source("SRC-x", line=3, excerpt="Foo()").to_dict()
        second = EvidenceReference.source("SRC-x", line=3, excerpt="Foo()").to_dict()
        self.assertEqual(first, second)
        self.assertEqual(first, {"ref_type": "source", "source_id": "SRC-x", "line": 3, "excerpt": "Foo()"})
        # None-valued fields are dropped, not emitted as null -- same
        # "no inventes campos" discipline the rest of the Evidence Core uses.
        self.assertNotIn("entity_kind", first)
        self.assertNotIn("legacy_ref", first)

    def test_7_real_evidence_carries_provenance_where_the_contract_requires_it(self) -> None:
        """Every `PROVENANCE_KINDS` entity in the real fixture-derived
        evidence (not a synthetic double) has >=1 provenance reference, and
        every reference resolves -- `SourceArtifact` deliberately excluded
        (root exception, V5.0 R3)."""
        report = provenance_report(self.evidence, self.store)
        self.assertGreater(report["entities_checked"], 0)
        self.assertEqual(report["entities_with_empty_provenance"], 0)
        self.assertEqual(report["broken_references"], 0)
        self.assertNotIn("SourceArtifact", PROVENANCE_KINDS)

    def test_8_i4_runs_for_real_and_rejects_empty_provenance(self) -> None:
        import copy
        import dataclasses

        evidence = copy.copy(self.evidence)
        evidence.components = list(self.evidence.components)
        evidence.components[0] = dataclasses.replace(evidence.components[0], provenance=[])
        with self.assertRaises(InvariantViolation) as ctx:
            validate_provenance(evidence)
        self.assertIn("I-4", str(ctx.exception))

    def test_9_i5_runs_for_real_and_rejects_a_broken_reference(self) -> None:
        import copy
        import dataclasses

        evidence = copy.copy(self.evidence)
        evidence.components = list(self.evidence.components)
        evidence.components[0] = dataclasses.replace(
            evidence.components[0], provenance=[EvidenceReference.source("SRC-does-not-exist")]
        )
        with self.assertRaises(InvariantViolation) as ctx:
            validate_provenance(evidence)
        self.assertIn("I-5", str(ctx.exception))

    def test_10_i4_i5_failure_propagates_to_run_failure(self) -> None:
        """A broken `provenance` reference is caught by the production gate
        (`validate_evidence` -> `validate_provenance`) exactly like a broken
        `sha256`/duplicate id (V5.1 R3.1 D-3's failure semantics): the run
        is FAILED, the error is in `RUN_SUMMARY.json`, no stale manifest."""
        import dataclasses
        from unittest.mock import patch

        from legacy_documenter.cli.full_pipeline import run_full_pipeline

        real_build = NormalizedEvidenceBuilder.build

        def build_with_a_broken_provenance_reference(self, indexes):
            evidence = real_build(self, indexes)
            evidence.components = list(evidence.components)
            evidence.components[0] = dataclasses.replace(
                evidence.components[0], provenance=[EvidenceReference.source("SRC-does-not-exist")]
            )
            return evidence

        with tempfile.TemporaryDirectory() as out:
            with patch(
                "legacy_documenter.cli.pipeline_stages.NormalizedEvidenceBuilder.build",
                build_with_a_broken_provenance_reference,
            ):
                result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "FAILED")
            export = next(stage for stage in result.stages if stage.stage.value == "EXPORT")
            self.assertEqual(export.status.value, "FAILED")
            self.assertIn("I-5", export.error.message)
            self.assertTrue((Path(out) / "index" / "entry_points.json").exists())
            self.assertFalse((Path(out) / "evidence" / "EVIDENCE_MANIFEST.json").exists())

    def test_11_two_equivalent_builds_produce_identical_provenance(self) -> None:
        again = NormalizedEvidenceBuilder().build(self.indexes)
        self.assertEqual(
            [c.provenance for c in self.evidence.components], [c.provenance for c in again.components]
        )
        self.assertEqual(
            [d.provenance for d in self.evidence.external_dependencies],
            [d.provenance for d in again.external_dependencies],
        )
        self.assertEqual(
            [p["provenance"] for p in self.evidence.projects], [p["provenance"] for p in again.projects]
        )

    def test_provenance_persists_inside_evidence_json(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            evidence_dir = write_evidence(self.evidence, out)
            components = json.loads((evidence_dir / "components.json").read_text(encoding="utf-8"))
            projects = json.loads((evidence_dir / "projects.json").read_text(encoding="utf-8"))
        self.assertTrue(components)
        self.assertTrue(all(c["provenance"] for c in components))
        self.assertTrue(projects)
        self.assertTrue(all(p["provenance"] for p in projects))
        # Serialized provenance is plain JSON -- no dataclass survives the
        # round trip -- and each ref is one of the contract's four shapes.
        for ref in components[0]["provenance"]:
            self.assertIn(ref["ref_type"], ("entity", "source", "source_span", "textual"))

    def test_source_artifact_is_the_root_exception_no_provenance_field(self) -> None:
        artifact_dict = self.evidence.source_artifacts[0].to_dict()
        self.assertNotIn("provenance", artifact_dict)


if __name__ == "__main__":
    unittest.main()
