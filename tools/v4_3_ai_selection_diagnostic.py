"""Read-only diagnostic tool for V4.3 R3 proposal-diversity root cause (V4.3-R3-diagnostic).

Traces the real, unmodified production chain end-to-end:

    select_flow_ids -> hydration -> AiProjectionBuilder.package -> _build_request
    -> measure_request_payload -> (no provider call here) -> [findings/proposals,
    when available, mapped externally]

Reuses PRODUCTION functions verbatim -- it never re-implements or approximates
`select_flow_ids`, `_bucketed_order`, `AiProjectionBuilder.package`, budget
limits, SMALL/TINY thresholds, the real Copilot-backed provider adapter, or
any prompt/schema constant. It only READS already-computed evidence off the
objects those functions return, to answer "did rich evidence survive
selection/packing".

This module is diagnostic/tooling only:

* it never calls a real provider (no structured-generation call, no
  network access anywhere in this file);
* it never writes to `PROJECT_STATE.json`;
* it never mutates `confidence`, `terminal_type`, or any hydrated field;
* the only file it may optionally write is a diagnostic artifact
  (`ai_context/AI_SELECTION_DIAGNOSTIC.json`, opt-in via `--emit-artifact`),
  which is NOT a stable public contract.

See `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md`
for how this tool was used and what it found.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reused, unmodified production functions/constants -- never reimplemented here.
from legacy_documenter.context.ai_projection import (
    AiProjectionBuilder,
    PROFILE_REDUCTION,
    _WRITE_OPERATIONS,  # noqa: F401 (re-exported for callers/tests that want the exact set)
    _canonical,
    _record_richness_bucket,
    package_reference_ids,
    record_reference_ids,
    select_flow_ids,
)
from legacy_documenter.context.composer import PROFILES
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.llm.core import measure_request_payload
from legacy_documenter.orchestration._run_evidence_io import load_indexes, load_source_snapshot
from legacy_documenter.orchestration.ai_interpretation import (
    DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS,
    DEFAULT_PROFILE,
    FINDING_SCHEMA,
    _build_request,
)

#: Bucket ids `_record_richness_bucket`/`_flow_richness_bucket` classify a flow as
#: "rich" (has a resolved terminal, a confirmed write/transaction, or a confirmed
#: data operation) -- buckets 0 and 1. Bucket 2 is "some other diversity signal"
#: and bucket 3 is the trivial/dead-end case the V4.3 final AI pilot over-selected.
RICH_BUCKETS = (0, 1)


def _mixed_confirmed_unresolved(paths: list[dict]) -> bool:
    """Same predicate `ai_projection._record_richness_bucket` already computes internally.

    Read-only re-derivation over already-hydrated fields (never a new selection
    rule): a record is "mixed" when at least one of its paths is `unresolved`
    and at least one other path is not.
    """
    confidences = {p.get("confidence") for p in paths}
    return "unresolved" in confidences and bool(confidences - {"unresolved"})


def diagnose_flow(record: dict, *, selected_for_package: bool, final_request_included: bool) -> dict:
    """Builds the minimum per-flow diagnostic dict required by the R3 diagnostic prompt.

    `record` is an already-hydrated FLOW record (`EvidenceHydrator.hydrate_flow`
    output, unmodified). This function performs no selection/budget logic of its
    own -- `selected_for_package`/`final_request_included` are supplied by the
    caller, which got them from the real `AiProjectionBuilder.package` output.
    """
    terminals = record.get("terminals") or {}
    data_operations = record.get("data_operations") or []
    transactions = record.get("transactions") or []
    paths = record.get("paths") or []
    stored_procedures = terminals.get("stored_procedures") or []

    has_confirmed_write = any(
        op.get("operation") in _WRITE_OPERATIONS and op.get("confidence") == "confirmed" for op in data_operations
    )
    evidence_ref_count = sum(len(p.get("evidence_refs") or []) for p in paths)
    serialized_record_chars = len(_canonical(record))

    return {
        "flow_id": record.get("flow_id"),
        "entry_point_id": (record.get("entry_point") or {}).get("id"),
        "richness_bucket": _record_richness_bucket(record),
        "flow_confidence": record.get("confidence"),
        "hydrated": True,
        "selected_for_package": bool(selected_for_package),
        # A candidate that was offered to `AiProjectionBuilder.package` (selected_for_package=True)
        # but did not survive into `package["records"]` was cut by the character/record budget.
        # A candidate that was never offered at all (selected_for_package=False, only used for the
        # historical-flow report when the flow was not among the selected candidates) is reported as
        # excluded too, since it never had a chance to reach the request either way.
        "excluded_by_budget": not bool(final_request_included),
        "final_request_included": bool(final_request_included),
        "serialized_record_chars": serialized_record_chars,
        "path_count": len(paths),
        "evidence_ref_count": evidence_ref_count,
        "has_data_operations": bool(data_operations),
        "data_operation_count": len(data_operations),
        "has_stored_procedures": bool(stored_procedures),
        "stored_procedure_count": len(stored_procedures),
        "has_transactions": bool(transactions),
        "transaction_count": len(transactions),
        "has_confirmed_write": has_confirmed_write,
        "participating_component_count": len(set(record.get("projects") or [])),
        "mixed_confirmed_unresolved": _mixed_confirmed_unresolved(paths),
    }


def run_diagnostic(
    ix: dict, source_snapshot: str | None = None, profile: str = DEFAULT_PROFILE,
    limit: int = DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS, flow_ids: list[str] | None = None,
    historical_flow_id: str = "FLOW-0343552547",
) -> dict:
    """Runs the real selection -> hydration -> package -> request chain, read-only.

    Mirrors exactly what `orchestration.ai_interpretation._build_within_budget`
    does in production (reduce-once-then-fail-closed across
    `PROFILE_REDUCTION`), but stops before any provider call and additionally
    reports, per candidate flow, the diagnostic fields the R3 prompt requires.

    Never calls a provider. Never writes to disk on its own (the caller may
    choose to persist the returned dict).
    """
    hydrator = EvidenceHydrator()
    builder = AiProjectionBuilder(hydrator=hydrator)

    attempts = [profile] + ([PROFILE_REDUCTION[profile]] if profile in PROFILE_REDUCTION else [])
    attempt_reports: list[dict] = []
    final_package = final_request = final_metrics = None
    final_attempt_profile = None
    rejection_reasons: list[str] = []

    for attempt_profile in attempts:
        max_records = PROFILES[attempt_profile][0]
        candidate_ids = flow_ids if flow_ids is not None else select_flow_ids(ix, max_records)
        records = [hydrator.hydrate_flow(fid, ix) for fid in sorted(set(candidate_ids))]
        package = builder.package(records, source_snapshot=source_snapshot, profile=attempt_profile)
        request = _build_request(package)
        metrics = measure_request_payload(request, FINDING_SCHEMA)

        included_ids = {r.get("flow_id") for r in package.get("records", [])}
        flows = [
            diagnose_flow(record, selected_for_package=True, final_request_included=record.get("flow_id") in included_ids)
            for record in records
        ]

        fits = package["statistics"]["completeness"] != "BUDGET_INSUFFICIENT" and metrics["payload_estimated_tokens"] <= limit
        attempt_reports.append({
            "attempt_profile": attempt_profile,
            "candidate_flow_ids": candidate_ids,
            "package_statistics": package["statistics"],
            "request_metrics": metrics,
            "fits_within_limit": fits,
            "limit": limit,
            "flows": flows,
        })
        if not fits:
            if package["statistics"]["completeness"] == "BUDGET_INSUFFICIENT":
                rejection_reasons.append(f"budget_insufficient:profile={attempt_profile}")
            else:
                rejection_reasons.append(
                    f"payload_estimated_tokens={metrics['payload_estimated_tokens']}>limit={limit}:profile={attempt_profile}"
                )
            continue
        final_package, final_request, final_metrics = package, request, metrics
        final_attempt_profile = attempt_profile
        break

    used_report = attempt_reports[-1] if final_package is None else next(
        r for r in attempt_reports if r["attempt_profile"] == final_attempt_profile
    )
    flows = used_report["flows"]
    rich_included = [f for f in flows if f["richness_bucket"] in RICH_BUCKETS and f["final_request_included"]]
    rich_excluded = [f for f in flows if f["richness_bucket"] in RICH_BUCKETS and not f["final_request_included"]]

    historical = _historical_flow_report(ix, hydrator, historical_flow_id, flows)

    return {
        "requested_profile": profile,
        "attempts": attempt_reports,
        "final_attempt_profile": final_attempt_profile,
        "rejection_reasons": rejection_reasons,
        "final_fits": final_package is not None,
        "package": final_package,
        "request": None if final_request is None else {
            "purpose": final_request.purpose,
            "context_package_id": final_request.context_package_id,
            "context_schema_version": final_request.context_schema_version,
        },
        "request_metrics": final_metrics,
        "flows": flows,
        "rich_flows_in_final_request": rich_included,
        "rich_flows_excluded": rich_excluded,
        "historical_flow": historical,
        "known_reference_ids": sorted(package_reference_ids(final_package)) if final_package else [],
    }


def _historical_flow_report(ix: dict, hydrator: EvidenceHydrator, flow_id: str, diagnosed_flows: list[dict]) -> dict:
    """Reports on `flow_id` (the R3 historical flow) if present in `ix`.

    Never hardcodes/fails if absent: reports `exists=False` and lists rich
    equivalent candidates instead (found by property, not by id), per the
    diagnostic prompt's explicit instruction.
    """
    flow_index = {f.get("id"): f for f in ix.get("functional_flows", []) if f.get("id")}
    exists = flow_id in flow_index
    if not exists:
        equivalents = [f for f in diagnosed_flows if f["richness_bucket"] in RICH_BUCKETS][:5]
        return {"flow_id": flow_id, "exists": False, "equivalent_rich_flows": equivalents}

    record = hydrator.hydrate_flow(flow_id, ix)
    matching = next((f for f in diagnosed_flows if f["flow_id"] == flow_id), None)
    return {
        "flow_id": flow_id,
        "exists": True,
        "in_selected_candidates": matching is not None,
        "diagnostic": matching or diagnose_flow(record, selected_for_package=False, final_request_included=False),
    }


def map_proposals_to_flows(proposals: list[dict], package: dict) -> list[dict]:
    """Maps proposals (each `{"proposal_id": ..., "evidence_refs": [...]}`) to owning flow ids.

    A proposal's `evidence_refs` are validated (`ai_interpretation._validate_findings`)
    to be a subset of `package_reference_ids(package)`, i.e. ids from
    `record_reference_ids` of one of the records the package actually included.
    This function reuses that exact reference set per record (never re-derives
    it) to determine which flow(s) a proposal's evidence traces back to.
    """
    refs_by_flow = {
        record.get("flow_id"): record_reference_ids(record) for record in package.get("records", [])
    }
    mapped = []
    for proposal in proposals:
        proposal_id = proposal.get("proposal_id")
        evidence_refs = set(proposal.get("evidence_refs") or [])
        flow_ids = sorted(
            flow_id for flow_id, refs in refs_by_flow.items() if evidence_refs & refs
        )
        mapped.append({"proposal_id": proposal_id, "flow_ids": flow_ids})
    return mapped


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", help="A run's --output directory (must contain index/*.json).")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, choices=list(PROFILES.keys() - {"FULL"}))
    parser.add_argument("--limit", type=int, default=DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS)
    parser.add_argument("--flow-ids", nargs="*", default=None)
    parser.add_argument("--historical-flow-id", default="FLOW-0343552547")
    parser.add_argument("--emit-artifact", action="store_true", help="Write ai_context/AI_SELECTION_DIAGNOSTIC.json under output_dir.")
    args = parser.parse_args(argv)

    ix = load_indexes(args.output_dir)
    try:
        source_snapshot = load_source_snapshot(args.output_dir)
    except FileNotFoundError:
        source_snapshot = None

    result = run_diagnostic(
        ix, source_snapshot=source_snapshot, profile=args.profile, limit=args.limit,
        flow_ids=args.flow_ids, historical_flow_id=args.historical_flow_id,
    )

    summary = {
        "final_attempt_profile": result["final_attempt_profile"],
        "final_fits": result["final_fits"],
        "candidate_count": len(result["flows"]),
        "final_request_included_count": sum(1 for f in result["flows"] if f["final_request_included"]),
        "rich_in_final_request_count": len(result["rich_flows_in_final_request"]),
        "rich_excluded_count": len(result["rich_flows_excluded"]),
        "historical_flow_exists": result["historical_flow"]["exists"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.emit_artifact:
        artifact_path = Path(args.output_dir) / "ai_context" / "AI_SELECTION_DIAGNOSTIC.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"artifact written: {artifact_path}")

    return 0


if __name__ == "__main__":
    sys.exit(_cli())
