"""V4.3-R7 -- Internal acceptance and real-pilot packaging: verification tests.

Covers, per `prompts/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE.md`:

1. The wiring decision R2/R3/R4 deliberately deferred (see
   `docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md` section 9) is made
   here: `full` now produces `documentation/HUMAN_DOCUMENTATION.md` +
   `documentation/flujos_humanos/*.md` (Spanish, deterministic, no AI)
   alongside `consumer_projection/` (V4.3-R6) in the same run.
2. A genuine gap this round's own verification found: `compute_output_locations`
   never listed `consumer_projection` even though `CONTEXT` always produces
   it -- fixed, and locked in here.
3. `legacy_documenter.cli.output_manifest.build_output_manifest` deterministically
   enumerates every file a run produced, for external-pilot handoff auditing.
4. `tools.v4_3_r7_build_pilot_distribution` builds a clean, runtime-only copy
   of LegacyMapper (no docs/prompts/tests/history) that can run `full`
   standalone.
5. Two acceptance-blocker corrections found in Technical Lead review of this
   round's initial state: `output-manifest` exposed as a `legacy_documenter.cli`
   subcommand so it ships inside the clean distribution (BLOQUEO 1), and every
   human-readable/product-facing document `full` writes -- including
   `RUN_SUMMARY.md`, corrected in a follow-up pass after the rest of BLOQUEO 2 --
   is Spanish by default, preserving `StageId`/status/error/path/JSON-field
   identifiers verbatim (BLOQUEO 2).

REAL_AI_RUNTIME_CALL_ALLOWED=false: every test here injects
`legacy_documenter.llm.core.FakeLLMProvider` explicitly -- no test reaches
`_resolve_provider`/`ProviderRegistry` with a real `provider_type`. No test
reaches the real IST repository (`AGENTS.md` "Legacy Source Repository");
every run is against a committed synthetic fixture.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.output_manifest import build_output_manifest
from legacy_documenter.cli.pipeline_stages import render_documentation
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"


def _rich_indexes() -> dict:
    return {
        "functional_flows": [
            {"id": "FLOW-1", "entry_point_id": "EP-1", "confidence": "confirmed", "project_sequence": ["WEB"]},
        ],
        "functional_paths": [
            {"path_id": "PATH-1", "flow_id": "FLOW-1", "entry_point_id": "EP-1", "nodes": ["DAO-1"],
             "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed",
             "evidence_refs": ["CALL-1"]},
        ],
        "entry_points": [
            {"id": "EP-1", "webform": "web\\Form1.ascx", "event": "Click", "handler": "btn_Click", "start_method": "Start"},
        ],
        "data_access": [{"id": "DAO-1", "class": "Repo", "method": "Save",
                         "operation_kind": "stored_procedure", "confidence": "confirmed"}],
        "stored_procedures": [{"id": "SP-1", "name": "PKG.SAVE", "package": "PKG", "procedure": "SAVE"}],
        "sql_operations": [], "data_parameters": [],
        "repository": {}, "solutions": [], "projects": [], "symbols": [], "logical_symbols": [],
        "calls": [], "webforms": [], "configuration": [], "dependencies": [], "functional_dependencies": [],
        "flow_summary": {}, "flow_unresolved": [], "errors": [],
    }


class HumanDocumentationWiringTests(unittest.TestCase):
    """The Spanish human-documentation surface (V4.3-R3/R4) is now wired into
    the DOCUMENTATION stage, using the exact filename/subdirectory its own
    generated Markdown already hardcodes as a relative link
    (`../HUMAN_DOCUMENTATION.md`)."""

    def test_render_documentation_writes_human_documentation_index_and_partitions(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            outcome = render_documentation(out, _rich_indexes())
            self.assertIn("HUMAN_DOCUMENTATION.md", outcome.written)
            self.assertEqual(outcome.failures, [])
            index_path = Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md"
            self.assertTrue(index_path.is_file())
            text = index_path.read_text(encoding="utf-8")
            self.assertIn("Documentación humana de flujos", text)
            partition = Path(out) / "documentation" / "flujos_humanos" / "web.md"
            self.assertTrue(partition.is_file())

    def test_index_link_to_partition_matches_the_written_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            render_documentation(out, _rich_indexes())
            index_text = (Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").read_text(encoding="utf-8")
            self.assertIn("flujos_humanos/", index_text)
            partition_text = (Path(out) / "documentation" / "flujos_humanos" / "web.md").read_text(encoding="utf-8")
            self.assertIn("../HUMAN_DOCUMENTATION.md", partition_text)

    def test_full_command_produces_human_documentation_and_consumer_projection_together(self) -> None:
        # Prompt requirement 5: "documentación humana y consumer projection en
        # fixtures" -- both surfaces from one real run over a committed fixture.
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "SUCCESS")
            self.assertTrue((Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").is_file())
            self.assertTrue((Path(out) / "consumer_projection" / "CONSUMER_PROJECTION.json").is_file())

    def test_analyze_never_gains_human_documentation(self) -> None:
        # `analyze` never calls `render_documentation` -- unchanged since V4.2-R3;
        # this wiring must not accidentally leak into the simpler command.
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            self.assertFalse((Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").exists())

    def test_human_documentation_failure_does_not_prevent_other_documents(self) -> None:
        # Same partial-failure policy as the other four renderers: a broken
        # human-documentation render must not take down WEB_ENTRY_POINTS.md/etc.
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as out, patch(
            "legacy_documenter.cli.pipeline_stages.render_human_documentation_index",
            side_effect=RuntimeError("human-doc-boom"),
        ):
            outcome = render_documentation(out, _rich_indexes())
            self.assertEqual(outcome.failures, [("HUMAN_DOCUMENTATION.md", "human-doc-boom")])
            self.assertIn("WEB_ENTRY_POINTS.md", outcome.written)
            self.assertIn("FUNCTIONAL_FLOWS.md", outcome.written)
            self.assertFalse((Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").exists())
            self.assertTrue((Path(out) / "documentation" / "WEB_ENTRY_POINTS.md").exists())


class OutputLocationsIncludeConsumerProjectionTests(unittest.TestCase):
    """Regression lock for the gap this round's own verification found."""

    def test_output_locations_lists_consumer_projection_when_context_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertIn("consumer_projection", result.output_locations)
        self.assertIn("ai_context", result.output_locations)

    def test_console_summary_mentions_consumer_projection_location(self) -> None:
        from legacy_documenter.cli.run_summary_presenter import render_console_summary
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            console = render_console_summary(result, str(FIXTURE), Path(out))
        self.assertIn("consumer_projection", console)


class OutputManifestTests(unittest.TestCase):
    """`build_output_manifest` deterministically enumerates a run's own output tree."""

    def test_raises_for_a_missing_directory(self) -> None:
        with self.assertRaises(FileNotFoundError):
            build_output_manifest("/does/not/exist/at/all")

    def test_lists_every_file_with_size_and_hash(self) -> None:
        import hashlib
        with tempfile.TemporaryDirectory() as out:
            (Path(out) / "a.txt").write_text("hello", encoding="utf-8")
            (Path(out) / "sub").mkdir()
            (Path(out) / "sub" / "b.txt").write_text("world", encoding="utf-8")
            manifest = build_output_manifest(out)
        self.assertEqual(manifest["file_count"], 2)
        self.assertEqual(manifest["total_bytes"], len(b"hello") + len(b"world"))
        by_path = {entry["path"]: entry for entry in manifest["files"]}
        self.assertEqual(by_path["a.txt"]["sha256"], hashlib.sha256(b"hello").hexdigest())
        self.assertEqual(by_path["sub/b.txt"]["sha256"], hashlib.sha256(b"world").hexdigest())

    def test_paths_use_forward_slashes_and_are_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            (Path(out) / "z.txt").write_text("1", encoding="utf-8")
            (Path(out) / "a.txt").write_text("2", encoding="utf-8")
            manifest = build_output_manifest(out)
        self.assertEqual([e["path"] for e in manifest["files"]], ["a.txt", "z.txt"])

    def test_excludes_its_own_manifest_filename(self) -> None:
        from legacy_documenter.cli.output_manifest import MANIFEST_FILENAME
        with tempfile.TemporaryDirectory() as out:
            (Path(out) / MANIFEST_FILENAME).write_text("{}", encoding="utf-8")
            (Path(out) / "real.json").write_text("{}", encoding="utf-8")
            manifest = build_output_manifest(out)
        self.assertEqual([e["path"] for e in manifest["files"]], ["real.json"])

    def test_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            first = build_output_manifest(out)
            second = build_output_manifest(out)
        self.assertEqual(first, second)

    def test_manifest_over_a_real_run_covers_human_documentation_and_consumer_projection(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            manifest = build_output_manifest(out)
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("documentation/HUMAN_DOCUMENTATION.md", paths)
        self.assertIn("consumer_projection/CONSUMER_PROJECTION.json", paths)


class PilotDistributionTests(unittest.TestCase):
    """The clean, runtime-only distribution excludes dev-only content and can run `full` standalone."""

    def test_distribution_contains_only_main_py_legacy_documenter_and_requirements_copilot(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            build_distribution(dist)
            top_level = sorted(p.name for p in Path(dist).iterdir())
        self.assertEqual(top_level, ["legacy_documenter", "main.py", "requirements-copilot.txt"])

    def test_distribution_carries_requirements_copilot_with_the_optional_dependency(self) -> None:
        # V4.3 pre-closure distribution dependency follow-up: the clean pilot
        # distribution must transport the optional COPILOT dependency
        # declaration itself, so the pilot operator installs it from inside
        # the distribution instead of relying on their global Python
        # environment already having the SDK.
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            build_distribution(dist)
            content = (Path(dist) / "requirements-copilot.txt").read_text(encoding="utf-8")
        self.assertIn("github-copilot-sdk>=1.0.14", content)

    def test_distribution_excludes_dev_only_directories(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            build_distribution(dist)
            for dev_only in ("docs", "prompts", "tests", "codex", "output", "result_codex", "tools"):
                self.assertFalse((Path(dist) / dev_only).exists())

    def test_distribution_excludes_dev_only_root_files(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            build_distribution(dist)
            for dev_only in ("PROJECT_STATE.json", "README.md", "AGENTS.md", "CLAUDE.md"):
                self.assertFalse((Path(dist) / dev_only).exists())

    def test_distribution_excludes_pycache(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            build_distribution(dist)
            self.assertEqual(list(Path(dist).rglob("__pycache__")), [])

    def test_refuses_to_copy_into_a_non_empty_destination(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            (Path(dist) / "existing.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                build_distribution(dist)

    def test_build_distribution_return_value_lists_every_copied_file(self) -> None:
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist:
            copied = build_distribution(dist)
        self.assertIn("main.py", copied)
        self.assertIn("legacy_documenter/main.py", copied)
        self.assertIn("requirements-copilot.txt", copied)
        self.assertEqual(copied, sorted(copied))

    def test_clean_distribution_runs_full_standalone_against_a_fixture(self) -> None:
        # The real smoke test: copy the runtime-only distribution to a fresh
        # directory, `cd` into it, and run `python main.py full ...` with no
        # access to this development repository's docs/tests/tools at all.
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist, tempfile.TemporaryDirectory() as out:
            build_distribution(dist)
            result = subprocess.run(
                [sys.executable, "main.py", "full", str(FIXTURE), "--output", out],
                cwd=dist, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(out) / "consumer_projection" / "CONSUMER_PROJECTION.json").is_file())
            self.assertTrue((Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").is_file())
            summary = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "SUCCESS")

    def test_clean_distribution_builds_output_manifest_via_its_own_cli_subcommand(self) -> None:
        # V4.3-R7 BLOQUEO 1: `V4_3_REAL_PILOT_INSTRUCTIONS.md` previously told the
        # pilot operator to run `python -m tools.v4_3_r7_build_output_manifest`,
        # a script that lives under `tools/` -- excluded from this same clean
        # distribution by design (see the exclusion tests above). This is the
        # fix: `output-manifest` is a `legacy_documenter.cli` subcommand, so it
        # ships inside the distribution and needs no access back to this
        # development repository. Verified end to end via subprocess, exactly
        # like `full` above: `full` then `output-manifest`, both from inside the
        # copied distribution, with no development-repository file on
        # PYTHONPATH or in the working directory.
        from tools.v4_3_r7_build_pilot_distribution import build_distribution
        with tempfile.TemporaryDirectory() as dist, tempfile.TemporaryDirectory() as out:
            build_distribution(dist)
            full_result = subprocess.run(
                [sys.executable, "main.py", "full", str(FIXTURE), "--output", out],
                cwd=dist, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(full_result.returncode, 0, full_result.stderr)

            manifest_result = subprocess.run(
                [sys.executable, "main.py", "output-manifest", out],
                cwd=dist, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            manifest_path = Path(out) / "OUTPUT_MANIFEST.json"
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in manifest["files"]}
            self.assertIn("documentation/HUMAN_DOCUMENTATION.md", paths)
            self.assertIn("consumer_projection/CONSUMER_PROJECTION.json", paths)
            self.assertNotIn("OUTPUT_MANIFEST.json", paths)


class OutputManifestCliSubcommandTests(unittest.TestCase):
    """V4.3-R7 BLOQUEO 1: `output-manifest` is a `legacy_documenter.cli` subcommand
    (`parser.py`/`router.py`), not only a `tools/` script -- so it ships inside a
    clean, runtime-only pilot distribution. See `PilotDistributionTests
    .test_clean_distribution_builds_output_manifest_via_its_own_cli_subcommand`
    for the end-to-end subprocess verification from an actual copied
    distribution; these are the faster in-process unit-level checks.
    """

    def test_parser_accepts_the_output_manifest_command(self) -> None:
        from legacy_documenter.cli.parser import build_parser
        args = build_parser().parse_args(["output-manifest", "some/dir"])
        self.assertEqual(args.command, "output-manifest")
        self.assertEqual(args.output_dir, "some/dir")

    def test_router_writes_the_manifest_and_reports_success(self) -> None:
        from argparse import Namespace
        from legacy_documenter.cli.router import EXIT_SUCCESS, route
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            exit_code, result = route(Namespace(command="output-manifest", output_dir=out), analyze_repository=None)
            self.assertEqual(exit_code, EXIT_SUCCESS)
            self.assertEqual(result.status.value, "SUCCESS")
            self.assertTrue((Path(out) / "OUTPUT_MANIFEST.json").is_file())

    def test_router_propagates_file_not_found_for_a_missing_output_dir(self) -> None:
        from argparse import Namespace
        from legacy_documenter.cli.router import route
        with self.assertRaises(FileNotFoundError):
            route(Namespace(command="output-manifest", output_dir="/does/not/exist/at/all"), analyze_repository=None)


class SpanishByDefaultProductDocumentationTests(unittest.TestCase):
    """V4.3-R7 BLOQUEO 2: every human-readable/product-facing technical document
    `full` writes is Spanish by default -- verified over a real `full` run's
    actual on-disk output, not just in isolation against each renderer. Technical
    identifiers, paths, JSON field names and status values (e.g. `confirmed`/
    `unresolved`) are never translated; only prose/headers are.
    """

    def test_full_run_writes_every_mandatory_document_in_spanish(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status.value, "SUCCESS")
            doc_dir = Path(out) / "documentation"

            def text(name: str) -> str:
                return (doc_dir / name).read_text(encoding="utf-8")

            self.assertIn("# Resumen del proyecto", text("PROJECT_OVERVIEW.md"))
            self.assertIn("# Estructura de soluciones", text("SOLUTION_STRUCTURE.md"))
            self.assertIn("# Dependencias de proyectos", text("PROJECT_DEPENDENCIES.md"))
            self.assertIn("# Mapa de WebForms", text("WEBFORMS_MAP.md"))
            self.assertIn("# Resumen de configuración", text("CONFIGURATION_SUMMARY.md"))
            self.assertIn("# Puntos de entrada web", text("WEB_ENTRY_POINTS.md"))
            self.assertIn("# Flujos funcionales", text("FUNCTIONAL_FLOWS.md"))
            self.assertIn("# Acceso a base de datos", text("DATABASE_ACCESS.md"))
            self.assertIn("# Hallazgos no resueltos", text("UNRESOLVED_FINDINGS.md"))
            self.assertIn("# Advertencias de análisis", text("ANALYSIS_WARNINGS.md"))
            self.assertIn("# Documentación de LegacyMapper", text("README.md"))
            # V4.3-R3/R4: HUMAN_DOCUMENTATION.md was already Spanish before this round.
            self.assertIn("Documentación humana", text("HUMAN_DOCUMENTATION.md"))

    def test_technical_identifiers_are_never_translated(self) -> None:
        # Field/status values traced from `indexes` -- and the machine-readable
        # `index/*.json` root path itself -- must reach the Spanish documents
        # untouched: only surrounding prose is translated.
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            readme = (Path(out) / "documentation" / "README.md").read_text(encoding="utf-8")
            self.assertIn("`confirmed`", readme)
            self.assertIn("`unresolved`", readme)
            self.assertIn("index/*.json", readme)
            db_doc = (Path(out) / "documentation" / "DATABASE_ACCESS.md").read_text(encoding="utf-8")
            self.assertIn("`stored_procedure`", db_doc)
            self.assertIn("`sql_operation`", db_doc)

    def test_flat_english_renderers_are_not_part_of_full_output(self) -> None:
        # The pre-existing flat renderers (functional_flows(), database_access(),
        # unresolved_findings(), web_entry_points(), project_dependencies()) stay
        # English -- they are not human-readable/product-facing `full`/`analyze`
        # output, only kept for existing English-language test/API callers that
        # want one complete, unpartitioned document (see each renderer's own
        # docstring). This locks in that `full` itself never reaches them.
        from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            functional_flows_doc = (Path(out) / "documentation" / "FUNCTIONAL_FLOWS.md").read_text(encoding="utf-8")
        self.assertNotIn("# Functional Flows", functional_flows_doc)
        self.assertTrue(hasattr(TechnicalDocumentationRenderer, "functional_flows"))


class RunSummaryMarkdownSpanishByDefaultTests(unittest.TestCase):
    """V4.3-R7 BLOQUEO 2 follow-up correction: `RUN_SUMMARY.md` is generated by the
    product, designed for human reading, and is exactly what
    `V4_3_REAL_PILOT_INSTRUCTIONS.md` tells an external pilot operator to consult
    to diagnose a `PARTIAL`/`FAILED` run -- it is human-readable/product-facing,
    so it is now Spanish by default, like every other such document. Verified
    over real `full` runs, not just `render_markdown_summary` in isolation.
    `RUN_SUMMARY.json` -- the machine-readable contract -- is untouched.
    """

    def test_run_summary_md_has_spanish_prose_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("# Resumen de ejecución de LegacyMapper", markdown)
        self.assertIn("## Etapas", markdown)
        self.assertIn("## Ubicaciones de salida", markdown)
        self.assertIn("## Próxima acción", markdown)
        self.assertIn("Documentación técnica generada correctamente.", markdown)

    def test_stage_ids_and_statuses_are_never_translated(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
        # StageId values (technical identifiers) and StageStatus/RunStatus
        # values (enums) must appear exactly as `StageId`/`StageStatus` define
        # them -- never translated, never altered.
        for stage_id in ("SCAN", "EXTRACTION", "EXPORT", "CONTEXT", "DOCUMENTATION", "FINAL_SUMMARY"):
            self.assertIn(f"| {stage_id} | SUCCESS |", markdown)
        self.assertIn("**SUCCESS**", markdown)

    def test_error_category_and_message_are_preserved_verbatim(self) -> None:
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as out, patch(
            "legacy_documenter.cli.full_pipeline.stages.export_artifacts",
            side_effect=OSError("disk full"),
        ):
            run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("OSError: disk full", markdown)

    def test_run_summary_json_is_structurally_unchanged(self) -> None:
        # RUN_SUMMARY.json is machine-readable; this correction must not touch
        # its contract in any way -- same field set, same English `next_action`.
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        expected_fields = {
            "command", "status", "stages", "ai_requested", "ai_invoked", "proposal_count",
            "proposal_review_status", "canonical_knowledge_produced", "technical_lead_approval",
            "next_action", "output_locations",
        }
        self.assertEqual(set(payload.keys()), expected_fields)
        self.assertEqual(payload["next_action"], "Technical documentation generated successfully.")
        self.assertEqual(payload["next_action"], result.next_action)
        self.assertEqual(payload["status"], "SUCCESS")

    def test_success_partial_failed_still_render_correctly_in_markdown_and_json(self) -> None:
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(result.status.value, "SUCCESS")
        self.assertIn("**SUCCESS**", markdown)
        self.assertEqual(payload["status"], "SUCCESS")

        with tempfile.TemporaryDirectory() as out, patch(
            "legacy_documenter.cli.full_pipeline.stages.export_artifacts",
            side_effect=OSError("disk full"),
        ):
            result = run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(result.status.value, "FAILED")
        self.assertIn("**FAILED**", markdown)
        self.assertIn("El análisis no produjo el mínimo de salida útil.", markdown)
        self.assertEqual(payload["status"], "FAILED")

    def test_output_locations_still_include_consumer_projection_in_both_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertIn("consumer_projection", result.output_locations)
        self.assertIn("consumer_projection", payload["output_locations"])
        self.assertIn("- `consumer_projection`", markdown)


class AiFailureStillDoesNotAffectHumanDocumentationTests(unittest.TestCase):
    """Extends V4.3-R6's own invariant test to the newly-wired human documentation surface."""

    def test_ai_failure_leaves_human_documentation_intact(self) -> None:
        failing_provider = FakeLLMProvider(
            ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}),
            forced_status="PROVIDER_ERROR",
        )
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=failing_provider)
            self.assertTrue((Path(out) / "documentation" / "HUMAN_DOCUMENTATION.md").is_file())
            self.assertEqual(result.status.value, "PARTIAL")


if __name__ == "__main__":
    unittest.main()
