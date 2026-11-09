"""Semantic contracts, truth vocabulary, deterministic validation and identity helpers (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

SCHEMA_VERSION = "system-interpretation-1.0"
PROMPT_VERSION = "system-prompt-1"
CONTEXT_SCHEMA_VERSION = "system-context-1"

CLAIM_STATUSES = ("CONFIRMED", "INFERRED", "UNRESOLVED")
HUMAN_STATUS = {"CONFIRMED": "Confirmado", "INFERRED": "Inferido", "UNRESOLVED": "No resuelto"}
HUMAN_STATUS_VALUES = tuple(HUMAN_STATUS.values())

# Hierarchy: SYSTEM > SOLUTION > PROJECT > VIEW / DATA ; FLOW = cross-project relations of a solution.
KINDS = ("PROJECT", "VIEW", "DATA", "FLOW", "SOLUTION", "SYSTEM")
SECTIONS = {
    "PROJECT": ("purpose", "responsibilities", "consumers", "dependencies", "business_flow", "data_interactions", "unresolved"),
    "VIEW": ("behavior", "unresolved"),
    "DATA": ("interactions", "unresolved"),
    "FLOW": ("relations", "unresolved"),
    "SOLUTION": ("summary", "subsystems", "responsibilities", "interactions", "data", "unresolved"),
    "SYSTEM": ("summary", "solutions", "interaction_paths", "data", "cross_project", "unresolved"),
}
#: Named semantic models (each one is the validated content of one persisted request record).
SEMANTIC_MODELS = {
    "SYSTEM": "SystemInterpretation", "SOLUTION": "SolutionInterpretation", "PROJECT": "ProjectInterpretation",
    "VIEW": "ViewInterpretation", "FLOW": "CrossProjectFlowInterpretation", "DATA": "DataInteractionInterpretation",
}
COVERAGE_CONTRACT = "FullSystemCoverageManifest"

# Per-project coverage states: exactly one at completion; PENDING only exists in an interrupted run.
HUMAN_AND_MACHINE = "HUMAN_AND_MACHINE_DOCUMENTED"
MACHINE_ONLY = "MACHINE_ONLY_DOCUMENTED"
UNRESOLVED_NO_SOLUTION = "UNRESOLVED_NO_SOLUTION"
CONTROLLED_ERROR = "CONTROLLED_ERROR"
PENDING = "PENDING_INTERPRETATION"
FINAL_STATES = (HUMAN_AND_MACHINE, MACHINE_ONLY, UNRESOLVED_NO_SOLUTION, CONTROLLED_ERROR)

#: A claim that says a component is obsolete / unused is never accepted (absence of usage evidence != obsolescence).
OBSOLESCENCE = re.compile(
    r"(?i)\b(obsolet[oa]s?|c[oó]digo muerto|dead code|no se usa|sin uso|en desuso|no utilizad[oa]s?|inutilizad[oa]s?|deprecad[oa]s?|abandonad[oa]s?)\b")
#: Evidence identifiers, raw source paths / file names, line references and provider diagnostics never reach human prose.
LEAK = re.compile(
    r"(?:\b(?:EP|FLOW|CALL|DAO|PRJ|SOL|XPC|SRC|CMP|UID|REQ|RESP|CTX|SEM|SYS|CL)-[0-9A-Za-z]{4,})"
    r"|(?:\b[A-Za-z]:[\\/])"
    r"|(?:[\\/][\w.\-]+\.(?:vb|vbproj|ascx|aspx|sln|cs|py)\b)"
    r"|(?:\b[\w\-]+\.(?:vb|vbproj|ascx|aspx|sln|resx|master)\b)"
    r"|(?:\b(?:l[ií]neas?|lines?)\s+\d+)"
    r"|(?:\.(?:vb|cs|py):\d+)"
    r"|(?:(?i:copilot|gpt-\d|model_id|provider_id|claude))")
MAX_CLAIM_CHARS = 900


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_object(value: object) -> str:
    return sha256_text(canonical(value))


#: Truth-state markers that a provider repeats inside prose. The structured `status` is authoritative; the marker is presentation noise.
_STATE_WORD = r"(CONFIRMED|INFERRED|UNRESOLVED)"
_SEP = r"(?::|\s[–—-])\s*"            # "MARK:" or "MARK - " / "MARK — " (a dash needs a space before it)
_LEADING_MARKER = re.compile(rf"^\s*(?:\*\*)?{_STATE_WORD}(?:\*\*)?{_SEP}")
_SENTENCE_MARKER = re.compile(rf"(?<=[.!?;])\s+(?:\*\*)?{_STATE_WORD}(?:\*\*)?{_SEP}")
_BARE_STATE_WORD = re.compile(r"\b" + _STATE_WORD + r"\b")


def normalize_claim_text(text: str) -> str:
    """Deterministic, idempotent presentation normalization of a claim's prose (never touches its status, refs or provenance).

    1. A marker at the very start of the claim ("CONFIRMED: ...") is removed: the structured status already says it.
    2. A marker that opens a later sentence of a mixed claim ("CONFIRMED: a. INFERRED: b.") is rendered with the human
       vocabulary ("Inferido: b.") so the distinction survives.
    3. Any other standalone English state word that the provider wrote into the prose ("esa atribucion es INFERRED") is
       translated to the human vocabulary ("Inferido"), never deleted. Words that merely contain these letters are untouched."""
    if not isinstance(text, str):
        return text
    out = _LEADING_MARKER.sub("", text, count=1)
    out = _SENTENCE_MARKER.sub(lambda m: " " + HUMAN_STATUS[m.group(1)] + ": ", out)
    out = _BARE_STATE_WORD.sub(lambda m: HUMAN_STATUS[m.group(1)], out)
    return out.strip()


def normalize_record_semantic(record: dict) -> dict:
    """Copy of a persisted accepted record whose claim texts are presentation-normalized. The persisted record (and therefore
    request identity and dependency hashes, which are derived from the stored semantic) is never modified."""
    clone = dict(record)
    clone["semantic"] = {sec: [{**c, "text": normalize_claim_text(c.get("text", ""))} for c in claims]
                         for sec, claims in record.get("semantic", {}).items()}
    return clone


def has_leak(text: str) -> bool:
    return bool(LEAK.search(text or ""))


@dataclass(frozen=True)
class Fact:
    """One bounded, citable piece of persisted Evidence. `evidence` ids are internal provenance (never sent to the provider)."""
    ref: str
    kind: str          # name | structure | reference | view | flow | data | relation | unresolved | child
    certainty: str     # confirmed | inferred | unresolved
    text: str
    evidence: tuple = ()

    def for_provider(self) -> dict:
        return {"ref": self.ref, "kind": self.kind, "certainty": self.certainty, "fact": self.text}

    def identity_view(self) -> dict:
        return {"ref": self.ref, "kind": self.kind, "certainty": self.certainty, "text": self.text, "evidence": list(self.evidence)}


def output_schema(kind: str) -> dict:
    claim = {"type": "object", "required": ["text", "status", "refs"],
             "properties": {"text": {"type": "string"}, "status": {"enum": list(CLAIM_STATUSES)},
                            "refs": {"type": "array", "items": {"type": "string"}}, "subject": {"type": "string"}}}
    sections = SECTIONS[kind]
    return {"type": "object", "required": list(sections), "properties": {s: {"type": "array", "items": claim} for s in sections}}


@dataclass
class Validation:
    accepted: dict = field(default_factory=dict)      # section -> [claim]
    rejected: list = field(default_factory=list)      # [{section, text, reason}]
    downgraded: int = 0
    schema_ok: bool = False

    @property
    def accepted_count(self) -> int:
        return sum(len(v) for v in self.accepted.values())


def validate_semantic(kind: str, parsed: object, facts: list[Fact], claim_seed: str) -> Validation:
    """Deterministic grounding of an AI answer. The content of an accepted claim is never rewritten."""
    out = Validation()
    sections = SECTIONS[kind]
    if not isinstance(parsed, dict) or any(not isinstance(parsed.get(s), list) for s in sections):
        out.rejected.append({"section": "*", "text": "", "reason": "SCHEMA_INVALID"})
        return out
    out.schema_ok = True
    by_ref = {f.ref: f for f in facts}
    seen: set[tuple] = set()
    for section in sections:
        kept: list[dict] = []
        for raw in parsed[section]:
            text = raw.get("text") if isinstance(raw, dict) else None
            reason = None
            if not isinstance(text, str) or not text.strip():
                reason = "EMPTY_TEXT"
            elif len(text) > MAX_CLAIM_CHARS:
                reason = "TOO_LONG"
            elif not normalize_claim_text(text):
                reason = "EMPTY_TEXT"           # nothing but a truth-state marker
            status = raw.get("status") if isinstance(raw, dict) else None
            refs = raw.get("refs") if isinstance(raw, dict) else None
            subject = raw.get("subject") if isinstance(raw, dict) and isinstance(raw.get("subject"), str) else ""
            if reason is None and status not in CLAIM_STATUSES:
                reason = "INVALID_STATUS"
            if reason is None and (not isinstance(refs, list) or any(not isinstance(r, str) for r in refs)):
                reason = "INVALID_REFS"
            if reason is None:
                combined = f"{text} {subject}"
                if OBSOLESCENCE.search(combined):
                    reason = "OBSOLESCENCE_CLAIM"
                elif has_leak(combined):
                    reason = "HUMAN_LEAK"
                elif any(r not in by_ref for r in refs):
                    reason = "UNKNOWN_REF"
                elif status != "UNRESOLVED" and not refs:
                    reason = "NO_EVIDENCE"
                elif status != "UNRESOLVED" and all(by_ref[r].kind == "name" for r in refs):
                    reason = "NAME_ONLY_INFERENCE"
            if reason:
                out.rejected.append({"section": section, "text": text if isinstance(text, str) else "", "reason": reason})
                continue
            key = (section, text.strip(), subject)
            if key in seen:
                continue
            seen.add(key)
            final = status
            if status == "CONFIRMED" and not any(by_ref[r].certainty == "confirmed" for r in refs):
                final = "INFERRED"          # inference is never promoted to confirmed
                out.downgraded += 1
            kept.append({"claim_id": "CL-" + sha256_text(f"{claim_seed}|{section}|{len(kept)}|{text.strip()}")[:16],
                         "text": normalize_claim_text(text.strip()), "status": final, "refs": sorted(set(refs)), "subject": subject})
        out.accepted[section] = kept
    return out
