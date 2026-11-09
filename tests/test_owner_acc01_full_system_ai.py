"""Owner acceptance remediation R1 (ACC-01): full-system hierarchical AI interpretation, persistence, resume, projections.

Synthetic compact baseline only. The only providers are offline stubs: real provider calls = 0, scanner/analyzer calls = 0.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))

from system_fixtures import PROJECTS, build_baseline  # noqa: E402

from legacy_documenter.llm.contracts import LLMResponse, ProviderConfig, ProviderError, Usage  # noqa: E402
from legacy_documenter.main import main as cli_main  # noqa: E402
from legacy_documenter.system import machine, planner as P  # noqa: E402
from legacy_documenter.system.inventory import SystemBaselineInvalid, load_inventory  # noqa: E402
from legacy_documenter.system.models import (CLAIM_STATUSES, FINAL_STATES, HUMAN_STATUS_VALUES, KINDS, LEAK, Fact, output_schema,  # noqa: E402
                                              validate_semantic)
from legacy_documenter.system.orchestrator import RunOptions, run_system_interpretation  # noqa: E402
from legacy_documenter.system.preflight import check_account  # noqa: E402
from legacy_documenter.system.product import ProjectionError, project_system  # noqa: E402
from legacy_documenter.system.store import RequestStore  # noqa: E402
from legacy_documenter.system.stub_provider import StubProvider  # noqa: E402

CFG = ProviderConfig("STUB", "stub-local", "")
POLICY = {"provider_type": "STUB", "model": ""}
_RECORDING: list | None = None


def _audit(event, args):
    if _RECORDING is not None and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        _RECORDING.append(os.fsdecode(args[0]))


sys.addaudithook(_audit)


class Scripted(StubProvider):
    """Stub with failure injection. Never talks to a network or SDK."""

    def __init__(self, *, quota_after=None, unavailable_after=None, raise_after=None, error_for=None, mutate=None):
        super().__init__(CFG)
        self.seen: list[tuple] = []
        self.quota_after, self.unavailable_after, self.raise_after, self.error_for, self.mutate = quota_after, unavailable_after, raise_after, error_for, mutate

    def _fail(self, request, status, code=None):
        err = ProviderError(code or status, "scripted failure", "stub-local", "deterministic-stub") if code else None
        return LLMResponse(request.request_id, "R-" + request.request_id, "stub-local", "deterministic-stub", status, error=err, usage=Usage())

    def generate(self, request):
        kind, entity = self._kind_from(request), request.context["entity"]
        self.seen.append((kind, entity, request.context_package_id))
        n = len(self.seen)
        if self.quota_after is not None and n > self.quota_after:
            return self._fail(request, "RATE_LIMITED", "RATE_LIMITED")
        if self.unavailable_after is not None and n > self.unavailable_after:
            return self._fail(request, "PROVIDER_CONFIGURATION_ERROR", "PROVIDER_CONFIGURATION_ERROR")
        if self.raise_after is not None and n > self.raise_after:
            raise RuntimeError("scripted crash")
        if self.error_for and self.error_for(kind, entity):
            return self._fail(request, "INVALID_STRUCTURED_OUTPUT")
        resp = super().generate(request)
        if self.mutate:
            parsed = self.mutate(kind, resp.parsed_output, request.context["facts"])
            resp.parsed_output, resp.content = parsed, json.dumps(parsed, ensure_ascii=False)
        return resp


class Work(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acc01_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.baseline = build_baseline(self.tmp / "base ñ")
        self.state = self.tmp / "state dir"
        self.out = self.tmp / "out"

    def run_sys(self, provider=None, state=None, **opts):
        return run_system_interpretation(self.baseline, state or self.state, provider or Scripted(), POLICY, RunOptions(**opts))

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli_main(list(map(str, argv)))
            except SystemExit as exc:                      # argparse usage errors
                code = exc.code
        text = out.getvalue()
        return code, (json.loads(text[text.index("{"):]) if "{" in text else {}), err.getvalue()


class InventoryAndPlanningTests(Work):
    def test_full_inventory_enumeration_and_duplicate_identity(self):
        inv = load_inventory(self.baseline)
        self.assertEqual(len(inv.projects), len(PROJECTS))
        self.assertEqual(len(inv.solutions), 2)
        dup = [p for p in inv.projects.values() if p.name == "Shared"]
        self.assertEqual(len(dup), 2)
        self.assertEqual(len({p.display for p in dup}), 2)
        self.assertEqual(len({p.slug for p in inv.projects.values()}), len(inv.projects))
        self.assertFalse(any(".vbproj" in p.display for p in inv.projects.values()))
        orphan = next(p for p in inv.projects.values() if p.name == "Orphan")
        self.assertEqual(orphan.solution_ids, [])

    def test_hierarchical_request_planning_is_bounded(self):
        r = self.run_sys()
        by_kind = r.metrics.by_kind
        for kind in KINDS:
            self.assertGreater(by_kind[kind]["requests"], 0, kind)
        self.assertEqual(by_kind["SYSTEM"]["requests"], 1)
        self.assertEqual(by_kind["SOLUTION"]["requests"], 2)
        total = r.metrics.requests
        self.assertLessEqual(total, len(PROJECTS) * 3 + 4)       # never per source file / per fact
        for rec in RequestStore(self.state).iter_accepted():
            self.assertLessEqual(len(rec["facts"]), 120)

    def test_request_identity_is_stable_and_machine_independent(self):
        other = build_baseline(self.tmp / "elsewhere" / "otra ruta ü")
        ids = []
        for base in (self.baseline, other):
            inv = load_inventory(base)
            a = P.assess(inv, RequestStore(self.tmp / "empty"), POLICY, {})
            ids.append(sorted(i.identity for pc in a.projects.values() for i in pc.items))
        self.assertEqual(ids[0], ids[1])
        self.assertTrue(all(re.fullmatch(r"SYS-[0-9a-f]{40}", x) for x in ids[0]))
        inv = load_inventory(self.baseline)
        plan = P.plan_project(inv, next(p for p in inv.projects.values() if p.name == "WebAlpha"))
        base_id = plan.identity(POLICY)
        self.assertNotEqual(base_id, plan.identity({"provider_type": "STUB", "model": "other"}))
        plan.facts[0] = Fact(plan.facts[0].ref, plan.facts[0].kind, plan.facts[0].certainty, "changed", plan.facts[0].evidence)
        self.assertNotEqual(base_id, plan.identity(POLICY))

    def test_baseline_integrity_and_schema_are_enforced(self):
        part = self.baseline / "evidence" / "projects.json"
        part.write_text(part.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaises(SystemBaselineInvalid) as ctx:
            load_inventory(self.baseline)
        self.assertEqual(ctx.exception.reason, "EVIDENCE_PARTITION_CORRUPT")
        manifest = self.baseline / "evidence" / "EVIDENCE_MANIFEST.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["evidence_schema_version"] = "9.9"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(SystemBaselineInvalid) as ctx:
            load_inventory(self.baseline, "fast")
        self.assertEqual(ctx.exception.reason, "EVIDENCE_SCHEMA_UNSUPPORTED")


class CoverageTests(Work):
    def test_every_project_ends_in_exactly_one_state(self):
        r = self.run_sys()
        self.assertEqual((r.status, r.exit_code), ("COMPLETE", 0))
        states = {p["display"]: p["state"] for p in r.state["projects"]}
        self.assertEqual(len(states), len(PROJECTS))
        self.assertTrue(all(s in FINAL_STATES for s in states.values()))
        self.assertEqual(states["Orphan"], "UNRESOLVED_NO_SOLUTION")
        self.assertEqual(states["EmptyLib"], "MACHINE_ONLY_DOCUMENTED")
        self.assertEqual(states["WebAlpha"], "HUMAN_AND_MACHINE_DOCUMENTED")
        self.assertEqual(sum(r.state["counts"][s] for s in FINAL_STATES), len(PROJECTS))
        self.assertEqual(r.state["pending"], [])
        for entry in r.state["projects"]:
            for key in ("project_id", "stable_identity", "state", "human_documentation_applicable", "provider_request_ids", "semantic_artifact_ids", "solution_ids"):
                self.assertIn(key, entry)
        self.assertNotEqual(*[p["stable_identity"] for p in r.state["projects"] if p["name"] == "Shared"])

    def test_non_ui_projects_are_interpreted_without_inventing_ui(self):
        r = self.run_sys()
        prod = project_system(self.baseline, self.state, self.out)
        projects = {p["display"]: p for p in json.loads((self.out / "ai" / "projects.json").read_text(encoding="utf-8"))}
        for name in ("blAlpha", "blBeta"):
            self.assertEqual(projects[name]["state"], "HUMAN_AND_MACHINE_DOCUMENTED", name)
            self.assertFalse(projects[name]["has_user_interface"], name)
            self.assertEqual(projects[name]["view_set_ids"], [])
        self.assertTrue(projects["WebAlpha"]["has_user_interface"])
        self.assertEqual(prod["validation"]["defects"], 0)
        self.assertFalse((self.out / "human" / "views" / "blalpha.html").exists())

    def test_entities_without_requests_make_none(self):
        r = self.run_sys()
        by = {p["display"]: p for p in r.state["projects"]}
        self.assertEqual(by["Orphan"]["provider_request_ids"], [])
        self.assertEqual(by["EmptyLib"]["provider_request_ids"], [])


class PersistenceAndResumeTests(Work):
    def test_every_exchange_is_persisted_immediately(self):
        r = self.run_sys()
        store = RequestStore(self.state)
        records = list(store.iter_accepted())
        self.assertEqual(len(records), r.metrics.successes)
        for rec in records:
            for key in ("identity", "input_hash", "dependency_hashes", "policy", "validation", "semantic", "provider", "response", "facts"):
                self.assertIn(key, rec)
            self.assertEqual(rec["response"]["content_sha256"], hashlib.sha256(rec["response"]["content"].encode()).hexdigest())
            self.assertTrue((self.state / "attempts" / f"{rec['identity']}.jsonl").is_file())
            self.assertGreaterEqual(rec["validation"]["accepted_claims"], 1)

    def test_resume_without_replay_after_quota_exhaustion(self):
        first = Scripted(quota_after=5)
        r1 = self.run_sys(first)
        self.assertEqual((r1.status, r1.exit_code), ("INTERRUPTED_QUOTA_EXHAUSTED", 1))
        self.assertEqual(r1.metrics.successes, 5)
        state = json.loads((self.state / "FULL_SYSTEM_COVERAGE.json").read_text(encoding="utf-8"))     # valid, readable manifest
        self.assertFalse(state["complete"])
        self.assertTrue(state["pending"])
        self.assertEqual(state["errors"], {})                     # a quota stop is never recorded as a controlled error
        done = {ctx for _, _, ctx in first.seen[:5]}
        second = Scripted()
        r2 = self.run_sys(second)
        self.assertEqual((r2.status, r2.exit_code), ("COMPLETE", 0))
        self.assertEqual(r2.metrics.replays, 5)
        self.assertTrue(done.isdisjoint({ctx for _, _, ctx in second.seen}))      # completed requests: 0 provider calls
        self.assertEqual(r2.state["cumulative_metrics"]["provider_successes"], r1.metrics.successes + r2.metrics.successes)

    def test_complete_replay_makes_zero_calls_and_same_semantics(self):
        self.run_sys()
        project_system(self.baseline, self.state, self.out)
        before = {p: hashlib.sha256((self.out / "ai" / p).read_bytes()).hexdigest() for p in ("projects.json", "solutions.json", "system.json")}
        again = Scripted()
        r = self.run_sys(again)
        self.assertEqual((r.metrics.requests, again.seen, r.metrics.replays), (0, [], 12))
        out2 = self.tmp / "out2"
        project_system(self.baseline, self.state, out2)
        after = {p: hashlib.sha256((out2 / "ai" / p).read_bytes()).hexdigest() for p in before}
        self.assertEqual(before, after)

    def test_request_budget_stops_cleanly(self):
        p = Scripted()
        r = self.run_sys(p, max_requests=3)
        self.assertEqual((r.status, len(p.seen)), ("INTERRUPTED_REQUEST_BUDGET_REACHED", 3))
        self.assertTrue(r.state["pending"])
        self.assertEqual(self.run_sys(Scripted()).status, "COMPLETE")

    def test_changed_evidence_replays_unchanged_and_asks_only_for_the_changed(self):
        self.run_sys()
        flows = self.baseline / "evidence" / "functional_flows.json"
        data = json.loads(flows.read_text(encoding="utf-8"))
        data[0]["handler"] = "Home_Changed"
        raw = json.dumps(data, ensure_ascii=False).encode()
        flows.write_bytes(raw)
        manifest = self.baseline / "evidence" / "EVIDENCE_MANIFEST.json"
        m = json.loads(manifest.read_text(encoding="utf-8"))
        m["partition_sha256"]["functional_flows"] = hashlib.sha256(raw).hexdigest()
        manifest.write_text(json.dumps(m), encoding="utf-8")
        p = Scripted()
        r = self.run_sys(p)
        self.assertEqual(r.status, "COMPLETE")
        asked = {e for _, e, _ in p.seen}
        self.assertIn("WebAlpha", asked)
        self.assertNotIn("blBeta", asked)
        self.assertNotIn("Orphan", asked)
        self.assertGreater(r.metrics.replays, 0)


class FailureTests(Work):
    def test_controlled_failure_is_bounded_and_isolated_then_retried_on_resume(self):
        bad = Scripted(error_for=lambda kind, entity: kind == "PROJECT" and entity == "blBeta")
        r = self.run_sys(bad, max_retries=2)
        self.assertEqual((r.status, r.exit_code), ("COMPLETE_WITH_CONTROLLED_ERRORS", 1))
        states = {p["display"]: p for p in r.state["projects"]}
        self.assertEqual(states["blBeta"]["state"], "CONTROLLED_ERROR")
        self.assertEqual(states["WebAlpha"]["state"], "HUMAN_AND_MACHINE_DOCUMENTED")
        self.assertEqual(sum(1 for k, e, _ in bad.seen if k == "PROJECT" and e == "blBeta"), 3)       # 1 + max_retries
        self.assertEqual(r.metrics.retries, 2)
        self.assertEqual(len(r.state["errors"]), 1)
        again = self.run_sys(Scripted())
        self.assertEqual(again.status, "COMPLETE")
        self.assertEqual({p["display"]: p["state"] for p in again.state["projects"]}["blBeta"], "HUMAN_AND_MACHINE_DOCUMENTED")
        self.assertEqual(again.state["errors"], {})

    def test_provider_unavailable_stops_cleanly(self):
        r = self.run_sys(Scripted(unavailable_after=2))
        self.assertEqual((r.status, r.exit_code), ("INTERRUPTED_PROVIDER_UNAVAILABLE", 1))
        self.assertTrue(r.state["pending"])

    def test_raising_provider_trips_the_circuit_breaker(self):
        r = self.run_sys(Scripted(raise_after=1), max_consecutive_failures=4, max_retries=1)
        self.assertEqual(r.status, "INTERRUPTED_PROVIDER_FAILING_REPEATEDLY")
        self.assertEqual(self.run_sys(Scripted()).status, "COMPLETE")

    def test_quota_text_in_a_provider_error_is_a_quota_stop(self):
        class Quota(Scripted):
            def generate(self, request):
                return LLMResponse(request.request_id, "x", "stub-local", "m", "PROVIDER_ERROR",
                                   error=ProviderError("PROVIDER_ERROR", "You have exceeded your premium request quota", "stub-local", "m"))
        r = self.run_sys(Quota())
        self.assertEqual(r.status, "INTERRUPTED_QUOTA_EXHAUSTED")


class TruthContractTests(unittest.TestCase):
    FACTS = [Fact("F01", "name", "confirmed", "Nombre del proyecto: X."), Fact("F02", "flow", "inferred", "Una vista abre un manejador."),
             Fact("F03", "data", "confirmed", "Procedimiento P invocado.")]

    def _validate(self, claims, section="purpose"):
        parsed = {s: [] for s in ("purpose", "responsibilities", "consumers", "dependencies", "business_flow", "data_interactions", "unresolved")}
        parsed[section] = claims
        return validate_semantic("PROJECT", parsed, self.FACTS, "seed")

    def test_no_name_only_business_inference(self):
        v = self._validate([{"text": "Gestiona subsidios de salud.", "status": "CONFIRMED", "refs": ["F01"]}])
        self.assertEqual(v.accepted_count, 0)
        self.assertEqual(v.rejected[0]["reason"], "NAME_ONLY_INFERENCE")

    def test_obsolescence_and_leaks_and_unknown_refs_are_rejected(self):
        for text, reason in (("Este componente está obsoleto.", "OBSOLESCENCE_CLAIM"), ("Es código muerto.", "OBSOLESCENCE_CLAIM"),
                             ("Llama a FLOW-0000012345 en el proyecto.", "HUMAN_LEAK"), ("Abre Home.aspx al cargar.", "HUMAN_LEAK"),
                             ("Ejecuta en la línea 42 del archivo.", "HUMAN_LEAK"), ("Lo dice el modelo copilot.", "HUMAN_LEAK")):
            v = self._validate([{"text": text, "status": "INFERRED", "refs": ["F03"]}])
            self.assertEqual([r["reason"] for r in v.rejected], [reason], text)
        v = self._validate([{"text": "Algo.", "status": "INFERRED", "refs": ["F99"]}])
        self.assertEqual(v.rejected[0]["reason"], "UNKNOWN_REF")
        v = self._validate([{"text": "Algo.", "status": "CONFIRMED", "refs": []}])
        self.assertEqual(v.rejected[0]["reason"], "NO_EVIDENCE")

    def test_inference_is_never_promoted_to_confirmed(self):
        v = self._validate([{"text": "La vista abre un manejador.", "status": "CONFIRMED", "refs": ["F02"]}])
        self.assertEqual(v.accepted["purpose"][0]["status"], "INFERRED")
        self.assertEqual(v.downgraded, 1)
        v = self._validate([{"text": "Invoca el procedimiento P.", "status": "CONFIRMED", "refs": ["F03"]}])
        self.assertEqual(v.accepted["purpose"][0]["status"], "CONFIRMED")

    def test_unresolved_stays_visible_and_schema_is_enforced(self):
        v = self._validate([{"text": "No se pudo determinar el origen.", "status": "UNRESOLVED", "refs": []}], "unresolved")
        self.assertEqual(v.accepted["unresolved"][0]["status"], "UNRESOLVED")
        self.assertFalse(validate_semantic("PROJECT", {"purpose": []}, self.FACTS, "s").schema_ok)
        self.assertEqual(set(output_schema("SYSTEM")["required"]), {"summary", "solutions", "interaction_paths", "data", "cross_project", "unresolved"})

    def test_leaking_provider_output_never_reaches_the_human_product(self):
        def mutate(kind, parsed, facts):
            ref = next((f["ref"] for f in facts if f["kind"] != "name"), facts[0]["ref"])
            parsed = {k: list(v) for k, v in parsed.items()}
            first = next(iter(parsed))
            parsed[first].append({"text": "Pasa por FLOW-0000000001 y EP-0000000002 en Home.aspx línea 9.", "status": "INFERRED", "refs": [ref]})
            return parsed
        with tempfile.TemporaryDirectory() as tmp:
            base = build_baseline(Path(tmp) / "b")
            r = run_system_interpretation(base, Path(tmp) / "s", Scripted(mutate=mutate), POLICY)
            self.assertEqual(r.status, "COMPLETE")
            doc = project_system(base, Path(tmp) / "s", Path(tmp) / "o")
            self.assertEqual(doc["validation"]["human_provenance_leaks"], 0)
            for page in (Path(tmp) / "o" / "human").rglob("*.html"):
                self.assertNotRegex(re.sub(r"<[^>]+>", " ", page.read_text(encoding="utf-8")), LEAK)


class ProjectionTests(Work):
    def setUp(self):
        super().setUp()
        self.run_sys()
        self.doc = project_system(self.baseline, self.state, self.out)

    def test_product_layout_and_validation_metrics_are_clean(self):
        v = self.doc["validation"]
        self.assertEqual(v["defects"], 0, v["details"])
        for key in ("broken_links", "missing_assets", "invalid_json", "dangling_ids", "human_provenance_leaks", "invalid_human_states", "silent_project_omissions"):
            self.assertEqual(v[key], 0, key)
        for rel in ("human/index.html", "human/IST_Complete.pdf", "human/executive/index.html", "human/system/index.html", "human/solutions/index.html",
                    "human/projects/index.html", "human/views/index.html", "human/flows/index.html", "human/data/index.html", "human/diagrams/system-map.svg",
                    "ai/knowledge.json", "ai/system.json", "ai/solutions.json", "ai/projects.json", "ai/views.json", "ai/flows.json", "ai/data.json",
                    "ai/unresolved.json", "ai/provenance.json", "ai/coverage.json", "internal/requests_index.json", "ACCEPTANCE_MANIFEST.json"):
            self.assertTrue((self.out / rel).is_file(), rel)
        self.assertEqual((self.out / "human" / "IST_Complete.pdf").read_bytes()[:5], b"%PDF-")
        self.assertTrue(self.doc["complete"])

    def test_every_project_has_a_human_page_including_unresolved_and_machine_only(self):
        for p in load_inventory(self.baseline).projects.values():
            self.assertTrue((self.out / "human" / "projects" / f"{p.slug}.html").is_file(), p.display)
        text = (self.out / "human" / "projects" / "orphan.html").read_text(encoding="utf-8")
        self.assertIn("Sin solución resoluble", text)

    def test_human_state_vocabulary(self):
        html = (self.out / "human" / "projects" / "webalpha.html").read_text(encoding="utf-8")
        visible = re.sub(r"<[^>]+>", " ", html)
        self.assertTrue(any(w in visible for w in HUMAN_STATUS_VALUES))
        for token in ("CONFIRMED", "INFERRED", "UNRESOLVED", "AI_INTERPRETATION", "CANONICAL"):
            self.assertNotIn(token, visible)
        for rec in RequestStore(self.state).iter_accepted():
            for claims in rec["semantic"].values():
                self.assertTrue(all(c["status"] in CLAIM_STATUSES for c in claims))

    def test_machine_cross_references_have_no_dangling_ids(self):
        self.assertEqual(machine.check_machine(self.out / "ai")["dangling_ids"], 0)
        path = self.out / "ai" / "solutions.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data[0]["project_ids"].append("PRJ-missing")
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(machine.check_machine(self.out / "ai")["dangling_ids"], 1)

    def test_machine_knowledge_is_traceable(self):
        prov = json.loads((self.out / "ai" / "provenance.json").read_text(encoding="utf-8"))
        facts = {f["fact_id"]: f for rec in prov for f in rec["facts"]}
        projects = json.loads((self.out / "ai" / "projects.json").read_text(encoding="utf-8"))
        web = next(p for p in projects if p["display"] == "WebAlpha")
        claim = next(c for cs in web["semantic"].values() for c in cs if c["fact_ids"])
        self.assertIn(claim["fact_ids"][0], facts)
        self.assertTrue(any(f["evidence_ids"] for f in facts.values()))       # evidence ids live in ai/, never in human/
        self.assertTrue(json.loads((self.out / "ai" / "knowledge.json").read_text(encoding="utf-8"))["synthetic_provider"])

    def test_synthetic_provider_is_declared_in_the_human_product(self):
        self.assertIn("Interpretación sintética de prueba", (self.out / "human" / "index.html").read_text(encoding="utf-8"))
        self.assertTrue(self.doc["synthetic_provider"])
        self.assertEqual(self.doc["providers"], ["stub-local/deterministic-stub"])

    def test_projection_is_deterministic_and_never_resolves_a_provider(self):
        out2 = self.tmp / "out2"
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create", side_effect=AssertionError("provider resolved")), \
                mock.patch("legacy_documenter.llm.providers.copilot.CopilotProvider.__init__", side_effect=AssertionError("real provider")):
            doc2 = project_system(self.baseline, self.state, out2)
            doc3 = project_system(self.baseline, self.state, self.out)          # re-project over its own previous output
        key = lambda d: {f["path"]: f["sha256"] for f in d["files"]}
        self.assertEqual(key(self.doc), key(doc2))
        self.assertEqual(key(self.doc), key(doc3))

    def test_projection_refuses_to_overwrite_foreign_directories(self):
        foreign = self.tmp / "foreign"
        (foreign / "human").mkdir(parents=True)
        (foreign / "human" / "mine.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(ProjectionError) as ctx:
            project_system(self.baseline, self.state, foreign)
        self.assertEqual(ctx.exception.reason, "PRODUCT_OUTPUT_NOT_OWNED")
        self.assertTrue((foreign / "human" / "mine.txt").is_file())

    def test_interrupted_run_projects_a_partial_but_complete_listing(self):
        state = self.tmp / "partial state"
        r = self.run_sys(Scripted(), state=state, max_requests=4)
        self.assertEqual(r.status, "INTERRUPTED_REQUEST_BUDGET_REACHED")
        out = self.tmp / "partial out"
        doc = project_system(self.baseline, state, out)
        self.assertFalse(doc["complete"])
        self.assertEqual(doc["validation"]["silent_project_omissions"], 0)
        cov = json.loads((out / "ai" / "coverage.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cov["projects"]), len(PROJECTS))
        self.assertTrue(any(p["state"] == "PENDING_INTERPRETATION" for p in cov["projects"]))
        self.assertIn("Documentación parcial", (out / "human" / "index.html").read_text(encoding="utf-8"))


class NoSourceAccessTests(Work):
    def test_zero_source_reads_during_interpret_resume_and_projection(self):
        global _RECORDING
        sentinel = self.tmp / "source corpus"
        sentinel.mkdir()
        (sentinel / "Secret.vb").write_text("Module M\nEnd Module\n", encoding="utf-8")
        boom = AssertionError("source access")
        with mock.patch("legacy_documenter.scanner.repository_scanner.RepositoryScanner.scan", side_effect=boom), \
                mock.patch("legacy_documenter.cli.pipeline_stages.extract_repository", side_effect=boom), \
                mock.patch("legacy_documenter.cli.pipeline_stages.scan_repository", side_effect=boom):
            _RECORDING = []
            try:
                self.run_sys(Scripted(quota_after=3))
                self.run_sys(Scripted())
                project_system(self.baseline, self.state, self.out)
                opened = list(_RECORDING)
            finally:
                _RECORDING = None
        code_suffix = (".py", ".pyc", ".pyd", ".dll", ".so")
        data_opens = [p for p in opened if not p.lower().endswith(code_suffix) and "__pycache__" not in p]
        self.assertFalse([p for p in data_opens if str(sentinel) in p or p.lower().endswith((".vb", ".vbproj", ".aspx", ".ascx", ".sln"))])
        allowed = (str(self.tmp), os.path.join(sys.prefix), os.path.join(sys.base_prefix))
        self.assertFalse([p for p in data_opens if os.path.isabs(p) and not p.startswith(allowed) and "legacy_documenter" not in p and "Temp" not in p][:5])


class CliTests(Work):
    def test_exit_codes_and_consent(self):
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state)
        self.assertEqual((code, payload["status"]), (2, "USAGE"))
        self.assertFalse(self.state.exists())
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB", "--resume")
        self.assertEqual(code, 2)
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB", "--max-requests", "3")
        self.assertEqual((code, payload["status"]), (1, "INTERRUPTED_REQUEST_BUDGET_REACHED"))
        self.assertGreater(payload["pending_total"], 0)
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB", "--resume")
        self.assertEqual((code, payload["status"]), (0, "COMPLETE"))
        self.assertEqual(payload["this_run"]["provider_replays"], 3)
        code, payload, _ = self.cli("project-system", self.baseline, "--state-dir", self.state, "--output", self.out)
        self.assertEqual((code, payload["status"], payload["provider_calls"], payload["source_scanned"]), (0, "SUCCESS", 0, False))
        self.assertEqual(payload["validation"]["defects"], 0)

    def test_invalid_baseline_and_account_mismatch_are_refused_before_any_request(self):
        code, payload, _ = self.cli("interpret-system", self.tmp / "nowhere", "--state-dir", self.state, "--provider", "STUB")
        self.assertEqual((code, payload["status"], payload["provider_called"]), (4, "SYSTEM_BASELINE_INVALID", False))
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB", "--expect-account", "someone-else")
        self.assertEqual((code, payload["status"]), (4, "ACCOUNT_MISMATCH"))
        self.assertFalse(self.state.exists())
        code, payload, _ = self.cli("project-system", self.baseline, "--state-dir", self.tmp / "no state", "--output", self.out)
        self.assertEqual((code, payload["status"]), (4, "NO_INTERPRETATION_STATE"))

    def test_knowledge_output_projects_after_interpretation(self):
        code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB", "--knowledge-output", self.out)
        self.assertEqual(code, 0)
        self.assertEqual(payload["product"]["validation"]["defects"], 0)
        self.assertTrue((self.out / "human" / "index.html").is_file())

    def test_account_preflight_is_offline_for_stub_and_reports_identity(self):
        info = check_account("STUB", expect="x")
        self.assertTrue(info["checked"])
        self.assertFalse(info["matches_expected"])
        self.assertNotIn("token", json.dumps(info).lower())

    def test_real_provider_is_never_constructed_by_these_tests(self):
        with mock.patch("legacy_documenter.llm.providers.copilot.CopilotProvider.__init__", side_effect=AssertionError("real provider")):
            code, payload, _ = self.cli("interpret-system", self.baseline, "--state-dir", self.state, "--provider", "STUB")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
