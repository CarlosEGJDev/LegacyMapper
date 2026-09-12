STATUS
V3-R4_READY_FOR_REVIEW

FILES_CHANGED
legacy_documenter/llm/__init__.py
legacy_documenter/llm/core.py
tests/test_v3_r4.py

LLM_CONTRACT
Provider-neutral LLMProvider generate/capabilities/model_info contract.

REQUEST_MODEL
Separated system/user/context, deterministic request ID, purpose, ContextPackage identity/schema/snapshot and generation parameters.

RESPONSE_MODEL
Canonical statuses, content, usage, warnings, metadata and structured validation fields.

CAPABILITIES
Context/output limits, structured/JSON/streaming/tools/reasoning/system/temperature capabilities.

MODEL_INFO
Generic provider/model identifiers and capability metadata; no commercial catalog.

PROVIDER_CONFIG
Generic endpoint/options and credential_source reference; no credential value.

PROVIDER_REGISTRY
Lightweight FAKE factory; unknown providers rejected explicitly.

FAKE_PROVIDER
Fixed deterministic text/structured responses and forced statuses; no network/SDK/credentials.

STRUCTURED_OUTPUT
VALID_STRUCTURED_OUTPUT and INVALID_STRUCTURED_OUTPUT with parsed output/errors; no silent repair.

CAPABILITY_VALIDATION
Unsupported structured output/temperature, context overflow and max-output overflow return explicit statuses.

USAGE
Nullable provider-neutral usage; ContextComposer estimate marked estimated with method.

ERROR_MODEL
Structured code/message/provider/model/retryable/details contract; no retry execution.

TRACEABILITY
Response metadata preserves context_package_id and source_snapshot end-to-end.

DETERMINISM
Canonical SHA-256 request/fake-response IDs; repeated fake execution identical.

SECURITY
No secrets, network, external SDK, real LLM or legacy scan.

PROVIDER_INDEPENDENCE
Core schemas accept arbitrary provider/model identifiers; provider behavior isolated behind interface.

R4_TESTS
4 dedicated parametrized tests covering request, fake determinism, structured success/failure, capability rejection and registry/config security.

TOTAL_TESTS
71 passed

REGRESSION
All V1/V2/V3-R1/R2/R3 tests pass.

KNOWN_LIMITATIONS
No real provider, retries, exact tokenizer, streaming runtime, tools, prompt workflow or documentation generation.

DECISION
LLM_PROVIDER_ABSTRACTION_READY

NEXT
V3-R5_NOT_STARTED
