"""Deterministic aggregation for validated documentation assessments."""
import hashlib,json

STATUS_RANK={"UNRESOLVED":0,"INTERPRETED":1,"CONFIRMED":2}
ALLOWED_SOURCES={"DETERMINISTIC_CODE_FACT","AI_INTERPRETATION","UNRESOLVED"}

def _stable(prefix,value):
 return prefix+"-"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:16]

def aggregate(assessments,packages):
 """Performs aggregate while preserving this module's deterministic contract."""
 package_ids=sorted(p["package_id"] for p in packages); snapshots=sorted({p["source_snapshot"] for p in packages})
 evidence={str(r["ref"]) for p in packages for r in p.get("records",[]) if r.get("ref")}
 claims={}; missing={}
 for assessment in assessments:
  for claim in assessment.get("claims",[]):
   if claim.get("source_type") not in ALLOWED_SOURCES: continue
   refs=set(map(str,claim.get("evidence_refs",[])))
   if not refs or refs-evidence: continue
   key=claim.get("claim_id") or _stable("CLAIM",[claim.get("statement"),sorted(refs)])
   value={**claim,"claim_id":key,"evidence_refs":sorted(refs),"context_package_ids":sorted(set(claim.get("context_package_ids",[])) or set(assessment.get("context_package_ids",[])))}
   if key in claims:
    old=claims[key]; value["evidence_refs"]=sorted(set(old["evidence_refs"])|set(value["evidence_refs"])); value["context_package_ids"]=sorted(set(old["context_package_ids"])|set(value["context_package_ids"]))
    # Any weaker observation keeps the merged claim from being promoted.
    value["status"]=min((old.get("status","UNRESOLVED"),value.get("status","UNRESOLVED")),key=lambda x:STATUS_RANK.get(x,-1))
   claims[key]=value
  for item in assessment.get("missing_information",[]):
   key=item.get("request_id") or _stable("REQ",[item.get("document"),item.get("section"),item.get("question") or item.get("description")])
   value={**item,"request_id":key,"related_claim_ids":sorted(set(item.get("related_claim_ids",[]))),"related_evidence_ids":sorted(set(item.get("related_evidence_ids",item.get("related_evidence_refs",[]))))}
   if key in missing:
    value["related_claim_ids"]=sorted(set(missing[key]["related_claim_ids"])|set(value["related_claim_ids"])); value["related_evidence_ids"]=sorted(set(missing[key]["related_evidence_ids"])|set(value["related_evidence_ids"]))
   missing[key]=value
 return {"claims":[claims[k] for k in sorted(claims)],"missing_information":[missing[k] for k in sorted(missing)],"context_package_ids":package_ids,"source_snapshots":snapshots,"evidence_ids":sorted(evidence),"provenance":[p.get("provenance",{}) for p in sorted(packages,key=lambda x:x["package_id"])]}

def evidence_closed(document):
 """Performs evidence closed while preserving this module's deterministic contract."""
 known=set(document.get("evidence_ids",[]))
 return all(set(c.get("evidence_refs",[]))<=known for c in document.get("claims",[])) and all(set(m.get("related_evidence_ids",[]))<=known for m in document.get("missing_information",[]))

def hierarchical_aggregate(global_assessment,global_package,local_assessments,local_packages,coverage):
 """Performs hierarchical aggregate while preserving this module's deterministic contract."""
 local={}
 for assessment,package in zip(local_assessments,local_packages):
  for claim in assessment.get("claims",[]): local["LOCAL-"+package["package_id"][-8:]+"-"+claim["claim_id"]]={"claim":claim,"package_id":package["package_id"],"snapshot":package["source_snapshot"]}
 result=aggregate([global_assessment],[global_package]); leaf={str(r["ref"]) for p in local_packages for r in p.get("records",[])}
 for claim in result["claims"]:
  local_ids=list(claim["evidence_refs"]); refs=set(); packages=set(); snapshots=set()
  for lid in local_ids:
   item=local[lid]; refs.update(item["claim"].get("evidence_refs",[])); packages.add(item["package_id"]); snapshots.add(item["snapshot"])
  claim["local_claim_ids"]=sorted(local_ids); claim["evidence_refs"]=sorted(refs); claim["context_package_ids"]=sorted(packages); claim["source_snapshots"]=sorted(snapshots)
 for item in result["missing_information"]:
  local_ids=list(item["related_evidence_ids"]); item["local_claim_ids"]=sorted(local_ids); item["related_evidence_ids"]=sorted({e for lid in local_ids for e in local[lid]["claim"].get("evidence_refs",[])})
 local_missing=[m for a in local_assessments for m in a.get("missing_information",[])]; merged=aggregate([{"claims":[],"missing_information":local_missing}],local_packages)["missing_information"]
 existing={m["request_id"] for m in result["missing_information"]}; result["missing_information"]+= [m for m in merged if m["request_id"] not in existing]; result["missing_information"].sort(key=lambda x:x["request_id"])
 result["evidence_ids"]=sorted(leaf); result["source_snapshots"]=sorted({p["source_snapshot"] for p in local_packages}); result["context_package_ids"]=sorted(p["package_id"] for p in local_packages); result["coverage_metrics"]=coverage; result["hierarchical_traceability"]={k:{"local_claim_id":v["claim"]["claim_id"],"context_package_id":v["package_id"],"evidence_ids":sorted(v["claim"].get("evidence_refs",[])),"source_snapshot":v["snapshot"]} for k,v in sorted(local.items())}
 return result
