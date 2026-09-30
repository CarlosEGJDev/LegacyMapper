"""V5.2 R2: Profiles, Templates and Markdown Renderer (documentation_v52).

Tests contracts and structure, not full literal text.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.documentation_v52 import config as v52_config
from legacy_documenter.documentation_v52.categories import (
    DETAIL_ON_DEMAND, INTERNAL_ONLY, KEEP_SIMPLE, KEEP_TECHNICAL, AudienceDocumentModel, Item,
)
from legacy_documenter.documentation_v52.config import ConfigError, ConfigRegistry, OutputProfile, validate_template
from legacy_documenter.documentation_v52.engine import (
    OUTPUT_DIRNAME, generate_documentation_v52, parse_interpreted_sections, source_from_indexes,
)
from legacy_documenter.documentation_v52.noise import NoisePolicy, bare_name
from legacy_documenter.documentation_v52.renderer import PartitionPolicy, format_text, partition_ranges
from legacy_documenter.documentation_v52.structure import Text
from legacy_documenter.documentation_v52.template import ProfileView
from legacy_documenter.documentation_v52.transform import AudienceTransformer

PACKAGE_DIR = Path(v52_config.__file__).resolve().parent
INTERNAL_ID_RE = re.compile(r"\b(?:FLOW|PATH|CAL|CALL|UNRES|DAO|EP|EVB|SP|SRC|XDP|PRJ|CMP|SOL)-[0-9a-f]{8,}\b")
PURPOSE_PHRASE = "El propósito funcional del sistema no puede deducirse del código; requiere una descripción aportada por una persona."


def _source(flow_count: int = 4) -> dict:
    projects = [
        {"name": "WebA", "path": "WebA.vbproj", "output_type": "Library"},
        {"name": "blA", "path": "bl\\blA\\blA.vbproj", "output_type": "Library"},
    ]
    flows = []
    entry_points = []
    unresolved = []
    for index in range(flow_count):
        ep = f"EP-{index:010d}"
        flow = f"FLOW-{index:010d}"
        confirmed = index % 2 == 0
        entry_points.append({"id": ep, "type": "web_event", "webform": f"WebA\\f{index % 3}.ascx", "event": "Click",
                             "handler": f"btn{index}_Click", "project": "WebA.vbproj", "confidence": "confirmed"})
        flows.append({"id": flow, "entry_point_id": ep, "webform": f"WebA\\f{index % 3}.ascx", "event": "Click",
                      "handler": f"btn{index}_Click", "project_sequence": ["WebA.vbproj"],
                      "terminal_operations": ["PKG_X.PROC_A"] if confirmed else [],
                      "has_confirmed_terminal": confirmed, "has_unresolved_boundary": not confirmed})
        unresolved.append({"flow_id": flow, "path_id": f"PATH-{'a' * 64}", "terminal_target": "InitializeComponent()"})
        unresolved.append({"flow_id": flow, "path_id": f"PATH-{'b' * 64}", "terminal_target": "Foo.Bar(  x )"})
    data_access = [
        {"id": "DAO-0000000001", "operation_kind": "stored_procedure", "stored_procedure": "PKG_X.PROC_A", "provider": "OraConn",
         "class": "C", "method": "m", "project": "WebA.vbproj", "confidence": "confirmed",
         "evidence": [{"file": "C.vb", "line": 3}]},
        {"id": "DAO-0000000002", "operation_kind": "transaction", "provider": "OraConn", "class": "C", "method": "m",
         "project": "WebA.vbproj", "confidence": "confirmed", "evidence": [{"file": "C.vb", "line": 4}]},
    ]
    return {
        "repository": {"root": "C:\\repo\\Sample", "stats": {"vb_source": 10}},
        "solutions": [{"name": "SlnA", "path": "SlnA\\SlnA.sln", "projects": [{"name": "WebA", "path": "..\\WebA.vbproj"}]}],
        "projects": projects, "entry_points": entry_points, "functional_flows": flows, "flow_unresolved": unresolved,
        "data_access": data_access, "stored_procedures": [{"name": "PKG_X.PROC_A", "package": "PKG_X"}],
        "sql_operations": [],
        "dependencies": [
            {"source": "WebA.vbproj", "target": "bl\\blA\\blA.vbproj", "dependency_type": "Project -> Project"},
            {"source": "WebA.vbproj", "target": "SondaNetShared, Version=4.0.0.0", "dependency_type": "Project -> DLL"},
            {"source": "WebA.vbproj", "target": "System.Data", "dependency_type": "Project -> DLL"},
        ],
        "configuration": [{"path": "Web.config"}, {"path": "Backup\\Web.config"}],
        "flow_summary": {"total_flows": flow_count, "flows_with_confirmed_terminal": (flow_count + 1) // 2,
                         "flows_with_unresolved_boundary": flow_count // 2},
        "webforms": [], "external_dependencies": [],
    }


def _all_texts(root: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.rglob("*.md")))


def _link_targets(text: str) -> list[str]:
    return [t for t in re.findall(r"\]\(([^)]+)\)", text) if not t.startswith("http")]


class GeneratedTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name)
        cls.result = generate_documentation_v52(_source(), cls.out)
        cls.root = cls.out / OUTPUT_DIRNAME

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_both_profiles_generated_in_separate_directories(self) -> None:
        self.assertTrue((self.root / "general" / "README.md").is_file())
        self.assertTrue((self.root / "developer" / "README.md").is_file())
        self.assertTrue((self.root / "README.md").is_file())
        self.assertEqual(set(self.result.profiles), {"general_overview", "developer_technical"})

    def test_general_overview_has_neutral_purpose_without_interpreted(self) -> None:
        text = (self.root / "general" / "README.md").read_text(encoding="utf-8")
        self.assertIn(PURPOSE_PHRASE, text)
        self.assertNotIn("Contenido interpretado", text)

    def test_general_overview_covers_required_topics(self) -> None:
        names = {p.name for p in (self.root / "general").iterdir()}
        self.assertEqual(names, {"README.md", "modules.md", "external-systems.md", "data.md", "limitations.md"})

    def test_no_internal_ids_or_hashes_in_any_human_document(self) -> None:
        text = _all_texts(self.root)
        self.assertIsNone(INTERNAL_ID_RE.search(text))
        self.assertNotRegex(text, r"[0-9a-f]{40,}")

    def test_all_relative_links_resolve(self) -> None:
        for path in self.root.rglob("*.md"):
            for target in _link_targets(path.read_text(encoding="utf-8")):
                self.assertTrue((path.parent / target).resolve().is_file(), f"{path} -> {target}")

    def test_developer_module_navigation_and_progressive_detail(self) -> None:
        module = (self.root / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8")
        for heading in ("## Resumen", "## Puntos de entrada propios", "## Flujos originados aquí", "## Acceso directo a datos", "## Dependencias declaradas", "## Información no resuelta"):
            self.assertIn(heading, module)
        self.assertTrue((self.root / "developer" / "modules" / "WebA" / "detail.md").is_file())
        index = (self.root / "developer" / "README.md").read_text(encoding="utf-8")
        self.assertIn("modules/WebA.md", index)

    def test_solution_membership_resolved_by_path(self) -> None:
        module = (self.root / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8")
        self.assertIn("SlnA", module)

    def test_noise_hidden_from_body_but_available_in_detail(self) -> None:
        module = (self.root / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8")
        body_unresolved = module.split("## Información no resuelta")[1]
        self.assertNotIn("InitializeComponent", body_unresolved)
        self.assertIn("Foo.Bar", body_unresolved)
        detail = _all_texts(self.root / "developer" / "modules" / "WebA")
        self.assertIn("InitializeComponent", detail)

    def test_system_library_hidden_in_body(self) -> None:
        text = (self.root / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8")
        self.assertIn("SondaNetShared", text)
        self.assertNotIn("System.Data", text.split("## Dependencias")[1].split("## Información")[0])

    def test_generated_note_and_gaps_are_declared(self) -> None:
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("no permite determinar", readme)
        self.assertTrue(any("propósito de negocio" in gap for gap in self.result.gaps))

    def test_manifest_lists_every_file_with_hash(self) -> None:
        manifest = json.loads((self.root / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file_count"], len(self.result.files))
        for entry in manifest["files"]:
            data = (self.root / entry["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])


class DeterminismAndLegacyTests(unittest.TestCase):
    def test_same_input_same_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = generate_documentation_v52(_source(), a)
            second = generate_documentation_v52(_source(), b)
            self.assertEqual(first.files, second.files)
            for name in first.files:
                self.assertEqual((first.output_dir / name).read_bytes(), (second.output_dir / name).read_bytes(), name)

    def test_rerun_removes_stale_files_only_inside_v52_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "documentation").mkdir()
            legacy = out / "documentation" / "README.md"
            legacy.write_text("legacy", encoding="utf-8")
            generate_documentation_v52(_source(4), out)
            stale = out / OUTPUT_DIRNAME / "developer" / "modules" / "Gone.md"
            stale.write_text("old", encoding="utf-8")
            generate_documentation_v52(_source(4), out)
            self.assertFalse(stale.exists())
            self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy")

    def test_legacy_documentation_directory_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "documentation").mkdir()
            sentinel = out / "documentation" / "X.md"
            sentinel.write_text("keep", encoding="utf-8")
            before = sorted((p.name, p.read_bytes()) for p in (out / "documentation").iterdir())
            generate_documentation_v52(_source(), out)
            self.assertEqual(before, sorted((p.name, p.read_bytes()) for p in (out / "documentation").iterdir()))


class SeparationAndIndependenceTests(unittest.TestCase):
    @staticmethod
    def _imports(module: str) -> str:
        return "\n".join(l for l in (PACKAGE_DIR / module).read_text(encoding="utf-8").splitlines() if re.match(r"\s*(from|import) ", l))

    def test_renderer_knows_nothing_about_profile_noise_or_evidence(self) -> None:
        imports = self._imports("renderer.py")
        for forbidden in ("config", "noise", "transform", "template", "categories", "evidence"):
            self.assertNotRegex(imports, rf"\b{forbidden}\b", forbidden)

    def test_template_does_not_import_renderer_or_evidence(self) -> None:
        imports = self._imports("template.py")
        self.assertNotIn("renderer", imports)
        self.assertNotIn("evidence", imports)

    def test_transform_does_not_import_profile_template_or_renderer(self) -> None:
        imports = self._imports("transform.py")
        for forbidden in ("template", "renderer", "config", "structure"):
            self.assertNotRegex(imports, rf"\.{forbidden}\b")

    def test_no_ai_provider_imports_anywhere_in_package(self) -> None:
        for path in PACKAGE_DIR.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("openai", "anthropic", "ollama", "gemini", "legacy_documenter.llm", "orchestration"):
                self.assertNotRegex(text.lower(), rf"^\s*(from|import)\s+\S*{forbidden}", f"{path.name}:{forbidden}")

    def test_runtime_does_not_depend_on_dev_directories(self) -> None:
        for path in PACKAGE_DIR.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("PROJECT_STATE", "prompts/", "docs/", "tools/"):
                self.assertNotIn(forbidden, "\n".join(l for l in text.splitlines() if not l.strip().startswith(("#", '"""')) and "docs/V5" not in l), f"{path.name}:{forbidden}")

    def test_template_view_never_exposes_evidence_ids(self) -> None:
        model = AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(_source())
        for module in model.modules:
            for items in module.slots.values():
                for item in items:
                    for value in item.values.values():
                        self.assertIsNone(INTERNAL_ID_RE.search(str(value)))


class ProfileAndCategoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ConfigRegistry()
        self.policy = self.registry.noise_policy("default")

    def test_exactly_two_default_profiles(self) -> None:
        names = sorted(p.stem for p in (v52_config.DEFAULTS_DIR / "profiles").glob("*.json"))
        self.assertEqual(names, ["developer_technical", "general_overview"])

    def test_general_shows_only_keep_simple_developer_adds_technical(self) -> None:
        general = self.registry.profile("general_overview")
        developer = self.registry.profile("developer_technical")
        self.assertEqual(general.visible_categories, (KEEP_SIMPLE,))
        self.assertEqual(developer.visible_categories, (KEEP_SIMPLE, KEEP_TECHNICAL))
        for profile in (general, developer):
            self.assertNotIn(INTERNAL_ONLY, profile.visible_categories)

    def test_internal_only_is_never_visible_by_default_and_rejected_without_flag(self) -> None:
        data = json.loads((v52_config.DEFAULTS_DIR / "profiles" / "general_overview.json").read_text(encoding="utf-8"))
        data["visible_categories"] = ["KEEP_SIMPLE", "INTERNAL_ONLY"]
        with self.assertRaises(ConfigError):
            OutputProfile.from_dict(data)

    def test_profile_view_filters_by_category_and_level(self) -> None:
        profile = self.registry.profile("developer_technical")
        model = AudienceDocumentModel(system={}, slots={}, modules=[])
        view = ProfileView(model, profile, self.policy)
        items = [Item({"a": 1}, KEEP_SIMPLE, 1), Item({"a": 2}, KEEP_TECHNICAL, 3), Item({"a": 3}, DETAIL_ON_DEMAND, 4),
                 Item({"a": 4}, INTERNAL_ONLY, 1)]
        self.assertEqual([i.values["a"] for i in view.visible(items)], [1, 2])
        self.assertEqual([i.values["a"] for i in view.detail(items)], [1, 2, 3, 4][:4])

    def test_profile_view_detail_off_when_profile_has_no_detail_documents(self) -> None:
        general = self.registry.profile("general_overview")
        view = ProfileView(AudienceDocumentModel({}, {}, []), general, self.policy)
        self.assertEqual(view.detail([Item({}, DETAIL_ON_DEMAND, 4)]), [])

    def test_invalid_profile_partition_rejected(self) -> None:
        data = json.loads((v52_config.DEFAULTS_DIR / "profiles" / "general_overview.json").read_text(encoding="utf-8"))
        data["partition"] = {"max_items_per_part": 0, "max_bytes_per_part": 10}
        with self.assertRaises(ConfigError):
            OutputProfile.from_dict(data)


class NoisePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ConfigRegistry()
        self.policy = self.registry.noise_policy("default")

    def test_bare_name(self) -> None:
        self.assertEqual(bare_name("Me.parametrosURL(  )"), "parametrosURL")
        self.assertEqual(bare_name("dbc.Close()"), "Close")

    def test_classification_categories(self) -> None:
        cases = {
            "InitializeComponent()": "lifecycle_boilerplate", "dbc.Rollback()": "transaction_control",
            "dbc.Close()": "resource_cleanup", "DesplegarError(ex)": "exception_handling",
            "MsgBox(x)": "ui_messaging", "Not (Page.IsPostBack)": "string_utility",
        }
        for label, expected in cases.items():
            self.assertEqual(self.policy.classify(name=bare_name(label), label=label), expected, label)
        self.assertIsNone(self.policy.classify(name="RealBusinessCall", label="RealBusinessCall()"))
        self.assertEqual(self.policy.classify(name="System.Data"), "platform_library")

    def test_visibility_overrides_belong_to_profile(self) -> None:
        self.assertEqual(self.policy.visibility("transaction_control"), "hide")
        self.assertEqual(self.policy.visibility("transaction_control", {"transaction_control": "show"}), "show")

    def test_policy_is_technology_agnostic_data(self) -> None:
        text = (PACKAGE_DIR / "noise.py").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"InitializeComponent|BeginTrans|VB\.NET|WebForms")

    def test_custom_noise_policy_changes_body_without_code_change(self) -> None:
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as out:
            data = json.loads((v52_config.DEFAULTS_DIR / "noise" / "default.json").read_text(encoding="utf-8"))
            data["categories"]["lifecycle_boilerplate"]["body_visibility"] = "show"
            (Path(custom) / "noise").mkdir()
            (Path(custom) / "noise" / "default.json").write_text(json.dumps(data), encoding="utf-8")
            result = generate_documentation_v52(_source(), out, custom_dir=custom)
            module = (result.output_dir / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8")
            self.assertIn("InitializeComponent", module.split("## Información no resuelta")[1])

    def test_invalid_noise_policy_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            NoisePolicy.from_dict({"id": "x", "categories": {"a": {"body_visibility": "bogus"}}, "patterns": []})


class TemplateTests(unittest.TestCase):
    def test_all_default_templates_are_valid_and_cover_r1_contract(self) -> None:
        registry = ConfigRegistry()
        expected = {
            "general_overview": {"overview.system", "overview.modules", "overview.external_systems", "overview.data", "overview.limitations"},
            "developer_technical": {"dev.index", "dev.module", "dev.flow_summary", "dev.data_access_summary",
                                    "dev.dependency_summary", "dev.unresolved_summary", "dev.technical_detail"},
        }
        for profile_id, required in expected.items():
            profile = registry.profile(profile_id)
            catalog = registry.catalog(profile.language)
            self.assertTrue(required <= set(profile.templates))
            for template_id in profile.templates:
                template = registry.template(template_id, profile, catalog)
                validate_template(template, catalog, profile, expected_id=template_id)
        self.assertEqual(registry.warnings, [])

    def _custom(self, tmp: str, name: str, body: dict | str) -> None:
        directory = Path(tmp) / "templates"
        directory.mkdir(exist_ok=True)
        (directory / f"{name}.json").write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")

    def _default(self, name: str) -> dict:
        return json.loads((v52_config.DEFAULTS_DIR / "templates" / f"{name}.json").read_text(encoding="utf-8"))

    def test_custom_partial_override_replaces_only_that_template(self) -> None:
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as out:
            template = self._default("overview.data")
            template["blocks"] = [{"type": "paragraph", "text_key": "overview.data.none"}]
            self._custom(custom, "overview.data", template)
            result = generate_documentation_v52(_source(), out, custom_dir=custom)
            data = (result.output_dir / "general" / "data.md").read_text(encoding="utf-8")
            self.assertIn("No se detectó acceso a datos", data)
            self.assertNotIn("Paquete", data)
            self.assertIn("Soluciones y proyectos", (result.output_dir / "general" / "modules.md").read_text(encoding="utf-8"))
            self.assertEqual(result.warnings, [])

    def test_custom_invalid_template_warns_and_falls_back_to_default(self) -> None:
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as out:
            template = self._default("overview.data")
            template["blocks"][0]["text_key"] = "no.such.key"
            self._custom(custom, "overview.data", template)
            result = generate_documentation_v52(_source(), out, custom_dir=custom)
            self.assertTrue(any("overview.data" in w and "no.such.key" in w for w in result.warnings))
            self.assertIn("Paquete", (result.output_dir / "general" / "data.md").read_text(encoding="utf-8"))
            self.assertIn("inválido", (result.output_dir / "README.md").read_text(encoding="utf-8"))

    def test_custom_malformed_json_warns_and_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as out:
            self._custom(custom, "overview.data", "{not json")
            result = generate_documentation_v52(_source(), out, custom_dir=custom)
            self.assertTrue(any("overview.data" in w for w in result.warnings))
            self.assertTrue((result.output_dir / "general" / "data.md").is_file())

    def test_strict_mode_fails_on_invalid_custom(self) -> None:
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as out:
            template = self._default("overview.data")
            template["blocks"] = [{"type": "table", "source": "slots.evidence_core_internal", "columns": []}]
            self._custom(custom, "overview.data", template)
            with self.assertRaises(ConfigError) as ctx:
                generate_documentation_v52(_source(), out, custom_dir=custom, strict_templates=True)
            self.assertIn("overview.data", str(ctx.exception))

    def test_template_cannot_reference_internal_or_unknown_fields(self) -> None:
        registry = ConfigRegistry()
        profile = registry.profile("general_overview")
        catalog = registry.catalog("es")
        template = self._default("overview.data")
        template["blocks"] = [{"type": "table", "source": "slots.data_packages",
                               "columns": [{"field": "evidence_ids", "header_key": "col.name"}]}]
        with self.assertRaises(ConfigError):
            validate_template(template, catalog, profile)

    def test_template_cannot_write_outside_output_tree(self) -> None:
        registry = ConfigRegistry()
        profile = registry.profile("general_overview")
        template = self._default("overview.data")
        template["file"] = "../evil.md"
        with self.assertRaises(ConfigError):
            validate_template(template, registry.catalog("es"), profile)


class LanguageTests(unittest.TestCase):
    def test_default_language_is_spanish_and_catalog_driven(self) -> None:
        registry = ConfigRegistry()
        for profile_id in ("general_overview", "developer_technical"):
            self.assertEqual(registry.profile(profile_id).language, "es")
        self.assertIn("propósito", registry.catalog("es").text("purpose_missing"))

    def test_no_language_suffixed_functions(self) -> None:
        for path in PACKAGE_DIR.glob("*.py"):
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"def \w+_(es|en)\(")

    def test_unknown_language_falls_back_with_warning(self) -> None:
        registry = ConfigRegistry()
        catalog = registry.catalog("xx")
        self.assertEqual(catalog.text("purpose_missing"), registry.catalog("es").text("purpose_missing"))
        self.assertTrue(any("xx" in w for w in registry.warnings))

    def test_second_catalog_can_be_added_as_data(self) -> None:
        with tempfile.TemporaryDirectory() as custom:
            (Path(custom) / "i18n").mkdir()
            (Path(custom) / "i18n" / "en.json").write_text(json.dumps({"purpose_missing": "Unknown purpose."}), encoding="utf-8")
            catalog = ConfigRegistry(custom).catalog("en")
            self.assertEqual(catalog.text("purpose_missing"), "Unknown purpose.")
            self.assertIn("código fuente", catalog.text("generated_note"))  # falls back to es


class InterpretedTests(unittest.TestCase):
    def test_interpreted_section_is_labeled_with_origin_and_neutral_phrase_removed(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            sections = parse_interpreted_sections([{"target": "system", "content": "Gestiona beneficios.", "origin": "Analista humano", "created_at": "2026-01-01"}])
            result = generate_documentation_v52(_source(), out, interpreted=sections)
            text = (result.output_dir / "general" / "README.md").read_text(encoding="utf-8")
            self.assertIn("Contenido interpretado", text)
            self.assertIn("Analista humano", text)
            self.assertIn("Gestiona beneficios.", text)
            self.assertNotIn(PURPOSE_PHRASE, text)
            self.assertIn("Qué se analizó", text)  # deterministic content is still there

    def test_interpreted_requires_origin(self) -> None:
        with self.assertRaises(ConfigError):
            parse_interpreted_sections([{"target": "system", "content": "x", "origin": "", "created_at": "d"}])

    def test_empty_source_still_generates_useful_documents(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(source_from_indexes({}), out)
            self.assertTrue((result.output_dir / "general" / "README.md").is_file())
            self.assertIn(PURPOSE_PHRASE, (result.output_dir / "general" / "README.md").read_text(encoding="utf-8"))


class RendererAndPartitionTests(unittest.TestCase):
    def test_partition_by_items(self) -> None:
        ranges = partition_ranges([10] * 7, PartitionPolicy(3, 10**9), overhead=0)
        self.assertEqual(ranges, [(0, 3), (3, 6), (6, 7)])

    def test_partition_by_bytes(self) -> None:
        ranges = partition_ranges([40] * 6, PartitionPolicy(1000, 100), overhead=0)
        self.assertEqual(ranges, [(0, 2), (2, 4), (4, 6)])

    def test_oversize_row_is_alone_and_never_split(self) -> None:
        ranges = partition_ranges([10, 500, 10], PartitionPolicy(100, 100), overhead=0)
        self.assertEqual(ranges, [(0, 1), (1, 2), (2, 3)])

    def test_partition_is_deterministic(self) -> None:
        sizes = [17, 3, 99, 4, 4, 60, 61, 1]
        policy = PartitionPolicy(4, 120)
        self.assertEqual(partition_ranges(sizes, policy), partition_ranges(sizes, policy))

    def test_engine_partitions_by_items_with_navigation_links(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(30), out, partition_override=PartitionPolicy(8, 10**9))
            parts = sorted((result.output_dir / "developer" / "modules" / "WebA").glob("detail-flows-part-*.md"))
            self.assertGreaterEqual(len(parts), 4)
            second = parts[1].read_text(encoding="utf-8")
            self.assertIn("Anterior", second)
            self.assertIn("Siguiente", second)
            self.assertIn(parts[0].name, second)
            self.assertIn("Índice", parts[0].read_text(encoding="utf-8"))
            self.assertNotIn("Siguiente", parts[-1].read_text(encoding="utf-8"))
            for part in parts:
                self.assertLessEqual(sum(1 for line in part.read_text(encoding="utf-8").splitlines() if line.startswith("| `WebA")), 8)

    def test_engine_partitions_by_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(_source(40), out, partition_override=PartitionPolicy(10**6, 2500))
            parts = sorted((result.output_dir / "developer" / "modules" / "WebA").glob("detail-flows-part-*.md"))
            self.assertGreater(len(parts), 1)

    def test_oversize_element_is_written_alone_with_warning_not_truncated(self) -> None:
        source = _source(3)
        source["functional_flows"][0]["handler"] = "H" * 400
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(source, out, partition_override=PartitionPolicy(100, 1000))
            self.assertTrue(any("supera el límite" in w for w in result.warnings))
            self.assertIn("H" * 400, _all_texts(result.output_dir / "developer" / "modules" / "WebA"))

    def test_markdown_escaping_is_the_renderers_job(self) -> None:
        text = format_text(Text.of("Valor {v} y `{c}`", {"v": "a|b*c<d>", "c": "x`y"}))
        self.assertIn("a\\|b\\*c\\<d\\>", text)
        self.assertIn("`x'y`", text)

    def test_table_cells_escape_pipes(self) -> None:
        source = _source(2)
        source["functional_flows"][0]["handler"] = "a|b"
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(source, out)
            self.assertIn("a\\|b", (result.output_dir / "developer" / "modules" / "WebA.md").read_text(encoding="utf-8"))


class ProductionIntegrationTests(unittest.TestCase):
    def test_documentation_stage_writes_v52_and_keeps_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            outcome = stages.render_documentation(out, _source())
            self.assertIn("documentation_v52/README.md", outcome.written)
            self.assertTrue((Path(out) / "documentation_v52" / "developer" / "README.md").is_file())
            self.assertTrue((Path(out) / "documentation").is_dir())
            self.assertNotIn("documentation_v52", [name for name, _ in outcome.failures])

    def test_v52_failure_is_reported_not_swallowed_and_legacy_still_written(self) -> None:
        with tempfile.TemporaryDirectory() as out, mock.patch.object(stages, "generate_documentation_v52", side_effect=RuntimeError("boom")):
            outcome = stages.render_documentation(out, _source())
            self.assertIn(("documentation_v52", "RuntimeError: boom"), outcome.failures)
            self.assertTrue((Path(out) / "documentation").is_dir())


class TransformerTests(unittest.TestCase):
    def test_unassigned_flows_get_their_own_declared_module(self) -> None:
        source = _source(2)
        source["functional_flows"][0]["project_sequence"] = []
        source["entry_points"][0]["project"] = None
        model = AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source)
        self.assertTrue(any(m.values["path"] == "" for m in model.modules))
        self.assertIn("gap.flows_without_project", model.gaps)

    def test_module_is_project_and_never_invented_business_grouping(self) -> None:
        model = AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(_source())
        self.assertEqual({m.values["path"] for m in model.modules if m.values["path"]}, {"WebA.vbproj", "bl\\blA\\blA.vbproj"})
        self.assertIn("gap.no_business_purpose", model.gaps)

    def test_transformer_does_not_mutate_evidence(self) -> None:
        source = _source()
        snapshot = json.dumps(source, sort_keys=True)
        AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source)
        self.assertEqual(json.dumps(source, sort_keys=True), snapshot)

    def test_module_file_names_are_unique_case_insensitively(self) -> None:
        source = _source()
        source["projects"] += [
            {"name": "webA", "path": "other\webA.vbproj", "output_type": "Library"},
            {"name": "WEBA", "path": "x\WEBA.vbproj", "output_type": "Library"},
        ]
        model = AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(source)
        slugs = [m.slug.lower() for m in model.modules]
        self.assertEqual(len(slugs), len(set(slugs)))
        with tempfile.TemporaryDirectory() as out:
            result = generate_documentation_v52(source, out)
            modules = [name for name in result.files if name.startswith("developer/modules/") and name.count("/") == 2]
            self.assertEqual(len(modules), len(model.modules))

    def test_config_paths_are_noted_not_classified(self) -> None:
        model = AudienceTransformer(ConfigRegistry().noise_policy("default")).transform(_source())
        markers = {i.values["path"]: i.values["marker"] for i in model.slots["configs"]}
        self.assertEqual(markers["Web.config"], "")
        self.assertEqual(markers["Backup\\Web.config"], "Backup")
        self.assertIn("gap.config_ambiguity", model.gaps)


if __name__ == "__main__":
    unittest.main()
