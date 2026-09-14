"""V4.1-R7 characterization: pins the pre-cleanup behavior of the three
near-identical extractor try/except blocks in ``legacy_documenter.main.analyze_repository``
(CallExtractor / WebEventExtractor / DatabaseExtractor) before any consolidation.

These tests must pass unchanged both before and after the R7 SAFE_LOCAL_CLEANUP
extraction of the shared ``_extract_into`` helper.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.extractors.call_extractor import CallExtractor
from legacy_documenter.extractors.database_extractor import DatabaseExtractor
from legacy_documenter.extractors.web_event_extractor import WebEventExtractor
from legacy_documenter.main import analyze_repository


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _make_repo(root: Path) -> None:
    write(root / "App.vbproj", '<Project><PropertyGroup><RootNamespace>Empresa</RootNamespace></PropertyGroup><ItemGroup><Compile Include="A.vb" /></ItemGroup></Project>')
    write(root / "A.vb", "Public Class A\nPublic Sub Run()\nEnd Sub\nEnd Class\n")


class TestV4_1_R7ExceptionBoundaryCharacterization(unittest.TestCase):
    def test_call_extractor_failure_is_recorded_as_structured_error_and_others_still_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _make_repo(root)
            with patch.object(CallExtractor, "extract", side_effect=ValueError("call-boom")):
                indexes = analyze_repository(root, root / "out")
            self.assertEqual(
                indexes["errors"],
                [{"file": "A.vb", "extractor": "CallExtractor", "error": "call-boom"}],
            )
            self.assertEqual(indexes["calls"], [])

    def test_web_event_extractor_failure_is_recorded_as_structured_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _make_repo(root)
            with patch.object(WebEventExtractor, "extract", side_effect=RuntimeError("event-boom")):
                indexes = analyze_repository(root, root / "out")
            self.assertEqual(
                indexes["errors"],
                [{"file": "A.vb", "extractor": "WebEventExtractor", "error": "event-boom"}],
            )
            self.assertEqual(len(indexes["calls"]), 1)

    def test_database_extractor_failure_is_recorded_as_structured_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _make_repo(root)
            with patch.object(DatabaseExtractor, "extract", side_effect=KeyError("db-boom")):
                indexes = analyze_repository(root, root / "out")
            self.assertEqual(len(indexes["errors"]), 1)
            self.assertEqual(indexes["errors"][0]["file"], "A.vb")
            self.assertEqual(indexes["errors"][0]["extractor"], "DatabaseExtractor")
            self.assertIn("db-boom", indexes["errors"][0]["error"])

    def test_all_three_extractor_failures_preserve_call_order_per_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _make_repo(root)
            with patch.object(CallExtractor, "extract", side_effect=ValueError("c")), \
                 patch.object(WebEventExtractor, "extract", side_effect=ValueError("w")), \
                 patch.object(DatabaseExtractor, "extract", side_effect=ValueError("d")):
                indexes = analyze_repository(root, root / "out")
            self.assertEqual(
                [e["extractor"] for e in indexes["errors"]],
                ["CallExtractor", "WebEventExtractor", "DatabaseExtractor"],
            )
            self.assertEqual(indexes["calls"], [])
            self.assertEqual(indexes["data_access"], [])

    def test_no_failure_yields_no_errors_and_populated_results(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _make_repo(root)
            indexes = analyze_repository(root, root / "out")
            self.assertEqual(indexes["errors"], [])
            self.assertEqual(len(indexes["calls"]), 1)


if __name__ == "__main__":
    unittest.main()
