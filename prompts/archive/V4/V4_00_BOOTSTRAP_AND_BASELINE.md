# LegacyMapper V4 — Bootstrap and Baseline

TASK=V4_00_BOOTSTRAP_AND_BASELINE

MODE=ANALYZE_AND_PREPARE

IMPLEMENTATION_ALLOWED=false

## Objective

Prepare LegacyMapper for V4 development using the closed V3 baseline.

The current agent may be Claude, Codex or another capable development agent.

Do not assume access to previous conversations or agent memory.

All required context must be obtained from the repository.

## Required Reading

Read in this order:

1. `AGENTS.md`
2. `output/v3_final/V3_FINAL_BASELINE.json`
3. `codex/V3/V3_CIERRE_FINAL.md`
4. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
5. `docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md`
6. `docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. `docs/V4/V4_AI_HANDOVER.md`

Use the repository as authority.

Do not reconstruct project history from assumptions.

## V3 Verification

Run:

`python -m unittest discover -s tests`

Expected baseline:

662 tests PASS.

Also execute:

`python -m legacy_documenter.knowledge.readiness`

Expected:

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

Do not call real LLM providers.

Do not modify legacy source.

## Repository Agent Neutrality Review

Review root instructions and identify any development instruction that unnecessarily assumes Codex specifically.

The project must support continuation by different AI development agents.

If `AGENTS.md` contains execution rules that are valid independently of Codex, preserve them.

If wording is Codex-specific but the underlying rule is generic, propose an agent-neutral wording.

Do not remove historical Codex artifacts.

`codex/V1`, `codex/V2` and `codex/V3` remain historical execution records.

Do not rename them.

## Claude Bootstrap

Verify whether root `CLAUDE.md` exists.

If missing, propose a minimal `CLAUDE.md`.

It must NOT duplicate project knowledge.

It should direct Claude to:

`AGENTS.md`

and:

`docs/V4/V4_AI_HANDOVER.md`

The objective is to keep canonical project instructions agent-neutral.

## V4 Architecture Inventory

Inspect current production modules under:

`legacy_documenter/`

Identify components that can be reused for:

* provenance;
* evidence references;
* context packaging;
* document claims;
* human review;
* readiness;
* knowledge projection;
* provider abstraction;
* deterministic validation;
* security;
* traceability.

For every candidate classify:

REUSE_AS_IS

EXTEND

ADAPT

DO_NOT_REUSE

Explain why.

Do not modify production code.

## V4 Gap Analysis

Compare the current V3 capabilities against:

`docs/V4/V4_CONTRACT_FOUNDATION.md`

Identify missing capabilities for:

MULTI_SOURCE_KNOWLEDGE

HUMAN_INFORMATION_INGESTION

PROVENANCE

KNOWLEDGE_CLASSIFICATION

AS_IS_TO_BE_SEPARATION

GAP_DETECTION

CONFLICT_DETECTION

KNOWLEDGE_PROPOSAL

TECHNICAL_LEADER_APPROVAL

KNOWLEDGE_COMPOSITION

DOCUMENT_PROJECTION

Do not design V5.

Full technology/language/framework agnosticism remains deferred.

## Authority Model

Use the V4 rule:

The Technical Lead is the controlled operator and final approval authority.

Do not propose enterprise RBAC unless required by an actual V4 contract.

Continue preserving source provenance independently of approval authority.

## LegacyMapper / Plugin Boundary

Preserve:

LegacyMapper constructs the Knowledge Source.

The future multi-agent Plugin consumes it.

Identify any proposed functionality that appears to belong to the Plugin instead of LegacyMapper and explicitly mark:

OUT_OF_SCOPE_PLUGIN_RESPONSIBILITY

## Technical Debt Review

Read the technical debt inherited from V3.

Classify each item:

RELEVANT_TO_V4

DEFER

CANDIDATE_FOR_V5

Do not automatically fix debt in this round.

## V4 Roadmap Proposal

Produce a proposed phased V4 roadmap.

Do not implement it.

The roadmap should prioritize contracts before implementation.

Prefer incremental independently testable rounds.

It should include, at minimum, consideration of:

1. knowledge domain model;
2. input/source contracts;
3. provenance;
4. human supplied material;
5. classification;
6. AS_IS / TO_BE;
7. conflict and gap representation;
8. proposal lifecycle;
9. Technical Lead approval;
10. canonical knowledge composition;
11. document projection;
12. Plugin-facing output contract;
13. regression/security;
14. manuals and final baseline.

The exact decomposition must be based on the actual current codebase.

## Output

Create:

`output/v4_bootstrap/V4_REUSE_INVENTORY.json`

`output/v4_bootstrap/V4_GAP_ANALYSIS.json`

`output/v4_bootstrap/V4_TECHNICAL_DEBT_CLASSIFICATION.json`

`docs/V4/V4_PROPOSED_ROADMAP.md`

and:

`docs/V4/V4_00_BOOTSTRAP_RESULT.md`

The result must include:

STATUS
AGENT
V3_BASELINE
TESTS
READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
AGENT_NEUTRALITY
CLAUDE_BOOTSTRAP
REUSE_INVENTORY
V4_GAPS
PLUGIN_BOUNDARY
TECHNICAL_DEBT
PROPOSED_ROADMAP
PRODUCTION_CODE_CHANGED
REAL_LLM_CALLS
PROVIDER_CALLS
DECISION
NEXT

## Success State

Expected:

STATUS=V4_00_BOOTSTRAP_COMPLETE

V3_BASELINE=VALID

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

AGENT_NEUTRALITY=PASS

PRODUCTION_CODE_CHANGED=false

REAL_LLM_CALLS=0

PROVIDER_CALLS=0

DECISION=V4_READY_FOR_ROADMAP_REVIEW

NEXT=HUMAN_REVIEW_V4_ROADMAP

Stop.

Do not begin implementation of V4.