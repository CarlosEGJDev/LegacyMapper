"""Deterministic V3-R8.4 second-human-review package generation."""
import json
from pathlib import Path
from legacy_documenter.documentation.human_review import parse_document

ITEM_DECISIONS={"HUMAN_CONFIRMED","ACCEPTED_AS_PARTIAL","ACCEPTED_AS_UNRESOLVED_EXTERNAL","NEEDS_MORE_ANALYSIS","REJECTED"}
DOCUMENT_DECISIONS={"APPROVED","NEEDS_CHANGES","REJECTED"}
RESOLVED={"FMI-008","TMI-002","TMI-005"}
EXTERNAL={"FMI-007","TMI-001","TMI-011"}
PARTIAL={"FMI-001","FMI-002","FMI-003","FMI-004","FMI-005","FMI-006","TMI-003","TMI-004","TMI-006","TMI-007","TMI-008","TMI-009","TMI-010","TMI-012"}

def validate_item_decision(value): return value in ITEM_DECISIONS
def document_can_be_approved(item_decisions): return all(x in {"HUMAN_CONFIRMED","ACCEPTED_AS_PARTIAL","ACCEPTED_AS_UNRESOLVED_EXTERNAL"} for x in item_decisions)
def recommendation(target):
 """Performs recommendation while preserving this module's deterministic contract."""
 if target in RESOLVED:return "HUMAN_CONFIRMED"
 if target in PARTIAL:return "ACCEPTED_AS_PARTIAL"
 return "ACCEPTED_AS_UNRESOLVED_EXTERNAL"

def build_items(workspace):
 """Performs build items while preserving this module's deterministic contract."""
 workspace=Path(workspace); f=parse_document((workspace/"output/LEVANTAMIENTO_FUNCIONAL.md").read_text(encoding="utf-8")); t=parse_document((workspace/"output/LEVANTAMIENTO_TECNICO.md").read_text(encoding="utf-8")); canonical={x["request_id"]:x for x in f["missing_information"]+t["missing_information"]}
 r82=json.loads((workspace/"output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json").read_text(encoding="utf-8"))["items"]; r83={x["target_id"]:x for x in json.loads((workspace/"output/v3_r8_3/TARGET_REEVALUATION.json").read_text(encoding="utf-8"))["targets"]}; interpretations={x["target_id"]:x for x in json.loads((workspace/"output/v3_r8_2/INTERPRETATION_RESULTS.json").read_text(encoding="utf-8"))["interpretations"]}
 items=[]
 for value in r82:
  target=value["target_missing_information_id"]; original=canonical[target]; deep=r83.get(target); interpreted=interpretations.get(target,{}); status=deep["candidate_status"] if deep else value["candidate_status"]; evidence=(deep.get("existing_evidence_used",[])+deep.get("new_deterministic_evidence",[])) if deep else value.get("interpretation_evidence_ids",[])
  remaining=deep.get("remaining_unknowns",[]) if deep else interpreted.get("unresolved_aspects",[]) or ["La porción no resuelta permanece explícita en la evidencia canónica."]
  summary=interpreted.get("semantic_summary") or ("La evidencia determinista resolvió el inventario solicitado." if status=="RESOLVED_BY_DETERMINISTIC_EVIDENCE" else "La evidencia determinista aporta cobertura parcial y conserva incertidumbre.")
  items.append({"id":target,"profile":"functional" if target.startswith("FMI") else "technical","original_question":original["question"],"candidate_status":status,"summary":summary,"evidence_basis":sorted(set(evidence))[:5],"evidence_total":len(set(evidence)),"remaining_uncertainty":remaining,"recommended_human_disposition":recommendation(target),"human_decision":"PENDING","traceability_source":"output/v3_r8_3/TARGET_REEVALUATION.json" if deep else "output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json"})
 return sorted(items,key=lambda x:x["id"])

def build_package(items):
 """Performs build package while preserving this module's deterministic contract."""
 lines=["# LegacyMapper V3 — Segunda Revisión Humana","","## Estado","","```text","C04=HUMAN_CONFIRMED","FUNCTIONAL_DOCUMENT_DECISION=PENDING","TECHNICAL_DOCUMENT_DECISION=PENDING","AI_KNOWLEDGE_ALLOWED=false","```","","Las recomendaciones son informativas y no son decisiones humanas. Todos los ítems comienzan en `PENDING`.","","## Resumen","",f"- Candidatos resueltos: {len(RESOLVED)}.",f"- Candidatos parciales: {len(PARTIAL)}.",f"- Evidencia agotada / información externa: {len(EXTERNAL)}.","","## Revisión de los 20 ítems",""]
 for x in items:
  lines += [f"### {x['id']}","",f"- Pregunta original: {x['original_question']}",f"- Estado candidato: `{x['candidate_status']}`",f"- Resumen: {x['summary']}",f"- Evidencia representativa ({min(5,x['evidence_total'])} de {x['evidence_total']}): {', '.join(x['evidence_basis']) or 'Sin referencia adicional'}",f"- Incertidumbre restante: {'; '.join(x['remaining_uncertainty'])}",f"- Recomendación informativa: `{x['recommended_human_disposition']}`",f"- Decisión humana: `PENDING`",f"- Trazabilidad: `{x['traceability_source']}`",""]
 lines += ["## Representación arquitectónica","","- La evidencia de presentación orientada a ASP.NET WebForms está soportada.","- Existe evidencia `.aspx`/`.ascx`, code-behind e `Inherits`.","- MVC no está establecido.","- La ausencia de referencias a `System.Web.Mvc` no prueba que MVC nunca existiera ni que no coexistan componentes MVC.","- No se encontró declaración formal autoritativa de arquitectura ni especificación autoritativa de límites de capas.","- Pueden coexistir otros patrones; no debe forzarse una etiqueta arquitectónica.","","## Información externa",""]
 for x in items:
  if x["id"] in EXTERNAL: lines += [f"- `{x['id']}`: {x['original_question']}",f"  - Establecido: {x['summary']}",f"  - Desconocido: {'; '.join(x['remaining_uncertainty'])}","  - Agotamiento: evidencia canónica y búsqueda dirigida aplicable completadas.","  - Para resolver: información externa autoritativa sobre propósito funcional o arquitectura/límites formales, según el ítem."]
 lines += ["","## Regla de aprobación","","Un documento puede aprobarse con ítems `ACCEPTED_AS_PARTIAL` o `ACCEPTED_AS_UNRESOLVED_EXTERNAL` si la incertidumbre es explícita, no se promueven claims sin soporte, los bloqueantes reciben disposición, la trazabilidad permanece válida y el humano acepta expresamente las limitaciones.","","La aprobación significa que el documento representa correctamente lo conocido y desconocido; no que todo el legado sea conocido.",""]
 return "\n".join(lines)

def response_template(items):
 """Performs response template while preserving this module's deterministic contract."""
 lines=["# Respuesta — Segunda Revisión Humana LegacyMapper V3","","FUNCTIONAL_DOCUMENT_DECISION=PENDING","TECHNICAL_DOCUMENT_DECISION=PENDING","","Valores de documento permitidos: APPROVED, NEEDS_CHANGES, REJECTED.","","Valores de ítem permitidos: HUMAN_CONFIRMED, ACCEPTED_AS_PARTIAL, ACCEPTED_AS_UNRESOLVED_EXTERNAL, NEEDS_MORE_ANALYSIS, REJECTED.",""]
 for x in items: lines += [f"[{x['id']}]",f"ID={x['id']}","DECISION=PENDING","COMMENT=",""]
 return "\n".join(lines)

def run(workspace="."):
 """Performs run while preserving this module's deterministic contract."""
 workspace=Path(workspace); items=build_items(workspace); target=workspace/"codex/V3"; target.mkdir(parents=True,exist_ok=True); package=build_package(items); response=response_template(items); (target/"V3_R8_4_PAQUETE_SEGUNDA_REVISION_HUMANA.md").write_text(package,encoding="utf-8"); (target/"V3_R8_4_RESPUESTA_REVISION.md").write_text(response,encoding="utf-8"); return {"status":"V3-R8_4_WAITING_FOR_SECOND_HUMAN_REVIEW","review_items":len(items),"resolved":len(RESOLVED),"partial":len(PARTIAL),"external":len(EXTERNAL),"real_llm_calls":0,"ai_knowledge_allowed":False}
