import json,tempfile,unittest
from pathlib import Path
from legacy_documenter.context.resolver import ContextResolver,PACKAGE_TYPES
from legacy_documenter.context.composer import ContextComposer

class FakeResolver:
 def resolve(self,kind,scope,depth):
  return {"source_snapshot":"snap","selection_policy":{"expansion_depth":depth},"entities":{"flow_ids":["F"]},"relationships":{"r":["x"]},"flow_refs":[f"F{i}" for i in range(400)],"path_refs":[f"P{i}" for i in range(400)],"data_access_refs":[f"DAO-{i}" for i in range(100)],"evidence_refs":[f"E{i}" for i in range(100)],"unresolved_refs":[f"U{i}" for i in range(20)],"priority_records":[{"ref":"P1-A","priority":"P1","category":"support"},{"ref":"P2-A","priority":"P2","category":"structure"}],"provenance":{"artifacts":["index/x.json"],"source_snapshot":"snap"}}

class ContextResolverTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); (root/"ai_context").mkdir(); (root/"index").mkdir()
  (root/"ai_context"/"SYSTEM_CONTEXT.json").write_text(json.dumps({"metadata":{"source_snapshot_sha256":"snap"}}))
  (root/"ai_context"/"FUNCTIONAL_FLOWS.json").write_text(json.dumps({"flows":[{"flow_id":"F1","path_ids":["P1"]}],"paths":[{"path_id":"P1","nodes":["DAO-1"],"terminal_type":"unresolved_boundary","evidence_refs":["E1"]}]}))
  (root/"ai_context"/"TRACEABILITY.json").write_text(json.dumps({"entry_point_to_flow":{"EP1":"F1"}})); self.r=ContextResolver(root)
 def tearDown(self): self.tmp.cleanup()
 def test_all_package_types_snapshot_and_determinism(self):
  for kind in PACKAGE_TYPES:
   a=self.r.resolve(kind,{"flow_id":"F1"} if kind=="FLOW" else None,0); b=self.r.resolve(kind,{"flow_id":"F1"} if kind=="FLOW" else None,0)
   self.assertEqual(a,b); self.assertEqual(a["source_snapshot"],"snap"); self.assertNotIn("INTERPRETED",json.dumps(a))
 def test_lookup_states_and_no_guessing(self):
  self.assertEqual(self.r.lookup("F1")["status"],"FOUND"); self.assertEqual(self.r.lookup("missing")["status"],"NOT_FOUND")
 def test_flow_references_and_unresolved(self):
  x=self.r.resolve("FLOW",{"flow_id":"F1"},2); self.assertEqual(x["path_refs"],["P1"]); self.assertEqual(x["unresolved_refs"],["P1"]); self.assertIn("ai_context/FUNCTIONAL_FLOWS.json",x["provenance"]["artifacts"])
 def test_truncation_explicit(self):
  x=self.r.resolve("SYSTEM",limits={"flows":0}); self.assertTrue(x["truncation"]["truncated"]); self.assertTrue(x["selection_policy"]["truncation_reasons"])
 def test_ambiguous_normalized_lookup(self):
  self.r.trace["entry_point_to_flow"]["f1"]="F1"; result=self.r.lookup("F1"); self.assertEqual(result["status"],"AMBIGUOUS"); self.assertEqual(result["candidates"],sorted(result["candidates"])); self.assertGreater(len(result["candidates"]),1)
 def test_targeted_entity_scopes_are_retained_without_interpretation(self):
  for kind in ["PROJECT","UI","COMPONENT","METHOD","DATA_OPERATION","STORED_PROCEDURE"]:
   x=self.r.resolve("ENTITY",{"entity_type":kind,"entity_id":"X"}); self.assertEqual(x["scope"]["entity_type"],kind); self.assertEqual(x["source_snapshot"],"snap"); self.assertNotIn("business",json.dumps(x).lower())

class ContextComposerTests(unittest.TestCase):
 def test_budget_order_and_full_complete(self):
  c=ContextComposer(FakeResolver()); results=[c.compose("FUNCTIONAL",profile=p) for p in ["TINY","SMALL","MEDIUM","LARGE","FULL"]]
  self.assertEqual(results[-1]["statistics"]["completeness"],"COMPLETE"); self.assertEqual(sorted(x["statistics"]["records_included"] for x in results),[x["statistics"]["records_included"] for x in results]); self.assertGreater(results[-1]["statistics"]["records_included"],results[-2]["statistics"]["records_included"])
 def test_dedup_priority_unresolved_and_metrics(self):
  x=ContextComposer(FakeResolver()).compose("FUNCTIONAL",profile="TINY"); refs=[r["ref"] for r in x["records"]]
  self.assertEqual(len(refs),len(set(refs))); self.assertTrue(any(r["priority"]=="P3" for r in x["records"])); self.assertIn("counts_by_category",x["statistics"]); self.assertEqual(x["statistics"]["estimated_tokens"],-(-x["statistics"]["character_count"]//4))
 def test_budget_insufficient_and_deterministic(self):
  c=ContextComposer(FakeResolver(),chars_per_token=5); a=c.compose("FLOW",profile="TINY",budget={"max_characters":1}); b=c.compose("FLOW",profile="TINY",budget={"max_characters":1})
  self.assertEqual(a,b); self.assertEqual(a["statistics"]["completeness"],"BUDGET_INSUFFICIENT"); self.assertGreater(a["statistics"]["minimum_required_characters"],1)
 def test_progressive_levels(self):
  c=ContextComposer(FakeResolver()); expected={"SYSTEM":"L0","TECHNICAL":"L1","ENTITY":"L2","FLOW":"L3","DATA_ACCESS":"L4","FUNCTIONAL":"L5"}
  for kind,level in expected.items(): self.assertEqual(c.compose(kind,profile="TINY")["progressive_level"],level)
 def test_independent_limits_and_priority_order(self):
  c=ContextComposer(FakeResolver()); budget={"max_flows":2,"max_paths":3,"max_entities":4,"max_unresolved":2,"max_evidence_refs":3,"max_estimated_tokens":100000}
  x=c.compose("FUNCTIONAL",profile="FULL",budget=budget); counts=x["statistics"]["counts_by_category"]
  self.assertEqual(counts["flow_refs"],2); self.assertEqual(counts["path_refs"],3); self.assertEqual(counts["data_access_refs"],4); self.assertEqual(counts["unresolved_refs"],2); self.assertEqual(counts["evidence_refs"],3); self.assertEqual([r["priority"] for r in x["records"]],sorted(r["priority"] for r in x["records"])); self.assertTrue(x["truncation"]["truncated"])
 def test_p0_insufficient_token_formula_metrics_and_traceability(self):
  c=ContextComposer(FakeResolver(),chars_per_token=7); x=c.compose("DATA_ACCESS",profile="TINY",budget={"max_characters":1})
  self.assertEqual(x["statistics"]["completeness"],"BUDGET_INSUFFICIENT"); self.assertTrue(any(r["priority"]=="P0" for r in x["records"])); self.assertEqual(x["statistics"]["estimated_tokens"],-(-x["statistics"]["character_count"]//7)); self.assertEqual(x["source_snapshot"],x["provenance"]["source_snapshot"])
  required={"package_bytes","character_count","estimated_tokens","records_selected","records_included","records_excluded","deduplicated_records","counts_by_priority","counts_by_category","confirmed_reference_count","unresolved_reference_count","traceability_reference_count","flow_count","data_access_count","entity_count","coverage_by_priority"}; self.assertFalse(required-set(x["statistics"]))
