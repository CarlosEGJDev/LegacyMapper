"""Deterministic human view of pending proposals, decisions and canonical knowledge (V5.7).

Pure formatting over the persisted store: same store -> same bytes. Written to `knowledge/REVIEW_VIEW.md`
only after a human decision exists; existing V5.2 templates and proposal artifacts are untouched.
"""
from __future__ import annotations

from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

from .evidence import EvidenceIndex, evidence_fingerprint
from .models import ReviewError
from .service import load_proposals, scope_of
from .store import ReviewStore

VIEW_FILE = Path("knowledge") / "REVIEW_VIEW.md"


def pending_proposals(run_dir: str | Path) -> list[dict]:
    """Proposals with no terminal decision, each with the evidence fingerprint a reviewer should confirm."""
    store = ReviewStore(run_dir)
    try:
        _, proposals = load_proposals(run_dir)
    except ReviewError:
        return []  # proposals/ cleared by a later run: nothing pending; decisions and snapshots remain readable
    index = EvidenceIndex(run_dir)
    rows = []
    for proposal in sorted(proposals, key=lambda p: p["proposal_id"]):
        history = store.decisions_for(proposal["proposal_id"])
        if history and history[-1].action.value != "DEFER":
            continue
        try:
            fp = evidence_fingerprint(index.snapshot(proposal.get("evidence_refs", [])))
        except Exception:
            fp = None
        rows.append({"proposal_id": proposal["proposal_id"], "scope": scope_of(proposal), "statement": proposal["statement"],
                     "evidence_refs": list(proposal.get("evidence_refs", [])), "evidence_fingerprint": fp,
                     "deferred": bool(history), "baseline_prepared": bool(store.baselines_for(proposal["proposal_id"]))})
    return rows


def render_view(run_dir: str | Path) -> str:
    """Markdown text of pending proposals, decisions and canonical records."""
    store = ReviewStore(run_dir)
    lines = ["# Knowledge Review View", "", "Decisions are human acts. Canonical records reference Evidence and proposals; they never replace them.", ""]
    lines += ["## Pending proposals", ""]
    pending = pending_proposals(run_dir)
    if not pending:
        lines += ["_none_", ""]
    for row in pending:
        scope = row["scope"]
        label = f"PARTIAL (parent `{scope['parent_flow_id']}`, segment `{scope['segment_id']}`, {scope['included_path_count']} included / {scope['omitted_path_count']} omitted)" if scope["partial"] else "COMPLETE"
        lines += [f"- `{row['proposal_id']}` — {label}{' — DEFERRED' if row['deferred'] else ''}", f"  - Statement: {row['statement']}",
                  f"  - Evidence fingerprint: `{row['evidence_fingerprint']}`"]
    lines += ["", "## Decisions", ""]
    decisions = store.decisions()
    if not decisions:
        lines += ["_none_", ""]
    for d in decisions:
        lines += [f"- `{d.decision_id}` — **{d.action.value}** `{d.proposal_id}` by {d.reviewer} at {d.decided_at}"]
        if d.rationale:
            lines += [f"  - Rationale: {d.rationale}"]
    lines += ["", "## Canonical knowledge", ""]
    records = store.canonical_records()
    if not records:
        lines += ["_none_", ""]
    for r in records:
        scope = r.scope
        label = f"PARTIAL (parent `{scope['parent_flow_id']}`, segment `{scope['segment_id']}`)" if scope.get("partial") else "COMPLETE"
        lines += [f"- `{r.canonical_id}` — {label} from `{r.source_proposal_id}` via `{r.decision_id}` ({r.decision_action.value})",
                  f"  - {r.content['statement']}", f"  - Evidence: {', '.join(f'`{ref}`' for ref in r.evidence_refs)}"]
    lines.append("")
    return "\n".join(lines)


def write_view(run_dir: str | Path) -> Path:
    """Atomically writes `knowledge/REVIEW_VIEW.md` and returns its path."""
    target = Path(run_dir) / VIEW_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(target, render_view(run_dir))
    return target
