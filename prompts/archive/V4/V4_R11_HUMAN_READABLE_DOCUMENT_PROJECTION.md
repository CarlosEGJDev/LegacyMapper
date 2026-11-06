# LegacyMapper V4 — R11 Human-Readable Document Projection

TASK=V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION

MODE=DETERMINISTIC_HUMAN_READABLE_PROJECTION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Implement V4-R11:

```text id="7f3t18"
Human-Readable Document Projection
```

R10 established one canonical approved Knowledge Source.

R11 must project that canonical knowledge into deterministic, human-readable documentation.

Fundamental architecture:

```text id="qmy9mr"
Canonical Knowledge Source (R10)
              │
              │ deterministic projection
              ▼
      Human-Readable Projection
              │
              ▼
          Markdown
```

The Markdown output is a projection.

It is NOT:

* a second Knowledge Source;
* an independent truth store;
* a replacement for canonical knowledge;
* a new approval system;
* a place where new knowledge is inferred;
* a Plugin-facing payload.

Required invariant:

```text id="0r9mxb"
MARKDOWN_IS_PROJECTION=true
MARKDOWN_IS_CANONICAL_SOURCE=false
```

---

# Required Reading

Read in this order:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. `docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md`
9. `docs/V4/V4_R10_CLOSURE_AND_VERSIONING_RESULT.md`
10. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json`
11. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json`
12. `legacy_documenter/knowledge/canonical/models.py`
13. `legacy_documenter/knowledge/canonical/service.py`
14. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
15. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Also inspect existing V3 human-readable documentation generation components before implementing anything.

Reuse or adapt existing deterministic rendering infrastructure where appropriate.

Do not duplicate a capability merely because it originated in V3.

---

# Entry Gate

Before implementation verify:

```text id="qvvls5"
latest_completed_round = V4-R10
latest_approved_round = V4-R10

current_round_in_progress = null

round_status = V4-R10_APPROVED
next = V4-R11

tests >= 1163

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Also verify:

```text id="h1n6ca"
git status
```

Expected:

```text id="06vk7u"
CLEAN
```

If R10 is not formally approved and closed:

STOP.

If unrelated user work is present:

STOP and report it.

Do not silently reconcile repository state.

---

# Fundamental R11 Rules

R11 consumes R10 canonical knowledge.

R11 must NOT:

* mutate canonical knowledge;
* create canonical knowledge;
* approve canonical knowledge;
* reject canonical knowledge;
* modify R8 proposals;
* modify R9 approvals;
* reinterpret source material;
* infer new facts from free text;
* change KnowledgeStatus;
* change SourceType;
* change KnowledgeNature;
* infer temporal state;
* resolve conflicts;
* fill gaps;
* supersede knowledge;
* call an AI model;
* call a provider.

Required:

```text id="pxegfu"
CANONICAL_INPUT_READ_ONLY=true
```

---

# One Canonical Source

Preserve:

```text id="zm9cmz"
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

R11 creates views of that source.

It must never create concepts equivalent to:

```text id="fdb89z"
human_truth
document_truth
functional_truth
technical_truth
markdown_truth
```

Required:

```text id="d4prvo"
DOCUMENT_PROJECTION != CANONICAL_KNOWLEDGE_SOURCE
```

---

# Human Documentation Structure

The initial target information architecture is:

```text id="c84jfr"
00-el-area/
01-gobernanza/
02-flujos/
03-desarrollo-de-software/
04-arquitecturas-de-referencia/
05-plantillas/
06-catalogo/
07-proyectos/
08-historial/
09-capacitacion/
```

This structure is a projection/navigation concern.

It is NOT the canonical domain model.

Do NOT create one Python domain class per folder or document family.

Required:

```text id="g4pgsa"
DOCUMENT_STRUCTURE_IS_PROJECTION_CONCERN=true
DOCUMENT_STRUCTURE_IS_DOMAIN_MODEL=false
```

---

# Initial Target Documents

Support the following initial document paths.

## 00 — El área

```text id="0a8s6q"
00-el-area/que-es-el-area.md
00-el-area/funciones.md
00-el-area/equipo-y-roles.md
00-el-area/espacios-de-trabajo.md
00-el-area/primer-dia.md
00-el-area/glosario.md
```

Purpose:

```text id="wutg7s"
ONBOARDING / CONTEXT
```

---

## 01 — Gobernanza

```text id="4j4b7q"
01-gobernanza/fuente-de-verdad.md
01-gobernanza/ramas-y-versionamiento.md
01-gobernanza/gestion-del-tablero.md
01-gobernanza/seguridad-y-datos.md
01-gobernanza/imputacion-y-reporte.md
```

Purpose:

```text id="q2vvxv"
NORMA
```

Important:

The historical reference structure may use the human phrase "fuente de verdad" as a document filename.

That filename MUST NOT redefine the V4 architectural concept.

Architecturally:

```text id="6gwhpd"
Canonical Knowledge Source = Fuente de Conocimiento
```

The projected filename:

```text id="ur4y4f"
fuente-de-verdad.md
```

is only a human-facing document name retained from the target information architecture.

Do not create a second truth source.

---

## 02 — Flujos

```text id="5hw3ki"
02-flujos/desarrollo-en-blanco.md
02-flujos/desarrollo-evolutivo-y-soporte.md
02-flujos/ingesta-y-actualizacion-de-contexto.md
02-flujos/acompanamiento.md
02-flujos/soporte-y-capacitacion.md
02-flujos/propuesta-preventa.md
```

Purpose:

```text id="w7bx4x"
FLUJO
```

---

## 03 — Desarrollo de software

Support projection categories covering:

* methodology;
* Definition of Done;
* deliverables;
* coding standards;
* naming standards;
* configuration standards;
* source-control standards;
* development-environment standards;
* design principles;
* patterns;
* anti-patterns;
* DevSecOps;
* pipeline;
* quality;
* security;
* environments.

Do not invent content when canonical knowledge does not contain it.

---

## 04 — Arquitecturas de referencia

Initial target documents:

```text id="fmg3y7"
04-arquitecturas-de-referencia/herramientas.md
04-arquitecturas-de-referencia/agentes.md
04-arquitecturas-de-referencia/capacidades.md
04-arquitecturas-de-referencia/plataforma-agentica.md
```

Purpose:

```text id="4kxt48"
NORMA / REFERENCE ARCHITECTURE
```

Preserve conceptual distinctions if canonical knowledge contains them:

```text id="n2a9c1"
AGENT != CAPABILITY
```

Agent concept:

```text id="4wqqmy"
single responsibility
judgment
mission
inputs
outputs
limits
human approval
model profile
```

Capability concept:

```text id="fp5qk7"
action without judgment
procedure/script/connector
declared degradation
external credentials outside package
```

R11 must not manufacture these statements if they are absent from canonical knowledge.

---

## 05 — Plantillas

Projection family:

```text id="8esvy7"
05-plantillas/
```

Purpose:

```text id="xk18om"
PLANTILLA
```

---

## 06 — Catálogo

Projection family:

```text id="fajrgm"
06-catalogo/
```

Purpose:

```text id="47m3bb"
LEVANTAMIENTO / CURRENT INVENTORY
```

Critical:

```text id="chv5y8"
CATALOG != NORM
```

Current inventory must never automatically become a standard.

---

## 07 — Proyectos

Projection family:

```text id="64bz4d"
07-proyectos/
```

Purpose:

```text id="l7fb35"
PROJECT
```

One folder may represent one project/accompaniment when canonical knowledge explicitly supports that grouping.

Do not invent projects from text similarity.

The projected project documentation may contain references to external official documents, but R11 must not fetch or modify external systems.

---

## 08 — Historial

Projection family:

```text id="54p4xv"
08-historial/
```

Purpose:

```text id="a0phvh"
DECISIONS / RESOLUTIONS / LESSONS / HISTORY
```

Historical projection must preserve temporal meaning.

Do not mark an item SUPERSEDED merely because it appears in history.

---

## 09 — Capacitación

Projection family:

```text id="eqpjh6"
09-capacitacion/
```

Purpose:

```text id="t62ob6"
TRAINING / FORMATION
```

---

# Projection Mapping

R11 needs an explicit deterministic projection mapping.

The mapping may use only structured canonical fields such as:

```text id="l08ukc"
source_type
nature
status
temporal_state
metadata
related_statement_ids
```

Do not classify by semantic interpretation of free text.

Preferred approach:

```text id="1am9in"
ProjectionRule
ProjectionTarget
ProjectionManifest
```

These are projection-layer concepts, not canonical-domain concepts.

A rule should explicitly declare the structured conditions under which a canonical entry is projected into a target document.

Example conceptually:

```text id="amz6u8"
KnowledgeNature.NORMA
+
explicit projection metadata/category
        ↓
01-gobernanza/<known-target>.md
```

Do NOT implement rules such as:

```text id="o1q1cn"
if "security" in statement.lower():
    -> seguridad-y-datos.md
```

That would be semantic inference from free text and is forbidden.

---

# Missing Mapping Policy

A canonical entry that cannot be mapped deterministically must NOT disappear.

Required outcome:

```text id="cqvy3q"
UNMAPPED
```

The projection manifest must report it.

Required:

```text id="33wq1a"
UNMAPPED_CANONICAL_ENTRY != ERROR
UNMAPPED_CANONICAL_ENTRY != DELETED
UNMAPPED_CANONICAL_ENTRY != AUTO_CLASSIFIED
```

The system must preserve its canonical id for later configuration/review.

---

# Multi-Projection Policy

A canonical statement may legitimately appear in more than one human document if explicit projection rules require it.

This does NOT duplicate canonical knowledge.

Required:

```text id="87ndzf"
ONE_CANONICAL_ENTRY
MAY_HAVE_MULTIPLE_DOCUMENT_PROJECTIONS
```

Every projected occurrence must retain the same canonical knowledge id.

---

# Traceability in Human Documents

Every rendered knowledge item must remain traceable to its canonical entry.

At minimum retain:

```text id="7o95ob"
knowledge_id
```

Prefer human-readable traceability metadata that does not overwhelm normal reading.

Possible representation:

```text id="xkbw11"
<!-- knowledge_id: KNO-... -->
```

or another deterministic non-invasive format.

Choose one stable format and document it in the contract.

Do not expose sensitive internal metadata unnecessarily.

---

# Human Readability

The generated Markdown should be usable by a human, not merely a JSON dump wrapped in Markdown.

Provide deterministic structural elements such as:

* title;
* short projection metadata;
* sections;
* knowledge statements;
* status where useful;
* temporal context where useful;
* traceability marker.

Do not add AI-generated explanatory prose.

Do not summarize or paraphrase canonical statements unless an already-approved canonical field explicitly contains that text.

Canonical statement content must remain semantically unchanged.

---

# Empty Documents

Do not invent filler content.

For configured target documents with no matching canonical knowledge, choose one explicit deterministic policy.

Preferred:

```text id="ld0k0o"
GENERATE_EMPTY_DOCUMENT_WITH_EXPLICIT_NO_APPROVED_KNOWLEDGE_MARKER
```

Example concept:

```text id="frw1qj"
No approved canonical knowledge is currently projected to this document.
```

This marker is projection metadata, not new domain knowledge.

The contract must state the selected policy.

---

# Deterministic Ordering

Documents must be byte-identical for identical canonical input and projection configuration.

Define stable ordering.

Preferred:

```text id="yrgwmj"
document path
temporal_state
knowledge nature
knowledge_id
```

or another explicit deterministic order.

Do not rely on:

* insertion timing;
* filesystem enumeration order;
* Python object identity;
* current date/time;
* locale-dependent implicit sorting.

---

# Projection Manifest

Generate a deterministic manifest describing the projection.

Suggested model:

```text id="ld6xzl"
ProjectionManifest
```

It should report at minimum:

```text id="54q60v"
canonical_entry_count
projected_canonical_entry_count
unmapped_canonical_entry_count
document_count
non_empty_document_count
empty_document_count
projection_occurrence_count
```

and mappings:

```text id="9foaf3"
knowledge_id
→
document path(s)
```

plus:

```text id="h5m2v6"
unmapped knowledge_ids
```

This manifest is projection metadata.

It is NOT canonical knowledge.

---

# Output API

Prefer an in-memory deterministic projection API.

Suggested package:

```text id="tkfhk9"
legacy_documenter/knowledge/projection/
```

Possible files:

```text id="5xtifn"
__init__.py
models.py
rules.py
service.py
markdown_renderer.py
contract_report.py
example_report.py
```

Use the minimum structure that remains clear and maintainable.

Do not mechanically create files if responsibilities are too small.

Follow:

```text id="zt0g3u"
docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md
```

---

# Separation of Projection and File I/O

Core projection logic should operate in memory.

Preferred architecture:

```text id="b4jx5a"
CanonicalKnowledgeCollection
        ↓
ProjectionService
        ↓
DocumentProjection objects
        ↓
MarkdownRenderer
        ↓
rendered strings
```

Writing rendered Markdown to disk, if implemented, must be isolated from domain/projection decisions.

No projection semantics may depend on filesystem state.

---

# Required Human-Readable Example Output

Generate a deterministic synthetic documentation tree under:

```text id="adf7mt"
output/v4_r11/example_docs/
```

This is a test/example projection only.

It must NOT be presented as real approved organizational documentation.

Use synthetic canonical entries.

The example should demonstrate at least:

1. one governance/norma entry;
2. one flow entry;
3. one architecture/reference entry;
4. one catalog/current-inventory entry;
5. one historical entry;
6. one human-information-only entry;
7. one AS_IS entry;
8. one TO_BE entry;
9. one canonical entry projected into two documents through explicit rules;
10. one unmapped canonical entry;
11. at least one configured empty document.

Every rendered non-empty item must remain traceable to its `KNO-` id.

---

# Contract Artifact

Generate:

```text id="5dh4i3"
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json
```

It must document at minimum:

```text id="ocvjhp"
projection_model
projection_rule_model
target_model
manifest_model

canonical_input_policy
canonical_mutation_policy

document_structure_policy
document_structure_is_domain_model

mapping_policy
free_text_inference_policy
unmapped_policy
multi_projection_policy

traceability_policy
canonical_id_visibility_policy

human_readability_policy
canonical_statement_preservation_policy

empty_document_policy

ordering_policy
deterministic_identity_policy

file_io_boundary

R12_boundary

AI_policy
provider_policy
security_policy
```

Must explicitly state:

```text id="cmx3qd"
ONE_CANONICAL_KNOWLEDGE_SOURCE
MARKDOWN_IS_PROJECTION
MARKDOWN_IS_NOT_CANONICAL_KNOWLEDGE
CANONICAL_INPUT_READ_ONLY
DOCUMENT_STRUCTURE_IS_PROJECTION_CONCERN
DOCUMENT_STRUCTURE_IS_NOT_DOMAIN_MODEL
NO_FREE_TEXT_SEMANTIC_MAPPING
UNMAPPED_ENTRIES_ARE_PRESERVED
MULTIPLE_DOCUMENT_PROJECTIONS_DO_NOT_DUPLICATE_CANONICAL_KNOWLEDGE
EVERY_PROJECTED_ITEM_RETAINS_CANONICAL_KNOWLEDGE_ID
EMPTY_DOCUMENTS_DO_NOT_INVENT_KNOWLEDGE
R11_DOES_NOT_IMPLEMENT_PLUGIN_PAYLOAD
AI_NEVER_DECIDES_DOCUMENT_MAPPING
```

---

# Example Artifact

Generate:

```text id="nhwjz3"
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json
```

It must summarize the synthetic projection and reference the generated example Markdown tree.

It must include the required scenarios.

---

# Determinism

Generate the contract and example independently at least twice.

Require byte-identical results.

Also regenerate the synthetic Markdown projection tree and verify identical relative paths and bytes.

Required:

```text id="hbs2au"
CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS
MARKDOWN_TREE_DETERMINISM=PASS
```

---

# Security

Treat all canonical text and metadata as untrusted display data.

R11 must not execute it.

Forbidden:

```text id="96bx4a"
eval
exec
dynamic import from content
shell execution from content
template-code execution from content
filesystem path selection from untrusted free text
```

Projection paths must come from validated projection configuration / closed target definitions.

Prevent:

```text id="eohx7k"
../
absolute paths
drive-qualified paths
path traversal
```

when target paths are accepted by projection configuration.

Markdown content containing prompt-injection-shaped text remains inert display content.

No secret may be introduced into committed artifacts.

---

# AI Boundary

Required:

```text id="r3vp28"
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

R11 is deterministic.

Do not invoke Copilot, Gemini, OpenAI, Anthropic, Ollama, or any provider.

Do not use an AI model to decide where knowledge belongs.

If a canonical entry lacks sufficient structured mapping information:

```text id="qlqed7"
UNMAPPED
```

not AI classification.

---

# R12 Boundary

R11 must NOT implement:

```text id="wtcd6p"
Plugin payload
Plugin schema
Plugin consumer API
agent context package
machine-readable Plugin contract
```

R12 will project the same R10 canonical Knowledge Source independently.

Required architecture:

```text id="z0fsxt"
                 Canonical Knowledge Source
                          │
                 ┌────────┴────────┐
                 ↓                 ↓
                R11               R12
         Human projection    Plugin projection
```

R12 must NOT consume R11 Markdown as its source.

Required:

```text id="4q7x04"
R12_SOURCE=CANONICAL_KNOWLEDGE_SOURCE
R12_SOURCE!=R11_MARKDOWN
```

---

# Tests

Add deterministic tests covering at minimum:

## Entry Gate

* R10 formally approved;
* repository continuity;
* baseline >=1163.

## Canonical Boundary

* canonical input read-only;
* no canonical creation;
* no proposal mutation;
* no approval mutation;
* no relation mutation;
* no status mutation;
* no temporal mutation.

## Mapping

* explicit structured mapping;
* no free-text semantic mapping;
* known target mapping;
* unmapped preserved;
* multi-document projection;
* canonical id retained.

## Structure

* initial 00–09 families represented as projection targets/configuration;
* no one-domain-class-per-folder architecture;
* catalog != norm;
* historical != superseded.

## Rendering

* deterministic Markdown;
* human-readable title/sections;
* canonical statement preserved;
* traceability marker;
* empty-document policy;
* no invented explanatory content.

## Manifest

* counts correct;
* knowledge → document mappings correct;
* unmapped IDs correct;
* multi-projection counts correct.

## Temporal

* AS_IS preserved;
* TO_BE preserved;
* HISTORICAL preserved;
* no automatic conflict/supersession.

## Security

* prompt injection inert;
* HTML/Markdown-shaped content inert;
* path traversal rejected;
* absolute path rejected;
* drive-qualified path rejected;
* no execution primitives;
* no secret leakage through fixed exception messages.

## AI Boundary

* zero provider calls;
* zero real LLM calls;
* no provider imports in projection package;
* no AI mapping.

## R12 Boundary

* no Plugin payload;
* no Plugin schema;
* no Plugin-facing context.

## Determinism

* contract deterministic;
* example deterministic;
* Markdown tree deterministic.

## Regression

Run full suite.

Expected:

```text id="3x2dks"
>1163 PASS
```

Do not reduce existing coverage.

---

# PROJECT_STATE After Successful Implementation

Update using the existing schema:

```text id="ep85rb"
latest_completed_round = V4-R11
latest_approved_round = V4-R10

current_round_in_progress =
"V4-R11 (pending Technical Lead review)"

round_status =
V4-R11_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R11

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R11 approved.

---

# Required Result Document

Create:

```text id="xkvwlr"
docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md
```

Report at minimum:

```text id="29jx2v"
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

PROJECTION_MODEL
PROJECTION_RULE_MODEL
TARGET_MODEL
MANIFEST_MODEL

CANONICAL_SOURCE_POLICY
CANONICAL_INPUT_MUTATION

DOCUMENT_STRUCTURE_POLICY

MAPPING_POLICY
FREE_TEXT_MAPPING
UNMAPPED_POLICY
MULTI_PROJECTION_POLICY

TRACEABILITY_POLICY
CANONICAL_ID_VISIBILITY

HUMAN_READABILITY_POLICY
CANONICAL_STATEMENT_PRESERVATION

EMPTY_DOCUMENT_POLICY
ORDERING_POLICY

FILE_IO_BOUNDARY

AI_CALLS
PROVIDER_CALLS

R12_BOUNDARY

SECURITY
PATH_SAFETY

CONTRACT_ARTIFACT
CONTRACT_SHA256

EXAMPLE_ARTIFACT
EXAMPLE_SHA256

EXAMPLE_DOCS_ROOT
EXAMPLE_DOCS_FILE_COUNT

CONTRACT_DETERMINISM
EXAMPLE_DETERMINISM
MARKDOWN_TREE_DETERMINISM

V3_REGRESSION
V4_R1_REGRESSION
V4_R2_REGRESSION
V4_R3_REGRESSION
V4_R4_REGRESSION
V4_R5_REGRESSION
V4_R6_REGRESSION
V4_R7_REGRESSION
V4_R8_REGRESSION
V4_R9_REGRESSION
V4_R10_REGRESSION

READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED

REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

PRODUCTION_BEHAVIOR_CHANGED
TECHNICAL_DEBT

DECISION
NEXT
```

---

# Expected Success State

```text id="19j60v"
STATUS=V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>1163_PASS

CANONICAL_SOURCE_POLICY=ONE_CANONICAL_KNOWLEDGE_SOURCE
CANONICAL_INPUT_MUTATION=NONE

DOCUMENT_STRUCTURE_POLICY=PROJECTION_ONLY

MAPPING_POLICY=EXPLICIT_STRUCTURED_RULES_ONLY
FREE_TEXT_MAPPING=FORBIDDEN

UNMAPPED_POLICY=PRESERVE_AND_REPORT
MULTI_PROJECTION_POLICY=ALLOWED_WITH_SAME_CANONICAL_ID

TRACEABILITY_POLICY=CANONICAL_ID_PRESERVED

EMPTY_DOCUMENT_POLICY=NO_KNOWLEDGE_INVENTED

AI_CALLS=0
PROVIDER_CALLS=0

R12_BOUNDARY=PASS

SECURITY=PASS
PATH_SAFETY=PASS

CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS
MARKDOWN_TREE_DETERMINISM=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_R11_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R11
```

---

# Stop Condition

After implementation, tests, deterministic artifact generation and result documentation:

STOP.

Do NOT:

* approve R11;
* commit;
* push;
* implement R12;
* create a Plugin payload;
* use R11 Markdown as machine-readable Plugin knowledge.

The next action is:

```text id="tq2m98"
HUMAN_REVIEW_V4_R11
```
