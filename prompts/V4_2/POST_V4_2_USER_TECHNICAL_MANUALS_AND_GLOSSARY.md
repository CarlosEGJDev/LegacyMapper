# LegacyMapper — Post-V4.2 User Manual, Technical Manual and Glossary Update

## MODE

POST_V4_2_DOCUMENTATION_UPDATE

## MODEL

Claude Opus 4.6

## AUTHORITY AND CURRENT STATE

LegacyMapper V4.2 is formally closed.

The Post-V4.2 repository cleanup is also complete.

Authoritative current state:

V4_2_CLOSED=true
V5_IMPLEMENTED=false
V5_CONTINUITY=READY
POST_V4_2_REPOSITORY_CLEANUP_COMPLETE=true
NEXT=POST_V4_2_DOCUMENTATION_UPDATE

Repository cleanup result:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_CLEANUP_AND_VERSIONING_RESULT.md

The cleaned repository is now the authoritative repository structure for this documentation task.

The repository contains approximately 647 tracked files and is intentionally small enough to be cloned and used to continue V5 without local operational-analysis output.

This task:

- DOES update documentation;
- DOES inspect the current repository;
- DOES NOT modify production code;
- DOES NOT modify tests;
- DOES NOT implement V5;
- DOES NOT reopen V4.2;
- DOES NOT access the real IST repository;
- DOES NOT execute real AI-provider calls;
- DOES NOT modify canonical knowledge contracts;
- DOES NOT implement the Plugin runtime;
- DOES NOT implement the Technical Lead approval surface.

---

# 1. OBJECTIVE

Produce the definitive Post-V4.2 documentation set that will serve three purposes:

1. allow a user to operate LegacyMapper correctly;
2. allow a programmer to understand, maintain and continue development of LegacyMapper;
3. allow the Technical Lead to manually audit the codebase and identify future improvement/refactoring opportunities.

Update/create exactly:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

Also create:

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

Do not create additional manuals unless strictly required to report a blocking problem.

---

# 2. SOURCE-OF-TRUTH ORDER

Do NOT write the manuals from memory or from historical documentation alone.

Inspect the actual repository.

Use this precedence:

1. current production source code;
2. current tests and fixtures;
3. PROJECT_STATE.json;
4. current contracts/baselines/manifests;
5. current repository policies;
6. V4.2 final closure;
7. V4.2 round results;
8. V4.1/V4/V3 historical documentation;
9. historical prompts/results only when needed to explain design history.

If documentation disagrees with current code:

DO NOT silently copy the documentation.

Document the current implementation and report the discrepancy in the result file.

Do not invent functionality.

---

# 3. DOCUMENTATION STYLE

Documentation must be written for a technically competent reader.

Prefer:

- clear headings;
- concise explanations;
- tables where they improve navigation;
- exact repository-relative paths;
- exact class/function/module names;
- concrete command examples;
- explicit boundaries;
- cross-references between sections.

Avoid:

- marketing language;
- generic Python tutorials;
- repeating the same explanation across many sections;
- speculative architecture;
- undocumented assumptions;
- enormous raw file listings with no explanation.

The Technical Manual must be detailed, but navigable.

---

# 4. USER MANUAL

Update:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

This document answers:

"How do I use LegacyMapper?"

It must cover at least:

## 4.1 Purpose

What LegacyMapper does.

Explain the principle:

Python discovers.
AI interprets.

Explain that V4.2 remains scoped to the current supported legacy ecosystem and that true technology/provider agnosticism is V5 work.

## 4.2 Installation / prerequisites

Document only prerequisites supported by the repository.

Do not invent package managers, deployment methods, environment variables, or dependencies not evidenced by the repository.

## 4.3 CLI

Document current commands:

analyze
full
readiness

and legacy bare-positional analyze compatibility.

Include exact syntax supported by the current parser.

## 4.4 analyze

Explain:

- purpose;
- required arguments;
- optional arguments;
- generated artifacts;
- expected use;
- deterministic behavior;
- AI availability/restrictions.

## 4.5 full

Explain:

- deterministic pipeline;
- stages;
- output structure;
- partial/failure containment;
- generated documentation;
- optional AI interpretation;
- proposals;
- human-review boundary.

## 4.6 readiness

Explain what it verifies and what READY means.

## 4.7 AI

Explain:

--allow-ai-interpretation

including:

- disabled by default;
- only valid where current code permits it;
- proposals are not approved facts;
- no automatic canonical promotion;
- provider/model behavior actually implemented today.

Do NOT describe V5 provider abstraction as already implemented.

## 4.8 Output navigation

Explain the current output workspace.

Include:

documentation/README.md

and the ten historical top-level technical-document filenames.

Explain partitioned documentation:

functional_flows/
database_access/
unresolved_findings/

Explain which documents are summaries/navigation and where detailed records are located.

## 4.9 Exit codes

Document exactly:

SUCCESS=0
PARTIAL=1
USAGE=2
FAILED=4

if verified against current implementation.

## 4.10 Rerun/recovery

Explain:

- what is regenerated;
- what stale generated content is removed;
- what user-created files are preserved;
- source repository immutability.

## 4.11 Real-system output

Incorporate the new policy from:

docs/GENERATED_ARTIFACT_POLICY.md

Explain that operational analysis output should remain local and should not be committed.

## 4.12 Approval boundary

Clearly explain:

IMPLEMENTED:
proposal generation for Technical Lead review.

NOT IMPLEMENTED:
approve/reject/request-correction CLI;
run_id-bound approval;
automatic canonical promotion;
full R11/R12 orchestration after approval;
Plugin runtime.

## 4.13 Troubleshooting

Provide evidence-based troubleshooting for common situations visible in current code/tests/contracts.

Do not invent errors.

---

# 5. TECHNICAL MANUAL — PRIMARY PURPOSE

Update:

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

This is NOT merely an architecture overview.

It is the primary:

DEVELOPER HANDOVER
+
MAINTENANCE GUIDE
+
CODE AUDIT MAP

A programmer unfamiliar with LegacyMapper should be able to use this manual to understand the repository and continue development.

The Technical Lead should be able to use it to inspect the code module-by-module and identify areas worth improving.

---

# 6. TECHNICAL MANUAL — REPOSITORY MAP

Create a clear map of the current repository.

At minimum document:

main.py
legacy_documenter/
tests/
tools/
docs/
prompts/
codex/
result_codex/
output/
context/
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
.gitignore

Explain the responsibility of each.

Explicitly distinguish:

production source
tests
developer tooling
governance/continuity
historical evidence
prompts
small tracked contract artifacts
local generated operational output

---

# 7. TECHNICAL MANUAL — MODULE INVENTORY

This is mandatory and must be derived from the CURRENT SOURCE TREE.

For every significant package/module under:

legacy_documenter/

document:

MODULE/PACKAGE
PURPOSE
FILES
PRIMARY CLASSES/FUNCTIONS
RESPONSIBILITY
INPUTS
OUTPUTS
IMPORTANT DEPENDENCIES
CALLED_BY / USED_BY
RELATED_TESTS
NOTES / RISKS

Do not simply list filenames.

Explain why the module exists and how it participates in the system.

Where useful, use tables.

A programmer should be able to answer:

"What file should I inspect or modify for this responsibility?"

without searching the entire repository.

---

# 8. TECHNICAL MANUAL — FILE MAP

Within each significant module/package, enumerate its significant source files.

For each significant file explain:

- path;
- primary responsibility;
- important class(es);
- important public/significant function(s);
- major collaborators;
- relevant tests;
- whether it is orchestration, domain/model, extractor, resolver, renderer, adapter, infrastructure, utility, contract, etc.

Small cohesive helper files may be grouped when appropriate.

Do NOT produce meaningless one-line descriptions.

Do NOT omit a significant production `.py` file merely because it is internal/private.

The goal is code auditability.

---

# 9. TECHNICAL MANUAL — EXECUTION ARCHITECTURE

Document the real execution path.

At minimum:

CLI
→ argument parsing/routing
→ command execution
→ deterministic extraction/analysis
→ indexes/evidence
→ context
→ technical documentation
→ optional AI interpretation
→ proposal output
→ Technical Lead boundary

Explain `analyze` and `full` separately where their paths differ.

Identify the actual files/classes/functions responsible for each transition.

---

# 10. TECHNICAL MANUAL — FULL PIPELINE

Document every current full-pipeline stage.

For each stage include:

STAGE
RESPONSIBILITY
IMPLEMENTATION
INPUT
OUTPUT
FAILURE BEHAVIOR
DEPENDENCIES
RELATED TESTS

Explain:

RunResult
StageResult
RunStatus
StageStatus

and how partial/failure containment works.

---

# 11. TECHNICAL MANUAL — EXTRACTION / ANALYSIS

Document current deterministic discovery.

Cover the significant areas actually implemented, including where applicable:

- repository scanning;
- project/solution discovery;
- VB.NET symbols;
- WebForms;
- code-behind;
- calls;
- dependencies;
- database access;
- functional-flow resolution;
- unresolved boundaries;
- traceability/evidence.

Identify implementation modules.

Explain what Python establishes deterministically versus what AI may interpret.

---

# 12. TECHNICAL MANUAL — DOCUMENTATION SYSTEM

Document:

TechnicalDocumentationRenderer

and its collaborators.

Explain:

- fixed top-level documents;
- navigation documents;
- deterministic partitioning;
- safe filenames;
- relative links;
- stale partition cleanup;
- preservation of unknown/user files;
- functional flow partitions;
- database access partitions;
- unresolved finding partitions.

Explicitly record current maintainability concern:

legacy_documenter/exporters/technical_documentation_renderer.py

approximately 802 lines at the V4.2 closure baseline, with:

TechnicalDocumentationRenderer

approximately 462 lines.

Do not assume the numbers remain exact if the current source differs.

Measure/currently verify them and document current values.

Flag it as a known HIGH-risk future extraction candidate if still applicable.

---

# 13. TECHNICAL MANUAL — AI ARCHITECTURE

Document the CURRENT implementation only.

Identify:

- provider interface/abstraction currently present;
- concrete provider(s);
- configuration;
- context construction;
- interpretation;
- proposal generation;
- real-provider safety mechanisms;
- test fakes/mocks;
- readiness.

Explain current coupling/limitations.

Then separately identify V5 requirement:

AI/provider/model agnosticism.

Make explicit that V5 must make the runtime AI replaceable through a stable core contract/port, with provider-specific transport/auth/model/retry details outside core domain logic.

Do NOT implement or pretend this exists already.

Preserve:

Python discovers; AI interprets.

---

# 14. TECHNICAL MANUAL — KNOWLEDGE ARCHITECTURE

Document current V4 knowledge architecture:

input material
→ ingestion/normalization
→ evidence/context
→ analysis/classification/relationship
→ proposals
→ Technical Lead approval boundary
→ canonical knowledge
→ R11/R12 projections

Clearly distinguish what exists as reusable implementation/contracts from what is NOT orchestrated by V4.2 full workflow.

Document:

CanonicalKnowledgeEntry
KNO identifiers
one canonical source
R11 human projection
R12 LegacyMapperPluginKnowledge
Plugin contract version if current repository verifies it.

Do not imply Plugin runtime exists.

---

# 15. TECHNICAL MANUAL — CONTRACTS AND DATA MODELS

Inventory significant contracts/models.

For each explain:

NAME
MODULE
PURPOSE
KEY FIELDS
PRODUCER
CONSUMER
STABILITY / COMPATIBILITY NOTES

Prioritize public/cross-module contracts.

Do not turn the manual into a dump of every dataclass field if that harms usability.

---

# 16. TECHNICAL MANUAL — TEST ARCHITECTURE

Explain how the test suite is organized.

Identify meaningful groups by responsibility/version/contract.

Document:

- unit-style tests;
- deterministic regression tests;
- compatibility tests;
- security/provider-call guards;
- synthetic fixtures;
- V4/V4.1/V4.2 regression protection;
- real-pilot-derived synthetic tests;
- baseline/manifest integrity tests.

Map important production modules to relevant tests.

Do NOT claim the suite currently passes unless you execute it in this task.

Historical closure baseline may be described explicitly as historical:

1809_PASS_0_FAIL_0_SKIP

Do not silently present historical state as a fresh run.

---

# 17. TECHNICAL MANUAL — TOOLING

Document significant files under:

tools/

For each significant tool explain:

- purpose;
- when to use it;
- whether it changes state;
- expected output;
- relationship to baselines/manifests/audits/closure.

---

# 18. TECHNICAL MANUAL — CONTINUITY / AGENT HANDOVER

Explain:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

and the repository-authoritative continuity model.

Document the bootstrap sequence actually supported by the repository.

Explain that development-agent conversation memory is not authoritative.

Explain which artifacts a new developer/agent should read first.

Provide a concise:

"Starting development from a fresh clone"

sequence.

Do not implement V5.

---

# 19. TECHNICAL MANUAL — GENERATED ARTIFACT POLICY

Explain the distinction between:

operational generated output

and

tracked development/contract/history artifacts.

Document:

output/_local_<name>/

or the exact current convention verified from `.gitignore`/policy.

Explain why `output/` cannot be globally ignored.

Explain what may be safely deleted locally and what must remain tracked.

---

# 20. TECHNICAL MANUAL — KNOWN TECHNICAL DEBT

Create a dedicated audit section.

At minimum verify/document current status of:

F-05
F-06
F-07

documentation scale debt:
WEB_ENTRY_POINTS.md
PROJECT_DEPENDENCIES.md

maintainability debt:
technical_documentation_renderer.py

Post-V4.2 baseline/manifest integrity test scoping debt:
the test that compares mutable PROJECT_STATE.json even though the manifest identifies it as mutable.

Also inspect PROJECT_STATE.json and current closure/result documents for any additional OPEN/PARTIALLY_RESOLVED/DEFERRED debt still applicable.

For each debt item include:

ID
AREA
CURRENT STATUS
AFFECTED FILE(S)
IMPACT
WHY IT REMAINS
SUGGESTED FUTURE VERSION
RISK IF MODIFIED
RELATED TESTS/EVIDENCE

Do NOT fix debt in this task.

---

# 21. TECHNICAL MANUAL — CODE AUDIT MAP

Add a dedicated section:

CODE AUDIT MAP

Its purpose is to help the Technical Lead inspect the project manually.

Group production areas into an audit order.

For each area provide:

- module/package;
- important files;
- responsibility;
- complexity/maintainability concern;
- relevant contracts;
- relevant tests;
- known debt;
- suggested questions to ask during review.

Example questions:

- Is this responsibility too broad?
- Is orchestration mixed with domain logic?
- Is deterministic behavior adequately isolated?
- Does this module have sufficient characterization tests?
- Could this class be safely decomposed?
- Does this dependency belong at this architectural layer?
- Is provider-specific logic leaking into core behavior?

These are audit prompts, not findings unless evidence supports a finding.

---

# 22. TECHNICAL MANUAL — MAINTAINABILITY INVENTORY

Perform a deterministic/static maintainability inventory of current production Python.

At minimum report:

- production .py file count;
- largest production modules by lines;
- largest classes/functions where reasonably measurable;
- module risk buckets if existing project tooling already defines them;
- modules with especially broad responsibility;
- current type-hint/docstring coverage where existing deterministic tooling can measure it safely;
- files already identified by prior rounds as risky/deferred.

Do not introduce arbitrary quality scores.

Prefer existing LegacyMapper metrics/thresholds where available.

This is documentation/audit information only.

No refactor.

---

# 23. TECHNICAL MANUAL — V5 HANDOVER

Finish the Technical Manual with:

V5 HANDOVER

Clearly separate:

WHAT V4.2 ALREADY PROVIDES

WHAT V5 MUST DESIGN

WHAT DEBT MAY BE RESOLVED IN V5

WHAT MAY BE DEFERRED TO V5.1/V5.2

V5 design requirements include at minimum:

- language agnosticism;
- framework agnosticism;
- database agnosticism;
- project-layout agnosticism;
- runtime AI/provider/model agnosticism.

Preserve:

Python discovers; AI interprets.

State that runtime AI agnosticism and development-agent neutrality are related but distinct.

Do NOT design the complete V5 architecture in this task.

---

# 24. GLOSSARY

Create/update:

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

The glossary must consolidate terminology needed to understand V4.2.

Include, where currently applicable:

LegacyMapper
deterministic discovery
AI interpretation
evidence
context
source
provenance
proposal
Technical Lead
approval
canonical knowledge
CanonicalKnowledgeEntry
KNO
R11
R12
LegacyMapperPluginKnowledge
Plugin runtime
RunResult
StageResult
RunStatus
StageStatus
SUCCESS
PARTIAL
FAILED
READY
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
AS_IS
TO_BE
HISTORICAL
GAP
unresolved boundary
confirmed terminal
operational output
tracked artifact
synthetic fixture
baseline
manifest
agent-neutral continuity

and other important current terms discovered in code/contracts.

Definitions must reflect actual LegacyMapper semantics, not generic dictionary definitions.

---

# 25. CROSS-DOCUMENT CONSISTENCY

Verify consistency between:

USER MANUAL
TECHNICAL MANUAL
GLOSSARY

for:

- CLI commands;
- exit codes;
- AI behavior;
- approval boundary;
- Plugin status;
- V5 status;
- operational output policy;
- current supported technologies;
- terminology.

No document may claim that an unimplemented capability exists.

---

# 26. REPOSITORY SAFETY

Do NOT access:

C:\Users\cgalianj\source\IST_40\operacional

or any real legacy repository.

Do NOT run LegacyMapper against a real repository.

Do NOT perform real AI calls.

Do NOT alter production code.

Do NOT alter tests.

Do NOT alter baselines/manifests.

Do NOT alter historical round results.

Do NOT alter historical prompts.

Do NOT alter V4/V4.1/V4.2 closure decisions.

---

# 27. VALIDATION

Because this is documentation-only:

A full test-suite run is not mandatory.

Perform deterministic/source inspection sufficient to verify claims.

At minimum:

- inspect current CLI help/parser implementation;
- inspect current production package tree;
- inspect current test tree;
- inspect tools;
- inspect PROJECT_STATE.json;
- inspect current .gitignore;
- inspect GENERATED_ARTIFACT_POLICY;
- inspect V4.2 final baseline/manifest;
- inspect V4.2 final closure;
- inspect known debt sources;
- verify no real-provider call occurred;
- verify no real IST access occurred.

If a test is run, report it accurately.

Do not alter tests to make documentation claims true.

---

# 28. RESULT DOCUMENT

Create:

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

It must contain:

## STATUS

## FILES_CREATED

## FILES_UPDATED

## USER_MANUAL_SUMMARY

## TECHNICAL_MANUAL_SUMMARY

## MODULE_INVENTORY_SUMMARY

## FILE_MAP_SUMMARY

## EXECUTION_ARCHITECTURE_VERIFICATION

## TEST_ARCHITECTURE_VERIFICATION

## MAINTAINABILITY_INVENTORY

## CODE_AUDIT_MAP_SUMMARY

## KNOWN_DEBT_VERIFICATION

## GLOSSARY_SUMMARY

## CROSS_DOCUMENT_CONSISTENCY

## SOURCE_VS_DOCUMENTATION_DISCREPANCIES

## REAL_PROVIDER_CALLS

Expected:
0

## REAL_IST_ACCESSED

Expected:
false

## PRODUCTION_CODE_CHANGED

Expected:
false

## TESTS_CHANGED

Expected:
false

## V4_2_REOPENED

Expected:
false

## V5_IMPLEMENTED

Expected:
false

## PLUGIN_RUNTIME

Expected:
NOT_IMPLEMENTED

## APPROVAL_SURFACE_IMPLEMENTATION

Expected:
NOT_IMPLEMENTED

## VALIDATION

## GIT_STATUS

## DECISION

Expected:
POST_V4_2_DOCUMENTATION_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

Expected:
HUMAN_DOCUMENTATION_REVIEW

---

# 29. GIT

Do NOT commit.

Do NOT push.

The Technical Lead must review the three manuals and result document first.

Do not modify PROJECT_STATE.json in this task.

Do not create a closure/versioning prompt automatically.

Stop after generating and validating the documentation.

---

# 30. STOP CONDITIONS

STOP and report if:

- current source contradicts a critical V4.2 closure claim;
- a required production module cannot be understood from repository evidence;
- significant repository content required for the manuals appears missing;
- documentation would require access to real IST data;
- documentation would require a real provider call;
- a baseline/manifest appears corrupted;
- an unimplemented capability appears to have been accidentally documented as implemented;
- unexpected production/test modifications are detected.

Do not repair these issues in this task.

---

# 31. EXPECTED DECISION

On success:

STATUS=COMPLETE
DECISION=POST_V4_2_DOCUMENTATION_READY_FOR_TECHNICAL_LEAD_REVIEW
V4_2_CLOSED=true
V5_IMPLEMENTED=false
REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false
PRODUCTION_CODE_CHANGED=false
TESTS_CHANGED=false
NEXT=HUMAN_DOCUMENTATION_REVIEW

Stop.

Do NOT commit.
Do NOT push.
Do NOT start V5.