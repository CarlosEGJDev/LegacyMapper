import asyncio,inspect,json,re,time
from legacy_documenter.llm import LLMProvider,LLMCapabilities,LLMModelInfo,LLMRequest,LLMResponse,ProviderConfig,Usage,ProviderError,sid,render_request_payload

_SECRET_VALUE_PATTERNS=[re.compile(p,re.IGNORECASE) for p in (
 r"bearer\s+\S+",
 r"(gh|github|copilot_github)?_?token\s*[:=]\s*\S+",
 r"(api[_-]?key|session[_-]?token|oauth[_-]?secret|[a-z0-9_\-]*secret[a-z0-9_\-]*)\s*[:=]\s*\S+",
 r"cookie\s*[:=]\s*\S+",
 r"\bgh[pousr]_[A-Za-z0-9]{10,}\b",
)]
def _sanitize(message: str) -> str:
 """Redacts credential-shaped substrings before a raw exception message is ever persisted."""
 out=message
 for pattern in _SECRET_VALUE_PATTERNS: out=pattern.sub("[REDACTED]",out)
 return out

class CopilotProvider(LLMProvider):
 """Provides the cohesive CopilotProvider responsibility for this module."""
 def __init__(self,config: ProviderConfig,client_factory: object=None) -> None:
  self.config=config
  self.client_factory=client_factory
 def capabilities(self) -> LLMCapabilities:
  """Performs capabilities while preserving this module's deterministic contract."""
  values={"structured_output":True,"json_mode":True,"system_instruction":True,"temperature_control":False}
  values.update(self.config.capabilities)
  return LLMCapabilities(context_window=self.config.context_window,max_output_tokens=self.config.max_output_tokens,**values)
 def model_info(self) -> LLMModelInfo: return LLMModelInfo(self.config.provider_id,self.config.model_id,self.config.model_id,self.config.provider_type,self.capabilities())
 def _prompt(self,r: LLMRequest,schema: dict|None=None) -> str:
  """Delegates to the shared, provider-neutral `render_request_payload` (V4.3-R5).

  The construction itself was moved to `legacy_documenter.llm.core` unchanged
  so the size a caller measures before sending is the size of *this* exact
  string, and so no second copy can drift from it. This method is kept as the
  provider's own entry point (unchanged signature and output).
  """
  return render_request_payload(r,schema)
 def generate(self,r: LLMRequest) -> LLMResponse: return asyncio.run(self._generate(r,None))
 def structured_generate(self,r: LLMRequest,schema: dict) -> LLMResponse: return asyncio.run(self._generate(r,schema))
 async def _generate(self,r: LLMRequest,schema: dict|None) -> LLMResponse:
  started=time.perf_counter(); client=None; session=None; phase="client_init"; attempted_model=self.config.model_id or None
  try:
   if self.client_factory: client=self.client_factory()
   else:
    from copilot import CopilotClient
    client=CopilotClient(use_logged_in_user=True)
   phase="client_start"
   await client.start()
   model=self.config.model_id
   if not model:
    phase="list_models"
    models=await client.list_models()
    if not models: return self._error(r,"MODEL_UNAVAILABLE","no Copilot model available",False,phase=phase,attempted_model=attempted_model)
    model=getattr(models[0],"id",None) or getattr(models[0],"model_id",None)
   attempted_model=model
   async def deny(_request):
    """Performs deny while preserving this module's deterministic contract."""
    from copilot.generated.rpc import PermissionDecisionDeniedByRules
    return PermissionDecisionDeniedByRules(rules=[])
   opts=dict(model=model,on_permission_request=deny,tools=[],available_tools=[],enable_file_change_tracking=False,skip_custom_instructions=True,enable_config_discovery=False,enable_on_demand_instruction_discovery=False,enable_file_hooks=False,enable_host_git_operations=False,enable_skills=False,enable_mcp_apps=False,enable_session_store=False)
   phase="create_session"
   session=client.create_session(**opts)
   if inspect.isawaitable(session): session=await session
   phase="send_and_wait"
   event=await session.send_and_wait(self._prompt(r,schema),timeout=self.config.options.get("timeout",60))
   if event is None: return self._error(r,"PROVIDER_ERROR","Copilot returned no assistant response",False,phase=phase,attempted_model=attempted_model)
   phase="structured_parse"
   data=event.data; content=data.content; actual_model=getattr(data,"model",None) or model
   output_tokens=getattr(data,"output_tokens",None)
   usage=Usage(output_tokens=output_tokens,total_tokens=output_tokens,token_count_method="provider" if output_tokens is not None else "context_estimate",estimated=output_tokens is None,latency_ms=round((time.perf_counter()-started)*1000))
   out=LLMResponse(r.request_id,sid("RESP",[r.request_id,content]),self.config.provider_id,actual_model,"SUCCESS",content,usage=usage,metadata={"context_package_id":r.context_package_id,"source_snapshot":r.source_snapshot,"tool_execution":"DISABLED"})
   if schema is not None:
    try:
     value=json.loads(content); errors=[] if isinstance(value,dict) else ["expected object"]
     errors += ["missing:"+k for k in schema.get("required",[]) if not isinstance(value,dict) or k not in value]
    except Exception: value=None; errors=["invalid json"]
    out.parsed_output=value if not errors else None; out.validation_errors=errors; out.schema_validation_status="VALID_STRUCTURED_OUTPUT" if not errors else "INVALID_STRUCTURED_OUTPUT"
    if errors: out.status="INVALID_STRUCTURED_OUTPUT"
   return out
  except TimeoutError as exc:
   return self._error(r,"TIMEOUT","Copilot request timed out",True,phase=phase,exception_type=type(exc).__name__,attempted_model=attempted_model,raw_message=str(exc))
  except Exception as exc:
   message=str(exc).lower(); code="MODEL_UNAVAILABLE" if "model" in message and any(x in message for x in ("unavailable","not found","invalid","access")) else "PROVIDER_ERROR"
   return self._error(r,code,"Copilot provider request failed",False,phase=phase,exception_type=type(exc).__name__,attempted_model=attempted_model,raw_message=str(exc))
  finally:
   if session is not None:
    try: await session.disconnect()
    except Exception: pass
   if client is not None:
    try: await client.stop()
    except Exception: pass
 def _error(self,r: LLMRequest,code: str,message: str,retryable: bool,*,phase: str|None=None,exception_type: str|None=None,attempted_model: str|None=None,raw_message: str|None=None) -> LLMResponse:
  """Builds a `PROVIDER_ERROR`/`TIMEOUT`/`MODEL_UNAVAILABLE` response, preserving diagnosable-but-safe
  details (V4.3 pre-closure Copilot correction): which phase failed, the exception's type, and the model
  actually attempted -- never a raw, unsanitized exception message."""
  status="TIMEOUT" if code=="TIMEOUT" else "PROVIDER_ERROR"
  model_id=attempted_model or self.config.model_id or ""
  details={}
  if phase is not None: details["phase"]=phase
  if exception_type is not None: details["exception_type"]=exception_type
  if attempted_model: details["attempted_model"]=attempted_model
  if raw_message:
   sanitized=_sanitize(raw_message)
   if sanitized: details["sanitized_message"]=sanitized
  return LLMResponse(r.request_id,sid("RESP",[r.request_id,code]),self.config.provider_id,model_id,status,error=ProviderError(code,message,self.config.provider_id,model_id,retryable,details=details))
