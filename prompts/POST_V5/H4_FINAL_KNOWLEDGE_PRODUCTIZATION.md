# LegacyMapper Post-V5 — H4 Final Knowledge Productization

## Objective

Perform the final H4 productization step before formal closure.

This is **not H4-R6**.
This is **not H5**.
Do not start V6.
Do not reopen the deterministic architecture, Evidence Core, portability gates, or cross-project resolver.

The purpose is to align LegacyMapper with its intended final product:

> **A reliable source of knowledge with two primary consumers: humans and AI.**

The output should no longer expose the internal processing pipeline as the product.

The human output must be concise, explanatory and focused on what LegacyMapper actually knows.

The AI output must be structured, complete and useful for future maintenance, modernization, migration and automated reasoning.

---

# 1. Current state

Treat as already complete and valid:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS
PRE_H5_GATE_C_FINAL_HARDENING = PASS
PRE_H5_BLOCKING_DEBT = 0
```

Current H4 state:

```text
H4_FINAL_HUMAN_CONTENT_POLISH = READY_FOR_HUMAN_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

The owner approves the direction but requests these final product changes:

```text
1. AI interpretation must be simpler, shorter and more explanatory.
2. Human documentation must focus on useful known behavior, not analysis metrics.
3. Product output must be simplified into human knowledge and AI knowledge.
4. Internal artifacts must remain available but not dominate the user-facing structure.
5. Human-confirmed domain knowledge must be supported.
6. Final full suite must be green.
```

---

# 2. Product model

LegacyMapper must expose two primary knowledge products:

```text
HUMAN KNOWLEDGE
AI KNOWLEDGE
```

Internal Evidence, logs, manifests, validation, raw AI responses and diagnostics remain necessary, but they are implementation/support artifacts.

Final conceptual output:

```text
output\
    human\
    ai\
    internal\
```

---

# 3. Human output

Target:

```text
output\human\
```

Recommended structure:

```text
human\
    index.html
    LegacyMapper.pdf
    executive.pdf
    functional\
    technical\
    diagrams\
```

Equivalent structure is acceptable if technically cleaner, but the human user must see a single obvious entry point.

The user should not have to understand folders such as:

```text
human_default
human_executive
docs
visuals
behavioral
package
```

Those concepts may still exist internally, but they should not define the public output structure.

---

# 4. AI output

Target:

```text
output\ai\
```

This is the machine-oriented knowledge product.

It must be useful to another AI for:

```text
understanding architecture
planning changes
impact analysis
maintenance
modernization
migration
reimplementation
technical documentation
reasoning over flows and dependencies
```

Recommended structured projections:

```text
ai\
    knowledge.json
    architecture.json
    solutions.json
    projects.json
    modules.json
    views.json
    flows.json
    dependencies.json
    data.json
    external_boundaries.json
    unresolved.json
    provenance.json
```

Exact filenames may differ if the current contracts suggest a better mapping.

Do not duplicate the same full semantic model unnecessarily across many files.

Prefer:

```text
one authoritative machine-readable knowledge model
+
small projections/indexes optimized for AI consumption
```

The AI knowledge output must preserve:

```text
entity identities
status
relationships
technical symbols
source references
provenance
confidence/state
confirmed/inferred/unresolved distinctions
human-confirmed knowledge
```

---

# 5. Internal output

Target:

```text
output\internal\
```

Move or project support artifacts here:

```text
Evidence
baseline
raw AI responses
validation reports
logs
manifests
diagnostics
request IDs
hashes
analysis metrics
intermediate render models
```

Do not break reproducibility or existing internal contracts.

If a compatibility layer is needed:

```text
keep old paths as aliases/compatibility projections temporarily
```

but the public documented contract must point users to:

```text
human\
ai\
internal\
```

---

# 6. AI interpretation style — change required

The current persisted H4 AI interpretation still contains analysis-oriented metrics.

Update the AI interpretation prompt so that future real interpretations are:

```text
simple
concise
explanatory
behavior-focused
name-focused
relationship-focused
```

The AI should explain:

```text
what the project appears to do
what each relevant view does
what actions are available
what other views/components are related
what business/service/data path is followed
what data/procedures are reached
what remains indeterminate when materially relevant
```

The AI should NOT focus on:

```text
number of calls
number of facts
number of controls
number of unresolved calls
number of Evidence records
request counts
candidate counts
coverage percentages
internal validator metrics
```

Counts are only allowed when they communicate useful scope, e.g.:

```text
Project X contains 42 views
```

and only when the names/list are also available.

---

# 7. Required AI prompt principle

Add an explicit instruction equivalent to:

> Explain the system for a human reader. Focus on what is known, what the component does, how it behaves, what it calls, what it opens, and what data it reaches. Prefer concrete names and relationships over counts. Avoid analysis statistics. If something is not known, mention it briefly only when it materially affects understanding; do not make uncertainty the main narrative.

For technical interpretation:

> Prefer execution routes using actual symbols:
> View → Event → Handler → Business Method → Cross-Project Method → Data Method → Stored Procedure / SQL → Database/Boundary.

Do not expose Evidence IDs in prose.

---

# 8. New real AI interpretation is authorized

For this round, unlike the previous polish, a **new Copilot interpretation is explicitly authorized** because the AI prose itself must change.

Use the existing supported provider:

```text
provider_id = copilot-local
```

Use:

```text
model_id = gpt-6-luna
```

unless the current provider contract requires a different exact model identifier.

Important:

```text
DO NOT re-run scanner/analyzer
DO NOT rebuild Evidence
DO NOT re-read source
```

Use the existing persisted analyzer-v4 baseline from the successful real H4 run.

This round may call the AI provider only for the new interpretation.

Record provider/model/request details internally, not in the human narrative.

---

# 9. Human-confirmed domain knowledge

Implement a minimal supported mechanism for human-confirmed domain knowledge.

Use the current canonical/review model where possible.

Do not create a competing truth system unless unavoidable.

Desired capability:

```text
COB = Cobranza
WebCob = project associated with Cobranza
Mantencion = maintenance-related functional area
Morosidad = delinquency/debt-related functional area
```

These are examples only.

Do not pre-populate them unless explicitly provided by the owner.

The mechanism should allow future input in an explicit structured format such as:

```json
{
  "terms": [
    {
      "term": "COB",
      "meaning": "Cobranza",
      "status": "CANONICAL",
      "source": "human"
    }
  ]
}
```

or an equivalent current-contract format.

Human-confirmed knowledge must be usable by human documentation, AI knowledge projection, future AI interpretation context, and module/functional grouping, but must never be confused with deterministic source evidence.

---

# 10. Human documentation rules

Continue enforcing the previous polish rules.

Human documentation should emphasize:

```text
project names
module names if known
view names
visible titles
what each view does
main actions
view relationships
technical route
data/procedure reached
diagrams
tables
wireframes
```

Avoid repetitive filler.

Example:

```text
Project: WebPREPrevencion

Views
- ucPreMantJerarquia2 — Mantención de Jerarquías
- ucBusSuc — Buscar Centro de Trabajo
- ucPreMantEmpadronamiento — Empadronamiento Comité Paritario
...
```

Technical example:

```text
ucPreMantJerarquia2
→ hypAsignar.Click
→ hypAsignar_Click
→ PreGesJerarquia.txcrear
→ sysPreGesJerarquia.crear
→ PPRE_GES_JERARQUIA.CREAR
```

If the tail is unknown:

```text
→ destino posterior indeterminado
```

Do not explain the same uncertainty repeatedly.

---

# 11. Audience model

Keep audience differentiation, but expose it under one human knowledge product.

Recommended:

```text
human\
    index.html
    executive\
    functional\
    technical\
```

or equivalent navigation.

The experience must feel like **one documentation system**, not separate duplicated products.

Executive:
- system
- projects
- functional areas
- major capabilities
- major dependencies
- important data systems

Functional:
- projects
- modules
- views
- what users can do
- flows
- relations between screens

Technical:
- views
- events
- handlers
- methods
- cross-project calls
- data routes
- stored procedures
- external boundaries

---

# 12. Avoid duplication

The same explanation must not be copied across executive, functional, and technical without purpose.

Prefer shared canonical semantic content projected differently.

Rule:

> **One semantic knowledge source, multiple audience projections.**

---

# 13. Compatibility

Do not break existing tests/contracts unnecessarily.

If existing commands currently write:

```text
baseline
ai
docs
visuals
human_default
human_executive
```

implement a final packaging/projection layer that produces:

```text
human
ai
internal
```

from those outputs.

Do not force the user to manually assemble folders.

---

# 14. Public knowledge manifest

Create a top-level manifest, e.g.:

```text
KNOWLEDGE_PACKAGE.json
```

with:

```text
schema_version
source logical identity
human_entry_point
ai_entry_point
internal_artifacts_path
solution/project coverage
AI provider/model provenance
deterministic evidence fingerprint
```

Only include timestamps if consistent with current deterministic-output rules.

---

# 15. Tests

Add targeted tests for:

```text
human/ai/internal final package structure
single obvious human entry point
AI structured knowledge entry point
internal artifacts separated
old compatibility paths still safe if required
new AI prompt excludes analysis metrics from narrative
real names preferred over counts
technical routes preserved
unresolved grouped
human-confirmed knowledge can be loaded
human-confirmed knowledge is distinguishable from Evidence
same semantic truth across human and AI projections
no source read during interpretation/rendering
no scanner/analyzer rerun
```

Do not use the real provider in automated tests.

Mock/fake provider for prompt contract tests.

---

# 16. Real validation for this round

After implementation is stable:

Use the existing real H4 baseline:

```text
C:\PruebasLegacyMapper\runs\manual_validation\baseline
```

or the actual persisted baseline location if different.

Do not run analysis again.

Perform:

```text
new real Copilot interpretation
human knowledge projection
AI knowledge projection
internal packaging
```

Use:

```text
WebPREPrevencion
slnPREPrevencion_2010
```

as the H4 validation target.

Generate review output under a new folder, e.g.:

```text
C:\PruebasLegacyMapper\Resultados\h4_final_knowledge_productization\
```

Do not overwrite previous artifacts.

---

# 17. Human review package

The owner should only need to inspect:

```text
human\index.html
human\LegacyMapper.pdf
human\executive.pdf
ai\knowledge.json
KNOWLEDGE_PACKAGE.json
```

Optionally include `REVIEW_GUIDE.md`.

Review questions:

```text
Does the human documentation explain the project clearly?
Is the AI prose concise?
Are useful names/relations shown?
Are useless counts absent?
Is uncertainty grouped?
Is technical routing useful?
Is the AI knowledge package structured enough for future maintenance/migration?
Is the folder structure understandable?
```

---

# 18. Final suite requirement

The previous H4 content polish full suite initially had one inventory snapshot failure and then only targeted tests were rerun.

Before this round can be considered complete:

```text
run the full suite exactly once after all final changes are stable
```

Required:

```text
python -X utf8 -m unittest discover -s tests
```

Must finish with:

```text
0 failures
0 errors
```

Do not close H4 with a non-green final full suite.

---

# 19. Result report

Create:

```text
docs/POST_V5/H4_FINAL_KNOWLEDGE_PRODUCTIZATION_RESULT.md
```

Include:

```text
final output structure
AI prompt/style changes
real provider/model used
real provider call count
proof of zero scanner/analyzer rerun
human-confirmed domain knowledge mechanism
human package contents
AI package contents
internal package contents
compatibility behavior
targeted tests
full suite result
human review paths
```

---

# 20. Final state

If technically successful:

```text
H4_FINAL_KNOWLEDGE_PRODUCTIZATION = READY_FOR_HUMAN_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

The owner will perform one more manual review.

If approved, the next action will be a separate formal H4 closure prompt followed by H5 full-IST validation preparation.

---

# 21. Git authority

For this round:

```text
production edits = YES
tests = YES
docs/state draft updates = YES
new real AI interpretation = YES
scanner/analyzer rerun = NO
commit = NO
push = NO
tag = NO
```

Do not commit, push or tag without explicit human authorization.

---

# Final principles

> **LegacyMapper is a knowledge product, not a pipeline dump.**

> **Humans receive concise, understandable documentation.**

> **AI receives structured, high-fidelity knowledge for maintenance, modernization and migration.**

> **Evidence and diagnostics remain available internally without dominating the user experience.**

> **One semantic truth, projected for different consumers.**
