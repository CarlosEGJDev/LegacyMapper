# LegacyMapper Post-V5 — H1 Integrated Delivery
## AI-only interpretation from an existing deterministic baseline

### Execution model
Complete this milestone in one integrated round whenever reasonably possible.

Normal correction budget:

```text
R1 = Integrated Delivery
R2 = Targeted Corrections only if real evidence requires them
R3 = Final Verification & Closure
```

If R1 is clean, skip R2 and go directly to R3/closure.
Do not create micro-rounds.

---

## 1. Objective

Implement and validate the missing post-V5 capability:

> Run AI interpretation against an already generated, valid deterministic LegacyMapper output without rescanning or reanalyzing the source repository.

Target model:

```text
source repo
   ↓
deterministic analysis (once)
   ↓
persisted deterministic baseline
   ├── Evidence
   ├── AI context
   ├── manifests
   ├── provenance
   └── analyzer/repository identity
            ↓
       AI-only execution
            ↓
       AI proposals / interpretation
```

Permanent rules:

> Analyze once, interpret many times.

> Python discovers and validates; AI interprets.

The AI-only path MUST NOT silently rebuild deterministic analysis.

---

## 2. Read first

Read actual current repository state before changing code.

At minimum:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
README.md
docs/PROJECT_RECOVERY.md

docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md
docs/POST_V5/POST_V5_DOCUMENTATION_CONSOLIDATION_RESULT.md

LEGACYMAPPER_V5_ROADMAP.md
LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md
LEGACYMAPPER_LESSONS_LEARNED.md

docs/V5/V5_OPERATIONS_GUIDE.md
docs/V5/V5_FINAL_CLOSURE.md
docs/V5/V5_FINAL_CLOSURE.json
docs/V5/V5_FINAL_BASELINE.json
```

Also inspect the actual implementation of:

```text
main.py
full pipeline
analyze pipeline
AI interpretation stage
proposal generation
AI provider abstraction
AI context persistence/loading
Evidence persistence/loading
repository/analyzer manifests
review/canonical workflow
consumer read API
```

Do not trust old summaries over current code.

---

## 3. Empirical discovery first

Before designing the command, determine exactly what the deterministic output already persists.

Use a real completed deterministic output if available, preferably:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\outputs\IST_REAL
```

or another current clean deterministic output.

Document:

```text
which files are sufficient to reconstruct AI input
which files contain Evidence
which files contain AI context
which manifests/fingerprints exist
which source/repository identity exists
which runtime objects currently assume in-memory analysis state
which AI stages can already be reused
which parts would accidentally rescan the source
```

Do not re-run IST just to answer these questions if a valid persisted output already exists.

If no suitable persisted output exists, use a small deterministic fixture/output for development and reserve IST for final real validation.

---

## 4. Required UX

Expose one clear public CLI entry point for AI-only execution.

Do not lock the name before inspecting existing CLI conventions.

Preferred candidates:

```text
interpret
ai-only
interpret-existing
```

Choose the name that best matches current CLI style and document why.

Desired shape:

```powershell
python main.py interpret "<existing-output>" [AI/provider options]
```

The command MUST accept a deterministic output directory, not a source repository.

Its public help must clearly say that it:

```text
does not rescan the repository
does not rebuild deterministic Evidence
requires a valid existing deterministic baseline
runs AI interpretation/proposal generation only
```

Reuse actual provider/configuration conventions already implemented.
Do not invent a second provider configuration model.

---

## 5. Mandatory validation gate

Before any AI provider invocation, validate the persisted baseline.

At minimum, using real repository contracts:

```text
output directory exists
deterministic run completed successfully
Evidence exists
Evidence manifest exists and validates
AI context required for interpretation exists
schema/version is supported
analyzer version/fingerprint is known/compatible
repository/source identity is available
required provenance references resolve
baseline is not obviously corrupt/incomplete
```

Reuse existing validators/contracts wherever possible.
Do not duplicate Evidence validation logic.

If invalid, emit:

```text
AI_ONLY_INPUT_INVALID
```

or the repository's equivalent structured failure state.

Critical invariant:

```text
invalid baseline
→ zero provider calls
```

Add a test proving this.

---

## 6. No deterministic re-analysis

The H1 path must not:

```text
scan source files
parse source files
resolve calls again
rebuild normalized Evidence from source
regenerate deterministic documentation as a side effect
```

It may read persisted deterministic artifacts.

Add tests/guards proving the AI-only path does not require the original source repository to still exist, if persisted output contains all required information.

Strong acceptance test:

```text
1. create deterministic output from a small fixture/repository
2. move/remove/rename the original source fixture
3. execute AI-only using only persisted output
4. AI-only still succeeds with Fake provider
```

Do not delete or modify the real IST source.

---

## 7. Output isolation and provenance

AI-only executions must not corrupt or ambiguously overwrite the deterministic baseline.

Prefer an architecture-consistent solution such as:

```text
<baseline>\ai_runs\<run-id>\
```

or:

```text
--output <ai-output>
```

Choose the smallest solution consistent with current architecture.

Every AI-only result must record enough provenance to identify:

```text
source deterministic output
repository identity
analyzer version
analyzer fingerprint
Evidence manifest identity/hash if available
AI context version
provider
model
AI/profile/configuration
generation time
proposal status
canonical = false
```

Do not turn AI output into canonical knowledge automatically.

---

## 8. Review compatibility

H1 proposals must remain compatible with existing V5 review flow:

```text
proposal
→ review prepare
→ human decision
→ canonical only after explicit human authority
```

Do not create a second review mechanism.
Do not auto-approve.
Do not auto-canonicalize.

If compatibility requires a small adapter/loading change, implement the minimum necessary.

---

## 9. Fake provider first

All automated tests must use the existing Fake provider or equivalent networkless provider.

Requirements:

```text
networkless
deterministic enough for tests
grounded in real persisted Evidence
Evidence guard remains active
```

Do not weaken grounding/security checks just to make H1 work.

If a generic Fake produces invalid ungrounded output, adapt the test fixture/provider response to quote/reference valid Evidence instead of weakening validation.

---

## 10. Real provider

Do not make a real external/provider call unless the current repository explicitly documents a safe manual verification path and configuration already exists.

Real-provider verification is optional for H1 integrated delivery.

A successful Fake-provider end-to-end path is mandatory.

If real-provider validation is not run, document that accurately.

---

## 11. Tests

Add focused tests covering at least:

```text
valid persisted baseline accepted
missing output rejected
missing Evidence rejected
missing/invalid manifest rejected
unsupported analyzer/schema rejected if applicable
missing AI context rejected
provider not called on invalid input
AI-only does not invoke scanner/analyzer
AI-only works without original source tree
Fake provider generates grounded proposal
proposal remains non-canonical
review flow can consume H1 proposal
deterministic baseline remains unchanged
CLI help documents behavior accurately
```

Run directed tests first.

Then run:

```text
python -m unittest discover -s tests
```

Expected:

```text
0 failures
0 errors
```

Do not hardcode the old test total if new tests increase it.
Record exact totals.

---

## 12. Real validation

### 12.1 Small real validation

Use a small repository/output first.

Prove:

```text
deterministic run
→ persisted baseline
→ AI-only Fake run
→ proposal generated
→ source can be unavailable
→ deterministic baseline unchanged
```

Compare hashes/manifests before and after where practical.

### 12.2 IST validation

Use an already existing valid IST deterministic output if available.

The purpose is to prove:

```text
AI-only can load the large persisted IST baseline
without rescanning IST
```

Do NOT run another full IST deterministic analysis unless there is no valid persisted IST output and it is genuinely required.

For H1, a Fake-provider AI-only run against a representative IST AI context/segment is sufficient if a full provider request would be excessive.

Report:

```text
startup/load time
number of AI contexts/segments considered
provider calls
proposal count
whether source scan/analyze stages ran (must be NO)
baseline file delta (must be 0 for deterministic artifacts)
```

---

## 13. Performance intent

H1 exists partly to eliminate repeated expensive deterministic analysis.

Report a simple comparison:

```text
full deterministic analysis cost (historical/current baseline)
vs
AI-only load + interpretation preparation cost
```

Do not over-optimize in H1.
Just prove deterministic source analysis is not repeated.

---

## 14. Documentation

Update only canonical docs needed for the implemented feature:

```text
README.md
docs/V5/V5_OPERATIONS_GUIDE.md or current canonical operations guide
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json only after successful validation
```

Document exact commands from actual `--help`.

Clearly distinguish:

```text
deterministic full
full with AI
AI-only from persisted output
review/canonical
```

---

## 15. Product state after successful H1

If all acceptance criteria pass, update state to equivalent of:

```text
POST_V5
H1_AI_ONLY = IMPLEMENTED_AND_VALIDATED
NEXT = H2_HUMAN_DOCUMENTATION_BY_AUDIENCE
```

Do not start H2.
Do not call this V6.

---

## 16. Non-goals

Do not implement:

```text
H2 audience redesign
H3 visual diagrams
H4 HTML/PDF generation
H5 final human acceptance
third technology
Plugin Runtime
consumer CLI
deep Python inference
new provider family
large refactor
V6
```

H1 has one objective:

> Reuse persisted deterministic knowledge for AI interpretation without source re-analysis.

---

## 17. Result document

Create:

```text
docs/POST_V5/H1_AI_ONLY_INTEGRATED_DELIVERY_RESULT.md
```

Include:

```text
selected CLI name and rationale
empirical persisted-output inventory
architecture changes
files changed
validation gate
proof of zero provider calls on invalid baseline
proof no deterministic analysis runs
small end-to-end test
IST persisted-baseline validation
directed tests
full suite totals
baseline before/after comparison
known limitations
debt introduced
Git status
recommendation
```

Final state must be exactly one of:

```text
H1_READY_FOR_HUMAN_REVIEW
H1_TARGETED_CORRECTION_REQUIRED
H1_BLOCKED
H1_OPEN_DECISION
```

---

## 18. Git authority

For this H1 integrated delivery:

```text
edit production code = YES
edit tests = YES
edit documentation/state = YES

commit = NO
push = NO
tag = NO
```

Leave all changes in the working tree for human review.

---

## 19. Stop conditions

Stop and report instead of inventing if:

```text
persisted deterministic output lacks information fundamentally required by AI
H1 would require breaking a closed V5 contract
review compatibility would require redesigning V5.7
baseline validation cannot be made reliable without source re-analysis
current AI provider abstraction cannot consume persisted context without architectural contradiction
```

Use:

```text
H1_OPEN_DECISION
```

with concrete evidence and the smallest decision needed.

---

## 20. Acceptance criterion

H1 is successful when this statement is demonstrably true:

> A user can analyze a repository once, keep the deterministic LegacyMapper output, and later run AI interpretation/proposal generation from that persisted output without rescanning the source repository, while retaining provenance, grounding, review compatibility and human authority.
