"""System knowledge product: human + machine projection of the persisted semantic model, plus its validation.

`project_system` reads only the baseline's Evidence partitions and the interpretation state directory. It never calls a provider and
never opens source code, so re-running it after a template change costs 0 provider requests.
"""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import shutil
from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

from . import human, machine
from . import planner as P
from .inventory import load_inventory
from .models import CLAIM_STATUSES, FINAL_STATES, LEAK, PENDING, normalize_record_semantic
from .store import RequestStore

PRODUCT_CONTRACT = "LegacyMapperSystemKnowledgeProduct"
MANIFEST_NAME = "ACCEPTANCE_MANIFEST.json"
_OWNED = ("human", "ai", "internal")
_LINK = re.compile(r'(?:href|src)="([^"]+)"')
_UPPER_STATE = re.compile(r"\b(AI_INTERPRETATION|CANONICAL|CONFIRMED|INFERRED|UNRESOLVED)\b")


class ProjectionError(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason, self.detail = reason, detail


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_assessment(a: P.Assessment) -> None:
    """Presentation boundary (owner acceptance R2, BD-1): swap every resolved record for a copy whose claim prose has no redundant
    truth-state marker. Runs AFTER `assess` because request identity / dependency hashes are derived from the stored semantic, so
    persisted accepted responses stay reusable with 0 provider calls; the persisted files are never rewritten."""
    items = [i for pc in a.projects.values() for i in pc.items]
    for unit in a.solutions.values():
        items += [i for i in (unit.flow, unit.item) if i]
    if a.system.item:
        items.append(a.system.item)
    for item in items:
        if item.record:
            item.record = normalize_record_semantic(item.record)


def current_records(a: P.Assessment) -> list[dict]:
    """The accepted records that the CURRENT baseline + dependencies resolve to (stale identities are excluded)."""
    found: dict[str, dict] = {}
    for pc in a.projects.values():
        for item in pc.items:
            if item.record:
                found[item.identity] = item.record
    for unit in a.solutions.values():
        for item in (unit.flow, unit.item):
            if item and item.record:
                found[item.identity] = item.record
    if a.system.item and a.system.item.record:
        found[a.system.item.identity] = a.system.item.record
    return [found[k] for k in sorted(found)]


def validate_product(out: Path, inv, a: P.Assessment, records: list[dict]) -> dict:
    human_dir = out / "human"
    pages = sorted(human_dir.rglob("*.html"))
    broken_links = missing_assets = leaks = invalid_states = 0
    details: list[str] = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for target in _LINK.findall(text):
            if target.startswith(("http:", "https:", "mailto:", "data:", "#")):
                continue
            path = (page.parent / target.split("#")[0]).resolve()
            if not path.exists():
                is_asset = target.split("#")[0].endswith((".css", ".svg", ".js", ".png"))
                if is_asset:
                    missing_assets += 1
                else:
                    broken_links += 1
                details.append(f"{page.relative_to(out).as_posix()} -> {target}")
        visible = htmllib.unescape(re.sub(r"<[^>]+>", " ", text))
        if LEAK.search(visible):
            leaks += 1
            details.append(f"leak in {page.relative_to(out).as_posix()}: {LEAK.search(visible).group(0)!r}")
        if _UPPER_STATE.search(visible):
            invalid_states += 1
            details.append(f"invalid state vocabulary in {page.relative_to(out).as_posix()}")
    for rec in records:
        for claims in rec["semantic"].values():
            invalid_states += sum(1 for c in claims if c["status"] not in CLAIM_STATUSES)
    ai_check = machine.check_machine(out / "ai")
    coverage = json.loads((out / "ai" / "coverage.json").read_text(encoding="utf-8")) if (out / "ai" / "coverage.json").is_file() else {}
    covered = {p["project_id"]: p["state"] for p in coverage.get("projects", [])}
    omissions = 0
    for pid, p in inv.projects.items():
        if covered.get(pid) not in (*FINAL_STATES, PENDING) or not (human_dir / "projects" / f"{p.slug}.html").is_file():
            omissions += 1
            details.append(f"silent omission: {p.display}")
    pdf = human_dir / "IST_Complete.pdf"
    pdf_ok = pdf.is_file() and pdf.read_bytes()[:5] == b"%PDF-"
    return {"html_pages": len(pages), "broken_links": broken_links, "missing_assets": missing_assets, "invalid_json": ai_check["invalid_json"],
            "dangling_ids": ai_check["dangling_ids"], "duplicate_ids": ai_check["duplicate_ids"], "human_provenance_leaks": leaks,
            "invalid_human_states": invalid_states, "silent_project_omissions": omissions, "pdf_valid": pdf_ok,
            "defects": broken_links + missing_assets + ai_check["invalid_json"] + ai_check["dangling_ids"] + ai_check["duplicate_ids"] + leaks + invalid_states + omissions + (0 if pdf_ok else 1),
            "details": (details + ai_check["details"])[:50]}


def project_system(baseline: str | Path, state_dir: str | Path, output: str | Path, *, verify: str = "hash") -> dict:
    store = RequestStore(state_dir)
    state = store.load_state()
    if not state.get("policy"):
        raise ProjectionError("NO_INTERPRETATION_STATE", "run interpret-system first")
    out = Path(output)
    if out.resolve() in (Path(baseline).resolve(), Path(state_dir).resolve()):
        raise ProjectionError("OUTPUT_OVERLAPS_INPUT", "use a separate --output")
    manifest = out / MANIFEST_NAME
    if any((out / d).exists() for d in _OWNED):
        try:
            owned = json.loads(manifest.read_text(encoding="utf-8")).get("contract") == PRODUCT_CONTRACT
        except (OSError, ValueError):
            owned = False
        if not owned:
            raise ProjectionError("PRODUCT_OUTPUT_NOT_OWNED", "output already holds human/ai/internal that this command did not create")
        for d in _OWNED:
            shutil.rmtree(out / d, ignore_errors=True)
    inv = load_inventory(baseline, verify)
    a = P.assess(inv, store, state["policy"], state.get("errors", {}))
    normalize_assessment(a)
    records = current_records(a)
    synthetic = any(r["provider"].get("synthetic") for r in records)
    machine_counts = machine.build_machine(inv, a, state, out, records)
    site = human.build_site(inv, a, records, synthetic)
    files = human.write_site(site, out)
    validation = validate_product(out, inv, a, records)
    listing = sorted(p for d in _OWNED for p in (out / d).rglob("*") if p.is_file())
    doc = {"contract": PRODUCT_CONTRACT, "complete": a.complete, "synthetic_provider": synthetic, "baseline": inv.identity.as_dict(),
           "policy": state["policy"], "counts": state.get("counts", {}), "machine": machine_counts, "validation": validation,
           "files": [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size, "sha256": _sha(p)} for p in listing],
           "providers": sorted({f"{r['provider']['provider_id']}/{r['provider']['model_id']}" for r in records})}
    atomic_write_text(manifest, json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    return doc
