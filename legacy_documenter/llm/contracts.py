from __future__ import annotations

from dataclasses import dataclass,field,asdict
from abc import ABC,abstractmethod
import hashlib,json,math

PURPOSES={"FUNCTIONAL_DOCUMENTATION","TECHNICAL_DOCUMENTATION","ARCHITECTURE_INTERPRETATION","FUNCTIONAL_INTERPRETATION","MISSING_INFORMATION_ANALYSIS","KNOWLEDGE_GENERATION","TEST"}
STATUSES={"SUCCESS","INVALID_REQUEST","CONTEXT_TOO_LARGE","UNSUPPORTED_CAPABILITY","INVALID_STRUCTURED_OUTPUT","PROVIDER_ERROR","TIMEOUT","RATE_LIMITED","CANCELLED","PROVIDER_CONFIGURATION_ERROR"}
def sid(prefix: str,value: object) -> str: return prefix+"-"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
@dataclass
class LLMCapabilities:
 """Provides the cohesive LLMCapabilities responsibility for this module."""
 context_window:int|None=None; max_output_tokens:int|None=None; structured_output:bool=False; json_mode:bool=False; streaming:bool=False; tool_use:bool=False; reasoning:bool=False; system_instruction:bool=True; temperature_control:bool=True
@dataclass
class ProviderCapabilities(LLMCapabilities):
 """Declared limits and identity; no credentials, source or provider SDK types."""
 provider_id:str=""; model_id:str=""; provider_version:str="1.0"
@dataclass
class LLMModelInfo:
 """Provides the cohesive LLMModelInfo responsibility for this module."""
 provider_id:str; model_id:str; display_name:str; provider_type:str; capabilities:LLMCapabilities; metadata:dict=field(default_factory=dict)
@dataclass
class ProviderConfig:
 """Provides the cohesive ProviderConfig responsibility for this module."""
 provider_type:str; provider_id:str; model_id:str; endpoint:str|None=None; context_window:int|None=None; max_output_tokens:int|None=None; capabilities:dict=field(default_factory=dict); options:dict=field(default_factory=dict); credential_source:str|None=None
 timeout_s:float|None=None
 def __post_init__(self) -> None:
  if self.timeout_s is not None and (not isinstance(self.timeout_s,(int,float)) or isinstance(self.timeout_s,bool) or not math.isfinite(self.timeout_s) or self.timeout_s<=0): raise ValueError("invalid provider timeout")
 @property
 def timeout(self) -> float:
  """Explicit timeout_s wins over the historical options.timeout setting."""
  return self.timeout_s if self.timeout_s is not None else self.options.get("timeout",60)
@dataclass
class LLMRequest:
 """Provides the cohesive LLMRequest responsibility for this module."""
 purpose:str; system_instruction:str; user_instruction:str; context:dict; context_package_id:str; context_schema_version:str; source_snapshot:str; temperature:float|None=None; max_output_tokens:int|None=None; structured_output:bool=False; metadata:dict=field(default_factory=dict); request_id:str|None=None
 output_contract:dict|None=None; model_id:str|None=None; timeout_s:float|None=None
 def __post_init__(self) -> None:
  if self.purpose not in PURPOSES: raise ValueError("purpose")
  if not self.request_id: self.request_id=sid("REQ",{k:v for k,v in asdict(self).items() if k!="request_id" and not (k in {"output_contract","model_id","timeout_s"} and v is None)})
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
 """Generic AI interface. Legacy LLM names remain exact aliases.

 `structured_generate` has a local JSON fallback for generate-only providers
 declaring structured support. Native adapters may override it. Unsupported
 structure fails explicitly before any invocation; no automatic text fallback.
 """
 @abstractmethod
 def generate(self,request: LLMRequest) -> LLMResponse: ...
 @abstractmethod
 def capabilities(self) -> LLMCapabilities: ...
 @abstractmethod
 def model_info(self) -> LLMModelInfo: ...
 @property
 def context_window(self) -> int|None: return self.capabilities().context_window
 @property
 def structured_output(self) -> bool: return self.capabilities().structured_output
 def structured_generate(self,request: LLMRequest,schema: dict) -> LLMResponse:
  from dataclasses import replace
  from .validation import validate_structured_response
  if not self.structured_output:
   info=self.model_info()
   return LLMResponse(request.request_id,sid("RESP",[request.request_id,"UNSUPPORTED_CAPABILITY"]),info.provider_id,info.model_id,"UNSUPPORTED_CAPABILITY")
  response=self.generate(replace(request,structured_output=True,output_contract=schema))
  return validate_structured_response(response,schema)
 def close(self) -> None:
  """Idempotent resource release; stateless providers require no work."""
 def __enter__(self): return self
 def __exit__(self,*exc): self.close()

AIProvider = LLMProvider
AIRequest = LLMRequest
AIResponse = LLMResponse
