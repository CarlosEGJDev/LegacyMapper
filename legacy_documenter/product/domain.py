"""Human-confirmed domain knowledge (post-V5 H4).

An explicit, structured glossary supplied by a person, e.g. `COB = Cobranza`. It is never inferred from names and never mixed with
deterministic source evidence: every entry carries `origin = HUMAN_CONFIRMED`, `status = CANONICAL` (the existing human-approved status)
and `source = human`. Documents show it in its own, visibly different table; AI projections keep it in its own section.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

CONTRACT = "LegacyMapperDomainKnowledge"
CONTRACT_VERSION = "1.0"
ORIGIN = "HUMAN_CONFIRMED"
STATUS = "CANONICAL"


class DomainKnowledgeError(ValueError):
    pass


def load(path: str | Path | None) -> list[dict]:
    """Validated terms (sorted, deterministic). `None` / missing path = no human knowledge supplied."""
    if not path:
        return []
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DomainKnowledgeError(f"domain knowledge file unreadable: {exc}") from exc
    terms = data.get("terms") if isinstance(data, dict) else None
    if not isinstance(terms, list):
        raise DomainKnowledgeError("domain knowledge: a top-level `terms` list is required")
    out: dict[str, dict] = {}
    for i, t in enumerate(terms):
        if not isinstance(t, dict):
            raise DomainKnowledgeError(f"terms[{i}]: object expected")
        term, meaning = str(t.get("term", "")).strip(), str(t.get("meaning", "")).strip()
        if not term or not meaning:
            raise DomainKnowledgeError(f"terms[{i}]: `term` and `meaning` are required")
        if t.get("status") != STATUS:
            raise DomainKnowledgeError(f"terms[{i}] «{term}»: status must be {STATUS} (explicit human confirmation)")
        if str(t.get("source", "")).lower() != "human":
            raise DomainKnowledgeError(f"terms[{i}] «{term}»: source must be `human`")
        if term.lower() in out:
            raise DomainKnowledgeError(f"duplicate term «{term}»")
        entry = {"term": term, "meaning": meaning, "status": STATUS, "source": "human", "origin": ORIGIN}
        if t.get("note"):
            entry["note"] = str(t["note"]).strip()
        out[term.lower()] = entry
    return [out[k] for k in sorted(out)]


def tokens(name: str) -> set[str]:
    parts = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", name or "")
    return {p.lower() for p in parts} | {w.lower() for w in re.findall(r"\w+", name or "")}


def appears_in(terms: list[dict], names: list[str]) -> dict[str, list[str]]:
    """term -> names (views / projects) whose name contains it as a word or camel-case token. A convenience index, not a fact."""
    return {t["term"]: sorted(n for n in names if t["term"].lower() in tokens(n)) for t in terms}
