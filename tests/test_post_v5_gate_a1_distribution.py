"""Post-V5 pre-H5 Gate A.1: real distribution/installability, generic behavior defaults, controlled output-manifest failure.

The distribution tests build a wheel from a *copy* of `pyproject.toml` + `legacy_documenter/` (the checkout is never
polluted with build/ or egg-info), install it into a throw-away venv and run it from an unrelated cwd with a scrubbed
environment (no PYTHONPATH, no COPILOT_CLI_PATH, no provider SDK). They need a PEP 517 build backend: when it cannot be
obtained (offline machine without setuptools) they are skipped with an explicit reason, never silently passed.
No real AI provider is ever called.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from pathlib import Path
from types import SimpleNamespace

from legacy_documenter.behavior import prototype as P
from legacy_documenter.main import main as cli_main

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "legacy_documenter"
FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"
REQUIRED_RESOURCES = (
    "legacy_documenter/templates/human/default/template.yaml",
    "legacy_documenter/templates/human/default/document.html",
    "legacy_documenter/templates/human/default/styles.css",
    "legacy_documenter/templates/human/default/pdf.css",
    "legacy_documenter/templates/ai/README.md",
    "legacy_documenter/documentation_v52/defaults/i18n/es.json",
    "legacy_documenter/documentation_v52/defaults/noise/default.json",
)


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli_main(argv)
    return code, out.getvalue(), err.getvalue()


def payload_of(text: str) -> dict:
    return json.loads(text[text.index("{"):])


def view_project(name: str, *items: str) -> dict:
    return {"name": name, "path": f"{name}\\{name}.vbproj", "content_items": list(items), "compile_items": []}


def fake_context(projects: list[dict], solutions: list[dict]):
    return SimpleNamespace(source={"projects": projects, "solutions": solutions})


class GenericBehaviorSelectionTests(unittest.TestCase):
    """A1-02: no developer project names; 0 -> error, 1 -> deterministic (recorded), >1 -> explicit selection required."""

    def test_no_ist_specific_literals_in_production_code(self):
        needles = ("WebPREPrevencion", "slnPREPrevencion", "IST_40", "PREPrevencion")
        offenders = []
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file() and path.suffix in {".py", ".json", ".html", ".css", ".yaml", ".md"} and "__pycache__" not in path.parts:
                text = path.read_text(encoding="utf-8", errors="replace")
                offenders += [f"{path.relative_to(REPO).as_posix()}: {n}" for n in needles if n in text]
        self.assertEqual(offenders, [])
        tree = ast.parse((PACKAGE / "behavior" / "prototype.py").read_text(encoding="utf-8"))
        defaults = {a.arg: d.value for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef) and fn.name == "build"
                    for a, d in zip(fn.args.args[-len(fn.args.defaults):], fn.args.defaults) if isinstance(d, ast.Constant)}
        self.assertIsNone(defaults.get("project"))
        self.assertIsNone(defaults.get("solution"))

    def test_cli_has_no_default_project_or_solution(self):
        import argparse
        seen = {}
        original = argparse.ArgumentParser.add_argument

        def spy(self, *names, **kw):
            if names and names[0] in ("--project", "--solution"):
                seen[names[0]] = kw.get("default", "<unset>")
            return original(self, *names, **kw)
        argparse.ArgumentParser.add_argument = spy
        try:
            with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
                P.main(["--help"])
        finally:
            argparse.ArgumentParser.add_argument = original
        self.assertEqual(seen, {"--project": None, "--solution": None})

    def test_single_candidate_is_selected_deterministically_and_recorded(self):
        ctx = fake_context([view_project("Web", "Home.aspx"), view_project("Lib")], [{"name": "Sln", "path": "Sln.sln", "projects": ["Web\\Web.vbproj", "Lib\\Lib.vbproj"]}])
        project, solution, record = P.select_project_and_solution(ctx, None, None)
        self.assertEqual((project, solution), ("Web", "Sln"))
        self.assertEqual(record, {"project": "deterministic_single_candidate", "solution": "deterministic_single_candidate"})

    def test_explicit_choice_is_honoured_and_recorded(self):
        ctx = fake_context([view_project("A", "a.ascx"), view_project("B", "b.ascx")],
                           [{"name": "S1", "projects": ["A\\A.vbproj"]}, {"name": "S2", "projects": ["A\\A.vbproj"]}])
        project, solution, record = P.select_project_and_solution(ctx, "A", "S2")
        self.assertEqual((project, solution, record), ("A", "S2", {"project": "explicit", "solution": "explicit"}))

    def test_several_candidates_require_explicit_selection(self):
        ctx = fake_context([view_project("B", "b.ascx"), view_project("A", "a.aspx")], [{"name": "S", "projects": ["A\\A.vbproj", "B\\B.vbproj"]}])
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(ctx, None, None)
        self.assertEqual((raised.exception.code, raised.exception.candidates), ("PROJECT_SELECTION_REQUIRED", ["A", "B"]))
        ctx = fake_context([view_project("A", "a.ascx")], [{"name": "S1", "projects": ["A\\A.vbproj"]}, {"name": "S2", "projects": ["A\\A.vbproj"]}])
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(ctx, None, None)
        self.assertEqual((raised.exception.code, raised.exception.candidates), ("SOLUTION_SELECTION_REQUIRED", ["S1", "S2"]))

    def test_zero_candidates_and_unknown_names_are_controlled_errors(self):
        none = fake_context([view_project("Lib")], [])
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(none, None, None)
        self.assertEqual(raised.exception.code, "NO_BEHAVIORAL_PROJECT_CANDIDATES")
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(none, "Missing", None)
        self.assertEqual(raised.exception.code, "PROJECT_NOT_FOUND")
        unsolved = fake_context([view_project("Web", "x.aspx")], [])
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(unsolved, None, None)
        self.assertEqual(raised.exception.code, "NO_SOLUTION_CANDIDATES")
        with self.assertRaises(P.SelectionError) as raised:
            P.select_project_and_solution(unsolved, "Web", "Nope")
        self.assertEqual(raised.exception.code, "SOLUTION_NOT_FOUND_FOR_PROJECT")

    def test_prototype_cli_reports_selection_errors_without_traceback(self):
        tmp = Path(tempfile.mkdtemp(prefix="gatea1_"))
        self.addCleanup(shutil.rmtree, tmp, True)
        code, _, err = run_cli(["full", str(FIXTURE), "--output", str(tmp / "o")])
        self.assertEqual(code, 0, err)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exit_code = P.main([str(tmp / "o"), "--source", str(FIXTURE), "--output", str(tmp / "b"), "--no-pdf"])
        self.assertEqual(exit_code, 4)
        self.assertEqual(json.loads(out.getvalue())["code"], "NO_BEHAVIORAL_PROJECT_CANDIDATES")
        self.assertFalse((tmp / "b").exists())


class OutputManifestControlledFailureTests(unittest.TestCase):
    """A1-03: expected invalid input is a controlled CLI failure on the existing exit-code contract, never a traceback."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gatea1_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_nonexistent_directory(self):
        code, out, err = run_cli(["output-manifest", str(self.tmp / "missing")])
        self.assertEqual(code, 4)
        payload = json.loads(err)
        self.assertEqual((payload["status"], payload["code"]), ("PATH_CONTRACT_VIOLATION", "OUTPUT_MANIFEST_INPUT_NOT_FOUND"))
        self.assertNotIn("Traceback", out + err)
        self.assertFalse((self.tmp / "missing").exists())

    def test_path_is_a_file_and_nothing_is_written(self):
        file = self.tmp / "f.txt"
        file.write_text("x")
        code, _, err = run_cli(["output-manifest", str(file)])
        self.assertEqual((code, json.loads(err)["code"]), (4, "OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY"))
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["f.txt"])

    def test_valid_directory_still_writes_the_manifest(self):
        (self.tmp / "a.txt").write_text("a")
        code, out, _ = run_cli(["output-manifest", str(self.tmp)])
        self.assertEqual(code, 0)
        self.assertIn("OUTPUT_MANIFEST.json", out)
        self.assertTrue((self.tmp / "OUTPUT_MANIFEST.json").is_file())

    def test_other_public_commands_fail_through_contracts_for_a_missing_baseline(self):
        for command in ("docs", "visuals", "deliver", "interpret"):
            code, out, err = run_cli([command, str(self.tmp / "missing")])
            self.assertEqual(code, 4, command)
            self.assertNotIn("Traceback", out + err, command)
            self.assertIn("INVALID", payload_of(out)["status"], command)


def _build_distribution(work: Path) -> tuple[Path | None, str]:
    """Wheel built from a copy of pyproject.toml + the package. Returns (wheel or None, reason when not buildable)."""
    source = work / "src"
    source.mkdir()
    shutil.copy(REPO / "pyproject.toml", source / "pyproject.toml")
    shutil.copytree(PACKAGE, source / "legacy_documenter", ignore=shutil.ignore_patterns("__pycache__"))
    dist = work / "dist"
    result = subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", str(dist), str(source)],
                            capture_output=True, text=True, timeout=600)
    wheels = list(dist.glob("legacymapper-*.whl")) if dist.exists() else []
    if result.returncode != 0 or not wheels:
        return None, (result.stderr or result.stdout)[-400:]
    return wheels[0], ""


class InstalledDistributionTests(unittest.TestCase):
    """A1-01: the product installed from a wheel into an isolated venv, run outside the checkout, with no provider."""

    @classmethod
    def setUpClass(cls):
        cls.work = Path(tempfile.mkdtemp(prefix="legacymapper-dist-"))
        cls.wheel, reason = _build_distribution(cls.work)
        if cls.wheel is None:
            shutil.rmtree(cls.work, ignore_errors=True)
            raise unittest.SkipTest(f"no PEP 517 build backend available on this machine: {reason}")
        cls.venv_dir = cls.work / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(cls.venv_dir)
        scripts = cls.venv_dir / ("Scripts" if os.name == "nt" else "bin")
        cls.python = scripts / ("python.exe" if os.name == "nt" else "python")
        cls.console = scripts / ("legacymapper.exe" if os.name == "nt" else "legacymapper")
        install = subprocess.run([str(cls.python), "-m", "pip", "install", "--no-deps", "--no-index", "-q", str(cls.wheel)],
                                 capture_output=True, text=True, timeout=600)
        assert install.returncode == 0, install.stderr[-500:]
        cls.cwd = cls.work / "elsewhere ünï"
        cls.cwd.mkdir()
        cls.env = {k: v for k, v in os.environ.items()
                   if k not in {"PYTHONPATH", "COPILOT_CLI_PATH", "PYTHONHOME", "VIRTUAL_ENV"} and not k.startswith("LEGACYMAPPER_")}
        cls.env["PYTHONUTF8"] = "1"
        cls.source = cls.work / "my repo ñ" / "src"
        shutil.copytree(FIXTURE, cls.source)
        cls.output = cls.work / "out dir" / "o"
        cls.results = {}
        cls.results["full"] = cls.run_cli("full", cls.source, "--output", cls.output)
        for command in ("docs", "visuals", "deliver"):
            cls.results[command] = cls.run_cli(command, cls.output)
        cls.results["interpret"] = cls.run_cli("interpret", cls.output)

    @classmethod
    def run_cli(cls, *argv, console: bool = False):
        head = [str(cls.console)] if console else [str(cls.python), "-m", "legacy_documenter"]
        return subprocess.run(head + [str(a) for a in argv], cwd=cls.cwd, env=cls.env, capture_output=True, text=True,
                              encoding="utf-8", timeout=900)

    @classmethod
    def run_python(cls, code: str, *argv):
        return subprocess.run([str(cls.python), "-c", code, *map(str, argv)], cwd=cls.cwd, env=cls.env,
                              capture_output=True, text=True, encoding="utf-8", timeout=300)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "work", Path("nonexistent")), ignore_errors=True)

    # -- artifact integrity --------------------------------------------------------------------------------
    def test_wheel_contains_required_resources_and_nothing_else_unwanted(self):
        names = set(zipfile.ZipFile(self.wheel).namelist())
        for resource in REQUIRED_RESOURCES:
            self.assertIn(resource, names)
        self.assertEqual([n for n in names if n.split("/")[0] not in {"legacy_documenter"} and not n.startswith("legacymapper-")], [])
        for unwanted in ("tests/", "tools/", "docs/", "output/", "prompts/", "codex/"):
            self.assertFalse(any(n.startswith(unwanted) for n in names), unwanted)
        self.assertFalse(any(n.endswith(".pyc") or "__pycache__" in n for n in names))
        self.assertLess(self.wheel.stat().st_size, 5 * 1024 * 1024)
        entry = zipfile.ZipFile(self.wheel).read(next(n for n in names if n.endswith("entry_points.txt"))).decode()
        self.assertIn("legacymapper = legacy_documenter.main:main", entry)

    def test_source_tree_declares_every_runtime_resource_kind_as_package_data(self):
        """Fails when a new non-Python resource kind appears under the package without being declared in pyproject.toml."""
        declared = set(re.findall(r'\*\*/\*\.(\w+)', (REPO / "pyproject.toml").read_text(encoding="utf-8")))
        present = {p.suffix.lstrip(".") for p in PACKAGE.rglob("*") if p.is_file() and p.suffix not in {".py", ".pyc", ""} and "__pycache__" not in p.parts}
        self.assertLessEqual(present, declared, "undeclared package-data kinds")

    # -- installed behaviour -------------------------------------------------------------------------------
    def test_runtime_comes_from_site_packages_never_from_the_checkout(self):
        result = self.run_python(
            "import legacy_documenter as m, sys\n"
            "from legacy_documenter.utils.path_contract import builtin_templates_root, runtime_resource_root\n"
            "print(m.__file__); print(builtin_templates_root()); print(runtime_resource_root())")
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in result.stdout.splitlines():
            self.assertIn("site-packages", line)
            self.assertFalse(Path(line).resolve().is_relative_to(REPO), line)

    def test_help_and_both_entry_points(self):
        for console in (False, True):
            result = self.run_cli("--help", console=console)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("full", result.stdout)

    def test_deterministic_pipeline_from_unrelated_cwd_with_no_provider(self):
        for name in ("full", "docs", "visuals", "deliver"):
            result = self.results[name]
            self.assertEqual(result.returncode, 0, f"{name}: {result.stdout[-300:]} {result.stderr[-300:]}")
        deliver = payload_of(self.results["deliver"].stdout)
        self.assertEqual((deliver["provider_calls"], deliver["source_scanned"]), (0, False))
        self.assertTrue((self.output / "human_package" / "index.html").is_file())
        self.assertTrue(list((self.output / "human_package").rglob("*.pdf")))

    def test_interpret_without_provider_is_a_controlled_failure(self):
        result = self.results["interpret"]
        self.assertEqual(result.returncode, 1)
        payload = payload_of(result.stdout)
        self.assertEqual((payload["reason"], payload["provider_called"]), ("PROVIDER_UNAVAILABLE", False))
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_inputs_fail_through_contracts_when_installed(self):
        missing = self.run_cli("full", self.work / "no such repo", "--output", self.work / "o2")
        self.assertEqual(missing.returncode, 4)
        self.assertEqual(json.loads(missing.stderr)["code"], "SOURCE_PATH_NOT_FOUND")
        manifest = self.run_cli("output-manifest", self.work / "no such dir")
        self.assertEqual((manifest.returncode, json.loads(manifest.stderr)["code"]), (4, "OUTPUT_MANIFEST_INPUT_NOT_FOUND"))
        for result in (missing, manifest):
            self.assertNotIn("Traceback", result.stderr)

    def test_builtin_template_and_external_template_dir_after_install(self):
        external = self.work / "ext tpl"
        shutil.copytree(PACKAGE / "templates" / "human" / "default", external / "human" / "default")
        manifest = external / "human" / "default" / "template.yaml"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('template_version: "1.0.0"', 'template_version: "9.9.9"'), encoding="utf-8")
        code = ("import sys\nfrom legacy_documenter.behavior.template import discover\n"
                "print(discover('human/default').manifest['template_version'])\n"
                "print(discover('human/default', sys.argv[1]).manifest['template_version'])\n"
                "print(discover('human/default').manifest['template_version'])")
        result = self.run_python(code, external)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(), ["1.0.0", "9.9.9", "1.0.0"])

    def test_installed_behavior_cli_has_no_default_project(self):
        result = subprocess.run([str(self.python), "-m", "legacy_documenter.behavior.prototype", str(self.output), "--source", str(self.source),
                                 "--output", str(self.work / "b"), "--no-pdf"], cwd=self.cwd, env=self.env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["code"], "NO_BEHAVIORAL_PROJECT_CANDIDATES")
        self.assertNotIn("Traceback", result.stderr)


class CheckoutCompatibilityTests(unittest.TestCase):
    def test_python_main_py_still_works(self):
        tmp = Path(tempfile.mkdtemp(prefix="gatea1_"))
        self.addCleanup(shutil.rmtree, tmp, True)
        result = subprocess.run([sys.executable, "-X", "utf8", str(REPO / "main.py"), "full", str(FIXTURE), "--output", str(tmp / "o")],
                                cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr[-300:])
        self.assertTrue((tmp / "o" / "RUN_SUMMARY.json").is_file())

    def test_python_dash_m_matches_main_py(self):
        result = subprocess.run([sys.executable, "-m", "legacy_documenter", "--help"], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr[-300:])
        self.assertIn("full", result.stdout)


if __name__ == "__main__":
    unittest.main()
