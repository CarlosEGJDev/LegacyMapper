"""Explicit resumable V3-R7.2.1 execution."""
import asyncio,json
from pathlib import Path
from legacy_documenter.documentation.coverage import CoveragePlanner
from legacy_documenter.documentation.systematic import _package,_previous,_global_rules
from legacy_documenter.documentation.generator import _request,_schema,_strict,prevalidate_request
from legacy_documenter.documentation.interpretation import FUNCTIONAL_PROFILE,TECHNICAL_PROFILE
from legacy_documenter.documentation.synthesis import AssessmentStore,SynthesisPlanner,request_identity,expand_document
from legacy_documenter.documentation.aggregation import evidence_closed
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider
from legacy_documenter.llm.copilot_pilot import discover_model

def run(workspace="."):
 """Performs run while preserving this module's deterministic contract."""
 workspace=Path(workspace); root=workspace/"output"/"v2_r5_1_full"; planner=CoveragePlanner(root); coverage=planner.plan(); batches=planner.batches(coverage,8,35); synth=SynthesisPlanner(); out=workspace/"output"/"v3_r7_2"
 local_store=AssessmentStore(out/"LOCAL_ASSESSMENTS.json"); intermediate_store=AssessmentStore(out/"INTERMEDIATE_ASSESSMENTS.json")
 packages={k:[_package(k,i,b,coverage["snapshot"],coverage["metrics"]) for i,b in enumerate(batches)] for k in ("functional","technical")}; profiles={"functional":FUNCTIONAL_PROFILE,"technical":TECHNICAL_PROFILE}
 previous={k:_previous(workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if k=="functional" else "LEVANTAMIENTO_TECNICO.md")) for k in profiles}; preflight=[]
 for kind in profiles:
  for p in packages[kind]:
   request=_request(profiles[kind],p,kind); request.user_instruction += " Produce at most 5 high-value claims and at most 3 MissingInformation items. V2 lookup has completed."; schema=_schema(profiles[kind],p,kind); schema["properties"]["claims"]["maxItems"]=5
   errors=prevalidate_request(request,schema,profiles[kind],p)
   if errors or p["statistics"]["estimated_tokens"]>5000: return {"status":"V3-R7_2_1_BUDGET_STRATEGY_FAILURE","calls":0,"errors":errors,"tokens":p["statistics"]["estimated_tokens"]}
   preflight.append(p["statistics"]["estimated_tokens"])
 try: model=asyncio.run(discover_model())
 except Exception: return {"status":"V3-R7_2_1_BLOCKED_PROVIDER","calls":0}
 provider=CopilotProvider(ProviderConfig("COPILOT","copilot-local",model,max_output_tokens=3000,options={"timeout":120})); calls=0; reused=0; invalidated=0
 def execute(kind,package,stage,store,max_claims=8):
  """Performs execute while preserving this module's deterministic contract."""
  nonlocal calls,reused,invalidated,model
  profile=profiles[kind]; request=_request(profile,package,kind)
  request.user_instruction += (" This is a local assessment of deterministic V2 coverage records. V2 lookup has completed." if stage.startswith("LOCAL_") else " This is "+stage+" synthesis over validated child claims. Preserve child statuses and identifiers. A CONFIRMED result may cite only CONFIRMED DETERMINISTIC_CODE_FACT children.")+" Produce at most "+str(max_claims)+" claims."
  schema=_schema(profile,package,kind); schema["properties"]["claims"]["maxItems"]=max_claims
  errors=prevalidate_request(request,schema,profile,package)
  if errors or package["statistics"]["estimated_tokens"]>5000: raise ValueError("REQUEST_PREFLIGHT")
  identity=request_identity(request,schema); cached=store.find(identity)
  if cached: reused+=1; return cached["assessment_payload"],cached.get("model_id")
  invalidated += sum(1 for x in store.load() if x.get("context_package_id")==package["package_id"] and x.get("identity")!=identity)
  response=provider.structured_generate(request,schema); calls+=1; errors=list(response.validation_errors) if not response.parsed_output else _strict(response.parsed_output,profile,package)+([] if stage.startswith("LOCAL_") else _global_rules(response.parsed_output,package))
  if errors: raise RuntimeError("MODEL_CONTRACT:"+",".join(sorted(set(errors))))
  store.persist(identity,response.parsed_output,"COPILOT",response.model_id,stage); model=response.model_id; return response.parsed_output,response.model_id
 local={"functional":[],"technical":[]}; all_assessments={"functional":[],"technical":[]}; all_packages={"functional":[],"technical":[]}; intermediate_counts={"functional":0,"technical":0}; depth_used={}
 try:
  for kind in profiles:
   for p in packages[kind]:
    a,_=execute(kind,p,"LOCAL_"+kind.upper(),local_store,5); local[kind].append(a); all_assessments[kind].append(a); all_packages[kind].append(p)
  globals={}; final_packages={}
  for kind in profiles:
   current_a=list(local[kind]); current_p=list(packages[kind]); depth=1
   while True:
    synthesis_packages=synth.packages(kind,current_a,current_p,coverage["snapshot"],depth,coverage["metrics"])
    preflight += [p["statistics"]["estimated_tokens"] for p in synthesis_packages]
    if any(p["statistics"]["estimated_tokens"]>5000 for p in synthesis_packages): raise ValueError("BUDGET_STRATEGY_FAILURE")
    if len(synthesis_packages)==1:
     a,_=execute(kind,synthesis_packages[0],"GLOBAL_"+kind.upper(),intermediate_store,20); globals[kind]=a; final_packages[kind]=synthesis_packages[0]; depth_used[kind]=depth; break
    next_a=[]
    for p in synthesis_packages:
     a,_=execute(kind,p,"INTERMEDIATE_"+kind.upper()+"_L"+str(depth),intermediate_store,8); next_a.append(a); all_assessments[kind].append(a); all_packages[kind].append(p); intermediate_counts[kind]+=1
    current_a=next_a; current_p=synthesis_packages; depth=synth.next_level(depth)
 except ValueError: return {"status":"V3-R7_2_1_BUDGET_STRATEGY_FAILURE","calls":calls,"reused":reused,"max_tokens":max(preflight)}
 except RuntimeError as exc: return {"status":"V3-R7_2_1_MODEL_CONTRACT_FAILURE","calls":calls,"reused":reused,"failure":str(exc),"model_id":model}
 documents={}; comparison={}
 for kind in profiles:
  document=expand_document(globals[kind],final_packages[kind],all_assessments[kind],all_packages[kind],coverage["metrics"])
  if not evidence_closed(document): return {"status":"V3-R7_2_1_TRACEABILITY_FAILURE","calls":calls,"reused":reused}
  text=render(document,kind,model); path=workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if kind=="functional" else "LEVANTAMIENTO_TECNICO.md"); path.write_text(text,encoding="utf-8")
  after={"projects_represented":coverage["metrics"]["total_projects"],"webforms_represented":coverage["metrics"]["represented_webforms"],"flows_represented":coverage["metrics"]["represented_flows"],"data_operations_linked":coverage["metrics"]["linked_data_operations"],"stored_procedures_linked":coverage["metrics"]["linked_stored_procedures"],"confirmed":sum(c["status"]=="CONFIRMED" for c in document["claims"]),"interpreted":sum(c["status"]=="INTERPRETED" for c in document["claims"]),"unresolved":sum(c["status"]=="UNRESOLVED" for c in document["claims"]),"missing_information":len(document["missing_information"])}
  comparison[kind]={"before":previous[kind],"after":after}; documents[kind]={"path":str(path),"bytes":len(text.encode()),"claims":len(document["claims"]),"missing":len(document["missing_information"]),"closed":True}
 index={"schema_version":"3.1.0","metrics":coverage["metrics"],"hierarchy_depth":depth_used,"cache":{"reused":reused,"invalidated":invalidated},"calls":calls,"max_request_estimated_tokens":max(preflight),"local_assessments":{k:len(v) for k,v in local.items()},"intermediate_assessments":intermediate_counts,"comparison":comparison}
 out.mkdir(parents=True,exist_ok=True); (out/"COVERAGE_INDEX.json").write_text(json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
 return {"status":"V3-R7_2_1_READY_FOR_HUMAN_REVIEW","calls":calls,"reused":reused,"invalidated":invalidated,"model_id":model,"hierarchy_depth":depth_used,"intermediate":intermediate_counts,"max_request_estimated_tokens":max(preflight),"documents":documents,"comparison":comparison}
if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,sort_keys=True,indent=2))
