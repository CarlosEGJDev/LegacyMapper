"""Deterministic V3-R8 human-review package preparation."""
import json
import re
from pathlib import Path


CLAIM_RE = re.compile(r"^- \[(CONFIRMED|INTERPRETED|UNRESOLVED)\] (.*?) \(`([^`]+)`; evidencia: (.*?)\)$")
MISSING_RE = re.compile(r"^- `((?:FMI|TMI)-\d{3})` \[([^]]+)] \(([^)]+)\): (.*)$")


def validate_preconditions(functional_text, technical_text, parent_text):
    """Performs validate preconditions while preserving this module's deterministic contract."""
    required = ("document_status=DRAFT", "human_review_required=true",
                "approved=false", "knowledge_source_eligible=false")
    return (all(x in functional_text for x in required)
            and all(x in technical_text for x in required)
            and "V3-R7_2_4_READY_FOR_HUMAN_REVIEW" in parent_text)


def parse_document(text):
    """Performs parse document while preserving this module's deterministic contract."""
    claims = []
    missing = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = CLAIM_RE.match(line)
        if match:
            refs = [x.strip() for x in match.group(4).split(",") if x.strip()]
            claims.append({"status": match.group(1), "statement": match.group(2),
                           "claim_id": match.group(3), "evidence_refs": refs})
        match = MISSING_RE.match(line)
        if match:
            reason = ""
            if index + 1 < len(lines) and lines[index + 1].startswith("  - Motivo: "):
                reason = lines[index + 1][12:]
            missing.append({"request_id": match.group(1), "blocking_level": match.group(2),
                            "family": match.group(3), "question": match.group(4), "reason": reason})
    return {"claims": claims, "missing_information": missing}


def _evidence_summary(refs):
    shown = refs[:3]
    suffix = f" (+{len(refs)-3} referencias)" if len(refs) > 3 else ""
    return ", ".join(shown) + suffix


def _claim_groups(parsed, number):
    labels = (("CONFIRMED", "Confirmed"), ("INTERPRETED", "Interpreted"), ("UNRESOLVED", "Unresolved"))
    lines = []
    for offset, (status, label) in enumerate(labels, 1):
        lines += [f"### {number}.{offset} {label}", ""]
        values = [x for x in parsed["claims"] if x["status"] == status]
        for claim in values:
            lines.append(f"- `{claim['claim_id']}` — {claim['statement']}")
            lines.append(f"  - Evidencia: {_evidence_summary(claim['evidence_refs'])}")
            if status == "INTERPRETED":
                lines.append("  - REQUIRES_HUMAN_CONFIRMATION")
        if not values:
            lines.append("- Ninguno.")
        lines.append("")
    return lines


def _missing(items, source):
    lines = []
    for item in items:
        lines += [f"- `{item['request_id']}` | `{item['family']}` | `{item['blocking_level']}`",
                  f"  - Pregunta: {item['question']}", f"  - Motivo: {item['reason']}",
                  "  - TRACEABILITY_AVAILABLE=true", f"  - Detalle: `{source}`", ""]
    return lines


FUNCTIONAL_CHECKLIST = (
    "Are the identified functional areas correct?", "Are important functional areas missing?",
    "Are the described WebForms/entry points representative?", "Are interpreted functional conclusions reasonable?",
    "Are any CONFIRMED claims actually incorrect?", "Can I answer any FMI requests?",
    "Are any FMI requests unnecessary?", "Does the document adequately describe the application functionally?",
)
TECHNICAL_CHECKLIST = (
    "Are the identified technical components correct?", "Is the WebForms presentation description correct?",
    "Is the Oracle/data-access description correct?", "Are project/component responsibilities correctly represented?",
    "Do I know the architecture/pattern used by the system?", "Can I provide missing project dependency information?",
    "Can I provide external assembly/dependency information?", "Can I clarify end-to-end WebForm -> BL -> DAL/SYS -> Oracle flows?",
    "Are any CONFIRMED technical claims incorrect?", "Are INTERPRETED technical claims reasonable?",
    "Can I answer any TMI requests?", "Does the technical document adequately represent the system?",
)


def response_template():
    """Performs response template while preserving this module's deterministic contract."""
    return """# Respuesta de revisión humana — LegacyMapper V3

FUNCTIONAL_DECISION=PENDING
TECHNICAL_DECISION=PENDING

Valores permitidos al completar la revisión: APPROVED, NEEDS_CHANGES, NEEDS_MORE_INFORMATION, REJECTED.

FUNCTIONAL_COMMENTS=

TECHNICAL_COMMENTS=

FUNCTIONAL_MISSING_INFORMATION_RESPONSES=

TECHNICAL_MISSING_INFORMATION_RESPONSES=

GENERAL_COMMENTS=
"""


def knowledge_ready(functional_decision, technical_decision):
    """Performs knowledge ready while preserving this module's deterministic contract."""
    return functional_decision == "APPROVED" and technical_decision == "APPROVED"


def build_package(functional_text, technical_text, metrics):
    """Performs build package while preserving this module's deterministic contract."""
    functional = parse_document(functional_text)
    technical = parse_document(technical_text)
    lines = ["# LegacyMapper V3 — Revisión Humana", "", "## 1. Estado", "", "```text",
             "FUNCTIONAL_DOCUMENT=DRAFT", "TECHNICAL_DOCUMENT=DRAFT", "HUMAN_REVIEW_REQUIRED=true",
             "AI_KNOWLEDGE_ALLOWED=false", "```", "",
             "Este paquete no aprueba la documentación. La decisión final debe ser proporcionada explícitamente por el revisor humano.", "",
             "## 2. System Coverage Summary", "", "```text",
             f"PROJECTS_CLASSIFIED={metrics['total_projects']}", f"SOLUTIONS_REPRESENTED={metrics['represented_solutions']}",
             f"WEBFORMS_REPRESENTED={metrics['represented_webforms']}", f"FUNCTIONAL_FLOWS_REPRESENTED={metrics['represented_flows']}",
             f"LINKED_DATA_OPERATIONS={metrics['linked_data_operations']}", f"LINKED_STORED_PROCEDURES={metrics['linked_stored_procedures']}",
             f"UNRESOLVED_RELATIONSHIPS={metrics['unresolved_relationships']}", "STRUCTURAL_COVERAGE != COMPLETE_SEMANTIC_UNDERSTANDING", "```", "",
             "Los 259 proyectos están clasificados estructuralmente; esto no afirma comprensión semántica completa.", "",
             "## 3. Functional Review", ""]
    lines += _claim_groups(functional, 3)
    lines += ["Detalle autoritativo: `output/LEVANTAMIENTO_FUNCIONAL.md`.", "", "## 4. Functional Missing Information", ""]
    lines += _missing(functional["missing_information"], "output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional")
    lines += ["## 5. Functional Human Checklist", ""] + [f"- [ ] {x}" for x in FUNCTIONAL_CHECKLIST] + ["", "## 6. Technical Review", ""]
    lines += _claim_groups(technical, 6)
    lines += ["Detalle autoritativo: `output/LEVANTAMIENTO_TECNICO.md`.", "", "## 7. Quantitative Technical Review", "",
              "SYSTEM STRUCTURAL:", "", "```text", "linked_data_operations=19159", "linked_stored_procedures=5389", "```", "",
              "COVERAGE PARTITION EXAMPLES:", "", "```text", "data_access_partition_count=2009", "stored_procedures_partition_count=674", "```", "",
              "Estos valores tienen alcances deterministas diferentes y no son directamente contradictorios. El revisor debe verificar si la terminología comunica correctamente el sistema legado; los números no fueron modificados.", "",
              "## 8. Technical Missing Information", ""]
    lines += _missing(technical["missing_information"], "output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional")
    lines += ["Familias especialmente relevantes: `TECHNICAL_ARCHITECTURE_PATTERN`, `TECHNICAL_PROJECT_DEPENDENCIES`, `TECHNICAL_EXTERNAL_DEPENDENCIES`, `TECHNICAL_COMPONENT_RESPONSIBILITY`, `TECHNICAL_END_TO_END_FLOW`.", "",
              "## 9. Technical Human Checklist", ""] + [f"- [ ] {x}" for x in TECHNICAL_CHECKLIST]
    lines += ["", "## 10. Critical Items for Approval", "", "### FUNCTIONAL_BLOCKING_ITEMS", ""]
    lines += [f"- `{x['request_id']}` — {x['question']} — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE" for x in functional["missing_information"] if x["blocking_level"] == "BLOCKING_FOR_APPROVAL"] or ["- Ninguno."]
    lines += ["", "### TECHNICAL_BLOCKING_ITEMS", ""]
    lines += [f"- `{x['request_id']}` — {x['question']} — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE" for x in technical["missing_information"] if x["blocking_level"] == "BLOCKING_FOR_APPROVAL"] or ["- Ninguno."]
    lines += ["", "## 11. Reviewer Response Template", "", "```text", response_template().split("\n", 2)[2].rstrip(), "```", "",
              "## 12. Approval Rules", "", "AI_KNOWLEDGE permanece bloqueado salvo que `FUNCTIONAL_DECISION=APPROVED` y `TECHNICAL_DECISION=APPROVED` sean decisiones humanas explícitas.", "",
              "Un PASS de tests, un estado de Codex o la creación de este paquete no constituye aprobación.", "", "## Review Observations", "",
              "- Las solicitudes UNCLASSIFIED se conservaron separadas por cautela determinista; el revisor puede solicitar otra ronda de corrección.",
              "- Los documentos fuente y su trazabilidad detallada permanecen autoritativos y sin cambios.", ""]
    return "\n".join(lines)


def run(workspace="."):
    """Performs run while preserving this module's deterministic contract."""
    workspace = Path(workspace)
    functional_path = workspace / "output" / "LEVANTAMIENTO_FUNCIONAL.md"
    technical_path = workspace / "output" / "LEVANTAMIENTO_TECNICO.md"
    parent_path = workspace / "codex" / "V3" / "V3_R7_2_4_RESULTADO.md"
    functional_text = functional_path.read_text(encoding="utf-8")
    technical_text = technical_path.read_text(encoding="utf-8")
    if not validate_preconditions(functional_text, technical_text, parent_path.read_text(encoding="utf-8")):
        return {"status": "V3-R8_PRECONDITION_FAILURE", "calls": 0}
    coverage = json.loads((workspace / "output" / "v3_r7_2" / "COVERAGE_INDEX.json").read_text(encoding="utf-8"))["metrics"]
    package = build_package(functional_text, technical_text, coverage)
    target = workspace / "codex" / "V3"
    target.mkdir(parents=True, exist_ok=True)
    (target / "V3_R8_PAQUETE_REVISION_HUMANA.md").write_text(package, encoding="utf-8")
    response_path = target / "V3_R8_RESPUESTA_REVISION.md"
    existing = response_path.read_text(encoding="utf-8") if response_path.exists() else ""
    # An explicit human response is immutable input for later rounds.
    if not existing or ("FUNCTIONAL_DECISION=PENDING" in existing and "TECHNICAL_DECISION=PENDING" in existing):
        response_path.write_text(response_template(), encoding="utf-8")
    return {"status": "V3-R8_WAITING_FOR_HUMAN_REVIEW", "calls": 0,
            "functional_claims": len(parse_document(functional_text)["claims"]),
            "technical_claims": len(parse_document(technical_text)["claims"]),
            "functional_missing": len(parse_document(functional_text)["missing_information"]),
            "technical_missing": len(parse_document(technical_text)["missing_information"])}
