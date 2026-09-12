# LegacyMapper — V3-R10 Code Quality, Maintainability & Documentation

TASK=V3-R10_CODE_QUALITY_MAINTAINABILITY_DOCUMENTATION

MODE=REFACTOR_TEST_DOCUMENT

PARENT=V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE

## 1. Objective

Perform the final engineering-quality pass of LegacyMapper V3.

Goals:

1. improve Python source organization;
2. improve human readability;
3. improve maintainability;
4. reduce unnecessary complexity;
5. establish coding conventions for V4, V5 and future versions;
6. preserve all validated behavior;
7. preserve all V3 contracts and evidence;
8. produce a V3 User Manual;
9. produce a V3 Technical Manual.

This is a refactoring/documentation round.

Do NOT add new LegacyMapper functional capabilities.

Do NOT generate AI_KNOWLEDGE.

---

# 2. Fundamental Refactoring Rule

BEHAVIOR MUST NOT CHANGE.

R10 may improve:

structure
naming
separation of responsibilities
typing
documentation
comments
module organization
dependency organization
code duplication
maintainability
test readability

R10 must NOT change:

V1/V2/V3 semantics
discovery results
evidence semantics
claim semantics
human decisions
knowledge readiness result
security guarantees
LLM contracts
provider behavior
source immutability guarantees

Current baseline:

638 PASS

After refactoring:

ALL existing tests must continue PASS.

---

# 3. Permanent LegacyMapper Python Style Rule

This rule applies to:

R10
V4
V5
future LegacyMapper development

Priority:

GOOD PYTHON PRACTICES FIRST.

Where compatible with Python, organize the code so it is familiar and understandable to a C# developer.

Do not imitate C# when doing so would produce bad Python.

Target:

Pythonic implementation with C#-friendly organization.

---

# 4. Class and File Naming

Classes:

PascalCase

Example:

KnowledgeReadinessService

Files:

snake_case equivalent of the primary class.

Example:

KnowledgeReadinessService
->
knowledge_readiness_service.py

TargetedEvidenceAnalyzer
->
targeted_evidence_analyzer.py

DocumentRenderer
->
document_renderer.py

When a module has one clear primary class, prefer:

one primary class per file.

Do not mechanically split tiny cohesive structures merely to satisfy one-class-per-file.

Small:

Enums
dataclasses
value objects
protocols
closely related DTOs

may share a module when this improves clarity.

---

# 5. Module Responsibility

Each module should have one understandable responsibility.

Avoid large files mixing:

I/O
validation
business rules
LLM communication
rendering
evidence selection
serialization
security
orchestration

when these responsibilities can reasonably be separated.

Prefer understandable structures such as:

models/
services/
validators/
providers/
analysis/
documentation/
knowledge/
security/
utils/

only when compatible with the existing architecture.

Do not reorganize directories merely for aesthetics.

Every move must have a maintainability justification.

---

# 6. C#-Friendly Organization

Where reasonable, favor conceptual organization familiar to a C# developer:

Models
Services
Validators
Providers
Repositories only where actual repository semantics exist
Factories only where creation complexity justifies them
Interfaces/Protocols only where abstraction is actually useful

Avoid pattern proliferation.

Do NOT introduce:

Repository Pattern
Factory Pattern
Strategy Pattern
Mediator
Dependency Injection containers
interfaces/protocols

merely because they are common in C#.

Use them only when the Python design benefits.

---

# 7. Methods

Methods/functions should:

have one clear responsibility;
use descriptive names;
avoid excessive nesting;
avoid hidden side effects;
avoid unnecessary mutation;
prefer early validation/returns where clearer;
use explicit inputs/outputs.

Break large methods only when decomposition improves comprehension.

Do not create dozens of trivial one-line methods merely to reduce line count.

---

# 8. Mandatory Method Documentation

Every public or significant internal:

class
method
function

must have a concise explanatory docstring.

The intended reader is:

a C# developer who understands software engineering but may not be highly experienced with Python.

Explain simply:

WHAT the method does;
WHY it exists when not obvious;
important input/output behavior;
important side effects or constraints.

Example:

class KnowledgeReadinessService:
"""Validates whether approved V3 documentation can be used as a knowledge source."""

```
def validate(self, context: KnowledgeContext) -> ReadinessResult:
    """
    Validates the approved documentation and returns the final
    knowledge-readiness result without modifying source evidence.
    """
```

Avoid useless documentation such as:

"""Gets value."""

Do not repeat the method name without adding meaning.

---

# 9. Comments

Use comments where they help explain:

non-obvious algorithms;
deterministic guarantees;
security boundaries;
evidence rules;
why a specific implementation exists;
why an apparently simpler approach is unsafe;
LLM boundaries;
immutability requirements.

Avoid comments describing obvious syntax.

Prefer explaining WHY over WHAT when the code already makes WHAT obvious.

---

# 10. Type Hints

Use Python type hints consistently for:

public functions
public methods
service boundaries
models
provider boundaries
important internal transformations

Prefer modern Python typing compatible with the project's supported Python version.

Do not use `Any` unless necessary.

When `Any` is necessary, keep its scope small.

Do not add typing complexity that makes the code harder to understand than the behavior itself.

---

# 11. Models

Review use of:

dataclass
Pydantic
Enum
TypedDict
Protocol

Use the simplest appropriate construct.

Do not migrate models merely for stylistic consistency if the migration creates unnecessary risk.

Preserve serialization contracts exactly where they are externally/canonically consumed.

---

# 12. Constants

Replace unexplained repeated literals with named constants where this improves clarity.

Avoid excessive constant extraction.

Security limits, token limits, statuses and canonical values should have clear ownership.

Do not duplicate canonical status strings across unrelated modules when a safe shared definition already exists or can be introduced without changing serialization.

---

# 13. Error Handling

Make failures explicit and understandable.

Prefer domain-specific exceptions where useful.

Do not:

silently swallow exceptions;
silently repair invalid evidence;
silently downgrade validation failures;
use broad `except Exception` without justification.

Where a broad exception boundary is required, document why.

Preserve existing safe-failure behavior.

---

# 14. Logging

Review runtime diagnostic output.

Logging should help answer:

what stage is running;
what failed;
what artifact was involved;
whether an LLM/provider was called;
whether evidence validation failed.

Never log:

passwords
tokens
credentials
secret connection values
sensitive request payloads

Do not introduce excessive logging.

---

# 15. LLM Boundary

Preserve:

PYTHON DISCOVERS.
LLM INTERPRETS.
HUMAN APPROVES.

Keep provider abstraction clear.

Provider-specific behavior must remain isolated.

No model-specific business logic.

Do not hardcode:

gpt-5.6-luna
Copilot
Gemini

into semantic logic.

Effective provider/model identity remains runtime telemetry.

---

# 16. Deterministic Boundary

Clearly separate deterministic Python responsibilities from LLM interpretation.

A developer reading the code should be able to identify:

discovery
evidence collection
context composition
LLM request
response validation
human review
knowledge readiness

without reverse-engineering large mixed functions.

---

# 17. Runtime Independence

LegacyMapper runtime must remain independent from:

Codex
ChatGPT
manual development prompts

Development prompts under:

codex/

are engineering artifacts only.

Production/runtime Python must not depend on them.

---

# 18. Compatibility

Do not change public runtime entry points without a compatibility layer.

Existing entry points used by tests or documented workflows must continue to function.

If an internal module is moved:

preserve imports where practical

or provide a small compatibility wrapper.

Do not create unnecessary breaking changes immediately before V4.

---

# 19. Dead Code

Identify:

unused helpers
obsolete compatibility code
duplicated implementations
temporary R7/R8/R9 engineering helpers

Do NOT delete code merely because static inspection suggests it is unused.

Before removal establish:

no runtime reference;
no test reference;
no documented entry-point dependency;
no compatibility requirement;
no canonical artifact generation dependency.

Record removals.

If uncertain:

KEEP IT

and document the candidate technical debt.

---

# 20. Tests

Refactor tests where useful for readability.

Preserve behavioral coverage.

Avoid test duplication when safe.

Test names should describe expected behavior.

Do not weaken assertions merely to make refactoring pass.

Do not replace strict validation with permissive validation.

Baseline:

638 PASS

Run full regression repeatedly during refactoring.

Final requirement:

python -m unittest discover -s tests

ALL PASS.

---

# 21. Refactoring Strategy

Do NOT rewrite the entire project at once.

Perform incremental refactoring.

Recommended order:

1. inventory Python modules;
2. classify responsibilities;
3. identify highest-maintenance-risk modules;
4. define target organization;
5. refactor one bounded area;
6. run relevant tests;
7. continue;
8. run full regression;
9. generate documentation from final code state.

Preserve checkpoints locally as appropriate.

---

# 22. Maintainability Audit

Before modifications create a deterministic audit containing:

Python files
classes
functions/methods
approximate module size
modules with multiple responsibilities
modules with large methods
typing coverage indicators
docstring coverage indicators
duplicated responsibility candidates
compatibility entry points

Create:

output/v3_r10/MAINTAINABILITY_AUDIT_BEFORE.json

After refactoring create:

output/v3_r10/MAINTAINABILITY_AUDIT_AFTER.json

And:

output/v3_r10/REFACTORING_MAP.json

The map should explain:

old module/class
new module/class
reason
compatibility impact
tests covering change

Do not treat line count alone as a quality metric.

---

# 23. Permanent Coding Standard

Create:

docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

This document becomes the coding standard for:

V4
V5
future LegacyMapper versions.

Include:

Python-first principle
C#-friendly organization
class/file naming
module responsibilities
docstrings
comments
typing
models
validation
errors
logging
determinism
LLM boundaries
security
tests
compatibility
refactoring rules

Explicitly state:

Python good practices take precedence when a C# convention conflicts with idiomatic Python.

---

# 24. User Manual V3

Create:

docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md

Language:

Spanish.

Audience:

A user/operator of LegacyMapper who does not need to understand the implementation.

Make it human-readable.

Include at minimum:

1. Qué es LegacyMapper V3
2. Objetivo
3. Qué analiza
4. Qué NO hace
5. Requisitos
6. Preparación del entorno
7. Configuración
8. Configuración del repositorio legado
9. Ejecución
10. Flujo completo V3
11. V1/V2/V3 relationship where relevant
12. Archivos de salida
13. Levantamiento Funcional
14. Levantamiento Técnico
15. Revisión humana
16. Estados y decisiones
17. Uso del proveedor LLM
18. Seguridad y privacidad
19. Interpretación de resultados
20. Información parcial
21. Información externa no disponible
22. Knowledge Readiness
23. Qué significa AI_KNOWLEDGE_ALLOWED
24. Qué NO significa AI_KNOWLEDGE_ALLOWED
25. Errores frecuentes
26. Diagnóstico
27. Reejecución segura
28. Qué archivos no deben modificarse
29. Ejemplo de uso
30. Preguntas frecuentes

Commands must reflect actual runtime entry points.

Do not invent CLI commands.

If no unified CLI exists, explain the actual available execution method.

---

# 25. Technical Manual V3

Create:

docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md

Language:

Spanish.

Audience:

Software developer, particularly a C# developer who may have limited Python experience.

Include at minimum:

1. Propósito técnico
2. Arquitectura de LegacyMapper itself
3. Important distinction:
   LegacyMapper architecture vs analyzed legacy-system architecture
4. Directory structure
5. Main modules
6. Main classes
7. Runtime flow
8. V1 pipeline
9. V2 pipeline
10. V3 pipeline
11. Deterministic discovery
12. Context Resolver
13. Context composition
14. Documentation profiles
15. LLMProvider abstraction
16. Copilot adapter
17. Gemini adapter where still applicable
18. Assessment contracts
19. Evidence model
20. Claim model
21. AllowedEvidenceCatalog
22. Human review
23. Deep source analysis
24. Deep interpretation
25. Knowledge readiness
26. Knowledge projection
27. Knowledge boundary
28. Security model
29. Immutability guarantees
30. Error handling
31. Tests
32. How to run tests
33. How to add a module
34. How to add a class
35. Naming conventions
36. Why class names and file names differ by PascalCase/snake_case
37. Type hints
38. Docstrings/comments
39. How to add a provider
40. How to change context budgeting
41. How to extend evidence types
42. How to extend human review
43. How to debug a failed validation
44. How to inspect generated artifacts
45. Compatibility requirements
46. Known limitations
47. Technical debt intentionally preserved
48. Guidelines for V4/V5
49. Safe modification checklist
50. Regression checklist

Use examples from actual code after refactoring.

Do not document nonexistent abstractions.

---

# 26. Documentation Quality

Manuals must be understandable documents, not raw machine reports.

Prefer:

clear headings
short paragraphs
tables where useful
small examples
real paths
real class/module names

Avoid:

massive evidence dumps
internal Codex history
R7/R8 debugging chronology unless technically relevant
unnecessary hashes

The technical manual should allow another developer to modify LegacyMapper safely without needing this conversation.

---

# 27. Preserve V3 Knowledge State

R10 must preserve:

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

Do not generate AI_KNOWLEDGE.

R10 refactoring must not alter R9 knowledge projection semantics.

After refactoring rerun the R9 readiness validation.

Expected:

READINESS=READY

If R9 no longer returns READY:

R10 FAILS.

Stop and report regression.

---

# 28. Security

Preserve all existing security guarantees.

No legacy source modification.

No secrets in manuals.

No credentials in examples.

No external provider calls are required for R10.

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

Do not use an LLM to rewrite project code during runtime.

Codex may perform the development refactoring as the authorized engineering agent.

---

# 29. Immutability

Verify:

LEGACY_SOURCE_IMMUTABILITY
V2_CANONICAL_EVIDENCE_INTEGRITY
R8_HUMAN_DECISION_INTEGRITY
R9_KNOWLEDGE_SEMANTICS_INTEGRITY

Generated engineering/documentation artifacts may change only within R10-authorized scope.

---

# 30. Required Outputs

Create:

output/v3_r10/MAINTAINABILITY_AUDIT_BEFORE.json
output/v3_r10/MAINTAINABILITY_AUDIT_AFTER.json
output/v3_r10/REFACTORING_MAP.json

Create:

docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

Create:

docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md
docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md

Create result:

codex/V3/V3_R10_CODE_QUALITY_MAINTAINABILITY_DOCUMENTATION_RESULTADO.md

---

# 31. Final Validation

Run:

python -m unittest discover -s tests

Then rerun the deterministic R9 Knowledge Readiness Gate using its actual runtime entry point/API without overwriting canonical human decisions.

Validate:

638 baseline tests remain behaviorally covered;
all current tests PASS;
READINESS=READY;
AI_KNOWLEDGE_ALLOWED=true;
AI_KNOWLEDGE_GENERATED=false;
source immutable;
knowledge semantics unchanged;
security PASS.

---

# 32. Result Report

Required fields:

STATUS
FILES_CHANGED
MODULES_ANALYZED
MODULES_REFACTORED
CLASSES_CREATED
CLASSES_MOVED
METHODS_DOCUMENTED
TYPE_HINT_COVERAGE_BEFORE
TYPE_HINT_COVERAGE_AFTER
DOCSTRING_COVERAGE_BEFORE
DOCSTRING_COVERAGE_AFTER
DUPLICATION_REDUCED
COMPATIBILITY_WRAPPERS
DEAD_CODE_REMOVED
TECHNICAL_DEBT_PRESERVED
PYTHON_STANDARD_CREATED
USER_MANUAL_CREATED
TECHNICAL_MANUAL_CREATED
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

---

# 33. Success

Expected:

STATUS=
V3-R10_CODE_QUALITY_MAINTAINABILITY_DOCUMENTATION_COMPLETE

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

PYTHON_STANDARD_CREATED=
true

USER_MANUAL_CREATED=
true

TECHNICAL_MANUAL_CREATED=
true

DECISION=
V3_ENGINEERING_QUALITY_VALIDATED

NEXT=
V3_FINAL_CLOSURE_REVIEW

Do not declare V3 closed automatically.

Stop after report generation.