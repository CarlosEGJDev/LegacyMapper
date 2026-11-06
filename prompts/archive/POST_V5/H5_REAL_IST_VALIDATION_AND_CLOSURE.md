# LegacyMapper Post-V5 — H5 Real IST Validation and Closure

## Entry gate

Start H5 only after the authorized H4 Git checkpoint has been committed and pushed successfully.

Required starting state:

```text
H1 = CLOSED
H2 = CLOSED
H3 = CLOSED
H4 = CLOSED
H4_OWNER_APPROVAL = APPROVED
H4_BLOCKING_DEBT = 0
POST_H4_STATE_CONSISTENCY_SYNC = PASS
H5 = NOT_STARTED
V6 = NOT_STARTED
```

H5 is the **final Post-V5 validation milestone**.

This is not V6.

---

# 1. H5 objective

Validate LegacyMapper against the **complete real IST corpus** and close Post-V5 if the product contract holds at scale.

Core principle:

> **Analyze once, interpret/project many times.**

H5 must validate that the final product works as a standalone knowledge product across the real IST estate without reverting to per-project rescans.

---

# 2. Authoritative product contract to validate

Final public package:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

Human contract:

```text
human = interpreted explanation
```

Machine/internal contract:

```text
ai/internal = structured knowledge + provenance/evidence
```

Human documentation should remain free of normal-reading raw provenance such as:

```text
EP-*
FLOW-*
CALL-*
DAO-*
source file paths
source line numbers
provider/model diagnostics
raw Evidence tables
```

Human states:

```text
Confirmado
Inferido
No resuelto
```

---

# 3. IST scope

H5 must validate **all relevant IST solutions/projects**, not only `WebPREPrevencion`.

Use the real IST source root already established by repository/runtime configuration.

Do not hardcode one pilot project as the H5 product scope.

First inventory the actual solution/project population from the deterministic analysis.

Report:

```text
solutions discovered
projects discovered
technology/adapters represented
projects eligible for human docs
projects with UI/views
projects with no UI
projects with unresolved structure
```

---

# 4. One deterministic IST analysis

Perform exactly one fresh authoritative deterministic analysis of the H5 IST corpus.

This is the H5 baseline build.

Allowed:

```text
scanner = 1 full IST run
analyzer = 1 full IST run
```

Not allowed:

```text
one scan per project
one scan per solution
rescans during documentation
rescans during AI interpretation
rescans during presentation changes
```

Persist the resulting Evidence/baseline as the H5 authoritative reusable state.

Record:

```text
source root
file count
byte count
analyzer version
analyzer fingerprint
Evidence schema versions
baseline hash/fingerprint
duration
scanner/analyzer invocation counts
```

---

# 5. Enumerate from persisted Evidence

After the single deterministic run, all downstream project/solution validation must use persisted Evidence.

No source-tree reads downstream unless a defect investigation is explicitly opened and documented.

Validate:

```text
solution discovery
project discovery
project dependencies
cross-project calls
UI/view inventories
view relationships
data/procedure routes
usage classification
unresolved preservation
```

---

# 6. AI interpretation strategy

Do not automatically interpret every project with unlimited provider calls.

First classify projects/solutions into representative validation cohorts using deterministic metadata.

At minimum cover:

```text
large web/UI project
small web/UI project
project with cross-project dependencies
data/business project without primary UI
project/solution with unresolved or sparse evidence
```

Use the real configured provider only where H5 needs to validate the AI interpretation contract.

Provider calls must be bounded and documented.

Reuse identical persisted interpretation responses whenever the same input is regenerated.

No fake provider fallback for claims of real-AI validation.

---

# 7. Validate multi-project / multi-solution behavior

For each selected representative target, validate:

```text
human package generation
AI knowledge generation
internal provenance preservation
diagram generation where applicable
screen reconstruction where applicable
technical routes
cross-project calls
data/procedure mapping
unresolved behavior
```

Additionally validate machine-only output for projects where human UI documentation is not applicable.

Do not force a screen/view model onto non-UI projects.

---

# 8. Scale validation

Validate the final system at IST scale.

Measure:

```text
total packages/project projections generated
total human HTML files
total PDFs
total AI knowledge artifacts
total diagrams
total wireframes
broken links
missing assets
invalid JSON
overflow/layout failures detected by structural guards
provider calls
downstream source reads
scanner/analyzer counts
```

Do not optimize for high output counts; optimize for contract correctness.

---

# 9. Standalone/runtime validation

Validate installation/execution outside the development checkout.

Use an isolated environment/wheel.

Required:

```text
no PYTHONPATH dependency
package resources available
templates available
CLI works from unrelated working directory
paths with spaces/Unicode remain valid
provider optional for deterministic-only paths
controlled failure when provider required but unavailable
```

Confirm normal end-user workflow remains understandable.

---

# 10. Analyze-once invariant

Instrument or otherwise prove:

```text
full deterministic IST analyses = 1
scanner invocations after baseline = 0
analyzer invocations after baseline = 0
downstream source opens = 0
```

for interpretation/docs/visuals/package replay.

If downstream source reads occur:

```text
H5 cannot close
investigate and classify as blocking unless explicitly justified by contract
```

---

# 11. Knowledge truth invariants

Validate:

```text
Existence in source != reachable != observably used
Absence of observable usage evidence != evidence of obsolescence
Unresolved remains unresolved
AI does not silently promote inference to confirmed
AI does not invent unsupported business facts
No automatic canonicalization
Human remains final authority
```

Validate statuses across generated human and machine projections.

---

# 12. Human documentation validation at scale

Sample across different projects/solutions.

Check:

```text
solution/project names are correct
purpose wording is conservative
useful behavior before metrics
technical routes are readable
human documentation does not expose Evidence machinery
states are understandable
unknowns are concise
no repeated IA badges
diagrams fit
wireframes readable
```

Do not require every project to have the exact same document sections if evidence does not support them.

---

# 13. AI knowledge validation

Validate machine-readable package schemas and semantic usefulness.

At minimum inspect:

```text
knowledge.json
architecture.json
views.json when applicable
flows.json
data.json
unresolved.json
provenance.json
KNOWLEDGE_PACKAGE.json
```

Check:

```text
stable IDs
valid references
no dangling IDs
provenance retained
statuses preserved
human-confirmed knowledge remains distinct
```

---

# 14. Debt policy

H5 is validation and closure, not a new architecture phase.

Classify findings as:

```text
BLOCKING
OBSERVATION
FUTURE_CAPABILITY
HISTORICAL_COMPATIBILITY
```

H5 may close only with:

```text
BLOCKING = 0
```

Do not create V6 work to hide unresolved Post-V5 fundamentals.

If a fundamental Post-V5 product defect is found, fix it within H5 before closure.

---

# 15. Test strategy

During H5 implementation/validation:

```text
targeted tests while investigating
```

At final stabilization:

```text
python -X utf8 -m unittest discover -s tests
```

Run the full suite once on the final H5 tree.

Required:

```text
0 failures
0 errors
```

Expected fresh-clone skips must remain explained.

---

# 16. H5 reports

Create:

```text
docs/POST_V5/H5_REAL_IST_VALIDATION_AND_CLOSURE_RESULT.md
docs/POST_V5/H5_REAL_IST_VALIDATION_EVIDENCE.json
```

Include:

```text
IST scope inventory
single-baseline proof
analyzer/scanner counts
provider calls
representative project/solution matrix
runtime/clean-room validation
human package validation
AI knowledge validation
cross-project/data validation
scale measurements
full suite
debt classification
blocking debt count
```

---

# 17. Closure decision

If all closure gates pass:

```text
H5 = CLOSED
POST_V5 = CLOSED
BLOCKING_DEBT = 0
V6 = NOT_STARTED
```

Do not automatically start V6.

If any blocking defect remains:

```text
H5 = IN_PROGRESS
POST_V5 = NOT_CLOSED
```

Document the blocker precisely.

---

# 18. Git authority for H5

For this H5 execution prompt:

```text
production edits needed to fix H5 blockers = YES
tests = YES
docs/state updates = YES
real IST analysis = YES (exactly one authoritative deterministic run)
bounded real provider validation = YES

commit = NO
push = NO
tag = NO
```

H5 implementation/validation must finish first.

Git closure will require separate explicit owner authorization after H5 approval.

---

# Final principles

> **Analyze once, interpret/project many times.**

> **H5 validates the complete real IST estate; it does not redesign H4.**

> **Post-V5 closes only when the real product contract holds at scale with zero blocking debt.**

> **V6 remains NOT_STARTED after H5 unless the owner explicitly starts it.**
