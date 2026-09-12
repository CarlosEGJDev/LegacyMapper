import json,unittest
from types import SimpleNamespace
from legacy_documenter.llm import LLMProvider,LLMRequest,ProviderConfig,ProviderRegistry
from legacy_documenter.llm.providers.copilot import CopilotProvider

class Session:
 def __init__(self,content='{"assessment_id":"A","claims":[]} ',error=None,usage=4): self.content=content; self.error=error; self.usage=usage; self.prompt=None
 async def send_and_wait(self,prompt,timeout=60):
  self.prompt=prompt
  if self.error: raise self.error
  return SimpleNamespace(data=SimpleNamespace(content=self.content,model="test-model",output_tokens=self.usage))
 async def disconnect(self): pass
class Client:
 def __init__(self,session=None,models=None): self.session=session or Session(); self.models=models or []; self.options=None
 async def start(self): pass
 async def stop(self): pass
 async def list_models(self): return self.models
 def create_session(self,**options): self.options=options; return self.session
class AsyncClient(Client):
 async def create_session(self,**options): self.options=options; return self.session
def request(): return LLMRequest("TEST","SYS","TASK",{"records":[{"ref":"E1"}]},"P1","3.1.0","S1",structured_output=True,metadata={"evidence_policy":{"confirmed_requires_authoritative":True},"missing_information_policy":{"report_insufficient":True}})
def config(model="test-model"): return ProviderConfig("COPILOT","copilot-local",model,capabilities={})

class CopilotProviderTests(unittest.TestCase):
 def test_implements_and_registry(self):
  self.assertIsInstance(CopilotProvider(config(),lambda:Client()),LLMProvider)
  self.assertIsInstance(ProviderRegistry().create(config(),client_factory=lambda:Client()),CopilotProvider)
 def test_no_credentials_and_mapping(self):
  c=Client(); p=CopilotProvider(config(),lambda:c); out=p.generate(request())
  self.assertEqual(out.content,c.session.content); self.assertEqual(out.model_id,"test-model")
  self.assertIn("<system_instruction>\nSYS",c.session.prompt); self.assertIn("<task_instruction>\nTASK",c.session.prompt); self.assertIn('"ref":"E1"',c.session.prompt)
  self.assertFalse(any("credential" in key.lower() or "token" in key.lower() for key in c.options)); self.assertEqual(c.options["model"],"test-model")
 def test_tools_and_permissions_disabled(self):
  c=Client(); CopilotProvider(config(),lambda:c).generate(request())
  self.assertEqual(c.options["tools"],[]); self.assertEqual(c.options["available_tools"],[]); self.assertFalse(c.options["enable_host_git_operations"]); self.assertTrue(callable(c.options["on_permission_request"]))
 def test_structured_valid_invalid_and_usage(self):
  c=Client(Session(usage=7)); out=CopilotProvider(config(),lambda:c).structured_generate(request(),{"required":["assessment_id","claims"]})
  self.assertEqual(out.schema_validation_status,"VALID_STRUCTURED_OUTPUT"); self.assertEqual(out.usage.output_tokens,7); self.assertFalse(out.usage.estimated)
  bad=CopilotProvider(config(),lambda:Client(Session("not json",usage=None))).structured_generate(request(),{"required":["claims"]})
  self.assertEqual(bad.status,"INVALID_STRUCTURED_OUTPUT"); self.assertTrue(bad.usage.estimated)
 def test_error_and_model_unavailable(self):
  out=CopilotProvider(config(),lambda:Client(Session(error=RuntimeError("service failed")))).generate(request())
  self.assertEqual(out.error.error_code,"PROVIDER_ERROR")
  out=CopilotProvider(config(),lambda:Client(Session(error=RuntimeError("model unavailable")))).generate(request())
  self.assertEqual(out.error.error_code,"MODEL_UNAVAILABLE")
 def test_model_discovery(self):
  c=Client(models=[SimpleNamespace(id="discovered")]); out=CopilotProvider(config(""),lambda:c).generate(request())
  self.assertEqual(c.options["model"],"discovered"); self.assertEqual(out.model_id,"test-model")
 def test_async_session_creation(self):
  c=AsyncClient(); out=CopilotProvider(config(),lambda:c).generate(request())
  self.assertEqual(out.status,"SUCCESS"); self.assertIsNotNone(c.session.prompt)

if __name__=="__main__": unittest.main()
