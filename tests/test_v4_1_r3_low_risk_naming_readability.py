"""V4.1-R3 -- Naming Pass Part 1 (Low-Risk Renames) verification.

Covers the two safe renames actually implemented this round, both recorded
in output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json's naming_candidates
and confirmed against DEBT-003 in known_debt:

1. The generic `requests` batch-service parameters renamed to
   request-kind-specific names (`classification_requests` /
   `proposal_requests` / `relation_requests`) in `classify_batch`,
   `create_proposal_batch`, and `create_relation_batch`. Repository-wide
   grep confirmed every caller (production and tests) is positional, so
   DIRECT_RENAME_SAFE was used -- no compatibility shim needed.

2. `legacy_documenter.quality.maintainability_audit.audit` kept exactly
   as-is, with a new, clearer `build_maintainability_inventory` alias added
   (delegates to `audit`, identical return value).

No production behavior changes: only parameter/symbol names moved.
"""
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path

from legacy_documenter.knowledge.classification.enums import ClassificationMethod, ClassificationStatus
from legacy_documenter.knowledge.classification.service import (
    ClassificationRejectedError,
    ClassificationRequest,
    KnowledgeClassificationService,
)
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, SourceType
from legacy_documenter.knowledge.domain.models import MaterialItem, new_material_id
from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod
from legacy_documenter.knowledge.proposals.service import ProposalRejectedError, ProposalRequest, ProposalService
from legacy_documenter.knowledge.relations.enums import RelationKind
from legacy_documenter.knowledge.relations.service import RelationRejectedError, RelationRequest, RelationService
from legacy_documenter.quality.maintainability_audit import audit, build_maintainability_inventory, write_audit

REPO_ROOT = Path(__file__).resolve().parents[1]

HIGH_RISK_MODULES = [
    "legacy_documenter/extractors/database_extractor.py",
    "legacy_documenter/analysis/flow_resolver.py",
    "legacy_documenter/knowledge/readiness.py",
    "legacy_documenter/documentation/resume.py",
    "legacy_documenter/analysis/deep_source.py",
]


def _material(suffix: str) -> MaterialItem:
    return MaterialItem(
        material_id=new_material_id(SourceType.PROJECT_DOCUMENT.value, suffix),
        source_type=SourceType.PROJECT_DOCUMENT,
        content="contenido de prueba " + suffix,
    )


class BatchParameterRenameSignatureTests(unittest.TestCase):
    """The three batch methods now expose request-kind-specific parameter names."""

    def test_classify_batch_parameter_renamed(self):
        params = list(inspect.signature(KnowledgeClassificationService.classify_batch).parameters)
        self.assertEqual(params, ["self", "classification_requests"])

    def test_create_proposal_batch_parameter_renamed(self):
        params = list(inspect.signature(ProposalService.create_proposal_batch).parameters)
        self.assertEqual(params, ["self", "proposal_requests"])

    def test_create_relation_batch_parameter_renamed(self):
        params = list(inspect.signature(RelationService.create_relation_batch).parameters)
        self.assertEqual(params, ["self", "relation_requests"])


class BatchParameterPositionalCompatibilityTests(unittest.TestCase):
    """Positional calling style -- the only style used anywhere in the repository
    per the pre-implementation grep -- must be unaffected by the rename."""

    def test_classify_batch_positional_call_unchanged(self):
        service = KnowledgeClassificationService()
        m1, m2 = _material("r3-c1"), _material("r3-c2")
        result = service.classify_batch([
            ClassificationRequest(material=m1, selected_nature=KnowledgeNature.NORM),
            ClassificationRequest(material=m2),
        ])
        self.assertEqual(result.accepted_count, 2)
        self.assertEqual(result.rejected_count, 0)
        self.assertEqual(result.accepted[0].status, ClassificationStatus.CLASSIFIED)
        self.assertEqual(result.accepted[0].classification_method, ClassificationMethod.EXPLICIT)

    def test_create_proposal_batch_positional_call_unchanged(self):
        service = ProposalService()
        request = ProposalRequest(
            proposal_kind=ProposalKind.INTERPRETATION, statement="interpretacion de prueba r3",
            proposal_method=ProposalMethod.HUMAN_PROPOSED, material_ids=("mat-r3-1",),
        )
        result = service.create_proposal_batch([request])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 0)

    def test_create_relation_batch_positional_call_unchanged(self):
        service = RelationService()
        request = RelationRequest(relation_kind=RelationKind.CONFLICT, material_a="mat-r3-a", material_b="mat-r3-b")
        result = service.create_relation_batch([request])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 0)

    def test_keyword_calls_by_new_name_also_work(self):
        # The new parameter names are supported as keyword arguments too --
        # this is new capability, not a compatibility requirement (no
        # caller ever used the old `requests=` keyword form; grep confirmed
        # zero repository-wide `requests=` call sites for these methods).
        service = KnowledgeClassificationService()
        m = _material("r3-kw")
        result = service.classify_batch(classification_requests=[ClassificationRequest(material=m)])
        self.assertEqual(result.accepted_count, 1)


class BatchOutputEquivalenceTests(unittest.TestCase):
    """Batch outputs (ordering, isolation-of-failures policy, deterministic
    ids) must be byte/value-identical to pre-rename behavior."""

    def test_classification_batch_order_and_isolation_preserved(self):
        service = KnowledgeClassificationService()
        m1, m2 = _material("r3-order-1"), _material("r3-order-2")
        result = service.classify_batch([
            ClassificationRequest(material=m1, selected_nature=KnowledgeNature.NORM),
            ClassificationRequest(material=m2, candidate_natures=[KnowledgeNature.PROCESS]),  # invalid: single candidate
        ])
        self.assertEqual(result.accepted_count, 1)
        self.assertEqual(result.rejected_count, 1)
        self.assertEqual(result.rejected[0].index, 1)

    def test_proposal_batch_duplicate_policy_preserved(self):
        service = ProposalService()
        request = ProposalRequest(
            proposal_kind=ProposalKind.INTERPRETATION, statement="duplicado r3",
            proposal_method=ProposalMethod.HUMAN_PROPOSED, material_ids=("mat-r3-dup",),
        )
        result = service.create_proposal_batch([request, request])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 0)  # exact duplicate: idempotent no-op

    def test_relation_batch_duplicate_policy_preserved(self):
        service = RelationService()
        request = RelationRequest(relation_kind=RelationKind.CONFLICT, material_a="mat-r3-x", material_b="mat-r3-y")
        result = service.create_relation_batch([request, request])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 0)

    def test_deterministic_ids_unchanged_across_two_invocations(self):
        service = ProposalService()
        request = ProposalRequest(
            proposal_kind=ProposalKind.RESOLUTION, statement="misma propuesta r3",
            proposal_method=ProposalMethod.HUMAN_PROPOSED, material_ids=("mat-r3-det",),
        )
        first = service.create_proposal_batch([request])
        second = service.create_proposal_batch([request])
        self.assertEqual(first.accepted[0].proposal_id, second.accepted[0].proposal_id)


class BatchExceptionBehaviorTests(unittest.TestCase):
    """Non-batch single-item methods raise the same exception types for the
    same invalid input as before the rename (they were not renamed, but
    are exercised here as the underlying behavior the batch methods wrap)."""

    def test_classify_rejects_invalid_request_same_as_before(self):
        service = KnowledgeClassificationService()
        with self.assertRaises(ClassificationRejectedError):
            service.classify(ClassificationRequest(
                material=_material("r3-exc-1"),
                selected_nature=KnowledgeNature.NORM,
                candidate_natures=[KnowledgeNature.PROCESS, KnowledgeNature.FLOW],
            ))

    def test_create_proposal_rejects_blank_statement_same_as_before(self):
        service = ProposalService()
        with self.assertRaises(ProposalRejectedError):
            service.create_proposal(ProposalRequest(
                proposal_kind=ProposalKind.INTERPRETATION, statement="   ",
                proposal_method=ProposalMethod.HUMAN_PROPOSED, material_ids=("mat-r3-exc",),
            ))

    def test_create_relation_rejects_self_relation_same_as_before(self):
        service = RelationService()
        with self.assertRaises(RelationRejectedError):
            service.create_relation(RelationRequest(
                relation_kind=RelationKind.CONFLICT, material_a="same", material_b="same",
            ))


class MaintainabilityAuditAliasTests(unittest.TestCase):
    """`audit` is preserved exactly; `build_maintainability_inventory` is a
    new, purely additive alias with identical behavior."""

    def test_old_audit_import_still_valid(self):
        from legacy_documenter.quality.maintainability_audit import audit as reimported_audit
        self.assertIs(reimported_audit, audit)

    def test_write_audit_still_importable_and_unbroken(self):
        from legacy_documenter.quality.maintainability_audit import write_audit as reimported_write_audit
        self.assertIs(reimported_write_audit, write_audit)

    def test_new_alias_resolves_and_matches_audit_exactly(self):
        self.assertEqual(build_maintainability_inventory(REPO_ROOT), audit(REPO_ROOT))

    def test_new_alias_is_repeatable_like_audit(self):
        self.assertEqual(build_maintainability_inventory(REPO_ROOT), build_maintainability_inventory(REPO_ROOT))

    def test_new_alias_accepts_default_workspace_argument(self):
        # audit()/build_maintainability_inventory() both default workspace to ".";
        # calling with no argument must not raise.
        build_maintainability_inventory()


class HighRiskModulesUntouchedTests(unittest.TestCase):
    """Confirm this round did not modify any of the five high-risk modules
    R0/R2 already fenced off (R3 is not their round)."""

    def test_high_risk_modules_not_in_working_tree_diff(self):
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=False,
        )
        changed = set(result.stdout.splitlines())
        for module in HIGH_RISK_MODULES:
            self.assertNotIn(module, changed, f"{module} must not be modified in V4.1-R3")


class SerializationUnchangedTests(unittest.TestCase):
    """Parameter renames must not affect any JSON-serialized contract shape."""

    def test_proposal_batch_result_serialization_unaffected(self):
        service = ProposalService()
        request = ProposalRequest(
            proposal_kind=ProposalKind.SELECTION, statement="serializacion r3",
            proposal_method=ProposalMethod.HUMAN_PROPOSED, material_ids=("mat-r3-ser",),
        )
        result = service.create_proposal_batch([request])
        proposal = result.accepted[0]
        # Field names on the returned domain object are untouched by the
        # parameter rename (parameter names are not part of any contract).
        self.assertTrue(hasattr(proposal, "proposal_id"))
        self.assertTrue(hasattr(proposal, "statement"))


class ReadinessAndProviderCallsTests(unittest.TestCase):
    def test_readiness_ready_and_no_provider_or_llm_calls(self):
        from legacy_documenter.knowledge.readiness import run
        result = run(REPO_ROOT)
        self.assertEqual(result["readiness"], "READY")
        self.assertEqual(result.get("provider_calls", 0), 0)
        self.assertEqual(result.get("real_llm_calls", 0), 0)


class V4ContractsUnchangedTests(unittest.TestCase):
    def test_plugin_contract_name_and_version_unchanged(self):
        text = (REPO_ROOT / "docs" / "V4" / "V4_FINAL_CLOSURE_RESULT.md").read_text(encoding="utf-8")
        self.assertIn("LegacyMapperPluginKnowledge", text)

    def test_no_cross_import_between_projection_and_plugin_projection(self):
        projection_src = (REPO_ROOT / "legacy_documenter/knowledge/projection/service.py").read_text(encoding="utf-8")
        plugin_projection_src = (
            REPO_ROOT / "legacy_documenter/knowledge/plugin_projection/service.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("plugin_projection", projection_src)
        self.assertNotIn("from legacy_documenter.knowledge.projection", plugin_projection_src)
        self.assertNotIn("import legacy_documenter.knowledge.projection", plugin_projection_src)


class NamingCompatibilityArtifactTests(unittest.TestCase):
    def test_naming_compatibility_artifact_exists_and_is_deterministic_json(self):
        path = REPO_ROOT / "output" / "v4_1_r3" / "V4_1_R3_NAMING_COMPATIBILITY.json"
        self.assertTrue(path.exists(), "V4_1_R3_NAMING_COMPATIBILITY.json must be generated")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("round"), "V4.1-R3")
        self.assertEqual(payload.get("production_behavior_changed"), False)

    def test_naming_compatibility_artifact_has_no_provider_or_llm_language(self):
        path = REPO_ROOT / "output" / "v4_1_r3" / "V4_1_R3_NAMING_COMPATIBILITY.json"
        text = path.read_text(encoding="utf-8").lower()
        self.assertNotIn("real llm call is allowed", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)


if __name__ == "__main__":
    unittest.main()
