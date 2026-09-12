"""Atomic assessment persistence and deterministic bounded synthesis planning."""
import hashlib,json,os,tempfile
from pathlib import Path

CONTRACT_VERSION="V3-R7.1-CANONICAL-1"
SCHEMA_VERSION="3.1.0"
def canonical_hash(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def request_identity(request,schema):
 """Performs request identity while preserving this module's deterministic contract."""
 return {"profile_id":request.metadata["profile_id"],"context_package_id":request.context_package_id,"source_snapshot":request.source_snapshot,"prompt_contract_version":CONTRACT_VERSION,"schema_version":SCHEMA_VERSION,"request_hash":canonical_hash({"system":request.system_instruction,"task":request.user_instruction,"context":request.context,"schema":schema})}

class AssessmentStore:
 """Provides the cohesive AssessmentStore responsibility for this module."""
 def __init__(self,path): self.path=Path(path)
 def load(self):
  """Performs load while preserving this module's deterministic contract."""
  if not self.path.exists(): return []
  data=json.loads(self.path.read_text(encoding="utf-8")); return data.get("assessments",[])
 def find(self,identity):
  """Performs find while preserving this module's deterministic contract."""
  for item in self.load():
   if item.get("identity")==identity and item.get("validation_status")=="VALID": return item
  return None
 def persist(self,identity,assessment,provider,model_id,stage,migration=None):
  """Performs persist while preserving this module's deterministic contract."""
  entry={"identity":identity,"assessment_id":assessment["assessment_id"],"profile_id":assessment["profile_id"],"assessment_status":assessment["status"],"context_package_id":identity["context_package_id"],"source_snapshot":identity["source_snapshot"],"claims":assessment["claims"],"missing_information":assessment["missing_information"],"assessment_payload":assessment,"provider":provider,"model_id":model_id,"prompt_contract_version":identity["prompt_contract_version"],"schema_version":identity["schema_version"],"validation_status":"VALID","stage":stage}
  entry["content_hash"]=canonical_hash({k:v for k,v in entry.items() if k!="content_hash"})
  if migration:
   entry["migration"]=migration
   entry["content_hash"]=canonical_hash({k:v for k,v in entry.items() if k!="content_hash"})
  items=[x for x in self.load() if x.get("identity")!=identity and not (migration and x.get("context_package_id")==identity["context_package_id"] and x.get("stage")==stage)]+[entry]; items.sort(key=lambda x:(x["stage"],x["context_package_id"],x["profile_id"]))
  payload=json.dumps({"schema_version":SCHEMA_VERSION,"assessments":items},ensure_ascii=False,sort_keys=True,indent=2)
  self.path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=self.path.name+".",suffix=".tmp",dir=self.path.parent)
  try:
   with os.fdopen(fd,"w",encoding="utf-8") as handle: handle.write(payload); handle.flush(); os.fsync(handle.fileno())
   os.replace(tmp,self.path)
  finally:
   if os.path.exists(tmp): os.unlink(tmp)
  return entry

def _record_lineage(record,package):
 lineage=(record.get("fact") or {}).get("lineage")
 return lineage or {"local_claim_ids":[],"evidence_ids":[record["ref"]],"context_package_ids":[package["package_id"]],"source_snapshots":[package["source_snapshot"]]}
def compact_assessments(assessments,packages):
 """Performs compact assessments while preserving this module's deterministic contract."""
 records=[]; seen=set()
 for assessment,package in zip(assessments,packages):
  source_records={r["ref"]:r for r in package["records"]}
  for claim in assessment["claims"]:
   lineages=[_record_lineage(source_records[r],package) for r in claim["evidence_refs"]]
   local_ids=sorted({x for l in lineages for x in l["local_claim_ids"]} or {"LOCAL-"+package["package_id"][-8:]+"-"+claim["claim_id"]})
   lineage={"local_claim_ids":local_ids,"evidence_ids":sorted({x for l in lineages for x in l["evidence_ids"]}),"context_package_ids":sorted({x for l in lineages for x in l["context_package_ids"]}),"source_snapshots":sorted({x for l in lineages for x in l["source_snapshots"]})}
   key=canonical_hash([claim["statement"],claim["status"],claim["source_type"],lineage]);
   if key in seen: continue
   seen.add(key); ref="SYN-"+key[:20]; records.append({"ref":ref,"category":"VALIDATED_CHILD_CLAIM","source_type":claim["source_type"],"fact":{"claim_id":claim["claim_id"],"status":claim["status"],"source_type":claim["source_type"],"statement":claim["statement"],"lineage":lineage}})
 return sorted(records,key=lambda x:x["ref"])

class SynthesisPlanner:
 """Provides the cohesive SynthesisPlanner responsibility for this module."""
 def __init__(self,target_tokens=4200,max_tokens=5000,max_records=35,max_depth=3): self.target_tokens=target_tokens; self.max_tokens=max_tokens; self.max_records=max_records; self.max_depth=max_depth
 def packages(self,kind,assessments,source_packages,snapshot,level,metrics=None):
  """Performs packages while preserving this module's deterministic contract."""
  records=compact_assessments(assessments,source_packages); groups=[]; current=[]
  for record in records:
   candidate=current+[record]; estimate=sum(len(json.dumps(x,ensure_ascii=False)) for x in candidate)//4
   if current and (estimate>self.target_tokens or len(candidate)>self.max_records): groups.append(current); current=[record]
   else: current=candidate
  if current: groups.append(current)
  packages=[]
  for i,group in enumerate(groups):
   body={"package_type":"FUNCTIONAL" if kind=="functional" else "TECHNICAL","schema_version":SCHEMA_VERSION,"source_snapshot":snapshot,"scope":{"document":kind,"synthesis_level":level,"group":i},"records":group,"unresolved_refs":[r["ref"] for r in group if r["source_type"]=="UNRESOLVED"],"statistics":{"records_included":len(group),"estimated_tokens":sum(len(json.dumps(r,ensure_ascii=False)) for r in group)//4,"completeness":"PARTIAL"},"provenance":{"source":"VALIDATED_CHILD_ASSESSMENTS","synthesis_level":level,"repository_scan":False}}
   if len(groups)==1 and metrics is not None: body["statistics"]["coverage_metrics"]=metrics
   body["package_id"]="CTX-SYN-"+canonical_hash(body); packages.append(body)
  if any(p["statistics"]["estimated_tokens"]>self.max_tokens for p in packages): raise ValueError("BUDGET_STRATEGY_FAILURE")
  return packages
 def next_level(self,depth):
  """Performs next level while preserving this module's deterministic contract."""
  if depth>=self.max_depth: raise ValueError("MAX_HIERARCHY_DEPTH")
  return depth+1

def expand_document(global_assessment,global_package,all_assessments,all_packages,coverage):
 """Performs expand document while preserving this module's deterministic contract."""
 source={r["ref"]:r for r in global_package["records"]}; claims=[]
 for claim in global_assessment["claims"]:
  lineages=[source[r]["fact"]["lineage"] for r in claim["evidence_refs"]]
  value={**claim,"local_claim_ids":sorted({x for l in lineages for x in l["local_claim_ids"]}),"evidence_refs":sorted({x for l in lineages for x in l["evidence_ids"]}),"context_package_ids":sorted({x for l in lineages for x in l["context_package_ids"]}),"source_snapshots":sorted({x for l in lineages for x in l["source_snapshots"]})}; claims.append(value)
 missing={}
 for assessment,package in zip(all_assessments,all_packages):
  records={r["ref"]:r for r in package["records"]}
  for item in assessment.get("missing_information",[]):
   refs=[]
   for ref in item.get("related_evidence_ids",[]): refs += _record_lineage(records[ref],package)["evidence_ids"] if ref in records else []
   value={**item,"related_evidence_ids":sorted(set(refs or item.get("related_evidence_ids",[])))}; key=canonical_hash([value.get("document"),value.get("section"),value.get("question"),value.get("reason"),value.get("blocking_level")]); missing.setdefault(key,value)
 leaf={x for p in all_packages if p["scope"].get("coverage_batch") is not None for r in p["records"] for x in [r["ref"]]}
 return {"claims":sorted(claims,key=lambda x:x["claim_id"]),"missing_information":[missing[k] for k in sorted(missing)],"context_package_ids":sorted({x for c in claims for x in c["context_package_ids"]}),"source_snapshots":sorted({x for c in claims for x in c["source_snapshots"]}),"evidence_ids":sorted(leaf),"coverage_metrics":coverage,"hierarchical_traceability":{c["claim_id"]:{"intermediate_claim_refs":c.get("evidence_refs",[]),"local_claim_ids":c["local_claim_ids"],"context_package_ids":c["context_package_ids"],"evidence_ids":c["evidence_refs"]} for c in claims}}
