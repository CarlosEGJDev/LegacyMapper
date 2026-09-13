"""Parsing of the R8.4 human-review record and Markdown document text fields (DEBT-002, V4.1-R4)."""
import re

from legacy_documenter.documentation.second_review import EXTERNAL, PARTIAL, RESOLVED

HUMAN_CONFIRMED = {"C04", *RESOLVED}
EXPECTED = ({x: "ACCEPTED_AS_PARTIAL" for x in PARTIAL}
            | {x: "ACCEPTED_AS_UNRESOLVED_EXTERNAL" for x in EXTERNAL}
            | {x: "HUMAN_CONFIRMED" for x in RESOLVED})


def parse_human_record(text: str) -> dict[str, object]:
    """Parses the exact R8.4 decisions and rejects duplicate dispositions."""
    decisions = {}
    for key, value in re.findall(r"^(FMI-\d{3}|TMI-\d{3})=(HUMAN_CONFIRMED|ACCEPTED_AS_PARTIAL|ACCEPTED_AS_UNRESOLVED_EXTERNAL)(?:;[^\n]*)?$", text, re.M):
        if key in decisions:
            raise ValueError("DUPLICATE_HUMAN_DISPOSITION")
        decisions[key] = value
    return {
        "functional_decision": _field(text, "FUNCTIONAL_DOCUMENT_DECISION"),
        "technical_decision": _field(text, "TECHNICAL_DOCUMENT_DECISION"),
        "c04": _field(text, "C04"),
        "decisions": decisions,
        "external_exhausted": {x for x in EXTERNAL if re.search(rf"^{x}=ACCEPTED_AS_UNRESOLVED_EXTERNAL; evidence_exhausted=true$", text, re.M)},
    }


def _field(text: str, name: str) -> str | None:
    """Retrieves a single line-oriented contract field from Markdown."""
    match = re.search(rf"^{re.escape(name)}=([^\r\n;]+)", text, re.M)
    return match.group(1).strip() if match else None


def _details(text: str) -> dict[str, dict[str, object]]:
    """Recover canonical request traceability serialized in document Markdown."""
    result = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^- `((?:FMI|TMI)-\d{3})`", line)
        if not match:
            continue
        block = lines[index:index + 7]
        joined = "\n".join(block)
        ev = re.search(r"; evidencias: (.*)", joined)
        claim_refs = re.search(r"  - Claims: (.*?); evidencias:", joined)
        request_refs = re.search(r"  - Solicitudes originales: (.*)", joined)
        packages = re.search(r"  - Paquetes: (.*?); snapshots: (.*)", joined)
        result[match.group(1)] = {
            "evidence_ids": _csv(ev.group(1)) if ev else [],
            "assessment_claim_refs": _csv(claim_refs.group(1)) if claim_refs else [],
            "assessment_request_refs": _csv(request_refs.group(1)) if request_refs else [],
            "context_package_ids": _csv(packages.group(1)) if packages else [],
            "source_snapshot_ids": _csv(packages.group(2)) if packages else [],
        }
    return result


def _csv(value: str) -> list[str]:
    """Parses canonical comma-separated identifier fields, including N/A."""
    return [] if value == "N/A" else [x.strip() for x in value.split(",") if x.strip()]
