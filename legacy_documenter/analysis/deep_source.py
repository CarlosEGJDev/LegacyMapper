"""Reusable deterministic deep-source analysis for human NEEDS_ANALYSIS items."""
from dataclasses import asdict, dataclass
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil

from legacy_documenter.main import analyze_repository
from legacy_documenter.utils import sanitize_data, sanitize_text


STATUSES={"CONFIRMED","PARTIAL","AMBIGUOUS","UNRESOLVED"}
TARGETS={
 "FMI-001":"LLM_INTERPRETATION","FMI-002":"DETERMINISTIC_DISCOVERY","FMI-003":"DETERMINISTIC_DISCOVERY",
 "FMI-004":"DETERMINISTIC_DISCOVERY","FMI-005":"DETERMINISTIC_DISCOVERY","FMI-006":"DETERMINISTIC_DISCOVERY",
 "FMI-007":"LLM_INTERPRETATION","FMI-008":"LLM_INTERPRETATION",
 "TMI-001":"LLM_INTERPRETATION","TMI-002":"LLM_INTERPRETATION","TMI-003":"DETERMINISTIC_DISCOVERY",
 "TMI-004":"DETERMINISTIC_DISCOVERY","TMI-005":"DETERMINISTIC_DISCOVERY","TMI-006":"LLM_INTERPRETATION",
 "TMI-007":"DETERMINISTIC_DISCOVERY","TMI-008":"DETERMINISTIC_DISCOVERY","TMI-009":"LLM_INTERPRETATION",
 "TMI-010":"DETERMINISTIC_DISCOVERY","TMI-011":"LLM_INTERPRETATION","TMI-012":"DETERMINISTIC_DISCOVERY",
}
INTEGRATION_RE=re.compile(r"\b(SAP|SOAP|WCF|HttpClient|WebRequest|WebService|ServiceReference|SMTP|MailMessage|MSMQ|MessageQueue|FTP|SFTP|COM)\b",re.I)
SECRET_RE=re.compile(r"(?i)(password|pwd|token|secret|user\s*id|uid)\s*[:=]\s*[^\s;,\"']+")


@dataclass(frozen=True)
class DeepEvidence:
 """Provides the cohesive DeepEvidence responsibility for this module."""
 evidence_id:str; evidence_type:str; source_file:str; source_project:str|None; symbol:str|None
 relationship_type:str; resolution_status:str; provenance:dict; source_snapshot:str
 def to_dict(self): return asdict(self)


def stable_id(prefix,value):
 """Performs stable id while preserving this module's deterministic contract."""
 return prefix+"-"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:16]


def tree_snapshot(root):
 """Performs tree snapshot while preserving this module's deterministic contract."""
 root=Path(root).resolve(); h=hashlib.sha256(); count=0
 for p in sorted((x for x in root.rglob("*") if x.is_file()),key=lambda x:str(x).lower()):
  s=p.stat(); h.update(str(p.relative_to(root)).replace("\\","/").encode()); h.update(f"{s.st_size}:{s.st_mtime_ns}".encode()); count+=1
 return {"root":str(root),"file_count":count,"metadata_hash":h.hexdigest()}


def plan_requests():
 """Performs plan requests while preserving this module's deterministic contract."""
 return [{"target_missing_information_id":k,"strategy":v} for k,v in sorted(TARGETS.items())]


def project_dependencies(projects,snapshot):
 """Performs project dependencies while preserving this module's deterministic contract."""
 project_paths={str(x.get("path","")).replace("\\","/").lower():x for x in projects}; result=[]
 for project in projects:
  base=Path(project["path"]).parent
  for ref in project.get("project_references",[]):
   target=str((base/str(ref.get("include","")).replace("\\","/")).as_posix())
   normalized=posixpath.normpath(target).lower()
   matches=[p["path"] for key,p in project_paths.items() if key==normalized]
   status="CONFIRMED" if len(matches)==1 else "AMBIGUOUS" if len(matches)>1 else "UNRESOLVED"
   value={"source_project":project["path"],"target":matches[0] if len(matches)==1 else ref.get("include"),"name":ref.get("name"),"project_guid":ref.get("project"),"relationship_type":"PROJECT_REFERENCE","resolution_status":status,"source_snapshot":snapshot}
   value["evidence_id"]=stable_id("DEEP-PROJ",value); result.append(value)
 return sorted(result,key=lambda x:x["evidence_id"])


def external_dependencies(projects,snapshot):
 """Performs external dependencies while preserving this module's deterministic contract."""
 result=[]
 for project in projects:
  for ref in project.get("assembly_references",[]):
   include=ref.get("include") or ""; name,_,metadata=include.partition(",")
   version=re.search(r"Version=([^,]+)",metadata,re.I)
   value={"source_project":project["path"],"assembly":name.strip(),"version":version.group(1) if version else None,"hint_path":sanitize_text(ref.get("hint_path") or "") or None,"relationship_type":"ASSEMBLY_REFERENCE","resolution_status":"CONFIRMED","source_snapshot":snapshot}
   value["evidence_id"]=stable_id("DEEP-ASM",value); result.append(value)
 return sorted(result,key=lambda x:x["evidence_id"])


def integration_evidence(root,files,snapshot,max_items=5000):
 """Performs integration evidence while preserving this module's deterministic contract."""
 allowed={"vb_source","web_config","aspx","ascx"}; result=[]
 for item in files:
  if item.get("file_type") not in allowed: continue
  path=Path(root)/item["relative_path"]
  for line_no,line in enumerate(path.read_text(encoding="utf-8",errors="replace").splitlines(),1):
   found=sorted({x.upper() for x in INTEGRATION_RE.findall(line)})
   if not found: continue
   excerpt=SECRET_RE.sub(lambda m:m.group(1)+"=********",sanitize_text(line.strip()))[:500]
   value={"source_file":item["relative_path"],"line":line_no,"indicators":found,"excerpt":excerpt,"resolution_status":"CONFIRMED","source_snapshot":snapshot}
   value["evidence_id"]=stable_id("DEEP-INT",value); result.append(value)
   if len(result)>=max_items: return sorted(result,key=lambda x:x["evidence_id"])
 return sorted(result,key=lambda x:x["evidence_id"])


def web_entry_evidence(webforms,entry_points,event_bindings,snapshot):
 """Performs web entry evidence while preserving this module's deterministic contract."""
 by_form={x["path"]:x for x in webforms}; result=[]
 for entry in entry_points:
  form=by_form.get(entry.get("webform"),{})
  value={"evidence_id":entry["id"],"webform":entry.get("webform"),"kind":form.get("kind"),"codebehind":form.get("codebehind") or form.get("codefile"),"inherits":form.get("inherits"),"event":entry.get("event"),"handler":entry.get("handler"),"start_method":entry.get("start_method"),"resolution_status":"CONFIRMED" if entry.get("start_method") else "UNRESOLVED","source_snapshot":snapshot}
  result.append(value)
 return sorted(result,key=lambda x:x["evidence_id"])


def architecture_evidence(indexes,project_deps,external,snapshot):
 """Performs architecture evidence while preserving this module's deterministic contract."""
 refs=[x.get("assembly","") for x in external]; mvc=sorted(x for x in refs if "system.web.mvc" in x.lower())
 indicators=[
  {"indicator":"WEBFORMS_USAGE","count":len(indexes["webforms"]),"status":"SUPPORTED" if indexes["webforms"] else "INSUFFICIENT_EVIDENCE"},
  {"indicator":"PROJECT_REFERENCE_DIRECTION","count":len(project_deps),"status":"SUPPORTED" if project_deps else "INSUFFICIENT_EVIDENCE"},
  {"indicator":"DATA_ACCESS_OPERATIONS","count":len(indexes["data_access"]),"status":"SUPPORTED" if indexes["data_access"] else "INSUFFICIENT_EVIDENCE"},
  {"indicator":"MVC_FRAMEWORK_REFERENCE","count":len(mvc),"status":"SUPPORTED" if mvc else "INSUFFICIENT_EVIDENCE"},
 ]
 return {"source_snapshot":snapshot,"DETERMINISTIC_INDICATORS":indicators,"LLM_INTERPRETATION":{"status":"NOT_EXECUTED","candidate_conclusion":"INSUFFICIENT_EVIDENCE"},"CONTRADICTING_EVIDENCE":[],"UNRESOLVED_EVIDENCE":["Formal architecture cannot be confirmed from structural indicators alone."],"pattern_confirmed":False}


def reevaluate(evidence_counts):
 """Performs reevaluate while preserving this module's deterministic contract."""
 result=[]
 for target,strategy in sorted(TARGETS.items()):
  if strategy=="LLM_INTERPRETATION": status="REQUIRES_LLM_INTERPRETATION"; ids=evidence_counts.get("semantic",[])
  elif target in {"FMI-002","FMI-004","FMI-005","TMI-003","TMI-007"}: status="PARTIALLY_RESOLVED"; ids=evidence_counts.get("flows",[])
  elif target in {"FMI-003","FMI-006","TMI-004","TMI-008","TMI-010","TMI-012"}: status="PARTIALLY_RESOLVED"; ids=evidence_counts.get("external",[])
  elif target=="TMI-005": status="RESOLVED_BY_DETERMINISTIC_EVIDENCE" if evidence_counts.get("projects") else "STILL_UNRESOLVED"; ids=evidence_counts.get("projects",[])
  else: status="STILL_UNRESOLVED"; ids=[]
  if status in {"RESOLVED_BY_DETERMINISTIC_EVIDENCE","PARTIALLY_RESOLVED","REQUIRES_LLM_INTERPRETATION"} and not ids: status="STILL_UNRESOLVED"
  result.append({"target_missing_information_id":target,"original_disposition":"NEEDS_ANALYSIS","analysis_strategy":strategy,"reevaluation_status":status,"evidence_ids":ids[:100]})
 return result


def run(source_root,output_dir):
 """Performs run while preserving this module's deterministic contract."""
 source=Path(source_root).resolve(); output=Path(output_dir).resolve()
 if not source.is_dir(): raise ValueError("SOURCE_ROOT_NOT_FOUND")
 output.mkdir(parents=True,exist_ok=True); before=tree_snapshot(source); scratch=output/"_runtime_scan"
 required=("repository","files","projects","calls","entry_points","event_bindings","data_access","stored_procedures","data_parameters","functional_flows","functional_paths","flow_unresolved","webforms","errors")
 if all((scratch/"index"/(name+".json")).exists() for name in required):
  indexes={name:json.loads((scratch/"index"/(name+".json")).read_text(encoding="utf-8")) for name in required}
 else:
  indexes=analyze_repository(source,scratch,flow_max_depth=20)
 snapshot=indexes["repository"].get("root","")+":"+before["metadata_hash"]
 projects=project_dependencies(indexes["projects"],snapshot); external=external_dependencies(indexes["projects"],snapshot)
 integrations=integration_evidence(source,indexes["files"],snapshot); entries=web_entry_evidence(indexes["webforms"],indexes["entry_points"],indexes["event_bindings"],snapshot)
 deep_evidence={"schema_version":"3.2.0","source_snapshot":snapshot,"web_entries":entries,"calls":indexes["calls"],"data_access":indexes["data_access"],"stored_procedures":indexes["stored_procedures"],"parameters":indexes["data_parameters"],"integrations":integrations}
 flows={"schema_version":"3.2.0","flows":indexes["functional_flows"],"paths":indexes["functional_paths"],"unresolved":indexes["flow_unresolved"]}
 architecture=architecture_evidence(indexes,projects,external,snapshot)
 ids={"projects":[x["evidence_id"] for x in projects],"external":[x["evidence_id"] for x in external+integrations],"flows":[x["path_id"] for x in indexes["functional_paths"]],"semantic":[x["path_id"] for x in indexes["functional_paths"]]+[x["evidence_id"] for x in integrations]}
 reevaluation=reevaluate(ids); after=tree_snapshot(source)
 summary={"status":"V3-R8_1_DEEP_SOURCE_ANALYSIS_COMPLETE","runtime_entry_point":"legacy_documenter.analysis.deep_source.run","source_root":str(source),"source_before":before,"source_after":after,"source_immutable":before==after,"analysis_targets":plan_requests(),"counts":{"files":len(indexes["files"]),"webforms":len(indexes["webforms"]),"entry_points":len(entries),"calls":len(indexes["calls"]),"project_dependencies":len(projects),"external_dependencies":len(external),"integrations":len(integrations),"data_access":len(indexes["data_access"]),"stored_procedures":len(indexes["stored_procedures"]),"flows":len(indexes["functional_flows"]),"paths":len(indexes["functional_paths"]),"errors":len(indexes["errors"])},"reevaluation":dict(Counter(x["reevaluation_status"] for x in reevaluation)),"real_llm_calls":0,"effective_provider":None,"effective_model":None,"model_change_recommended":False,"ai_knowledge_allowed":False}
 outputs={"DEEP_ANALYSIS_SUMMARY.json":summary,"DEEP_ANALYSIS_EVIDENCE.json":deep_evidence,"DEEP_ANALYSIS_FLOWS.json":flows,"PROJECT_DEPENDENCIES.json":{"dependencies":projects},"EXTERNAL_DEPENDENCIES.json":{"assemblies":external,"integrations":integrations},"ARCHITECTURE_EVIDENCE.json":architecture,"MISSING_INFORMATION_REEVALUATION.json":{"items":reevaluation}}
 for name,value in outputs.items(): (output/name).write_text(json.dumps(sanitize_data(value),ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
 shutil.rmtree(scratch,ignore_errors=True)
 return summary


def main(argv=None):
 """Performs main while preserving this module's deterministic contract."""
 parser=argparse.ArgumentParser(); parser.add_argument("source_root"); parser.add_argument("--output",default="output/v3_r8_1"); args=parser.parse_args(argv); print(json.dumps(run(args.source_root,args.output),ensure_ascii=False,sort_keys=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
