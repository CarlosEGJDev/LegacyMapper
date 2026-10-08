"""`review` command: explicit human decisions over persisted AI proposals (V5.7).

Thin adapter over `legacy_documenter.review`. Never invoked by `full`/`analyze`; the reviewer is
always an explicit argument (no environment/OS/Git fallback) and no provider is ever resolved here.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from legacy_documenter.review.models import ReviewError, ReviewErrorCode
from legacy_documenter.review.render import pending_proposals, write_view
from legacy_documenter.review.service import ApprovalService
from legacy_documenter.review.store import ReviewStore


def add_review_parser(subparsers) -> None:
    """Registers `review {list,decide,canonical}`."""
    review = subparsers.add_parser("review", help="Apply an explicit human decision to an AI proposal, or inspect review state (no AI, no provider).")
    sub = review.add_subparsers(dest="review_command", required=True)
    list_p = sub.add_parser("list", help="Pending proposals, decisions and canonical records of a run.")
    list_p.add_argument("--output", required=True, help="The --output directory of a completed run.")
    prepare = sub.add_parser("prepare", help="Pin the review baseline (proposal + evidence fingerprints); required before the first decision.")
    prepare.add_argument("--output", required=True)
    prepare.add_argument("--proposal", action="append", default=None, help="proposal_id (repeatable); default: every pending proposal.")
    prepare.add_argument("--reviewer", required=True, help="Explicit human reviewer identity.")
    decide = sub.add_parser("decide", help="Record one human decision for one proposal.")
    decide.add_argument("--output", required=True)
    decide.add_argument("--proposal", required=True, help="proposal_id (PRP-...)")
    decide.add_argument("--action", required=True, choices=["APPROVE", "REJECT", "CORRECT", "DEFER"])
    decide.add_argument("--reviewer", required=True, help="Explicit human reviewer identity (no default, never AUTO).")
    decide.add_argument("--rationale", default=None)
    decide.add_argument("--correction-file", default=None, help="JSON {statement, evidence_refs?}; required for CORRECT.")
    decide.add_argument("--expected-evidence-fingerprint", default=None, help="Fingerprint shown by `review list`; mismatch -> PROPOSAL_STALE.")
    canonical = sub.add_parser("canonical", help="Query canonical records.")
    canonical.add_argument("--output", required=True)
    canonical.add_argument("--chain", action="store_true", help="With --id: resolve canonical -> decision -> proposal snapshot -> evidence baseline.")
    group = canonical.add_mutually_exclusive_group()
    group.add_argument("--id")
    group.add_argument("--proposal")
    group.add_argument("--evidence-ref")


def run_review(args: Namespace) -> tuple[int, str]:
    """Returns (exit_code, JSON message). 0 on success; 4 with the stable error code on rejection."""
    try:
        return 0, json.dumps(_dispatch(args), ensure_ascii=False, sort_keys=True, indent=2)
    except ReviewError as exc:
        return 4, json.dumps({"status": "REJECTED", "error_code": exc.code.value, "detail": exc.detail}, sort_keys=True, indent=2)
    except (OSError, ValueError) as exc:
        return 4, json.dumps({"status": "REJECTED", "error_code": "INVALID_DECISION", "detail": exc.__class__.__name__}, sort_keys=True, indent=2)


def _dispatch(args: Namespace) -> dict:
    run_dir = Path(args.output)
    store = ReviewStore(run_dir)
    if args.review_command == "list":
        return {"pending": pending_proposals(run_dir), "decisions": [d.to_dict() for d in store.decisions()],
                "canonical": [r.to_dict() for r in store.canonical_records()], "metrics": store.metrics()}
    if args.review_command == "prepare":
        service = ApprovalService(run_dir)
        ids = args.proposal or [row["proposal_id"] for row in pending_proposals(run_dir)]
        baselines = [service.prepare(pid, args.reviewer) for pid in ids]
        return {"status": "PREPARED", "baselines": [{"proposal_id": b.proposal_id, "baseline_id": b.baseline_id,
                                                      "evidence_fingerprint": b.evidence_fingerprint} for b in baselines], "provider_calls": 0}
    if args.review_command == "canonical":
        if args.chain:
            record = store.canonical_by_id(args.id) if args.id else None
            if record is None:
                raise ReviewError(ReviewErrorCode.PROPOSAL_NOT_FOUND, "canonical_not_found")
            chain = store.audit_chain(record.decision_id)
            return {"audit_chain": {"canonical": record.to_dict(), "decision": chain["decision"].to_dict(),
                                    "proposal_snapshot": chain["proposal_snapshot"].to_dict(), "baseline": chain["baseline"].to_dict(),
                                    "evidence_fingerprint": chain["evidence_fingerprint"]}}
        if args.id:
            record = store.canonical_by_id(args.id)
            records = [record] if record else []
        elif args.proposal:
            records = store.canonical_for_proposal(args.proposal)
        elif args.evidence_ref:
            records = store.canonical_by_evidence_ref(args.evidence_ref)
        else:
            records = store.canonical_records()
        return {"canonical": [r.to_dict() for r in records]}
    correction = None
    if args.correction_file:
        correction = json.loads(Path(args.correction_file).read_text(encoding="utf-8"))
    outcome = ApprovalService(run_dir).decide(
        args.proposal, args.action, args.reviewer, rationale=args.rationale, correction=correction,
        expected_evidence_fingerprint=args.expected_evidence_fingerprint,
    )
    write_view(run_dir)
    return {"status": "RECORDED", "idempotent_replay": outcome.idempotent_replay, "decision_id": outcome.decision.decision_id,
            "action": outcome.decision.action.value, "canonical_id": outcome.canonical.canonical_id if outcome.canonical else None,
            "provider_calls": 0}
