from __future__ import annotations

import ast
import inspect
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import config as analysis_config, fingerprints, versions
from legacy_documenter.cli.parser import build_parser
from legacy_documenter.documentation_v52 import engine
from legacy_documenter.documentation_v52.config import DEFAULTS_DIR
from legacy_documenter.evidence import entities
from legacy_documenter.fingerprints import (
    AVAILABLE, UNAVAILABLE, analysis_config_fingerprint, analyzer_code_fingerprint, config_fingerprint,
    projection_config_fingerprint, semantic_content_sha256, semantic_file_sha256, template_profile_fingerprint,
)

PACKAGE = Path(versions.__file__).resolve().parent

# --- ANALYZER_VERSION guard -------------------------------------------------------------------------------
# This pair lives in the TEST on purpose (never in runtime) and is only changed by a person who has decided
# whether the analysis output can change. Procedure when `test_analyzer_version_guard` fails:
#   1. relevant analyzer code changed -> bump `legacy_documenter.versions.ANALYZER_VERSION`;
#   2. then update BOTH values below to the new version and the fingerprint the failure message prints.
GUARD_ANALYZER_VERSION = 3
# V5.9-R1: the python-generic adapter (new analyzer source), the `.py` file kind and the stage routing change the code fingerprint;
# the vbnet-webforms-oracle output is proven byte-identical on the real IST run, so ANALYZER_VERSION stays 3 (previous value: 4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6).
# V5.9-R2: namespaced SourceArtifact identity in both adapters' normalization (opt-in, undeclared = V5.1 ids); previous: ce21000dfe5c64c4ad8af70c1dcb240eeb9d342bdf06d72220b7be7cbd39d2d7.
GUARD_ANALYZER_CODE_FINGERPRINT = "f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b"


def _new_runtime_files() -> list[Path]:
    return [PACKAGE / "versions.py", *sorted((PACKAGE / "fingerprints").glob("*.py"))]


def _copy_analyzer_tree(destination: Path) -> Path:
    root = destination / "legacy_documenter"
    for directory in fingerprints.ANALYZER_CODE_DIRECTORIES:
        shutil.copytree(PACKAGE / directory, root / directory, ignore=shutil.ignore_patterns("__pycache__"))
    for relative in (*fingerprints.ANALYZER_CODE_FILES, fingerprints.PIPELINE_STAGES_FILE):
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE / relative, root / relative)
    return root


class VersionTests(unittest.TestCase):
    def test_analyzer_version_is_a_stable_positive_int(self):
        self.assertIs(type(versions.ANALYZER_VERSION), int)
        self.assertGreaterEqual(versions.ANALYZER_VERSION, 1)

    def test_evidence_schema_version_is_reused_not_duplicated(self):
        self.assertIs(versions.evidence_schema_version(), entities.EVIDENCE_SCHEMA_VERSION)
        for path in _new_runtime_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            assigned = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
            self.assertNotIn("EVIDENCE_SCHEMA_VERSION", assigned)

    def test_renderer_families_registered_with_existing_constants(self):
        registry = versions.renderer_versions()
        self.assertEqual(set(registry), {
            "legacy_markdown", "human_documentation", "consumer_projection", "ai_context", "hydration", "documentation_v52",
        })
        from legacy_documenter.context import consumer_projection, hydration
        from legacy_documenter.documentation_v52 import config as v52_config

        self.assertEqual(registry["hydration"]["model_version"], hydration.MODEL_VERSION)
        self.assertEqual(registry["consumer_projection"]["contract_version"], consumer_projection.CONTRACT_VERSION)
        self.assertEqual(registry["documentation_v52"]["contract_version"], v52_config.CONTRACT_VERSION)
        self.assertEqual(registry["legacy_markdown"]["version"], versions.LEGACY_MARKDOWN_RENDERER_VERSION)
        for family, entries in registry.items():
            self.assertTrue(entries and all(isinstance(v, str) and v for v in entries.values()), family)

    def test_registry_matches_current_contracts(self):
        # Frozen at R2.3: this round changes no output contract; a later change must update this on purpose.
        self.assertEqual(versions.renderer_versions(), {
            "legacy_markdown": {"version": "1"},
            "human_documentation": {"flow_model_version": "V4.3-R3", "flow_schema_version": "1.0",
                                    "scaling_model_version": "V4.3-R4", "scaling_schema_version": "1.0"},
            "consumer_projection": {"contract_version": "1.0", "schema_version": "1.0"},
            "ai_context": {"model_version": "V2-R5", "contract_version": "1.0", "schema_version": "1.0"},
            "hydration": {"model_version": "V4.3-R3"},
            "documentation_v52": {"contract_version": "1"},
        })

    def test_nothing_in_the_runtime_consumes_the_new_modules_yet(self):
        # R2.3 exposed values only. From R2.4 the `cache` package (File State / Cache Manifest) is the one
        # consumer; nothing else (pipeline stages, extractors, renderers...) may depend on them yet.
        for path in PACKAGE.rglob("*.py"):
            if path in _new_runtime_files() or "cache" in path.relative_to(PACKAGE).parts[:1]:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("legacy_documenter.fingerprints", text, path)
            self.assertNotIn("legacy_documenter.versions", text, path)
            self.assertNotIn("import fingerprints", text, path)

    def test_runtime_independence(self):
        for path in _new_runtime_files():
            module = path
            tree = ast.parse(path.read_text(encoding="utf-8"))
            constants = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            for forbidden in ("PROJECT_STATE", "AGENTS.md", "CLAUDE.md", "prompts", "docs/", "tests", "copilot", "subprocess"):
                self.assertFalse(any(forbidden in c for c in constants if len(c) < 120), (path.name, forbidden))
            imported = {n.module.split(".")[-1] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
            imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
            self.assertFalse(imported & {"llm", "knowledge", "orchestration", "subprocess", "requests"})


class AnalyzerCodeFingerprintTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = _copy_analyzer_tree(Path(self._tmp.name))

    def _fp(self, root=None) -> str:
        result = analyzer_code_fingerprint(root or self.root)
        self.assertEqual(result.status, AVAILABLE, result.reason)
        return result.sha256

    def test_same_tree_same_fingerprint_and_equals_the_installed_one(self):
        self.assertEqual(self._fp(), self._fp())
        self.assertEqual(self._fp(), analyzer_code_fingerprint().sha256)

    def test_enumeration_order_does_not_matter(self):
        original = Path.rglob
        with patch.object(Path, "rglob", lambda self, pattern: iter(reversed(list(original(self, pattern))))):
            self.assertEqual(self._fp(), analyzer_code_fingerprint(self.root).sha256)

    def test_one_byte_in_an_included_extractor_changes_it(self):
        before = self._fp()
        target = self.root / "extractors" / "vbnet_extractor.py"
        target.write_bytes(target.read_bytes() + b"# x\n")
        self.assertNotEqual(self._fp(), before)

    def test_one_byte_in_an_included_analysis_module_changes_it(self):
        before = self._fp()
        target = self.root / "analysis" / "call_resolver.py"
        target.write_bytes(target.read_bytes() + b"#\n")
        self.assertNotEqual(self._fp(), before)

    def test_scanner_models_sanitizer_and_config_are_included(self):
        for relative in ("scanner/file_classifier.py", "models/symbol.py", "utils/sanitizer.py", "config.py"):
            with self.subTest(relative):
                before = self._fp()
                target = self.root / relative
                original = target.read_bytes()
                target.write_bytes(original + b"#\n")
                self.assertNotEqual(self._fp(), before)
                target.write_bytes(original)

    def test_only_listed_pipeline_stage_functions_count(self):
        before = self._fp()
        stages = self.root / fingerprints.PIPELINE_STAGES_FILE
        text = stages.read_text(encoding="utf-8")
        # a non-fingerprinted function (rendering) changes: no effect
        stages.write_text(text + "\n\ndef _unrelated_render():\n    return 1\n", encoding="utf-8")
        self.assertEqual(self._fp(), before)
        # a fingerprinted function changes: effect
        marker = "def extract_repository("
        self.assertIn(marker, text)
        stages.write_text(text.replace(marker, "def extract_repository(", 1).replace(
            "    return (selected or ReferenceAdapter()).extract(files, root, extraction_cache)\n", "    pass  # changed\n    return (selected or ReferenceAdapter()).extract(files, root, extraction_cache)\n", 1), encoding="utf-8")
        self.assertNotEqual(self._fp(), before)

    def test_files_outside_scope_do_not_affect_it(self):
        before = self._fp()
        for relative in ("docs/x.md", "prompts/p.md", "tests/t.py", "PROJECT_STATE.json", "cli/other.py", "documentation_v52/engine.py"):
            path = self.root.parent / relative if relative.split("/")[0] in ("docs", "prompts", "tests") or relative == "PROJECT_STATE.json" else self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("changed", encoding="utf-8")
        self.assertEqual(self._fp(), before)

    def test_timestamps_do_not_affect_it(self):
        before = self._fp()
        for path in self.root.rglob("*.py"):
            os.utime(path, (1_000_000, 1_000_000))
        self.assertEqual(self._fp(), before)

    def test_crlf_checkout_does_not_change_it(self):
        before = self._fp()
        for path in self.root.rglob("*.py"):
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(self._fp(), before)

    def test_unreadable_or_missing_sources_are_explicitly_unavailable(self):
        (self.root / "config.py").unlink()
        result = analyzer_code_fingerprint(self.root)
        self.assertEqual((result.status, result.sha256), (UNAVAILABLE, None))
        self.assertTrue(result.reason)
        shutil.rmtree(self.root / "extractors")
        self.assertEqual(analyzer_code_fingerprint(self.root).status, UNAVAILABLE)

    def test_pyc_only_distribution_is_unavailable(self):
        for path in (self.root / "analysis").rglob("*.py"):
            path.unlink()
        result = analyzer_code_fingerprint(self.root)
        self.assertEqual(result.status, UNAVAILABLE)
        self.assertIn("analysis", result.reason)

    def test_missing_fingerprinted_function_is_unavailable(self):
        stages = self.root / fingerprints.PIPELINE_STAGES_FILE
        stages.write_text(stages.read_text(encoding="utf-8").replace("def extract_repository(", "def extract_other(", 1), encoding="utf-8")
        self.assertEqual(analyzer_code_fingerprint(self.root).status, UNAVAILABLE)

    def test_unparseable_stages_file_is_unavailable(self):
        (self.root / fingerprints.PIPELINE_STAGES_FILE).write_text("def (:\n", encoding="utf-8")
        self.assertEqual(analyzer_code_fingerprint(self.root).status, UNAVAILABLE)

    def test_labels_are_normalized_posix_paths(self):
        # the same content under a different absolute location gives the same fingerprint
        other = Path(self._tmp.name) / "elsewhere" / "deeper"
        other.mkdir(parents=True)
        self.assertEqual(self._fp(_copy_analyzer_tree(other)), self._fp())

    def test_every_listed_pipeline_function_exists(self):
        names = {n.name for n in ast.parse((PACKAGE / fingerprints.PIPELINE_STAGES_FILE).read_text(encoding="utf-8")).body
                 if isinstance(n, ast.FunctionDef)}
        self.assertLessEqual(set(fingerprints.PIPELINE_STAGES_FUNCTIONS), names)

    def test_analyzer_version_guard(self):
        current = analyzer_code_fingerprint()
        self.assertEqual(current.status, AVAILABLE, "los fuentes del analizador no son legibles en esta instalación")
        if versions.ANALYZER_VERSION == GUARD_ANALYZER_VERSION:
            self.assertEqual(
                current.sha256, GUARD_ANALYZER_CODE_FINGERPRINT,
                "\nCAMBIÓ CÓDIGO RELEVANTE DEL ANALIZADOR y ANALYZER_VERSION sigue en "
                f"{versions.ANALYZER_VERSION}.\nSi la salida del análisis puede cambiar: suba "
                "legacy_documenter.versions.ANALYZER_VERSION y luego actualice GUARD_ANALYZER_VERSION y "
                f"GUARD_ANALYZER_CODE_FINGERPRINT en este test a:\n  {current.sha256}\n"
                "(ver el procedimiento en el encabezado de este archivo)",
            )
        else:
            self.fail(
                f"ANALYZER_VERSION ahora es {versions.ANALYZER_VERSION} pero el test guardián sigue en "
                f"{GUARD_ANALYZER_VERSION}: actualice GUARD_ANALYZER_VERSION y "
                f"GUARD_ANALYZER_CODE_FINGERPRINT = {current.sha256!r}"
            )


class ConfigFingerprintTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.defaults = Path(self._tmp.name) / "defaults"
        shutil.copytree(DEFAULTS_DIR, self.defaults)

    def test_default_excludes_change(self):
        before = analysis_config_fingerprint()
        with patch.object(analysis_config, "DEFAULT_EXCLUDES", set(analysis_config.DEFAULT_EXCLUDES) | {"extra"}):
            self.assertNotEqual(analysis_config_fingerprint(), before)
        self.assertEqual(analysis_config_fingerprint(), before)

    def test_exclude_is_a_set(self):
        self.assertEqual(analysis_config_fingerprint(["a", "b"]), analysis_config_fingerprint(["b", "a", "a"]))
        self.assertNotEqual(analysis_config_fingerprint(["a"]), analysis_config_fingerprint([]))
        self.assertNotEqual(analysis_config_fingerprint(["a"]), analysis_config_fingerprint(["A"]))  # scanner is case-sensitive
        self.assertEqual(analysis_config_fingerprint(None), analysis_config_fingerprint([]))

    def test_flow_max_depth_changes(self):
        self.assertNotEqual(analysis_config_fingerprint(flow_max_depth=12), analysis_config_fingerprint(flow_max_depth=13))

    def test_language_change_changes_projection(self):
        before = projection_config_fingerprint(defaults_dir=self.defaults)
        profile = self.defaults / "profiles" / "general_overview.json"
        profile.write_text(profile.read_text(encoding="utf-8").replace('"language": "es"', '"language": "en"'), encoding="utf-8")
        self.assertNotEqual(projection_config_fingerprint(defaults_dir=self.defaults), before)

    def test_profile_set_and_order_change(self):
        a = projection_config_fingerprint(["general_overview", "developer_technical"], defaults_dir=self.defaults)
        self.assertNotEqual(a, projection_config_fingerprint(["general_overview"], defaults_dir=self.defaults))
        self.assertNotEqual(a, projection_config_fingerprint(["developer_technical", "general_overview"], defaults_dir=self.defaults))

    def test_custom_dir_and_strict_templates_change(self):
        base = projection_config_fingerprint(defaults_dir=self.defaults)
        custom = Path(self._tmp.name) / "custom"
        (custom / "templates").mkdir(parents=True)
        (custom / "templates" / "dev.index.json").write_text("{}", encoding="utf-8")
        with_custom = projection_config_fingerprint(custom_dir=custom, defaults_dir=self.defaults)
        self.assertNotEqual(with_custom, base)
        (custom / "templates" / "dev.index.json").write_text('{"a": 1}', encoding="utf-8")
        self.assertNotEqual(projection_config_fingerprint(custom_dir=custom, defaults_dir=self.defaults), with_custom)
        self.assertNotEqual(projection_config_fingerprint(strict_templates=True, defaults_dir=self.defaults), base)

    def test_ai_verbose_and_output_do_not_enter(self):
        params = set(inspect.signature(config_fingerprint).parameters) | set(inspect.signature(analysis_config_fingerprint).parameters)
        for name in ("allow_ai_interpretation", "verbose", "output", "output_dir", "long_paths", "repository", "interpreted"):
            self.assertNotIn(name, params)
        self.assertEqual(config_fingerprint(defaults_dir=self.defaults), config_fingerprint(defaults_dir=self.defaults))

    def test_combined_fingerprint_follows_both_parts(self):
        base = config_fingerprint(defaults_dir=self.defaults)
        self.assertNotEqual(config_fingerprint(flow_max_depth=3, defaults_dir=self.defaults), base)
        self.assertNotEqual(config_fingerprint(strict_templates=True, defaults_dir=self.defaults), base)
        self.assertNotEqual(config_fingerprint(excludes=["x"], defaults_dir=self.defaults), base)

    def test_analysis_fingerprint_ignores_projection_options(self):
        self.assertEqual(analysis_config_fingerprint(["x"], 5), analysis_config_fingerprint(["x"], 5))
        self.assertNotIn("profiles", inspect.signature(analysis_config_fingerprint).parameters)


class CliOptionClassificationTests(unittest.TestCase):
    ALLOWED = {
        fingerprints.ANALYSIS_AFFECTING, fingerprints.PROJECTION_AFFECTING, fingerprints.RUNTIME_ONLY,
        fingerprints.AI_ONLY, fingerprints.OUTPUT_LOCATION_ONLY, fingerprints.REPOSITORY_IDENTITY,
    }

    @staticmethod
    def _real_dests() -> dict[str, set[str]]:
        parser = build_parser()
        subparsers = next(a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction")
        found: dict[str, set[str]] = {}
        for command, sub in subparsers.choices.items():
            for action in sub._actions:
                if action.dest in ("help",):
                    continue
                found.setdefault(action.dest, set()).add(command)
        return found

    def test_every_real_cli_option_is_classified_and_no_entry_is_stale(self):
        real = self._real_dests()
        self.assertTrue(real)
        unclassified = set(real) - set(fingerprints.CLI_OPTION_CLASSES)
        self.assertFalse(unclassified, (
            f"opciones de CLI sin clasificar: {sorted(unclassified)}. Declare en fingerprints.CLI_OPTION_CLASSES si "
            "invalidan caché (analysis-/projection-affecting) o no (runtime-only, ai-only, output-location-only)."))
        self.assertEqual(set(fingerprints.CLI_OPTION_CLASSES) - set(real), set(), "entradas obsoletas en la clasificación")
        self.assertLessEqual(set(fingerprints.CLI_OPTION_CLASSES.values()), self.ALLOWED)

    def test_classification_of_current_options(self):
        classes = fingerprints.CLI_OPTION_CLASSES
        self.assertEqual(classes["exclude"], fingerprints.ANALYSIS_AFFECTING)
        self.assertEqual(classes["flow_max_depth"], fingerprints.ANALYSIS_AFFECTING)
        self.assertEqual(classes["verbose"], fingerprints.RUNTIME_ONLY)
        self.assertEqual(classes["allow_ai_interpretation"], fingerprints.AI_ONLY)
        self.assertEqual(classes["output"], fingerprints.OUTPUT_LOCATION_ONLY)

    def test_analysis_affecting_options_are_wired_into_the_analysis_fingerprint(self):
        affecting = {d for d, c in fingerprints.CLI_OPTION_CLASSES.items() if c == fingerprints.ANALYSIS_AFFECTING}
        self.assertEqual(affecting, {"exclude", "flow_max_depth"})
        base = analysis_config_fingerprint()
        self.assertNotEqual(analysis_config_fingerprint(excludes=["x"]), base)
        self.assertNotEqual(analysis_config_fingerprint(flow_max_depth=99), base)

    def test_v52_generation_parameters_are_classified(self):
        params = set(inspect.signature(engine.generate_documentation_v52).parameters) - {"source", "output_dir"}
        self.assertEqual(params, set(fingerprints.V52_PARAMETER_CLASSES))
        projection = {p for p, c in fingerprints.V52_PARAMETER_CLASSES.items() if c == fingerprints.PROJECTION_AFFECTING}
        for name in ("profiles", "custom_dir", "strict_templates"):
            self.assertIn(name, projection)
            self.assertIn(name, inspect.signature(projection_config_fingerprint).parameters)


class TemplateProfileFingerprintTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.defaults = Path(self._tmp.name) / "defaults"
        shutil.copytree(DEFAULTS_DIR, self.defaults)

    def _fp(self, **kwargs) -> str:
        return template_profile_fingerprint(defaults_dir=self.defaults, **kwargs)

    def test_same_content_same_fingerprint_as_installed_defaults(self):
        self.assertEqual(self._fp(), template_profile_fingerprint())
        self.assertEqual(self._fp(), self._fp())

    def test_read_order_does_not_matter(self):
        original = Path.rglob
        before = self._fp()
        with patch.object(Path, "rglob", lambda self, pattern: iter(reversed(sorted(original(self, pattern))))):
            self.assertEqual(self._fp(), before)

    def test_template_profile_i18n_noise_changes(self):
        for relative in ("templates/dev.index.json", "profiles/developer_technical.json", "i18n/es.json", "noise/default.json"):
            with self.subTest(relative):
                before = self._fp()
                path = self.defaults / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n ")
                self.assertNotEqual(self._fp(), before)
                path.write_bytes(original)
                self.assertEqual(self._fp(), before)

    def test_language_change_changes_it(self):
        before = self._fp()
        path = self.defaults / "profiles" / "developer_technical.json"
        path.write_text(path.read_text(encoding="utf-8").replace('"language": "es"', '"language": "en"'), encoding="utf-8")
        self.assertNotEqual(self._fp(), before)

    def test_custom_dir_is_incorporated_and_labelled(self):
        before = self._fp()
        custom = Path(self._tmp.name) / "custom"
        (custom / "i18n").mkdir(parents=True)
        (custom / "i18n" / "en.json").write_text("{}", encoding="utf-8")
        with_custom = self._fp(custom_dir=custom)
        self.assertNotEqual(with_custom, before)
        # the same file placed as a custom override differs from the default having that content
        (custom / "i18n" / "en.json").unlink()
        self.assertEqual(self._fp(custom_dir=custom), self._fp(custom_dir=custom))
        self.assertNotEqual(self._fp(custom_dir=custom), before)  # a present-but-empty custom dir is still a marker

    def test_file_added_or_removed_changes_it(self):
        before = self._fp()
        extra = self.defaults / "templates" / "extra.json"
        extra.write_text("{}", encoding="utf-8")
        added = self._fp()
        self.assertNotEqual(added, before)
        extra.unlink()
        self.assertEqual(self._fp(), before)
        (self.defaults / "templates" / "dev.index.json").unlink()
        self.assertNotEqual(self._fp(), before)

    def test_active_profiles_matter(self):
        self.assertNotEqual(self._fp(profiles=["general_overview"]), self._fp())

    def test_mtime_without_content_change_does_not_matter(self):
        before = self._fp()
        for path in self.defaults.rglob("*.json"):
            os.utime(path, (1_000_000, 1_000_000))
        self.assertEqual(self._fp(), before)

    def test_crlf_conversion_does_not_matter(self):
        before = self._fp()
        for path in self.defaults.rglob("*.json"):
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(self._fp(), before)

    def test_defaults_content_is_untouched_by_the_round(self):
        self.assertTrue(any(DEFAULTS_DIR.rglob("*.json")))


class SemanticHashTests(unittest.TestCase):
    def test_crlf_cr_and_lf_are_equivalent(self):
        lf = semantic_content_sha256(b"a\nb\n", "vb_source")
        self.assertEqual(semantic_content_sha256(b"a\r\nb\r\n", "vb_source"), lf)
        self.assertEqual(semantic_content_sha256(b"a\rb\r", "vb_source"), lf)
        self.assertEqual(semantic_content_sha256(b"a\r\nb\rc\n", "aspx"), semantic_content_sha256(b"a\nb\nc\n", "aspx"))

    def test_bom_is_preserved(self):
        self.assertNotEqual(semantic_content_sha256(b"\xef\xbb\xbfa\n", "vb_source"), semantic_content_sha256(b"a\n", "vb_source"))

    def test_whitespace_is_preserved(self):
        self.assertNotEqual(semantic_content_sha256(b"a \n", "vb_source"), semantic_content_sha256(b"a\n", "vb_source"))
        self.assertNotEqual(semantic_content_sha256(b"a\n\n", "vb_source"), semantic_content_sha256(b"a\n", "vb_source"))
        self.assertNotEqual(semantic_content_sha256(b"\ta\n", "vb_source"), semantic_content_sha256(b"    a\n", "vb_source"))

    def test_different_content_differs(self):
        self.assertNotEqual(semantic_content_sha256(b"a\n", "vb_source"), semantic_content_sha256(b"b\n", "vb_source"))

    def test_empty_file(self):
        import hashlib

        self.assertEqual(semantic_content_sha256(b"", "vb_source"), hashlib.sha256(b"").hexdigest())

    def test_not_analyzed_types_have_no_semantic_hash(self):
        for file_type in ("javascript", "css", "html", "xml", "resource", "assembly", "other", "app_config", ""):
            self.assertIsNone(semantic_content_sha256(b"a\r\n", file_type), file_type)

    def test_deterministic_and_raw_hash_still_differs(self):
        import hashlib

        crlf, lf = b"a\r\nb\r\n", b"a\nb\n"
        self.assertEqual(semantic_content_sha256(crlf, "vb_source"), semantic_content_sha256(crlf, "vb_source"))
        self.assertNotEqual(hashlib.sha256(crlf).hexdigest(), hashlib.sha256(lf).hexdigest())
        self.assertNotEqual(semantic_content_sha256(crlf, "vb_source"), hashlib.sha256(crlf).hexdigest())

    def test_file_helper_reads_only_analyzed_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.vb"
            path.write_bytes(b"x\r\n")
            self.assertEqual(semantic_file_sha256(path, "vb_source"), semantic_content_sha256(b"x\n", "vb_source"))
            self.assertIsNone(semantic_file_sha256(Path(tmp) / "does-not-exist.js", "javascript"))

    def test_analyzed_types_equal_the_extractor_map_of_the_pipeline(self):
        tree = ast.parse((PACKAGE / "adapters" / "vbnet_webforms_oracle" / "extraction.py").read_text(encoding="utf-8"))
        extract = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_extractors")
        keys: set[str] = set()
        for node in ast.walk(extract):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                keys = {k.value for k in node.value.keys}
        # V5.9: the analyzed set is the union of every registered adapter's extractable kinds.
        from legacy_documenter.adapters.python_generic.adapter import PythonGenericAdapter
        self.assertEqual(set(fingerprints.ANALYZED_FILE_TYPES), keys | PythonGenericAdapter.descriptor.source_kinds)

    def test_source_artifact_sha256_is_not_modified(self):
        from legacy_documenter.adapters.vbnet_webforms_oracle import normalization as builder

        text = Path(builder.__file__).read_text(encoding="utf-8")
        self.assertIn("sha256=_hash_file(repo_root / record[\"relative_path\"])", text)
        self.assertNotIn("semantic", text)


if __name__ == "__main__":
    unittest.main()
