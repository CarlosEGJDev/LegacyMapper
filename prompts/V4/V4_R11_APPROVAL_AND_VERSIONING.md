# LegacyMapper V4 — R11 Approval, Closure and Versioning

TASK=V4_R11_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
R11_SEMANTIC_CHANGE_ALLOWED=false
R12_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text id="qx0l1d"
V4-R11 — Human-Readable Document Projection
```

The Technical Lead explicitly accepts the three design decisions documented by R11:

1. `03-desarrollo-de-software/` uses 16 closed projection documents, one for each category explicitly named by the R11 specification.
2. `05-plantillas`, `06-catalogo`, `07-proyectos`, `08-historial`, and `09-capacitacion` initially use one closed general document per family; future granularity must be an explicit additive configuration change and must never be inferred from free text.
3. The V3 Markdown renderer is not reused directly because its claim/coverage schema is incompatible with R10 canonical-entry projection; R11's purpose-built renderer preserves the same deterministic pure-string-rendering principles.

This task only records that human approval and versions the already-reviewed checkpoint.

The development agent must NOT grant or reinterpret approval.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R10_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md`
9. `output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json`
10. `output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Expected Pre-Closure State

Verify:

```text id="b03x4s"
latest_completed_round = V4-R11
latest_approved_round = V4-R10

current_round_in_progress =
"V4-R11 (pending Technical Lead review)"

round_status =
V4-R11_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R11

tests = 1213

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If this semantic state differs:

STOP.

Do not reconcile silently.

---

# Reviewed Artifact Integrity

Expected contract:

```text id="cj3f29"
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json

SHA256=
5802e0e78dabd8e44de030ee15c56db747444147a462d050ad2971ffc39206fd
```

Expected example:

```text id="o9nrcp"
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json

SHA256=
4923fa6f1e506fc657c520888c7ebe2ad52102673983424e7c7a26d9d13cbe86
```

Require:

```text id="a21nqj"
R11_CONTRACT_INTEGRITY=PASS
R11_EXAMPLE_INTEGRITY=PASS
```

Also verify the deterministic example documentation tree remains consistent with the reviewed checkpoint.

If reviewed artifacts differ:

STOP.

Do not repair and approve in the same task.

---

# Approved Architecture

Preserve:

```text id="j1ot78"
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

and:

```text id="9bmuwm"
Canonical Knowledge Source
        ↓ read-only
Human-Readable Projection
        ↓
Markdown
```

Required:

```text id="gaw5tz"
MARKDOWN_IS_PROJECTION
MARKDOWN_IS_NOT_CANONICAL_KNOWLEDGE

CANONICAL_INPUT_READ_ONLY

DOCUMENT_STRUCTURE_IS_PROJECTION_CONCERN
DOCUMENT_STRUCTURE_IS_NOT_DOMAIN_MODEL
```

---

# Approved Mapping Policy

Preserve:

```text id="5etukr"
MAPPING_POLICY=EXPLICIT_STRUCTURED_RULES_ONLY
FREE_TEXT_MAPPING=FORBIDDEN
```

Rules may use only approved structured fields/configuration.

An entry without deterministic mapping remains:

```text id="0ozd5i"
UNMAPPED
```

Required:

```text id="rb1zdc"
UNMAPPED_ENTRIES_ARE_PRESERVED
```

No AI fallback classification.

---

# Approved Multi-Projection Policy

Preserve:

```text id="c7kh1g"
ONE_CANONICAL_ENTRY
MAY_HAVE_MULTIPLE_DOCUMENT_PROJECTIONS
```

Every occurrence retains the same canonical `knowledge_id`.

Multiple Markdown occurrences do not create multiple canonical facts.

---

# Approved Traceability

Preserve the reviewed human projection traceability format:

```text id="y7mpda"
### KNO-...

<!-- knowledge_id: KNO-... -->
```

Do not introduce proposal/approval/evidence internals into normal human-readable projection during closure.

---

# Approved Statement Preservation

Preserve:

```text id="fpf56r"
CANONICAL_STATEMENT_PRESERVATION=VERBATIM
```

R11 must not:

* paraphrase;
* summarize;
* explain;
* reinterpret;
* enrich;
* correct;
* translate

canonical statements during deterministic projection.

---

# Approved Empty Document Policy

Preserve:

```text id="shjzgm"
GENERATE_EMPTY_DOCUMENT_WITH_EXPLICIT_NO_APPROVED_KNOWLEDGE_MARKER
```

Empty documents must not invent knowledge.

---

# Approved Information Architecture Decisions

Preserve the reviewed 00–09 closed projection configuration.

Explicitly record Technical Lead acceptance of:

```text id="zv3twe"
03-desarrollo-de-software = 16 closed documents
```

and initial general documents for:

```text id="bxn0dz"
05-plantillas
06-catalogo
07-proyectos
08-historial
09-capacitacion
```

Do not add project-specific documents during closure.

Do not infer project names.

---

# Approved Renderer Decision

Preserve the purpose-built R11 renderer.

Do not refactor it back into the V3 renderer during closure.

No renderer refactoring is authorized in this task.

---

# R12 Boundary

Preserve:

```text id="u3dufi"
R12_SOURCE=CANONICAL_KNOWLEDGE_SOURCE
R12_SOURCE!=R11_MARKDOWN
```

Do NOT implement R12.

Do NOT create:

```text id="0gx13e"
Plugin payload
Plugin schema
Plugin consumer API
agent context package
machine-readable Plugin contract
```

---

# Regression Validation

Run:

```text id="5k7x3z"
python -m unittest discover -s tests
```

Expected:

```text id="y3yihk"
>=1213 PASS
```

Run readiness.

Require:

```text id="bc9hwe"
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

If any validation fails:

STOP.

---

# Register Technical Lead Approval

Update `PROJECT_STATE.json` using the existing schema.

Required final semantic state:

```text id="3v9f4w"
latest_completed_round = V4-R11
latest_approved_round = V4-R11

current_round_in_progress = null

round_status = V4-R11_APPROVED

next = V4-R12

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R11 Result

Append only a closure section to:

```text id="9gcyy6"
docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md
```

Record at minimum:

```text id="l5qz9g"
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

DESIGN_DECISION_03_DOCUMENTS=APPROVED
DESIGN_DECISION_05_09_GENERAL_DOCUMENTS=APPROVED
DESIGN_DECISION_RENDERER=APPROVED

ROUND_STATUS=APPROVED

DECISION=V4_R11_FORMALLY_APPROVED

NEXT=V4-R12
```

Do not rewrite the reviewed result.

---

# Do Not Modify Reviewed Implementation

Do not modify:

```text id="v4td7g"
legacy_documenter/knowledge/projection/

tests/test_v4_r11_human_readable_document_projection.py

output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json

output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json

output/v4_r11/example_docs/
```

If reviewed artifact integrity differs:

STOP.

---

# Git Safety

Inspect:

```text id="ry4qhw"
git status
git diff
git diff --stat
```

No destructive Git operation.

Do not use:

```text id="r0tq7y"
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

Verify:

```text id="ix8vfj"
SECRET_SCAN=PASS
```

No credentials, tokens, `.env`, private keys, unrelated generated output, or heavy artifacts may be committed.

---

# Closure Result

Create:

```text id="vv2jzq"
docs/V4/V4_R11_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text id="luz04g"
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

DESIGN_DECISION_03_DOCUMENTS
DESIGN_DECISION_05_09_GENERAL_DOCUMENTS
DESIGN_DECISION_RENDERER

R11_CONTRACT_SHA256
R11_CONTRACT_INTEGRITY

R11_EXAMPLE_SHA256
R11_EXAMPLE_INTEGRITY

EXAMPLE_DOCS_INTEGRITY

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

```text id="8ic4zn"
legacy_documenter/knowledge/projection/

tests/test_v4_r11_human_readable_document_projection.py

output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json
output/v4_r11/example_docs/

docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md

prompts/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION.md
prompts/V4/V4_R11_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R11_CLOSURE_AND_VERSIONING_RESULT.md
```

Use explicit staging where practical.

Inspect staged diff before commit.

No R12 implementation file belongs in this commit.

---

# Commit

Preferred message:

```text id="3hrrsg"
Approve and close LegacyMapper V4-R11
```

One normal commit.

No amend.

No squash.

---

# Push

Push current branch normally to `origin`.

No force push.

If the environment requires explicit user authorization for push:

STOP after commit and request it.

---

# Final Validation

After push require:

```text id="rck6je"
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN
```

Repository must be up to date with `origin`.

---

# Repository Continuity

A fresh agent using repository artifacts alone must determine:

```text id="mx5nlq"
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

readiness = READY
next = V4-R12
```

---

# Expected Success State

```text id="ukwzvx"
STATUS=V4_R11_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

DESIGN_DECISION_03_DOCUMENTS=APPROVED
DESIGN_DECISION_05_09_GENERAL_DOCUMENTS=APPROVED
DESIGN_DECISION_RENDERER=APPROVED

R11_CONTRACT_INTEGRITY=PASS
R11_EXAMPLE_INTEGRITY=PASS
EXAMPLE_DOCS_INTEGRITY=PASS

TESTS=>=1213_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R11_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R11_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R12
```

---

# Stop Condition

STOP after closing and versioning R11.

Do NOT begin V4-R12.
