import json
from pathlib import Path
import unittest

from legacy_documenter.knowledge.readiness import KnowledgeReadinessService, run
from legacy_documenter.quality.maintainability_audit import audit

ROOT = Path(__file__).parents[1]


class EngineeringQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audit(ROOT)
        cls.standard = (ROOT / "docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md").read_text(encoding="utf-8")
        cls.user = (ROOT / "docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md").read_text(encoding="utf-8")
        cls.technical = (ROOT / "docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md").read_text(encoding="utf-8")

    def test_service_entry_point_preserves_ready(self): self.assertEqual(KnowledgeReadinessService(ROOT).validate()["readiness"], "READY")
    def test_compatibility_wrapper_preserves_ready(self): self.assertEqual(run(ROOT)["readiness"], "READY")
    def test_audit_is_deterministic(self): self.assertEqual(self.audit, audit(ROOT))
    def test_audit_inventory_is_nonempty(self): self.assertGreater(self.audit["python_files"], 0)
    def test_audit_has_coverage_indicators(self): self.assertIn("typing_coverage_percent", self.audit["summary"])
    def test_python_first_standard(self): self.assertIn("prevalecen las buenas prácticas de Python", self.standard)
    def test_standard_preserves_llm_boundary(self): self.assertIn("Python descubre", self.standard)
    def test_user_manual_documents_real_discovery_command(self): self.assertIn("python -m legacy_documenter.main", self.user)
    def test_user_manual_does_not_claim_knowledge_generated(self): self.assertIn("AI_KNOWLEDGE_GENERATED", self.user)
    def test_technical_manual_documents_service(self): self.assertIn("KnowledgeReadinessService", self.technical)
    def test_technical_manual_distinguishes_architectures(self): self.assertIn("Dos arquitecturas distintas", self.technical)
    def test_manuals_do_not_contain_example_secret(self): self.assertNotIn("Password=", self.user + self.technical)


if __name__ == "__main__": unittest.main()
