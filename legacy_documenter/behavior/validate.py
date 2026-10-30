"""Deterministic validation of structured explanations (post-V5 H4-R4).

Python validates what any interpretation layer (the deterministic explainer today, an AI provider later) produced:

* referenced views / events / methods / classes / procedures must exist in the evidence;
* `source_refs` must resolve (baseline ids, `src:<file>:<line>` inside the file as analyzed (persisted line count), projects/solutions known to the baseline);
* CONFIRMED needs deterministic support (>= 1 resolvable ref, deterministic origin); INFERRED must state its basis; UNRESOLVED stays
  unresolved; an AI-origin claim can only be AI_INTERPRETATION (anything stronger is downgraded, never promoted);
* claims that cite non-existent entities or fabricated refs are REJECTED (dropped), with the reason recorded.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .evidence import BehaviorContext, norm_path
from .model import AI_INTERPRETATION, CANONICAL, CONFIRMED, INFERRED, STATUSES, UNRESOLVED, Claim

_SRC = re.compile(r"^src:(.+):(\d+)$")


@dataclass
class Violation:
    code: str
    where: str
    detail: str
    action: str                           # rejected | downgraded | noted


@dataclass
class ReferenceIndex:
    bc: BehaviorContext
    _line_counts: dict = field(default_factory=dict)

    def _lines(self, rel: str) -> int:
        """Line count of an analyzed file, from persisted UI Evidence (0 when the evidence holds no count for it)."""
        return self.bc.ui.lines_of(rel)

    def ref_ok(self, ref: str) -> bool:
        m = _SRC.match(ref)
        if m:
            rel, line = m.group(1), int(m.group(2))
            known = rel.replace("/", "\\").lower() in {f.replace("/", "\\").lower() for f in self.bc.rel_files}
            return known and 1 <= line <= max(1, self._lines(rel))
        if ref.startswith("project:"):
            return ref[8:].lower() == self.bc.project_path.lower() or any(str(p.get("path", "")).lower() == ref[8:].lower() for p in self.bc.ctx.source["projects"])
        if ref.startswith("solution:"):
            return any(str(s.get("name")) == ref[9:] for s in self.bc.ctx.source["solutions"])
        return ref in self.bc.known_refs or ref in self.bc.dao or ref in self.bc.flows_by_ep or any(ref == ep["id"] for eps in self.bc.eps_by_webform.values() for ep in eps)

    def entity_ok(self, kind: str, name: str, view: str = "") -> bool:
        low = name.lower()
        if kind == "view":
            return norm_path(name) in self.bc.webforms or norm_path(name) in {norm_path(p) for p in self.bc.view_paths} or any(
                f.replace("/", "\\").lower() == norm_path(name) for f in self.bc.rel_files)
        if kind == "event":
            ctrl, _, ev = name.partition(".")
            views = [self.bc.view(view)] if view else []
            return any(e.event.lower() == ev.lower() and (e.control.lower() == ctrl.lower() or not ctrl) for v in views for e in v.events)
        if kind == "method":
            v = self.bc.view(view) if view else None
            subs = {s["name"].lower() for s in (v.code.subs if v and v.code else [])}
            handlers = {e.handler.lower() for e in (v.events if v else [])}
            daos = {str(d.get("method") or "").lower() for d in self.bc.dao.values()}
            return low in subs or low in handlers or low in daos
        if kind == "class":
            return low in self.bc.all_class_names() or any(str(d.get("class") or "").lower() == low for d in self.bc.dao.values())
        if kind == "procedure":
            procs = {str(sp.get("name") or sp.get("full_name") or sp).lower() if isinstance(sp, dict) else str(sp).lower()
                     for sp in self.bc.ctx.source.get("stored_procedures", [])}
            return low in procs or any(
                str(d.get("procedure") or "").lower() == low for v in self.bc._views.values() for e in v.events for d in e.data_ops)
        return False


def check_claim(claim: Claim, refs: ReferenceIndex, where: str, view: str = "") -> tuple[Claim | None, list[Violation]]:
    out: list[Violation] = []
    c = Claim(**{**claim.__dict__})
    if c.status not in STATUSES:
        return None, [Violation("INVALID_STATUS", where, c.status, "rejected")]
    for ref in c.source_refs:
        if not refs.ref_ok(ref):
            return None, [Violation("UNRESOLVED_SOURCE_REF", where, ref, "rejected")]
    for ent in c.entities:
        if not refs.entity_ok(ent.get("type", ""), ent.get("name", ""), view):
            return None, [Violation("UNKNOWN_ENTITY", where, f'{ent.get("type")}:{ent.get("name")}', "rejected")]
    if c.origin == "ai":
        if c.status != AI_INTERPRETATION:
            out.append(Violation("AI_CLAIM_DOWNGRADED", where, f"{c.status}->AI_INTERPRETATION", "downgraded"))
            c.status = AI_INTERPRETATION
        return c, out
    if c.status == CANONICAL:
        out.append(Violation("CANONICAL_NOT_FROM_EVIDENCE", where, "canonical requires an explicit human decision record", "downgraded"))
        c.status = AI_INTERPRETATION
    elif c.status == CONFIRMED and not c.source_refs:
        out.append(Violation("CONFIRMED_WITHOUT_SUPPORT", where, c.text[:80], "downgraded"))
        c.status = UNRESOLVED
        c.basis = c.basis or "afirmación sin soporte determinista: degradada"
    elif c.status == INFERRED and not c.basis.strip():
        out.append(Violation("INFERRED_WITHOUT_BASIS", where, c.text[:80], "downgraded"))
        c.status = UNRESOLVED
    return c, out


def _claims_of(view) -> list[tuple[str, list[Claim]]]:
    groups = [("what_it_does", view.what_it_does), ("receives", view.receives), ("ai_interpretation", view.ai_interpretation),
              ("unresolved.known", view.unresolved.known), ("unresolved.inferred", view.unresolved.inferred), ("unresolved.unresolved", view.unresolved.unresolved)]
    for a in view.actions:
        groups.append((f"action[{a.action}].simple", [a.simple] if a.simple else []))
        groups.append((f"action[{a.action}].result", a.result))
    return groups


def validate_view(refs: ReferenceIndex, view) -> list[Violation]:
    """Validates (and rewrites in place) one ViewExplanation; returns every violation found."""
    violations: list[Violation] = []
    bc = refs.bc
    for where, claims in _claims_of(view):
        kept = []
        for c in claims:
            nc, vs = check_claim(c, refs, f"{view.name}:{where}", view.view)
            violations += vs
            if nc is not None:
                kept.append(nc)
        claims[:] = kept
    for a in list(view.actions):
        if a.technical_path is None:
            continue
        ok_steps = []
        for s in a.technical_path.steps:
            bad = [r for r in s.get("source_refs", []) if not refs.ref_ok(r)]
            if bad:
                violations.append(Violation("UNRESOLVED_SOURCE_REF", f"{view.name}:path[{a.action}]", bad[0], "rejected"))
                continue
            if s["kind"] == "procedure" and not refs.entity_ok("procedure", s["label"], view.view):
                violations.append(Violation("UNKNOWN_ENTITY", f"{view.name}:path[{a.action}]", f"procedure:{s['label']}", "rejected"))
                continue
            ok_steps.append(s)
        a.technical_path.steps = ok_steps
        for d in list(a.data):
            if d.status == CONFIRMED and not all(refs.ref_ok(r) for r in d.source_refs):
                violations.append(Violation("UNRESOLVED_SOURCE_REF", f"{view.name}:data[{d.object_name}]", ",".join(d.source_refs), "rejected"))
                a.data.remove(d)
    for inv in list(view.reaches) + list(view.reached_by):
        if not all(refs.ref_ok(r) for r in inv.source_refs):
            violations.append(Violation("UNRESOLVED_SOURCE_REF", f"{view.name}:invocation", inv.file, "rejected"))
            (view.reaches if inv in view.reaches else view.reached_by).remove(inv)
        elif not inv.target_exists:
            violations.append(Violation("INVOCATION_TARGET_MISSING", f"{view.name}:invocation", inv.target_view, "noted"))
    if view.ui is not None and view.ui.status == "DOCUMENTARY_RECONSTRUCTION" and bc.view(view.view).markup is not None:
        evidenced = {c.id or f"{c.tag}@{c.line}" for c in bc.view(view.view).markup.controls}
        extra = [c.id for c in view.ui.controls if (c.id or "") not in evidenced]
        if extra:
            violations.append(Violation("WIREFRAME_CONTROL_NOT_IN_EVIDENCE", f"{view.name}:ui", ",".join(extra), "rejected"))
            view.ui.controls = [c for c in view.ui.controls if c.id not in extra]
    return violations


def apply_ai_overlay(refs: ReferenceIndex, view, ai_claims: list[dict]) -> list[Violation]:
    """Adds AI-produced claims to `view.ai_interpretation` after validation. Any status the AI asks for is forced to AI_INTERPRETATION."""
    violations: list[Violation] = []
    for i, raw in enumerate(ai_claims):
        claim = Claim(text=str(raw.get("text", "")), status=str(raw.get("status", AI_INTERPRETATION)), source_refs=list(raw.get("source_refs", [])),
                      basis=str(raw.get("basis", "")), origin="ai", entities=list(raw.get("entities", [])))
        if not claim.text.strip():
            violations.append(Violation("EMPTY_CLAIM", f"{view.name}:ai[{i}]", "", "rejected"))
            continue
        checked, vs = check_claim(claim, refs, f"{view.name}:ai[{i}]", view.view)
        violations += vs
        if checked is not None:
            view.ai_interpretation.append(checked)
    return violations
