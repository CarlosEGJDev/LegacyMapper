import unittest
from legacy_documenter.llm import *
class R4Tests(unittest.TestCase):
 def req(self,**kw): return LLMRequest("TEST","system","user",{"statistics":{"estimated_tokens":10}},"CTX","3.1.0","snap",**kw)
 def test_request_and_fake_determinism(self):
  r=self.req(); p=ProviderRegistry().create(ProviderConfig("FAKE","fake","m",capabilities={"structured_output":True,"context_window":100,"max_output_tokens":50})); self.assertEqual(p.generate(r),p.generate(r)); self.assertEqual(p.generate(r).status,"SUCCESS"); self.assertEqual(p.generate(r).metadata["source_snapshot"],"snap")
 def test_structured_valid_invalid(self):
  c=ProviderConfig("FAKE","f","m",capabilities={"structured_output":True}); self.assertEqual(FakeLLMProvider(c,structured_response={"x":1}).structured_generate(self.req(),{"required":["x"]}).schema_validation_status,"VALID_STRUCTURED_OUTPUT"); self.assertEqual(FakeLLMProvider(c,structured_response={}).structured_generate(self.req(),{"required":["x"]}).status,"INVALID_STRUCTURED_OUTPUT")
 def test_capability_validation(self):
  c=ProviderConfig("FAKE","f","m",capabilities={"context_window":1,"temperature_control":False}); self.assertEqual(FakeLLMProvider(c).generate(self.req()).status,"CONTEXT_TOO_LARGE"); self.assertEqual(FakeLLMProvider(ProviderConfig("FAKE","f","m")).structured_generate(self.req(),{}).status,"UNSUPPORTED_CAPABILITY")
 def test_registry_unknown_and_config_has_no_secret(self):
  with self.assertRaises(ValueError): ProviderRegistry().create(ProviderConfig("CUSTOM","x","m"))
  self.assertNotIn("password",asdict(ProviderConfig("FAKE","f","m","",credential_source="ENVIRONMENT")))
