import json,math,hashlib

PROFILES={"TINY":(20,4000),"SMALL":(80,16000),"MEDIUM":(250,50000),"LARGE":(800,160000),"FULL":(10**9,10**9)}
class ContextComposer:
 """Provides the cohesive ContextComposer responsibility for this module."""
 def __init__(self,resolver: object,chars_per_token: int=4) -> None: self.resolver=resolver; self.chars_per_token=chars_per_token
 def compose(self,package_type: str,scope: dict|None=None,profile: str="MEDIUM",expansion_depth: int=2,budget: dict|None=None) -> dict:
  """Performs compose while preserving this module's deterministic contract."""
  if profile not in PROFILES: raise ValueError("profile")
  raw=self.resolver.resolve(package_type,scope,expansion_depth); max_records,max_chars=PROFILES[profile]
  budget=budget or {}; max_records=budget.get("max_records",max_records); max_chars=min(budget.get("max_characters",max_chars),budget.get("max_estimated_tokens",10**18)*self.chars_per_token)
  category_limits={"flow_refs":"max_flows","path_refs":"max_paths","data_access_refs":"max_entities","unresolved_refs":"max_unresolved","evidence_refs":"max_evidence_refs"}
  limited={}; preexcluded=[]
  for key,limit_name in category_limits.items():
   values=raw.get(key,[]); limit=budget.get(limit_name,len(values)); limited[key]=values[:limit]; preexcluded += [{"ref":x,"priority":"P3" if key=="unresolved_refs" else "P4","category":key} for x in values[limit:]]
  records=[]
  for key,priority in [("flow_refs","P0"),("path_refs","P0"),("data_access_refs","P0"),("evidence_refs","P4"),("unresolved_refs","P3")]:
   records += [{"ref":x,"priority":priority,"category":key} for x in limited.get(key,[])]
  records += list(raw.get("priority_records",[]))
  unique=[]; seen=set()
  for r in sorted(records,key=lambda x:(x["priority"],x["category"],str(x["ref"]))):
   if r["ref"] not in seen: seen.add(r["ref"]); unique.append(r)
  chosen=[]; excluded=list(preexcluded); reserve=min(budget.get("reserved_unresolved_records",1),sum(x["priority"]=="P3" for x in unique))
  for r in unique:
   if len(chosen)<max_records-reserve or r["priority"]=="P3": chosen.append(r)
   else: excluded.append(r)
  body={"package_type":package_type,"schema_version":"3.1.0","source_snapshot":raw["source_snapshot"],"scope":scope or {},"selection_policy":raw["selection_policy"]|{"budget_profile":profile,"budget":budget},"entities":raw["entities"],"relationships":raw["relationships"],"records":chosen,"provenance":raw["provenance"],"progressive_level":{"SYSTEM":"L0","TECHNICAL":"L1","ENTITY":"L2","FLOW":"L3","DATA_ACCESS":"L4","FUNCTIONAL":"L5"}[package_type]}
  minimum={**body,"records":[x for x in chosen if x["priority"]=="P0"]}; minimum_chars=len(json.dumps(minimum,sort_keys=True,separators=(",",":")))
  text=json.dumps(body,sort_keys=True,separators=(",",":")); insufficient=minimum_chars>max_chars
  completeness="BUDGET_INSUFFICIENT" if insufficient else ("TRUNCATED" if excluded or len(text)>max_chars else "COMPLETE")
  body["statistics"]={"package_bytes":len(text.encode()),"character_count":len(text),"estimated_tokens":math.ceil(len(text)/self.chars_per_token),"estimation_method":"approximation: ceil(chars/chars_per_token)","chars_per_token":self.chars_per_token,"records_selected":len(records),"records_included":len(chosen),"records_excluded":len(excluded),"deduplicated_records":len(records)-len(unique),"counts_by_priority":{p:sum(x["priority"]==p for x in chosen) for p in ["P0","P1","P2","P3","P4"]},"counts_by_category":{c:sum(x["category"]==c for x in chosen) for c in sorted({x["category"] for x in unique})},"confirmed_reference_count":sum(x["priority"]=="P0" for x in chosen),"unresolved_reference_count":sum(x["priority"]=="P3" for x in chosen),"traceability_reference_count":len(chosen),"flow_count":len(raw.get("flow_refs",[])),"data_access_count":len(raw.get("data_access_refs",[])),"entity_count":len(raw.get("entities",{})),"coverage_by_priority":{p:sum(x["priority"]==p for x in chosen) for p in ["P0","P1","P2","P3","P4"]},"minimum_required_characters":minimum_chars,"budget_profile":profile,"completeness":completeness}
  body["truncation"]={"truncated":completeness!="COMPLETE","excluded_counts":len(excluded),"excluded_by_priority":{p:sum(x["priority"]==p for x in excluded) for p in ["P0","P1","P2","P3","P4"]},"continuation_refs":[x["ref"] for x in excluded]}
  canon=json.dumps(body,sort_keys=True,separators=(",",":")); body["package_id"]="CTX-"+hashlib.sha256(canon.encode()).hexdigest(); return body
