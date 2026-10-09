"""V5.9-R2: SourceArtifact identity is unique across declared repository identities and stable across roots."""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from legacy_documenter.adapters.python_generic.adapter import PythonGenericAdapter
from legacy_documenter.adapters.vbnet_webforms_oracle.adapter import ReferenceAdapter
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.parser import build_parser
from legacy_documenter.consumers.facade import ConsumerFacade
from legacy_documenter.evidence.identity import normalize_repository_id, sha256_id, source_artifact_id
from legacy_documenter.evidence.invariants import validate_evidence
from legacy_documenter.llm import FakeAIProvider, ProviderConfig
from legacy_documenter.main import analyze_repository
from legacy_documenter.review.service import ApprovalService
from tests.test_v5_9_r1_python_adapter import CLEAN_FILES, VB_FIXTURE, write_repo

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "legacy_documenter"
GITIGNORE = {".gitignore": "bin/\nobj/\n", "app.py": "def main():\n    return 0\n\n\nif __name__ == '__main__':\n    main()\n"}


def evidence(out: Path, name: str):
    return json.loads((out / "evidence" / f"{name}.json").read_text(encoding="utf-8"))


def tree(out: Path) -> dict:
    return {p.relative_to(out).as_posix(): p.read_bytes() for p in sorted((out / "evidence").rglob("*.json"))}


class IdentityFunctionTests(unittest.TestCase):
    def test_undeclared_repository_keeps_the_v51_formula(self) -> None:
        self.assertEqual(source_artifact_id(".gitignore"), sha256_id("SRC", ".gitignore"))
        self.assertEqual(source_artifact_id("a\\b.py"), source_artifact_id("a/b.py"))  # IDENTITY_COMPATIBLE: ids of every existing baseline

    def test_same_path_in_different_repositories_differs_and_same_repository_agrees(self) -> None:
        a, b = source_artifact_id(".gitignore", "repo-a"), source_artifact_id(".gitignore", "repo-b")
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, source_artifact_id(".gitignore"))  # a declared namespace never aliases the undeclared one
        self.assertEqual(a, source_artifact_id(".gitignore", "repo-a"))
        self.assertEqual(source_artifact_id("x\\y.py", "repo-a"), source_artifact_id("x/y.py", "repo-a"))

    def test_repository_id_is_a_name_never_a_path(self) -> None:
        for good in ("legacy-v4.2:e9e3d60", "SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60", "a"):
            self.assertEqual(normalize_repository_id(good), good)
        for bad in ("C:\\dev\\repo", "/home/user/repo", "../repo", "my repo", "", "a" * 129, "usuario\\repo", 5):
            with self.subTest(bad), self.assertRaises(ValueError):
                normalize_repository_id(bad)
        self.assertIsNone(normalize_repository_id(None))


class CollisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_analysis(self, name: str, files: dict, repository_id: str | None, root_name: str | None = None) -> Path:
        repo = write_repo(self.tmp / (root_name or f"src_{name}") / "repo", files)
        out = self.tmp / f"out_{name}"
        analyze_repository(repo, out, repository_id=repository_id)
        return out

    def src_ids(self, out: Path) -> dict:
        return {a["path"]: a["id"] for a in evidence(out, "source_artifacts")}

    def test_same_relative_path_different_repository_identity_differs(self) -> None:
        a = self.run_analysis("a", GITIGNORE, "repo-a")
        b = self.run_analysis("b", GITIGNORE, "repo-b")
        self.assertNotEqual(self.src_ids(a)[".gitignore"], self.src_ids(b)[".gitignore"])
        self.assertFalse(set(self.src_ids(a).values()) & set(self.src_ids(b).values()))  # no SourceArtifact id shared at all
        undeclared = self.run_analysis("u", GITIGNORE, None)
        self.assertEqual(self.src_ids(undeclared)[".gitignore"], sha256_id("SRC", ".gitignore"))  # compat: V5.1 id

    def test_same_repository_identity_other_absolute_root_gives_identical_evidence(self) -> None:
        a = self.run_analysis("a", CLEAN_FILES, "repo-a", root_name="one/deeper/place")
        b = self.run_analysis("b", CLEAN_FILES, "repo-a", root_name="completely_other_root")
        self.assertEqual(self.src_ids(a), self.src_ids(b))
        ta, tb = tree(a), tree(b)
        physical = {"evidence/scan_summary.json", "evidence/EVIDENCE_MANIFEST.json"}  # the scan summary carries the physical root (informative, not identity); the manifest hashes it
        self.assertEqual({k: v for k, v in ta.items() if k not in physical}, {k: v for k, v in tb.items() if k not in physical})
        self.assertEqual(set(ta), set(tb))

    def test_no_machine_specific_data_in_identity(self) -> None:
        out = self.run_analysis("a", CLEAN_FILES, "repo-a", root_name="Usuario_Secreto_X/work")
        for name, data in tree(out).items():
            if name.endswith("scan_summary.json"):
                continue
            self.assertNotIn(b"Usuario_Secreto_X", data, name)
        manifest = evidence(out, "EVIDENCE_MANIFEST")
        self.assertEqual(manifest["repository_id"], "repo-a")

    def test_undeclared_run_does_not_mention_a_repository_id(self) -> None:
        out = self.run_analysis("u", CLEAN_FILES, None)
        self.assertNotIn("repository_id", evidence(out, "EVIDENCE_MANIFEST"))
        self.assertNotIn("repository_id", json.loads((out / "index" / "repository.json").read_text(encoding="utf-8")))


class DerivedIdentityTests(unittest.TestCase):
    """Every entity that points at a SourceArtifact resolves against the namespaced ids, for both adapters."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp())
        cls.runs = {}
        for key, repo in (("vbnet-webforms-oracle", VB_FIXTURE), ("python-generic", write_repo(cls.tmp / "py", CLEAN_FILES))):
            out = cls.tmp / f"out_{key}"
            with mock.patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider", side_effect=AssertionError("real provider forbidden")):
                result = run_full_pipeline(repo, out, None, 12, repository_id=f"pilot:{key}")
            assert result.status.value == "SUCCESS", (key, result.status)
            cls.runs[key] = out

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, True)

    def test_derived_references_resolve(self) -> None:
        for key, out in self.runs.items():
            artifacts = {a["id"] for a in evidence(out, "source_artifacts")}
            self.assertTrue(artifacts, key)
            for name, field in (("components", "source_ref"), ("call_identities", "source_artifact"), ("instantiations", "source_artifact")):
                refs = {r[field] for r in evidence(out, name) if r.get(field)}
                self.assertTrue(refs <= artifacts, (key, name, sorted(refs - artifacts)[:3]))
            for name in ("components", "call_identities", "projects", "solutions", "data_objects", "instantiations", "external_dependencies"):
                for record in evidence(out, name):
                    for ref in record.get("provenance", []):
                        if ref["ref_type"] in ("source", "source_span"):
                            self.assertIn(ref["source_id"], artifacts, (key, name))

    def test_other_id_families_are_untouched_by_the_namespace(self) -> None:
        for key, out in self.runs.items():
            other = out.parent / f"plain_{key}"
            repo = VB_FIXTURE if key == "vbnet-webforms-oracle" else out.parent / "py"
            run_full_pipeline(repo, other, None, 12)
            for name in ("entry_points", "functional_flows", "functional_paths", "data_access", "event_bindings"):
                self.assertEqual(evidence(out, name), evidence(other, name), (key, name))  # UNAFFECTED_BY_DESIGN
            for name in ("components", "call_identities", "projects", "external_dependencies"):
                self.assertEqual([r["id"] for r in evidence(out, name)], [r["id"] for r in evidence(other, name)], (key, name))  # ids path-based, unchanged
            self.assertNotEqual({a["id"] for a in evidence(out, "source_artifacts")}, {a["id"] for a in evidence(other, "source_artifacts")})

    def test_evidence_invariants_hold_with_a_declared_repository(self) -> None:
        for key, out in self.runs.items():
            indexes = {n: json.loads((out / "index" / f"{n}.json").read_text(encoding="utf-8")) for n in (
                "repository", "files", "solutions", "projects", "symbols", "webforms", "calls", "flow_unresolved", "functional_dependencies", "stored_procedures",
                "sql_operations", "entry_points", "event_bindings", "functional_flows", "functional_paths", "data_access", "data_parameters", "dependencies",
                "configuration", "errors", "logical_symbols", "flow_summary")}
            adapter = PythonGenericAdapter() if key == "python-generic" else ReferenceAdapter()
            built = adapter.normalize(indexes, repo_root=indexes["repository"]["root"])
            validate_evidence(built)  # I-1, sha256, I-4/I-5 (provenance resolves), schema 1.0
            again = adapter.normalize(indexes, repo_root=indexes["repository"]["root"])
            self.assertEqual([a.id for a in built.source_artifacts], [a.id for a in again.source_artifacts])
            self.assertEqual(indexes["repository"]["repository_id"], f"pilot:{key}")

    def test_consumers_are_unchanged_on_a_namespaced_run(self) -> None:
        for key, out in self.runs.items():
            facade = ConsumerFacade(out)
            flows = json.loads((out / "index" / "functional_flows.json").read_text(encoding="utf-8"))
            base = {"contract_version": "1.0", "scope": "ENTITIES", "entity_ids": [flows[0]["id"]]}
            self.assertTrue(facade.handle({**base, "consumer_id": "builtin.flow-reader", "capability": "READ_FLOW"}).ok, key)
            self.assertTrue(facade.handle({**base, "consumer_id": "builtin.ai-context", "capability": "READ_AI_CONTEXT", "profile": "SMALL"}).ok, key)
            ids = [json.loads((out / "index" / "entry_points.json").read_text(encoding="utf-8"))[0]["id"]]
            self.assertTrue(facade.handle({**base, "entity_ids": ids, "consumer_id": "builtin.evidence-reader", "capability": "READ_EVIDENCE"}).ok, key)
            self.assertTrue(facade.handle({"consumer_id": "builtin.json-export", "contract_version": "1.0", "capability": "EXPORT_JSON", "scope": "RUN"}).ok, key)


class CacheAndReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = write_repo(self.tmp / "repo", CLEAN_FILES)

    def test_extraction_cache_does_not_depend_on_the_repository_id(self) -> None:
        out = self.tmp / "out"
        run_full_pipeline(self.repo, out, None, 12, repository_id="repo-a")
        before = {a["id"] for a in evidence(out, "source_artifacts")}
        run_full_pipeline(self.repo, out, None, 12, repository_id="repo-b")  # same output dir, other declared identity
        metrics = json.loads((out / "_cache_v53/RUN_METRICS.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["session_mode"], "warm")
        self.assertEqual(metrics["extraction_cache"]["extraction_cache_misses"], 0)  # extraction results do not carry SRC ids
        after = {a["id"] for a in evidence(out, "source_artifacts")}
        self.assertFalse(before & after)  # evidence is always rebuilt: no stale ids survive the identity change
        self.assertEqual(evidence(out, "EVIDENCE_MANIFEST")["repository_id"], "repo-b")

    def test_determinism_same_repository_same_bytes(self) -> None:
        a, b = self.tmp / "a", self.tmp / "b"
        run_full_pipeline(self.repo, a, None, 12, repository_id="repo-a")
        run_full_pipeline(self.repo, b, None, 12, repository_id="repo-a")
        self.assertEqual(tree(a).keys(), tree(b).keys())
        skip = {"evidence/scan_summary.json", "evidence/EVIDENCE_MANIFEST.json"}  # physical roots differ between the two output dirs' runs? no: same root; kept for symmetry
        self.assertEqual({k: v for k, v in tree(a).items() if k not in skip}, {k: v for k, v in tree(b).items() if k not in skip})

    def test_review_baseline_snapshot_and_canonical_chain_remain_valid(self) -> None:
        from legacy_documenter.context.ai_projection import package_reference_ids

        class Grounded(FakeAIProvider):
            def structured_generate(self, request, schema=None):
                refs = sorted(r for r in package_reference_ids(request.context) if str(r).startswith(("DAO-", "PATH-"))) or sorted(package_reference_ids(request.context))
                self.structured = {"findings": [{"statement": "The traced flow reaches a file operation.", "confidence": "UNCERTAIN", "evidence_refs": refs[:1]}]}
                return super().structured_generate(request, schema)

        out = self.tmp / "ai"
        provider = Grounded(ProviderConfig("FAKE", "fake-r2", "offline", context_window=16000, max_output_tokens=2000, capabilities={"structured_output": True}))
        with mock.patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider", side_effect=AssertionError("real provider forbidden")):
            result = run_full_pipeline(self.repo, out, None, 12, allow_ai_interpretation=True, ai_provider=provider, repository_id="repo-a")
        self.assertEqual(result.proposal_count, 1)
        proposal = json.loads((out / "proposals/AI_PROPOSALS.json").read_text(encoding="utf-8"))["proposals"][0]
        copy = self.tmp / "review"
        for sub in ("index", "proposals"):
            shutil.copytree(out / sub, copy / sub)
        service = ApprovalService(copy, clock=lambda: "2026-10-08T12:00:00Z")
        baseline = service.prepare(proposal["proposal_id"], "Ana Reviewer")  # refs resolve, fingerprints pinned
        outcome = service.decide(proposal["proposal_id"], "APPROVE", "Ana Reviewer")
        chain = service.store.audit_chain(outcome.decision.decision_id)
        self.assertEqual(chain["baseline"].baseline_id, baseline.baseline_id)
        self.assertEqual(chain["canonical"].canonical_id, outcome.canonical.canonical_id)
        self.assertFalse((out / "knowledge").exists())  # the original artifact is never approved


class CliAndIndependenceTests(unittest.TestCase):
    def test_cli_accepts_a_name_and_rejects_a_path(self) -> None:
        parser = build_parser()
        self.assertEqual(parser.parse_args(["full", "repo", "--repository-id", "pilot:abc"]).repository_id, "pilot:abc")
        self.assertIsNone(parser.parse_args(["analyze", "repo"]).repository_id)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["full", "repo", "--repository-id", "C:\\some\\path"])

    def test_the_fix_is_neutral(self) -> None:
        for path in (PACKAGE / "evidence").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("python_generic", text, path)
            self.assertNotIn("python-generic", text, path)
        for layer in ("cache", "consumers", "review", "llm", "context", "documentation_v52"):
            for path in (PACKAGE / layer).rglob("*.py"):
                self.assertNotIn("adapters.python_generic", path.read_text(encoding="utf-8"), path)

    def test_identity_inputs_exclude_paths_and_machine_data(self) -> None:
        import inspect
        source = inspect.getsource(source_artifact_id)
        for forbidden in ("getcwd", "resolve(", "gethostname", "getuser", "uuid", "time.", "random", "environ"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
