"""V4-R14 — Manuals and Final Baseline: deterministic verification tests.

This is a documentation-consolidation round: no new knowledge capability is
implemented. These tests verify that the four required manuals exist and
contain the fixed, already-approved contract markers they must not
contradict, that the two final deterministic artifacts
(`output/v4_r14/V4_FINAL_BASELINE.json`, `output/v4_r14/V4_FINAL_MANIFEST.json`)
are valid, deterministic, and internally consistent with the repository, and
that R13's security/regression state is preserved.

Per the V4-R14 prompt's explicit warning (learned from `REG-001` in R13):
no test here hardcodes a `PROJECT_STATE.json` field value that will become
stale the moment V4-R14 itself is formally approved. Every such assertion
uses a round-ordinal "at least" comparison instead of an exact literal.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from legacy_documenter.knowledge.closure.artifact_hashes import (
    all_match,
    verify_reviewed_artifacts,
)
from legacy_documenter.knowledge.closure.baseline_report import (
    PLUGIN_CONTRACT_NAME,
    PLUGIN_CONTRACT_VERSION,
    build_final_baseline,
    render_final_baseline_json,
)
from legacy_documenter.knowledge.closure.manifest_report import (
    build_final_manifest,
    render_final_manifest_json,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

MANUAL_PATHS = (
    "docs/V4/V4_USER_MANUAL.md",
    "docs/V4/V4_DEVELOPER_MANUAL.md",
    "docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md",
    "docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md",
)

BASELINE_PATH = REPO_ROOT / "output" / "v4_r14" / "V4_FINAL_BASELINE.json"
MANIFEST_PATH = REPO_ROOT / "output" / "v4_r14" / "V4_FINAL_MANIFEST.json"


def _round_ordinal(round_label: str) -> int:
    """Extracts the numeric round ordinal from a label like 'V4-R13' or
    'V4-R13_APPROVED'. Used so tests never hardcode a literal round name
    that a later approval would invalidate (the REG-001 lesson)."""
    match = re.search(r"V4-R(\d+)", round_label)
    if not match:
        raise AssertionError(f"no_round_ordinal_found:{round_label}")
    return int(match.group(1))


def _read_manual(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _project_state() -> dict:
    return json.loads((REPO_ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))


class EntryGateAndContinuityTests(unittest.TestCase):
    """Item 1: entry gate / continuity."""

    def test_project_state_at_least_r13_approved(self) -> None:
        state = _project_state()
        self.assertGreaterEqual(_round_ordinal(state["latest_approved_round"]), 13)

    def test_project_state_readiness_ready(self) -> None:
        state = _project_state()
        self.assertEqual(state["readiness"], "READY")
        self.assertTrue(state["ai_knowledge_allowed"])
        self.assertFalse(state["ai_knowledge_generated"])
        self.assertEqual(state["provider_calls"], 0)
        self.assertEqual(state["real_llm_calls"], 0)

    def test_project_state_not_marked_r14_approved(self) -> None:
        """R14 must remain pending review; this round never approves itself."""
        state = _project_state()
        self.assertNotEqual(state.get("round_status"), "V4-R14_APPROVED")


class ManualsExistTests(unittest.TestCase):
    """Item 2: manuals exist."""

    def test_all_four_manuals_exist(self) -> None:
        for relative_path in MANUAL_PATHS:
            with self.subTest(manual=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).is_file())


class ContractMarkerTests(unittest.TestCase):
    """Items 3, 5, 6, 7, 8, 9: required contract markers present somewhere
    across the four manuals."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.combined_text = "\n".join(_read_manual(p) for p in MANUAL_PATHS)

    def test_one_canonical_knowledge_source_marker(self) -> None:
        self.assertIn("ONE_CANONICAL_KNOWLEDGE_SOURCE", self.combined_text)

    def test_source_code_optional_marker(self) -> None:
        self.assertIn("SOURCE_CODE_OPTIONAL", self.combined_text)

    def test_technical_lead_authority_marker(self) -> None:
        self.assertIn("TECHNICAL_LEAD", self.combined_text)

    def test_v5_not_implemented_marker(self) -> None:
        self.assertIn("V5_NOT_IMPLEMENTED", self.combined_text)

    def test_post_v4_maintainability_refactor_planned_marker(self) -> None:
        self.assertIn("POST_V4_MAINTAINABILITY_REFACTOR", self.combined_text)
        self.assertIn("PLANNED", self.combined_text)

    def test_plugin_contract_name_and_version_markers(self) -> None:
        self.assertIn("LegacyMapperPluginKnowledge", self.combined_text)
        self.assertIn("1.0", self.combined_text)

    def test_ai_never_grants_approval_marker(self) -> None:
        self.assertIn("AI_NEVER_GRANTS_APPROVAL", self.combined_text)

    def test_r11_r12_sibling_language_present(self) -> None:
        self.assertIn("sibling", self.combined_text.lower())


class PluginContractConsistencyTests(unittest.TestCase):
    """Item 4: Plugin contract name/version matches R12 exactly."""

    def test_matches_r12_contract_json(self) -> None:
        r12_contract = json.loads(
            (
                REPO_ROOT
                / "output"
                / "v4_r12"
                / "V4_PLUGIN_FACING_OUTPUT_CONTRACT.json"
            ).read_text(encoding="utf-8")
        )
        contract_text = json.dumps(r12_contract)
        self.assertIn(PLUGIN_CONTRACT_NAME, contract_text)
        self.assertIn(PLUGIN_CONTRACT_VERSION, contract_text)

    def test_matches_baseline_builder_constants(self) -> None:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(baseline["plugin_contract_name"], PLUGIN_CONTRACT_NAME)
        self.assertEqual(baseline["plugin_contract_version"], PLUGIN_CONTRACT_VERSION)


class BaselineJsonValidityTests(unittest.TestCase):
    """Item 10: baseline JSON validity."""

    REQUIRED_KEYS = (
        "version",
        "latest_completed_round",
        "latest_approved_round",
        "test_count",
        "readiness",
        "ai_knowledge_allowed",
        "ai_knowledge_generated",
        "provider_calls",
        "real_llm_calls",
        "canonical_knowledge_model",
        "human_projection",
        "plugin_projection",
        "plugin_contract_name",
        "plugin_contract_version",
        "security_gate",
        "regression_gate",
        "critical_open",
        "high_open",
        "medium_open",
        "low_open",
        "source_code_optional",
        "technical_lead_final_approval_authority",
        "v5_implemented",
        "post_v4_maintainability_refactor",
        "approved_artifact_hashes",
        "manuals",
        "maintainability_baseline",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    def test_file_exists_and_parses(self) -> None:
        self.assertIsInstance(self.baseline, dict)

    def test_all_required_keys_present(self) -> None:
        for key in self.REQUIRED_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, self.baseline)

    def test_version_is_v4(self) -> None:
        self.assertEqual(self.baseline["version"], "V4")

    def test_v5_implemented_is_false(self) -> None:
        self.assertFalse(self.baseline["v5_implemented"])

    def test_provider_and_llm_calls_zero(self) -> None:
        self.assertEqual(self.baseline["provider_calls"], 0)
        self.assertEqual(self.baseline["real_llm_calls"], 0)
        self.assertFalse(self.baseline["ai_knowledge_generated"])

    def test_latest_completed_round_is_r14_or_later(self) -> None:
        self.assertGreaterEqual(
            _round_ordinal(self.baseline["latest_completed_round"]), 14
        )

    def test_latest_approved_round_is_at_least_r13(self) -> None:
        self.assertGreaterEqual(
            _round_ordinal(self.baseline["latest_approved_round"]), 13
        )


class ManifestJsonValidityTests(unittest.TestCase):
    """Item 11: manifest JSON validity."""

    REQUIRED_CATEGORIES = (
        "authority_files",
        "manuals",
        "round_results",
        "round_closures",
        "contracts",
        "examples",
        "security_artifacts",
        "baseline",
        "continuity_files",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_file_exists_and_parses(self) -> None:
        self.assertIsInstance(self.manifest, dict)

    def test_all_required_categories_present(self) -> None:
        for category in self.REQUIRED_CATEGORIES:
            with self.subTest(category=category):
                self.assertIn(category, self.manifest)
                self.assertIsInstance(self.manifest[category], list)

    def test_index_not_authority_policy_present(self) -> None:
        self.assertEqual(
            self.manifest["index_policy"], "FINAL_MANIFEST_IS_INDEX_NOT_AUTHORITY"
        )

    def test_manuals_category_lists_all_four(self) -> None:
        self.assertEqual(sorted(self.manifest["manuals"]), sorted(MANUAL_PATHS))


class DeterminismTests(unittest.TestCase):
    """Items 12, 13: deterministic baseline / manifest generation."""

    def test_baseline_deterministic_across_two_builds(self) -> None:
        first = render_final_baseline_json(build_final_baseline(REPO_ROOT))
        second = render_final_baseline_json(build_final_baseline(REPO_ROOT))
        self.assertEqual(first, second)

    def test_baseline_matches_on_disk_artifact(self) -> None:
        rebuilt = render_final_baseline_json(build_final_baseline(REPO_ROOT))
        on_disk = BASELINE_PATH.read_text(encoding="utf-8")
        self.assertEqual(rebuilt, on_disk)

    def test_manifest_deterministic_across_two_builds(self) -> None:
        first = render_final_manifest_json(build_final_manifest(REPO_ROOT))
        second = render_final_manifest_json(build_final_manifest(REPO_ROOT))
        self.assertEqual(first, second)

    def test_manifest_matches_on_disk_artifact(self) -> None:
        rebuilt = render_final_manifest_json(build_final_manifest(REPO_ROOT))
        on_disk = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertEqual(rebuilt, on_disk)


class NoMachineSpecificPathTests(unittest.TestCase):
    """Item 14: no machine-specific absolute paths in the final artifacts."""

    _ABSOLUTE_PATTERNS = (
        re.compile(r"[A-Za-z]:[\\/]"),  # drive-qualified Windows path
        re.compile(r"/home/"),
        re.compile(r"/Users/"),
        re.compile(r"\\\\"),  # UNC path
    )

    def test_baseline_has_no_absolute_paths(self) -> None:
        text = BASELINE_PATH.read_text(encoding="utf-8")
        for pattern in self._ABSOLUTE_PATTERNS:
            with self.subTest(pattern=pattern.pattern):
                self.assertIsNone(pattern.search(text))

    def test_manifest_has_no_absolute_paths(self) -> None:
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        for pattern in self._ABSOLUTE_PATTERNS:
            with self.subTest(pattern=pattern.pattern):
                self.assertIsNone(pattern.search(text))

    def test_baseline_has_no_timestamp_like_fields(self) -> None:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        text = json.dumps(baseline)
        # No ISO-8601-shaped timestamp anywhere in the baseline.
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", text))


class ArtifactHashIntegrityTests(unittest.TestCase):
    """Item 15: important (R10-R13) artifact hashes match their recorded
    closure-document values, recomputed independently of the production
    `closure` package's own verification call."""

    def test_reviewed_artifacts_recorded_hash_matches_disk(self) -> None:
        import hashlib

        results = verify_reviewed_artifacts(REPO_ROOT)
        self.assertTrue(all_match(results))
        for item in results:
            with self.subTest(path=item["path"]):
                actual = hashlib.sha256(
                    (REPO_ROOT / item["path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(actual, item["recorded_sha256"])

    def test_baseline_approved_artifact_hashes_match_disk(self) -> None:
        import hashlib

        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        for entry in baseline["approved_artifact_hashes"]:
            with self.subTest(path=entry["path"]):
                actual = hashlib.sha256(
                    (REPO_ROOT / entry["path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(actual, entry["sha256"])


class ManifestPathsExistTests(unittest.TestCase):
    """Items 16, 17: manifest repository paths exist; broken internal
    references == 0."""

    def test_every_manifest_path_exists(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        broken = []
        for category, paths in manifest.items():
            if category == "index_policy" or not isinstance(paths, list):
                continue
            for relative_path in paths:
                if not (REPO_ROOT / relative_path).exists():
                    broken.append(relative_path)
        self.assertEqual(broken, [], f"broken manifest references: {broken}")

    _PATH_TOKEN_RE = re.compile(
        r"`((?:docs|output|tests|prompts|legacy_documenter|codex)/[A-Za-z0-9_./-]+"
        r"|PROJECT_STATE\.json|AGENTS\.md|CLAUDE\.md|\.gitignore)`"
    )

    def _extract_path_like_tokens(self, text: str) -> list[str]:
        """Extracts backtick-quoted tokens from manual prose that look like
        genuine repository-relative file references (not conceptual
        examples, which use placeholders like `<...>` and are excluded by
        the pattern itself requiring no angle brackets)."""
        return sorted(set(self._PATH_TOKEN_RE.findall(text)))

    def test_manual_path_references_exist(self) -> None:
        broken = []
        for manual_relative_path in MANUAL_PATHS:
            text = _read_manual(manual_relative_path)
            for token in self._extract_path_like_tokens(text):
                candidate = REPO_ROOT / token
                if not candidate.exists():
                    broken.append((manual_relative_path, token))
        self.assertEqual(broken, [], f"broken internal references: {broken}")


class SecurityAndRegressionPreservedTests(unittest.TestCase):
    """Item 18: security/regression state preserved from R13."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(
            (
                REPO_ROOT / "output" / "v4_r13" / "V4_REGRESSION_SECURITY_REPORT.json"
            ).read_text(encoding="utf-8")
        )

    def test_security_gate_pass(self) -> None:
        self.assertEqual(self.report["security_gate"]["status"], "PASS")
        self.assertEqual(self.report["security_gate"]["critical_open"], 0)
        self.assertEqual(self.report["security_gate"]["high_open"], 0)

    def test_regression_gate_pass(self) -> None:
        self.assertEqual(self.report["regression_gate"]["status"], "PASS")

    def test_open_defect_counts_preserved(self) -> None:
        counts = self.report["open_defect_counts_by_severity"]
        self.assertEqual(counts["CRITICAL"], 0)
        self.assertEqual(counts["HIGH"], 0)

    def test_baseline_reflects_same_gates(self) -> None:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(baseline["security_gate"], "PASS")
        self.assertEqual(baseline["regression_gate"], "PASS")
        self.assertEqual(baseline["critical_open"], 0)
        self.assertEqual(baseline["high_open"], 0)


class NoProviderOrLlmCallsTests(unittest.TestCase):
    """Item 19: no provider/LLM calls anywhere in the new R14 code."""

    _FORBIDDEN_IMPORTS = ("openai", "anthropic", "google.generativeai", "cohere", "ollama")

    def test_closure_package_has_no_provider_imports(self) -> None:
        closure_dir = REPO_ROOT / "legacy_documenter" / "knowledge" / "closure"
        for py_file in closure_dir.glob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for forbidden in self._FORBIDDEN_IMPORTS:
                with self.subTest(file=py_file.name, forbidden=forbidden):
                    self.assertNotIn(forbidden, text)

    def test_project_state_confirms_zero_calls(self) -> None:
        state = _project_state()
        self.assertEqual(state["provider_calls"], 0)
        self.assertEqual(state["real_llm_calls"], 0)


class AgentNeutralContinuityTests(unittest.TestCase):
    """Item 20: repository continuity remains agent-neutral."""

    def test_agents_md_names_no_specific_ai_vendor_as_a_requirement(self) -> None:
        # AGENTS.md's one "Codex" mention is an explicit, historical
        # explanation of the `codex/` directory name (V1-V3 execution
        # records) and explicitly states it is "not a Codex-only capability
        # requirement" -- this is the required agent-neutral framing, not a
        # violation of it. Claude/Copilot/Gemini/ChatGPT are never named.
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for vendor_token in ("Claude", "Copilot", "Gemini", "ChatGPT"):
            with self.subTest(vendor=vendor_token):
                self.assertNotIn(vendor_token, text)
        self.assertIn("not a Codex-only capability requirement", text)

    def test_agents_md_points_to_project_state_for_current_phase(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("PROJECT_STATE.json", text)

    def test_developer_manual_is_agent_neutral_in_framing(self) -> None:
        text = _read_manual("docs/V4/V4_DEVELOPER_MANUAL.md")
        self.assertIn("AI development agent", text)


if __name__ == "__main__":
    unittest.main()
