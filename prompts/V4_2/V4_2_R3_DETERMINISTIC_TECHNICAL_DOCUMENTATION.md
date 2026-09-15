# LegacyMapper V4.2-R3
# Deterministic Technical Documentation

TASK=V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION

MODE=CONTROLLED_IMPLEMENTATION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

AI_RUNTIME_CALL_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# 1. Authority

V4.2-R0, R1 and R2 have been reviewed and approved by the Technical Lead.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md
docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md
docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md

docs/V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md

Inspect current production source directly.

---

# 2. Objective

Make:

python main.py full <repository> --output <directory>

produce a useful deterministic technical-documentation package from the
analysis data already discovered by LegacyMapper.

The primary human goal is:

"I give LegacyMapper a legacy system and I can open the generated
documentation and understand its technical structure, entry points,
dependencies, database access and discovered execution flows."

R3 must improve human usability.

R3 must NOT invent business meaning that deterministic evidence does not
support.

---

# 3. Core Rule

DETERMINISTIC EVIDENCE != AI INTERPRETATION

R3 documentation must be derived only from deterministic analysis data.

No LLM/provider call is allowed.

Do not infer:

business purpose not present in evidence
intent
unstated architectural decisions
unstated database relationships
unstated call relationships
unstated ownership
unstated functional meaning

If LegacyMapper cannot establish something deterministically, expose it as
unresolved/unknown rather than guessing.

---

# 4. Existing Documentation

Preserve the existing MarkdownExporter outputs:

PROJECT_OVERVIEW.md
SOLUTION_STRUCTURE.md
PROJECT_DEPENDENCIES.md
WEBFORMS_MAP.md
CONFIGURATION_SUMMARY.md
ANALYSIS_WARNINGS.md

Do not rewrite them unnecessarily.

R3 should add the missing technical views identified in R0.

At minimum:

WEB ENTRY POINTS
FUNCTIONAL FLOWS
DATABASE ACCESS

Also evaluate whether an explicit:

UNRESOLVED FINDINGS

document adds useful information beyond ANALYSIS_WARNINGS.md.

Only add it if it provides materially different value.

---

# 5. Target Documentation Package

After a successful `full` run, a human should have a coherent package under
the run's documentation area.

Expected conceptual package:

documentation/
    PROJECT_OVERVIEW.md
    SOLUTION_STRUCTURE.md
    PROJECT_DEPENDENCIES.md
    WEBFORMS_MAP.md
    CONFIGURATION_SUMMARY.md
    ANALYSIS_WARNINGS.md

    WEB_ENTRY_POINTS.md
    FUNCTIONAL_FLOWS.md
    DATABASE_ACCESS.md

Potentially:
    UNRESOLVED_FINDINGS.md

Exact names may be corrected if repository conventions justify better names.

Do not rename historical existing documents.

---

# 6. Web Entry Points Document

Create a deterministic human-readable projection over the existing:

entry_points
event_bindings
webforms

data.

The document should help a developer answer questions such as:

Which WebForms pages/controls are entry points?

Which UI events were discovered?

Which code-behind/class/method is associated where evidence supports it?

What relationships remain unresolved?

Do not claim relationships not present in the deterministic indexes.

Prefer identifiers/path/evidence already present in models.

---

# 7. Functional Flows Document

Create a deterministic human-readable projection over:

functional_flows
functional_paths
flow_summary
flow_unresolved

The document should help a developer understand discovered execution paths.

Where evidence supports it, show a readable chain conceptually similar to:

WebForm/Event
→ handler/method
→ call
→ service/class
→ database operation

Do not force every flow into that exact shape.

Render what the actual flow model contains.

Preserve:

status
confidence
unresolved boundaries
evidence identifiers

where present and useful.

Do not convert unresolved boundaries into assumed calls.

---

# 8. Database Access Document

Create a deterministic human-readable projection over:

data_access
stored_procedures
sql_operations
data_parameters

and relevant project/symbol context where already available.

The document should help answer:

Which components access the database?

Which stored procedures were discovered?

Which SQL operations were discovered?

Which parameters were discovered?

Which source locations/evidence support the relationship?

Do not infer database schema relationships not discovered by the analyzer.

Do not infer tables from procedure names.

Do not infer business meaning from SQL names.

---

# 9. Unresolved Findings

Evaluate:

errors
flow_unresolved
unresolved relationships represented elsewhere

If ANALYSIS_WARNINGS.md already adequately covers these, do not duplicate it.

If it does not, add:

UNRESOLVED_FINDINGS.md

with a clearly different responsibility:

"What LegacyMapper could not establish deterministically."

This document must never turn unresolved data into interpretation.

---

# 10. Documentation Architecture

Do NOT put renderer logic into:

full_pipeline.py
pipeline_stages.py
router.py
main.py

Those files are already orchestration infrastructure.

Use the existing exporter/documentation architecture where appropriate.

Prefer small focused deterministic renderers/services.

Do not use `documentation/generator.py` in R3 if it requires AI.

That module belongs to R4 analysis.

R3 documentation is deterministic only.

---

# 11. DOCUMENTATION Stage

R1 already defined:

StageId.DOCUMENTATION

R3 should now make it a real stage in `full`.

Expected conceptual order:

...
EXPORT
CONTEXT
DOCUMENTATION
FINAL_SUMMARY

Derive actual prerequisites from source.

DOCUMENTATION must consume already-produced in-memory analysis data where
possible.

Avoid rereading JSON files merely because they were written to disk if the
same typed/in-memory data is already available.

---

# 12. Failure Policy

DOCUMENTATION is a user-facing value stage.

A failure in one new renderer should not necessarily destroy all other
documentation.

Design the smallest sensible failure boundary.

Possible approaches:

one DOCUMENTATION stage with internally recorded renderer failures

or

a deterministic documentation service that produces a structured outcome

Do not add many new StageId values unless there is a strong reason.

Keep StageId.DOCUMENTATION as the public orchestration stage unless source
evidence justifies otherwise.

If deterministic analysis/export succeeded but one documentation projection
failed:

overall run should normally be PARTIAL, not FAILED.

Existing useful machine analysis must remain available.

---

# 13. Human Readability

These documents are for software developers, not only machines.

Prefer:

clear headings
small summary sections
tables where useful
readable flow chains
source references
counts
explicit unresolved sections

Avoid:

huge raw JSON dumps
thousands of lines without grouping
Python repr output
internal dataclass syntax
opaque identifiers without contextual labels when labels exist

Large systems must remain navigable.

Use grouping/sorting deterministically.

---

# 14. Scalability

The real IST/Operacional repository is large.

Design documents so they remain useful when there are:

hundreds of projects
thousands of symbols
thousands of entry points
many database operations
many functional paths

Do not load unnecessary duplicate copies of the entire analysis.

Do not introduce quadratic rendering where a simple index/grouping can
avoid it.

Do not truncate silently.

If a document becomes large, structure it with deterministic sections and
navigation rather than dropping evidence.

---

# 15. Determinism

Same deterministic analysis input must produce byte-identical Markdown.

Stable sorting is mandatory.

No timestamps.

No random IDs.

No environment-specific metadata unless it is part of the analyzed evidence.

No AI.

---

# 16. Evidence and Traceability

Every important rendered relationship should preserve enough information for
a developer to trace it back to the deterministic analysis.

Reuse existing IDs, source paths, symbols, line information, statuses or
evidence references where available.

Do not create fake provenance.

R3 is NOT the V4 knowledge/provenance integration.

Knowledge-grade provenance remains a later integration concern.

---

# 17. Existing Output Compatibility

Do not change the shape of:

output/index/*.json
output/context/*.json
output/ai_context/*.json

unless absolutely required.

Prefer additive Markdown projections.

Existing V4.1/V4.2 consumers of machine output must remain compatible.

---

# 18. Python Development Style

Use idiomatic Python first.

Where compatible, keep organization comfortable for a C# developer.

PascalCase classes.
snake_case modules.

Clear responsibilities.

Type hints on public/service boundaries.

Concise explanatory docstrings.

Comments explain non-obvious evidence/determinism/security rules.

Avoid unnecessary Python magic.

Avoid C# ceremony transplanted into Python.

Do not over-engineer.

---

# 19. Characterization Before Rendering

Before implementing each renderer, inspect the actual model/index shape.

Add characterization tests where assumptions about:

entry_points
functional_flows
functional_paths
database access

are not already pinned.

Do not design Markdown against imagined schemas.

Use actual fixtures/models.

---

# 20. Tests

Add focused tests covering at minimum:

WEB_ENTRY_POINTS deterministic rendering

FUNCTIONAL_FLOWS deterministic rendering

DATABASE_ACCESS deterministic rendering

stable ordering

empty-data behavior

unresolved-data behavior

special Markdown characters / paths where relevant

no invented relationships

DOCUMENTATION stage appears in full

documentation failure → PARTIAL while machine analysis remains available

existing documentation remains generated

existing index JSON shapes remain compatible

AI not invoked

approval not invoked

canonical knowledge not produced

source repository remains immutable

legacy/analyze behavior remains compatible

run summary reflects DOCUMENTATION status

Do not weaken/delete existing tests.

---

# 21. Regression

Entering baseline:

1617_PASS_0_FAIL_0_SKIP

Run:

python -m unittest discover -s tests

Require:

all existing tests remain passing
plus new R3 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

Verify:

python main.py full --help

Do not run the real IST repository yet.
That is reserved for R7.

---

# 22. Maintainability Guard

Do not add renderer logic to the already-large:

legacy_documenter/cli/pipeline_stages.py
legacy_documenter/cli/full_pipeline.py

If new modules affect:

tests/test_v4_1_r0_maintainability_inventory.py

recompute deltas empirically using the same deterministic inventory builder.

Never modify the frozen V4.1-R0 artifact.

Never weaken assertions merely to make the test pass.

Document any legitimate delta.

---

# 23. Scope Guard

R3 MUST NOT implement:

AI interpretation
ProviderRegistry changes
documentation/generator.py AI integration
knowledge ingestion
proposal generation
approval UX
canonical knowledge
R11
R12
Plugin runtime
V5

If any becomes necessary unexpectedly:

STOP and report the dependency.

---

# 24. Result

Create:

docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md

Include:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
DOCUMENTATION_ARCHITECTURE
DOCUMENTATION_STAGE
WEB_ENTRY_POINTS_DOCUMENT
FUNCTIONAL_FLOWS_DOCUMENT
DATABASE_ACCESS_DOCUMENT
UNRESOLVED_FINDINGS_DECISION
EVIDENCE_TRACEABILITY
DETERMINISM
SCALABILITY
OUTPUT_COMPATIBILITY
FAILURE_POLICY
TESTS
READINESS
AI_INVOKED
CANONICAL_KNOWLEDGE_PRODUCED
TECHNICAL_LEAD_APPROVAL
PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DEFERRED_TO_R4
RISKS
DECISION
NEXT

Expected invariants:

AI_INVOKED=false
CANONICAL_KNOWLEDGE_PRODUCED=false
TECHNICAL_LEAD_APPROVAL=false

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R3_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R3

Otherwise:

DECISION=V4_2_R3_BLOCKED
NEXT=<explicit reason>

---

# 25. Stop

STOP after R3 implementation, tests, readiness and result.

Do not implement R4.
Do not commit.
Do not push.
Do not reopen V4.1.
Do not begin V5.