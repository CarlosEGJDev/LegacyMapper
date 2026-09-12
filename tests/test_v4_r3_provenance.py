import unittest

from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.domain.models import Origin, Provenance
from legacy_documenter.knowledge.input.contracts import SourceInput
from legacy_documenter.knowledge.provenance.contract_report import (
    build_provenance_contract,
    render_provenance_contract_json,
)
from legacy_documenter.knowledge.provenance.enums import (
    EdgeRelationship,
    LineageCompleteness,
    NodeKind,
    TransformationType,
)
from legacy_documenter.knowledge.provenance.graph import ProvenanceGraph, material_node_from_source_input
from legacy_documenter.knowledge.provenance.models import (
    ProvenanceEdge,
    ProvenanceNode,
    ProvenanceValidationError,
    new_edge_id,
    new_node_id,
)


def _node(node_id, kind, source_type=None, reference=None, origin=None, status=LineageCompleteness.UNRESOLVED,
          metadata=None):
    return ProvenanceNode(node_id=node_id, node_kind=kind, source_type=source_type, reference=reference,
                           origin=origin, provenance_status=status, metadata=metadata or {})


def _edge(edge_id, frm, to, relationship, transformation=None):
    return ProvenanceEdge(edge_id=edge_id, from_node_id=frm, to_node_id=to, relationship=relationship,
                           transformation=transformation)


class BasicLineageTests(unittest.TestCase):
    def test_material_evidence_statement_traversal_both_directions(self):
        g = ProvenanceGraph()
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_node(_node("E1", NodeKind.EVIDENCE, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_node(_node("S1", NodeKind.STATEMENT, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_edge(_edge("PED-1", "M1", "E1", EdgeRelationship.EVIDENCE_FROM))
        g.add_edge(_edge("PED-2", "E1", "S1", EdgeRelationship.DERIVED_FROM))

        self.assertEqual(g.children_of("M1"), ["E1"])
        self.assertEqual(g.children_of("E1"), ["S1"])
        self.assertEqual(g.parents_of("S1"), ["E1"])
        self.assertEqual(g.parents_of("E1"), ["M1"])
        self.assertEqual(g.ancestors_of("S1"), ["E1", "M1"])
        self.assertEqual(g.descendants_of("M1"), ["E1", "S1"])


class HumanOnlyProvenanceTests(unittest.TestCase):
    def test_fully_human_lineage_valid_without_code(self):
        g = ProvenanceGraph()
        origin = Origin(kind="HUMAN_INPUT", contributor="Technical Lead")
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT, origin=origin))
        g.add_node(_node("S1", NodeKind.STATEMENT, source_type=SourceType.HUMAN_REQUIREMENT, origin=origin))
        g.add_edge(_edge("PED-1", "M1", "S1", EdgeRelationship.DERIVED_FROM, TransformationType.HUMAN_SUPPLIED))
        self.assertEqual(g.parents_of("S1"), ["M1"])
        for node_id in ("M1", "S1"):
            fields = vars(g.get_node(node_id))
            self.assertFalse(any(k in fields.get("metadata", {}) for k in ("file", "symbol", "project", "language")))


class CodeOnlyProvenanceTests(unittest.TestCase):
    def test_deterministic_code_fact_lineage_valid(self):
        g = ProvenanceGraph()
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.DETERMINISTIC_CODE_FACT,
                          reference="Modulo1.vb:10", origin=Origin(kind="CODE_REPOSITORY", reference="Modulo1.vb")))
        g.add_node(_node("E1", NodeKind.EVIDENCE, source_type=SourceType.DETERMINISTIC_CODE_FACT,
                          reference="Modulo1.vb:10"))
        g.add_edge(_edge("PED-1", "M1", "E1", EdgeRelationship.EVIDENCE_FROM, TransformationType.DETERMINISTIC_EXTRACTION))
        self.assertEqual(g.parents_of("E1"), ["M1"])


class MixedProvenanceTests(unittest.TestCase):
    def test_human_requirement_code_fact_and_standard_all_contribute_and_remain_visible(self):
        g = ProvenanceGraph()
        g.add_node(_node("REQ", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_node(_node("CODE", NodeKind.MATERIAL, source_type=SourceType.DETERMINISTIC_CODE_FACT, reference="M.vb:1"))
        g.add_node(_node("STD", NodeKind.MATERIAL, source_type=SourceType.CORPORATE_STANDARD, reference="STD-1"))
        g.add_node(_node("DERIVED", NodeKind.PROPOSAL))
        g.add_edge(_edge("PED-1", "REQ", "DERIVED", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-2", "CODE", "DERIVED", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-3", "STD", "DERIVED", EdgeRelationship.DERIVED_FROM))
        self.assertEqual(g.parents_of("DERIVED"), ["CODE", "REQ", "STD"])


class PartialProvenanceTests(unittest.TestCase):
    def test_partial_provenance_stays_partial(self):
        g = ProvenanceGraph()
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.PROJECT_DOCUMENT,
                          status=LineageCompleteness.PARTIAL))
        self.assertEqual(g.lineage_completeness("M1"), LineageCompleteness.PARTIAL)


class UnresolvedProvenanceTests(unittest.TestCase):
    def test_explicit_unresolved_stays_unresolved(self):
        g = ProvenanceGraph()
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.UNRESOLVED))
        self.assertEqual(g.lineage_completeness("M1"), LineageCompleteness.UNRESOLVED)

    def test_default_status_is_unresolved_not_fabricated_complete(self):
        node = _node("M1", NodeKind.MATERIAL)
        self.assertEqual(node.provenance_status, LineageCompleteness.UNRESOLVED)


class RootDiscoveryTests(unittest.TestCase):
    def test_roots_are_deterministic_and_not_privileged(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        g.add_node(_node("B", NodeKind.EVIDENCE))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))
        self.assertEqual(g.roots_of(), ["A"])
        # a root carries no authority/approval field at all
        self.assertFalse(hasattr(g.get_node("A"), "authoritative"))
        self.assertFalse(hasattr(g.get_node("A"), "approved"))


class MultiParentTests(unittest.TestCase):
    def test_all_parents_and_full_ancestry_preserved(self):
        g = ProvenanceGraph()
        for n in ("A", "B", "C"):
            g.add_node(_node(n, NodeKind.MATERIAL))
        g.add_node(_node("D", NodeKind.STATEMENT))
        g.add_node(_node("E", NodeKind.STATEMENT))
        g.add_edge(_edge("PED-1", "A", "D", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-2", "B", "D", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-3", "C", "D", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-4", "D", "E", EdgeRelationship.DERIVED_FROM))
        self.assertEqual(g.parents_of("D"), ["A", "B", "C"])
        self.assertEqual(g.ancestors_of("E"), ["A", "B", "C", "D"])


class CycleRejectionTests(unittest.TestCase):
    def test_self_cycle_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-1", "A", "A", EdgeRelationship.REFERENCES))

    def test_two_node_cycle_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        g.add_node(_node("B", NodeKind.EVIDENCE))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-2", "B", "A", EdgeRelationship.EVIDENCE_FROM))

    def test_longer_cycle_rejected(self):
        g = ProvenanceGraph()
        for n in ("A", "B", "C"):
            g.add_node(_node(n, NodeKind.MATERIAL))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.DERIVED_FROM))
        g.add_edge(_edge("PED-2", "B", "C", EdgeRelationship.DERIVED_FROM))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-3", "C", "A", EdgeRelationship.DERIVED_FROM))


class DanglingReferenceTests(unittest.TestCase):
    def test_missing_source_node_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("B", NodeKind.EVIDENCE))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-1", "GHOST", "B", EdgeRelationship.EVIDENCE_FROM))

    def test_missing_destination_node_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-1", "A", "GHOST", EdgeRelationship.EVIDENCE_FROM))


class DuplicateNodeTests(unittest.TestCase):
    def test_same_id_same_semantics_is_idempotent(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_node(_node("A", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        self.assertEqual(g.get_node("A").source_type, SourceType.HUMAN_REQUIREMENT)

    def test_same_id_conflicting_semantics_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        with self.assertRaises(ProvenanceValidationError):
            g.add_node(_node("A", NodeKind.MATERIAL, source_type=SourceType.CORPORATE_STANDARD))


class DuplicateEdgeTests(unittest.TestCase):
    def test_exact_duplicate_edge_is_idempotent(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        g.add_node(_node("B", NodeKind.EVIDENCE))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))
        self.assertEqual(g.children_of("A"), ["B"])

    def test_conflicting_duplicate_edge_rejected(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        g.add_node(_node("B", NodeKind.EVIDENCE))
        g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))
        with self.assertRaises(ProvenanceValidationError):
            g.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.DERIVED_FROM))


class DeterministicIdentityTests(unittest.TestCase):
    def test_equivalent_normalized_lineage_produces_same_ids(self):
        id1 = new_node_id(NodeKind.MATERIAL.value, SourceType.HUMAN_REQUIREMENT.value, "x")
        id2 = new_node_id(NodeKind.MATERIAL.value, SourceType.HUMAN_REQUIREMENT.value, "x")
        self.assertEqual(id1, id2)

    def test_different_inputs_produce_different_ids(self):
        id1 = new_edge_id("A", "B")
        id2 = new_edge_id("A", "C")
        self.assertNotEqual(id1, id2)


class DeterministicSerializationTests(unittest.TestCase):
    def test_equivalent_graphs_different_insertion_order_serialize_identically(self):
        g1 = ProvenanceGraph()
        g1.add_node(_node("A", NodeKind.MATERIAL))
        g1.add_node(_node("B", NodeKind.EVIDENCE))
        g1.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))

        g2 = ProvenanceGraph()
        g2.add_node(_node("B", NodeKind.EVIDENCE))
        g2.add_node(_node("A", NodeKind.MATERIAL))
        g2.add_edge(_edge("PED-1", "A", "B", EdgeRelationship.EVIDENCE_FROM))

        self.assertEqual(g1.render_canonical_json(), g2.render_canonical_json())


class AIAncestryTests(unittest.TestCase):
    def test_direct_ai_derived_node_detected(self):
        g = ProvenanceGraph()
        g.add_node(_node("AI1", NodeKind.INTERPRETATION, source_type=SourceType.AI_INTERPRETATION))
        self.assertTrue(g.has_ai_ancestry("AI1"))

    def test_indirect_descendant_of_ai_node_detected(self):
        g = ProvenanceGraph()
        g.add_node(_node("AI1", NodeKind.INTERPRETATION, source_type=SourceType.AI_INTERPRETATION))
        g.add_node(_node("S1", NodeKind.STATEMENT, source_type=SourceType.PROJECT_DOCUMENT))
        g.add_edge(_edge("PED-1", "AI1", "S1", EdgeRelationship.INTERPRETED_FROM))
        self.assertTrue(g.has_ai_ancestry("S1"))

    def test_non_ai_lineage_returns_false(self):
        g = ProvenanceGraph()
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_node(_node("S1", NodeKind.STATEMENT, source_type=SourceType.HUMAN_REQUIREMENT))
        g.add_edge(_edge("PED-1", "M1", "S1", EdgeRelationship.DERIVED_FROM))
        self.assertFalse(g.has_ai_ancestry("S1"))

    def test_ai_ancestry_detectable_through_multiple_levels(self):
        g = ProvenanceGraph()
        g.add_node(_node("AI1", NodeKind.INTERPRETATION, source_type=SourceType.AI_INTERPRETATION))
        g.add_node(_node("P1", NodeKind.PROPOSAL, source_type=SourceType.PROJECT_DOCUMENT))
        g.add_node(_node("K1", NodeKind.KNOWLEDGE, source_type=SourceType.PROJECT_DOCUMENT))
        g.add_edge(_edge("PED-1", "AI1", "P1", EdgeRelationship.INTERPRETED_FROM))
        g.add_edge(_edge("PED-2", "P1", "K1", EdgeRelationship.DERIVED_FROM))
        self.assertTrue(g.has_ai_ancestry("K1"))


class HumanOriginPreservationTests(unittest.TestCase):
    def test_normalization_does_not_erase_original_human_origin(self):
        g = ProvenanceGraph()
        human_origin = Origin(kind="HUMAN_INPUT", contributor="Technical Lead")
        g.add_node(_node("M1", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT, origin=human_origin))
        g.add_node(_node("M2", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT, origin=human_origin))
        g.add_edge(_edge("PED-1", "M1", "M2", EdgeRelationship.DERIVED_FROM, TransformationType.NORMALIZATION))
        self.assertEqual(g.get_node("M2").origin.kind, "HUMAN_INPUT")
        self.assertEqual(g.get_node("M2").origin.contributor, "Technical Lead")
        self.assertNotEqual(g.get_node("M2").origin.kind, "LegacyMapper")


class AuthoritySeparationTests(unittest.TestCase):
    def test_traceable_source_does_not_become_authoritative(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL, status=LineageCompleteness.COMPLETE))
        self.assertFalse(hasattr(g.get_node("A"), "authoritative"))

    def test_root_does_not_become_authoritative(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL))
        self.assertIn("A", g.roots_of())
        self.assertFalse(hasattr(g.get_node("A"), "authoritative"))

    def test_complete_lineage_does_not_become_approved(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.STATEMENT, status=LineageCompleteness.COMPLETE))
        self.assertEqual(g.lineage_completeness("A"), LineageCompleteness.COMPLETE)
        self.assertFalse(hasattr(g.get_node("A"), "approved"))
        self.assertFalse(hasattr(g.get_node("A"), "approval_status"))


class R1CompatibilityTests(unittest.TestCase):
    def test_existing_r1_provenance_semantics_remain_valid(self):
        origin = Origin(kind="HUMAN_INPUT", contributor="Technical Lead")
        provenance = Provenance(origin=origin, material_ids=["MAT-1"], evidence_ids=["EVR-1"],
                                 contributor="Technical Lead")
        self.assertTrue(provenance.validate())

        g = ProvenanceGraph()
        g.add_node(_node("MAT-1", NodeKind.MATERIAL, source_type=SourceType.HUMAN_REQUIREMENT, origin=origin))
        g.add_node(_node("EVR-1", NodeKind.EVIDENCE, source_type=SourceType.HUMAN_REQUIREMENT, origin=origin))
        g.add_edge(_edge("PED-1", "MAT-1", "EVR-1", EdgeRelationship.EVIDENCE_FROM))
        self.assertEqual(provenance.material_ids, g.parents_of("EVR-1"))


class R2CompatibilityTests(unittest.TestCase):
    def test_validated_source_input_represented_without_code_when_human_only(self):
        source_input = SourceInput(
            source_type=SourceType.HUMAN_REQUIREMENT,
            content="El descuento deberia ser configurable.",
            origin=Origin(kind="HUMAN_INPUT", contributor="Technical Lead"),
        )
        node = material_node_from_source_input(source_input)
        self.assertEqual(node.node_kind, NodeKind.MATERIAL)
        self.assertEqual(node.source_type, SourceType.HUMAN_REQUIREMENT)
        self.assertIsNone(node.reference)
        node.validate()

    def test_equivalent_source_inputs_produce_equivalent_material_node_ids(self):
        a = SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="Contexto X")
        b = SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="Contexto X")
        self.assertEqual(
            material_node_from_source_input(a).node_id,
            material_node_from_source_input(b).node_id,
        )


class MetadataValidationTests(unittest.TestCase):
    def test_json_compatible_metadata_accepted(self):
        g = ProvenanceGraph()
        node = g.add_node(_node("A", NodeKind.MATERIAL, metadata={"tags": ["a", "b"], "n": 1}))
        self.assertEqual(node.metadata["n"], 1)

    def test_unsupported_metadata_object_rejected(self):
        g = ProvenanceGraph()
        with self.assertRaises(ProvenanceValidationError):
            g.add_node(_node("A", NodeKind.MATERIAL, metadata={"bad": {1, 2}}))


class SecurityTests(unittest.TestCase):
    def test_fake_secret_in_reference_is_sanitized(self):
        g = ProvenanceGraph()
        node = g.add_node(_node("A", NodeKind.MATERIAL, reference="Password=clave123"))
        self.assertNotIn("clave123", node.reference)
        self.assertIn("Password=********", node.reference)

    def test_fake_secret_in_metadata_is_sanitized(self):
        g = ProvenanceGraph()
        node = g.add_node(_node("A", NodeKind.MATERIAL, metadata={"raw": "Password=clave123"}))
        self.assertNotIn("clave123", node.metadata["raw"])

    def test_fake_secret_not_leaked_in_canonical_serialization(self):
        g = ProvenanceGraph()
        g.add_node(_node("A", NodeKind.MATERIAL, reference="Password=clave123"))
        self.assertNotIn("clave123", g.render_canonical_json())

    def test_fake_secret_not_leaked_in_contract_or_example_artifacts(self):
        self.assertNotIn("clave123", render_provenance_contract_json())


class ContractDeterminismTests(unittest.TestCase):
    def test_contract_generation_is_byte_identical_across_runs(self):
        self.assertEqual(render_provenance_contract_json(), render_provenance_contract_json())

    def test_contract_covers_required_keys(self):
        contract = build_provenance_contract()
        for key in ("node_kinds", "edge_relationships", "transformation_types", "completeness_states",
                    "edge_direction", "identity_rules", "cycle_policy", "dangling_reference_policy",
                    "duplicate_policy", "authority_distinction", "approval_distinction",
                    "ai_ancestry_semantics", "r1_provenance_relationship", "r2_input_relationship"):
            self.assertIn(key, contract)


if __name__ == "__main__":
    unittest.main()
