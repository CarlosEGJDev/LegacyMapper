"""Post-V5 H2: human documentation by audience (executive / functional / technical_overview).

Networkless and deterministic. Every provider is a Fake grounded in persisted Evidence; `docs` never resolves one.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.documentation_v52.audience import UNRESOLVED, classify_layer
from legacy_documenter.documentation_v52.config import ConfigRegistry
from legacy_documenter.documentation_v52.engine import AUDIENCE_PROFILES, DEFAULT_PROFILES
from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration import ai_interpretation
from legacy_documenter.orchestration.ai_only import run_ai_only
from legacy_documenter.review.service import ApprovalService
from tests.test_post_v5_h1_ai_only import make_provider

FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"
LINK = re.compile(r"\]\(([^)#]+)(?:#[^)]*)?\)")


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def run_docs(baseline: Path, out: Path, *extra: str) -> tuple[int, dict]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli_main(["docs", str(baseline), "--output", str(out), *extra])
    text = buf.getvalue()
    return code, json.loads(text[text.index("{"):])


def tree_digest(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def read(root: Path, profile: str) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted((root / "documentation_v52" / profile).rglob("*.md")))


class H2Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="h2_"))
        source = cls.tmp / "source"
        shutil.copytree(FIXTURE, source)
        cls.baseline = cls.tmp / "baseline"
        assert quiet(run_full_pipeline, source, cls.baseline, [], 12).status.value == "SUCCESS"
        shutil.rmtree(source)  # no H2 test has the original source tree
        cls.before = tree_digest(cls.baseline)
        cls.out = cls.tmp / "docs"
        code, cls.summary = run_docs(cls.baseline, cls.out)
        assert code == 0, cls.summary

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def files(self, profile: str) -> list[str]:
        return sorted(p.relative_to(self.out / "documentation_v52" / profile).as_posix()
                      for p in (self.out / "documentation_v52" / profile).rglob("*.md"))


class ProfileContractTests(H2Base):
    def test_three_profiles_exist_and_are_opt_in(self):
        registry = ConfigRegistry()
        for pid in AUDIENCE_PROFILES:
            profile = registry.profile(pid)
            self.assertEqual(profile.output_dir, pid)
            self.assertEqual(profile.language, "es")
        self.assertEqual(AUDIENCE_PROFILES, ("executive", "functional", "technical_overview"))
        self.assertTrue(set(AUDIENCE_PROFILES).isdisjoint(DEFAULT_PROFILES))  # `full` output is unchanged

    def test_same_evidence_three_different_abstraction_levels(self):
        sizes = {p: self.summary["profiles"][p]["files"] for p in AUDIENCE_PROFILES}
        self.assertEqual(self.files("executive"), ["README.md", "areas.md"])
        self.assertIn("processes.md", self.files("functional"))
        self.assertTrue(any(f.startswith("areas/") for f in self.files("functional")))
        self.assertTrue(any(f.startswith("modules/") for f in self.files("technical_overview")))
        self.assertLess(sizes["executive"], sizes["functional"])
        self.assertEqual(len({tuple(self.files(p)) for p in AUDIENCE_PROFILES}), 3)

    def test_executive_hides_method_class_and_file_detail(self):
        text = read(self.out, "executive")
        for forbidden in ("btnSave_Click", "Page_Load", "btnNotify_Click", "CustomerPage.aspx", ".vb", "SAVE_CUSTOMER"):
            self.assertNotIn(forbidden, text)
        self.assertIn("Resumen ejecutivo", text)

    def test_functional_surfaces_flows_screens_data_integrations(self):
        text = read(self.out, "functional")
        self.assertIn("CustomerPage.aspx", text)            # screens / entry points
        self.assertIn("PKG_CUSTOMER.SAVE_CUSTOMER", text)   # data reached by an observable process
        self.assertIn("Conexiones a base de datos", text)   # integrations
        self.assertIn("Procesos observables", text)
        self.assertNotIn("btnSave_Click", text)            # no method-level story

    def test_technical_overview_surfaces_projects_layers_dependencies(self):
        layers = (self.out / "documentation_v52" / "technical_overview" / "layers.md").read_text(encoding="utf-8")
        for project in ("Web", "CustomerService", "CustomerRepository"):
            self.assertIn(project, layers)
        self.assertIn("Presentación", layers)
        self.assertIn("Acceso a datos", layers)
        self.assertTrue((self.out / "documentation_v52" / "technical_overview" / "dependencies.md").is_file())
        self.assertNotIn("btnSave_Click", read(self.out, "technical_overview"))
        # deep technical evidence stays reachable: the project page names the existing developer document
        self.assertIn("documentation_v52/developer/modules/Web.md", (self.out / "documentation_v52" / "technical_overview" / "modules" / "Web.md").read_text(encoding="utf-8"))
        self.assertTrue((self.baseline / "documentation_v52" / "developer" / "modules" / "Web.md").is_file())


class EpistemicStatusTests(H2Base):
    def test_layer_rules_are_structural_and_labelled_inferred(self):
        base = {"screens": 0, "project_type": "", "data_ops": 0, "incoming_flows": 0}
        self.assertEqual(classify_layer({**base, "screens": 2}, False)[0::2], ("presentation", "INFERRED"))
        self.assertEqual(classify_layer({**base, "data_ops": 1}, False)[0::2], ("data_access", "INFERRED"))
        self.assertEqual(classify_layer({**base, "incoming_flows": 1}, False)[0::2], ("logic", "INFERRED"))
        self.assertEqual(classify_layer(base, True)[0::2], ("logic", "INFERRED"))
        self.assertEqual(classify_layer(base, False)[0::2], ("unclassified", UNRESOLVED))  # never guessed

    def test_statuses_visible_in_generated_docs(self):
        text = read(self.out, "technical_overview")
        self.assertIn("Inferido (regla estructural)", text)
        self.assertIn("confirmado por evidencia", text)
        self.assertIn("no resuelto", text.lower())
        self.assertIn("No resuelto", read(self.out, "executive"))

    def test_layer_assignment_follows_evidence_not_names(self):
        page = lambda n: (self.out / "documentation_v52" / "technical_overview" / "modules" / f"{n}.md").read_text(encoding="utf-8")
        self.assertIn("Presentación (pantallas)", page("Web"))
        self.assertIn("Acceso a datos", page("CustomerRepository"))
        self.assertIn("Lógica / servicios", page("CustomerService"))

    def test_areas_are_real_solutions_with_identified_projects_only(self):
        evidence_projects = {p["name"] for p in json.loads((self.baseline / "index" / "projects.json").read_text(encoding="utf-8"))}
        areas = (self.out / "documentation_v52" / "functional" / "areas.md").read_text(encoding="utf-8")
        solutions = {s["name"] for s in json.loads((self.baseline / "index" / "solutions.json").read_text(encoding="utf-8"))}
        self.assertTrue(any(name in areas for name in solutions))
        area_page = next((self.out / "documentation_v52" / "functional" / "areas").glob("*.md")).read_text(encoding="utf-8")
        trace = area_page.split("## Trazabilidad técnica")[1]
        listed = set(re.findall(r"^\| (\w+) \|", trace, flags=re.M)) - {"Proyecto"}
        self.assertTrue(listed and listed <= evidence_projects, listed)  # no invented project membership


class KnowledgePrecedenceTests(H2Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        copy = cls.tmp / "ai_baseline"
        shutil.copytree(cls.baseline, copy)
        provider = make_provider()
        cls.ai = run_ai_only(copy, provider=provider)
        assert cls.ai.status == "SUCCESS", cls.ai.reason
        cls.ai_dir = cls.ai.ai_run_dir

    def docs_with_ai(self, name: str) -> Path:
        out = self.tmp / name
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("docs must never resolve a provider")) as guard:
            code, _ = run_docs(self.baseline, out, "--ai-run", str(self.ai_dir))
        self.assertEqual(code, 0)
        self.assertEqual(guard.call_count, 0)
        return out

    def test_docs_work_without_any_ai_run(self):
        text = read(self.out, "functional") + read(self.out, "executive")
        self.assertNotIn("Interpretaciones de IA", text)
        self.assertFalse((self.out / "documentation_v52" / "functional" / "interpretation.md").exists())

    def test_ai_proposal_is_never_rendered_as_confirmed(self):
        out = self.docs_with_ai("docs_ai")
        statement = json.loads((self.ai_dir / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]["statement"]
        executive = (out / "documentation_v52" / "executive" / "README.md").read_text(encoding="utf-8")
        self.assertIn(statement, executive)
        ai_part = executive.split("## Interpretaciones de IA (no aprobadas)")[1]
        self.assertIn(statement, ai_part)
        self.assertIn("Interpretación de IA (no aprobada)", ai_part)
        self.assertNotIn(statement, executive.split("## Interpretaciones de IA (no aprobadas)")[0])  # not among the facts
        self.assertNotIn("Canónico (aprobado", executive)
        functional = (out / "documentation_v52" / "functional" / "interpretation.md").read_text(encoding="utf-8")
        self.assertIn("Interpretación de IA (no aprobada)", functional)
        self.assertIn("no es un hecho", functional)

    def test_canonical_is_distinguishable_from_raw_ai_proposal(self):
        copy = self.tmp / "ai_run_approved"
        shutil.copytree(self.ai_dir, copy)
        proposal_id = json.loads((copy / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]["proposal_id"]
        service = ApprovalService(copy)
        service.prepare(proposal_id, "Test Reviewer")
        service.decide(proposal_id, "APPROVE", "Test Reviewer", rationale="explicit human approval in test")
        out = self.tmp / "docs_canonical"
        code, summary = run_docs(self.baseline, out, "--ai-run", str(copy))
        self.assertEqual(code, 0)
        self.assertEqual((summary["canonical_records_shown"], summary["ai_proposals_shown"]), (1, 0))  # approved proposal moves out of the AI list
        executive = (out / "documentation_v52" / "executive" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Conocimiento aprobado por una persona", executive)
        self.assertIn("Canónico (aprobado por una persona)", executive)
        self.assertNotIn("Interpretación de IA (no aprobada)", executive)
        self.assertIn("Test Reviewer", executive)

    def test_rejected_proposal_is_not_listed_as_interpretation(self):
        copy = self.tmp / "ai_run_rejected"
        shutil.copytree(self.ai_dir, copy)
        proposal_id = json.loads((copy / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]["proposal_id"]
        service = ApprovalService(copy)
        service.prepare(proposal_id, "Test Reviewer")
        service.decide(proposal_id, "REJECT", "Test Reviewer", rationale="not supported")
        code, summary = run_docs(self.baseline, self.tmp / "docs_rejected", "--ai-run", str(copy))
        self.assertEqual((code, summary["ai_proposals_shown"], summary["canonical_records_shown"]), (0, 0, 0))


class NavigationAndDeterminismTests(H2Base):
    def test_navigation_links_resolve(self):
        broken = []
        for md in (self.out / "documentation_v52").rglob("*.md"):
            for target in LINK.findall(md.read_text(encoding="utf-8")):
                if target.startswith(("http:", "https:", "mailto:")):
                    continue
                if not (md.parent / target).resolve().exists():
                    broken.append((md.name, target))
        self.assertEqual(broken, [])

    def test_deterministic_rerun_is_byte_identical(self):
        again = self.tmp / "docs_again"
        code, _ = run_docs(self.baseline, again)
        self.assertEqual(code, 0)
        self.assertEqual(tree_digest(again), tree_digest(self.out))

    def test_baseline_unchanged_and_source_not_required(self):
        self.assertFalse((self.tmp / "source").exists())
        self.assertEqual(tree_digest(self.baseline), self.before)
        self.assertFalse(self.summary["baseline_modified"])
        self.assertFalse(self.summary["source_scanned"])
        self.assertEqual(self.summary["provider_calls"], 0)

    def test_no_deterministic_stage_runs(self):
        from legacy_documenter.cli import full_pipeline, pipeline_stages

        def forbidden(*a, **k):
            raise AssertionError("deterministic analysis must not run in docs")
        with patch.object(pipeline_stages, "scan_repository", forbidden), patch.object(pipeline_stages, "extract_repository", forbidden), \
                patch.object(pipeline_stages, "resolve_flows", forbidden), patch.object(full_pipeline, "run_full_pipeline", forbidden), \
                patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")):
            code, _ = run_docs(self.baseline, self.tmp / "docs_guarded")
        self.assertEqual(code, 0)

    def test_existing_default_profiles_are_untouched(self):
        # `full` still renders only general/developer; audience docs live apart from the baseline documentation.
        self.assertEqual(sorted(p.name for p in (self.baseline / "documentation_v52").iterdir() if p.is_dir()), ["developer", "general"])

    def test_invalid_baseline_is_refused_without_writing(self):
        out = self.tmp / "docs_invalid"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli_main(["docs", str(self.tmp / "missing"), "--output", str(out)])
        self.assertEqual(code, 4)
        self.assertIn("DOCS_INPUT_INVALID", buf.getvalue())
        self.assertFalse(out.exists())

    def test_single_audience_selection(self):
        out = self.tmp / "docs_exec_only"
        code, summary = run_docs(self.baseline, out, "--audience", "executive")
        self.assertEqual(code, 0)
        self.assertEqual(list(summary["profiles"]), ["executive"])
        self.assertFalse((out / "documentation_v52" / "functional").exists())

    def test_cli_help_documents_behavior(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            cli_main(["docs", "--help"])
        text = " ".join(buf.getvalue().split())
        for phrase in ("does NOT rescan", "NEVER calls an AI provider", "executive, functional, technical_overview", "clearly labelled" if False else "labelled apart"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
