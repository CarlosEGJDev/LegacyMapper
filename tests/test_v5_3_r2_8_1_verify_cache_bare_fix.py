"""R2.8.1: bare verification preserves repository arguments; no real AI calls."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from legacy_documenter.cli import router
from legacy_documenter.cli.execution_model import RunResult, RunStatus
from legacy_documenter.cli.parser import build_parser, normalize_cache_argv


ROOT = Path(__file__).resolve().parents[1]


class BareVerifyCacheParserTests(unittest.TestCase):
    def parse(self, *argv):
        return build_parser().parse_args(["full", *argv])

    def test_absent_flag_defaults_to_fast(self):
        self.assertEqual(self.parse("repo").verify_cache, "fast")

    def test_bare_at_end(self):
        args = self.parse("repo", "--output", "out", "--verify-cache")
        self.assertEqual((args.repository, args.output, args.verify_cache), ("repo", "out", "hash"))

    def test_bare_before_repository(self):
        args = self.parse("--verify-cache", "repo", "--output", "out")
        self.assertEqual((args.repository, args.output, args.verify_cache), ("repo", "out", "hash"))

    def test_bare_before_another_flag(self):
        args = self.parse("--verify-cache", "--verbose", "repo")
        self.assertTrue(args.verbose)
        self.assertEqual((args.repository, args.verify_cache), ("repo", "hash"))

    def test_bare_between_repository_and_output_option(self):
        # full has one positional only; --output's value is an option argument.
        args = self.parse("repo", "--verify-cache", "--output", "out")
        self.assertEqual((args.repository, args.output, args.verify_cache), ("repo", "out", "hash"))

    def test_paths_named_like_levels_are_not_consumed(self):
        for repository in ("hash", "fast"):
            with self.subTest(repository=repository):
                args = self.parse("--verify-cache", repository)
                self.assertEqual((args.repository, args.verify_cache), (repository, "hash"))

    def test_path_with_spaces_is_preserved(self):
        args = self.parse("--verify-cache", "C:/repo with spaces", "--output", "out with spaces")
        self.assertEqual((args.repository, args.output, args.verify_cache),
                         ("C:/repo with spaces", "out with spaces", "hash"))

    def test_explicit_levels(self):
        for level in ("fast", "hash"):
            with self.subTest(level=level):
                args = self.parse(f"--verify-cache={level}", "repo")
                self.assertEqual((args.repository, args.verify_cache), ("repo", level))

    def test_invalid_level_has_clear_parser_error(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
            self.parse("repo", "--verify-cache=foo")
        self.assertEqual(error.exception.code, 2)
        self.assertIn("--verify-cache", stderr.getvalue())
        self.assertIn("invalid choice: 'foo'", stderr.getvalue())

    def test_analyze_still_rejects_verification_controls(self):
        for flag in ("--verify-cache", "--verify-cache=fast", "--verify-cache=hash"):
            with self.subTest(flag=flag), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    build_parser().parse_args(["analyze", flag, "repo"])
                self.assertEqual(error.exception.code, 2)

    def test_only_exact_tokens_change_order_and_input_are_preserved(self):
        argv = ["full", "path/--verify-cache", "--verify-cache=fast", "--verify-cache",
                "--verify-cache=hash", "--output=--verify-cache"]
        original = argv.copy()
        expected = ["full", "path/--verify-cache", "--verify-cache=fast", "--verify-cache=hash",
                    "--verify-cache=hash", "--output=--verify-cache"]
        self.assertEqual(normalize_cache_argv(argv), expected)
        self.assertEqual(argv, original)
        self.assertEqual(normalize_cache_argv(expected), expected)
        for repository in ("path/--verify-cache", "--verify-cache=hash.txt"):
            args = self.parse("--verify-cache", "--", repository)
            self.assertEqual((args.repository, args.verify_cache), (repository, "hash"))

    def test_end_of_options_preserves_exact_flag_as_path(self):
        argv = ["full", "--verify-cache", "--", "--verify-cache"]
        self.assertEqual(normalize_cache_argv(argv), ["full", "--verify-cache=hash", "--", "--verify-cache"])
        args = build_parser().parse_args(argv)
        self.assertEqual((args.repository, args.verify_cache), ("--verify-cache", "hash"))

    def test_parser_uses_sys_argv_when_no_list_is_passed(self):
        with patch.object(sys, "argv", ["main.py", "full", "--verify-cache", "fast"]):
            args = build_parser().parse_args()
        self.assertEqual((args.repository, args.verify_cache), ("fast", "hash"))

    def test_router_passes_levels_unchanged(self):
        for flags, expected in (([], "fast"), (["--verify-cache"], "hash"),
                                (["--verify-cache=fast"], "fast"), (["--verify-cache=hash"], "hash")):
            with self.subTest(flags=flags):
                args = self.parse(*flags, "repo", "--output", "out")
                with patch.object(router, "run_full_pipeline", return_value=RunResult(
                    command="full", status=RunStatus.SUCCESS,
                )) as pipeline:
                    code, _ = router.route(args, lambda *a: self.fail("Unexpected analyze route"))
                self.assertEqual(code, 0)
                self.assertEqual(pipeline.call_args.args, ("repo", "out", [], 12))
                self.assertEqual(pipeline.call_args.kwargs["verify_cache"], expected)


class RealCliSmokeTests(unittest.TestCase):
    def test_main_py_smoke_a_through_d_with_pipeline_interception(self):
        # Real subprocess + root main.py + production router. Intercept only the
        # library call, as authorized by the round; no fixture analysis or AI.
        code = """
import json
import runpy
from unittest.mock import patch
from legacy_documenter.cli.execution_model import RunResult, RunStatus

def pipeline(repository, output, excludes, depth, **kwargs):
    print(json.dumps(dict(repository=repository, output=output, verify_cache=kwargs['verify_cache'],
                         allow_ai_interpretation=kwargs['allow_ai_interpretation'])))
    return RunResult(command='full', status=RunStatus.SUCCESS)

with patch('legacy_documenter.cli.router.run_full_pipeline', side_effect=pipeline), \
     patch('legacy_documenter.main.render_console_summary', return_value=''):
    runpy.run_path('main.py', run_name='__main__')
"""
        repository = "tests/fixtures/v4_2_r7_full_sample"
        output = "output/v5_3_r2_8_1_smoke"
        positionals = [repository, "--output", output]
        cases = (
            ("A", ["full", *positionals, "--verify-cache"], "hash"),
            ("B", ["full", "--verify-cache", *positionals], "hash"),
            ("C", ["full", *positionals, "--verify-cache=fast"], "fast"),
            ("D", ["full", *positionals, "--verify-cache=hash"], "hash"),
        )
        for name, argv, expected in cases:
            with self.subTest(smoke=name):
                result = subprocess.run([sys.executable, "-c", code, *argv], cwd=ROOT,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout.strip())
                self.assertEqual(payload, dict(repository=repository, output=output,
                                               verify_cache=expected, allow_ai_interpretation=False))


if __name__ == "__main__":
    unittest.main()
