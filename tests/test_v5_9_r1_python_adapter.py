"""V5.9-R1: python-generic technology adapter, coexistence with vbnet-webforms-oracle, cross-tech contract and leakage guards.

Synthetic fixtures only here (unit tests); the real-corpus pilot evidence lives in docs/V5/V5_9_R1_*.
"""
from __future__ import annotations

import ast
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.adapters.contracts import AdapterRegistry, AdapterSelectionError
from legacy_documenter.adapters.python_generic import analysis, extraction, resolution
from legacy_documenter.adapters.python_generic.adapter import PythonGenericAdapter
from legacy_documenter.adapters.python_generic.source_parser import module_name, parse_python_source
from legacy_documenter.adapters.vbnet_webforms_oracle.adapter import ReferenceAdapter
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.consumers.facade import ConsumerFacade
from legacy_documenter.evidence import entities as core_entities
from legacy_documenter.evidence.invariants import validate_evidence
from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES, semantic_content_sha256
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.main import analyze_repository
from legacy_documenter.scanner.file_classifier import FileClassifier
from legacy_documenter.versions import ANALYZER_VERSION

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "legacy_documenter"
ADAPTER_DIR = PACKAGE / "adapters" / "python_generic"
VB_FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"

FILES = {
    "pkg/__init__.py": "from .service import Service\n",
    "pkg/util.py": "def clean(value):\n    return value.strip()\n\n\nclass Helper:\n    def __init__(self):\n        self.items = []\n\n    def add(self, item):\n        self.items.append(clean(item))\n",
    "pkg/base.py": "class Base:\n    def shared(self):\n        return 1\n",
    "pkg/service.py": (
        "import json\nimport requests\nfrom pathlib import Path\nfrom . import util\nfrom .util import Helper, clean\nfrom .base import Base\n\n\n"
        "class Service(Base):\n    def __init__(self):\n        self.helper = Helper()\n\n    def run(self, path):\n        self.helper.add('x')\n"
        "        text = open(path).read()\n        Path(path).write_text(clean(text))\n        self.shared()\n        self.step()\n"
        "        util.clean(text)\n        json.dumps({})\n        requests.get('http://x')\n        unknown_object.method()\n        return len(text)\n\n"
        "    def step(self):\n        return clean(' y ')\n"
    ),
    "app.py": "import sys\nfrom pkg.service import Service\n\n\ndef main():\n    Service().run('data.txt')\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())\n",
    "tools/runner.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    pass\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n",
    "broken.py": "def oops(:\n",
}


CLEAN_FILES = {k: v for k, v in FILES.items() if k != "broken.py"}


def write_repo(root: Path, files: dict[str, str] = FILES) -> Path:
    for relative, text in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def extract(root: Path, cache=None):
    scan = stages.scan_repository(root, None)
    return scan, PythonGenericAdapter().extract(scan.files, scan.root, cache)


class PythonCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = write_repo(self.tmp / "repo")
        self.scan, self.outcome = extract(self.repo)
        self.adapter = PythonGenericAdapter()
        self.call_outcome = self.adapter.resolve_calls(self.outcome.calls, self.outcome.symbols)
        self.resolved, self.dependencies = self.call_outcome

    def calls(self, owner_suffix: str, method: str) -> list[dict]:
        return [c for g in self.resolved for c in g["calls"] if c["containing_class"].endswith(owner_suffix) and c["containing_method"] == method]

    def call(self, owner_suffix: str, method: str, expression: str) -> dict:
        return next(c for c in self.calls(owner_suffix, method) if c["expression"] == expression)


class ApplicabilityTests(PythonCase):
    def test_classifier_and_selection(self) -> None:
        self.assertEqual(FileClassifier().classify(Path("a/b.py")), "python_source")
        registry = AdapterRegistry([ReferenceAdapter(), PythonGenericAdapter()])
        self.assertEqual(registry.select({"python_source", "other"}).descriptor.adapter_id, "python-generic")
        self.assertEqual(registry.select({"vb_source", "aspx", "other"}).descriptor.adapter_id, "vbnet-webforms-oracle")
        self.assertIsNone(registry.select({"other", "xml"}))
        with self.assertRaises(AdapterSelectionError):
            registry.select({"python_source", "vb_source"})  # mixed repos fail clearly, never guess
        self.assertEqual(registry.get("python-generic").descriptor.cache_identity, ("python-generic", "1.0"))

    def test_wrong_adapter_is_not_applicable(self) -> None:
        vb_scan = stages.scan_repository(VB_FIXTURE, None)
        python_outcome = PythonGenericAdapter().extract(vb_scan.files, vb_scan.root)
        self.assertEqual((python_outcome.symbols, python_outcome.projects, python_outcome.calls, python_outcome.errors), ([], [], [], []))
        vb_outcome = ReferenceAdapter().extract(self.scan.files, self.scan.root)
        self.assertEqual((vb_outcome.symbols, vb_outcome.projects, vb_outcome.calls), ([], [], []))
        self.assertIs(stages.adapter_of(self.outcome).__class__, PythonGenericAdapter)
        self.assertIs(stages.adapter_of(vb_outcome).__class__, ReferenceAdapter)
        with self.assertRaises(ValueError) as ctx:
            stages.extract_repository([mock.Mock(file_type="css", relative_path="a.css")], self.repo)
        self.assertIn("UNSUPPORTED_TECHNOLOGY", str(ctx.exception))


class ParsingTests(PythonCase):
    def test_module_names_projects_and_structure(self) -> None:
        self.assertEqual(module_name("pkg\\__init__.py"), "pkg")
        self.assertEqual(module_name("pkg/service.py"), "pkg.service")
        self.assertEqual({p["name"] for p in self.outcome.projects}, {"(root)", "pkg", "tools"})
        pkg = next(p for p in self.outcome.projects if p["name"] == "pkg")
        self.assertEqual(pkg["path"].replace("\\", "/"), "pkg/__init__.py")
        self.assertEqual(sorted(i.replace("\\", "/") for i in pkg["compile_items"]), ["__init__.py", "base.py", "service.py", "util.py"])
        self.assertEqual([r["include"] for r in pkg["assembly_references"]], ["requests"])  # stdlib and internal imports are not external packages
        root = next(p for p in self.outcome.projects if p["name"] == "(root)")
        self.assertEqual([r["name"] for r in root["project_references"]], ["pkg"])
        kinds = {(s["name"], s["kind"]) for s in self.outcome.symbols}
        self.assertIn(("pkg.service", "module"), kinds)
        self.assertIn(("pkg.service.Service", "class"), kinds)
        self.assertIn(("pkg.util.Helper", "class"), kinds)

    def test_members_imports_and_entries(self) -> None:
        service = next(s for s in self.outcome.symbols if s["name"] == "pkg.service.Service")
        self.assertEqual([m["name"] for m in service["members"]], ["__init__", "run", "step"])
        self.assertEqual(service["inherits"], ["Base"])
        group = next(g for g in self.outcome.calls if g["file"].replace("\\", "/") == "pkg/service.py")
        self.assertTrue(any(i["level"] == 1 and i["name"] == "Helper" for i in group["imports"]))
        entries = {e["file"].replace("\\", "/"): e["entries"] for e in self.outcome.web_events}
        self.assertEqual(entries["app.py"][0]["callee_chain"], ["main"])  # sys.exit(...) only wraps the real entry
        self.assertEqual(entries["tools/runner.py"][0]["callee_chain"], ["unittest", "main"])

    def test_unparseable_file_is_an_error_not_a_crash(self) -> None:
        self.assertEqual([e["file"] for e in self.outcome.errors], ["broken.py"])
        self.assertEqual(self.outcome.errors[0]["error"], "SyntaxError at line 1")  # class and position only, never source text
        self.assertNotIn("oops", json.dumps(self.outcome.errors))

    def test_extraction_is_deterministic(self) -> None:
        _, again = extract(self.repo)
        self.assertEqual(json.dumps(again.__dict__, sort_keys=True), json.dumps(self.outcome.__dict__, sort_keys=True))

    def test_nested_scopes_and_decorators(self) -> None:
        source = "import os\n\n\ndef outer():\n    def inner():\n        os.remove('a')\n    inner()\n\n\nclass A:\n    class B:\n        def m(self):\n            pass\n\n    @staticmethod\n    def s():\n        pass\n"
        parsed = parse_python_source(source, "m.py")
        self.assertEqual([s["name"] for s in parsed["symbols"]], ["m", "m.A", "m.A.B"])
        self.assertEqual(next(m for m in parsed["symbols"][1]["members"] if m["name"] == "s")["shared"], True)
        remove = next(c for c in parsed["calls"] if c["expression"] == "os.remove(...)")
        self.assertEqual((remove["containing_class"], remove["containing_method"]), ("m", "outer"))  # closures belong to the enclosing function


class ResolutionTests(PythonCase):
    def test_internal_resolution_is_confirmed(self) -> None:
        self.assertEqual(self.call("pkg.service.Service", "run", "self.helper.add(...)")["confidence"], "unresolved")  # attribute of unknown type
        step = self.call("pkg.service.Service", "run", "self.step(...)")
        self.assertEqual((step["confidence"], step["resolved_target"]), ("confirmed", "pkg.service.Service.step"))
        inherited = self.call("pkg.service.Service", "run", "self.shared(...)")
        self.assertEqual(inherited["resolved_target"], "pkg.base.Base.shared")  # statically known base class
        self.assertEqual(self.call("pkg.service.Service", "run", "util.clean(...)")["resolved_target"], "pkg.util.clean")
        self.assertEqual(self.call("pkg.service.Service", "step", "clean(...)")["resolved_target"], "pkg.util.clean")
        constructor = self.call("pkg.service.Service", "__init__", "Helper(...)")
        self.assertEqual((constructor["resolution_kind"], constructor["resolved_target"]), ("instantiation", "pkg.util.Helper.__init__"))
        self.assertEqual(self.call("app", "main", "Service(...)")["resolution_kind"], "instantiation")  # Service defines __init__

    def test_external_and_unresolved_are_not_invented(self) -> None:
        for expression in ("json.dumps(...)", "requests.get(...)", "len(...)", "open(...)"):
            call = self.call("pkg.service.Service", "run", expression)
            self.assertEqual((call["resolution_kind"], call["resolved_target"]), ("external", None), expression)
        unknown = self.call("pkg.service.Service", "run", "unknown_object.method(...)")
        self.assertEqual((unknown["resolution_kind"], unknown["confidence"], unknown["resolved_target"]), ("unresolved", "unresolved", None))
        external = self.call("pkg.service.Service", "run", "requests.get(...)")
        self.assertEqual(external["external_kind"], "third_party")
        self.assertEqual(self.call("pkg.service.Service", "run", "json.dumps(...)")["external_kind"], "stdlib")

    def test_entries_confirmed_only_when_callee_is_internal(self) -> None:
        entry_points, bindings, _ = self.adapter.resolve_entries([], self.outcome.symbols, self.outcome.web_events, self.resolved)
        by_file = {e["webform"].replace("\\", "/"): e for e in entry_points}
        self.assertEqual((by_file["app.py"]["confidence"], by_file["app.py"]["handler_method"]), ("confirmed", "app.main"))
        self.assertEqual((by_file["tools/runner.py"]["confidence"], by_file["tools/runner.py"]["handler_method"]), ("unresolved", None))
        self.assertEqual({b["id"][4:] for b in bindings}, {e["id"][3:] for e in entry_points})

    def test_file_operations_distinguish_confirmed_from_inferred(self) -> None:
        records, procedures, sql, params, dependencies = self.adapter.resolve_database(self.outcome.data_access_indexes, self.outcome.projects)
        by_kind = {(r["operation_kind"], r["confidence"], r["provider"]) for r in records}
        self.assertIn(("file_read", "confirmed", "builtins.open"), by_kind)
        self.assertIn(("file_write", "inferred", "pathlib_method_name"), by_kind)  # receiver type unknown: never promoted
        self.assertEqual((procedures, sql, params), ([], [], []))
        self.assertEqual(len({r["id"] for r in records}), len(records))
        self.assertTrue(all(d["dependency_type"] == "Method -> DataAccessOperation" for d in dependencies))


class FlowAndEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = write_repo(self.tmp / "repo")
        self.out = self.tmp / "out"
        analyze_repository(self.repo, self.out)
        self.index = lambda name: json.loads((self.out / "index" / f"{name}.json").read_text(encoding="utf-8"))
        self.evidence = lambda name: json.loads((self.out / "evidence" / f"{name}.json").read_text(encoding="utf-8"))

    def test_flows_reach_file_operations_and_keep_unresolved(self) -> None:
        flows, paths = self.index("functional_flows"), self.index("functional_paths")
        self.assertEqual(len(flows), 1)  # only app.py's entry resolves internally
        self.assertEqual(flows[0]["start_method"] if "start_method" in flows[0] else flows[0]["start_ref"], "app.main")
        terminals = {p["terminal_type"] for p in paths}
        self.assertIn("data_operation", terminals)
        self.assertIn("unresolved_boundary", terminals)  # unknown_object.method(...) is preserved, not dropped
        self.assertTrue(all(p["confidence"] in {"confirmed", "inferred", "unresolved"} for p in paths))
        self.assertTrue(self.index("flow_unresolved"))

    def test_normalized_evidence_is_valid_neutral_and_deterministic(self) -> None:
        repository = self.index("repository")
        indexes = {name: self.index(name) for name in ("files", "projects", "symbols", "calls", "flow_unresolved", "functional_dependencies", "entry_points",
                                                       "event_bindings", "functional_flows", "functional_paths", "data_access", "data_parameters", "dependencies",
                                                       "configuration", "errors", "logical_symbols", "flow_summary")}
        indexes["repository"] = repository
        first = PythonGenericAdapter().normalize(indexes, repo_root=self.repo)
        second = PythonGenericAdapter().normalize(indexes, repo_root=self.repo)
        validate_evidence(first)  # I-1 unique ids, sha256, I-4/I-5 provenance
        self.assertEqual([c.id for c in first.components], [c.id for c in second.components])
        self.assertEqual([c.id for c in first.call_identities], [c.id for c in second.call_identities])
        self.assertEqual({c.component_kind for c in first.components}, {"module", "class"})
        self.assertEqual({d.dependency_kind for d in first.external_dependencies}, {"package"})
        self.assertTrue(all(a.adapter_id == "python-generic" and a.sha256 for a in first.source_artifacts))
        self.assertTrue(all(c.provenance for c in first.components + first.call_identities))
        self.assertEqual(len(first.call_identities), sum(len(g["calls"]) for g in indexes["calls"]))
        self.assertEqual(first.data_objects, [])  # no stored procedures / SQL: nothing invented

    def test_pipeline_outputs_use_the_common_contracts(self) -> None:
        for name in ("components", "call_identities", "external_dependencies", "functional_paths", "entry_points"):
            self.assertTrue((self.out / "evidence" / f"{name}.json").is_file(), name)


class CacheTests(PythonCase):
    class MemoryCache:
        def __init__(self) -> None:
            self.records: dict = {}
            self.hits = self.misses = 0

        def lookup(self, path):
            if path in self.records:
                self.hits += 1
                return json.loads(json.dumps(self.records[path]))
            self.misses += 1
            return None

        def store(self, path, record, cacheable):
            if cacheable:
                self.records[path] = json.loads(json.dumps(record))

        def record_extraction_seconds(self, seconds):
            pass

    def test_unchanged_files_are_reused_and_output_is_identical(self) -> None:
        cache = self.MemoryCache()
        _, cold = extract(self.repo, cache)
        self.assertEqual((cache.hits, cache.misses), (0, 7))
        _, warm = extract(self.repo, cache)
        self.assertEqual((cache.hits, cache.misses), (7, 7))
        self.assertEqual(json.dumps(cold.__dict__, sort_keys=True), json.dumps(warm.__dict__, sort_keys=True))

    def test_one_changed_file_recomputes_only_that_file(self) -> None:
        cache = self.MemoryCache()
        extract(self.repo, cache)
        cache.hits = cache.misses = 0
        (self.repo / "pkg" / "base.py").write_text("class Base:\n    def shared(self):\n        return 2\n\n    def extra(self):\n        return 3\n", encoding="utf-8")
        for stale in ("pkg/base.py",):
            cache.records.pop(next(k for k in cache.records if k.replace("\\", "/") == stale))
        _, changed = extract(self.repo, cache)
        self.assertEqual((cache.hits, cache.misses), (6, 1))
        self.assertIn("extra", [m["name"] for s in changed.symbols if s["name"] == "pkg.base.Base" for m in s["members"]])

    def test_cache_layer_knows_the_kind_without_assuming_a_technology(self) -> None:
        self.assertIn("python_source", ANALYZED_FILE_TYPES)
        self.assertIsNotNone(semantic_content_sha256(b"x\r\n", "python_source"))
        self.assertEqual(semantic_content_sha256(b"x\r\n", "python_source"), semantic_content_sha256(b"x\n", "python_source"))
        from legacy_documenter.cache.context import build_context
        a = build_context(self.repo, None, 12, adapter_identity=("python-generic", "1.0"))
        b = build_context(self.repo, None, 12, adapter_identity=("vbnet-webforms-oracle", "1.0"))
        self.assertNotEqual(a.analysis_config_fingerprint, b.analysis_config_fingerprint)
        self.assertEqual(ANALYZER_VERSION, 3)  # no analyzer-version bump: record format and contracts are unchanged


class SecurityTests(unittest.TestCase):
    def test_target_is_data_never_executed_or_imported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker.txt"
            repo = write_repo(Path(tmp) / "repo", {
                "evil_module_xyz.py": f"import os\nopen({str(marker)!r}, 'w').write('executed')\nos.system('echo hi')\nraise SystemExit(7)\n",
                "setup.py": "raise RuntimeError('must not run')\n"})
            _, outcome = extract(repo)
            self.assertFalse(marker.exists())
            self.assertNotIn("evil_module_xyz", sys.modules)
            self.assertEqual(outcome.errors, [])
            self.assertTrue(any(s["name"] == "evil_module_xyz" for s in outcome.symbols))

    def test_adapter_package_has_no_execution_network_or_import_machinery(self) -> None:
        banned_imports = {"importlib", "subprocess", "socket", "urllib", "http", "requests", "runpy", "pkgutil", "ctypes", "multiprocessing", "os", "shutil"}
        banned_calls = {"exec", "eval", "compile", "__import__", "system", "popen", "import_module"}
        for path in sorted(ADAPTER_DIR.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse({a.name.split(".")[0] for a in node.names} & banned_imports, path.name)
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or "").split(".")[0], banned_imports, path.name)
                elif isinstance(node, ast.Call):
                    name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                    self.assertNotIn(name, banned_calls, f"{path.name}:{node.lineno}")
        for path in sorted(ADAPTER_DIR.glob("*.py")):
            imports = {n.module or "" for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(n, ast.ImportFrom)}
            for module in imports:
                for banned in ("legacy_documenter.cli", "legacy_documenter.llm", "legacy_documenter.orchestration", "legacy_documenter.consumers",
                               "legacy_documenter.plugins", "legacy_documenter.review", "legacy_documenter.knowledge", "legacy_documenter.context"):
                    self.assertFalse(module.startswith(banned), f"{path.name} imports {module}")


class LeakageAndIndependenceTests(unittest.TestCase):
    ALLOWED_KIND_LABEL = {
        "cache/scope.py", "fingerprints/semantic.py", "scanner/file_classifier.py", "documentation_v52/transform.py", "cli/pipeline_stages.py",
    }

    def test_python_adapter_is_imported_only_by_the_composition_root(self) -> None:
        importers = sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob("*.py")
                           if "adapters/python_generic" not in p.relative_to(PACKAGE).as_posix()
                           and "legacy_documenter.adapters.python_generic" in p.read_text(encoding="utf-8"))
        self.assertEqual(importers, ["cli/pipeline_stages.py"])

    def test_python_specifics_do_not_leak_into_neutral_layers(self) -> None:
        mentioning = sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob("*.py")
                            if p.relative_to(PACKAGE).parts[:2] != ("adapters", "python_generic")
                            and ("python_source" in p.read_text(encoding="utf-8") or "python-generic" in p.read_text(encoding="utf-8")))
        self.assertEqual(sorted(set(mentioning) - self.ALLOWED_KIND_LABEL), [])
        for layer in ("evidence", "context", "cache", "consumers", "plugins", "review", "knowledge", "llm", "orchestration"):
            for path in (PACKAGE / layer).rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("python_generic", text, path)
                self.assertNotIn("python-generic", text, path)

    def test_core_entities_are_unchanged(self) -> None:
        classes = sorted(n for n, o in vars(core_entities).items() if isinstance(o, type) and o.__module__ == core_entities.__name__)
        self.assertEqual(classes, ["CallIdentity", "Component", "DataObject", "ExternalDependency", "Instantiation", "ScanSummary",
                                   "Solution", "SourceArtifact", "UnresolvedBoundary"])  # no PythonModule / PythonFunction / PythonImport

    def test_neutral_layers_do_not_import_the_python_adapter_nor_add_vbnet_imports(self) -> None:
        importers = []
        for layer in ("evidence", "context", "consumers", "plugins", "review", "llm", "documentation_v52", "exporters", "cache", "fingerprints"):
            for path in (PACKAGE / layer).rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("adapters.python_generic", text, path)
                if "legacy_documenter.adapters.vbnet" in text:
                    importers.append(path.relative_to(PACKAGE).as_posix())
        # the only pre-existing V5.4 legacy-import shims; V5.9 adds none
        self.assertEqual(sorted(importers), ["evidence/builder.py", "evidence/projection.py"])


class CrossTechnologyContractTests(unittest.TestCase):
    """Same assertions for both adapters, over the same common pipeline."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp())
        cls.python_repo = write_repo(cls.tmp / "py", CLEAN_FILES)
        cls.runs = {}
        for key, repo in (("vbnet-webforms-oracle", VB_FIXTURE), ("python-generic", cls.python_repo)):
            out = cls.tmp / f"out_{key}"
            with mock.patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider", side_effect=AssertionError("real provider forbidden")):
                result = run_full_pipeline(repo, out, None, 12)
            assert result.status.value == "SUCCESS", (key, result.status)
            cls.runs[key] = out

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, True)

    def evidence(self, key, name):
        return json.loads((self.runs[key] / "evidence" / f"{name}.json").read_text(encoding="utf-8"))

    def test_same_evidence_partitions_ids_and_provenance(self) -> None:
        for key in self.runs:
            manifest = json.loads((self.runs[key] / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["evidence_schema_version"], "1.0", key)
            components = self.evidence(key, "components")
            self.assertTrue(components, key)
            ids = [c["id"] for c in components]
            self.assertEqual(len(ids), len(set(ids)), key)  # I-1
            self.assertTrue(all(c["provenance"] for c in components), key)  # I-4

    def test_each_run_records_its_own_adapter_identity(self) -> None:
        for key in self.runs:
            artifacts = self.evidence(key, "source_artifacts")
            self.assertEqual({a["adapter"]["id"] for a in artifacts}, {key})
            self.assertEqual({a["adapter"]["version"] for a in artifacts}, {"1.0"})

    def test_similar_names_do_not_collide_across_technologies(self) -> None:
        extra = {"main.py": "def main():\n    pass\n\n\ndef run():\n    pass\n\n\nclass Service:\n    pass\n\n\nclass Config:\n    pass\n\n\nif __name__ == '__main__':\n    main()\n"}
        with tempfile.TemporaryDirectory() as tmp:
            repo = write_repo(Path(tmp) / "r", extra)
            out = Path(tmp) / "o"
            analyze_repository(repo, out)
            py = {}
            for name in ("components", "call_identities", "entry_points", "functional_flows", "functional_paths", "data_access"):
                py[name] = {r.get("id") or r.get("path_id") for r in json.loads((out / "evidence" / f"{name}.json").read_text(encoding="utf-8"))}
        for name, py_ids in py.items():
            vb_ids = {r.get("id") or r.get("path_id") for r in self.evidence("vbnet-webforms-oracle", name)}
            self.assertFalse(py_ids & vb_ids, name)

    def test_documentation_uses_the_same_templates_with_a_vocabulary_overlay_only(self) -> None:
        general = (self.runs["python-generic"] / "documentation_v52" / "general" / "README.md").read_text(encoding="utf-8")
        self.assertIn("archivos de código fuente Python", general)
        for forbidden in ("WebForm", "ASPX", "Oracle", "VB.NET", ".vbproj", "pantalla", "solución"):
            self.assertNotIn(forbidden, general)
        vb = (self.runs["vbnet-webforms-oracle"] / "documentation_v52" / "general" / "README.md").read_text(encoding="utf-8")
        self.assertIn("pantallas o controles web", vb)  # the reference adapter keeps the default catalog, byte for byte
        for key in self.runs:  # same profiles, templates and renderer for both: identical file structure of the general profile
            files = sorted(p.name for p in (self.runs[key] / "documentation_v52" / "general").glob("*.md"))
            self.assertEqual(files, ["README.md", "data.md", "external-systems.md", "limitations.md", "modules.md"], key)

    def test_consumer_contract_serves_both_technologies_unchanged(self) -> None:
        for key, out in self.runs.items():
            facade = ConsumerFacade(out)
            flows = json.loads((out / "index" / "functional_flows.json").read_text(encoding="utf-8"))
            self.assertTrue(flows, key)
            result = facade.handle({"consumer_id": "builtin.flow-reader", "contract_version": "1.0", "capability": "READ_FLOW",
                                    "scope": "ENTITIES", "entity_ids": [flows[0]["id"]]})
            self.assertTrue(result.ok, (key, result.error))
            self.assertFalse(result.payload["flows"][0]["partial"])
            ai = facade.handle({"consumer_id": "builtin.ai-context", "contract_version": "1.0", "capability": "READ_AI_CONTEXT",
                                "scope": "ENTITIES", "entity_ids": [flows[0]["id"]], "profile": "SMALL"})
            self.assertTrue(ai.ok, (key, ai.error))
            self.assertEqual(ai.provenance["provider_calls"], 0)
            for profile in ("human-functional", "human-technical"):
                docs = facade.handle({"consumer_id": "builtin.human-docs", "contract_version": "1.0", "capability": "RENDER_HUMAN_DOC",
                                      "scope": "RUN", "profile": profile})
                self.assertTrue(docs.ok, (key, profile, docs.error))
            export = facade.handle({"consumer_id": "builtin.json-export", "contract_version": "1.0", "capability": "EXPORT_JSON", "scope": "RUN"})
            self.assertTrue(export.ok, (key, export.error))

    def test_resolution_module_is_deterministic_helper_free_of_global_state(self) -> None:
        self.assertFalse([n for n in vars(resolution) if n.startswith("_CACHE")])
        self.assertTrue(hasattr(analysis, "PythonFlowResolver"))
        self.assertTrue(hasattr(extraction, "ExtractionOutcome"))


class SegmentationContractTests(unittest.TestCase):
    """CONTROLLED_FIXTURE: a large Python flow segments through the neutral V5.6 contract (the real corpus is covered by the pilot proof)."""

    def test_large_python_flow_is_segmented_without_loss_or_overlap(self) -> None:
        helpers = "".join(f"def step_{i}():\n    open('f{i}.txt').read()\n\n\n" for i in range(40))
        calls = "".join(f"    step_{i}()\n" for i in range(40))
        files = {"big.py": helpers + "def main():\n" + calls + "\n\nif __name__ == '__main__':\n    main()\n"}
        with tempfile.TemporaryDirectory() as tmp:
            repo, out = write_repo(Path(tmp) / "r", files), Path(tmp) / "o"
            analyze_repository(repo, out)
            flow = json.loads((out / "index" / "functional_flows.json").read_text(encoding="utf-8"))[0]
            facade = ConsumerFacade(out)
            base = {"consumer_id": "builtin.flow-reader", "contract_version": "1.0", "scope": "ENTITIES", "entity_ids": [flow["id"]]}
            complete = facade.handle({**base, "capability": "READ_FLOW"})
            all_paths = {p for path in complete.payload["flows"][0]["paths"] for p in path["path_ids"]}
            partial = facade.handle({**base, "capability": "READ_PARTIAL_FLOW", "options": {"max_characters": 12000}})
            self.assertTrue(partial.ok, partial.error)
            segments = partial.payload["flows"][0]["segments"]
            self.assertGreater(len(segments), 1)
            included = [p for s in segments for p in s["included_paths"]]
            self.assertEqual(set(included), all_paths)  # union is the whole flow
            self.assertEqual(len(included), len(set(included)))  # no overlap
            self.assertTrue(all(s["partial"] and s["omitted_paths"] and s["evidence_refs"] and s["parent_flow_id"] == flow["id"] for s in segments))
            self.assertTrue(partial.provenance["partial"])


if __name__ == "__main__":
    unittest.main()
