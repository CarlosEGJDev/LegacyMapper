"""Evidence-constrained semantic interpretation of R8.1 deep evidence."""
import asyncio,hashlib,json,os
from pathlib import Path
from legacy_documenter.llm import LLMRequest,ProviderConfig,ProviderRegistry
from legacy_documenter.llm.copilot_pilot import discover_model
from legacy_documenter.utils import sanitize_data

TARGETS=("FMI-001","FMI-007","FMI-008","TMI-001","TMI-002","TMI-006","TMI-009","TMI-011")
GROUPS=(("FMI-001","FMI-007"),("FMI-008","TMI-001","TMI-006","TMI-011"),("TMI-002","TMI-009"))
NEXT={"RESOLVED_WITH_INTERPRETATION","PARTIALLY_RESOLVED_WITH_INTERPRETATION","STILL_UNRESOLVED","REQUIRES_HUMAN_KNOWLEDGE","REQUIRES_EXTERNAL_INFORMATION"}
CLAIM={"CONFIRMED","INTERPRETED","UNRESOLVED"}

def hid(prefix,value): return prefix+"-"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def estimate(value): return len(json.dumps(value,ensure_ascii=False,separators=(",",":")))//4

def evidence_pool(root):
 """Performs evidence pool while preserving this module's deterministic contract."""
 root=Path(root); summary=json.loads((root/"DEEP_ANALYSIS_SUMMARY.json").read_text(encoding="utf-8")); arch=json.loads((root/"ARCHITECTURE_EVIDENCE.json").read_text(encoding="utf-8")); projects=json.loads((root/"PROJECT_DEPENDENCIES.json").read_text(encoding="utf-8"))["dependencies"][:24]; ext=json.loads((root/"EXTERNAL_DEPENDENCIES.json").read_text(encoding="utf-8"));
 values=[]
 for key,value in sorted(summary["counts"].items()): values.append({"canonical_id":"R81-SUMMARY-counts-"+key,"kind":"SYSTEM_COUNT","fact":{key:value},"authoritative":True})
 for i,value in enumerate(arch["DETERMINISTIC_INDICATORS"]): values.append({"canonical_id":f"R81-ARCH-{i:02d}","kind":"ARCHITECTURE_INDICATOR","fact":value,"authoritative":True})
 for value in projects: values.append({"canonical_id":value["evidence_id"],"kind":"PROJECT_DEPENDENCY","fact":{k:value.get(k) for k in ("source_project","target","name","relationship_type","resolution_status")},"authoritative":value["resolution_status"]=="CONFIRMED"})
 for value in ext["assemblies"][:24]: values.append({"canonical_id":value["evidence_id"],"kind":"ASSEMBLY_REFERENCE","fact":{k:value.get(k) for k in ("source_project","assembly","version","hint_path","resolution_status")},"authoritative":True})
 for value in ext["integrations"][:24]: values.append({"canonical_id":value["evidence_id"],"kind":"INTEGRATION_INDICATOR","fact":{k:value.get(k) for k in ("source_file","line","indicators","excerpt","resolution_status")},"authoritative":True})
 return values,summary["source_before"]["metadata_hash"]

def select_for_group(pool,targets):
 """Performs select for group while preserving this module's deterministic contract."""
 kinds={"SYSTEM_COUNT"}
 if any(x in targets for x in ("FMI-001","FMI-007")): kinds|={"INTEGRATION_INDICATOR","ASSEMBLY_REFERENCE"}
 if any(x in targets for x in ("FMI-008","TMI-001","TMI-006","TMI-011")): kinds|={"ARCHITECTURE_INDICATOR","PROJECT_DEPENDENCY","ASSEMBLY_REFERENCE"}
 if any(x in targets for x in ("TMI-002","TMI-009")): kinds|={"PROJECT_DEPENDENCY","ASSEMBLY_REFERENCE","INTEGRATION_INDICATOR"}
 selected=[]; counts={}
 for item in pool:
  if item["kind"] not in kinds: continue
  limit=99 if item["kind"] in {"SYSTEM_COUNT","ARCHITECTURE_INDICATOR"} else 6
  if counts.get(item["kind"],0)>=limit: continue
  counts[item["kind"]]=counts.get(item["kind"],0)+1; selected.append(item)
 return selected

def semantic_schema(targets,aliases,purpose="SEMANTIC_INTERPRETATION"):
 """Performs semantic schema while preserving this module's deterministic contract."""
 statuses=["INTERPRETED","UNRESOLVED"] if purpose=="SEMANTIC_INTERPRETATION" else sorted(CLAIM)
 item={"type":"object","additionalProperties":False,"required":["target_id","interpretation_status","semantic_summary","claim_candidates","evidence_aliases","unresolved_aspects","recommended_next_status"],"properties":{"target_id":{"type":"string","enum":list(targets)},"interpretation_status":{"type":"string","enum":["VALID","INVALID","INSUFFICIENT_EVIDENCE"]},"semantic_summary":{"type":"string"},"claim_candidates":{"type":"array","items":{"type":"object","additionalProperties":False,"required":["statement","status","evidence_aliases"],"properties":{"statement":{"type":"string"},"status":{"type":"string","enum":statuses},"evidence_aliases":{"type":"array","items":{"type":"string","enum":aliases}}}}},"evidence_aliases":{"type":"array","items":{"type":"string","enum":aliases}},"unresolved_aspects":{"type":"array","items":{"type":"string"}},"recommended_next_status":{"type":"string","enum":sorted(NEXT)}}}
 return {"type":"object","additionalProperties":False,"required":["interpretations"],"properties":{"interpretations":{"type":"array","minItems":len(targets),"maxItems":len(targets),"items":item}}}

def plan_requests(evidence_root,token_budget=4200):
 """Performs plan requests while preserving this module's deterministic contract."""
 pool,snapshot=evidence_pool(evidence_root); requests=[]
 for n,targets in enumerate(GROUPS,1):
  selected=select_for_group(pool,targets); width=max(2,len(str(len(selected)))); catalog=[{"alias":f"E{i:0{width}d}","canonical_id":x["canonical_id"],"kind":x["kind"],"fact":x["fact"],"authoritative":x["authoritative"]} for i,x in enumerate(selected,1)]
  visible=[{k:x[k] for k in ("alias","kind","fact","authoritative")} for x in catalog]; context={"records":visible,"statistics":{"estimated_tokens":estimate(visible),"completeness":"FOCUSED_R8_1_EVIDENCE"}}
  if context["statistics"]["estimated_tokens"]>token_budget: raise ValueError("TOKEN_BUDGET")
  aliases=[x["alias"] for x in catalog]; schema=semantic_schema(targets,aliases); package_id=hid("CTX-R82",[targets,catalog,snapshot])
  request=LLMRequest("MISSING_INFORMATION_ANALYSIS","You are interpreting supplied evidence; you are not confirming new facts. Use INTERPRETED when evidence supports a semantic conclusion and UNRESOLVED when evidence is insufficient. Never upgrade an interpretation to CONFIRMED. Do not discover or assert new classes, methods, projects, procedures, dependencies, integrations, flow edges, WebForms, or architecture evidence. Do not invent evidence; preserve uncertainty.","Return exactly one item for each target. Cite only request-local aliases. Architecture conclusions must be PATTERN_SUPPORTED, HYBRID_PATTERN, NO_PATTERN_CONFIRMED, or INSUFFICIENT_EVIDENCE in semantic text; never force MVC. Do not infer business rules from names alone. Deterministic facts in context remain Python-owned and must not be emitted as newly confirmed semantic claims.",context,package_id,"3.2.0",snapshot,max_output_tokens=2600,structured_output=True,metadata={"target_ids":list(targets),"request_purpose":"SEMANTIC_INTERPRETATION","token_budget":token_budget,"provider_neutral":True,"evidence_policy":{"unknown_alias":"REJECT","nearest_match":False}})
  requests.append({"group":n,"target_ids":list(targets),"catalog":catalog,"request":request,"schema":schema,"estimated_tokens":context["statistics"]["estimated_tokens"]})
 return requests

def resolve_result(payload,plan):
 """Performs resolve result while preserving this module's deterministic contract."""
 if not isinstance(payload,dict) or not isinstance(payload.get("interpretations"),list): raise ValueError("SCHEMA")
 if sorted(x.get("target_id") for x in payload["interpretations"])!=sorted(plan["target_ids"]): raise ValueError("TARGET_SET")
 mapping={x["alias"]:x for x in plan["catalog"]}; out=[]
 for item in payload["interpretations"]:
  aliases=item.get("evidence_aliases",[])+[a for c in item.get("claim_candidates",[]) for a in c.get("evidence_aliases",[])]
  if any(x not in mapping for x in aliases): raise ValueError("UNKNOWN_EVIDENCE_ALIAS")
  for claim in item.get("claim_candidates",[]):
   if claim.get("status")=="CONFIRMED" and not claim.get("evidence_aliases"): raise ValueError("CONFIRMED_WITHOUT_EVIDENCE")
   if claim.get("status")=="CONFIRMED" and not all(mapping[x]["authoritative"] for x in claim["evidence_aliases"]): raise ValueError("CONFIRMED_WITHOUT_AUTHORITY")
  out.append({**item,"canonical_evidence_ids":sorted({mapping[x]["canonical_id"] for x in item.get("evidence_aliases",[]) + [a for c in item.get("claim_candidates",[]) for a in c.get("evidence_aliases",[])]}),"source_snapshots":[plan["request"].source_snapshot]})
 return sorted(out,key=lambda x:x["target_id"])

def merge_reevaluation(r81,interpretations):
 """Performs merge reevaluation while preserving this module's deterministic contract."""
 by={x["target_id"]:x for x in interpretations}; result=[]
 for item in r81:
  target=item["target_missing_information_id"]
  result.append({**item,"human_disposition":"NEEDS_ANALYSIS","candidate_status":by[target]["recommended_next_status"] if target in by else item["reevaluation_status"],"interpretation_evidence_ids":by[target]["canonical_evidence_ids"] if target in by else []})
 return result

def configured_provider():
 """Performs configured provider while preserving this module's deterministic contract."""
 provider_type=os.environ.get("LEGACYMAPPER_LLM_PROVIDER","COPILOT").upper(); model=os.environ.get("LEGACYMAPPER_LLM_MODEL")
 if provider_type=="COPILOT" and not model: model=asyncio.run(discover_model())
 config=ProviderConfig(provider_type,os.environ.get("LEGACYMAPPER_LLM_PROVIDER_ID",provider_type.lower()+"-local"),model or "",max_output_tokens=3000,options={"timeout":120})
 return ProviderRegistry().create(config),config

def run_deep_interpretation(evidence_root="output/v3_r8_1",output_dir="output/v3_r8_2",provider=None):
 """Performs run deep interpretation while preserving this module's deterministic contract."""
 root=Path(evidence_root); out=Path(output_dir); plans=plan_requests(root); out.mkdir(parents=True,exist_ok=True); actual_provider=provider; config=None; calls=0; retries=0; results=[]; failure=None; response=None; failed_plan=None; group_results=[]
 if actual_provider is None: actual_provider,config=configured_provider()
 for plan in plans:
  response=actual_provider.structured_generate(plan["request"],plan["schema"]); calls+=1
  if not response.parsed_output and response.validation_errors==["invalid json"]:
   response=actual_provider.structured_generate(plan["request"],plan["schema"]); calls+=1; retries+=1
  if not response.parsed_output: failure="MODEL_CONTRACT"; failed_plan=plan; break
  try: results+=resolve_result(response.parsed_output,plan)
  except ValueError as exc: failure="EVIDENCE_SELECTION:"+str(exc); failed_plan=plan; break
  group_results.append({"group":plan["group"],"target_ids":plan["target_ids"],"status":"VALID"})
 if failure: return {"status":"V3-R8_2_NEEDS_CORRECTION","failure":failure,"calls":calls,"retries":retries,"effective_provider":getattr(response,"provider_id",None),"effective_model":getattr(response,"model_id",None),"request_id":getattr(response,"request_id",None),"target_group":failed_plan["group"] if failed_plan else None,"validation_failure":failure}
 r81=json.loads((root/"MISSING_INFORMATION_REEVALUATION.json").read_text(encoding="utf-8"))["items"]; merged=merge_reevaluation(r81,results)
 arch_items=[x for x in results if x["target_id"] in {"FMI-008","TMI-001","TMI-006","TMI-011"}]
 architecture={"deterministic_indicators":json.loads((root/"ARCHITECTURE_EVIDENCE.json").read_text(encoding="utf-8"))["DETERMINISTIC_INDICATORS"],"contradicting_indicators":[],"llm_interpretation":arch_items,"pattern_status":"INSUFFICIENT_EVIDENCE" if all(x["interpretation_status"]=="INSUFFICIENT_EVIDENCE" for x in arch_items) else "NO_PATTERN_CONFIRMED","unresolved_points":sorted({u for x in arch_items for u in x["unresolved_aspects"]}),"evidence_ids":sorted({e for x in arch_items for e in x["canonical_evidence_ids"]})}
 request_log=[{"group":p["group"],"target_ids":p["target_ids"],"context_package_id":p["request"].context_package_id,"source_snapshot_ids":[p["request"].source_snapshot],"token_budget":p["request"].metadata["token_budget"],"estimated_tokens":p["estimated_tokens"],"allowed_evidence_catalog":[{"alias":x["alias"],"kind":x["kind"]} for x in p["catalog"]],"deterministic_facts":[{"canonical_id":x["canonical_id"],"fact":x["fact"]} for x in p["catalog"] if x["authoritative"]],"output_schema":p["schema"],"provider_neutral_metadata":True} for p in plans]
 provider_id=getattr(response,"provider_id",None); model_id=getattr(response,"model_id",None)
 summary={"status":"V3-R8_2_INTERPRETATION_COMPLETE","targets":list(TARGETS),"request_groups":len(plans),"group_results":group_results,"real_llm_calls":calls,"retries":retries,"effective_provider":provider_id,"effective_model":model_id,"model_failure_classification":None,"model_change_recommended":False,"model_change_reason":"No model-capability failure.","ai_knowledge_allowed":False}
 values={"INTERPRETATION_REQUESTS.json":{"requests":request_log},"INTERPRETATION_RESULTS.json":{"interpretations":results},"ARCHITECTURE_INTERPRETATION.json":architecture,"MISSING_INFORMATION_REEVALUATION.json":{"items":merged},"DEEP_ANALYSIS_MERGED_SUMMARY.json":summary}
 for name,value in values.items(): (out/name).write_text(json.dumps(sanitize_data(value),ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
 return summary
