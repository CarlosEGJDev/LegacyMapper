"""Explicit, three-call Copilot pilot. Never imported or run by the test suite."""
import asyncio,importlib.util,json
from legacy_documenter.documentation.interpretation import DocumentationPrompt,FUNCTIONAL_PROFILE,TECHNICAL_PROFILE,AssessmentValidator
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider

ASSESSMENT_SCHEMA={
 "type":"object",
 "required":["assessment_id","profile_id","context_package_ids","source_snapshots","status","summary","claims","missing_information"],
 "properties":{
  "assessment_id":{"type":"string"},"profile_id":{"type":"string"},
  "context_package_ids":{"type":"array","items":{"type":"string"}},
  "source_snapshots":{"type":"array","items":{"type":"string"}},
  "status":{"enum":["COMPLETE","PARTIAL","NEEDS_MORE_INFORMATION"]},"summary":{"type":"string"},
  "claims":{"type":"array","items":{"type":"object","required":["claim_id","statement","status","source_type","evidence_refs"],"properties":{"claim_id":{"type":"string"},"statement":{"type":"string"},"status":{"enum":["CONFIRMED","INTERPRETED","UNRESOLVED"]},"source_type":{"enum":["DETERMINISTIC_ANALYSIS","AI_INTERPRETATION"]},"evidence_refs":{"type":"array","items":{"type":"string"}}}}},
  "missing_information":{"type":"array","items":{"type":"object","required":["description"],"properties":{"description":{"type":"string"},"related_evidence_refs":{"type":"array","items":{"type":"string"}}}}}
 }
}
def fixture(insufficient=False):
 """Performs fixture while preserving this module's deterministic contract."""
 records=[
  {"ref":"E_FACT","kind":"ENTRY_POINT","fact":"Public endpoint Orders.Get exists.","source_type":"DETERMINISTIC_ANALYSIS","provenance":{"path":"fixture/Orders.cs","line":10}},
  {"ref":"E_REL","kind":"CALL_RELATIONSHIP","fact":"Orders.Get calls IOrderReader.Read.","source_type":"DETERMINISTIC_ANALYSIS","provenance":{"path":"fixture/Orders.cs","line":12}},
  {"ref":"E_UNKNOWN","kind":"UNRESOLVED_RELATIONSHIP","fact":"Concrete target of IOrderReader is unresolved.","source_type":"DETERMINISTIC_ANALYSIS","provenance":{"path":"fixture/Orders.cs","line":12}}
 ]
 if insufficient: records=[records[0],{"ref":"E_UNKNOWN","kind":"UNRESOLVED_RELATIONSHIP","fact":"Downstream behavior and dependencies are unavailable.","source_type":"DETERMINISTIC_ANALYSIS","provenance":{"path":"fixture/Orders.cs","line":10}}]
 return {"package_id":"CTX-COPILOT-INSUFFICIENT" if insufficient else "CTX-COPILOT-SMALL","source_snapshot":"SNAP-COPILOT-PILOT-1","records":records,"unresolved_refs":["E_UNKNOWN"],"statistics":{"estimated_tokens":220,"completeness":"PARTIAL" if insufficient else "CONTROLLED"},"provenance":{"fixture":True,"repository_scan":False}}
def enrich(request,profile,insufficient):
 """Performs enrich while preserving this module's deterministic contract."""
 request.max_output_tokens=1200
 request.user_instruction += " Use exactly profile_id '%s', context_package_ids [%s], and source_snapshots [%s]. Status must be %s. Deterministic facts may be CONFIRMED only with evidence. Semantic meaning must be INTERPRETED. Preserve E_UNKNOWN as UNRESOLVED and describe missing information. Do not claim business rules, database objects, module ownership, external systems, or architecture unless explicit evidence supports them."%(profile.profile_id,json.dumps(request.context_package_id),json.dumps(request.source_snapshot),"PARTIAL or NEEDS_MORE_INFORMATION" if insufficient else "COMPLETE or PARTIAL")
 return request
async def discover_model():
 """Performs discover model while preserving this module's deterministic contract."""
 from copilot import CopilotClient
 client=CopilotClient(use_logged_in_user=True)
 await client.start()
 try:
  models=await client.list_models()
  if not models: raise RuntimeError("MODEL_UNAVAILABLE")
  return getattr(models[0],"id",None) or getattr(models[0],"model_id",None)
 finally: await client.stop()
def run():
 """Performs run while preserving this module's deterministic contract."""
 if importlib.util.find_spec("copilot") is None: return {"precondition":"BLOCKED_DEPENDENCY","calls":[]}
 try: model=asyncio.run(discover_model())
 except Exception as exc:
  message=str(exc).lower()
  condition="BLOCKED_COPILOT_AUTH" if "not authenticated" in message or "authenticate first" in message else "BLOCKED_COPILOT_ACCESS"
  return {"precondition":condition,"calls":[]}
 config=ProviderConfig("COPILOT","copilot-local",model,max_output_tokens=1200,capabilities={},options={"timeout":90})
 provider=CopilotProvider(config); validator=AssessmentValidator(); calls=[]
 for name,profile,insufficient in (("functional",FUNCTIONAL_PROFILE,False),("technical",TECHNICAL_PROFILE,False),("insufficient",FUNCTIONAL_PROFILE,True)):
  package=fixture(insufficient); request=enrich(DocumentationPrompt(profile,[package]).to_request(),profile,insufficient)
  response=provider.structured_generate(request,ASSESSMENT_SCHEMA)
  validation=validator.validate(response.parsed_output,profile,[package]) if response.parsed_output else {"valid":False,"errors":response.validation_errors}
  semantic_ok=validation["valid"]
  if insufficient and response.parsed_output: semantic_ok=semantic_ok and response.parsed_output.get("status") in ("PARTIAL","NEEDS_MORE_INFORMATION")
  calls.append({"pilot":name,"provider_status":response.status,"model_id":response.model_id,"structured":response.schema_validation_status,"assessment_valid":validation["valid"],"semantic_ok":semantic_ok,"assessment_status":response.parsed_output.get("status") if response.parsed_output else None,"claim_statuses":[c.get("status") for c in (response.parsed_output or {}).get("claims",[])],"evidence_refs":sorted({e for c in (response.parsed_output or {}).get("claims",[]) for e in c.get("evidence_refs",[])}),"validation_errors":validation.get("errors",[]),"usage":{"output_tokens":response.usage.output_tokens if response.usage else None,"estimated":response.usage.estimated if response.usage else True},"error_code":response.error.error_code if response.error else None})
 return {"precondition":"OK","model_id":model,"calls":calls}
if __name__=="__main__": print(json.dumps(run(),indent=2,sort_keys=True))
