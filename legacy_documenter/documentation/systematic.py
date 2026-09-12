"""Explicit V3-R7.2 hierarchical generation from existing V2 evidence only."""
import asyncio,hashlib,json,re
from collections import Counter
from pathlib import Path
from legacy_documenter.documentation.coverage import CoveragePlanner
from legacy_documenter.documentation.generator import _request,_schema,_strict,prevalidate_request
from legacy_documenter.documentation.interpretation import FUNCTIONAL_PROFILE,TECHNICAL_PROFILE
from legacy_documenter.documentation.aggregation import hierarchical_aggregate,evidence_closed
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider
from legacy_documenter.llm.copilot_pilot import discover_model

def _package(kind,index,units,snapshot,metrics):
 records=[{"ref":"COV-SYSTEM-METRICS","category":"SYSTEM","priority":"P0","fact":metrics,"source_type":"DETERMINISTIC_CODE_FACT"}]+[{"ref":u["unit_id"],"category":u["category"],"priority":u["priority"],"fact":u["fact"],"source_type":"DETERMINISTIC_CODE_FACT"} for u in units]
 body={"package_type":"FUNCTIONAL" if kind=="functional" else "TECHNICAL","schema_version":"3.1.0","source_snapshot":snapshot,"scope":{"document":kind,"coverage_batch":index,"systematic":True},"records":records,"unresolved_refs":[r["ref"] for r in records if r["category"]=="UNRESOLVED_BOUNDARIES"],"statistics":{"records_included":len(records),"estimated_tokens":sum(len(json.dumps(r,ensure_ascii=False)) for r in records)//4,"completeness":"PARTIAL","v2_lookup_completed":True},"provenance":{"artifacts":"V2-R5.1","coverage_batch":index,"repository_scan":False,"v2_lookup_before_missing_information":True}}
 body["package_id"]="CTX-R72-"+hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(); return body
def _global_package(kind,assessments,packages,snapshot,metrics):
 records=[]
 for assessment,package in zip(assessments,packages):
  for c in assessment["claims"]:
   ref="LOCAL-"+package["package_id"][-8:]+"-"+c["claim_id"]
   records.append({"ref":ref,"category":"VALIDATED_LOCAL_CLAIM","fact":{"statement":c["statement"],"status":c["status"],"source_type":c["source_type"],"leaf_evidence_refs":c["evidence_refs"],"context_package_id":package["package_id"]},"source_type":c["source_type"]})
 records=sorted(records,key=lambda x:x["ref"])
 body={"package_type":"FUNCTIONAL" if kind=="functional" else "TECHNICAL","schema_version":"3.1.0","source_snapshot":snapshot,"scope":{"document":kind,"global_synthesis":True},"records":records,"unresolved_refs":[r["ref"] for r in records if r["source_type"]=="UNRESOLVED"],"statistics":{"records_included":len(records),"estimated_tokens":sum(len(json.dumps(r,ensure_ascii=False)) for r in records)//4,"completeness":"PARTIAL","coverage_metrics":metrics},"provenance":{"source":"VALIDATED_LOCAL_ASSESSMENTS","repository_scan":False}}
 body["package_id"]="CTX-R72-GLOBAL-"+hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(); return body
def _previous(path):
 if not path.exists(): return {}
 text=path.read_text(encoding="utf-8"); refs=set(re.findall(r"PROJECT-\d+",text)); flows=set(re.findall(r"FLOW-\d+",text)); forms=set(re.findall(r"WEBFORM-\d+",text))
 return {"projects_represented":len(refs),"flows_represented":len(flows),"webforms_represented":len(forms),"missing_information":len(re.findall(r"^- `[^`]+` \[",text,re.M)),**{s.lower():len(re.findall(r"\["+s+r"\]",text)) for s in ("CONFIRMED","INTERPRETED","UNRESOLVED")}}
def _global_rules(result,package):
 records={r["ref"]:r for r in package["records"]}; errors=[]
 for c in result.get("claims",[]):
  if c.get("status")=="CONFIRMED" and any(records[r]["fact"]["status"]!="CONFIRMED" or records[r]["source_type"]!="DETERMINISTIC_CODE_FACT" for r in c.get("evidence_refs",[]) if r in records): errors.append("global status promotion")
 return sorted(set(errors))
def run(workspace="."):
 """Performs run while preserving this module's deterministic contract."""
 workspace=Path(workspace); root=workspace/"output"/"v2_r5_1_full"; planner=CoveragePlanner(root); plan=planner.plan(); batches=planner.batches(plan,count=8,max_records=35)
 previous={k:_previous(workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if k=="functional" else "LEVANTAMIENTO_TECNICO.md")) for k in ("functional","technical")}
 packages={"functional":[],"technical":[]}; local={"functional":[],"technical":[]}; summaries=[]
 for kind in packages:
  for i,batch in enumerate(batches):
   p=_package(kind,i,batch,plan["snapshot"],plan["metrics"]); packages[kind].append(p)
   if len(p["records"])>35 or p["statistics"]["estimated_tokens"]>5000: return {"status":"V3-R7_2_BUDGET_INSUFFICIENT","calls":0,"package":p["package_id"],"records":len(p["records"]),"tokens":p["statistics"]["estimated_tokens"]}
   profile=FUNCTIONAL_PROFILE if kind=="functional" else TECHNICAL_PROFILE; request=_request(profile,p,kind); request.user_instruction += " Produce at most 5 high-value claims and at most 3 MissingInformation items. V2 lookup has already completed for this coverage unit; ask only for genuinely absent or ambiguous facts."; schema=_schema(profile,p,kind); schema["properties"]["claims"]["maxItems"]=5; schema["properties"]["missing_information"]["maxItems"]=3
   if prevalidate_request(request,schema,profile,p): return {"status":"V3-R7_2_REQUEST_CONTRACT_FAILURE","calls":0}
 try: model=asyncio.run(discover_model())
 except Exception: return {"status":"V3-R7_2_BLOCKED_PROVIDER","calls":0}
 provider=CopilotProvider(ProviderConfig("COPILOT","copilot-local",model,max_output_tokens=3000,options={"timeout":120})); calls=0
 for kind,profile in (("functional",FUNCTIONAL_PROFILE),("technical",TECHNICAL_PROFILE)):
  for p in packages[kind]:
   request=_request(profile,p,kind); request.user_instruction += " Produce at most 5 high-value claims and at most 3 MissingInformation items. V2 lookup has already completed; ask only for genuinely absent or ambiguous facts."; schema=_schema(profile,p,kind); schema["properties"]["claims"]["maxItems"]=5; schema["properties"]["missing_information"]["maxItems"]=3
   response=provider.structured_generate(request,schema); calls+=1; errors=list(response.validation_errors) if not response.parsed_output else _strict(response.parsed_output,profile,p)
   if errors: return {"status":"V3-R7_2_MODEL_CONTRACT_FAILURE","calls":calls,"stage":"local-"+kind,"errors":errors,"model_id":response.model_id}
   local[kind].append(response.parsed_output); summaries.append({"kind":kind,"package_id":p["package_id"],"claims":len(response.parsed_output["claims"]),"missing":len(response.parsed_output["missing_information"]),"valid":True})
 globals={}; global_packages={}
 for kind,profile in (("functional",FUNCTIONAL_PROFILE),("technical",TECHNICAL_PROFILE)):
  gp=_global_package(kind,local[kind],packages[kind],plan["snapshot"],plan["metrics"]); global_packages[kind]=gp
  if len(gp["records"])>40 or gp["statistics"]["estimated_tokens"]>5000: return {"status":"V3-R7_2_BUDGET_INSUFFICIENT","calls":calls,"stage":"global-"+kind,"records":len(gp["records"]),"tokens":gp["statistics"]["estimated_tokens"]}
  request=_request(profile,gp,kind); request.user_instruction += " This is bounded global synthesis over validated local claims, not raw evidence. Preserve local statuses. A global CONFIRMED claim may cite only CONFIRMED DETERMINISTIC_CODE_FACT local claims. Do not promote INTERPRETED or UNRESOLVED local claims."; schema=_schema(profile,gp,kind); schema["properties"]["claims"]["maxItems"]=20
  if prevalidate_request(request,schema,profile,gp): return {"status":"V3-R7_2_REQUEST_CONTRACT_FAILURE","calls":calls}
  response=provider.structured_generate(request,schema); calls+=1; errors=list(response.validation_errors) if not response.parsed_output else _strict(response.parsed_output,profile,gp)+_global_rules(response.parsed_output,gp)
  if errors: return {"status":"V3-R7_2_MODEL_CONTRACT_FAILURE","calls":calls,"stage":"global-"+kind,"errors":sorted(set(errors)),"model_id":response.model_id}
  globals[kind]=response.parsed_output; model=response.model_id
 docs={}; comparison={}
 for kind in ("functional","technical"):
  document=hierarchical_aggregate(globals[kind],global_packages[kind],local[kind],packages[kind],plan["metrics"])
  if not evidence_closed(document): return {"status":"V3-R7_2_TRACEABILITY_FAILURE","calls":calls}
  text=render(document,kind,model); path=workspace/"output"/("LEVANTAMIENTO_FUNCIONAL.md" if kind=="functional" else "LEVANTAMIENTO_TECNICO.md"); path.write_text(text,encoding="utf-8")
  current={"projects_represented":plan["metrics"]["total_projects"],"flows_represented":plan["metrics"]["represented_flows"],"webforms_represented":plan["metrics"]["represented_webforms"],"data_operations_linked":plan["metrics"]["linked_data_operations"],"stored_procedures_linked":plan["metrics"]["linked_stored_procedures"],"missing_information":len(document["missing_information"]),**{s.lower():sum(c["status"]==s for c in document["claims"]) for s in ("CONFIRMED","INTERPRETED","UNRESOLVED")}}
  comparison[kind]={"before":previous[kind],"after":current}; docs[kind]={"path":str(path),"bytes":len(text.encode()),"claims":len(document["claims"]),"missing":len(document["missing_information"]),"closed":True}
 index={"schema_version":"3.1.0","source_snapshot":plan["snapshot"],"metrics":plan["metrics"],"project_classification":plan["projects"],"coverage_units":[{"unit_id":u["unit_id"],"category":u["category"],"priority":u["priority"]} for u in plan["units"]],"batches":[[u["unit_id"] for u in b] for b in batches],"local_assessments":summaries,"global_packages":{k:v["package_id"] for k,v in global_packages.items()},"comparison":comparison}
 target=workspace/"output"/"v3_r7_2"; target.mkdir(parents=True,exist_ok=True); (target/"COVERAGE_INDEX.json").write_text(json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
 return {"status":"V3-R7_2_READY_FOR_HUMAN_REVIEW","calls":calls,"model_id":model,"coverage_units":len(plan["units"]),"batches_per_kind":len(batches),"metrics":plan["metrics"],"local_assessments":summaries,"documents":docs,"comparison":comparison}
if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,sort_keys=True,indent=2))
