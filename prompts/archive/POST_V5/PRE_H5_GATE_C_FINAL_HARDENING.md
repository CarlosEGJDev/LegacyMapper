# LegacyMapper Post-V5 — Gate C
## Final Pre-H5 Technical Hardening: Cross-Project BL Resolution, Template Independence, Consumer CLI Decision, and Selected Remaining Product Debt

### Status

Pre-H5 Gate A = PASS.
Pre-H5 Gate A.1 = PASS.
Pre-H5 Gate B = PASS.
Pre-H5 Gate B.1 = PASS.
H5 = NOT_STARTED.

This is the **final technical gate before H5**.

The goal is to leave LegacyMapper functionally and architecturally ~99.9% ready before H5, so that H5 is validation and closure rather than construction.

Do not start H5 until Gate C is explicitly PASS.
Do not start V6.

---

# 1. Scope

Resolve or formally close by decision:

```text
DT-04  Cross-project BL / call resolution
DT-07  Second human template validation
DT-08  Selected lower-priority product debt
UX-03  Consumer CLI decision
```

Also perform a final pre-H5 debt sweep to ensure no critical/high product debt remains hidden.

Do not reopen already-passed Gates A/A.1/B/B.1 unless a real regression is found.

---

# 2. Product principle

LegacyMapper must be able to explain a legacy system from persisted deterministic knowledge with maximal practical depth, while preserving uncertainty.

Target behavioral route:

```text
View
→ UI event / handler
→ code-behind/controller
→ business class
→ cross-project business/service class
→ DAO/repository/data layer
→ stored procedure / SQL
→ database
```

When any step is not provable:

```text
UNRESOLVED
```

Never infer continuity just because names look similar.

---

# 3. DT-04 — Cross-project BL resolution

This is the main technical objective of Gate C.

Improve deterministic resolution across solution projects using only evidence such as:

```text
project references
assembly references
namespace imports
fully-qualified type names
class/method declarations
method signatures
constructor/member types
inheritance/interfaces where useful
literal class/member calls
known project dependency graph
```

Do not require compilation.
Do not load or execute legacy assemblies.

---

# 4. Cross-project resolution model

Build an explicit deterministic symbol/call resolution layer:

```text
Call site
→ candidate symbol
→ declaring type
→ project/assembly ownership
→ candidate target method(s)
→ deterministic disambiguation
→ resolved edge or unresolved candidates
```

Each persisted cross-project edge must record:

```text
source symbol
target symbol if resolved
source project
target project
resolution basis
candidate count
status
source_refs
```

Statuses:

```text
CONFIRMED
INFERRED
UNRESOLVED
```

---

# 5. Conservative resolution precedence

Use precedence such as:

```text
1. exact fully-qualified symbol match
2. exact declared type + method signature match
3. project reference + namespace/type match
4. unique candidate under imported namespaces
5. otherwise unresolved
```

Never choose a target based only on:

```text
same method name
same class basename
same filename
proximity in solution
```

Ambiguity must remain visible.

---

# 6. Overloads and dynamic dispatch

Resolve overloads only when sufficient static evidence exists. Consider:

```text
argument count
literal/static argument types
declared variable types
ByVal/ByRef
generic arity if supported
optional parameters
```

If multiple candidates remain:

```text
UNRESOLVED_AMBIGUOUS_CALL
```

For interface/base dispatch, record declared target and concrete candidates. Only mark a concrete implementation CONFIRMED when uniquely determined statically.

Otherwise:

```text
UNRESOLVED_DYNAMIC_DISPATCH
```

---

# 7. External assembly boundary

If referenced code is not present in source:

```text
EXTERNAL_ASSEMBLY_BOUNDARY
```

Persist assembly/reference identity, known symbol, call site, and status.

Do not fabricate internals.

---

# 8. Continue to data

Once a cross-project target is resolved, continue through the existing deterministic flow/database resolver:

```text
web project
→ BL project
→ data project
→ stored procedure / SQL
```

Reuse existing DB resolution. Do not create a parallel pipeline.

---

# 9. Persist results in Evidence

Cross-project resolution must be persisted in Evidence, not calculated only for final documentation.

Downstream consumers:

```text
AI context
docs
visuals
deliver
behavioral documentation
```

must consume persisted relationships and must not reread source after analysis.

---

# 10. Measurement

Before/after metrics must include:

```text
cross-project call candidates
resolved
ambiguous
external
unresolved
routes reaching data
routes reaching stored procedures
```

Do not claim success merely because resolved counts increase; every new resolved edge must have a deterministic basis.

---

# 11. Representative fixtures

Cover at least:

```text
Web project → BL project → DAL project
fully-qualified call
imported namespace call
two projects with same class name
two overloads
interface dispatch
missing referenced source assembly
project reference absent
ambiguous candidates
resolved call continuing to stored procedure
```

Expected outputs must be deterministic.

---

# 12. DT-07 — Second human template

Create a second built-in template, e.g.:

```text
legacy_documenter/templates/human/executive/
```

Purpose: prove presentation independence, not redesign semantics.

It must use the same validated model/Evidence/AI interpretation but present a materially different structure.

Example:

```text
solution
projects
important capabilities/views
major flows
data impact
unresolved
minimal technical appendix
```

No duplicate AI interpretation generation.
No source reads.
No provider call merely because template changes.

---

# 13. Template independence proof

Prove:

```text
same semantic model
→ human/default
→ human/executive
```

with different presentation but the same underlying claims, statuses, and source refs.

Template must not:

```text
promote AI_INTERPRETATION
hide UNRESOLVED
change evidence refs
mutate canonical knowledge
invoke provider
```

---

# 14. UX-03 — Consumer CLI decision

Current state:

```text
Consumer API exists
public Consumer CLI does not
```

Make an explicit decision before H5:

```text
A. IMPLEMENT NOW
B. ACCEPT AS NON-BLOCKING FUTURE CAPABILITY
```

If implementing, add only a thin read-only CLI over the existing Consumer API, with no new semantics, no writes, and no provider requirement.

If deferring, document rationale, classify as FUTURE_CAPABILITY, and prove H5 does not depend on it.

Do not leave UX-03 ambiguous.

---

# 15. DT-08 — Selected remaining product debt

Review only debt affecting:

```text
correctness
portability
runtime reliability
determinism
Evidence integrity
public CLI behavior
source-offline operation
human deliverable correctness
```

Do not do repository-wide cleanup.

Cosmetic refactors, large-module cleanup, docstrings, generic naming, and historical formatting are non-blocking unless they create an actual product risk.

---

# 16. Dependency / exception sweep

Review newly introduced or touched code for:

```text
new dependency cycles
uncaught expected-input exceptions
broad exception handlers in Gate C code
absolute path coupling
provider coupling
source rereads downstream
```

Fix regressions introduced by post-V5 work. Do not refactor unrelated historical modules.

---

# 17. Accepted Gate B.1 limitations

Do not speculate-fix:

```text
~2,570 relative assets whose runtime base depends on host/execution context
scan_summary.root/source_repository physical compatibility fields
UNRESOLVED_HISTORICAL_PARITY mechanical cause of old H4 package
```

These may remain accepted if ambiguity is explicit and no new identity logic depends on physical paths.

If deterministic host context safely resolves some relative assets, it may be added, but this is not required for Gate C PASS.

---

# 18. Tests — directed first

Create focused tests, for example:

```text
tests/test_post_v5_gate_c_final_hardening.py
```

Cover at least:

```text
exact cross-project type/method resolution
namespace/import resolution
overload disambiguation
ambiguous overload preserved
same class name across projects preserved
interface/base dispatch unresolved when dynamic
external assembly boundary
resolved cross-project route reaches existing DB resolver
persisted cross-project evidence survives source removal
AI/docs/visuals/deliver consume persisted relationships
second template uses same semantic model
second template requires zero provider calls
template cannot hide unresolved
consumer CLI decision covered by tests/docs
no new dependency cycles
no new source reads downstream
```

No real provider calls in tests.

---

# 19. Test execution policy

During implementation:

```text
directed Gate C tests only
```

Then relevant existing tests:

```text
call resolver
flow resolver
database resolver
Evidence
H1
H3
H4 behavior/templates
Gates A/A.1/B/B.1
```

Then exactly one final full suite:

```text
python -X utf8 -m unittest discover -s tests
```

Require 0 failures / 0 errors.

---

# 20. IST validation strategy

Do not repeatedly reanalyze IST.

Develop with fixtures.

When stable, if Evidence changes require it, perform ONE deterministic IST analysis and record:

```text
scanner count
analyzer count
duration
cross-project resolution counts
data-route reachability before/after
stored procedure reachability before/after
unresolved counts
external-boundary counts
```

Then validate downstream with source access blocked/instrumented:

```text
source_reads = 0
scanner = 0
analyzer = 0
```

Run behavior, docs, visuals, deliver default, deliver second template, and replay interpretation where applicable.

---

# 21. Human documentation acceptance

For representative resolved routes verify the final human document can explain:

```text
what the view does
action
handler
business class
cross-project class
data class
stored procedure / SQL
database
```

For unresolved routes, explicitly say unresolved.

---

# 22. Final pre-H5 debt sweep

Classify remaining items as:

```text
BLOCKING_BEFORE_H5
ACCEPTED_LIMITATION
FUTURE_CAPABILITY
HISTORICAL_COMPATIBILITY
VISUAL_POLISH_ONLY
```

Requirement:

```text
BLOCKING_BEFORE_H5 = 0
```

Any remaining correctness, portability, determinism, or Evidence-integrity blocker must be fixed before PASS.

---

# 23. Required reports

Create:

```text
docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_RESULT.md
```

and preferably:

```text
docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json
```

Include cross-project design, before/after measurements, ambiguity preservation, second-template proof, UX-03 decision, DT-08 decisions, dependency/exception audit, IST validation, and remaining-debt classification.

---

# 24. State updates

Update:

```text
PROJECT_STATE.json
README.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

Successful state:

```text
PRE_H5_GATE_C_FINAL_HARDENING = PASS
PRE_H5_BLOCKING_DEBT = 0
H5 = NOT_STARTED
```

Next step after explicit human review:

```text
H5_REAL_IST_VALIDATION_AND_CLOSURE
```

---

# 25. Git authority

```text
edit production code = YES
edit tests = YES
edit docs/state = YES
commit = NO
push = NO
tag = NO
```

No Git versioning without explicit human authorization.

---

# 26. Success criteria

Gate C passes only if:

```text
cross-project BL resolution materially improves with deterministic evidence
ambiguous/dynamic/external calls remain explicit rather than guessed
resolved cross-project routes persist in Evidence
downstream works without source
second human template proves presentation independence
second template does not trigger new AI interpretation
UX-03 has an explicit implemented-or-deferred decision
selected product-critical DT-08 debt is closed
no new high-risk dependency/runtime defects remain
BLOCKING_BEFORE_H5 = 0
one final full suite passes
H5 remains NOT_STARTED
```

Final principle:

> **H5 should validate the finished product, not discover architectural work still waiting to be built.**
