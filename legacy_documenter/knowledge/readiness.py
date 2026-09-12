"""V3-R9 deterministic knowledge-readiness gate (no LLM or network access)."""
import hashlib
import json
import re
from pathlib import Path
from typing import TypeAlias

from legacy_documenter.documentation.human_review import parse_document
from legacy_documenter.documentation.second_review import EXTERNAL, PARTIAL, RESOLVED

ALLOWED_STATUSES = {"CONFIRMED", "INTERPRETED", "UNRESOLVED"}
ALLOWED_METRIC_SCOPES = {"SYSTEM_TOTAL", "SYSTEM_LINKED", "COVERAGE_PARTITION", "UNRESOLVED_SCOPE"}
HUMAN_CONFIRMED = {"C04", *RESOLVED}
EXPECTED = ({x: "ACCEPTED_AS_PARTIAL" for x in PARTIAL}
            | {x: "ACCEPTED_AS_UNRESOLVED_EXTERNAL" for x in EXTERNAL}
            | {x: "HUMAN_CONFIRMED" for x in RESOLVED})
PROHIBITED_ASSERTIONS = [
    "Declarar MVC basándose en ausencia de referencias MVC.",
    "Declarar una arquitectura formal sin evidencia autoritativa.",
    "Asignar propósito de negocio a procedimientos almacenados solo por su nombre.",
    "Resolver información externa aceptada como no resuelta.",
    "Convertir relaciones parciales en relaciones completas.",
]
SECRET_RE = re.compile(r"(?i)(password|passwd|pwd|api[_-]?key|secret|token)\s*[:=]\s*[^\s,;]+")
JsonObject: TypeAlias = dict[str, object]


def _read(path: Path) -> str:
    """Reads a UTF-8 canonical artifact without modifying it."""
    return path.read_text(encoding="utf-8")


def _hash(path: Path) -> str:
    """Returns the SHA-256 used by immutability and repeatability checks."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_human_record(text: str) -> JsonObject:
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


def _details(text: str) -> dict[str, JsonObject]:
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


def _canonical_catalog(root: Path) -> tuple[set[str], set[str], set[str], set[str]]:
    """Builds closed evidence, assessment, package and snapshot identifier sets."""
    assessments = []
    for name in ("LOCAL_ASSESSMENTS.json", "INTERMEDIATE_ASSESSMENTS.json"):
        assessments.extend(json.loads(_read(root / "output/v3_r7_2" / name))["assessments"])
    evidence, assessment_ids, packages, snapshots = set(), set(), set(), set()
    for entry in assessments:
        payload = entry.get("assessment_payload", entry)
        assessment_ids.add(payload.get("assessment_id") or entry.get("assessment_id"))
        packages.update(payload.get("context_package_ids", []))
        snapshots.update(payload.get("source_snapshots", []))
        for claim in payload.get("claims", []):
            evidence.update(claim.get("evidence_refs", []))
            packages.update(claim.get("context_package_ids", []))
        for missing in payload.get("missing_information", []):
            evidence.update(missing.get("related_evidence_ids", []))
    return evidence, assessment_ids, packages, snapshots


def evidence_closed(documents: dict[str, JsonObject], details: dict[str, dict[str, JsonObject]],
                    snapshots: dict[str, str | None], catalog: tuple[set[str], set[str], set[str], set[str]]) -> bool:
    """Validates the complete document-to-canonical-evidence traceability chain."""
    evidence, assessments, packages, known_snapshots = catalog
    claim_refs = {ref for document in documents.values() for claim in document["claims"] for ref in claim["evidence_refs"]}
    traced = [item for values in details.values() for item in values.values()]
    request_evidence = {ref for item in traced for ref in item["evidence_ids"]}
    request_packages = {ref for item in traced for ref in item["context_package_ids"]}
    request_snapshots = {ref for item in traced for ref in item["source_snapshot_ids"]}
    assessment_refs = {ref.split(":", 1)[0] for item in traced for ref in item["assessment_claim_refs"] + item["assessment_request_refs"]}
    return (claim_refs <= evidence and request_evidence <= evidence and request_packages <= packages
            and assessment_refs <= assessments and request_snapshots <= known_snapshots
            and set(snapshots.values()) <= known_snapshots
            and all(item["evidence_ids"] and item["source_snapshot_ids"] and item["context_package_ids"]
                    and (item["assessment_claim_refs"] or item["assessment_request_refs"]) for item in traced))


def evidence_closure_diagnostics(documents: dict[str, JsonObject], details: dict[str, dict[str, JsonObject]],
                                 snapshots: dict[str, str | None], catalog: tuple[set[str], set[str], set[str], set[str]]) -> dict[str, list[str]]:
    """Lists unresolved identifiers by namespace for safe diagnostic output."""
    evidence, assessments, packages, known_snapshots = catalog
    traced = [item for values in details.values() for item in values.values()]
    actual = {
        "evidence": {ref for document in documents.values() for claim in document["claims"] for ref in claim["evidence_refs"]} | {ref for item in traced for ref in item["evidence_ids"]},
        "assessments": {ref.split(":", 1)[0] for item in traced for ref in item["assessment_claim_refs"] + item["assessment_request_refs"]},
        "packages": {ref for item in traced for ref in item["context_package_ids"]},
        "snapshots": set(snapshots.values()) | {ref for item in traced for ref in item["source_snapshot_ids"]},
    }
    known = {"evidence": evidence, "assessments": assessments, "packages": packages, "snapshots": known_snapshots}
    return {key: sorted(actual[key] - known[key]) for key in actual}


def _csv(value: str) -> list[str]:
    """Parses canonical comma-separated identifier fields, including N/A."""
    return [] if value == "N/A" else [x.strip() for x in value.split(",") if x.strip()]


def validate_preconditions(functional: str, technical: str, review: JsonObject) -> bool:
    """Checks approvals, eligibility, all dispositions and exhaustion markers."""
    metadata = ("document_status=APPROVED", "human_review_required=false", "approved=true", "knowledge_source_eligible=true")
    return (all(x in functional for x in metadata) and all(x in technical for x in metadata)
            and review["functional_decision"] == "APPROVED"
            and review["technical_decision"] == "APPROVED"
            and review["c04"] == "HUMAN_CONFIRMED"
            and review["decisions"] == EXPECTED
            and review["external_exhausted"] == EXTERNAL)


def validate_claims(documents: dict[str, JsonObject]) -> bool:
    """Ensures claims keep allowed semantic statuses and supporting evidence."""
    claims = [claim for document in documents.values() for claim in document["claims"]]
    return bool(claims) and all(c["status"] in ALLOWED_STATUSES and c["evidence_refs"] for c in claims)


def architecture_valid(technical_text: str, human_text: str, architecture_evidence: JsonObject) -> bool:
    """Preserves supported WebForms evidence without inventing a formal architecture."""
    preserved = technical_text + "\n" + human_text
    required = ("WebForms", ".aspx", ".ascx", "code-behind", "Inherits",
                "MVC no está establecido", "No se encontró declaración formal autoritativa")
    forbidden = ("ARCHITECTURE_CONFIRMED", "MVC está establecido", "Clean Architecture confirmada", "Arquitectura hexagonal confirmada")
    indicators = {x["indicator"]: x["status"] for x in architecture_evidence["DETERMINISTIC_INDICATORS"]}
    return (all(x in preserved for x in required)
            and indicators.get("WEBFORMS_USAGE") == "SUPPORTED"
            and indicators.get("MVC_FRAMEWORK_REFERENCE") == "INSUFFICIENT_EVIDENCE"
            and architecture_evidence.get("pattern_confirmed") is False
            and not any(x in preserved for x in forbidden))


def quantitative_valid(texts: dict[str, str]) -> bool:
    """Accepts only explicit metric scopes validated by the R7.2.4 contract."""
    scopes = re.findall(r"; alcance=([^;\r\n]+);", "\n".join(texts.values()))
    return bool(scopes) and set(scopes) <= ALLOWED_METRIC_SCOPES and "alcance=UNRESOLVED_SCOPE" not in "\n".join(texts.values())


def build_projection(documents: dict[str, JsonObject], details: dict[str, dict[str, JsonObject]],
                     review: JsonObject, snapshots: dict[str, str | None]) -> list[JsonObject]:
    """Projects approved claims and human dispositions without reinterpreting them."""
    records = []
    for source, document in documents.items():
        for claim in document["claims"]:
            status = claim["status"]
            eligibility = {"CONFIRMED": "ELIGIBLE_FACT", "INTERPRETED": "ELIGIBLE_INTERPRETATION", "UNRESOLVED": "INELIGIBLE"}[status]
            records.append({
                "record_id": f"KR-{source.upper()}-{claim['claim_id']}", "source_document": source,
                "source_claim_id": claim["claim_id"], "semantic_status": status,
                "human_disposition": "HUMAN_CONFIRMED" if claim["claim_id"] == "C04" and source == "functional" else None,
                "statement": claim["statement"], "evidence_ids": claim["evidence_refs"],
                "source_snapshot_ids": [snapshots[source]],
                "provenance_type": "HUMAN_REVIEW_CONFIRMED_INTERPRETATION" if claim["claim_id"] == "C04" and source == "functional" else ("DETERMINISTIC_EVIDENCE" if status == "CONFIRMED" else "EVIDENCE_CONSTRAINED_INTERPRETATION"),
                "uncertainty": "explicit unresolved claim" if status == "UNRESOLVED" else ("interpretation; not a deterministic fact" if status == "INTERPRETED" else None),
                "knowledge_eligibility": eligibility,
            })
    missing_by_id = {x["request_id"]: x for document in documents.values() for x in document["missing_information"]}
    for target, disposition in sorted(review["decisions"].items()):
        source = "functional" if target.startswith("FMI") else "technical"
        info = details[source][target]
        eligibility = {"HUMAN_CONFIRMED": "ELIGIBLE_FACT", "ACCEPTED_AS_PARTIAL": "ELIGIBLE_PARTIAL", "ACCEPTED_AS_UNRESOLVED_EXTERNAL": "ELIGIBLE_UNRESOLVED_LIMITATION"}[disposition]
        item = missing_by_id[target]
        records.append({
            "record_id": f"KR-{target}", "source_document": source, "source_claim_id": target,
            "semantic_status": "UNRESOLVED" if target in EXTERNAL else "PARTIAL_INFORMATION",
            "human_disposition": disposition, "statement": item["question"],
            "evidence_ids": info["evidence_ids"], "source_snapshot_ids": info["source_snapshot_ids"],
            "provenance_type": "HUMAN_REVIEW_DISPOSITION", "uncertainty": item["reason"],
            "knowledge_eligibility": eligibility,
            "evidence_exhausted": target in EXTERNAL,
            "context_package_ids": info["context_package_ids"],
        })
    return records


def build_boundary(records: list[JsonObject]) -> dict[str, list[str]]:
    """Groups projected records into runtime-consumable knowledge boundaries."""
    buckets = {
        "WHAT_IS_KNOWN": [x["record_id"] for x in records if x["knowledge_eligibility"] == "ELIGIBLE_FACT"],
        "WHAT_IS_INTERPRETED": [x["record_id"] for x in records if x["knowledge_eligibility"] == "ELIGIBLE_INTERPRETATION"],
        "WHAT_IS_PARTIALLY_KNOWN": [x["record_id"] for x in records if x["knowledge_eligibility"] == "ELIGIBLE_PARTIAL"],
        "WHAT_IS_UNKNOWN_AND_ACCEPTED": [x["record_id"] for x in records if x["knowledge_eligibility"] == "ELIGIBLE_UNRESOLVED_LIMITATION"],
        "WHAT_IS_NOT_ALLOWED_TO_BE_ASSERTED": PROHIBITED_ASSERTIONS,
    }
    return buckets


def _safe(payload: object) -> bool:
    """Prevents common credential-shaped values from entering R9 outputs."""
    return not SECRET_RE.search(json.dumps(payload, ensure_ascii=False))


def _execute(workspace: str | Path = ".") -> JsonObject:
    """Executes the deterministic gate and writes only the four R9 JSON artifacts."""
    root = Path(workspace)
    paths = {"functional": root / "output/LEVANTAMIENTO_FUNCIONAL.md", "technical": root / "output/LEVANTAMIENTO_TECNICO.md"}
    texts = {key: _read(path) for key, path in paths.items()}
    human_path = root / "codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md"
    human_text = _read(human_path)
    review = parse_human_record(human_text)
    documents = {key: parse_document(value) for key, value in texts.items()}
    details = {key: _details(value) for key, value in texts.items()}
    snapshots = {key: _field(value, "source_snapshots") for key, value in texts.items()}
    preconditions = validate_preconditions(texts["functional"], texts["technical"], review)
    claims_ok = validate_claims(documents)
    catalog = _canonical_catalog(root)
    traceability = evidence_closed(documents, details, snapshots, catalog)
    closure_diagnostics = evidence_closure_diagnostics(documents, details, snapshots, catalog)
    projection = build_projection(documents, details, review, snapshots)
    boundary = build_boundary(projection)
    architecture_evidence = json.loads(_read(root / "output/v3_r8_1/ARCHITECTURE_EVIDENCE.json"))
    architecture = architecture_valid(texts["technical"], human_text, architecture_evidence)
    security = _safe(projection) and _safe(boundary)
    checks = {"preconditions": preconditions, "claim_integrity": claims_ok, "evidence_closure": traceability,
              "quantitative_integrity": quantitative_valid(texts), "architecture_integrity": architecture,
              "knowledge_projection": bool(projection), "knowledge_boundary": all(boundary.values()), "security": security}
    readiness = "READY" if all(checks.values()) else "BLOCKED"
    output = root / "output/v3_r9"
    output.mkdir(parents=True, exist_ok=True)
    readiness_payload = {"status": "V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE", "readiness": readiness,
                         "checks": checks, "ai_knowledge_allowed": readiness == "READY", "ai_knowledge_generated": False,
                         "real_llm_calls": 0, "provider_calls": 0}
    trace = {"documents": {key: {"sha256": _hash(path), "claims": len(documents[key]["claims"]), "missing_information": len(documents[key]["missing_information"]), "source_snapshot": snapshots[key]} for key, path in paths.items()},
             "human_review": {"path": str(human_path.relative_to(root)).replace("\\", "/"), "sha256": _hash(human_path), "dispositions": len(review["decisions"])},
             "claim_evidence_links": sum(len(c["evidence_refs"]) for d in documents.values() for c in d["claims"]),
             "request_traceability_records": sum(len(x) for x in details.values()), "unresolved_aliases": closure_diagnostics}
    payloads = {"KNOWLEDGE_READINESS.json": readiness_payload,
                "KNOWLEDGE_PROJECTION.json": {"schema_version": "V3-R9", "records": projection},
                "KNOWLEDGE_BOUNDARY.json": {"schema_version": "V3-R9", **boundary},
                "READINESS_TRACEABILITY.json": trace}
    for name, payload in payloads.items():
        (output / name).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {**readiness_payload, "records": len(projection), "ineligible_records": sum(x["knowledge_eligibility"] == "INELIGIBLE" for x in projection), "output": str(output)}


class KnowledgeReadinessService:
    """Validates whether approved V3 documentation is safe for later knowledge use."""

    def __init__(self, workspace: str | Path = ".") -> None:
        """Stores the workspace boundary; validation remains side-effect free outside R9 output."""
        self._workspace = Path(workspace)

    def validate(self) -> JsonObject:
        """Runs all readiness checks and returns the final machine-readable status."""
        return _execute(self._workspace)


def run(workspace: str | Path = ".") -> JsonObject:
    """Compatibility entry point retained for existing tests and documented workflows."""
    return KnowledgeReadinessService(workspace).validate()


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True, indent=2))
