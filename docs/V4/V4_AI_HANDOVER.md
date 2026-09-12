# LegacyMapper — AI Handover

## Purpose

This document allows any capable AI development agent to continue LegacyMapper without relying on previous agent memory or conversation history.

The repository is authoritative.

Agent memory is not authoritative.

## Current Project State

V1:
CLOSED

V2:
CLOSED

V3:
FORMALLY_CLOSED

V4:
FOUNDATION / DEFINITION

V4 implementation has not started.

## Required Starting Point

Read, at minimum:

1. `AGENTS.md`
2. `output/v3_final/V3_FINAL_BASELINE.json`
3. `codex/V3/V3_CIERRE_FINAL.md`
4. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
5. `docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md`
6. `docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. the active V4 prompt

Historical Codex artifacts are evidence of previous executions but do not make Codex an architectural dependency.

## V3 Baseline

Expected regression baseline:

662 tests PASS.

Knowledge state:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

V3 canonical evidence, human review decisions and knowledge semantics must remain intact.

## Development Philosophy

Python-first.

Use good Python practices.

When compatible with idiomatic Python, prefer organization understandable to a C# developer.

Classes:
PascalCase

Modules:
snake_case

Use explicit type hints on significant/public boundaries.

Use concise explanatory docstrings for significant public classes, methods and functions.

Avoid unnecessary Python magic.

Prefer simple, secure, maintainable and testable designs.

Do not introduce patterns solely to imitate C#.

## Execution Philosophy

Deterministic work belongs in Python whenever practical.

Use LLMs for non-deterministic interpretation.

Do not spend model tokens performing transformations that Python can perform deterministically.

LLM-generated semantic output must be constrained by explicit contracts and validated by Python.

## Evidence Philosophy

Never invent:

* source relationships;
* requirements;
* business rules;
* architecture;
* dependencies;
* ownership;
* approvals;
* evidence.

Preserve uncertainty explicitly.

AI interpretation is not automatically authoritative knowledge.

## V4 Purpose

V4 expands LegacyMapper from primarily code-derived knowledge into multi-source knowledge construction.

Inputs may include:

* code;
* existing documents;
* requirements;
* user stories;
* business needs;
* business context;
* standards;
* technical constraints;
* decisions;
* information supplied by the Technical Lead.

LegacyMapper processes and organizes this material into an approved Knowledge Source intended for a later multi-agent Plugin.

## Human Authority

LegacyMapper V4 is operated by the Technical Lead.

The Technical Lead has final authority to accept, reject or correct proposed knowledge.

Do not implement an unnecessary organization-wide RBAC system unless explicitly requested in a future decision.

Provenance must still be preserved.

## Separation of Responsibilities

LegacyMapper:
constructs knowledge.

Plugin:
consumes knowledge and performs autonomous project work.

Do not move Plugin agent responsibilities into LegacyMapper.

## V5 Boundary

Full language/framework/technology/project-layout agnosticism is deferred to V5.

Do not attempt to solve V5 during V4 unless the Technical Lead explicitly changes scope.

## Backward Compatibility

V3 is a closed baseline.

Do not silently modify:

* canonical V3 artifacts;
* approved human review decisions;
* R9 semantics;
* V3 evidence;
* V3 closure records.

Any unavoidable compatibility change must be explicitly documented and validated.

## Agent Independence Rule

Do not introduce implementation or process requirements that unnecessarily bind LegacyMapper development to:

* Claude;
* Codex;
* Copilot;
* Gemini;
* any specific model;
* any specific AI vendor.

Provider-specific adapters are permitted.

Core contracts must remain provider-neutral.

## Before Implementing V4

The agent must first:

1. verify repository state;
2. verify V3 baseline;
3. run existing tests;
4. read the V4 foundation;
5. inventory existing components reusable by V4;
6. identify compatibility boundaries;
7. produce a proposed V4 execution roadmap.

Do not begin feature implementation until that bootstrap review is complete.

## Continuity Requirement

At the end of each significant V4 round update:

* current state;
* decisions;
* unresolved questions;
* changed files;
* test baseline;
* next step.

A replacement AI must be able to resume from repository artifacts alone.