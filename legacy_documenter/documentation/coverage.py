"""Deterministic systematic coverage planning over existing V2 artifacts."""
from collections import Counter
from pathlib import Path
import hashlib,json,math

DIMENSIONS=("PROJECTS","SOLUTIONS","WEBFORMS","FUNCTIONAL_FLOWS","DATA_ACCESS","STORED_PROCEDURES","UNRESOLVED_BOUNDARIES")
def _chunks(values,count):
 values=list(values); size=max(1,math.ceil(len(values)/count)); return [values[i:i+size] for i in range(0,len(values),size)]
def _uid(category,index,value): return "COV-%s-%02d-%s"%(category,index,hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()[:10])

class CoveragePlanner:
 """Provides the cohesive CoveragePlanner responsibility for this module."""
 def __init__(self,root):
  self.root=Path(root); self.ai=self.root/"ai_context"; self.index=self.root/"index"
  self.system=self._load(self.ai/"SYSTEM_CONTEXT.json"); self.flows=self._load(self.ai/"FUNCTIONAL_FLOWS.json")
  self.data=self._load(self.index/"data_access.json"); self.procedures=self._load(self.index/"stored_procedures.json"); self.unresolved=self._load(self.index/"flow_unresolved.json")
 def _load(self,path): return json.loads(path.read_text(encoding="utf-8"))
 @property
 def snapshot(self): return self.system["metadata"]["source_snapshot_sha256"]
 def _project_states(self):
  data_projects={x.get("project") for x in self.data}; flow_projects={p for f in self.flows.get("flows",[]) for p in f.get("projects",[]) if p}; web_paths=[x.get("path","").lower() for x in self.system.get("web",{}).get("webforms",[])]
  result=[]
  for p in sorted(self.system.get("projects",[]),key=lambda x:(x.get("path") or "",x.get("name") or "")):
   name=p.get("name") or Path(p.get("path","")).stem; path=p.get("path",""); linked=name in data_projects or path in data_projects or any(name.lower() in x for x in web_paths) or name in flow_projects or path in flow_projects
   refs=bool(p.get("project_references") or p.get("assembly_references")); state="COVERED" if linked else "PARTIALLY_COVERED" if refs else "NO_USABLE_EVIDENCE"
   result.append({"id":path or name,"name":name,"state":state,"project_references":len(p.get("project_references") or []),"assembly_references":len(p.get("assembly_references") or [])})
  return result
 def _unit(self,category,index,fact,priority="P1"): return {"unit_id":_uid(category,index,fact),"category":category,"priority":priority,"fact":fact,"provenance":{"artifact":"V2-R5.1","deterministic":True}}
 def plan(self):
  """Performs plan while preserving this module's deterministic contract."""
  projects=self._project_states(); forms=sorted(self.system.get("web",{}).get("webforms",[]),key=lambda x:x.get("path", "")); flows=sorted(self.flows.get("flows",[]),key=lambda x:x.get("flow_id","")); solutions=sorted(self.system.get("solutions",[]),key=lambda x:x.get("path",""))
  units=[]
  for i,g in enumerate(_chunks(projects,33)): units.append(self._unit("PROJECTS",i,{"projects":[{k:x[k] for k in ("name","state","project_references","assembly_references")} for x in g],"count":len(g)},"P0"))
  for category,values,groups,fields in (("SOLUTIONS",solutions,10,("name","path")),("WEBFORMS",forms,10,("id","path","type","entry_point_ids")),("FUNCTIONAL_FLOWS",flows,10,("flow_id","entry_point_id","projects","confidence","status","path_ids"))):
   for i,g in enumerate(_chunks(values,groups)):
    items=[]
    for x in g[:8]:
     item={k:x.get(k) for k in fields if k not in ("entry_point_ids","path_ids")}
     if "entry_point_ids" in fields: item["entry_point_count"]=len(x.get("entry_point_ids") or []); item["entry_point_ids"]=(x.get("entry_point_ids") or [])[:3]
     if "path_ids" in fields: item["path_count"]=len(x.get("path_ids") or []); item["path_ids"]=(x.get("path_ids") or [])[:3]
     items.append(item)
    units.append(self._unit(category,i,{"count":len(g),"items":items},"P1"))
  for category,values,groups,fields in (("DATA_ACCESS",sorted(self.data,key=lambda x:x.get("id","")),10,("id","operation_kind","access_kind","provider","stored_procedure","sql_operation","class","method","project","confidence")),("STORED_PROCEDURES",sorted(self.procedures,key=lambda x:x.get("id","")),8,("id","name","package","procedure","confidence"))):
   for i,g in enumerate(_chunks(values,groups)): units.append(self._unit(category,i,{"count":len(g),"representatives":[{k:x.get(k) for k in fields} for x in g[:5]],"linked_count":sum(bool(x.get("project") or x.get("evidence")) for x in g)},"P1"))
  classified=Counter(); samples={}
  for x in self.unresolved:
   target=(x.get("terminal_target") or "").lower(); project_sequence=x.get("project_sequence") or []
   kind="UI_BINDING" if "databind" in target else "FRAMEWORK_CALL" if "initializecomponent" in target else "DATA_BOUNDARY" if any(t in target for t in ("sql","exec","query")) else "CROSS_PROJECT_UNRESOLVED" if len(set(project_sequence))>1 else "LOCAL_CALL_UNRESOLVED" if len(set(project_sequence))==1 else "UNKNOWN"
   classified[kind]+=1; samples.setdefault(kind,[])
   if len(samples[kind])<5: samples[kind].append({k:(x.get(k) or [])[:3] if k=="evidence_refs" else x.get(k) for k in ("flow_id","path_id","entry_point_id","terminal_target","evidence_refs")})
  for i,kind in enumerate(sorted(classified)): units.append(self._unit("UNRESOLVED_BOUNDARIES",i,{"classification":kind,"count":classified[kind],"representatives":samples[kind]},"P2"))
  states=Counter(x["state"] for x in projects); metrics={"total_projects":len(projects),"covered_projects":states["COVERED"],"partially_covered_projects":states["PARTIALLY_COVERED"],"projects_without_usable_evidence":states["NO_USABLE_EVIDENCE"],"unresolved_ownership_projects":states["UNRESOLVED_OWNERSHIP"],"total_solutions":len(solutions),"represented_solutions":len(solutions),"total_webforms":len(forms),"represented_webforms":len(forms),"total_flows":len(flows),"represented_flows":len(flows),"total_data_operations":len(self.data),"linked_data_operations":sum(bool(x.get("project") and x.get("method")) for x in self.data),"total_stored_procedures":len(self.procedures),"linked_stored_procedures":sum(bool(x.get("evidence")) for x in self.procedures),"unresolved_relationships":len(self.unresolved),"represented_unresolved_relationships":sum(classified.values()),"structural_coverage":{"projects_classified":len(projects),"categories_inventory":list(DIMENSIONS)},"interpretation_coverage":{"units_planned":len(units),"semantic_coverage_percent":None},"priority_counts":dict(sorted(Counter(x["priority"] for x in units).items()))}
  units=sorted(units,key=lambda x:(x["priority"],x["category"],x["unit_id"])); return {"snapshot":self.snapshot,"projects":projects,"units":units,"metrics":metrics,"v2_lookup_completed":True}
 def batches(self,plan,count=3,max_records=35):
  """Performs batches while preserving this module's deterministic contract."""
  p0=[x for x in plan["units"] if x["priority"]=="P0"]; other=[x for x in plan["units"] if x["priority"]!="P0"]
  buckets=[[] for _ in range(count)]
  for i,u in enumerate(p0+other): buckets[i%count].append(u)
  if any(len(x)>max_records for x in buckets): raise ValueError("BUDGET_INSUFFICIENT")
  return buckets
