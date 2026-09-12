import unittest

from legacy_documenter.knowledge.domain.enums import SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import Origin
from legacy_documenter.knowledge.input.catalog import SourceContractCatalog, UnknownSourceTypeError
from legacy_documenter.knowledge.input.contract_report import (
    build_source_contract_report,
    render_source_contract_report_json,
)
from legacy_documenter.knowledge.input.contracts import SourceInput, SourceInputValidationError
from legacy_documenter.knowledge.input.normalization import normalize_source_input, validate_metadata
from legacy_documenter.knowledge.input.validator import validate_source_input


class CatalogCompletenessTests(unittest.TestCase):
    def test_every_source_type_has_exactly_one_policy(self):
        self.assertEqual(set(SourceType), SourceContractCatalog.supported_types())
        self.assertTrue(SourceContractCatalog.assert_complete())

    def test_unknown_source_type_is_rejected(self):
        with self.assertRaises(UnknownSourceTypeError):
            SourceContractCatalog.get("NOT_A_SOURCE_TYPE")


class CodeOnlyTests(unittest.TestCase):
    def test_valid_code_fact_accepted_with_sufficient_traceability(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            reference="Modulo1.vb:10",
            origin=Origin(kind="CODE_REPOSITORY", reference="Modulo1.vb"),
        ))
        self.assertEqual(value.reference, "Modulo1.vb:10")

    def test_code_fact_without_traceability_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.DETERMINISTIC_CODE_FACT, content="algo"))

    def test_code_fact_without_origin_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.DETERMINISTIC_CODE_FACT, reference="Modulo1.vb:1"))


class HumanInformationOnlyTests(unittest.TestCase):
    def _assert_accepted_without_code(self, source_type, **kwargs):
        return validate_source_input(SourceInput(source_type=source_type, **kwargs))

    def test_human_requirement_accepted_with_zero_code_fields(self):
        self._assert_accepted_without_code(SourceType.HUMAN_REQUIREMENT, content="Se requiere X.")

    def test_user_story_accepted_with_zero_code_fields(self):
        self._assert_accepted_without_code(SourceType.USER_STORY, content="Como usuario quiero X.")

    def test_business_requirement_accepted_with_zero_code_fields(self):
        self._assert_accepted_without_code(SourceType.BUSINESS_REQUIREMENT, content="El negocio requiere X.")

    def test_business_context_accepted_with_zero_code_fields(self):
        self._assert_accepted_without_code(SourceType.BUSINESS_CONTEXT, content="Contexto de negocio X.")

    def test_technical_constraint_accepted_with_zero_code_fields(self):
        self._assert_accepted_without_code(SourceType.TECHNICAL_CONSTRAINT, content="Debe correr en Windows Server.")

    def test_corporate_standard_accepted_without_code(self):
        self._assert_accepted_without_code(
            SourceType.CORPORATE_STANDARD, content="Norma ISO X.", reference="ISO-27001")

    def test_approved_decision_accepted_without_code(self):
        self._assert_accepted_without_code(
            SourceType.APPROVED_DECISION, content="Se aprobo usar Postgres.", reference="DEC-001",
            origin=Origin(kind="MEETING_MINUTES", contributor="Comite Arquitectura"))

    def test_external_document_accepted_without_code(self):
        self._assert_accepted_without_code(
            SourceType.EXTERNAL_DOCUMENT, content="Documento externo.", reference="https://example.org/doc")

    def test_project_document_accepted_without_code(self):
        self._assert_accepted_without_code(
            SourceType.PROJECT_DOCUMENT, content="Documento del proyecto.", reference="docs/manual.md")

    def test_unresolved_material_accepted_without_code(self):
        self._assert_accepted_without_code(
            SourceType.UNRESOLVED, content="No se sabe quien es el propietario del proceso.")


class CodeAndHumanInformationTests(unittest.TestCase):
    def test_code_and_human_inputs_coexist_without_contaminating_each_other(self):
        code = validate_source_input(SourceInput(
            source_type=SourceType.DETERMINISTIC_CODE_FACT,
            reference="Modulo1.vb:42",
            origin=Origin(kind="CODE_REPOSITORY", reference="Modulo1.vb"),
        ))
        human = validate_source_input(SourceInput(
            source_type=SourceType.HUMAN_REQUIREMENT,
            content="El descuento deberia ser configurable.",
            origin=Origin(kind="HUMAN_INPUT", contributor="Technical Lead"),
        ))
        self.assertIsNone(human.reference)
        self.assertIsNone(code.content)
        self.assertNotEqual(code.origin.kind, human.origin.kind)


class PartialInformationTests(unittest.TestCase):
    def test_unresolved_material_preserved_without_inventing_classification(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.UNRESOLVED,
            content="El propietario del proceso de aprobacion de compras no esta identificado.",
        ))
        self.assertEqual(value.source_type, SourceType.UNRESOLVED)
        self.assertFalse(value.authoritative)

    def test_unresolved_without_content_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.UNRESOLVED, reference="ticket-123"))


class UserStoryFlexibilityTests(unittest.TestCase):
    def test_free_form_user_story_accepted(self):
        validate_source_input(SourceInput(source_type=SourceType.USER_STORY, content="Como usuario quiero X para Y."))

    def test_structured_actor_goal_benefit_accepted_without_free_form_content(self):
        validate_source_input(SourceInput(
            source_type=SourceType.USER_STORY,
            metadata={"actor": "cliente", "goal": "pagar en linea", "benefit": "ahorrar tiempo"},
        ))

    def test_structured_form_does_not_require_all_three_fields(self):
        validate_source_input(SourceInput(source_type=SourceType.USER_STORY, metadata={"actor": "cliente", "goal": "pagar"}))

    def test_user_story_with_neither_form_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.USER_STORY))


class AuthorityScopeTests(unittest.TestCase):
    def test_human_requirement_authoritative_is_not_proof_of_as_is_implementation(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.HUMAN_REQUIREMENT, content="Se requiere X.", authoritative=True))
        self.assertTrue(value.authoritative)
        self.assertIn("not automatically evidence that the current system implements it", value.authority_scope)
        self.assertIsNone(value.temporal_state)

    def test_corporate_standard_authoritative_does_not_imply_current_compliance(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.CORPORATE_STANDARD, content="Norma X.", reference="STD-1", authoritative=True))
        self.assertIn("not automatically evidence that every existing application complies with it", value.authority_scope)

    def test_ai_interpretation_authoritative_flag_never_auto_derived_from_validity(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.AI_INTERPRETATION, content="Interpretacion generada.",
            metadata={"model": "fixture-model"},
        ))
        self.assertFalse(value.authoritative)

    def test_ai_interpretation_can_declare_authority_but_scope_stays_narrow(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.AI_INTERPRETATION, content="Interpretacion generada.",
            metadata={"model": "fixture-model"}, authoritative=True,
        ))
        self.assertIn("never becomes authoritative merely by being structurally valid", value.authority_scope)

    def test_unresolved_cannot_be_marked_authoritative(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(
                source_type=SourceType.UNRESOLVED, content="Sin resolver.", authoritative=True))

    def test_caller_supplied_authority_scope_is_not_overwritten(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.HUMAN_REQUIREMENT, content="Se requiere X.",
            authoritative=True, authority_scope="Custom scope text.",
        ))
        self.assertEqual(value.authority_scope, "Custom scope text.")


class TemporalStateTests(unittest.TestCase):
    def test_valid_closed_enum_accepted(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.BUSINESS_REQUIREMENT, content="X", temporal_state=TemporalState.TO_BE))
        self.assertEqual(value.temporal_state, TemporalState.TO_BE)

    def test_unknown_temporal_state_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(
                source_type=SourceType.BUSINESS_REQUIREMENT, content="X", temporal_state="SOMEDAY"))

    def test_missing_temporal_state_accepted_when_policy_permits_it(self):
        value = validate_source_input(SourceInput(source_type=SourceType.BUSINESS_REQUIREMENT, content="X"))
        self.assertIsNone(value.temporal_state)

    def test_as_is_never_inferred_from_deterministic_code_fact(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.DETERMINISTIC_CODE_FACT, reference="M.vb:1",
            origin=Origin(kind="CODE_REPOSITORY"),
        ))
        self.assertIsNone(value.temporal_state)

    def test_to_be_never_inferred_merely_because_something_is_a_requirement(self):
        value = validate_source_input(SourceInput(source_type=SourceType.HUMAN_REQUIREMENT, content="Se requiere X."))
        self.assertIsNone(value.temporal_state)


class SanitizationTests(unittest.TestCase):
    def test_secret_like_content_is_redacted_not_leaked(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.PROJECT_DOCUMENT,
            content="La cadena es Password=clave123",
            reference="docs/config.md",
        ))
        self.assertNotIn("clave123", value.content)
        self.assertIn("Password=********", value.content)

    def test_secret_like_metadata_value_is_redacted(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.PROJECT_DOCUMENT,
            content="Config note.", reference="docs/config.md", metadata={"raw": "Password=clave123"},
        ))
        self.assertNotIn("clave123", value.metadata["raw"])

    def test_validation_error_message_never_contains_raw_secret(self):
        try:
            validate_source_input(SourceInput(source_type=SourceType.UNRESOLVED, reference="Password=clave123"))
        except SourceInputValidationError as exc:
            self.assertNotIn("clave123", str(exc))


class ReferencesTests(unittest.TestCase):
    def test_non_filesystem_reference_accepted(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.EXTERNAL_DOCUMENT,
            content="Ticket de negocio.",
            reference="JIRA-4821",
        ))
        self.assertEqual(value.reference, "JIRA-4821")


class MetadataTests(unittest.TestCase):
    def test_json_compatible_nested_metadata_accepted(self):
        value = validate_source_input(SourceInput(
            source_type=SourceType.BUSINESS_CONTEXT, content="Contexto.",
            metadata={"tags": ["a", "b"], "nested": {"k": 1, "v": None, "flag": True}},
        ))
        self.assertEqual(value.metadata["nested"]["k"], 1)

    def test_unsupported_metadata_object_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_metadata({"bad": {1, 2, 3}})

    def test_non_dict_metadata_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_metadata(["not", "a", "dict"])


class NormalizationTests(unittest.TestCase):
    def test_whitespace_normalized_deterministically(self):
        value = normalize_source_input(SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="  hola  "))
        self.assertEqual(value.content, "hola")

    def test_whitespace_only_becomes_none(self):
        value = normalize_source_input(SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="   "))
        self.assertIsNone(value.content)

    def test_normalization_is_idempotent(self):
        raw = SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="  hola  ", title="  T  ")
        once = normalize_source_input(raw)
        twice = normalize_source_input(once)
        self.assertEqual(once.content, twice.content)
        self.assertEqual(once.title, twice.title)
        self.assertEqual(once.metadata, twice.metadata)


class EmptyMaterialTests(unittest.TestCase):
    def test_empty_content_and_reference_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.BUSINESS_CONTEXT))

    def test_whitespace_only_content_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.BUSINESS_CONTEXT, content="   "))

    def test_whitespace_only_reference_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.BUSINESS_CONTEXT, reference="   "))


class ApprovedDecisionIdentityTests(unittest.TestCase):
    def test_decision_without_identity_or_authority_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(source_type=SourceType.APPROVED_DECISION, content="Se aprobo algo."))

    def test_decision_without_fabricated_approver_is_rejected(self):
        with self.assertRaises(SourceInputValidationError):
            validate_source_input(SourceInput(
                source_type=SourceType.APPROVED_DECISION, content="Se aprobo algo.", reference="DEC-002"))


class ContractArtifactDeterminismTests(unittest.TestCase):
    def test_report_generation_is_byte_identical_across_runs(self):
        first = render_source_contract_report_json()
        second = render_source_contract_report_json()
        self.assertEqual(first, second)

    def test_report_covers_all_twelve_source_types(self):
        report = build_source_contract_report()
        self.assertEqual(len(report["source_types"]), 12)
        self.assertEqual(
            {entry["source_type"] for entry in report["source_types"]},
            {st.value for st in SourceType},
        )


if __name__ == "__main__":
    unittest.main()
