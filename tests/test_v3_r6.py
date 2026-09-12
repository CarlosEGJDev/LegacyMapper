import unittest,json
from legacy_documenter.llm import *
from legacy_documenter.llm.providers import GeminiProvider
class R6Tests(unittest.TestCase):
 def req(self): return LLMRequest("TEST","sys","user",{"package_id":"CTX"},"CTX","3.1.0","snap",max_output_tokens=20)
 def test_missing_credential_structured_error(self):
  p=GeminiProvider(ProviderConfig("GEMINI","g","model","https://example.invalid",100,50,credential_source="MISSING_TEST_KEY")); r=p.generate(self.req()); self.assertIsInstance(p,LLMProvider); self.assertEqual(r.error.error_code,"PROVIDER_CONFIGURATION_ERROR"); self.assertNotIn("key",json.dumps(asdict(r.error)).lower())
 def test_mapping_response_usage_and_traceability(self):
  transport=lambda u,p,t:{"candidates":[{"content":{"parts":[{"text":"ok"}]}}],"usageMetadata":{"promptTokenCount":2,"candidatesTokenCount":1,"totalTokenCount":3}}
  p=GeminiProvider(ProviderConfig("GEMINI","g","model","endpoint",100,50,credential_source="PATH"),transport); p._credential=lambda:"configured"; r=p.generate(self.req()); self.assertEqual(r.status,"SUCCESS"); self.assertEqual(r.usage.total_tokens,3); self.assertEqual(r.metadata["source_snapshot"],"snap")
 def test_structured_mapping_and_timeout(self):
  p=GeminiProvider(ProviderConfig("GEMINI","g","m","e",100,50),lambda u,p,t:{"candidates":[{"content":{"parts":[{"text":"{\"x\":1}"}]}}]}); p._credential=lambda:"configured"; self.assertEqual(p.structured_generate(self.req(),{"required":["x"]}).schema_validation_status,"VALID_STRUCTURED_OUTPUT")
  p.transport=lambda *a:(_ for _ in ()).throw(TimeoutError()); self.assertEqual(p.generate(self.req()).status,"TIMEOUT")
