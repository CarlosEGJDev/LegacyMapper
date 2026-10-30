"""Post-V5 pre-H5 Gate A: portability, runtime independence, strict input validation, optional AI, path/resource contract.

Directed tests only. No real provider is ever resolved or called: provider seams are test doubles, and the clean-room
run uses an unknown provider type / a missing SDK so nothing can reach a network.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.main import main as cli_main
from legacy_documenter.utils import path_contract as pc

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "legacy_documenter"
FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"
MODULE_SOURCE = "def f():\n    return 1\n"

#: Artifacts whose bytes legitimately carry the physical source/output location or wall-clock data (V5.9-R2 contract:
#: the scan summary root is informative, not identity; its partition hash is therefore the only manifest value that moves).
MACHINE_SPECIFIC = {
    "ai_context/SYSTEM_CONTEXT.json", "evidence/EVIDENCE_MANIFEST.json", "evidence/scan_summary.json",
    "index/repository.json", "_cache_v53/CACHE_MANIFEST.json", "_cache_v53/RUN_METRICS.json",
}
ABSOLUTE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|file:///|/Users/|AppData|Temp[\\/]claude|scratchpad", re.I)


def run_cli(argv: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    previous = Path.cwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli_main(argv)
    finally:
        os.chdir(previous)
    return code, out.getvalue(), err.getvalue()


def payload_of(stdout: str) -> dict:
    """`interpret` prints a one-line AI notice before its JSON payload."""
    return json.loads(stdout[stdout.index("{"):])


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def make_source(parent: Path, name: str = "src") -> Path:
    src = parent / name
    src.mkdir(parents=True)
    (src / "m.py").write_text(MODULE_SOURCE, encoding="utf-8")
    return src


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gatea_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)


class InvalidSourceIsNeverSuccessTests(Workspace):
    """UX-01: invalid input stops before scanner, analyzer and provider; no output, no SUCCESS."""

    def _guarded_run(self, argv):
        with mock.patch("legacy_documenter.scanner.repository_scanner.RepositoryScanner.scan") as scan, \
                mock.patch("legacy_documenter.cli.pipeline_stages.extract_repository") as extract, \
                mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider, \
                mock.patch("legacy_documenter.orchestration.ai_interpretation.run_ai_interpretation") as ai:
            result = run_cli(argv)
        return result, scan, extract, provider, ai

    def test_nonexistent_source_is_rejected_before_scanner_analyzer_and_provider(self):
        out = self.tmp / "out"
        (code, stdout, stderr), scan, extract, provider, ai = self._guarded_run(
            ["full", str(self.tmp / "missing"), "--output", str(out), "--allow-ai-interpretation"])
        self.assertEqual(code, 4)                                    # the existing FAILED exit code, not a new scheme
        payload = json.loads(stderr)
        self.assertEqual((payload["status"], payload["code"]), ("PATH_CONTRACT_VIOLATION", pc.SOURCE_NOT_FOUND))
        self.assertNotIn("SUCCESS", stdout + stderr)
        for seam in (scan, extract, provider, ai):
            seam.assert_not_called()
        self.assertFalse(out.exists())                               # no partial fake output

    def test_analyze_rejects_the_same_way(self):
        out = self.tmp / "out"
        (code, _, stderr), scan, extract, provider, _ = self._guarded_run(["analyze", str(self.tmp / "missing"), "--output", str(out)])
        self.assertEqual((code, json.loads(stderr)["code"]), (4, pc.SOURCE_NOT_FOUND))
        scan.assert_not_called()
        self.assertFalse(out.exists())

    def test_source_that_is_a_file_is_rejected(self):
        file = self.tmp / "a.py"
        file.write_text(MODULE_SOURCE)
        (code, _, stderr), scan, *_ = self._guarded_run(["full", str(file), "--output", str(self.tmp / "out")])
        self.assertEqual((code, json.loads(stderr)["code"]), (4, pc.SOURCE_NOT_DIRECTORY))
        scan.assert_not_called()

    def test_unreadable_source_is_rejected(self):
        src = make_source(self.tmp)
        with mock.patch("legacy_documenter.utils.path_contract.os.scandir", side_effect=PermissionError("denied")):
            with self.assertRaises(pc.PathContractError) as ctx:
                pc.validate_source_directory(src)
        self.assertEqual(ctx.exception.code, pc.SOURCE_NOT_READABLE)

    def test_output_that_is_a_file_or_under_a_file_is_rejected(self):
        src = make_source(self.tmp)
        blocker = self.tmp / "blocker"
        blocker.write_text("x")
        for target, code in ((blocker, pc.OUTPUT_NOT_DIRECTORY), (blocker / "child", pc.OUTPUT_NOT_DIRECTORY)):
            with self.assertRaises(pc.PathContractError) as ctx:
                pc.validate_source_and_output(src, target)
            self.assertEqual(ctx.exception.code, code)

    def test_unwritable_output_is_rejected(self):
        src = make_source(self.tmp)
        with mock.patch("legacy_documenter.utils.path_contract._probe_writable", return_value=False):
            with self.assertRaises(pc.PathContractError) as ctx:
                pc.validate_source_and_output(src, self.tmp / "a" / "b")
        self.assertEqual(ctx.exception.code, pc.OUTPUT_NOT_WRITABLE)

    def test_contradictory_layouts_are_rejected(self):
        src = make_source(self.tmp)
        for output in (src, src / "out", self.tmp):           # output == source, inside source, source inside output
            with self.assertRaises(pc.PathContractError, msg=str(output)) as ctx:
                pc.validate_source_and_output(src, output)
            self.assertEqual(ctx.exception.code, pc.LAYOUT_CONTRADICTORY)

    def test_missing_output_parents_are_creatable_and_not_created_by_validation(self):
        src = make_source(self.tmp)
        out = self.tmp / "deep" / "er" / "out"
        self.assertEqual(pc.validate_source_and_output(src, out)[1], out.resolve())
        self.assertFalse((self.tmp / "deep").exists())

    def test_library_entry_points_enforce_the_contract(self):
        from legacy_documenter.cli.execution_model import RunStatus
        from legacy_documenter.cli.full_pipeline import run_full_pipeline
        result = run_full_pipeline(self.tmp / "missing", self.tmp / "out", None, 12)
        self.assertEqual(result.status, RunStatus.FAILED)
        self.assertFalse((self.tmp / "out").exists())


class PathShapesTests(Workspace):
    """Spaces, Unicode, relative, trailing separator, "." and a different drive all behave like absolute paths."""

    def _ok(self, src_arg, out_arg, cwd):
        code, stdout, stderr = run_cli(["full", src_arg, "--output", out_arg], cwd=cwd)
        self.assertEqual(code, 0, stdout + stderr)
        self.assertTrue((cwd / out_arg).resolve().joinpath("RUN_SUMMARY.json").is_file() if not Path(out_arg).is_absolute()
                        else Path(out_arg, "RUN_SUMMARY.json").is_file())

    def test_spaces_and_unicode(self):
        src = make_source(self.tmp / "my docs ünï ñ", "repo with spaces")
        self._ok(str(src), str(self.tmp / "out put ü" / "o"), self.tmp)

    def test_relative_source_and_output_from_an_unrelated_cwd(self):
        make_source(self.tmp, "src")
        self._ok("src", "rel_out", self.tmp)

    def test_trailing_separator_and_dot_source(self):
        src = make_source(self.tmp, "src")
        self._ok(str(src) + os.sep, str(self.tmp / "o1"), self.tmp)
        self._ok(".", str(self.tmp / "o2"), src)                       # "." cwd source, output elsewhere

    @unittest.skipUnless(os.name == "nt", "drive letters are a Windows concern")
    def test_different_drive_pair_is_not_a_contradiction(self):
        self.assertFalse(pc._same_or_inside(Path("C:\\a\\b"), Path("D:\\a")))
        self.assertFalse(pc._same_or_inside(Path("D:\\a"), Path("C:\\a")))
        self.assertTrue(pc._same_or_inside(Path("C:\\A\\b"), Path("c:\\a")))     # case differences


class PackagedResourcesTests(Workspace):
    def test_builtin_templates_live_inside_the_package(self):
        from legacy_documenter.behavior import template as T
        root = pc.builtin_templates_root()
        self.assertEqual(root, PACKAGE / "templates")
        self.assertTrue((root / "human" / "default" / "template.yaml").is_file())
        self.assertFalse((REPO / "templates").exists(), "the checkout-root templates/ must not be a runtime dependency")
        self.assertEqual(T.template_roots(None), [root])

    def test_default_template_resolves_from_another_cwd_and_external_override_never_mutates_it(self):
        from legacy_documenter.behavior import template as T
        before = tree(pc.builtin_templates_root())
        external = self.tmp / "ext templates"
        shutil.copytree(pc.builtin_templates_root() / "human" / "default", external / "human" / "default")
        manifest = external / "human" / "default" / "template.yaml"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('template_version: "1.0.0"', 'template_version: "7.7.7"'), encoding="utf-8")
        previous = Path.cwd()
        os.chdir(self.tmp)
        try:
            self.assertEqual(T.discover("human/default").manifest["template_version"], "1.0.0")
            self.assertEqual(T.discover("human/default", external).manifest["template_version"], "7.7.7")
        finally:
            os.chdir(previous)
        self.assertEqual(tree(pc.builtin_templates_root()), before)

    def test_no_hardcoded_development_paths_in_runtime_string_literals(self):
        needles = re.compile(r"[A-Za-z]:\\|[A-Za-z]:/(?!/)|\\Users\\|/Users/|AppData|Temp\\claude|scratchpad|PruebasLegacyMapper|dev\\LegacyMapper|source\\IST|cgalianj", re.I)
        offenders = []
        for path in sorted(PACKAGE.rglob("*.py")):
            tree_ = ast.parse(path.read_text(encoding="utf-8"))
            docstrings = {id(n.body[0].value) for n in ast.walk(tree_)
                          if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body
                          and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)
                          and isinstance(n.body[0].value.value, str)}
            for node in ast.walk(tree_):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
                    if needles.search(node.value):
                        offenders.append(f"{path.relative_to(REPO).as_posix()}:{node.lineno}: {node.value[:60]!r}")
        # Windows drive-letter regex also matches harmless text such as "SYMMETRIC:"; keep only real path-like hits.
        offenders = [o for o in offenders if not re.search(r"[A-Za-z]{2,}:\\|[A-Za-z]{2,}:/", o.split(": ", 1)[1]) or "Users" in o or "AppData" in o]
        self.assertEqual(offenders, [])

    def test_runtime_never_reads_cwd_or_checkout_relative_resources(self):
        for path in sorted(PACKAGE.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("getcwd", text, path.name)
            self.assertNotIn("Path.cwd", text, path.name)
            self.assertNotIn("parents[2]", text, path.name)


class ProviderOptionalTests(Workspace):
    def _baseline(self) -> Path:
        out = self.tmp / "baseline"
        code, _, err = run_cli(["full", str(make_source(self.tmp)), "--output", str(out)])
        self.assertEqual(code, 0, err)
        return out

    def test_deterministic_commands_never_touch_a_provider(self):
        baseline = self._baseline()
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create", side_effect=AssertionError("provider touched")) as create, \
                mock.patch("legacy_documenter.llm.registry.resolve_provider", side_effect=AssertionError("provider touched")), \
                mock.patch.dict(sys.modules, {"copilot": None, "openai": None}):
            for command in ("docs", "visuals", "deliver"):
                code, stdout, stderr = run_cli([command, str(baseline)])
                self.assertEqual(code, 0, command + stderr)
                self.assertEqual(json.loads(stdout)["provider_calls" if command != "visuals" else "status"] in (0, "SUCCESS"), True)
        create.assert_not_called()

    def _interpret_subprocess(self, baseline: Path, *, block_sdk: bool, provider: str | None) -> subprocess.CompletedProcess:
        """The production resolution path, in a child process (the in-process suite guard blocks `_resolve_provider`)."""
        env = {k: v for k, v in os.environ.items() if k not in {"LEGACYMAPPER_LLM_PROVIDER", "COPILOT_CLI_PATH"}}
        env.update(PYTHONPATH=str(REPO), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
        if provider:
            env["LEGACYMAPPER_LLM_PROVIDER"] = provider
        code = chr(10).join(["import sys", "sys.modules['copilot'] = None" if block_sdk else "",
                          "from legacy_documenter.main import main", "raise SystemExit(main(['interpret', sys.argv[1]]))"])
        return subprocess.run([sys.executable, "-B", "-c", code, str(baseline)], cwd=self.tmp, env=env,
                              capture_output=True, text=True, encoding="utf-8", timeout=300)

    def test_interpret_without_provider_sdk_fails_cleanly_and_leaves_the_baseline_intact(self):
        baseline = self._baseline()
        before = tree(baseline)
        result = self._interpret_subprocess(baseline, block_sdk=True, provider=None)
        payload = payload_of(result.stdout)
        self.assertEqual(result.returncode, 1)                       # existing contract: AI stage failed over a valid baseline
        self.assertEqual(payload["reason"], "PROVIDER_UNAVAILABLE")
        self.assertFalse(payload["provider_called"])
        self.assertEqual(payload["proposal_count"], 0)
        after = tree(baseline)
        self.assertEqual({k: v for k, v in after.items() if not k.startswith("ai_runs/")}, before)   # only the isolated AI run dir is new
        self.assertFalse(any("proposals" in k for k in after))       # nothing invented

    def test_unknown_provider_type_is_a_controlled_configuration_error(self):
        result = self._interpret_subprocess(self._baseline(), block_sdk=False, provider="NOT_INSTALLED")
        self.assertEqual((result.returncode, payload_of(result.stdout)["reason"]), (1, "PROVIDER_CONFIGURATION_ERROR"))

    def test_explicit_provider_executable_path_reaches_the_sdk_untouched(self):
        """LegacyMapper neither sets nor searches a provider location: the SDK's documented COPILOT_CLI_PATH is honoured."""
        from legacy_documenter.llm import LLMRequest, ProviderConfig
        from legacy_documenter.llm.providers.copilot import CopilotProvider
        seen = {}

        class StubClient:
            def __init__(self, **_kwargs):
                seen["cli_path"] = os.environ.get("COPILOT_CLI_PATH")

            async def start(self):
                raise RuntimeError("stub stops here")

        stub = mock.MagicMock(CopilotClient=StubClient)
        explicit = str(self.tmp / "tools" / "copilot-cli")
        request = LLMRequest.__new__(LLMRequest)
        for attr, value in (("request_id", "R1"), ("model_id", None), ("timeout_s", 1), ("output_contract", None),
                            ("context_package_id", None), ("source_snapshot", None)):
            object.__setattr__(request, attr, value) if hasattr(type(request), "__dataclass_fields__") else setattr(request, attr, value)
        provider = CopilotProvider(ProviderConfig("COPILOT", "copilot-local", "m"))
        with mock.patch.dict(os.environ, {"COPILOT_CLI_PATH": explicit}), mock.patch.dict(sys.modules, {"copilot": stub}):
            import asyncio
            response = asyncio.run(provider._generate(request, None))
        self.assertEqual(seen["cli_path"], explicit)
        self.assertNotEqual(response.status, "SUCCESS")


class CleanRoomTests(unittest.TestCase):
    """A runtime copy (package + main.py only) in a read-only-marked folder, run from an unrelated cwd with absolute paths."""

    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp(prefix="legacymapper-cleanroom-"))
        cls.runtime = cls.base / "runtime dir"
        shutil.copytree(PACKAGE, cls.runtime / "legacy_documenter", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(REPO / "main.py", cls.runtime / "main.py")
        cls.source = cls.base / "src ünï" / "repo"
        shutil.copytree(FIXTURE, cls.source)
        cls.output = cls.base / "out put" / "o"
        cls.cwd = cls.base / "elsewhere"
        cls.cwd.mkdir()
        for root in (cls.runtime, cls.source):                      # read-only runtime and read-only source; only output is writable
            for path in root.rglob("*"):
                if path.is_file():
                    os.chmod(path, stat.S_IREAD)
        cls.runtime_before, cls.source_before = tree(cls.runtime), tree(cls.source)
        cls.env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "LEGACYMAPPER_LLM_PROVIDER": "NOT_INSTALLED", "PYTHONUTF8": "1"}
        cls.env.pop("COPILOT_CLI_PATH", None)
        cls.env.pop("PYTHONPATH", None)
        cls.results: dict[str, subprocess.CompletedProcess] = {}
        for name, argv in (("full", ["full", cls.source, "--output", cls.output]), ("docs", ["docs", cls.output]),
                           ("visuals", ["visuals", cls.output]), ("deliver", ["deliver", cls.output]),
                           ("interpret", ["interpret", cls.output])):
            cls.results[name] = cls.invoke(argv)

    @classmethod
    def invoke(cls, argv):
        return subprocess.run([sys.executable, "-B", "-X", "utf8", str(cls.runtime / "main.py"), *map(str, argv)],
                              cwd=cls.cwd, env=cls.env, capture_output=True, text=True, encoding="utf-8", timeout=600)

    @classmethod
    def tearDownClass(cls):
        for path in cls.base.rglob("*"):
            if path.is_file():
                try:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
        shutil.rmtree(cls.base, ignore_errors=True)

    def test_deterministic_pipeline_runs_from_an_unrelated_cwd(self):
        for name in ("full", "docs", "visuals", "deliver"):
            result = self.results[name]
            self.assertEqual(result.returncode, 0, f"{name}: {result.stdout[-400:]} {result.stderr[-400:]}")
        deliver = json.loads(self.results["deliver"].stdout)
        self.assertEqual((deliver["provider_calls"], deliver["source_scanned"]), (0, False))
        self.assertTrue(len(deliver["pdfs"]) >= 1)

    def test_interpret_is_a_controlled_error_when_the_provider_is_unconfigured(self):
        result = self.results["interpret"]
        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload_of(result.stdout)["reason"], "PROVIDER_CONFIGURATION_ERROR")

    def test_read_only_runtime_and_source_are_never_written(self):
        self.assertEqual(tree(self.runtime), self.runtime_before)
        self.assertEqual(tree(self.source), self.source_before)
        self.assertEqual([p for p in self.runtime.rglob("__pycache__")], [])

    def test_human_package_has_no_absolute_or_development_paths(self):
        package = self.output / "human_package"
        self.assertTrue((package / "index.html").is_file())
        checked = 0
        for path in package.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".html", ".svg", ".json", ".css", ".md", ".txt"}:
                checked += 1
                text = path.read_text(encoding="utf-8", errors="replace")
                self.assertIsNone(ABSOLUTE.search(text), f"{path.relative_to(package)}: {ABSOLUTE.search(text)}")
                self.assertNotIn(str(self.base), text)
        self.assertGreater(checked, 10)
        for html in package.rglob("*.html"):
            for target in re.findall(r'(?:href|src)="([^"#]+)"', html.read_text(encoding="utf-8")):
                if re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
                    self.fail(f"{html.name}: external/absolute link {target}")
                self.assertTrue((html.parent / target).exists(), f"{html.name}: broken relative link {target}")

    def test_pdfs_embed_everything_and_reference_no_local_files(self):
        pdfs = list((self.output / "human_package").rglob("*.pdf"))
        self.assertTrue(pdfs)
        for pdf in pdfs:
            data = pdf.read_bytes()
            self.assertTrue(data.startswith(b"%PDF"))
            self.assertIsNone(re.search(rb"/URI\s*\(\s*file:", data))
            self.assertNotIn(str(self.base).encode("utf-8", "replace"), data)


class DeterminismAcrossLocationsTests(Workspace):
    def test_same_source_in_two_locations_differs_only_in_declared_machine_specific_files(self):
        outs, roots = [], []
        for name in ("A dir", "Ünï cödé B"):
            src = self.tmp / name / "src"
            shutil.copytree(FIXTURE, src)
            out = self.tmp / name / "out"
            code, _, err = run_cli(["full", str(src), "--output", str(out)])
            self.assertEqual(code, 0, err)
            outs.append(out)
            roots.append(src)
        a, b = tree(outs[0]), tree(outs[1])
        self.assertEqual(set(a), set(b))
        differing = {k for k in a if a[k] != b[k]}
        self.assertLessEqual(differing, MACHINE_SPECIFIC, differing - MACHINE_SPECIFIC)
        evidence_a = json.loads((outs[0] / "evidence/EVIDENCE_MANIFEST.json").read_text("utf-8"))
        evidence_b = json.loads((outs[1] / "evidence/EVIDENCE_MANIFEST.json").read_text("utf-8"))
        moved = {k for k in evidence_a["partition_sha256"] if evidence_a["partition_sha256"][k] != evidence_b["partition_sha256"][k]}
        self.assertEqual(moved, {"scan_summary"})                    # identity partitions (and every stable ID) are path-independent


if __name__ == "__main__":
    unittest.main()
