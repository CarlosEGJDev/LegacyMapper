# LegacyMapper V4 — R12 Approval, Closure and Versioning

TASK=V4_R12_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
R12_SEMANTIC_CHANGE_ALLOWED=false
R13_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R12 — Plugin-Facing Machine-Readable Output Contract
```

The Technical Lead explicitly accepts the following R12 design decisions:

1. `CANONICAL_METADATA_DEFAULT=NOT_PROJECTED`.
2. Payload fingerprint is optional and not embedded into the base contract artifacts.
3. Serialized payload validation operates on plain dictionaries in addition to dataclass validation.
4. Missing temporal state is represented in manifest counts as `UNSPECIFIED`.
5. Semantically unordered evidence/reference identifier collections are deterministically sorted.
6. R12 remains completely independent from R11 Markdown and projection rules.
7. R12 defines only the machine-readable Plugin contract; it does not implement Plugin runtime, agents, orchestration, model routing, planning, or autonomous execution.

This task records the already-granted Technical Lead approval and versions the reviewed checkpoint.

The development agent must NOT grant approval itself.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R11_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md`
9. `output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json`
10. `output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R12
latest_approved_round = V4-R11

current_round_in_progress =
"V4-R12 (pending Technical Lead review)"

round_status =
V4-R12_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R12

tests = 1288

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If the semantic state differs:

STOP.

Do not reconcile silently.

---

# Reviewed Artifact Integrity

Expected contract:

```text
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json

SHA256=
42e28173fea3ceafd091e3ee106e334ada3f9dd470073748452172223df19d97
```

Expected example:

```text
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json

SHA256=
d90665f9e155d7bcb06ae22feb3ba961838c8359c9650b09a09acb5743b8cff7
```

Require:

```text
R12_CONTRACT_INTEGRITY=PASS
R12_EXAMPLE_INTEGRITY=PASS
```

If reviewed artifacts differ:

STOP.

Do not repair and approve in the same task.

---

# Approved Architecture

Preserve:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

and:

```text
R10 Canonical Knowledge Source
        ↓ read-only
R12 Plugin-Facing Projection
        ↓
Versioned deterministic JSON
```

Required:

```text
PLUGIN_PAYLOAD_IS_PROJECTION
PLUGIN_PAYLOAD_IS_NOT_CANONICAL_KNOWLEDGE

R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY=NONE

CANONICAL_INPUT_READ_ONLY
CANONICAL_INPUT_MUTATION=NONE
```

---

# Approved Contract

Preserve:

```text
CONTRACT_NAME=LegacyMapperPluginKnowledge
CONTRACT_VERSION=1.0
```

Do not change contract version during closure.

No schema redesign is authorized.

---

# Approved Identity Policy

Preserve:

```text
PLUGIN_ENTRY_ID=CANONICAL_KNOWLEDGE_ID
```

Do not introduce a second knowledge identity.

---

# Approved Completeness Policy

Preserve:

```text
ALL_CANONICAL_ENTRIES_PROJECTED
SILENT_ENTRY_OMISSION=FORBIDDEN
```

Every canonical R10 entry must remain represented.

Do not introduce filtering.

Do not reuse R11 mapping rules.

---

# Approved Knowledge Semantics

Preserve exactly:

```text
STATEMENT_POLICY=VERBATIM
STATUS_POLICY=PRESERVE
TEMPORAL_POLICY=PRESERVE
EVIDENCE_POLICY=PRESERVE_REFERENCES
PROVENANCE_POLICY=PRESERVE_WHEN_PRESENT
RELATIONSHIP_POLICY=PRESERVE_REFERENCES
APPROVAL_TRACEABILITY_POLICY=PRESERVE
```

Required:

```text
APPROVED != CONFIRMED
```

Approval traceability must not modify canonical status.

---

# Approved Metadata Policy

Preserve:

```text
CANONICAL_METADATA_DEFAULT=NOT_PROJECTED
```

Do not add a general metadata field to `PluginKnowledgeEntry`.

If Plugin later requires specific metadata, that must be an explicit future contract decision.

No metadata redesign is authorized in this closure task.

---

# Approved Human-Only Support

Preserve:

```text
SOURCE_CODE_OPTIONAL=true
PLUGIN_CONTRACT_NOT_VBNET_SPECIFIC=true
```

Plugin payload must remain usable for:

```text
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

Do not introduce source-code-required fields.

---

# Approved Serialization

Preserve deterministic JSON behavior:

```text
stable key ordering
entries sorted by knowledge_id
evidence_refs sorted by evidence_id
semantically unordered ID collections sorted
no timestamps
no random UUIDs
no runtime identity
no machine-specific paths
```

---

# Approved Fingerprint Decision

Preserve the optional fingerprint utility:

```text
payload_fingerprint = SHA256(render_payload_json(payload))
```

The fingerprint must remain outside the bytes being hashed.

Do not make fingerprint mandatory during closure.

Do not add it into the base dataclass contract.

---

# Approved Validation Policy

Preserve:

```text
STRICT_CONTRACT_VALIDATION
```

The serialized-dict validator must continue validating:

```text
contract name
contract version
source kind
projection kind
required fields
closed enums
knowledge-id uniqueness
manifest consistency
traceability fields
```

Fixed non-echoing validation errors must remain unchanged.

---

# Plugin Boundary

Preserve:

```text
LEGACYMAPPER_CONSTRUCTS_KNOWLEDGE
PLUGIN_CONSUMES_KNOWLEDGE
```

R12 must remain:

```text
CONTRACT_ONLY_NO_RUNTIME
```

Do NOT implement:

```text
Plugin runtime
agents
orchestration
task planning
code generation
project modification
autonomous execution
model routing
provider routing
prompt execution
```

---

# R11 Independence

Preserve:

```text
R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R12_SOURCE!=R11_MARKDOWN
R11_DEPENDENCY=NONE
```

Do not add imports from:

```text
legacy_documenter.knowledge.projection
```

No semantic dependency on R11 is authorized.

---

# Regression Validation

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1288 PASS
```

Run readiness.

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

If validation fails:

STOP.

---

# Register Technical Lead Approval

Update `PROJECT_STATE.json` using the existing schema.

Required final semantic state:

```text
latest_completed_round = V4-R12
latest_approved_round = V4-R12

current_round_in_progress = null

round_status = V4-R12_APPROVED

next = V4-R13

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R12 Result

Append only a closure section to:

```text
docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md
```

Record at minimum:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

METADATA_POLICY_DECISION=APPROVED
FINGERPRINT_DECISION=APPROVED
DICT_VALIDATION_DECISION=APPROVED
UNSPECIFIED_TEMPORAL_DECISION=APPROVED
REFERENCE_SORTING_DECISION=APPROVED
R11_INDEPENDENCE_DECISION=APPROVED
PLUGIN_BOUNDARY_DECISION=APPROVED

ROUND_STATUS=APPROVED

DECISION=V4_R12_FORMALLY_APPROVED

NEXT=V4-R13
```

Do not rewrite the reviewed result.

---

# Do Not Modify Reviewed Implementation

Do not modify:

```text
legacy_documenter/knowledge/plugin_projection/

tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py

output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json

output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json
```

If reviewed artifact integrity differs:

STOP.

---

# Git Safety

Inspect:

```text
git status
git diff
git diff --stat
```

Do not use destructive Git operations.

Forbidden:

```text
git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force
```

---

# Security

Require:

```text
SECRET_SCAN=PASS
```

No credentials, tokens, `.env`, private keys, unrelated output, or heavy artifacts may be committed.

---

# Closure Result

Create:

```text
docs/V4/V4_R12_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

METADATA_POLICY_DECISION
FINGERPRINT_DECISION
DICT_VALIDATION_DECISION
UNSPECIFIED_TEMPORAL_DECISION
REFERENCE_SORTING_DECISION
R11_INDEPENDENCE_DECISION
PLUGIN_BOUNDARY_DECISION

R12_CONTRACT_SHA256
R12_CONTRACT_INTEGRITY

R12_EXAMPLE_SHA256
R12_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

GIT_STATUS_BEFORE
GIT_BRANCH
GIT_REMOTE

GIT_SAFETY
SECRET_SCAN

GIT_COMMIT
GIT_COMMIT_HASH
GIT_PUSH
GIT_STATUS_AFTER

REPOSITORY_CONTINUITY

ROUND_STATUS
DECISION
NEXT
```

---

# Expected Checkpoint Files

Stage as applicable:

```text
legacy_documenter/knowledge/plugin_projection/

tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py

output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json

docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md

prompts/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT.md
prompts/V4/V4_R12_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R12_CLOSURE_AND_VERSIONING_RESULT.md
```

No R13 implementation file belongs in this commit.

Inspect staged diff before committing.

---

# Commit

Preferred commit message:

```text
Approve and close LegacyMapper V4-R12
```

One normal commit.

No amend.

No squash.

---

# Push

Push current branch normally to `origin`.

No force push.

If explicit user authorization is required for push:

STOP after commit and request it.

---

# Final Validation

Require:

```text
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN
```

Repository must be synchronized with `origin`.

---

# Repository Continuity

A fresh agent using repository artifacts alone must determine:

```text
V3 = FORMALLY CLOSED

V4-R1    = APPROVED
V4-R1.1  = APPROVED
V4-R2    = APPROVED
V4-R3    = APPROVED
V4-R4    = APPROVED
V4-R5    = APPROVED
V4-R6    = APPROVED
V4-R7    = APPROVED
V4-R8    = APPROVED
V4-R9    = APPROVED
V4-R10   = APPROVED
V4-R11   = APPROVED
V4-R12   = APPROVED

readiness = READY
next = V4-R13
```

---

# Expected Success State

```text
STATUS=V4_R12_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

METADATA_POLICY_DECISION=APPROVED
FINGERPRINT_DECISION=APPROVED
DICT_VALIDATION_DECISION=APPROVED
UNSPECIFIED_TEMPORAL_DECISION=APPROVED
REFERENCE_SORTING_DECISION=APPROVED
R11_INDEPENDENCE_DECISION=APPROVED
PLUGIN_BOUNDARY_DECISION=APPROVED

R12_CONTRACT_INTEGRITY=PASS
R12_EXAMPLE_INTEGRITY=PASS

TESTS=>=1288_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R12_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R12_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R13
```

---

# Stop Condition

STOP after closing and versioning R12.

Do NOT begin V4-R13.
