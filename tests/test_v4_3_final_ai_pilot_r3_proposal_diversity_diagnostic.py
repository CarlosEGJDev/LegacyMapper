"""V4.3 final AI pilot R3 -- proposal diversity root-cause diagnostic: verification tests.

Covers the nine minimum tests the diagnostic prompt requires
(`prompts/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_PROMPT.md`,
section "Tests minimos"):

1. the diagnostic replicates `select_flow_ids` exactly (same candidate ids);
2. the diagnostic replicates `AiProjectionBuilder.package` exactly (same
   included records/statistics);
3. an oversized rich candidate is reported `excluded_by_budget=True`;
4. a small rich candidate that IS included correctly reflects SP/write/
   transaction evidence;
5. proposal -> flow mapping via `evidence_refs` is correct;
6. the diagnostic's output is deterministic/stable across repeated runs;
7. the diagnostic never calls a provider;
8. the diagnostic never leaks a secret/credential;
9. (covered by the full regression run, not by a single test here --
   `python -m unittest discover -s tests`).

`tools.v4_3_ai_selection_diagnostic` is diagnostic/tooling only: this module
never invokes `legacy_documenter.llm.providers.copilot`, never touches
`PROJECT_STATE.json`, and every fixture here is synthetic (no real repository
or real pilot output is read).
"""
from __future__ import annotations

import inspect
import json
import os
import unittest

from legacy_documenter.context import ai_projection as aip
from legacy_documenter.context.composer import PROFILES
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.orchestration import ai_interpretation as ai
from tools import v4_3_ai_selection_diagnostic as diag


def _flow(
    flow_id: str, entry_id: str, *, confidence: str = "confirmed",
    terminal_type: str = "unresolved_boundary", terminal_target: str | None = "TARGET",
    nodes: list[str] | None = None, evidence_refs: list[str] | None = None,
    node_padding: int = 0, projects: list[str] | None = None,
) -> tuple[dict, dict, dict]:
    """Builds one (flow, entry_point, path) synthetic triple of the exact `ix` shape."""
    padding = [f"PADDING-{flow_id}-{n:05d}" for n in range(node_padding)]
    flow = {
        "id": flow_id, "entry_point_id": entry_id, "confidence": confidence,
        "project_sequence": projects or ["P"],
    }
    entry = {
        "id": entry_id, "webform": f"web\\{flow_id}.ascx", "event": "Click",
        "handler": f"{flow_id}_Click", "start_method": f"Start_{flow_id}",
    }
    path = {
        "path_id": f"PATH-{flow_id}", "flow_id": flow_id,
        "nodes": (nodes or []) + padding, "terminal_type": terminal_type,
        "terminal_target": terminal_target, "confidence": confidence,
        "evidence_refs": evidence_refs or [],
    }
    return flow, entry, path


def _build_ix(triples: list[tuple[dict, dict, dict]], data_access=None, stored_procedures=None) -> dict:
    flows = [t[0] for t in triples]
    entry_points = [t[1] for t in triples]
    paths = [t[2] for t in triples]
    return {
        "functional_flows": flows, "entry_points": entry_points, "functional_paths": paths,
        "data_access": data_access or [], "stored_procedures": stored_procedures or [],
        "sql_operations": [], "data_parameters": [],
    }


def _mixed_richness_ix() -> dict:
    """One small rich flow, one oversized rich flow, and many trivial flows.

    Mirrors, at synthetic scale, the exact shape the real R3 diagnostic run
    found against the real repository: rich candidates exist and are
    selected, but only the ones small enough to fit the SMALL profile's
    16,000-character package budget actually survive into the final request.
    """
    triples = []

    # DAO with a confirmed write + a confirmed transaction, referenced by both
    # the rich-small and rich-oversized flows below.
    data_access = [
        {
            "id": "DAO-WRITE", "class": "Repo", "method": "Save", "operation_kind": "data_access",
            "confidence": "confirmed", "sql_operation": "INSERT",
        },
        {
            "id": "DAO-TX", "class": "Repo", "method": "Commit", "operation_kind": "transaction",
            "confidence": "confirmed", "evidence": [{"expression": "dbc.BeginTrans()"}],
        },
    ]
    stored_procedures = [{"id": "SP-1", "name": "PKG.SAVE", "package": "PKG", "procedure": "SAVE"}]

    # Rich, small: has a resolved SP terminal + confirmed write/transaction nodes, fits any budget.
    triples.append(_flow(
        "FLOW-RICH-SMALL", "EP-RICH-SMALL", terminal_type="stored_procedure", terminal_target="SP-1",
        nodes=["DAO-WRITE", "DAO-TX"], evidence_refs=["EVID-RICH-SMALL"],
    ))

    # Rich, oversized: same evidence shape, but padded with thousands of extra node ids so its
    # serialized size alone exceeds the whole SMALL package budget (16,000 characters).
    triples.append(_flow(
        "FLOW-RICH-BIG", "EP-RICH-BIG", terminal_type="stored_procedure", terminal_target="SP-1",
        nodes=["DAO-WRITE", "DAO-TX"], evidence_refs=["EVID-RICH-BIG"], node_padding=3000,
    ))

    # Many trivial flows: no data operations, unresolved terminal -- small enough that dozens fit.
    for index in range(30):
        triples.append(_flow(f"FLOW-TRIVIAL-{index:03d}", f"EP-TRIVIAL-{index:03d}"))

    return _build_ix(triples, data_access=data_access, stored_procedures=stored_procedures)


class ReplicatesSelectFlowIdsTests(unittest.TestCase):
    """Test 1: the diagnostic must replicate `select_flow_ids` exactly, never approximate it."""

    def test_candidate_flow_ids_match_direct_select_flow_ids_call(self) -> None:
        ix = _mixed_richness_ix()
        max_records = PROFILES["SMALL"][0]
        expected = aip.select_flow_ids(ix, max_records)

        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        first_attempt = result["attempts"][0]

        self.assertEqual(first_attempt["attempt_profile"], "SMALL")
        self.assertEqual(first_attempt["candidate_flow_ids"], expected)


class ReplicatesPackageTests(unittest.TestCase):
    """Test 2: the diagnostic must replicate `AiProjectionBuilder.package` exactly."""

    def test_final_package_matches_a_direct_builder_call(self) -> None:
        ix = _mixed_richness_ix()
        hydrator = EvidenceHydrator()
        builder = aip.AiProjectionBuilder(hydrator=hydrator)
        max_records = PROFILES["SMALL"][0]
        candidate_ids = aip.select_flow_ids(ix, max_records)
        records = [hydrator.hydrate_flow(fid, ix) for fid in sorted(set(candidate_ids))]
        expected_package = builder.package(records, source_snapshot="SNAP", profile="SMALL")

        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")

        self.assertEqual(result["package"]["package_id"], expected_package["package_id"])
        self.assertEqual(result["package"]["statistics"], expected_package["statistics"])
        self.assertEqual(
            [r["flow_id"] for r in result["package"]["records"]],
            [r["flow_id"] for r in expected_package["records"]],
        )


class OversizedCandidateExcludedByBudgetTests(unittest.TestCase):
    """Test 3: an oversized rich candidate must be reported `excluded_by_budget=True`."""

    def test_oversized_rich_flow_is_excluded_by_budget(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        by_id = {f["flow_id"]: f for f in result["flows"]}

        big = by_id["FLOW-RICH-BIG"]
        self.assertGreater(big["serialized_record_chars"], PROFILES["SMALL"][1])
        self.assertTrue(big["excluded_by_budget"])
        self.assertFalse(big["final_request_included"])
        # It IS a rich candidate (richness bucket 0/1) that WAS offered to the packer --
        # this proves the exclusion is a budget/packing effect, not a selection gap.
        self.assertIn(big["richness_bucket"], (0, 1))
        self.assertTrue(big["selected_for_package"])


class RichIncludedCandidateReflectsEvidenceTests(unittest.TestCase):
    """Test 4: a small rich candidate that IS included must correctly reflect SP/write/transaction."""

    def test_small_rich_flow_is_included_and_correctly_flagged(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        by_id = {f["flow_id"]: f for f in result["flows"]}

        small = by_id["FLOW-RICH-SMALL"]
        self.assertTrue(small["final_request_included"])
        self.assertFalse(small["excluded_by_budget"])
        self.assertEqual(small["richness_bucket"], 0)
        self.assertTrue(small["has_stored_procedures"])
        self.assertEqual(small["stored_procedure_count"], 1)
        self.assertTrue(small["has_confirmed_write"])
        self.assertTrue(small["has_transactions"])
        self.assertEqual(small["transaction_count"], 1)


class ProposalToFlowMappingTests(unittest.TestCase):
    """Test 5: proposal -> flow mapping via `evidence_refs` must be correct."""

    def test_proposal_maps_to_the_flow_whose_evidence_it_cites(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        package = result["package"]
        included_ids = {r["flow_id"] for r in package["records"]}
        self.assertIn("FLOW-RICH-SMALL", included_ids)

        proposals = [
            {"proposal_id": "PROP-1", "evidence_refs": ["EVID-RICH-SMALL"]},
            {"proposal_id": "PROP-2", "evidence_refs": ["FLOW-RICH-SMALL"]},
            {"proposal_id": "PROP-3", "evidence_refs": ["NO-SUCH-REF"]},
        ]
        mapped = diag.map_proposals_to_flows(proposals, package)
        by_id = {m["proposal_id"]: m for m in mapped}

        self.assertEqual(by_id["PROP-1"]["flow_ids"], ["FLOW-RICH-SMALL"])
        self.assertEqual(by_id["PROP-2"]["flow_ids"], ["FLOW-RICH-SMALL"])
        self.assertEqual(by_id["PROP-3"]["flow_ids"], [])


class DeterministicOutputTests(unittest.TestCase):
    """Test 6: the diagnostic's output must be stable/deterministic across runs."""

    def test_repeated_runs_produce_identical_output(self) -> None:
        ix = _mixed_richness_ix()
        first = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        second = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")

        self.assertEqual(
            json.dumps(first, sort_keys=True, default=str),
            json.dumps(second, sort_keys=True, default=str),
        )


class NoProviderCallTests(unittest.TestCase):
    """Test 7: the diagnostic must never call a real (or fake) provider."""

    def test_module_source_never_references_a_provider_class_or_send_call(self) -> None:
        source = inspect.getsource(diag)
        for forbidden in ("CopilotProvider", "structured_generate", "ProviderRegistry", "_resolve_provider"):
            self.assertNotIn(forbidden, source)

    def test_run_diagnostic_accepts_no_provider_argument(self) -> None:
        signature = inspect.signature(diag.run_diagnostic)
        self.assertNotIn("provider", signature.parameters)


class NoSecretLeakageTests(unittest.TestCase):
    """Test 8: the diagnostic must never leak a credential/secret in its output."""

    def test_output_never_contains_environment_or_credential_looking_values(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(ix, source_snapshot="SNAP", profile="SMALL")
        serialized = json.dumps(result, default=str).lower()
        for forbidden in ("api_key", "apikey", "secret", "password", "credential", "token=", "bearer "):
            self.assertNotIn(forbidden, serialized)

    def test_module_never_reads_provider_environment_variables(self) -> None:
        source = inspect.getsource(diag)
        self.assertNotIn("LEGACYMAPPER_LLM_PROVIDER", source)
        self.assertNotIn("os.environ", source)


class HistoricalFlowLookupTests(unittest.TestCase):
    """The historical flow id must never be hardcoded/failed on if absent -- report equivalents instead."""

    def test_absent_historical_flow_reports_equivalents_instead_of_failing(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(
            ix, source_snapshot="SNAP", profile="SMALL", historical_flow_id="FLOW-DOES-NOT-EXIST",
        )
        historical = result["historical_flow"]
        self.assertFalse(historical["exists"])
        self.assertIsInstance(historical["equivalent_rich_flows"], list)

    def test_present_historical_flow_is_reported_with_full_diagnostic(self) -> None:
        ix = _mixed_richness_ix()
        result = diag.run_diagnostic(
            ix, source_snapshot="SNAP", profile="SMALL", historical_flow_id="FLOW-RICH-BIG",
        )
        historical = result["historical_flow"]
        self.assertTrue(historical["exists"])
        self.assertEqual(historical["diagnostic"]["flow_id"], "FLOW-RICH-BIG")


if __name__ == "__main__":
    unittest.main()
