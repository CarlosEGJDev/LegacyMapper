"""Provider-neutral deterministic Markdown renderer."""
FUNCTIONAL_SECTIONS=["Metadata","Alcance del levantamiento","Resumen funcional del aplicativo","Módulos o áreas funcionales identificadas","Funcionalidades por módulo/área","Pantallas, WebForms o puntos de entrada relevantes","Flujos funcionales identificados","Integraciones funcionales detectadas","Operaciones de datos relacionadas con funcionalidades","Dependencias funcionales relevantes","Información no determinada","Solicitudes de información adicional","Cobertura del levantamiento","Trazabilidad","Estado de revisión"]
TECHNICAL_SECTIONS=["Metadata","Alcance técnico","Resumen tecnológico","Organización de soluciones y proyectos","Componentes técnicos identificados","Dependencias entre componentes","WebForms y capa de presentación","Lógica de aplicación / negocio","Acceso a datos","Oracle / procedimientos almacenados / SQL","Flujos técnicos representativos","Dependencias entre proyectos","Dependencias externas y ensamblados","Patrón de diseño / arquitectura","Evidencia a favor del patrón","Evidencia contradictoria o ambigua","Riesgos técnicos observables","Información técnica no determinada","Solicitudes de información adicional","Cobertura técnica","Trazabilidad","Estado de revisión"]

def render(document,kind,model_id):
 """Performs render while preserving this module's deterministic contract."""
 sections=FUNCTIONAL_SECTIONS if kind=="functional" else TECHNICAL_SECTIONS; title="LEVANTAMIENTO FUNCIONAL" if kind=="functional" else "LEVANTAMIENTO TÉCNICO"
 grouped={s:[] for s in sections}; fallback="Resumen funcional del aplicativo" if kind=="functional" else "Resumen tecnológico"
 for claim in document["claims"]: grouped.get(claim.get("section"),grouped[fallback]).append(claim)
 lines=[f"# {title}",""]
 for section in sections:
  lines += [f"## {section}",""]
  if section=="Metadata": lines += ["```text","document_status=DRAFT","human_review_required=true","approved=false","knowledge_source_eligible=false",f"provider=COPILOT",f"model_id={model_id}",f"source_snapshots={','.join(document['source_snapshots'])}","```",""]
  elif section=="Solicitudes de información adicional":
   if not document["missing_information"]: lines += ["- No se registraron solicitudes estructuradas.",""]
   for m in document["missing_information"]: lines += [f"- `{m['request_id']}` [{m.get('blocking_level','INFORMATIONAL')}] ({m.get('family','UNCLASSIFIED')}): {m.get('question') or m.get('description','No determinada')}",f"  - Motivo: {m.get('reason','Evidencia insuficiente')}",f"  - Solicitudes originales: {', '.join(m.get('source_request_ids',[])) or 'N/A'}",f"  - Claims: {', '.join(m['related_claim_ids']) or 'N/A'}; evidencias: {', '.join(m['related_evidence_ids']) or 'N/A'}",f"  - Paquetes: {', '.join(m.get('context_package_ids',[])) or 'N/A'}; snapshots: {', '.join(m.get('source_snapshots',[])) or 'N/A'}",""]
  elif section=="Trazabilidad":
   for c in document["claims"]: lines += [f"- `{c['claim_id']}` | {c.get('status')} | claims locales: {', '.join(c.get('local_claim_ids',[])) or 'N/A'} | evidencias: {', '.join(c['evidence_refs'])} | paquetes: {', '.join(c['context_package_ids'])}"]
   lines.append("")
  elif section in ("Cobertura del levantamiento","Cobertura técnica"):
   metrics=document.get("coverage_metrics",{}); lines += ["```json",__import__('json').dumps(metrics,ensure_ascii=False,sort_keys=True,indent=2),"```","","- STRUCTURAL_COVERAGE describe inclusión/clasificación determinista; INTERPRETATION_COVERAGE no implica cobertura semántica total.",""]
  elif section=="Estado de revisión": lines += ["```text","STATUS=DRAFT","HUMAN_REVIEW_REQUIRED=true","APPROVED=false","AI_KNOWLEDGE_ALLOWED=false","```",""]
  elif grouped[section]:
   for c in sorted(grouped[section],key=lambda x:x["claim_id"]):
    lines += [f"- [{c['status']}] {c.get('statement','')} (`{c['claim_id']}`; evidencia: {', '.join(c['evidence_refs'])})"]
    if c.get("metric_facts"):
     for f in c["metric_facts"]: lines += [f"  - Métrica: {f['metric_name']}={f['value']}; alcance={f['scope']}; población={f['population']}; agregación={f['aggregation']}; fuente={', '.join(f['source_refs'])}; snapshot={f['source_snapshot']}"]
   lines.append("")
  else: lines += ["- [UNRESOLVED] No determinado con la evidencia validada disponible.",""]
 return "\n".join(lines).rstrip()+"\n"
