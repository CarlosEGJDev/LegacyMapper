"""V3-R7.2.2 deterministic-envelope resumable execution."""
import asyncio,json
from pathlib import Path
from legacy_documenter.documentation.coverage import CoveragePlanner
from legacy_documenter.documentation.systematic import _package,_previous,_global_rules
from legacy_documenter.documentation.generator import _strict,SECTIONS
from legacy_documenter.documentation.interpretation import DocumentationPrompt,FUNCTIONAL_PROFILE,TECHNICAL_PROFILE
from legacy_documenter.documentation.envelope import semantic_schema,semantic_request,semantic_payload,compose_envelope,semantic_unchanged
from legacy_documenter.documentation.synthesis import AssessmentStore,SynthesisPlanner,request_identity,canonical_hash,expand_document
from legacy_documenter.documentation.aggregation import evidence_closed
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider
from legacy_documenter.llm.copilot_pilot import discover_model
from legacy_documenter.documentation.evidence_catalog import build_catalog,catalog_schema,catalog_request,resolve_payload,resolution_preserves_semantics,EvidenceCatalogError

def run(workspace=".",evidence_constrained=False,status_prefix="V3-R7_2_2"):
 """Performs run while preserving this module's deterministic contract."""
 workspace=Path(workspace); root=workspace/"output"/"v2_r5_1_full"; coverage=CoveragePlanner(root).plan(); batches=CoveragePlanner(root).batches(coverage,8,35); synth=SynthesisPlanner(); target=workspace/"output"/"v3_r7_2"
 stores={"local":AssessmentStore(target/"LOCAL_ASSESSMENTS.json"),"synthesis":AssessmentStore(target/"INTERMEDIATE_ASSESSMENTS.json")}; profiles={"functional":FUNCTIONAL_PROFILE,"technical":TECHNICAL_PROFILE}; packages={k:[_package(k,i,b,coverage["snapshot"],coverage["metrics"]) for i,b in enumerate(batches)] for k in profiles}
 previous={k:_previous(workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if k=="functional" else "LEVANTAMIENTO_TECNICO.md")) for k in profiles}; max_estimate=0; calls=0; reused=0; migrated=0; invalidated=0; model=None
 try: discovered=asyncio.run(discover_model())
 except Exception: return {"status":"V3-R7_2_2_BLOCKED_PROVIDER","calls":0}
 provider=CopilotProvider(ProviderConfig("COPILOT","copilot-local",discovered,max_output_tokens=3000,options={"timeout":120}))
 def prepare(kind,package,stage,max_claims):
  """Performs prepare while preserving this module's deterministic contract."""
  profile=profiles[kind]; catalog=build_catalog(package) if evidence_constrained else None
  request=(catalog_request(DocumentationPrompt(profile,[package]).to_request(),profile,package,SECTIONS[kind],catalog) if evidence_constrained else semantic_request(DocumentationPrompt(profile,[package]).to_request(),profile,package,SECTIONS[kind])); request.user_instruction += " Produce at most "+str(max_claims)+" claims."; schema=(catalog_schema(profile,catalog,SECTIONS[kind]) if evidence_constrained else semantic_schema(profile,package,SECTIONS[kind])); schema["properties"]["claims"]["maxItems"]=max_claims
  if any(x in schema.get("properties",{}) for x in ("profile_id","source_snapshots","context_package_ids")): raise ValueError("ENVELOPE_INTEGRITY")
  if package["statistics"]["estimated_tokens"]>5000: raise ValueError("BUDGET")
  return request,schema,request_identity(request,schema),catalog
 def execute(kind,package,stage,store,max_claims):
  """Performs execute while preserving this module's deterministic contract."""
  nonlocal calls,reused,migrated,invalidated,model,max_estimate
  profile=profiles[kind]; request,schema,identity,catalog=prepare(kind,package,stage,max_claims); max_estimate=max(max_estimate,package["statistics"]["estimated_tokens"]); cached=store.find(identity)
  if cached:
   if _strict(cached["assessment_payload"],profile,package): invalidated+=1
   else: reused+=1; model=cached.get("model_id") or model; return cached["assessment_payload"]
  for old in store.load():
   if old.get("context_package_id")!=package["package_id"] or old.get("profile_id")!=profile.profile_id or old.get("stage")!=stage: continue
   expected=canonical_hash({k:v for k,v in old.items() if k!="content_hash"})
   if old.get("validation_status")!="VALID" or old.get("content_hash")!=expected or _strict(old.get("assessment_payload",{}),profile,package): invalidated+=1; continue
   payload=semantic_payload(old["assessment_payload"]); composed=compose_envelope(payload,profile,package,identity["request_hash"],stage)
   if not semantic_unchanged(payload,composed) or _strict(composed,profile,package): invalidated+=1; continue
   store.persist(identity,composed,old.get("provider","COPILOT"),old.get("model_id"),stage,{"from_identity":old["identity"],"from_content_hash":old["content_hash"],"semantic_unchanged":True}); migrated+=1; reused+=1; model=old.get("model_id") or model; return composed
  if calls>=24: raise OverflowError("CALL_BUDGET")
  response=provider.structured_generate(request,schema); calls+=1
  if not response.parsed_output: raise RuntimeError("MODEL_CONTRACT:"+",".join(response.validation_errors))
  try: resolved=resolve_payload(response.parsed_output,catalog) if evidence_constrained else response.parsed_output
  except EvidenceCatalogError as exc: raise RuntimeError("EVIDENCE_KEY:"+str(exc))
  if evidence_constrained and not resolution_preserves_semantics(response.parsed_output,resolved): raise ValueError("ENVELOPE_INTEGRITY")
  composed=compose_envelope(resolved,profile,package,identity["request_hash"],stage)
  if not semantic_unchanged(resolved,composed): raise ValueError("ENVELOPE_INTEGRITY")
  errors=_strict(composed,profile,package)+([] if stage.startswith("LOCAL_") else _global_rules(composed,package))
  if errors: raise RuntimeError("MODEL_CONTRACT:"+",".join(sorted(set(errors))))
  store.persist(identity,composed,"COPILOT",response.model_id,stage); model=response.model_id; return composed
 local={k:[] for k in profiles}; all_a={k:[] for k in profiles}; all_p={k:[] for k in profiles}; intermediate={k:0 for k in profiles}; depths={}
 try:
  for kind in profiles:
   for p in packages[kind]:
    a=execute(kind,p,"LOCAL_"+kind.upper(),stores["local"],5); local[kind].append(a); all_a[kind].append(a); all_p[kind].append(p)
  globals={}; final_packages={}
  for kind in profiles:
   current_a=list(local[kind]); current_p=list(packages[kind]); depth=1
   while True:
    ps=synth.packages(kind,current_a,current_p,coverage["snapshot"],depth,coverage["metrics"])
    if len(ps)==1:
     globals[kind]=execute(kind,ps[0],"GLOBAL_"+kind.upper(),stores["synthesis"],20); final_packages[kind]=ps[0]; depths[kind]=depth; break
    next_a=[]
    for p in ps:
     a=execute(kind,p,"INTERMEDIATE_"+kind.upper()+"_L"+str(depth),stores["synthesis"],8); next_a.append(a); all_a[kind].append(a); all_p[kind].append(p); intermediate[kind]+=1
    current_a=next_a; current_p=ps; depth=synth.next_level(depth)
 except OverflowError: return {"status":status_prefix+"_CALL_BUDGET_EXHAUSTED","calls":calls,"reused":reused}
 except EvidenceCatalogError as exc: return {"status":status_prefix+"_EVIDENCE_CATALOG_FAILURE","calls":calls,"reused":reused,"failure":str(exc)}
 except ValueError as exc: return {"status":status_prefix+("_EVIDENCE_RESOLUTION_INTEGRITY_FAILURE" if "ENVELOPE" in str(exc) else "_BUDGET_STRATEGY_FAILURE"),"calls":calls,"reused":reused,"failure":str(exc)}
 except RuntimeError as exc: return {"status":status_prefix+("_MODEL_SEMANTIC_FAILURE" if evidence_constrained else "_MODEL_CONTRACT_FAILURE"),"calls":calls,"reused":reused,"failure":str(exc),"model_id":model}
 docs={}; comparison={}
 for kind in profiles:
  doc=expand_document(globals[kind],final_packages[kind],all_a[kind]+[globals[kind]],all_p[kind]+[final_packages[kind]],coverage["metrics"])
  if not evidence_closed(doc): return {"status":status_prefix+"_TRACEABILITY_FAILURE","calls":calls,"reused":reused}
  text=render(doc,kind,model); path=workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if kind=="functional" else "LEVANTAMIENTO_TECNICO.md"); path.write_text(text,encoding="utf-8")
  after={"projects_represented":coverage["metrics"]["total_projects"],"webforms_represented":coverage["metrics"]["represented_webforms"],"flows_represented":coverage["metrics"]["represented_flows"],"data_operations_linked":coverage["metrics"]["linked_data_operations"],"stored_procedures_linked":coverage["metrics"]["linked_stored_procedures"],"confirmed":sum(c["status"]=="CONFIRMED" for c in doc["claims"]),"interpreted":sum(c["status"]=="INTERPRETED" for c in doc["claims"]),"unresolved":sum(c["status"]=="UNRESOLVED" for c in doc["claims"]),"missing_information":len(doc["missing_information"])}; comparison[kind]={"before":previous[kind],"after":after}; docs[kind]={"path":str(path),"bytes":len(text.encode()),"claims":len(doc["claims"]),"missing":len(doc["missing_information"]),"closed":True}
 index={"schema_version":"3.1.0","envelope":"PYTHON_CONTROLLED_IDENTITY","calls":calls,"reused":reused,"migrated":migrated,"invalidated":invalidated,"hierarchy_depth":depths,"intermediate":intermediate,"max_request_estimated_tokens":max_estimate,"comparison":comparison,"metrics":coverage["metrics"]}; target.mkdir(parents=True,exist_ok=True); (target/"COVERAGE_INDEX.json").write_text(json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
 return {"status":status_prefix+"_READY_FOR_HUMAN_REVIEW","calls":calls,"reused":reused,"migrated":migrated,"invalidated":invalidated,"model_id":model,"hierarchy_depth":depths,"intermediate":intermediate,"max_request_estimated_tokens":max_estimate,"documents":docs,"comparison":comparison}
if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,sort_keys=True,indent=2))
