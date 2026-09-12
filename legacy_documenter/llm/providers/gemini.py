import json,os,urllib.request,urllib.error
from legacy_documenter.llm import LLMProvider,LLMCapabilities,LLMModelInfo,LLMRequest,LLMResponse,ProviderConfig,Usage,ProviderError,sid
class GeminiProvider(LLMProvider):
 """Provides the cohesive GeminiProvider responsibility for this module."""
 def __init__(self,config: ProviderConfig,transport: object=None) -> None: self.config=config; self.transport=transport or self._http
 def capabilities(self) -> LLMCapabilities: return LLMCapabilities(context_window=self.config.context_window,max_output_tokens=self.config.max_output_tokens,structured_output=True,json_mode=True,system_instruction=True,temperature_control=True)
 def model_info(self) -> LLMModelInfo: return LLMModelInfo(self.config.provider_id,self.config.model_id,self.config.model_id,self.config.provider_type,self.capabilities())
 def _credential(self) -> str|None: return os.environ.get(self.config.credential_source or "GEMINI_API_KEY")
 def _http(self,url: str,payload: dict,timeout: int) -> dict:
  req=urllib.request.Request(url,json.dumps(payload).encode(),{"Content-Type":"application/json"}); return json.loads(urllib.request.urlopen(req,timeout=timeout).read())
 def generate(self,r: LLMRequest) -> LLMResponse:
  """Performs generate while preserving this module's deterministic contract."""
  key=self._credential()
  if not key: return self._error(r,"PROVIDER_CONFIGURATION_ERROR","credential unavailable",False)
  payload={"system_instruction":{"parts":[{"text":r.system_instruction}]},"contents":[{"role":"user","parts":[{"text":r.user_instruction},{"text":json.dumps(r.context,sort_keys=True)}]}],"generationConfig":{"temperature":r.temperature or 0,"maxOutputTokens":r.max_output_tokens or self.config.max_output_tokens}}
  try:
   data=self.transport(f"{self.config.endpoint}/models/{self.config.model_id}:generateContent?key={key}",payload,30); text=data["candidates"][0]["content"]["parts"][0]["text"]; u=data.get("usageMetadata",{}); usage=Usage(u.get("promptTokenCount"),u.get("candidatesTokenCount"),u.get("totalTokenCount"),"provider",False)
   return LLMResponse(r.request_id,sid("RESP",[r.request_id,text]),self.config.provider_id,self.config.model_id,"SUCCESS",text,usage=usage,metadata={"context_package_id":r.context_package_id,"source_snapshot":r.source_snapshot})
  except TimeoutError:return self._error(r,"TIMEOUT","provider timeout",True)
  except Exception:return self._error(r,"PROVIDER_ERROR","provider request failed",False)
 def structured_generate(self,r: LLMRequest,schema: dict) -> LLMResponse:
  """Performs structured generate while preserving this module's deterministic contract."""
  out=self.generate(r)
  if out.status!="SUCCESS": return out
  try: value=json.loads(out.content); missing=[k for k in schema.get("required",[]) if k not in value]
  except Exception: value=None; missing=["invalid json"]
  out.parsed_output=value if not missing else None; out.validation_errors=missing; out.schema_validation_status="VALID_STRUCTURED_OUTPUT" if not missing else "INVALID_STRUCTURED_OUTPUT"; out.status="SUCCESS" if not missing else "INVALID_STRUCTURED_OUTPUT"; return out
 def _error(self,r: LLMRequest,code: str,message: str,retryable: bool) -> LLMResponse:
  e=ProviderError(code,message,self.config.provider_id,self.config.model_id,retryable); return LLMResponse(r.request_id,sid("RESP",[r.request_id,code]),self.config.provider_id,self.config.model_id,"TIMEOUT" if code=="TIMEOUT" else "PROVIDER_ERROR",error=e)
