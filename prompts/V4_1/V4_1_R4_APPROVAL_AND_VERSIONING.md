# LegacyMapper V4.1 — R4 Approval and Versioning

TASK=V4_1_R4_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R5_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R4 — Readiness Module Decomposition

The Technical Lead explicitly accepts:

- Phase A characterization before production modification;
- 18 characterization tests;
- READINESS_DECOMPOSITION_DECISION=SAFE_FOR_CONTROLLED_EXTRACTION;
- Phase B controlled decomposition;
- extraction of file I/O into `_readiness_io.py`;
- extraction of parsing into `_readiness_parsing.py`;
- extraction of evidence-closure computation into `_readiness_evidence.py`;
- preservation of validation, projection, security and orchestration/CLI in `readiness.py`;
- explicit compatibility forwarding for moved symbols;
- preservation of public/importable readiness symbols and signatures;
- preservation of monkeypatch/import compatibility;
- byte-equivalent R9 serialized outputs;
- result, ordering, exception and CLI equivalence;
- DEBT-002=RESOLVED;
- DEBT-003=RESOLVED unchanged;
- TD-005=PARTIALLY_RESOLVED unchanged;
- approved-artifact integrity;
- R0 frozen inventory remaining untouched;
- PRODUCTION_BEHAVIOR_CHANGED=false;
- no R4.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
6. `docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md`
7. `docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md`
9. `docs/V4_1/V4_1_R4_READINESS_MODULE_DECOMPOSITION_RESULT.md`
10. `output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json`
11. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R4
latest_approved_round = V4.1-R3

current_round_in_progress =
"V4.1-R4 (pending Technical Lead review)"

round_status =
V4_1_R4_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R4

tests = 1486
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed Equivalence Artifact

Expected:

output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

SHA256=
eb07e0f35540e0607b90f8ff707c7cac8e1f113419d338e3cc8579fa12f1e617

Recompute.

Require:

READINESS_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair it.

---

# Approved Decomposition

Require the reviewed structure to remain:

legacy_documenter/knowledge/readiness.py

legacy_documenter/knowledge/_readiness_io.py
legacy_documenter/knowledge/_readiness_parsing.py
legacy_documenter/knowledge/_readiness_evidence.py

Require:

EXTRACTIONS_PERFORMED=3

FILE_IO_EXTRACTION=APPROVED
PARSING_EXTRACTION=APPROVED
EVIDENCE_CLOSURE_EXTRACTION=APPROVED

No additional extraction is authorized during closure.

---

# Facade Responsibilities

Preserve in `readiness.py`:

- validation;
- projection;
- security;
- orchestration;
- CLI entry behavior.

Do not attempt to further reduce the facade during closure.

---

# Compatibility

Require:

READINESS_PUBLIC_IMPORTS_PRESERVED=PASS
READINESS_PUBLIC_SIGNATURES_PRESERVED=PASS
MONKEYPATCH_COMPATIBILITY=PASS

READINESS_RESULT_EQUIVALENCE=PASS
READINESS_SERIALIZATION_EQUIVALENCE=PASS
READINESS_ORDERING_EQUIVALENCE=PASS
READINESS_EXCEPTION_EQUIVALENCE=PASS
READINESS_CLI_EQUIVALENCE=PASS

No public compatibility cleanup is authorized during closure.

---

# Debt Decisions

Record:

DEBT_002_DECISION=RESOLVED_APPROVED
DEBT_003_STATUS=RESOLVED
TD_005_STATUS=PARTIALLY_RESOLVED

Do not reopen DEBT-002 or DEBT-003.

Do not mark TD-005 resolved.

---

# Approved Artifact Integrity

Recompute and preserve:

output/v4_r14/V4_FINAL_BASELINE.json
SHA256=d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e

output/v4_r14/V4_FINAL_MANIFEST.json
SHA256=be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551

output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
SHA256=55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b

output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
SHA256=bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4

output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json
SHA256=9e922d288b4f07812482baef1a5383276cd71f729e27cc67b47e54c30c5afecf

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

The authorized R4 structural differences in live reconstruction are accepted.

Do not alter:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Do not weaken durable comparison logic.

---

# Scope Fence

Do not modify structurally:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not:

- rename `copilot_pilot.py`;
- restructure `legacy_documenter/context/`;
- continue TD-005 typing work;
- implement V5;
- implement Plugin runtime.

Require:

REMAINING_HIGH_RISK_MODULES_PRESERVED=PASS

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1486 PASS
FAIL=0
SKIP=0

No test may be removed, skipped or weakened.

---

# Readiness

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

---

# V4 Preservation

Require:

V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED
V5_IMPLEMENTED=false

---

# Production Classification

Preserve:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

Closure itself must introduce no additional production change.

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R4
latest_approved_round = V4.1-R4

current_round_in_progress = null

round_status = V4_1_R4_APPROVED

next = V4.1-R5

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R4 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R4_READINESS_MODULE_DECOMPOSITION_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

CHARACTERIZATION_DECISION=APPROVED
DECOMPOSITION_DECISION=APPROVED

DEBT_002_DECISION=RESOLVED_APPROVED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

READINESS_EQUIVALENCE_DECISION=APPROVED

R4_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R4_FORMALLY_APPROVED
NEXT=V4.1-R5

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

CHARACTERIZATION_DECISION
DECOMPOSITION_DECISION

DEBT_002_DECISION
DEBT_003_DECISION
TD_005_DECISION

READINESS_EQUIVALENCE_ARTIFACT_SHA256
READINESS_EQUIVALENCE_ARTIFACT_INTEGRITY
READINESS_EQUIVALENCE_DECISION

READINESS_PUBLIC_IMPORTS_PRESERVED
READINESS_PUBLIC_SIGNATURES_PRESERVED
MONKEYPATCH_COMPATIBILITY

READINESS_RESULT_EQUIVALENCE
READINESS_SERIALIZATION_EQUIVALENCE
READINESS_ORDERING_EQUIVALENCE
READINESS_EXCEPTION_EQUIVALENCE
READINESS_CLI_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED
REMAINING_HIGH_RISK_MODULES_PRESERVED

TESTS
READINESS

V4_CONTRACTS_UNCHANGED
R11_BOUNDARY
R12_BOUNDARY

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

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
AGENT_NEUTRAL_CONTINUITY

ROUND_STATUS
DECISION
NEXT

---

# Expected Success State

STATUS=V4_1_R4_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

CHARACTERIZATION_DECISION=APPROVED
DECOMPOSITION_DECISION=APPROVED

DEBT_002_DECISION=RESOLVED_APPROVED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

READINESS_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
READINESS_EQUIVALENCE_DECISION=APPROVED

READINESS_PUBLIC_IMPORTS_PRESERVED=PASS
READINESS_PUBLIC_SIGNATURES_PRESERVED=PASS
MONKEYPATCH_COMPATIBILITY=PASS

READINESS_RESULT_EQUIVALENCE=PASS
READINESS_SERIALIZATION_EQUIVALENCE=PASS
READINESS_ORDERING_EQUIVALENCE=PASS
READINESS_EXCEPTION_EQUIVALENCE=PASS
READINESS_CLI_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false
REMAINING_HIGH_RISK_MODULES_PRESERVED=PASS

TESTS=>=1486_PASS
READINESS=READY

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R4_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R4_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R5

---

# Git Safety

Inspect:

git status
git diff
git diff --stat

Forbidden:

git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force

---

# Secret Scan

Require:

SECRET_SCAN=PASS

Do not expose secret values.

---

# Commit

Preferred message:

Approve LegacyMapper V4.1-R4 readiness decomposition

Use one normal commit.

No amend.
No squash.

IMPORTANT:

After commit, record the REAL commit hash using:

git rev-parse HEAD

The closure document must contain the actual hash.

Do not leave:

GIT_COMMIT_HASH=<recorded after commit>

or any equivalent placeholder.

---

# Push

Push normally to origin.

No force push.

After push require:

git status --short

to be empty.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED
V4.1-R3 = APPROVED
V4.1-R4 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-002 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

TESTS >= 1486 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R5 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R4 approval registration;
2. closure result creation;
3. full green regression;
4. readiness verification;
5. normal commit;
6. real commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R5;
- further decompose readiness.py;
- modify remaining high-risk modules;
- rename copilot_pilot.py;
- restructure context/;
- continue broad typing cleanup;
- change V4 contracts;
- begin V5;
- implement Plugin runtime.