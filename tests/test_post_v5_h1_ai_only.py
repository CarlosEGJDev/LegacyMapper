"""Post-V5 H1: AI-only interpretation over an existing deterministic baseline.

Networkless: every provider here is a Fake grounded in the persisted Evidence (the Evidence guard stays active).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.context.ai_projection import package_reference_ids
from legacy_documenter.llm import FakeAIProvider, ProviderConfig
from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration import ai_interpretation
from legacy_documenter.orchestration.ai_only import (
    AI_ONLY_INPUT_INVALID, BaselineInvalid, run_ai_only, validate_baseline,
)
from legacy_documenter.review.service import ApprovalService

FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"


class GroundedFake(FakeAIProvider):
    """Quotes a real Evidence id from the persisted package (never weakens grounding)."""

    def structured_generate(self, request, schema=None):
        refs = sorted(r for r in package_reference_ids(request.context) if str(r).startswith("DAO-")) or sorted(package_reference_ids(request.context))
        self.structured = {"findings": [{"statement": "H1: the traced flow ends in a data operation.", "confidence": "UNCERTAIN", "evidence_refs": refs[:1]}]}
        return super().structured_generate(request, schema)


def make_provider() -> GroundedFake:
    return GroundedFake(ProviderConfig("FAKE", "fake-h1", "offline", context_window=16000, max_output_tokens=2000,
                                        capabilities={"structured_output": True}))


def tree_digest(root: Path, skip: tuple[str, ...] = ("ai_runs",)) -> dict:
    out = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_file() and not any(rel == s or rel.startswith(s + "/") for s in skip):
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


class H1Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="h1_"))
        cls.source = cls.tmp / "source"
        shutil.copytree(FIXTURE, cls.source)
        cls.baseline = cls.tmp / "baseline"
        result = quiet(run_full_pipeline, cls.source, cls.baseline, [], 12)
        assert result.status.value == "SUCCESS", result.status
        cls.pristine = cls.tmp / "pristine"
        shutil.copytree(cls.baseline, cls.pristine)
        shutil.rmtree(cls.source)  # the original source tree no longer exists for any H1 test

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def fresh_baseline(self) -> Path:
        target = Path(tempfile.mkdtemp(prefix="h1b_", dir=self.tmp)) / "b"
        shutil.copytree(self.pristine, target)
        return target

    def assert_invalid_without_provider(self, baseline: Path, expect: str):
        provider = make_provider()
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider resolution forbidden")) as guard:
            result = run_ai_only(baseline, provider=provider)
        self.assertEqual(result.status, AI_ONLY_INPUT_INVALID)
        self.assertTrue(result.reason.startswith(expect), result.reason)
        self.assertFalse(result.provider_called)
        self.assertEqual(provider.requests, [])
        self.assertEqual(guard.call_count, 0)
        self.assertIsNone(result.ai_run_dir)


class BaselineValidationTests(H1Base):
    def test_valid_persisted_baseline_is_accepted(self):
        info = validate_baseline(self.pristine)
        self.assertEqual(info.evidence_schema_version, "1.0")
        self.assertTrue(info.repository["source_snapshot_sha256"])
        self.assertEqual(info.analyzer["analyzer_version"], 4)
        self.assertTrue(info.analyzer["fingerprint_matches_current"])

    def test_missing_output_rejected(self):
        self.assert_invalid_without_provider(self.tmp / "does_not_exist", "BASELINE_NOT_FOUND")

    def test_missing_evidence_manifest_rejected(self):
        b = self.fresh_baseline()
        (b / "evidence" / "EVIDENCE_MANIFEST.json").unlink()
        self.assert_invalid_without_provider(b, "EVIDENCE_MANIFEST_MISSING")

    def test_invalid_manifest_rejected(self):
        b = self.fresh_baseline()
        (b / "evidence" / "EVIDENCE_MANIFEST.json").write_text("{not json", encoding="utf-8")
        self.assert_invalid_without_provider(b, "EVIDENCE_MANIFEST_INVALID")

    def test_missing_evidence_partition_rejected(self):
        b = self.fresh_baseline()
        (b / "evidence" / "functional_flows.json").unlink()
        self.assert_invalid_without_provider(b, "EVIDENCE_PARTITION_MISSING")

    def test_corrupt_evidence_partition_rejected(self):
        b = self.fresh_baseline()
        path = b / "evidence" / "components.json"
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        self.assert_invalid_without_provider(b, "EVIDENCE_PARTITION_CORRUPT")

    def test_unsupported_schema_rejected(self):
        b = self.fresh_baseline()
        path = b / "evidence" / "EVIDENCE_MANIFEST.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["evidence_schema_version"] = "9.9"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_invalid_without_provider(b, "EVIDENCE_SCHEMA_UNSUPPORTED")

    def test_unsupported_analyzer_version_rejected(self):
        b = self.fresh_baseline()
        path = b / "_cache_v53" / "CACHE_MANIFEST.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["versions"]["analyzer_version"] = 2
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_invalid_without_provider(b, "ANALYZER_VERSION_UNSUPPORTED")

    def test_missing_ai_context_rejected(self):
        b = self.fresh_baseline()
        shutil.rmtree(b / "ai_context")
        self.assert_invalid_without_provider(b, "AI_CONTEXT_MISSING")

    def test_missing_source_identity_rejected(self):
        b = self.fresh_baseline()
        path = b / "ai_context" / "SYSTEM_CONTEXT.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["metadata"]["source_snapshot_sha256"] = ""
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_invalid_without_provider(b, "SOURCE_IDENTITY_MISSING")

    def test_missing_index_rejected(self):
        b = self.fresh_baseline()
        (b / "index" / "functional_paths.json").unlink()
        self.assert_invalid_without_provider(b, "INDEX_MISSING")

    def test_failed_deterministic_stage_rejected(self):
        b = self.fresh_baseline()
        path = b / "RUN_SUMMARY.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        next(s for s in summary["stages"] if s["stage"] == "CONTEXT")["status"] = "FAILED"
        path.write_text(json.dumps(summary), encoding="utf-8")
        self.assert_invalid_without_provider(b, "DETERMINISTIC_RUN_INCOMPLETE")

    def test_validate_baseline_raises_structured_error(self):
        with self.assertRaises(BaselineInvalid) as ctx:
            validate_baseline(self.tmp / "nope")
        self.assertEqual(ctx.exception.reason, "BASELINE_NOT_FOUND")

    def test_non_empty_output_refused_before_provider(self):
        out = self.tmp / "occupied"
        out.mkdir()
        (out / "x.txt").write_text("x", encoding="utf-8")
        provider = make_provider()
        result = run_ai_only(self.pristine, out, provider=provider)
        self.assertEqual(result.status, "AI_ONLY_OUTPUT_NOT_EMPTY")
        self.assertEqual(provider.requests, [])


class AiOnlyEndToEndTests(H1Base):
    def run_ai_only_guarded(self, baseline: Path, **kwargs):
        """Runs AI-only with every deterministic entry point booby-trapped: none may be reached."""
        from legacy_documenter.cli import full_pipeline, pipeline_stages
        import legacy_documenter.main as app

        def forbidden(*a, **k):
            raise AssertionError("deterministic analysis must not run in AI-only")
        provider = make_provider()
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(pipeline_stages, "resolve_flows", forbidden), patch.object(pipeline_stages, "export_artifacts", forbidden), \
                patch.object(pipeline_stages, "build_evidence_artifacts", forbidden), patch.object(pipeline_stages, "build_context_artifacts", forbidden), \
                patch.object(full_pipeline, "run_full_pipeline", forbidden), patch.object(app, "analyze_repository", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("real provider forbidden")):
            return run_ai_only(baseline, provider=provider, **kwargs), provider

    def test_works_without_original_source_and_without_any_deterministic_stage(self):
        self.assertFalse(self.source.exists())
        b = self.fresh_baseline()
        result, provider = self.run_ai_only_guarded(b)
        self.assertEqual(result.status, "SUCCESS", result.reason)
        self.assertTrue(result.provider_called)
        self.assertEqual(len(provider.requests), 1)
        self.assertEqual(result.proposal_count, 1)
        self.assertEqual(result.proposal_review_status, "PENDING_TECHNICAL_LEAD_REVIEW")

    def test_proposal_is_grounded_non_canonical_with_full_provenance(self):
        b = self.fresh_baseline()
        result, _ = self.run_ai_only_guarded(b)
        run_dir = result.ai_run_dir
        self.assertEqual(run_dir.parent.name, "ai_runs")
        envelope = json.loads((run_dir / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
        proposal = envelope["proposals"][0]
        self.assertEqual(proposal["status"], "READY_FOR_REVIEW")
        self.assertTrue(proposal["evidence_refs"])
        prov = json.loads((run_dir / "AI_RUN_PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertIs(prov["canonical_knowledge_produced"], False)
        self.assertIs(prov["source_scanned"], False)
        self.assertIs(prov["deterministic_baseline_modified"], False)
        for key in ("source_baseline", "evidence_manifest_sha256", "evidence_schema_version", "repository", "analyzer", "ai_context",
                    "provider", "ai_configuration", "generated_at", "proposal_review_status"):
            self.assertIn(key, prov)
        self.assertTrue(prov["provider"]["provider_id"])
        self.assertTrue(prov["provider"]["model_id"])
        self.assertEqual(prov["analyzer"]["analyzer_version"], 4)
        self.assertTrue(prov["repository"]["source_snapshot_sha256"])
        self.assertFalse((run_dir / "knowledge").exists())

    def test_deterministic_baseline_is_unchanged(self):
        b = self.fresh_baseline()
        before = tree_digest(b)
        result, _ = self.run_ai_only_guarded(b)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(tree_digest(b), before)  # everything except the new ai_runs/ directory
        self.assertTrue((b / "ai_runs").is_dir())

    def test_output_outside_baseline_leaves_baseline_byte_identical(self):
        b = self.fresh_baseline()
        out = self.tmp / "separate_ai_run"
        before = tree_digest(b, skip=())
        provider = make_provider()
        result = run_ai_only(b, out, provider=provider)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.ai_run_dir, out)
        self.assertEqual(tree_digest(b, skip=()), before)

    def test_unknown_flow_scope_does_not_call_provider(self):
        b = self.fresh_baseline()
        provider = make_provider()
        result = run_ai_only(b, flow_ids=["FLOW-DOES-NOT-EXIST"], provider=provider)
        if result.provider_called:  # an empty projection may still be valid; grounding keeps findings honest
            self.assertIn(result.status, ("SUCCESS", "INVALID_OUTPUT"))
        else:
            self.assertEqual(provider.requests, [])

    def test_review_flow_consumes_h1_proposal_and_canonical_only_after_explicit_approval(self):
        b = self.fresh_baseline()
        result, _ = self.run_ai_only_guarded(b)
        run_dir = result.ai_run_dir
        service = ApprovalService(run_dir)
        proposal_id = json.loads((run_dir / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]["proposal_id"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli_main(["review", "list", "--output", str(run_dir)])
        self.assertEqual(code, 0)
        listing = json.loads(buf.getvalue())
        self.assertEqual([p["proposal_id"] for p in listing["pending"]], [proposal_id])
        self.assertEqual(listing["canonical"], [])
        service.prepare(proposal_id, "Test Reviewer")
        self.assertFalse((run_dir / "knowledge" / "canonical").exists())
        outcome = service.decide(proposal_id, "APPROVE", "Test Reviewer", rationale="explicit human approval in test")
        self.assertIsNotNone(outcome.canonical)
        self.assertTrue(list((run_dir / "knowledge" / "canonical").glob("CAN-*.json")))
        self.assertFalse((b / "knowledge").exists())  # the deterministic baseline never receives canonical knowledge


class InterpretCliTests(H1Base):
    def test_cli_help_documents_behavior(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as ctx:
            cli_main(["interpret", "--help"])
        self.assertEqual(ctx.exception.code, 0)
        text = " ".join(buf.getvalue().split())
        for phrase in ("does NOT rescan the repository", "does NOT rebuild Evidence", "AI_ONLY_INPUT_INVALID",
                       "before any provider call", "never approved, never canonical", "NOT a source repository"):
            self.assertIn(phrase, text)

    def test_cli_invalid_baseline_exit_4_and_zero_provider(self):
        buf = io.StringIO()
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard, \
                contextlib.redirect_stdout(buf):
            code = cli_main(["interpret", str(self.tmp / "missing")])
        self.assertEqual(code, 4)
        self.assertEqual(guard.call_count, 0)
        self.assertIn(AI_ONLY_INPUT_INVALID, buf.getvalue())

    def test_cli_success_with_fake_provider(self):
        b = self.fresh_baseline()
        buf = io.StringIO()
        provider = make_provider()
        with patch.object(ai_interpretation, "_resolve_provider", return_value=provider), contextlib.redirect_stdout(buf):
            code = cli_main(["interpret", str(b)])
        self.assertEqual(code, 0)
        text = buf.getvalue()
        payload = json.loads(text[text.index("{"):])
        self.assertEqual(payload["status"], "SUCCESS")
        self.assertEqual(payload["proposal_count"], 1)
        self.assertIs(payload["source_scanned"], False)
        self.assertIs(payload["canonical_knowledge_produced"], False)
        self.assertEqual(len(provider.requests), 1)

    def test_interpret_accepts_directory_not_repository(self):
        # A source repository (no deterministic baseline) is refused, not analyzed.
        buf = io.StringIO()
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")), contextlib.redirect_stdout(buf):
            code = cli_main(["interpret", str(FIXTURE)])
        self.assertEqual(code, 4)
        self.assertIn(AI_ONLY_INPUT_INVALID, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
