from dataclasses import dataclass,field,asdict
import hashlib,json
from legacy_documenter.llm import LLMRequest
from legacy_documenter.documentation.contracts import FACT_STATUSES,SOURCE_TYPES

PROMPT_VERSION="1.0.0"
ASSESSMENT_STATUSES={"COMPLETE","PARTIAL","NEEDS_MORE_INFORMATION"}
ASSESSMENT_FIELDS=("assessment_id","profile_id","context_package_ids","source_snapshots","status","summary","claims","missing_information")
CLAIM_FIELDS=("claim_id","statement","status","source_type","evidence_refs","context_package_ids","section")
MISSING_INFORMATION_FIELDS=("request_id","document","section","question","reason","blocking_level","related_claim_ids","related_evidence_ids")
BLOCKING_LEVELS={"INFORMATIONAL","IMPORTANT","BLOCKING_FOR_APPROVAL"}
MODEL_SOURCE_TYPES=SOURCE_TYPES-{"APPROVED_FUNCTIONAL_DOCUMENT","APPROVED_TECHNICAL_DOCUMENT","APPROVED_EXTERNAL_INFORMATION"}

def canonical_assessment_schema(profile,package,sections):
 """Performs canonical assessment schema while preserving this module's deterministic contract."""
 evidence=sorted(str(r["ref"]) for r in package.get("records",[]) if r.get("ref") is not None)
 claim_properties={"claim_id":{"type":"string"},"statement":{"type":"string"},"status":{"type":"string","enum":sorted(FACT_STATUSES)},"source_type":{"type":"string","enum":sorted(MODEL_SOURCE_TYPES)},"evidence_refs":{"type":"array","items":{"type":"string","enum":evidence},"minItems":1},"context_package_ids":{"type":"array","const":[package["package_id"]]},"section":{"type":"string","enum":list(sections)}}
 missing_properties={"request_id":{"type":"string"},"document":{"type":"string","const":profile.profile_id},"section":{"type":"string","enum":list(sections)},"question":{"type":"string"},"reason":{"type":"string"},"blocking_level":{"type":"string","enum":sorted(BLOCKING_LEVELS)},"related_claim_ids":{"type":"array","items":{"type":"string"}},"related_evidence_ids":{"type":"array","items":{"type":"string","enum":evidence}}}
 return {"type":"object","additionalProperties":False,"required":list(ASSESSMENT_FIELDS),"properties":{"assessment_id":{"type":"string"},"profile_id":{"type":"string","const":profile.profile_id},"context_package_ids":{"type":"array","const":[package["package_id"]]},"source_snapshots":{"type":"array","const":[package["source_snapshot"]]},"status":{"type":"string","enum":sorted(ASSESSMENT_STATUSES)},"summary":{"type":"string"},"claims":{"type":"array","items":{"type":"object","additionalProperties":False,"required":list(CLAIM_FIELDS),"properties":claim_properties}},"missing_information":{"type":"array","items":{"type":"object","additionalProperties":False,"required":list(MISSING_INFORMATION_FIELDS),"properties":missing_properties}}}}
@dataclass(frozen=True)
class DocumentationProfile:
 """Provides the cohesive DocumentationProfile responsibility for this module."""
 profile_id:str; profile_version:str; purpose:str; required_context_types:tuple; preferred_context_types:tuple; required_sections:tuple; structured_output_schema:dict; claim_policy:dict; missing_information_policy:dict; instructions:str; metadata:dict=field(default_factory=dict)
FUNCTIONAL_PROFILE=DocumentationProfile("FUNCTIONAL_ASSESSMENT","1.0.0","FUNCTIONAL_DOCUMENTATION",("FUNCTIONAL",),("SYSTEM","FLOW","ENTITY","DATA_ACCESS"),("summary","claims","missing_information"),{"type":"object","required":["assessment_id","claims"]},{"confirmed_requires_authoritative":True},{"report_insufficient":True},"Connect entry points to evidence-supported flows; do not invent modules or business rules.")
TECHNICAL_PROFILE=DocumentationProfile("TECHNICAL_ASSESSMENT","1.0.0","TECHNICAL_DOCUMENTATION",("TECHNICAL",),("SYSTEM","ENTITY","FLOW","DATA_ACCESS"),("summary","claims","missing_information","architecture_patterns"),{"type":"object","required":["assessment_id","claims"]},{"confirmed_requires_authoritative":True},{"report_insufficient":True},"Describe components and dependencies cautiously; no architecture pattern is mandatory.")
@dataclass
class DocumentationPrompt:
 """Provides the cohesive DocumentationPrompt responsibility for this module."""
 profile:DocumentationProfile; packages:list[dict]; prompt_contract_version:str=PROMPT_VERSION
 @property
 def prompt_id(self): return "PROMPT-"+hashlib.sha256(json.dumps({"profile":self.profile.profile_id,"version":self.profile.profile_version,"packages":[x["package_id"] for x in self.packages]},sort_keys=True,separators=(",",":" )).encode()).hexdigest()
 def to_request(self):
  """Performs to request while preserving this module's deterministic contract."""
  system="You are an evidence-grounded software-system analyst. Use only supplied evidence. Never promote interpretation into deterministic fact. Mark insufficient evidence unresolved. All claims require traceable evidence. Do not infer unsupported architecture or business behavior. Output only the requested structured format."
  context={"packages":self.packages,"completeness":[x.get("statistics",{}).get("completeness") for x in self.packages],"unresolved_refs":[r for x in self.packages for r in x.get("unresolved_refs",[])]}
  task=self.profile.instructions+" Preserve truncation: absent evidence is not evidence of absence. Unresolved references do not permit target inference."
  return LLMRequest(self.profile.purpose,system,task,context,"+".join(x["package_id"] for x in self.packages),"3.1.0","+".join(sorted({x["source_snapshot"] for x in self.packages})),structured_output=True,metadata={"prompt_id":self.prompt_id,"profile_id":self.profile.profile_id,"evidence_policy":self.profile.claim_policy,"missing_information_policy":self.profile.missing_information_policy})
class AssessmentValidator:
 """Provides the cohesive AssessmentValidator responsibility for this module."""
 def validate(self,result,profile,packages):
  """Performs validate while preserving this module's deterministic contract."""
  errors=[]; package_ids={x["package_id"] for x in packages}; snapshots={x["source_snapshot"] for x in packages}; evidence={str(r.get("ref")) for x in packages for r in x.get("records",[])}
  if result.get("profile_id")!=profile.profile_id: errors.append("profile")
  if set(result.get("context_package_ids",[]))-package_ids: errors.append("package")
  if set(result.get("source_snapshots",[]))-snapshots: errors.append("snapshot")
  claims=result.get("claims",[]); ids=[x.get("claim_id") for x in claims]
  if len(ids)!=len(set(ids)): errors.append("duplicate claim")
  for claim in claims:
   refs=set(claim.get("evidence_refs",[]))
   if refs-evidence: errors.append("unknown evidence")
   if claim.get("status")=="CONFIRMED" and (not refs or claim.get("source_type")=="AI_INTERPRETATION"): errors.append("invalid confirmed")
  return {"valid":not errors,"status":result.get("status") if not errors else "INVALID","errors":errors}
