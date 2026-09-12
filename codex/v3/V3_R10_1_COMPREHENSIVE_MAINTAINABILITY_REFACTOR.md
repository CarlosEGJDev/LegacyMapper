# LegacyMapper — V3-R10.1 Comprehensive Maintainability Refactor

TASK=V3-R10_1_COMPREHENSIVE_MAINTAINABILITY_REFACTOR

MODE=INCREMENTAL_REFACTOR_TEST

PARENT=V3-R10_CODE_QUALITY_MAINTAINABILITY_DOCUMENTATION_COMPLETE

## Objective

Complete the maintainability objective that R10 intentionally handled conservatively.

R10 validated engineering quality and documentation, but only one of 71 analyzed modules was structurally refactored.

R10.1 must improve the remaining production Python code incrementally while preserving behavior.

This is NOT a rewrite.

This is NOT feature development.

This is the final code-maintainability pass before V3 closure and before V4/V5 use this codebase.

## Permanent Style Authority

Use:

docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

as the authoritative development standard.

Priority:

GOOD PYTHON PRACTICES FIRST.

Where compatible with idiomatic Python, organize code in a way familiar to a C# developer.

Classes:
PascalCase

Modules:
snake_case

When a module has one clear primary class:

ClassName
->
class_name.py

Prefer one significant primary class per file when this improves comprehension.

Do not mechanically apply C# patterns that make Python worse.

## Human Readability Requirement

The primary reader is a C# developer with limited Python experience.

A developer opening a production module should be able to understand:

what the module does;
what each important class does;
what each important method/function does;
what inputs it expects;
what it returns;
important side effects;
why non-obvious deterministic/security rules exist.

## Documentation Requirement

Every production:

public class
public method
public function
significant internal class
significant internal method/function

must have an explanatory docstring.

Docstrings must be concise and useful.

Explain WHAT and, where useful, WHY.

Do not add meaningless docstrings only to increase a metric.

Private trivial helpers may remain undocumented when their behavior is immediately obvious.

Comments must explain non-obvious:

deterministic behavior;
security boundaries;
evidence rules;
LLM restrictions;
immutability;
algorithms;
compatibility decisions.

Do not comment obvious Python syntax.

## Type Hint Requirement

Improve type hints across production code.

Prioritize:

public APIs;
service boundaries;
validators;
providers;
resolvers;
analysis services;
documentation services;
knowledge services;
important transformations.

Do not pursue 100% typing by introducing unreadable typing complexity.

Reduce unnecessary `Any`.

Preserve runtime compatibility.

## Refactoring Scope

Review all production Python modules under:

legacy_documenter/

Exclude:

tests
generated outputs
codex
documentation files

Use R10:

MAINTAINABILITY_AUDIT_AFTER.json

as the starting inventory.

Prioritize modules with:

multiple responsibilities;
low documentation coverage;
low type coverage;
large significant functions;
cross-round duplicated responsibility;
difficult-to-understand procedural orchestration.

## Incremental Strategy

Do NOT refactor all modules in one change.

Create deterministic refactoring batches.

Suggested conceptual order:

BATCH 1
models / shared contracts / utils

BATCH 2
extractors / resolvers

BATCH 3
context

BATCH 4
llm/providers

BATCH 5
documentation

BATCH 6
analysis

BATCH 7
knowledge / exporters / orchestration

Adjust batching based on actual dependencies.

After every batch:

run targeted tests.

If targeted tests PASS:

continue.

After major boundaries:

run full regression.

If a batch causes semantic regression:

STOP that batch,
restore/reconcile it,
do not weaken tests.

## Class Extraction

Where a procedural module clearly represents a cohesive service, consider extracting a class.

Examples of appropriate concepts:

Analyzer
Resolver
Validator
Composer
Renderer
Service
Provider

Only extract a class when:

state or cohesive behavior justifies it;
readability improves;
testing remains straightforward.

Do not wrap every function in a class.

## File Organization

Where a significant class exists in an unrelated or overly broad module, it may be moved to its own snake_case module.

Preserve compatibility using imports/wrappers when existing runtime paths are public or tested.

Example target:

class TargetedEvidenceAnalyzer

module:

targeted_evidence_analyzer.py

Existing import paths should continue working where required.

## Complexity

Reduce:

deep nesting;
very large functions;
mixed I/O and validation;
mixed discovery and interpretation;
duplicated status logic;
duplicated serialization logic;
unexplained literals.

Do not fragment simple code into unnecessary abstraction layers.

## Canonical Values

Identify duplicated canonical statuses/constants.

Centralize only where:

ownership is clear;
serialization remains unchanged;
circular dependencies are not introduced;
tests prove compatibility.

Do not perform a risky global constants rewrite.

## Provider Boundaries

Preserve provider behavior exactly.

Do not change external LLM semantics.

Do not make real provider calls.

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

Provider exception boundaries previously identified as technical debt may remain when changing them could alter safe-failure behavior.

Document why they remain.

## R7/R8 Historical Modules

R10 identified compact R7/R8 modules as technical debt.

Review them now.

Improve:

typing;
docstrings;
method decomposition;
naming;
responsibility separation

where this can be proven behavior-preserving.

Do NOT redesign the validated R7/R8 contracts.

Do NOT modify canonical evidence semantics.

If structural refactoring of a particular historical module is unsafe:

keep it;
document the exact reason;
still improve documentation/type hints when safe.

## Duplication

Investigate:

POTENTIAL_CROSS_ROUND_HELPER_DUPLICATION

Do not merge helpers solely because their code looks similar.

Merge only when they have the same semantic contract.

Otherwise document why duplication is intentional.

## Compatibility

Preserve all validated public entry points.

Compatibility wrappers are acceptable.

Do not break:

legacy_documenter.main
legacy_documenter.knowledge.readiness.run

or any other runtime path identified by tests/manuals as public.

If a class is moved:

leave a compatibility import/wrapper when required.

## Manual Synchronization

After final refactoring, update only where necessary:

docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md
docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md
docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

Do not rewrite manuals unnecessarily.

Update real:

module paths;
class names;
entry points;
developer extension instructions.

Manuals must describe the final codebase, not the pre-refactor codebase.

## Metrics

Generate:

output/v3_r10_1/MAINTAINABILITY_AUDIT_BEFORE.json
output/v3_r10_1/MAINTAINABILITY_AUDIT_AFTER.json
output/v3_r10_1/REFACTORING_MAP.json
output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json

Report separately:

production modules analyzed;
production modules changed;
significant symbols;
documented significant symbols;
typed significant boundaries.

Do not optimize blindly for percentages.

However, the final audit must demonstrate a substantial improvement over R10's:

TYPE_HINT_COVERAGE=49.72%
DOCSTRING_COVERAGE=7.19%

If improvement is small, explain why each remaining undocumented/untyped significant area cannot safely be improved.

## Behavior Preservation

The following must remain semantically unchanged:

V1 outputs/contracts
V2 outputs/contracts
V3 evidence contracts
human decisions
approved levantamientos
R9 knowledge projection
R9 knowledge boundary
R9 readiness traceability
security boundaries
source immutability

Do not generate AI_KNOWLEDGE.

## Regression

Current baseline:

650 PASS

Run:

python -m unittest discover -s tests

Final:

ALL PASS.

Do not weaken tests.

Add focused tests for compatibility wrappers and extracted services where required.

## R9 Revalidation

After all refactoring execute the actual deterministic R9 readiness entry point.

Require:

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

R9 canonical semantics/hashes must remain unchanged unless an output serialization timestamp or explicitly non-semantic field exists.

Any semantic change:

R10.1 FAILS.

## Security

Legacy source remains READ-ONLY.

No broad legacy source analysis is needed.

No external provider call.

No secrets in code examples, logs or manuals.

No credentials introduced.

## Required Result

Create:

codex/V3/V3_R10_1_COMPREHENSIVE_MAINTAINABILITY_REFACTOR_RESULTADO.md

Required fields:

STATUS
FILES_CHANGED
PRODUCTION_MODULES_ANALYZED
PRODUCTION_MODULES_CHANGED
REFACTORING_BATCHES
CLASSES_CREATED
CLASSES_MOVED
COMPATIBILITY_WRAPPERS
SIGNIFICANT_SYMBOLS
DOCUMENTED_SIGNIFICANT_SYMBOLS
TYPE_HINT_COVERAGE_BEFORE
TYPE_HINT_COVERAGE_AFTER
DOCSTRING_COVERAGE_BEFORE
DOCSTRING_COVERAGE_AFTER
DUPLICATION_REVIEW
DEAD_CODE_REVIEW
TECHNICAL_DEBT_REMAINING
PYTHON_STANDARD_STATUS
USER_MANUAL_STATUS
TECHNICAL_MANUAL_STATUS
BASELINE_TESTS
FINAL_TESTS
REGRESSION
R9_REVALIDATION
READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS
LEGACY_SOURCE_IMMUTABILITY
V2_CANONICAL_EVIDENCE_INTEGRITY
R8_HUMAN_DECISION_INTEGRITY
R9_KNOWLEDGE_SEMANTICS_INTEGRITY
SECURITY
DECISION
NEXT

## Success

Expected:

STATUS=
V3-R10_1_COMPREHENSIVE_MAINTAINABILITY_REFACTOR_COMPLETE

REGRESSION=
PASS

R9_REVALIDATION=
PASS

READINESS=
READY

AI_KNOWLEDGE_ALLOWED=
true

AI_KNOWLEDGE_GENERATED=
false

DECISION=
V3_CODEBASE_READY_FOR_FUTURE_DEVELOPMENT

NEXT=
V3_FINAL_CLOSURE_REVIEW

Do not declare V3 closed automatically.

Stop after final validation and report generation.