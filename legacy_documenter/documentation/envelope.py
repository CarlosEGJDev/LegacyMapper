"""Python-owned assessment identity envelope; semantic payload is never repaired."""
import copy
from legacy_documenter.documentation.interpretation import ASSESSMENT_STATUSES,FACT_STATUSES,MODEL_SOURCE_TYPES,BLOCKING_LEVELS,CLAIM_FIELDS,MISSING_INFORMATION_FIELDS
from legacy_documenter.documentation.synthesis import canonical_hash,CONTRACT_VERSION,SCHEMA_VERSION

SEMANTIC_CLAIM_FIELDS=tuple(x for x in CLAIM_FIELDS if x!="context_package_ids")
SEMANTIC_MISSING_FIELDS=tuple(x for x in MISSING_INFORMATION_FIELDS if x!="document")
SEMANTIC_FIELDS=("status","summary","claims","missing_information")
def semantic_schema(profile,package,sections):
 """Performs semantic schema while preserving this module's deterministic contract."""
 evidence=sorted(str(r["ref"]) for r in package["records"])
 cp={"claim_id":{"type":"string"},"statement":{"type":"string"},"status":{"type":"string","enum":sorted(FACT_STATUSES)},"source_type":{"type":"string","enum":sorted(MODEL_SOURCE_TYPES)},"evidence_refs":{"type":"array","minItems":1,"items":{"type":"string","enum":evidence}},"section":{"type":"string","enum":list(sections)}}
 mp={"request_id":{"type":"string"},"section":{"type":"string","enum":list(sections)},"question":{"type":"string"},"reason":{"type":"string"},"blocking_level":{"type":"string","enum":sorted(BLOCKING_LEVELS)},"related_claim_ids":{"type":"array","items":{"type":"string"}},"related_evidence_ids":{"type":"array","items":{"type":"string","enum":evidence}}}
 return {"type":"object","additionalProperties":False,"required":list(SEMANTIC_FIELDS),"properties":{"status":{"type":"string","enum":sorted(ASSESSMENT_STATUSES)},"summary":{"type":"string"},"claims":{"type":"array","items":{"type":"object","additionalProperties":False,"required":list(SEMANTIC_CLAIM_FIELDS),"properties":cp}},"missing_information":{"type":"array","items":{"type":"object","additionalProperties":False,"required":list(SEMANTIC_MISSING_FIELDS),"properties":mp}}}}
def semantic_payload(assessment):
 """Performs semantic payload while preserving this module's deterministic contract."""
 return {"status":assessment["status"],"summary":assessment["summary"],"claims":[{k:v for k,v in c.items() if k!="context_package_ids"} for c in assessment["claims"]],"missing_information":[{k:v for k,v in m.items() if k!="document"} for m in assessment["missing_information"]]}
def compose_envelope(payload,profile,package,request_hash,stage):
 """Performs compose envelope while preserving this module's deterministic contract."""
 semantic=copy.deepcopy(payload); assessment_id="ASSESS-"+canonical_hash([stage,profile.profile_id,package["package_id"],request_hash])
 return {"assessment_id":assessment_id,"profile_id":profile.profile_id,"context_package_ids":[package["package_id"]],"source_snapshots":[package["source_snapshot"]],"status":semantic["status"],"summary":semantic["summary"],"claims":[{**c,"context_package_ids":[package["package_id"]]} for c in semantic["claims"]],"missing_information":[{**m,"document":profile.profile_id} for m in semantic["missing_information"]]}
def semantic_unchanged(payload,composed): return payload==semantic_payload(composed)
def semantic_request(base_request,profile,package,sections):
 """Performs semantic request while preserving this module's deterministic contract."""
 base_request.user_instruction=profile.instructions+" Return semantic assessment JSON only. Python owns deterministic identity. Do not emit assessment_id, profile_id, context_package_id, context_package_ids, source_snapshot, source_snapshots, schema_version, prompt_contract_version, request_hash, provider metadata, model metadata, stage, or validation marker. Required semantic fields: status, summary, claims, missing_information. Claim fields: "+str(list(SEMANTIC_CLAIM_FIELDS))+". MissingInformation fields: "+str(list(SEMANTIC_MISSING_FIELDS))+". Allowed claim statuses: "+str(sorted(FACT_STATUSES))+". Allowed source types: "+str(sorted(MODEL_SOURCE_TYPES))+". CONFIRMED requires deterministic evidence; AI_INTERPRETATION must be INTERPRETED; UNRESOLVED must remain UNRESOLVED. Use only exact evidence IDs supplied in context. Return one strict JSON object only, no Markdown or prose. Allowed sections: "+str(list(sections))+"."
 base_request.metadata["envelope"]={"profile_id":profile.profile_id,"context_package_id":package["package_id"],"source_snapshot":package["source_snapshot"],"schema_version":SCHEMA_VERSION,"prompt_contract_version":CONTRACT_VERSION}
 return base_request
