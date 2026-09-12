from __future__ import annotations

from dataclasses import dataclass,field,asdict
from abc import ABC,abstractmethod
import hashlib,json

PURPOSES={"FUNCTIONAL_DOCUMENTATION","TECHNICAL_DOCUMENTATION","ARCHITECTURE_INTERPRETATION","FUNCTIONAL_INTERPRETATION","MISSING_INFORMATION_ANALYSIS","KNOWLEDGE_GENERATION","TEST"}
STATUSES={"SUCCESS","INVALID_REQUEST","CONTEXT_TOO_LARGE","UNSUPPORTED_CAPABILITY","INVALID_STRUCTURED_OUTPUT","PROVIDER_ERROR","TIMEOUT","RATE_LIMITED","CANCELLED"}
def sid(prefix: str,value: object) -> str: return prefix+"-"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
@dataclass
class LLMCapabilities:
 """Provides the cohesive LLMCapabilities responsibility for this module."""
 context_window:int|None=None; max_output_tokens:int|None=None; structured_output:bool=False; json_mode:bool=False; streaming:bool=False; tool_use:bool=False; reasoning:bool=False; system_instruction:bool=True; temperature_control:bool=True
@dataclass
class LLMModelInfo:
 """Provides the cohesive LLMModelInfo responsibility for this module."""
 provider_id:str; model_id:str; display_name:str; provider_type:str; capabilities:LLMCapabilities; metadata:dict=field(default_factory=dict)
@dataclass
class ProviderConfig:
 """Provides the cohesive ProviderConfig responsibility for this module."""
 provider_type:str; provider_id:str; model_id:str; endpoint:str|None=None; context_window:int|None=None; max_output_tokens:int|None=None; capabilities:dict=field(default_factory=dict); options:dict=field(default_factory=dict); credential_source:str|None=None
@dataclass
class LLMRequest:
 """Provides the cohesive LLMRequest responsibility for this module."""
 purpose:str; system_instruction:str; user_instruction:str; context:dict; context_package_id:str; context_schema_version:str; source_snapshot:str; temperature:float|None=None; max_output_tokens:int|None=None; structured_output:bool=False; metadata:dict=field(default_factory=dict); request_id:str|None=None
 def __post_init__(self) -> None:
  if self.purpose not in PURPOSES: raise ValueError("purpose")
  if not self.request_id: self.request_id=sid("REQ",{k:v for k,v in asdict(self).items() if k!="request_id"})
@dataclass
class Usage:
 """Provides the cohesive Usage responsibility for this module."""
 input_tokens:int|None=None; output_tokens:int|None=None; total_tokens:int|None=None; token_count_method:str|None=None; estimated:bool=False; latency_ms:int|None=None
@dataclass
class ProviderError:
 """Provides the cohesive ProviderError responsibility for this module."""
 error_code:str; message:str; provider_id:str; model_id:str; retryable:bool=False; details:dict=field(default_factory=dict)
@dataclass
class LLMResponse:
 """Provides the cohesive LLMResponse responsibility for this module."""
 request_id:str; response_id:str; provider_id:str; model_id:str; status:str; content:str|None=None; finish_reason:str|None=None; usage:Usage|None=None; warnings:list=field(default_factory=list); metadata:dict=field(default_factory=dict); parsed_output:object=None; schema_validation_status:str="RAW_TEXT"; validation_errors:list=field(default_factory=list); error:ProviderError|None=None
class LLMProvider(ABC):
 """Provides the cohesive LLMProvider responsibility for this module."""
 @abstractmethod
 def generate(self,request: LLMRequest) -> LLMResponse: ...
 @abstractmethod
 def capabilities(self) -> LLMCapabilities: ...
 @abstractmethod
 def model_info(self) -> LLMModelInfo: ...
class FakeLLMProvider(LLMProvider):
 """Provides the cohesive FakeLLMProvider responsibility for this module."""
 def __init__(self,config: ProviderConfig,fixed_response: str="ok",structured_response: object=None,forced_status: str|None=None) -> None: self.config=config; self.fixed=fixed_response; self.structured=structured_response; self.forced=forced_status
 def capabilities(self) -> LLMCapabilities: return LLMCapabilities(**self.config.capabilities)
 def model_info(self) -> LLMModelInfo: return LLMModelInfo(self.config.provider_id,self.config.model_id,self.config.model_id,self.config.provider_type,self.capabilities())
 def _status(self,r: LLMRequest) -> str:
  c=self.capabilities(); est=(r.context.get("statistics") or {}).get("estimated_tokens",0)
  if r.structured_output and not c.structured_output:return "UNSUPPORTED_CAPABILITY"
  if c.context_window and est>c.context_window:return "CONTEXT_TOO_LARGE"
  if c.max_output_tokens and r.max_output_tokens and r.max_output_tokens>c.max_output_tokens:return "INVALID_REQUEST"
  if r.temperature is not None and not c.temperature_control:return "UNSUPPORTED_CAPABILITY"
  return self.forced or "SUCCESS"
 def generate(self,r: LLMRequest) -> LLMResponse:
  """Performs generate while preserving this module's deterministic contract."""
  status=self._status(r); content=self.fixed if status=="SUCCESS" else None; rid=sid("RESP",[r.request_id,self.config.provider_id,self.config.model_id,content,status]); return LLMResponse(r.request_id,rid,self.config.provider_id,self.config.model_id,status,content,usage=Usage(estimated=True,token_count_method="context_estimate"),metadata={"context_package_id":r.context_package_id,"source_snapshot":r.source_snapshot})
 def structured_generate(self,r: LLMRequest,schema: dict) -> LLMResponse:
  """Performs structured generate while preserving this module's deterministic contract."""
  r.structured_output=True; out=self.generate(r)
  if out.status!="SUCCESS": return out
  value=self.structured
  errors=[]
  if not isinstance(value,dict): errors=["expected object"]
  for key in schema.get("required",[]):
   if not isinstance(value,dict) or key not in value: errors.append("missing:"+key)
  out.parsed_output=value if not errors else None; out.validation_errors=errors; out.schema_validation_status="VALID_STRUCTURED_OUTPUT" if not errors else "INVALID_STRUCTURED_OUTPUT"
  if errors: out.status="INVALID_STRUCTURED_OUTPUT"
  return out
class ProviderRegistry:
 """Provides the cohesive ProviderRegistry responsibility for this module."""
 def create(self,config: ProviderConfig,**kwargs: object) -> LLMProvider:
  """Performs create while preserving this module's deterministic contract."""
  if config.provider_type=="FAKE": return FakeLLMProvider(config,**kwargs)
  if config.provider_type=="COPILOT":
   from .providers.copilot import CopilotProvider
   return CopilotProvider(config,**kwargs)
  raise ValueError("unknown provider")
