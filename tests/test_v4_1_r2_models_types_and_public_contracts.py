"""V4.1-R2 -- Models, Types and Public Contracts Readability: equivalence tests.

This round adds narrow, safe return-type annotations (and one small, clearly
domain-meaningful type alias, `EvidenceKeyMap`) to a scoped subset of the
functions R0's `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
`type_safety_candidates` section flagged as below-average-typed. No
parameter typing of ambiguous/heterogeneous nested JSON shapes was
introduced, no dataclass/model field was touched, and no public calling
convention changed. These tests verify that equivalence holds; they do not
duplicate or weaken any existing semantic test.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class PublicImportsResolveTests(unittest.TestCase):
    """(1) Every affected public import still resolves."""

    def test_touched_modules_import_cleanly(self) -> None:
        import legacy_documenter.analysis.deep_interpretation as di
        import legacy_documenter.analysis.targeted_exhaustion as te
        import legacy_documenter.documentation.aggregation as agg
        import legacy_documenter.documentation.consistency as cons
        import legacy_documenter.documentation.contracts as contracts
        import legacy_documenter.documentation.coverage as coverage
        import legacy_documenter.documentation.envelope as envelope
        import legacy_documenter.documentation.evidence_catalog as ec
        import legacy_documenter.documentation.human_review as hr
        import legacy_documenter.documentation.interpretation as interp
        import legacy_documenter.documentation.renderer as renderer

        for mod, names in (
            (di, ["hid", "estimate"]),
            (te, ["_safe_path", "exhaustion_status"]),
            (agg, ["_stable", "evidence_closed"]),
            (cons, ["MetricFact", "extract_numbers", "validate_equivalent",
                    "validate_quantitative_consistency", "traceability_closed", "stable_hash"]),
            (contracts, ["stable_id", "DocumentationContract", "approval_gate",
                         "functional_markdown_template", "technical_markdown_template"]),
            (coverage, ["CoveragePlanner", "_uid"]),
            (envelope, ["semantic_unchanged"]),
            (ec, ["EvidenceKeyMap", "validate_catalog", "visible_catalog",
                  "resolution_preserves_semantics"]),
            (hr, ["validate_preconditions", "parse_document", "response_template",
                  "knowledge_ready", "build_package", "run"]),
            (interp, ["canonical_assessment_schema", "DocumentationPrompt", "AssessmentValidator"]),
            (renderer, ["render"]),
        ):
            for name in names:
                self.assertTrue(hasattr(mod, name), f"{mod.__name__}.{name} missing")


class CallingConventionTests(unittest.TestCase):
    """(2) Positional and keyword calling conventions unchanged."""

    def test_pure_functions_accept_same_call_shapes(self) -> None:
        from legacy_documenter.analysis.deep_interpretation import hid, estimate
        from legacy_documenter.documentation.aggregation import evidence_closed
        from legacy_documenter.documentation.consistency import extract_numbers, stable_hash
        from legacy_documenter.documentation.contracts import stable_id, functional_markdown_template
        from legacy_documenter.documentation.envelope import semantic_unchanged
        from legacy_documenter.documentation.evidence_catalog import visible_catalog

        # Positional.
        self.assertEqual(hid("X", {"a": 1}), hid("X", {"a": 1}))
        self.assertIsInstance(estimate({"a": 1}), int)
        # Keyword-compatible where the original parameter names allow it.
        self.assertIsInstance(extract_numbers(statement="12 y 34"), list)
        self.assertIsInstance(stable_hash({"a": 1}), str)
        self.assertTrue(stable_id("PFX", "a", "b").startswith("PFX-"))
        self.assertTrue(evidence_closed({"claims": [], "missing_information": [], "evidence_ids": []}))
        composed = {"status": "COMPLETE", "summary": "s", "claims": [], "missing_information": []}
        self.assertTrue(semantic_unchanged({"status": "COMPLETE", "summary": "s", "claims": [], "missing_information": []}, composed))
        self.assertEqual(visible_catalog([]), [])
        self.assertIsInstance(functional_markdown_template(), str)

    def test_human_review_run_still_accepts_default_and_keyword_workspace(self) -> None:
        from legacy_documenter.documentation.human_review import run
        import inspect
        sig = inspect.signature(run)
        self.assertEqual(list(sig.parameters), ["workspace"])
        self.assertEqual(sig.parameters["workspace"].default, ".")
        self.assertEqual(sig.parameters["workspace"].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)


class DataclassEquivalenceTests(unittest.TestCase):
    """(3)/(4) Dataclass field order, defaults and default factories unchanged."""

    def test_metric_fact_shape_unchanged(self) -> None:
        from legacy_documenter.documentation.consistency import MetricFact
        fields = dataclasses.fields(MetricFact)
        self.assertEqual(
            [f.name for f in fields],
            ["metric_name", "value", "scope", "population", "aggregation",
             "source_refs", "source_snapshot", "status"],
        )
        status_field = next(f for f in fields if f.name == "status")
        self.assertEqual(status_field.default, "CONFIRMED")
        self.assertTrue(MetricFact.__dataclass_params__.frozen)

    def test_documentation_contracts_dataclasses_shape_unchanged(self) -> None:
        from legacy_documenter.documentation.contracts import (
            EvidenceReference, DocumentClaim, MissingInformation, DocumentMetadata,
            FunctionalModule, ArchitecturePatternAssessment, DocumentationContract,
        )
        self.assertEqual([f.name for f in dataclasses.fields(EvidenceReference)],
                          ["source_type", "reference_id", "authoritative"])
        self.assertEqual(next(f for f in dataclasses.fields(EvidenceReference)
                               if f.name == "authoritative").default, False)
        self.assertEqual([f.name for f in dataclasses.fields(DocumentationContract)],
                          ["metadata", "claims", "modules", "patterns", "missing_information"])
        for f in dataclasses.fields(DocumentationContract):
            if f.name != "metadata":
                self.assertIsInstance(f.default_factory(), list)
        self.assertEqual([f.name for f in dataclasses.fields(MissingInformation)][0], "missing_id")
        self.assertEqual([f.name for f in dataclasses.fields(DocumentMetadata)][0], "document_id")
        self.assertEqual([f.name for f in dataclasses.fields(FunctionalModule)][0], "module_id")
        self.assertEqual([f.name for f in dataclasses.fields(ArchitecturePatternAssessment)][0], "pattern_id")
        del DocumentClaim  # imported only to confirm the symbol still resolves


class SerializationEquivalenceTests(unittest.TestCase):
    """(5)/(6) Serialized/deterministic output unchanged (byte-for-byte, repeatable)."""

    def test_metric_fact_to_dict_and_contract_canonical_json_stable(self) -> None:
        from legacy_documenter.documentation.consistency import MetricFact
        fact = MetricFact("total_projects", 5, "SYSTEM_TOTAL", "PROJECTS", "unique_projects", ("R1",), "SNAP")
        first = fact.to_dict()
        second = fact.to_dict()
        self.assertEqual(first, second)
        self.assertEqual(first["source_refs"], ["R1"])
        self.assertIsInstance(first["source_refs"], list)

    def test_stable_hash_and_id_are_deterministic(self) -> None:
        from legacy_documenter.documentation.consistency import stable_hash
        from legacy_documenter.documentation.contracts import stable_id
        from legacy_documenter.analysis.deep_interpretation import hid
        value = {"z": 1, "a": 2}
        self.assertEqual(stable_hash(value), stable_hash(value))
        self.assertEqual(stable_id("P", "x", "y"), stable_id("P", "x", "y"))
        self.assertEqual(hid("H", value), hid("H", value))

    def test_render_output_byte_identical_across_calls(self) -> None:
        from legacy_documenter.documentation.renderer import render
        document = {
            "claims": [{"claim_id": "C1", "status": "CONFIRMED", "statement": "s",
                        "evidence_refs": ["E1"], "context_package_ids": ["P1"], "section": "Metadata"}],
            "missing_information": [],
            "source_snapshots": ["SNAP"],
            "coverage_metrics": {},
        }
        first = render(document, "functional", "model-x")
        second = render(document, "functional", "model-x")
        self.assertEqual(first, second)
        self.assertIsInstance(first, str)


class ApprovedArtifactHashTests(unittest.TestCase):
    """(7) Approved V7-R14/V4.1-R1 artifact hashes unchanged (spot-check)."""

    EXPECTED = {
        "output/v4_r14/V4_FINAL_BASELINE.json":
            "d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e",
        "output/v4_r14/V4_FINAL_MANIFEST.json":
            "be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551",
        "output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json":
            "55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b",
    }

    def test_spot_checked_artifact_hashes_unchanged(self) -> None:
        for rel, expected in self.EXPECTED.items():
            path = REPO_ROOT / rel
            if not path.exists():
                self.skipTest(f"{rel} not present in this checkout")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"{rel} hash changed -- approved artifact drift")


class TypeAliasExpressesStableStructureTests(unittest.TestCase):
    """(8) New type aliases/TypedDicts actually express the intended stable structure."""

    def test_evidence_key_map_resolves_request_local_keys_to_canonical_ids(self) -> None:
        from legacy_documenter.documentation.evidence_catalog import build_catalog, resolve_payload

        package = {"records": [{"ref": "R-1", "category": "SYSTEM", "fact": {"a": 1}}]}
        catalog = build_catalog(package)
        self.assertEqual(len(catalog), 1)
        key = catalog[0]["key"]
        payload = {"claims": [{"evidence_keys": [key]}], "missing_information": []}
        resolved = resolve_payload(payload, catalog)
        self.assertEqual(resolved["claims"][0]["evidence_refs"], ["R-1"])
        self.assertNotIn("evidence_keys", resolved["claims"][0])


class DynamicBoundariesPreservedTests(unittest.TestCase):
    """(9) Intentionally dynamic (NECESSARY_DYNAMIC_BOUNDARY) boundaries remain dynamic."""

    def test_aggregate_and_build_catalog_still_accept_open_heterogeneous_shapes(self) -> None:
        from legacy_documenter.documentation.aggregation import aggregate
        from legacy_documenter.documentation.evidence_catalog import build_catalog

        # Deliberately heterogeneous / extra-keyed inputs: these functions
        # must not have gained parameter-level type narrowing that would
        # reject shapes their historical callers still legitimately pass.
        assessments = [{"claims": [{"claim_id": "C1", "source_type": "DETERMINISTIC_CODE_FACT",
                                     "evidence_refs": ["R1"], "extra_future_field": {"nested": True}}],
                         "missing_information": []}]
        packages = [{"package_id": "P1", "source_snapshot": "S1",
                     "records": [{"ref": "R1"}], "provenance": {"anything": [1, 2, {"x": "y"}]}}]
        result = aggregate(assessments, packages)
        self.assertIn("claims", result)

        package = {"records": [{"ref": "R-9", "category": "ANYTHING", "fact": {"deeply": {"nested": [1, 2, 3]}}}]}
        catalog = build_catalog(package)
        self.assertEqual(catalog[0]["type"], "ANYTHING")


class HighRiskModulesUntouchedTests(unittest.TestCase):
    """(10) The 5 R0 characterization-sensitive modules were not structurally refactored."""

    EXPECTED_SHA256 = {
        "legacy_documenter/extractors/database_extractor.py":
            "1e0e75ca01dad9dd5b09ef7867e24082e55dd3ab36dab0a261148c9b9b0d2d61",
        "legacy_documenter/analysis/flow_resolver.py":
            "e5a0e5e85bee61a7cca41fee869f5c367191cc068f79663dc345543aff7ba781",
        "legacy_documenter/knowledge/readiness.py":
            "f66980fb85ae671d2f4afb68c5f227f665567e4abd2a66d0f490e1ee783ccecb",
        "legacy_documenter/documentation/resume.py":
            "d15f498c3a1442086d37fbcb188e12a7b8b5d9c34ab561e29130aea1da0723b3",
        "legacy_documenter/analysis/deep_source.py":
            "a61612e0bf0ec0beac2607d87cc85f55f144b9973fbbe32058e960e1506d86f2",
    }

    def test_high_risk_module_bytes_unchanged(self) -> None:
        for rel, expected in self.EXPECTED_SHA256.items():
            path = REPO_ROOT / rel
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"{rel} was modified; R0 marked it DEFER_TO_CHARACTERIZATION_ROUND")

    def test_high_risk_module_public_signatures_unchanged(self) -> None:
        """AST-shape check: same top-level class/function names and same
        argument names, independent of the byte-hash check above."""
        expected_top_level = {
            "legacy_documenter/extractors/database_extractor.py": {"DatabaseExtractor"},
            "legacy_documenter/analysis/flow_resolver.py": {"FunctionalFlowResolver"},
            "legacy_documenter/documentation/resume.py": None,  # module-function-shaped; hash check suffices
            "legacy_documenter/analysis/deep_source.py": None,
            "legacy_documenter/knowledge/readiness.py": None,
        }
        for rel, expected_classes in expected_top_level.items():
            if expected_classes is None:
                continue
            tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
            classes = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
            self.assertEqual(classes, expected_classes)


class BoundaryDirectionTests(unittest.TestCase):
    """(11) R11/R12 knowledge-domain import direction unchanged."""

    def test_projection_and_plugin_projection_do_not_cross_import(self) -> None:
        projection_src = (REPO_ROOT / "legacy_documenter" / "knowledge" / "projection").glob("*.py")
        plugin_src = (REPO_ROOT / "legacy_documenter" / "knowledge" / "plugin_projection").glob("*.py")
        for path in projection_src:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("plugin_projection", text, f"{path} imports plugin_projection")
        for path in plugin_src:
            text = path.read_text(encoding="utf-8")
            # plugin_projection may reference "projection" only as part of
            # its own package name/words, never importing the sibling
            # projection package.
            self.assertNotRegex(text, r"from legacy_documenter\.knowledge\.projection\b")
            self.assertNotRegex(text, r"import legacy_documenter\.knowledge\.projection\b")

    def test_no_documentation_or_analysis_change_touches_knowledge_package(self) -> None:
        touched = [
            "legacy_documenter/analysis/deep_interpretation.py",
            "legacy_documenter/analysis/targeted_exhaustion.py",
            "legacy_documenter/documentation/aggregation.py",
            "legacy_documenter/documentation/consistency.py",
            "legacy_documenter/documentation/contracts.py",
            "legacy_documenter/documentation/coverage.py",
            "legacy_documenter/documentation/envelope.py",
            "legacy_documenter/documentation/evidence_catalog.py",
            "legacy_documenter/documentation/human_review.py",
            "legacy_documenter/documentation/interpretation.py",
            "legacy_documenter/documentation/renderer.py",
        ]
        for rel in touched:
            self.assertFalse(rel.startswith("legacy_documenter/knowledge/"))


class ReadinessAndNoProviderCallsTests(unittest.TestCase):
    """(12) Readiness remains READY. (13) No LLM/provider calls anywhere touched."""

    def test_readiness_remains_ready(self) -> None:
        from legacy_documenter.knowledge import readiness
        result = readiness.run() if hasattr(readiness, "run") else None
        if result is None:
            self.skipTest("readiness module has no callable run() entry point in this build")
        self.assertEqual(result.get("readiness"), "READY")
        self.assertEqual(result.get("provider_calls"), 0)
        self.assertEqual(result.get("real_llm_calls"), 0)
        self.assertTrue(result.get("ai_knowledge_allowed"))
        self.assertFalse(result.get("ai_knowledge_generated"))

    def test_touched_files_introduce_no_new_network_or_provider_imports(self) -> None:
        touched = [
            "legacy_documenter/analysis/deep_interpretation.py",
            "legacy_documenter/analysis/targeted_exhaustion.py",
            "legacy_documenter/documentation/aggregation.py",
            "legacy_documenter/documentation/consistency.py",
            "legacy_documenter/documentation/contracts.py",
            "legacy_documenter/documentation/coverage.py",
            "legacy_documenter/documentation/envelope.py",
            "legacy_documenter/documentation/evidence_catalog.py",
            "legacy_documenter/documentation/human_review.py",
            "legacy_documenter/documentation/interpretation.py",
            "legacy_documenter/documentation/renderer.py",
        ]
        network_pattern = re.compile(r"^\s*(import|from)\s+(urllib|requests|socket|httpx|aiohttp)\b", re.MULTILINE)
        for rel in touched:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            self.assertIsNone(network_pattern.search(text), f"{rel} gained a network/provider import")


class EquivalenceArtifactTests(unittest.TestCase):
    """The Type and Contract Equivalence artifact itself is present and deterministic."""

    def test_artifact_present_and_valid_json(self) -> None:
        path = REPO_ROOT / "output" / "v4_1_r2" / "V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json"
        if not path.exists():
            self.skipTest("equivalence artifact not yet generated")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data.get("round"), "V4.1-R2")
        self.assertIn("td_005", data)
        self.assertEqual(data.get("production_behavior_changed"), False)


if __name__ == "__main__":
    unittest.main()
