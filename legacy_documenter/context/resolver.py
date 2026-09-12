"""Read-only V3-R2 deterministic context package resolver."""
import hashlib,json
from pathlib import Path

SCHEMA_VERSION="3.1.0"
PACKAGE_TYPES={"SYSTEM","FUNCTIONAL","TECHNICAL","ENTITY","FLOW","DATA_ACCESS"}

class ContextResolver:
 """Provides the cohesive ContextResolver responsibility for this module."""
 def __init__(self, root: str|Path) -> None:
  self.root=Path(root); self.ai=self.root/"ai_context"; self.index=self.root/"index"
  self.system=self._load(self.ai/"SYSTEM_CONTEXT.json"); self.flows=self._load(self.ai/"FUNCTIONAL_FLOWS.json"); self.trace=self._load(self.ai/"TRACEABILITY.json")
  self.paths={x["path_id"]:x for x in self.flows.get("paths",[])}; self.flow_by_id={x["flow_id"]:x for x in self.flows.get("flows",[])}
 def _load(self,path: Path) -> dict:
  if not path.exists(): raise FileNotFoundError(path)
  return json.loads(path.read_text(encoding="utf8"))
 def lookup(self, ref: object) -> dict:
  """Performs lookup while preserving this module's deterministic contract."""
  ref=str(ref); candidates=[]
  for collection in (self.flow_by_id,self.paths,self.trace.get("entry_point_to_flow",{})):
   candidates += [key for key in collection if key.lower()==ref.lower()]
  return {"status":"NOT_FOUND","candidates":[]} if not candidates else {"status":"FOUND" if len(candidates)==1 else "AMBIGUOUS","candidates":sorted(candidates)}
 def resolve(self, package_type: str, scope: dict|None=None, expansion_depth: int=2, limits: dict|None=None) -> dict:
  """Performs resolve while preserving this module's deterministic contract."""
  if package_type not in PACKAGE_TYPES: raise ValueError("invalid package type")
  scope=scope or {}; limits=limits or {}; flow_ids=[]
  if package_type=="FLOW" and scope.get("flow_id") in self.flow_by_id: flow_ids=[scope["flow_id"]]
  elif package_type in {"FUNCTIONAL","SYSTEM","TECHNICAL"}: flow_ids=sorted(self.flow_by_id)[:limits.get("flows",len(self.flow_by_id))]
  path_ids=sorted(pid for fid in flow_ids for pid in self.flow_by_id[fid].get("path_ids",[]))
  truncated=len(flow_ids)<len(self.flow_by_id) and package_type in {"FUNCTIONAL","SYSTEM","TECHNICAL"}
  body={"package_type":package_type,"schema_version":SCHEMA_VERSION,"source_snapshot":self.system["metadata"].get("source_snapshot_sha256"),"scope":scope,"selection_policy":{"requested_scope":scope,"expansion_depth":expansion_depth,"priority_policy":["P0","P1","P2","P3","P4"],"limits":limits,"truncated":truncated,"truncation_reasons":["flow_limit"] if truncated else []},"statistics":{"flow_count":len(flow_ids),"path_count":len(path_ids)},"entities":{"flow_ids":flow_ids},"relationships":{"entry_point_to_flow":{k:v for k,v in self.trace.get("entry_point_to_flow",{}).items() if v in flow_ids}},"flow_refs":flow_ids,"path_refs":path_ids,"data_access_refs":sorted({n for p in path_ids for n in self.paths[p].get("nodes",[]) if n.startswith("DAO-")}),"evidence_refs":sorted({r for p in path_ids for r in self.paths[p].get("evidence_refs",[])}),"unresolved_refs":sorted(p for p in path_ids if self.paths[p].get("terminal_type")=="unresolved_boundary"),"warnings":[],"truncation":{"truncated":truncated},"provenance":{"artifacts":["ai_context/SYSTEM_CONTEXT.json","ai_context/FUNCTIONAL_FLOWS.json","ai_context/TRACEABILITY.json"],"source_snapshot":self.system["metadata"].get("source_snapshot_sha256")}}
  canonical=json.dumps(body,sort_keys=True,separators=(",",":")); body["package_id"]="CTX-"+hashlib.sha256(canonical.encode()).hexdigest(); return body
