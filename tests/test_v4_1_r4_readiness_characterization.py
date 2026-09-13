"""V4.1-R4 -- Readiness Module Decomposition: characterization tests (DEBT-002).

Pins the exact pre-decomposition behavior of `legacy_documenter.knowledge.readiness`
so that the internal parsing/evidence-closure/file-I/O split performed by this round
can be verified behaviorally equivalent. Captures existing behavior, not desired
behavior; nothing here may be weakened to make the split easier.
"""
from __future__ import annotations

import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path

from legacy_documenter.knowledge import readiness

ROOT = Path(__file__).parents[1]

PUBLIC_SIGNATURES = {
    "run": "(workspace: str | pathlib.Path = '.') -> dict[str, object]",
    "KnowledgeReadinessService": "(workspace: str | pathlib.Path = '.') -> None",
    "parse_human_record": "(text: str) -> dict[str, object]",
    "validate_preconditions": "(functional: str, technical: str, review: dict[str, object]) -> bool",
    "validate_claims": "(documents: dict[str, dict[str, object]]) -> bool",
    "architecture_valid": "(technical_text: str, human_text: str, architecture_evidence: dict[str, object]) -> bool",
    "quantitative_valid": "(texts: dict[str, str]) -> bool",
    "build_projection": "(documents: dict[str, dict[str, object]], details: dict[str, dict[str, dict[str, object]]], "
                         "review: dict[str, object], snapshots: dict[str, str | None]) -> list[dict[str, object]]",
    "build_boundary": "(records: list[dict[str, object]]) -> dict[str, list[str]]",
}

# Names that pre-decomposition tests (tests/test_v3_r9.py) rely on resolving directly
# from the `legacy_documenter.knowledge.readiness` module namespace -- either via
# `from ... import *` or an explicit private-name import. All must keep resolving.
PATCH_POINTS = [
    "run", "KnowledgeReadinessService", "parse_human_record", "quantitative_valid",
    "validate_preconditions", "validate_claims", "architecture_valid",
    "build_projection", "build_boundary",
    "EXPECTED", "PROHIBITED_ASSERTIONS", "ALLOWED_STATUSES", "ALLOWED_METRIC_SCOPES",
    "_hash", "_safe", "_read", "_field", "_details", "_csv",
    "_canonical_catalog", "evidence_closed", "evidence_closure_diagnostics", "_execute",
]


class PublicImportTests(unittest.TestCase):
    """Every currently-resolvable module attribute must keep resolving after the split."""

    def test_module_exposes_every_patch_point(self) -> None:
        for name in PATCH_POINTS:
            self.assertTrue(hasattr(readiness, name), msg=f"missing {name}")

    def test_wildcard_import_style_names_present(self) -> None:
        # Mirrors tests/test_v3_r9.py's `from legacy_documenter.knowledge.readiness import *`.
        namespace: dict[str, object] = {}
        exec("from legacy_documenter.knowledge.readiness import *", namespace)
        for name in ("EXPECTED", "PARTIAL", "EXTERNAL", "PROHIBITED_ASSERTIONS", "run",
                     "parse_human_record", "quantitative_valid", "validate_preconditions"):
            self.assertIn(name, namespace, msg=f"missing {name} from wildcard import")


class PublicSignatureTests(unittest.TestCase):
    """Signatures of the documented public surface must not drift."""

    def test_signatures_match_pinned_baseline(self) -> None:
        for name, expected in PUBLIC_SIGNATURES.items():
            actual = str(inspect.signature(getattr(readiness, name)))
            self.assertEqual(actual, expected, msg=f"{name} signature drifted")


class RepresentativeResultTests(unittest.TestCase):
    """Pins the shape and content of a representative READY run."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = readiness.run(ROOT)

    def test_result_keys(self) -> None:
        self.assertEqual(
            sorted(self.result.keys()),
            ["ai_knowledge_allowed", "ai_knowledge_generated", "checks", "ineligible_records",
             "output", "provider_calls", "readiness", "real_llm_calls", "records", "status"],
        )

    def test_readiness_is_ready(self) -> None:
        self.assertEqual(self.result["readiness"], "READY")

    def test_all_checks_pass(self) -> None:
        self.assertEqual(
            self.result["checks"],
            {"architecture_integrity": True, "claim_integrity": True, "evidence_closure": True,
             "knowledge_boundary": True, "knowledge_projection": True, "preconditions": True,
             "quantitative_integrity": True, "security": True},
        )

    def test_record_counts(self) -> None:
        self.assertEqual(self.result["records"], 47)
        self.assertEqual(self.result["ineligible_records"], 4)

    def test_ai_knowledge_semantics(self) -> None:
        self.assertTrue(self.result["ai_knowledge_allowed"])
        self.assertFalse(self.result["ai_knowledge_generated"])

    def test_no_provider_or_llm_calls(self) -> None:
        self.assertEqual(self.result["provider_calls"], 0)
        self.assertEqual(self.result["real_llm_calls"], 0)

    def test_non_ready_result_supported_by_existing_fixture(self) -> None:
        # Mirrors tests/test_v3_r9.py::test_39_nonready_flag: current behavior supports
        # a representative non-ready (validate_preconditions=False) input without a
        # full BLOCKED end-to-end run (no fixture for a full BLOCKED run exists).
        functional = (ROOT / "output/LEVANTAMIENTO_FUNCIONAL.md").read_text(encoding="utf-8")
        technical = (ROOT / "output/LEVANTAMIENTO_TECNICO.md").read_text(encoding="utf-8")
        human_text = (ROOT / "codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md").read_text(encoding="utf-8")
        review = readiness.parse_human_record(human_text)
        self.assertFalse(readiness.validate_preconditions(
            functional.replace("document_status=APPROVED", "document_status=DRAFT"), technical, review,
        ))


class SerializationAndOrderingTests(unittest.TestCase):
    """Output artifact bytes must be deterministic and stable across repeated runs."""

    def test_output_files_are_byte_identical_across_runs(self) -> None:
        output = ROOT / "output/v3_r9"
        files = sorted(output.glob("*.json"))
        before = [readiness._hash(p) for p in files]
        readiness.run(ROOT)
        after = [readiness._hash(p) for p in files]
        self.assertEqual(before, after)

    def test_pinned_output_hashes(self) -> None:
        # Pinned immediately before the V4.1-R4 internal decomposition; any change
        # here after the split means the decomposition altered output bytes.
        expected = {
            "KNOWLEDGE_BOUNDARY.json": "96b2e2aa6286331aeda4c5e0d239fe761397050b5163afb3cea90b0c8f477734",
            "KNOWLEDGE_PROJECTION.json": "e2974e6545f23576e5ba796d8df4b659f818bd194d12a5327ddb64375bcc373c",
            "KNOWLEDGE_READINESS.json": "8299c40b72e7b656a0c3d162b988f762937587a24686eebe15dd7c57214f6d19",
            "READINESS_TRACEABILITY.json": "165611f9dbf77ff8e5c71ce129a5714bc29bbe6b34c281d8a56411c619ac9fdd",
        }
        readiness.run(ROOT)
        output = ROOT / "output/v3_r9"
        for name, digest in expected.items():
            self.assertEqual(readiness._hash(output / name), digest, msg=name)


class ExceptionBehaviorTests(unittest.TestCase):
    """Existing failure modes must remain identical after the split."""

    def test_duplicate_human_disposition_raises(self) -> None:
        text = "FMI-001=HUMAN_CONFIRMED\nFMI-001=ACCEPTED_AS_PARTIAL\n"
        with self.assertRaises(ValueError):
            readiness.parse_human_record(text)

    def test_missing_field_returns_none(self) -> None:
        self.assertIsNone(readiness._field("no matching content", "SOME_FIELD"))

    def test_csv_na_returns_empty(self) -> None:
        self.assertEqual(readiness._csv("N/A"), [])


class CliInvocationTests(unittest.TestCase):
    """`python -m legacy_documenter.knowledge.readiness` must keep working unchanged."""

    def test_cli_prints_matching_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "legacy_documenter.knowledge.readiness"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["readiness"], "READY")
        self.assertEqual(payload["status"], "V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE")
        self.assertEqual(payload["provider_calls"], 0)
        self.assertEqual(payload["real_llm_calls"], 0)


class FilesystemAndStateInteractionTests(unittest.TestCase):
    """Records what readiness.py touches on disk and confirms no PROJECT_STATE coupling."""

    def test_previous_evidence_and_documents_immutable(self) -> None:
        files = [ROOT / "output/LEVANTAMIENTO_FUNCIONAL.md", ROOT / "output/LEVANTAMIENTO_TECNICO.md",
                 ROOT / "codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md"]
        before = [readiness._hash(p) for p in files]
        readiness.run(ROOT)
        after = [readiness._hash(p) for p in files]
        self.assertEqual(before, after)

    def test_no_project_state_dependency(self) -> None:
        # readiness.py reads only the fixed V3 document/evidence paths below; it has
        # no dependency on PROJECT_STATE.json (NOT_APPLICABLE, confirmed by source scan).
        source = inspect.getsource(readiness)
        self.assertNotIn("PROJECT_STATE", source)


if __name__ == "__main__":
    unittest.main()
