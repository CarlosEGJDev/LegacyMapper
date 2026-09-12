import inspect
import json
from pathlib import Path
import unittest

from legacy_documenter.context.composer import ContextComposer
from legacy_documenter.context.resolver import ContextResolver
from legacy_documenter.knowledge.readiness import run
from legacy_documenter.llm import LLMProvider, ProviderRegistry
from legacy_documenter.quality.maintainability_audit import audit

ROOT = Path(__file__).parents[1]


class ComprehensiveMaintainabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = json.loads((ROOT / "output/v3_r10_1/MAINTAINABILITY_AUDIT_BEFORE.json").read_text(encoding="utf-8"))
        cls.after = json.loads((ROOT / "output/v3_r10_1/MAINTAINABILITY_AUDIT_AFTER.json").read_text(encoding="utf-8"))
        cls.mapping = json.loads((ROOT / "output/v3_r10_1/REFACTORING_MAP.json").read_text(encoding="utf-8"))
        cls.debt = json.loads((ROOT / "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json").read_text(encoding="utf-8"))

    def test_docstring_coverage_substantially_improved(self): self.assertGreater(self.after["summary"]["docstring_coverage_percent"], self.before["summary"]["docstring_coverage_percent"] + 40)
    def test_type_coverage_substantially_improved(self): self.assertGreater(self.after["summary"]["typing_coverage_percent"], self.before["summary"]["typing_coverage_percent"] + 8)
    def test_significant_symbols_are_reported(self): self.assertGreater(self.after["summary"]["significant_symbols"], 0)
    def test_significant_documentation_is_high(self): self.assertGreaterEqual(self.after["summary"]["significant_docstring_coverage_percent"], 80)
    def test_all_batches_are_recorded(self): self.assertEqual(self.mapping["batches"], [f"BATCH_{number}" for number in range(1,8)])
    def test_no_behavior_change_recorded(self): self.assertTrue(all(not item["behavior_change"] for item in self.mapping["changes"]))
    def test_debt_has_explicit_reasons_and_plans(self): self.assertTrue(all(item["reason"] and item["plan"] for item in self.debt["items"]))
    def test_context_boundaries_are_typed(self): self.assertNotEqual(inspect.signature(ContextComposer.compose).return_annotation, inspect.Signature.empty)
    def test_provider_boundary_is_typed(self): self.assertNotEqual(inspect.signature(LLMProvider.generate).return_annotation, inspect.Signature.empty)
    def test_registry_is_documented(self): self.assertTrue(inspect.getdoc(ProviderRegistry))
    def test_r9_remains_ready(self): self.assertEqual(run(ROOT)["readiness"], "READY")
    def test_audit_repeatability(self): self.assertEqual(audit(ROOT), audit(ROOT))


if __name__ == "__main__": unittest.main()
