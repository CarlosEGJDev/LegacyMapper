"""Deterministic provider-neutral request serialization; V4.3 payload preserved."""
from __future__ import annotations
import json, math
from .contracts import LLMRequest

def render_request_payload(r: LLMRequest,schema: dict|None=None) -> str:
 """Renders the final, serialized payload an `LLMRequest` actually becomes when sent.

 This is the single, provider-neutral definition of "what really travels to
 the provider" (V4.3-R5). It is the construction
 `legacy_documenter.llm.providers.copilot.CopilotProvider._prompt` performed
 inline before R5 -- the only real implementation that existed -- moved here
 verbatim so it can be *measured* before a call is made, and so the provider
 now delegates to it instead of keeping a second copy that could drift.

 The V4.3-R0 defect `D-01`/`EEE-02` is precisely that nothing measured this
 string: `FakeLLMProvider._status` only ever compared
 `context["statistics"]["estimated_tokens"]` (the context package's own
 estimate) against the context window, which can be far smaller than this
 wrapped payload once the instructions, the policies and the output schema
 are added around it.
 """
 if schema is None: schema=r.output_contract
 parts=["<system_instruction>",r.system_instruction,"</system_instruction>","<task_instruction>",r.user_instruction,"</task_instruction>","<evidence_policy>",json.dumps(r.metadata.get("evidence_policy",{}),sort_keys=True),"</evidence_policy>","<claim_policy>",json.dumps(r.metadata.get("claim_policy",r.metadata.get("evidence_policy",{})),sort_keys=True),"</claim_policy>","<missing_information_policy>",json.dumps(r.metadata.get("missing_information_policy",{}),sort_keys=True),"</missing_information_policy>","<context>",json.dumps(r.context,sort_keys=True,separators=(",",":"),ensure_ascii=False),"</context>"]
 if schema is not None: parts += ["<output_contract>","Return exactly one strict JSON object only. No Markdown fences, comments, explanation, prefix, suffix, or chain-of-thought. Obey every const, enum, required, and additionalProperties constraint. Claims must cite only record ref values present in context.",json.dumps(schema,sort_keys=True,ensure_ascii=False),"</output_contract>"]
 return "\n".join(parts)
def measure_request_payload(r: LLMRequest,schema: dict|None=None,chars_per_token: int=4) -> dict:
 """Measures the payload `render_request_payload` produces: bytes, characters, estimated tokens.

 Same estimation method (`ceil(chars/chars_per_token)`) and the same reported
 shape as `legacy_documenter.context.composer`/`ai_projection`'s own
 `statistics`, so a caller comparing an internal package estimate against this
 payload estimate is comparing like with like. Pure: it never sends anything.
 """
 if schema is None: schema=r.output_contract
 text=render_request_payload(r,schema)
 return {"payload_bytes":len(text.encode()),"payload_characters":len(text),"payload_estimated_tokens":math.ceil(len(text)/chars_per_token),"chars_per_token":chars_per_token,"estimation_method":"approximation: ceil(chars/chars_per_token)","schema_included":schema is not None}
