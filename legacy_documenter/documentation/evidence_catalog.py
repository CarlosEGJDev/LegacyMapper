"""Request-local evidence-key catalogs and strict canonical resolution."""
import copy,json,math
from legacy_documenter.documentation.envelope import SEMANTIC_FIELDS,SEMANTIC_CLAIM_FIELDS,SEMANTIC_MISSING_FIELDS
from legacy_documenter.documentation.interpretation import ASSESSMENT_STATUSES,FACT_STATUSES,MODEL_SOURCE_TYPES,BLOCKING_LEVELS

class EvidenceCatalogError(ValueError): pass
def _safe(value):
 if isinstance(value,dict): return {k:_safe(v) for k,v in sorted(value.items()) if "id" not in k.lower() and "ref" not in k.lower() and k!="lineage"}
 if isinstance(value,list): return [_safe(x) for x in value[:4]]
 if isinstance(value,str): return value if len(value)<=100 else value[:97]+"..."
 return value
def build_catalog(package):
 """Performs build catalog while preserving this module's deterministic contract."""
 records=sorted(package.get("records",[]),key=lambda x:str(x.get("ref",""))); width=max(2,len(str(len(records)))); entries=[]
 for i,r in enumerate(records,1): entries.append({"key":"E"+str(i).zfill(width),"type":r.get("category") or r.get("type") or "EVIDENCE","description":json.dumps(_safe(r.get("fact",{})),ensure_ascii=False,sort_keys=True,separators=(",",":"))[:500],"canonical_id":str(r["ref"])})
 validate_catalog(entries,package); return entries
def validate_catalog(catalog,package):
 """Performs validate catalog while preserving this module's deterministic contract."""
 keys=[x.get("key") for x in catalog]; ids=[x.get("canonical_id") for x in catalog]; known=[str(r["ref"]) for r in package.get("records",[])]
 if len(keys)!=len(set(keys)) or any(not k or not k.startswith("E") for k in keys): raise EvidenceCatalogError("duplicate_or_invalid_key")
 if len(ids)!=len(set(ids)) or set(ids)!=set(known): raise EvidenceCatalogError("canonical_closure")
 if any(not isinstance(x.get("description"),str) for x in catalog): raise EvidenceCatalogError("description")
 return True
def visible_catalog(catalog): return [{"key":x["key"],"type":x["type"],"description":x["description"]} for x in catalog]
def catalog_schema(profile,catalog,sections):
 """Performs catalog schema while preserving this module's deterministic contract."""
 keys=[x["key"] for x in catalog]; cp={"claim_id":{"type":"string"},"statement":{"type":"string"},"status":{"type":"string","enum":sorted(FACT_STATUSES)},"source_type":{"type":"string","enum":sorted(MODEL_SOURCE_TYPES)},"evidence_keys":{"type":"array","minItems":1,"items":{"type":"string","enum":keys}},"section":{"type":"string","enum":list(sections)}}; mp={"request_id":{"type":"string"},"section":{"type":"string","enum":list(sections)},"question":{"type":"string"},"reason":{"type":"string"},"blocking_level":{"type":"string","enum":sorted(BLOCKING_LEVELS)},"related_claim_ids":{"type":"array","items":{"type":"string"}},"related_evidence_keys":{"type":"array","items":{"type":"string","enum":keys}}}
 return {"type":"object","additionalProperties":False,"required":list(SEMANTIC_FIELDS),"properties":{"status":{"type":"string","enum":sorted(ASSESSMENT_STATUSES)},"summary":{"type":"string"},"claims":{"type":"array","items":{"type":"object","additionalProperties":False,"required":["claim_id","statement","status","source_type","evidence_keys","section"],"properties":cp}},"missing_information":{"type":"array","items":{"type":"object","additionalProperties":False,"required":["request_id","section","question","reason","blocking_level","related_claim_ids","related_evidence_keys"],"properties":mp}}}}
def catalog_request(base_request,profile,package,sections,catalog):
 """Performs catalog request while preserving this module's deterministic contract."""
 base_request.context={"allowed_evidence_catalog":visible_catalog(catalog),"statistics":package.get("statistics",{}),"scope":package.get("scope",{}),"unresolved_evidence_keys":[x["key"] for x in catalog if x["canonical_id"] in package.get("unresolved_refs",[])]}
 base_request.user_instruction=profile.instructions+" Return semantic assessment JSON only. Python owns all identity metadata. Select evidence using evidence_keys only from AllowedEvidenceCatalog, an enum-like closed set. Never invent keys and never output canonical evidence IDs. If support is absent, use INTERPRETED or UNRESOLVED and MissingInformation rather than inventing evidence. Claims require claim_id, statement, status, source_type, evidence_keys, section. MissingInformation requires request_id, section, question, reason, blocking_level, related_claim_ids, related_evidence_keys. Strict JSON only; no Markdown or prose. Allowed sections: "+str(list(sections))+"."
 base_request.metadata["evidence_transport"]="REQUEST_LOCAL_KEYS"; return base_request
def resolve_payload(payload,catalog):
 """Performs resolve payload while preserving this module's deterministic contract."""
 mapping={x["key"]:x["canonical_id"] for x in catalog}; result=copy.deepcopy(payload)
 for c in result.get("claims",[]):
  keys=c.get("evidence_keys")
  if not isinstance(keys,list) or any(k not in mapping for k in keys): raise EvidenceCatalogError("unknown_claim_key")
  c["evidence_refs"]=[mapping[k] for k in keys]; del c["evidence_keys"]
 for m in result.get("missing_information",[]):
  keys=m.get("related_evidence_keys")
  if not isinstance(keys,list) or any(k not in mapping for k in keys): raise EvidenceCatalogError("unknown_missing_key")
  m["related_evidence_ids"]=[mapping[k] for k in keys]; del m["related_evidence_keys"]
 return result
def resolution_preserves_semantics(original,resolved):
 """Performs resolution preserves semantics while preserving this module's deterministic contract."""
 a=copy.deepcopy(original); b=copy.deepcopy(resolved)
 for x,y in zip(a.get("claims",[]),b.get("claims",[])): x.pop("evidence_keys",None); y.pop("evidence_refs",None)
 for x,y in zip(a.get("missing_information",[]),b.get("missing_information",[])): x.pop("related_evidence_keys",None); y.pop("related_evidence_ids",None)
 return a==b
