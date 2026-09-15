# LegacyMapper V4.2-R0
# Full Pipeline Architecture and Inventory

TASK=V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY

MODE=ARCHITECTURE_AND_INVENTORY_ONLY

IMPLEMENTATION_ALLOWED=false
PRODUCTION_CODE_CHANGE_ALLOWED=false
TEST_CHANGE_ALLOWED=false
V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false
COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# 1. Objective

Design the implementation roadmap for LegacyMapper V4.2.

V4.2 exists to expose and orchestrate the capabilities already implemented
through V4.1 as a practical end-to-end workflow for analyzing a legacy
system and producing useful technical/functional documentation.

Primary user need:

Given a legacy source repository, the user should eventually be able to
execute one clear CLI workflow and receive a coherent analysis/documentation
package that helps a human understand how the system works.

V4.2 is primarily:

ORCHESTRATION + CLI + OPERATIONAL DOCUMENTATION EXPERIENCE

V4.2 is NOT the V5 agnosticism redesign.

---

# 2. Current Baseline

Require and preserve:

V4_1_STATUS=FORMALLY_CLOSED
TESTS_BASELINE=1566_PASS_0_FAIL_0_SKIP
READINESS_BASELINE=READY

PLUGIN_RUNTIME=NOT_IMPLEMENTED
V5_IMPLEMENTED=false

Production behavior from V4.1 is the baseline.

Do not reopen or modify V4.1 historical artifacts.

---

# 3. Architectural Principles

Preserve:

Python discovers/resolves deterministic facts.
AI interprets only where interpretation is required.
Technical Lead remains the only final approval authority.
AI output must never silently become approved canonical knowledge.
Uncertainty must remain explicit.
Provenance and evidence must remain traceable.
Legacy source must remain read-only.
Generated output must never modify the analyzed source repository.

Reuse existing capabilities before creating new ones.

Do not duplicate analysis, knowledge, projection, or documentation logic
inside the CLI.

The CLI must be an orchestration boundary, not a second domain layer.

---

# 4. Python Development Style

Future V4.2 implementation must follow these rules.

Use good idiomatic Python practices first.

Where compatible with idiomatic Python, organize code in a way understandable
to a developer with a strong C# background.

Classes:
PascalCase

Modules/files:
snake_case

Prefer one primary/significant class per file where it improves clarity,
without mechanically splitting tiny cohesive structures.

Use clear responsibility boundaries.

Use type hints consistently at public/service boundaries.

Avoid unnecessary Python magic.

Do not introduce C#-style trivial getters/setters, empty interfaces,
unnecessary dependency injection, or pattern proliferation.

Every significant public class/function/method must have a concise docstring
explaining what it does and why it exists.

Comments should explain non-obvious deterministic, security, evidence,
approval, or orchestration rules rather than obvious Python syntax.

Prefer simple, maintainable code.

---

# 5. Required Repository Reading

Read at minimum:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md

docs/V4_1/V4_1_FINAL_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R10_FINAL_BASELINE_AND_FORMAL_CLOSURE_RESULT.md

Inspect current production source directly.

Do not rely solely on historical documentation when current source can
verify the actual implementation.

---

# 6. Current CLI

Inspect the actual CLI implementation.

Current supported user workflow is approximately:

python main.py <repository> --output <output>

with the actual supported flags verified from source.

Determine exactly:

- what main.py executes;
- what stages it already orchestrates;
- what artifacts it generates;
- which implemented capabilities are NOT reached by this CLI;
- which documentation capabilities already exist;
- which knowledge capabilities already exist;
- where AI interpretation can currently occur;
- which components require explicit inputs that the current CLI does not create.

Do not assume the answer from documentation.
Verify against source.

---

# 7. Capability Inventory

Produce a source-backed inventory of existing capabilities.

For every relevant capability record:

CAPABILITY
IMPLEMENTATION_LOCATION
INPUT
OUTPUT
DETERMINISTIC_OR_AI
CURRENTLY_REACHED_BY_CLI
REUSABLE_FOR_V4_2
MISSING_INTEGRATION
RISKS

At minimum inspect:

scanner
extractors
analysis
context
documentation
exporters
llm
knowledge/input
knowledge/ingestion
knowledge/provenance
knowledge/classification
knowledge/temporal
knowledge/relations
knowledge/proposals
knowledge/approval
knowledge/canonical
knowledge/projection
knowledge/plugin_projection
knowledge/readiness

---

# 8. Existing Output Inventory

Run or inspect the current pipeline sufficiently to determine the real output
contract of the existing CLI.

Document:

- generated directories;
- generated JSON artifacts;
- generated Markdown artifacts;
- evidence artifacts;
- context artifacts;
- flow artifacts;
- database artifacts;
- unresolved-information artifacts;
- documentation artifacts;
- temporary/intermediate artifacts.

Do not create a new output structure yet.

First establish what exists.

---

# 9. Documentation Capability Assessment

Determine whether current source already has enough reusable capability to
generate an end-user package covering, where evidence supports it:

SYSTEM OVERVIEW
TECHNICAL ARCHITECTURE
PROJECTS / MODULES
DEPENDENCIES
WEB ENTRY POINTS
FUNCTIONAL FLOWS
DATABASE ACCESS
UNRESOLVED FINDINGS
EVIDENCE / TRACEABILITY

For every candidate document classify:

ALREADY_GENERATED
GENERATABLE_WITH_EXISTING_COMPONENTS
REQUIRES_ORCHESTRATION
REQUIRES_SMALL_NEW_RENDERER
REQUIRES_NEW_DOMAIN_CAPABILITY
NOT_SUPPORTED_BY_CURRENT_EVIDENCE

Do not promise documentation that current evidence cannot support.

---

# 10. Full Pipeline Boundary

Design a proposed V4.2 full-pipeline boundary.

Conceptually evaluate:

legacy source
→ scan
→ extraction
→ deterministic analysis
→ evidence
→ context
→ interpretation where permitted
→ documentation
→ final run summary

Determine exactly where the V4 knowledge pipeline should or should not join
this workflow.

Do not bypass:

proposal
→ Technical Lead approval
→ canonical knowledge

If a fully automatic run cannot legitimately reach canonical knowledge,
state the boundary explicitly.

---

# 11. CLI Design

Evaluate a future command concept such as:

python main.py full <repository> --output <directory>

but DO NOT treat that syntax as already decided.

Compare at least:

A. preserve existing command and add --full
B. introduce subcommands such as analyze/full/readiness
C. another minimal design justified by current architecture

Recommend one.

The recommendation must prioritize:

clarity
backward compatibility
scriptability
future V5 extensibility
simple implementation
low duplication

Existing CLI behavior must remain available unless there is a strong,
documented reason otherwise.

---

# 12. Output Experience

Design a proposed human-friendly output package.

Separate conceptually:

human-readable documentation
machine-readable analysis
evidence/traceability
intermediate/internal artifacts
run summary

Do not finalize filenames merely because they appear in this prompt.

Derive the proposed structure from current capabilities.

The result must explain which artifacts are:

PUBLIC_USER_OUTPUT
MACHINE_OUTPUT
EVIDENCE_OUTPUT
INTERNAL_OUTPUT

---

# 13. Failure and Partial Analysis

Design how the future full pipeline should behave when:

- some files cannot be parsed;
- dependencies cannot be resolved;
- database operations cannot be resolved;
- flows are incomplete;
- AI is unavailable;
- AI interpretation fails;
- human information is absent;
- source code is partial;
- readiness is not READY.

Prefer partial useful results with explicit status over destroying the entire
run when safe.

Never convert unresolved information into invented facts.

---

# 14. AI Boundary

Inspect the existing LLM/provider boundary.

For V4.2:

do NOT redesign it into the future V5 provider-agnostic architecture.

Reuse the current boundary where appropriate.

However, identify coupling that V5 will eventually need to address.

Record those findings as V5 design inputs only.

V4.2 must not implement the V5 AI/provider abstraction redesign.

---

# 15. V5 Boundary

Explicitly preserve for V5:

language agnosticism
framework agnosticism
architecture/project-layout agnosticism
database/persistence agnosticism
AI provider/model agnosticism

V4.2 must not attempt those redesigns.

V4.2 may create clean orchestration seams that make V5 easier,
provided they are justified independently by V4.2 requirements.

---

# 16. Proposed V4.2 Roadmap

Validate or correct this preliminary roadmap:

V4.2-R0
Baseline + inventory + architecture.

V4.2-R1
CLI contract + execution/result model.

V4.2-R2
Full-pipeline orchestrator.

V4.2-R3
Integration of existing technical analysis.

V4.2-R4
Interpretation/context/documentation integration.

V4.2-R5
Unified full CLI and user-facing output experience.

V4.2-R6
Robustness, partial results, recovery, security.

V4.2-R7
Real pilot against the IST/Operacional legacy system.

V4.2-R8
Documentation, comprehensive regression, baseline and formal closure.

You may recommend splitting, merging, or reordering rounds if source evidence
shows a better implementation sequence.

Do not implement any round in R0.

---

# 17. Risk Analysis

Identify at minimum:

- orchestration duplication risk;
- coupling between current main.py and analysis components;
- generated artifact dependencies;
- historical output dependencies;
- AI availability/provider dependencies;
- output size/performance;
- deterministic reproducibility;
- source immutability;
- approval-boundary risks;
- regression risks to V4.1;
- future V5 migration risks.

Classify each:

LOW
MEDIUM
HIGH

and provide mitigation.

---

# 18. Verification

Run:

python -m unittest discover -s tests

Require expected baseline:

1566 PASS
0 FAIL
0 SKIP

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

Do not regenerate historical multi-GB artifacts unless strictly necessary.

If required artifacts are missing, stop and report the environment problem
rather than modifying production code.

---

# 19. Result

Create:

docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md

Include at minimum:

STATUS
BASELINE
TESTS
READINESS
CURRENT_CLI
CURRENT_PIPELINE
CAPABILITY_INVENTORY
CURRENT_OUTPUT_INVENTORY
DOCUMENTATION_CAPABILITY_MATRIX
FULL_PIPELINE_PROPOSAL
KNOWLEDGE_PIPELINE_BOUNDARY
AI_BOUNDARY
CLI_OPTIONS_EVALUATED
CLI_RECOMMENDATION
OUTPUT_EXPERIENCE_PROPOSAL
PARTIAL_FAILURE_POLICY
V5_BOUNDARY
RISKS
PROPOSED_V4_2_ROADMAP
PRODUCTION_CODE_CHANGED
TESTS_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DECISION
NEXT

Expected invariants:

PRODUCTION_CODE_CHANGED=false
TESTS_CHANGED=false
V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If architecture is sufficiently understood:

DECISION=V4_2_R0_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R0

Otherwise:

DECISION=V4_2_R0_BLOCKED
NEXT=<explicit reason>

---

# 20. Stop

STOP after producing the R0 result.

Do not implement R1.
Do not modify production code.
Do not modify tests.
Do not commit.
Do not push.
Do not reopen V4.1.
Do not begin V5.