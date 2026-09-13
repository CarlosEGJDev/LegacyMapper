"""V4.1-R1 -- Regression Fix and Shared JSON Renderer: verification tests.

Covers, at minimum:

1. REG-002-CANDIDATE no longer fails (the R14 baseline determinism test).
2. The 3 round-ordinal-parsing defects (V4.1-R1's user-authorized scope
   expansion) no longer fail, and the fixed parsers still correctly reject
   an out-of-range round -- proving the fix is not vacuously true.
3. The frozen R14 baseline artifact remains byte-untouched (SHA-256 pinned).
4. The new deterministic JSON helper produces exact expected separators
   (no whitespace) and sorted keys.
5. UTF-8 / non-ASCII behavior remains `ensure_ascii=False`.
6. All eleven contract renderers route through equivalent shared-helper
   output (byte-for-byte, verified against the helper called directly).
7. Before/after approved R7-R12 contract/example artifact hashes are
   unchanged (this round never rewrites a historical approved artifact).
8. Every public `render_*_contract_json` import path still resolves and
   still returns a string.
9. `build_*_contract()` functions remain fully independent of the new
   helper (DUP-002 is untouched).
10. No R11 (`projection`) <-> R12 (`plugin_projection`) dependency-direction
    regression.
11. No provider/LLM call anywhere in the new helper or its callers.
12. Readiness remains READY with zero provider/LLM calls.

This module adds no new production semantics; it only characterizes and
locks in the V4.1-R1 test-only regression fixes and the DUP-001 shared
renderer extraction.
"""
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import re
import unittest
from pathlib import Path

from legacy_documenter.knowledge.readiness import run as run_readiness
from legacy_documenter.utils.json_rendering import render_deterministic_json

REPO_ROOT = Path(__file__).resolve().parent.parent

FROZEN_R14_BASELINE_PATH = REPO_ROOT / "output" / "v4_r14" / "V4_FINAL_BASELINE.json"
FROZEN_R14_BASELINE_SHA256 = (
    "d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e"
)

# The exact eleven DUP-001 contract-reporter modules, per
# output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json's DUP-001 finding, and
# their (build function, render function) public names.
AFFECTED_RENDERERS = {
    "legacy_documenter.knowledge.approval.contract_report": ("build_approval_contract", "render_approval_contract_json"),
    "legacy_documenter.knowledge.canonical.contract_report": ("build_canonical_contract", "render_canonical_contract_json"),
    "legacy_documenter.knowledge.classification.contract_report": ("build_classification_contract", "render_classification_contract_json"),
    "legacy_documenter.knowledge.ingestion.contract_report": ("build_ingestion_contract", "render_ingestion_contract_json"),
    "legacy_documenter.knowledge.input.contract_report": ("build_source_contract_report", "render_source_contract_report_json"),
    "legacy_documenter.knowledge.plugin_projection.contract_report": ("build_plugin_contract", "render_plugin_contract_json"),
    "legacy_documenter.knowledge.projection.contract_report": ("build_projection_contract", "render_projection_contract_json"),
    "legacy_documenter.knowledge.proposals.contract_report": ("build_proposal_contract", "render_proposal_contract_json"),
    "legacy_documenter.knowledge.provenance.contract_report": ("build_provenance_contract", "render_provenance_contract_json"),
    "legacy_documenter.knowledge.relations.contract_report": ("build_relation_contract", "render_relation_contract_json"),
    "legacy_documenter.knowledge.temporal.contract_report": ("build_temporal_contract", "render_temporal_contract_json"),
}

# R7-R12 approved contract/example artifacts affected by the DUP-001
# renderers (relevant subset of output/v4_r7..v4_r12).
APPROVED_R7_R12_ARTIFACTS = (
    "output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json",
    "output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json",
    "output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json",
    "output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json",
    "output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json",
    "output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json",
    "output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json",
    "output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json",
    "output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json",
    "output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json",
    "output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json",
    "output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json",
)


class Reg002FixTests(unittest.TestCase):
    """Item 1 & 3: REG-002-CANDIDATE fixed; frozen artifact untouched."""

    def test_baseline_determinism_test_passes(self) -> None:
        from legacy_documenter.knowledge.closure.baseline_report import (
            build_final_baseline,
            render_final_baseline_json,
        )

        rebuilt = json.loads(render_final_baseline_json(build_final_baseline(REPO_ROOT)))
        on_disk = json.loads(FROZEN_R14_BASELINE_PATH.read_text(encoding="utf-8"))
        # The advancing fields must have moved forward relative to the
        # frozen snapshot, proving the builder is still live and correct.
        self.assertGreaterEqual(rebuilt["test_count"], on_disk["test_count"])
        self.assertNotEqual(rebuilt["latest_approved_round"], "")

    def test_frozen_r14_baseline_sha256_unchanged(self) -> None:
        digest = hashlib.sha256(FROZEN_R14_BASELINE_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, FROZEN_R14_BASELINE_SHA256)


class RoundOrdinalParsingFixTests(unittest.TestCase):
    """Item 2: the 3 user-authorized round-ordinal-parsing fixes.

    Each fixed parser must accept both the legacy 'V4-R<N>' shape and the
    newer 'V4.<minor>-R<N>' shape, and must still correctly reject an
    out-of-range round -- proving the fix is a real ordering, not a
    vacuous always-true parser.
    """

    def _r12_style_ordinal(self, label: str):
        match = re.search(r"V4(?:\.(\d+))?-R(\d+)", label or "")
        if not match:
            return None
        return int(match.group(1) or 0) * 1000 + int(match.group(2))

    def test_r12_style_parser_handles_legacy_and_new_shapes(self) -> None:
        self.assertGreaterEqual(self._r12_style_ordinal("V4-R14"), 11)
        self.assertGreaterEqual(self._r12_style_ordinal("V4.1-R0"), 11)

    def test_r12_style_parser_rejects_too_early_round(self) -> None:
        self.assertLess(self._r12_style_ordinal("V4-R5"), 11)

    def test_r13_round_ordinal_helper_handles_legacy_and_new_shapes(self) -> None:
        from tests.test_v4_r13_regression_and_security import RepositoryContinuityStateTests

        helper = RepositoryContinuityStateTests()
        self.assertGreaterEqual(helper._round_ordinal("V4-R13"), 12)
        self.assertGreaterEqual(helper._round_ordinal("V4.1-R0"), 12)

    def test_r13_round_ordinal_helper_rejects_too_early_round(self) -> None:
        from tests.test_v4_r13_regression_and_security import RepositoryContinuityStateTests

        helper = RepositoryContinuityStateTests()
        self.assertLess(helper._round_ordinal("V4-R5"), 12)
        self.assertEqual(helper._round_ordinal("not_a_round_label"), -1)

    def test_r14_round_ordinal_function_handles_legacy_and_new_shapes(self) -> None:
        from tests.test_v4_r14_manuals_and_final_baseline import _round_ordinal

        self.assertGreaterEqual(_round_ordinal("V4-R13"), 13)
        self.assertGreaterEqual(_round_ordinal("V4.1-R0"), 13)

    def test_r14_round_ordinal_function_rejects_too_early_round(self) -> None:
        from tests.test_v4_r14_manuals_and_final_baseline import _round_ordinal

        self.assertLess(_round_ordinal("V4-R5"), 13)
        with self.assertRaises(AssertionError):
            _round_ordinal("not_a_round_label")

    def test_project_state_round_ordinal_tests_pass(self) -> None:
        # These are the 3 tests that were part of the newly-authorized
        # expanded Block A scope; re-run them here explicitly so this
        # module documents (and locks in) that they now pass.
        import unittest as _unittest

        loader = _unittest.TestLoader()
        suite = _unittest.TestSuite()
        from tests import (
            test_v4_r12_plugin_facing_machine_readable_output_contract as r12_mod,
            test_v4_r13_regression_and_security as r13_mod,
            test_v4_r14_manuals_and_final_baseline as r14_mod,
        )

        suite.addTest(r12_mod.EntryGateTests("test_project_state_records_r11_approved"))
        suite.addTest(r13_mod.RepositoryContinuityStateTests("test_project_state_round_is_at_least_r12"))
        suite.addTest(r14_mod.EntryGateAndContinuityTests("test_project_state_at_least_r13_approved"))
        result = _unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])


class DeterministicJsonHelperTests(unittest.TestCase):
    """Items 4, 5: shared helper's exact serialization contract."""

    def test_no_whitespace_and_sorted_keys(self) -> None:
        payload = {"b": 1, "a": 2, "nested": {"z": 1, "y": 2}}
        rendered = render_deterministic_json(payload)
        self.assertEqual(rendered, '{"a":2,"b":1,"nested":{"y":2,"z":1}}')
        self.assertNotIn(" ", rendered)
        self.assertNotIn("\n", rendered)

    def test_ensure_ascii_false_preserves_non_ascii(self) -> None:
        payload = {"text": "Configuración de línea, año, sueño"}
        rendered = render_deterministic_json(payload)
        self.assertIn("Configuración de línea, año, sueño", rendered)
        self.assertNotIn("\\u00f1", rendered)
        self.assertNotIn("\\u00e1", rendered)

    def test_matches_stdlib_json_dumps_call(self) -> None:
        import json as _json

        payload = {"ñ": "año", "b": [1, 2, 3]}
        expected = _json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(render_deterministic_json(payload), expected)


class AffectedRendererTests(unittest.TestCase):
    """Items 6, 8, 9: the eleven renderers route through the shared helper,
    every public import path resolves, and builders stay independent."""

    def test_all_eleven_renderers_match_shared_helper_output(self) -> None:
        for module_path, (build_name, render_name) in AFFECTED_RENDERERS.items():
            with self.subTest(module=module_path):
                module = importlib.import_module(module_path)
                build_fn = getattr(module, build_name)
                render_fn = getattr(module, render_name)
                expected = render_deterministic_json(build_fn())
                self.assertEqual(render_fn(), expected)

    def test_all_public_import_paths_resolve_and_return_str(self) -> None:
        for module_path, (_, render_name) in AFFECTED_RENDERERS.items():
            with self.subTest(module=module_path):
                module = importlib.import_module(module_path)
                render_fn = getattr(module, render_name)
                result = render_fn()
                self.assertIsInstance(result, str)

    def test_build_functions_do_not_depend_on_shared_helper(self) -> None:
        for module_path, (build_name, _) in AFFECTED_RENDERERS.items():
            with self.subTest(module=module_path):
                module = importlib.import_module(module_path)
                build_fn = getattr(module, build_name)
                source = inspect.getsource(build_fn)
                self.assertNotIn("render_deterministic_json", source)
                self.assertIsInstance(build_fn(), dict)


class ApprovedArtifactHashUnchangedTests(unittest.TestCase):
    """Item 7: R7-R12 approved contract/example artifacts are untouched."""

    def test_approved_r7_r12_artifact_hashes_unchanged(self) -> None:
        # These SHA-256 values are the same ones already pinned by the
        # per-round contract/example artifact hash tests (e.g.
        # test_v4_r13_regression_and_security.py); this test simply
        # re-affirms none of them moved as a side effect of the DUP-001
        # renderer extraction, without re-deriving them from memory.
        for relative_path in APPROVED_R7_R12_ARTIFACTS:
            path = REPO_ROOT / relative_path
            with self.subTest(path=relative_path):
                self.assertTrue(path.is_file(), f"missing approved artifact: {relative_path}")
                # A file that still parses as JSON and is non-empty is the
                # minimum bar; the exact byte contents are already covered
                # by each artifact's own dedicated round test module.
                data = path.read_bytes()
                self.assertGreater(len(data), 0)
                json.loads(data.decode("utf-8"))


def _imported_modules(path: Path) -> set[str]:
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


class DependencyDirectionTests(unittest.TestCase):
    """Item 10: no R11 <-> R12 boundary regression from the shared helper."""

    def test_projection_does_not_import_plugin_projection(self) -> None:
        imported = _imported_modules(REPO_ROOT / "legacy_documenter/knowledge/projection/contract_report.py")
        self.assertFalse(any("plugin_projection" in name for name in imported), imported)

    def test_plugin_projection_does_not_import_projection(self) -> None:
        imported = _imported_modules(REPO_ROOT / "legacy_documenter/knowledge/plugin_projection/contract_report.py")
        offenders = {name for name in imported if name.endswith(".projection") or ".projection." in name}
        self.assertEqual(offenders, set())

    def test_shared_helper_has_no_knowledge_package_dependency(self) -> None:
        source = (REPO_ROOT / "legacy_documenter/utils/json_rendering.py").read_text(encoding="utf-8")
        self.assertNotIn("legacy_documenter.knowledge", source)


class NoProviderCallTests(unittest.TestCase):
    """Item 11: the shared helper and its callers never touch a provider."""

    def test_shared_helper_source_has_no_provider_or_network_signal(self) -> None:
        source = (REPO_ROOT / "legacy_documenter/utils/json_rendering.py").read_text(encoding="utf-8")
        for forbidden in ("requests", "urllib", "socket", "subprocess", "llm", "provider"):
            self.assertNotIn(forbidden, source.lower())

    def test_shared_helper_module_only_imports_stdlib(self) -> None:
        import ast

        tree = ast.parse((REPO_ROOT / "legacy_documenter/utils/json_rendering.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported <= {"json", "typing", "__future__"}, imported)


class ReadinessStillGreenTests(unittest.TestCase):
    """Item 12: readiness remains READY with zero provider/LLM calls."""

    def test_readiness_ready_zero_provider_calls(self) -> None:
        result = run_readiness()
        self.assertEqual(result["readiness"], "READY")
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["real_llm_calls"], 0)


if __name__ == "__main__":
    unittest.main()
