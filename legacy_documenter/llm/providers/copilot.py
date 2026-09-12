import asyncio,inspect,json,time
from legacy_documenter.llm import LLMProvider,LLMCapabilities,LLMModelInfo,LLMRequest,LLMResponse,ProviderConfig,Usage,ProviderError,sid

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
  parts=["<system_instruction>",r.system_instruction,"</system_instruction>","<task_instruction>",r.user_instruction,"</task_instruction>","<evidence_policy>",json.dumps(r.metadata.get("evidence_policy",{}),sort_keys=True),"</evidence_policy>","<claim_policy>",json.dumps(r.metadata.get("claim_policy",r.metadata.get("evidence_policy",{})),sort_keys=True),"</claim_policy>","<missing_information_policy>",json.dumps(r.metadata.get("missing_information_policy",{}),sort_keys=True),"</missing_information_policy>","<context>",json.dumps(r.context,sort_keys=True,separators=(",",":"),ensure_ascii=False),"</context>"]
  if schema is not None: parts += ["<output_contract>","Return exactly one strict JSON object only. No Markdown fences, comments, explanation, prefix, suffix, or chain-of-thought. Obey every const, enum, required, and additionalProperties constraint. Claims must cite only record ref values present in context.",json.dumps(schema,sort_keys=True,ensure_ascii=False),"</output_contract>"]
  return "\n".join(parts)
 def generate(self,r: LLMRequest) -> LLMResponse: return asyncio.run(self._generate(r,None))
 def structured_generate(self,r: LLMRequest,schema: dict) -> LLMResponse: return asyncio.run(self._generate(r,schema))
 async def _generate(self,r: LLMRequest,schema: dict|None) -> LLMResponse:
  started=time.perf_counter(); client=None; session=None
  try:
   if self.client_factory: client=self.client_factory()
   else:
    from copilot import CopilotClient
    client=CopilotClient(use_logged_in_user=True)
   await client.start()
   model=self.config.model_id
   if not model:
    models=await client.list_models()
    if not models: return self._error(r,"MODEL_UNAVAILABLE","no Copilot model available",False)
    model=getattr(models[0],"id",None) or getattr(models[0],"model_id",None)
   async def deny(_request):
    """Performs deny while preserving this module's deterministic contract."""
    from copilot.generated.rpc import PermissionDecisionDeniedByRules
    return PermissionDecisionDeniedByRules(rules=[])
   opts=dict(model=model,on_permission_request=deny,tools=[],available_tools=[],enable_file_change_tracking=False,skip_custom_instructions=True,enable_config_discovery=False,enable_on_demand_instruction_discovery=False,enable_file_hooks=False,enable_host_git_operations=False,enable_skills=False,enable_mcp_apps=False,enable_session_store=False)
   session=client.create_session(**opts)
   if inspect.isawaitable(session): session=await session
   event=await session.send_and_wait(self._prompt(r,schema),timeout=self.config.options.get("timeout",60))
   if event is None: return self._error(r,"PROVIDER_ERROR","Copilot returned no assistant response",False)
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
  except TimeoutError: return self._error(r,"TIMEOUT","Copilot request timed out",True)
  except Exception as exc:
   message=str(exc).lower(); code="MODEL_UNAVAILABLE" if "model" in message and any(x in message for x in ("unavailable","not found","invalid","access")) else "PROVIDER_ERROR"
   return self._error(r,code,"Copilot provider request failed",False)
  finally:
   if session is not None:
    try: await session.disconnect()
    except Exception: pass
   if client is not None:
    try: await client.stop()
    except Exception: pass
 def _error(self,r: LLMRequest,code: str,message: str,retryable: bool) -> LLMResponse:
  status="TIMEOUT" if code=="TIMEOUT" else "PROVIDER_ERROR"
  return LLMResponse(r.request_id,sid("RESP",[r.request_id,code]),self.config.provider_id,self.config.model_id or "",status,error=ProviderError(code,message,self.config.provider_id,self.config.model_id or "",retryable))
