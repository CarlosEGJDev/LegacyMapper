"""Post-H5 hygiene contract: no active external fixture/workspace dependency, profile coverage, workspace relocation.

Synthetic inputs only. No provider is resolved and no real corpus is analysed.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from legacy_documenter import devtest
from legacy_documenter.main import main as cli_main

REPO = Path(__file__).resolve().parents[1]
THIS = Path(__file__).name

# Machine/workspace specific locations that active code and tests must never embed.
FORBIDDEN = re.compile(r"PruebasLegacyMapper|[\\/]Users[\\/]cgalianj|\\Users\\cgalianj|source[\\/]IST", re.I)

# Tests that legitimately *name* these strings as negative needles or as fake example data.
NEEDLE_ALLOWED = {
    "test_post_v5_gate_a_portability.py",   # forbidden-needle regex
    "test_v3_r7_2_4.py", "test_v3_r8_4_approval.py",  # assertNotIn("source\\IST_40", ...)
    "test_v4_2_r7_1_real_pilot_findings_correction.py", "test_v4_2_r8_documentation_at_scale.py",  # fake testuser data
    "test_v5_1_r2_normalized_evidence_core.py",  # docstring describing a manual validation
}


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli_main(argv)
    return code, out.getvalue()


class ProfileCoverageTests(unittest.TestCase):
    def test_every_test_module_belongs_to_a_capability_profile(self):
        self.assertEqual(devtest.unassigned_modules(), [])

    def test_full_profile_selects_every_module(self):
        self.assertEqual(devtest.modules_for("FULL"), devtest.available_modules())

    def test_every_profile_is_documented_and_non_empty(self):
        for name, doc in devtest.PROFILE_DOCS.items():
            self.assertTrue(all(doc[k] for k in ("purpose", "external", "usage", "duration")), name)
            self.assertTrue(devtest.modules_for(name), name)

    def test_changed_area_mapping(self):
        pp = devtest.profiles_for_paths
        self.assertIn("BEHAVIOR", pp(["legacy_documenter/behavior/wireframe.py"]))
        self.assertIn("VISUALS", pp(["legacy_documenter/visuals/x.py"]))
        self.assertIn("PACKAGING", pp(["legacy_documenter/deliver/x.py"]))
        self.assertEqual({"PROVIDER", "AI_KNOWLEDGE"} - set(pp(["legacy_documenter/llm/core.py"])), set())
        self.assertEqual({"CORE", "DISTRIBUTION"} - set(pp(["legacy_documenter/utils/path_contract.py"])), set())
        self.assertIn("FULL", pp(["legacy_documenter/versions.py"]))

    def test_h5_regression_module_stays_active(self):
        self.assertIn("test_post_v5_h5_real_ist_scale", devtest.modules_for("PACKAGING"))


class NoExternalDependencyTests(unittest.TestCase):
    def _offenders(self, paths):
        found = []
        for path in paths:
            if path.name == THIS or path.name in NEEDLE_ALLOWED:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for number, line in enumerate(text.splitlines(), 1):
                if FORBIDDEN.search(line):
                    found.append(f"{path.relative_to(REPO).as_posix()}:{number}")
        return found

    def test_no_active_test_embeds_a_workspace_or_developer_path(self):
        self.assertEqual(self._offenders(sorted((REPO / "tests").glob("*.py"))), [])

    def test_runtime_and_tools_embed_no_workspace_or_developer_path(self):
        paths = sorted((REPO / "legacy_documenter").rglob("*.py")) + sorted((REPO / "tools").rglob("*.py"))
        self.assertEqual(self._offenders(paths), [])

    def test_operations_docs_use_placeholders_only(self):
        for doc in sorted((REPO / "docs" / "OPERATIONS").glob("*.md")) + [REPO / "docs" / "ARCHITECTURE" / "CURRENT_ARCHITECTURE.md"]:
            text = doc.read_text(encoding="utf-8")
            self.assertFalse(re.search(r"\b[A-Z]:\\", text), doc.name)
            self.assertFalse(FORBIDDEN.search(text), doc.name)

    def test_external_real_ist_test_is_configured_by_environment(self):
        text = (REPO / "tests" / "test_v4_3_r3a_r1_selection_packing_quality_correction.py").read_text(encoding="utf-8")
        self.assertIn("LEGACYMAPPER_REAL_IST_BASELINE", text)


class PromptHygieneTests(unittest.TestCase):
    def test_current_prompt_entry_point_declares_no_active_prompt(self):
        text = (REPO / "prompts" / "CURRENT" / "README.md").read_text(encoding="utf-8")
        for needle in ("POST_V5 CLOSED", "H1-H5 CLOSED", "V6 NOT_STARTED", "no active implementation prompt"):
            self.assertIn(needle, text)

    def test_closed_prompts_live_only_under_archive(self):
        prompts = REPO / "prompts"
        self.assertEqual([p.name for p in prompts.glob("*.md")], [])
        self.assertEqual(sorted(p.name for p in prompts.iterdir() if p.is_dir()), ["CURRENT", "archive"])
        self.assertEqual([p.name for p in (prompts / "CURRENT").iterdir()], ["README.md"])

    def test_canonical_documents_exist(self):
        for rel in ("PROJECT_STATE.json", "README.md", "docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md",
                    "docs/OPERATIONS/RESUME_LEGACYMAPPER.md", "docs/OPERATIONS/WORKSPACE_CONTRACT.md",
                    "docs/OPERATIONS/TESTING_GUIDE.md"):
            self.assertTrue((REPO / rel).is_file(), rel)


class WorkspaceRelocationTests(unittest.TestCase):
    """A generated baseline is movable: docs/visuals/deliver work after it is relocated to a new path
    (with spaces and Unicode), from an unrelated working directory."""

    def test_relocated_baseline_still_serves_projections(self):
        base = Path(tempfile.mkdtemp(prefix="hyg_"))
        self.addCleanup(shutil.rmtree, base, True)
        src = base / "fuente ñ"
        src.mkdir()
        (src / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        first = base / "work A" / "baseline"
        code, _ = _run(["full", str(src), "--output", str(first)])
        self.assertEqual(code, 0)
        second = base / "área nueva ü" / "work B" / "baseline"
        second.parent.mkdir(parents=True)
        shutil.move(str(first), str(second))
        self.assertFalse(first.exists())
        elsewhere = base / "otro cwd"
        elsewhere.mkdir()
        previous = Path.cwd()
        try:
            os.chdir(elsewhere)
            for command in ("docs", "visuals", "deliver"):
                code, out = _run([command, str(second)])
                self.assertEqual(code, 0, f"{command}: {out[-300:]}")
        finally:
            os.chdir(previous)
        payload = json.loads(out)
        self.assertEqual((payload["provider_calls"], payload["source_scanned"]), (0, False))


if __name__ == "__main__":
    unittest.main()
