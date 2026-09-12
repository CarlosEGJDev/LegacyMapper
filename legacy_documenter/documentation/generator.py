"""Explicit V3-R7 generator. Reads existing V2 artifacts; never scans legacy source."""
import asyncio,hashlib,json
from pathlib import Path
from legacy_documenter.context.resolver import ContextResolver
from legacy_documenter.context.composer import ContextComposer
from legacy_documenter.documentation.aggregation import aggregate,evidence_closed
from legacy_documenter.documentation.interpretation import DocumentationPrompt,FUNCTIONAL_PROFILE,TECHNICAL_PROFILE,AssessmentValidator,canonical_assessment_schema,ASSESSMENT_FIELDS,CLAIM_FIELDS,MISSING_INFORMATION_FIELDS,ASSESSMENT_STATUSES,FACT_STATUSES,MODEL_SOURCE_TYPES,BLOCKING_LEVELS
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider
from legacy_documenter.llm.copilot_pilot import discover_model

SECTIONS={"functional":["Resumen funcional del aplicativo","Módulos o áreas funcionales identificadas","Funcionalidades por módulo/área","Pantallas, WebForms o puntos de entrada relevantes","Flujos funcionales identificados","Integraciones funcionales detectadas","Operaciones de datos relacionadas con funcionalidades","Dependencias funcionales relevantes","Información no determinada"],"technical":["Resumen tecnológico","Organización de soluciones y proyectos","Componentes técnicos identificados","Dependencias entre componentes","WebForms y capa de presentación","Lógica de aplicación / negocio","Acceso a datos","Oracle / procedimientos almacenados / SQL","Flujos técnicos representativos","Dependencias entre proyectos","Dependencias externas y ensamblados","Patrón de diseño / arquitectura","Evidencia a favor del patrón","Evidencia contradictoria o ambigua","Riesgos técnicos observables","Información técnica no determinada"]}

def _id(body): return "CTX-R7-"+hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def build_package(root,kind):
 """Performs build package while preserving this module's deterministic contract."""
 resolver=ContextResolver(root); base=ContextComposer(resolver).compose("FUNCTIONAL" if kind=="functional" else "TECHNICAL",profile="SMALL",budget={"max_records":40,"max_flows":4,"max_paths":8,"max_evidence_refs":16,"max_unresolved":6,"max_estimated_tokens":6500})
 system=resolver.system; flows=resolver.flows; records=[]
 def add(ref,category,fact): records.append({"ref":str(ref),"category":category,"fact":fact,"source_type":"DETERMINISTIC_CODE_FACT"})
 add("SYS-REPOSITORY","SYSTEM",system.get("repository",{})); add("SYS-DATA-ACCESS","DATA_ACCESS",system.get("data_access",{})); add("SYS-CALLS","CALL_RELATIONSHIP",system.get("calls",{}))
 for i,p in enumerate(system.get("projects",[])[:6]):
  project_refs=p.get("project_references") or []; assembly_refs=p.get("assembly_references") or []
  add("PROJECT-%03d"%i,"PROJECT",{k:p.get(k) for k in ("path","name","root_namespace","assembly_name","target_framework")}|{"project_reference_count":len(project_refs),"project_references":[x.get("include") or x.get("name") for x in project_refs[:8]],"assembly_reference_count":len(assembly_refs),"assembly_references":[x.get("include") or x.get("name") for x in assembly_refs[:8]]})
 for i,w in enumerate(system.get("web",{}).get("webforms",[])[:6]):
  add("WEBFORM-%03d"%i,"WEBFORM",{k:w.get(k) for k in ("id","path","type","inherits","codebehind","entry_point_ids")}|{"register_count":len(w.get("registers") or [])})
 selected=set(base.get("records",[]) and [x["ref"] for x in base["records"] if x.get("category")=="flow_refs"] or [])
 chosen=[f for f in flows.get("flows",[]) if not selected or f.get("flow_id") in selected][:4]
 path_ids={p for f in chosen for p in f.get("path_ids",[])[:2]}
 for f in chosen: add(f["flow_id"],"FLOW",{k:f.get(k) for k in ("flow_id","entry_point","projects","terminal_operations","stored_procedures","sql_operations","unresolved_boundaries","confidence","status","path_ids")})
 for p in flows.get("paths",[]):
  if p.get("path_id") in path_ids: add(p["path_id"],"METHOD_CALL_DATA_PATH",{k:p.get(k) for k in ("path_id","terminal_type","terminal_target","confidence","depth","project_sequence")}|{"nodes":(p.get("nodes") or [])[:15],"relation_types":(p.get("relation_types") or [])[:15],"evidence_refs":(p.get("evidence_refs") or [])[:15]})
 records=records[:40]
 body={"package_type":"FUNCTIONAL" if kind=="functional" else "TECHNICAL","schema_version":"3.1.0","source_snapshot":base["source_snapshot"],"scope":{"document":kind,"bounded":True},"records":records,"unresolved_refs":sorted({r["ref"] for r in records if "unresolved" in json.dumps(r["fact"]).lower()}),"statistics":{"estimated_tokens":sum(len(json.dumps(r,ensure_ascii=False)) for r in records)//4,"records_included":len(records),"completeness":"PARTIAL"},"provenance":{"artifacts":["ai_context/SYSTEM_CONTEXT.json","ai_context/FUNCTIONAL_FLOWS.json","ai_context/TRACEABILITY.json"],"resolver_package_id":base["package_id"],"repository_scan":False}}
 body["package_id"]=_id(body); return body

def _request(profile,package,kind):
 r=DocumentationPrompt(profile,[package]).to_request(); r.max_output_tokens=3500
 evidence=sorted(str(x["ref"]) for x in package["records"])
 exemplar={"assessment_id":"SYN-ASSESSMENT","profile_id":"SYN-PROFILE","context_package_ids":["SYN-PACKAGE"],"source_snapshots":["SYN-SNAPSHOT"],"status":"PARTIAL","summary":"Synthetic shape exemplar only.","claims":[{"claim_id":"SYN-C1","statement":"Synthetic deterministic fact.","status":"CONFIRMED","source_type":"DETERMINISTIC_CODE_FACT","evidence_refs":["SYN-E1"],"context_package_ids":["SYN-PACKAGE"],"section":"SYN-SECTION"},{"claim_id":"SYN-C2","statement":"Synthetic grounded interpretation.","status":"INTERPRETED","source_type":"AI_INTERPRETATION","evidence_refs":["SYN-E1"],"context_package_ids":["SYN-PACKAGE"],"section":"SYN-SECTION"},{"claim_id":"SYN-C3","statement":"Synthetic unresolved item.","status":"UNRESOLVED","source_type":"UNRESOLVED","evidence_refs":["SYN-E1"],"context_package_ids":["SYN-PACKAGE"],"section":"SYN-SECTION"}],"missing_information":[{"request_id":"SYN-R1","document":"SYN-PROFILE","section":"SYN-SECTION","question":"Synthetic question?","reason":"Synthetic missing evidence.","blocking_level":"INFORMATIONAL","related_claim_ids":["SYN-C3"],"related_evidence_ids":["SYN-E1"]}]}
 r.user_instruction += "\nCANONICAL ENFORCEMENT:\nRETURN profile_id EXACTLY as supplied: "+profile.profile_id+". DO NOT rename, translate, or infer another profile. Copy context_package_ids EXACTLY as: "+json.dumps([package["package_id"]])+". Copy source_snapshots EXACTLY as: "+json.dumps([package["source_snapshot"]])+". Allowed assessment statuses EXACTLY: "+json.dumps(sorted(ASSESSMENT_STATUSES))+". Allowed claim statuses EXACTLY: "+json.dumps(sorted(FACT_STATUSES))+". Allowed source types EXACTLY: "+json.dumps(sorted(MODEL_SOURCE_TYPES))+". CONFIRMED requires cited deterministic evidence and source_type DETERMINISTIC_CODE_FACT. AI_INTERPRETATION MUST use INTERPRETED, never CONFIRMED. UNRESOLVED source MUST use UNRESOLVED, never CONFIRMED. If uncertain prefer INTERPRETED or UNRESOLVED. Claim required fields EXACTLY: "+json.dumps(list(CLAIM_FIELDS))+". MissingInformation required fields EXACTLY: "+json.dumps(list(MISSING_INFORMATION_FIELDS))+". Allowed blocking levels EXACTLY: "+json.dumps(sorted(BLOCKING_LEVELS))+". USE ONLY these evidence IDs exactly, without invention or modification: "+json.dumps(evidence)+". Return missing_information as [] when none. Return one JSON object only; no Markdown, prose, comments, prefix, suffix, or chain-of-thought. Allowed sections: "+json.dumps(SECTIONS[kind],ensure_ascii=False)+". Do not force an architecture pattern; use an UNRESOLVED claim stating NO_PATTERN_CONFIRMED or INSUFFICIENT_EVIDENCE when applicable. The following is a shape-only synthetic exemplar, not legacy evidence: "+json.dumps(exemplar,ensure_ascii=False,sort_keys=True)
 return r
def _schema(profile,package,kind): return canonical_assessment_schema(profile,package,SECTIONS[kind])
def prevalidate_request(request,schema,profile,package):
 """Performs prevalidate request while preserving this module's deterministic contract."""
 text=request.user_instruction+json.dumps(schema,sort_keys=True,ensure_ascii=False); errors=[]; evidence=sorted(str(r["ref"]) for r in package["records"])
 if schema["properties"]["profile_id"].get("const")!=profile.profile_id or profile.profile_id not in text: errors.append("profile")
 if schema["properties"]["context_package_ids"].get("const")!=[package["package_id"]]: errors.append("package")
 if schema["properties"]["source_snapshots"].get("const")!=[package["source_snapshot"]]: errors.append("snapshot")
 if sorted(schema["properties"]["claims"]["items"]["properties"]["evidence_refs"]["items"]["enum"])!=evidence: errors.append("evidence")
 if set(schema["properties"]["claims"]["items"]["required"])!=set(CLAIM_FIELDS): errors.append("claim schema")
 if set(schema["properties"]["missing_information"]["items"]["required"])!=set(MISSING_INFORMATION_FIELDS): errors.append("missing schema")
 if any(x in schema["properties"]["claims"]["items"]["properties"]["source_type"]["enum"] for x in ("APPROVED_FUNCTIONAL_DOCUMENT","APPROVED_TECHNICAL_DOCUMENT","APPROVED_EXTERNAL_INFORMATION")): errors.append("approved source")
 if "one JSON object only" not in request.user_instruction or "never CONFIRMED" not in request.user_instruction: errors.append("instruction")
 return sorted(errors)
def _strict(result,profile,package):
 basic=AssessmentValidator().validate(result,profile,[package]); errors=list(basic["errors"]); known={r["ref"] for r in package["records"]}; allowed={"DETERMINISTIC_CODE_FACT","AI_INTERPRETATION","UNRESOLVED"}
 for c in result.get("claims",[]):
  if not all(k in c for k in ("claim_id","statement","status","source_type","evidence_refs","section")): errors.append("claim schema")
  if c.get("source_type") not in allowed: errors.append("source type")
  if not c.get("evidence_refs") or set(c.get("evidence_refs",[]))-known: errors.append("evidence closure")
  if c.get("status")=="CONFIRMED" and c.get("source_type")!="DETERMINISTIC_CODE_FACT": errors.append("status promotion")
  if c.get("status") not in FACT_STATUSES: errors.append("claim status")
  if set(c)-set(CLAIM_FIELDS): errors.append("claim aliases")
 for m in result.get("missing_information",[]):
  if not all(k in m for k in ("request_id","document","section","question","reason","blocking_level","related_claim_ids","related_evidence_ids")): errors.append("missing schema")
  if set(m.get("related_evidence_ids",[]))-known: errors.append("missing evidence closure")
  if m.get("blocking_level") not in BLOCKING_LEVELS: errors.append("blocking level")
  if set(m)-set(MISSING_INFORMATION_FIELDS): errors.append("missing aliases")
 if result.get("status") not in ASSESSMENT_STATUSES: errors.append("assessment status")
 if result.get("context_package_ids")!=[package["package_id"]]: errors.append("package exact")
 if result.get("source_snapshots")!=[package["source_snapshot"]]: errors.append("snapshot exact")
 return sorted(set(errors))
def run(workspace="."):
 """Performs run while preserving this module's deterministic contract."""
 workspace=Path(workspace); source=workspace/"output"/"v2_r5_1_full"
 for name in ("SYSTEM_CONTEXT.json","FUNCTIONAL_FLOWS.json","TRACEABILITY.json"):
  if not (source/"ai_context"/name).exists(): return {"status":"V3-R7_BLOCKED_MISSING_V2_EVIDENCE","calls":0}
 try: model=asyncio.run(discover_model())
 except Exception: return {"status":"V3-R7_BLOCKED_PROVIDER","calls":0}
 provider=CopilotProvider(ProviderConfig("COPILOT","copilot-local",model,max_output_tokens=3500,options={"timeout":120})); accepted=[]; packages=[]; summaries=[]
 for kind,profile in (("functional",FUNCTIONAL_PROFILE),("technical",TECHNICAL_PROFILE)):
  package=build_package(source,kind); packages.append(package)
  request=_request(profile,package,kind); schema=_schema(profile,package,kind); preerrors=prevalidate_request(request,schema,profile,package)
  if preerrors: return {"status":"V3-R7_1_REQUEST_CONTRACT_FAILURE","calls":0,"errors":preerrors}
  response=provider.structured_generate(request,schema)
  errors=[] if response.parsed_output else list(response.validation_errors); errors += _strict(response.parsed_output,profile,package) if response.parsed_output else []
  if errors: summaries.append({"kind":kind,"valid":False,"errors":errors,"model_id":response.model_id}); continue
  accepted.append(response.parsed_output); summaries.append({"kind":kind,"valid":True,"claims":len(response.parsed_output.get("claims",[])),"missing":len(response.parsed_output.get("missing_information",[])),"model_id":response.model_id})
 if len(accepted)!=2: return {"status":"V3-R7_1_MODEL_CONTRACT_FAILURE","calls":2,"assessments":summaries}
 out=workspace/"output"; docs={}
 for i,(kind,_) in enumerate((("functional",FUNCTIONAL_PROFILE),("technical",TECHNICAL_PROFILE))):
  document=aggregate([accepted[i]],[packages[i]])
  if not evidence_closed(document): return {"status":"V3-R7_TRACEABILITY_FAILURE","calls":2}
  text=render(document,kind,summaries[i]["model_id"]); path=out/("LEVANTAMIENTO_FUNCIONAL.md" if kind=="functional" else "LEVANTAMIENTO_TECNICO.md"); path.write_text(text,encoding="utf-8"); docs[kind]={"path":str(path),"bytes":len(text.encode()),"claims":len(document["claims"]),"missing":len(document["missing_information"]),"closed":True}
 return {"status":"V3-R7_1_READY_FOR_HUMAN_REVIEW","calls":2,"model_id":summaries[0]["model_id"],"packages":[{"id":p["package_id"],"records":len(p["records"]),"tokens":p["statistics"]["estimated_tokens"]} for p in packages],"assessments":summaries,"documents":docs}
if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2,sort_keys=True))
