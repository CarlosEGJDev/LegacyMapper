import unittest

from legacy_documenter.knowledge.domain.enums import (
    ApprovalStatus,
    KnowledgeNature,
    KnowledgeStatus,
    SourceType,
    TemporalState,
)
from legacy_documenter.knowledge.domain.models import (
    DomainValidationError,
    EvidenceRef,
    KnowledgeStatement,
    MaterialItem,
    Origin,
    Provenance,
    new_evidence_id,
    new_material_id,
    new_statement_id,
)

TARGET_FAMILIES = [
    ("00 El Area", KnowledgeNature.EXISTING_IMPLEMENTATION),
    ("01 Gobernanza", KnowledgeNature.NORM),
    ("02 Flujos", KnowledgeNature.FLOW),
    ("03 Desarrollo de Software", KnowledgeNature.NORM),
    ("04 Arquitecturas de Referencia", KnowledgeNature.ARCHITECTURE),
    ("05 Plantillas", KnowledgeNature.CATALOG),
    ("06 Catalogo", KnowledgeNature.LEVANTAMIENTO),
    ("07 Proyectos", KnowledgeNature.PROJECT),
    ("08 Historial", KnowledgeNature.RESOLUTION),
    ("09 Capacitacion", KnowledgeNature.TRAINING),
]


class CodeOnlyScenarioTests(unittest.TestCase):
    def test_confirmed_statement_backed_by_code_fact(self):
        origin = Origin(kind="CODE_REPOSITORY", reference="Modulo1.vb")
        evidence = EvidenceRef(
            evidence_id=new_evidence_id("code", "Modulo1.vb", 10),
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            origin=origin,
            locator="Modulo1.vb:10",
            authoritative=True,
        )
        statement = KnowledgeStatement(
            statement_id=new_statement_id("code-only", 1),
            statement="La funcion CalcularTotal existe en Modulo1.vb.",
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            nature=KnowledgeNature.EXISTING_IMPLEMENTATION,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[evidence],
        )
        self.assertTrue(statement.validate())


class CodeAndHumanScenarioTests(unittest.TestCase):
    def test_code_fact_and_human_requirement_coexist_with_independent_provenance(self):
        code_evidence = EvidenceRef(
            evidence_id=new_evidence_id("code", "Modulo1.vb", 42),
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            origin=Origin(kind="CODE_REPOSITORY", reference="Modulo1.vb"),
            locator="Modulo1.vb:42",
            authoritative=True,
        )
        code_statement = KnowledgeStatement(
            statement_id=new_statement_id("mixed", "code"),
            statement="El valor de descuento esta fijo en el codigo.",
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            nature=KnowledgeNature.EXISTING_IMPLEMENTATION,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[code_evidence],
            temporal_state=TemporalState.AS_IS,
            provenance=Provenance(origin=code_evidence.origin, evidence_ids=[code_evidence.evidence_id]),
        )

        human_evidence = EvidenceRef(
            evidence_id=new_evidence_id("human", "requirement", 1),
            source_type=SourceType.HUMAN_REQUIREMENT,
            origin=Origin(kind="HUMAN_INPUT", contributor="Technical Lead"),
            locator="requirement-01",
        )
        human_statement = KnowledgeStatement(
            statement_id=new_statement_id("mixed", "human"),
            statement="El descuento deberia ser configurable.",
            source_type=SourceType.HUMAN_REQUIREMENT,
            nature=KnowledgeNature.REQUIREMENT,
            status=KnowledgeStatus.INTERPRETED,
            evidence_refs=[human_evidence],
            temporal_state=TemporalState.TO_BE,
            provenance=Provenance(origin=human_evidence.origin, evidence_ids=[human_evidence.evidence_id],
                                   contributor="Technical Lead"),
        )

        self.assertTrue(code_statement.validate())
        self.assertTrue(human_statement.validate())
        self.assertNotEqual(code_statement.provenance.origin.kind, human_statement.provenance.origin.kind)
        self.assertEqual(code_statement.provenance.evidence_ids, [code_evidence.evidence_id])
        self.assertEqual(human_statement.provenance.evidence_ids, [human_evidence.evidence_id])


class HumanInformationOnlyScenarioTests(unittest.TestCase):
    def test_valid_knowledge_without_any_code_metadata(self):
        material = MaterialItem(
            material_id=new_material_id("human-only", 1),
            source_type=SourceType.PROJECT_DOCUMENT,
            title="Politica de seguridad",
            content="Todas las contrasenas deben rotarse cada 90 dias.",
            origin=Origin(kind="HUMAN_INPUT", contributor="Technical Lead"),
        )
        self.assertTrue(material.validate())
        self.assertIsNone(material.reference)

        evidence = EvidenceRef(
            evidence_id=new_evidence_id("human-only", "policy"),
            source_type=SourceType.PROJECT_DOCUMENT,
            origin=material.origin,
            locator="Politica de seguridad, parrafo 1",
            authoritative=True,
        )
        statement = KnowledgeStatement(
            statement_id=new_statement_id("human-only", 1),
            statement="Las contrasenas deben rotarse cada 90 dias.",
            source_type=SourceType.PROJECT_DOCUMENT,
            nature=KnowledgeNature.NORM,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[evidence],
            provenance=Provenance(origin=material.origin, material_ids=[material.material_id],
                                   evidence_ids=[evidence.evidence_id], contributor="Technical Lead"),
        )
        self.assertTrue(statement.validate())


class PartialInformationScenarioTests(unittest.TestCase):
    def test_partial_statement_without_inventing_missing_content(self):
        statement = KnowledgeStatement(
            statement_id=new_statement_id("partial", 1),
            statement="El proceso de aprobacion de compras existe, pero su flujo completo no se conoce.",
            source_type=SourceType.UNRESOLVED,
            nature=KnowledgeNature.PROCESS,
            status=KnowledgeStatus.PARTIAL,
        )
        self.assertTrue(statement.validate())
        self.assertEqual(statement.evidence_refs, [])

        unresolved = KnowledgeStatement(
            statement_id=new_statement_id("partial", 2),
            statement="No existe evidencia suficiente sobre el propietario del proceso.",
            source_type=SourceType.UNRESOLVED,
            nature=KnowledgeNature.PROCESS,
            status=KnowledgeStatus.UNRESOLVED,
        )
        self.assertTrue(unresolved.validate())


class AsIsToBeCoexistenceScenarioTests(unittest.TestCase):
    def test_as_is_and_to_be_statements_coexist_without_automatic_conflict(self):
        as_is = KnowledgeStatement(
            statement_id=new_statement_id("temporal", "as-is"),
            statement="El sistema usa un valor de IVA fijo en el codigo.",
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            nature=KnowledgeNature.EXISTING_IMPLEMENTATION,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[EvidenceRef(
                evidence_id=new_evidence_id("temporal", "as-is"),
                source_type=SourceType.DETERMINISTIC_CODE_FACT,
                authoritative=True,
            )],
            temporal_state=TemporalState.AS_IS,
        )
        to_be = KnowledgeStatement(
            statement_id=new_statement_id("temporal", "to-be"),
            statement="El valor de IVA deberia ser configurable.",
            source_type=SourceType.BUSINESS_REQUIREMENT,
            nature=KnowledgeNature.REQUIREMENT,
            status=KnowledgeStatus.INTERPRETED,
            temporal_state=TemporalState.TO_BE,
            related_statement_ids=[as_is.statement_id],
        )
        self.assertTrue(as_is.validate())
        self.assertTrue(to_be.validate())
        self.assertEqual(as_is.temporal_state, TemporalState.AS_IS)
        self.assertEqual(to_be.temporal_state, TemporalState.TO_BE)
        self.assertIn(as_is.statement_id, to_be.related_statement_ids)


class TargetFamilyRepresentationScenarioTests(unittest.TestCase):
    def test_each_target_family_is_representable_without_specialized_classes(self):
        for family_name, nature in TARGET_FAMILIES:
            with self.subTest(family=family_name):
                statement = KnowledgeStatement(
                    statement_id=new_statement_id("family", family_name),
                    statement=f"Conocimiento de ejemplo para la familia {family_name}.",
                    source_type=SourceType.PROJECT_DOCUMENT,
                    nature=nature,
                    status=KnowledgeStatus.INTERPRETED,
                    metadata={"target_family": family_name},
                )
                self.assertTrue(statement.validate())
                self.assertEqual(statement.metadata["target_family"], family_name)
                self.assertIsInstance(statement, KnowledgeStatement)

    def test_no_specialized_family_classes_are_required(self):
        module_names = {type(nature) for _, nature in TARGET_FAMILIES}
        self.assertEqual(module_names, {KnowledgeNature})


class InvalidContractScenarioTests(unittest.TestCase):
    def test_material_without_content_or_reference_is_rejected(self):
        material = MaterialItem(material_id="MAT-1", source_type=SourceType.PROJECT_DOCUMENT)
        with self.assertRaises(DomainValidationError):
            material.validate()

    def test_material_with_empty_id_is_rejected(self):
        material = MaterialItem(material_id=" ", source_type=SourceType.PROJECT_DOCUMENT, content="x")
        with self.assertRaises(DomainValidationError):
            material.validate()

    def test_invalid_source_type_is_rejected(self):
        material = MaterialItem(material_id="MAT-1", source_type="NOT_A_SOURCE_TYPE", content="x")
        with self.assertRaises(DomainValidationError):
            material.validate()

    def test_confirmed_statement_without_authoritative_evidence_is_rejected(self):
        statement = KnowledgeStatement(
            statement_id="KST-1",
            statement="Algo confirmado sin evidencia autoritativa.",
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            nature=KnowledgeNature.EXISTING_IMPLEMENTATION,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[EvidenceRef(evidence_id="EVR-1", source_type=SourceType.DETERMINISTIC_CODE_FACT,
                                        authoritative=False)],
        )
        with self.assertRaises(DomainValidationError):
            statement.validate()

    def test_duplicate_evidence_references_are_rejected(self):
        evidence = EvidenceRef(evidence_id="EVR-1", source_type=SourceType.DETERMINISTIC_CODE_FACT, authoritative=True)
        statement = KnowledgeStatement(
            statement_id="KST-1",
            statement="Duplicado.",
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            nature=KnowledgeNature.EXISTING_IMPLEMENTATION,
            status=KnowledgeStatus.CONFIRMED,
            evidence_refs=[evidence, evidence],
        )
        with self.assertRaises(DomainValidationError):
            statement.validate()

    def test_origin_without_kind_is_rejected(self):
        with self.assertRaises(DomainValidationError):
            Origin(kind="").validate()

    def test_invalid_approval_status_is_rejected(self):
        statement = KnowledgeStatement(
            statement_id="KST-1",
            statement="x",
            source_type=SourceType.UNRESOLVED,
            nature=KnowledgeNature.PROCESS,
            status=KnowledgeStatus.PARTIAL,
        )
        statement.approval.approval_status = "APPROVED"
        with self.assertRaises(DomainValidationError):
            statement.validate()


if __name__ == "__main__":
    unittest.main()
