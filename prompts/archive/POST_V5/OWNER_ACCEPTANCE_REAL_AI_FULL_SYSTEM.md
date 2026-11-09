# LegacyMapper — Owner Acceptance Real AI Full-System Run

## Authorization

The owner authorizes the real AI phase of the standalone acceptance.

Current state:
```text
STANDALONE_INSTALL = PASS
FRESH_IST_ANALYSIS = PASS
ACC01_STUB_REHEARSAL = PASS
READY_FOR_REAL_AI_ACCEPTANCE = YES
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

Official remediation checkpoint:
```text
branch = main
commit = de0e822b7b02a60ffaa4447fd840b425795e8b77
subject = Add full-system AI interpretation and resume support
wheel = legacymapper-5.9.0-py3-none-any.whl
wheel SHA-256 = bd168371e2353d3a9d02baa9c1e89a150eeebebac6d2c158b82c938f894e34a9
```

Fresh standalone baseline to reuse:
```text
C:\LegacyMapperAcceptance\output\baseline
```

Do NOT rerun IST analysis.

## 1. Manual quota preflight

Before the first real provider request, the owner must manually verify:
```text
/user
/usage
```

Expected account:
```text
CarlosEGJDev
```

Continue only if:
```text
COPILOT_ACCOUNT = CarlosEGJDev
COPILOT_USAGE_REVIEWED = YES
```

SDK/account preflight must still report authenticated, expected account matches, no unexpected token override.

If mismatch:
```text
STOP
real provider calls = 0
```

## 2. Reuse baseline only

Use:
```text
C:\LegacyMapperAcceptance\output\baseline
```

Known baseline:
```text
files = 45874
solutions = 91
projects = 228
Evidence schema = 1.0
```

Verify its hash still matches the STUB rehearsal receipt.

During interpretation/projection:
```text
scanner = 0
analyzer = 0
source reads = 0
```

## 3. Official standalone runtime

Use the official wheel installed non-editable in the clean acceptance runtime.

Require:
```text
PYTHONPATH = empty
import = site-packages
no dependency on repository checkout
no H5 baseline reuse
no historical AI response reuse
```

## 4. Separate real state

Do not overwrite STUB evidence/state.

Use separate real AI paths, e.g.:
```text
C:\LegacyMapperAcceptance\work\real_ai_state\
C:\LegacyMapperAcceptance\output\real_ai_product\
```

## 5. First real-AI quality gate

Before the complete sweep, perform a small bounded real-provider sample through the production orchestration.

Include where possible:
```text
SYSTEM
1 SOLUTION
2 PROJECTS
1 VIEW
1 FLOW
1 DATA
1 non-UI project
```

Target:
```text
10–20 real provider requests maximum
```

Verify:
```text
provider adapter works
structured response parses
truth-state validator works
text quality is useful
no unsupported business invention
no provenance leaks
responses persist successfully
```

If the CLI cannot safely select a bounded subset, use the smallest supported resumable unit and document it.

## 6. Quality gate

Require:
```text
STRUCTURED_RESPONSE_VALID = PASS
PROVIDER_ADAPTER = PASS
PERSISTENCE = PASS
NO_NAME_ONLY_BUSINESS_INFERENCE = PASS
NO_OBSOLESCENCE_INFERENCE = PASS
UNRESOLVED_PRESERVED = PASS
HUMAN_LANGUAGE_QUALITY = ACCEPTABLE
```

If any fail:
```text
REAL_AI_QUALITY_GATE = FAIL
STOP
```

If all pass:
```text
REAL_AI_QUALITY_GATE = PASS
```

continue.

## 7. Full-system real AI interpretation

Run:
```text
SYSTEM
→ SOLUTION
→ PROJECT / COMPONENT
→ VIEW / BEHAVIOR
→ CROSS-PROJECT FLOW
→ DATA INTERACTION
```

Expected plan from STUB:
```text
planned requests = 597
SYSTEM = 1
SOLUTION = 85
PROJECT = 184
VIEW = 135
FLOW = 72
DATA = 120
```

If planner differs, report why.

## 8. Persist every response immediately

Persist:
```text
deterministic request identity
input hash
response hash
validation status
provider metadata
```

Do not wait until the end.

## 9. Resume without replay

If interrupted by quota/provider/network/manual stop:
```text
preserve completed state
mark remaining requests pending
do not mark pending as successful
```

On restart:
```text
completed -> replay persisted response, provider calls 0
pending -> continue normally
```

Never discard valid real accepted state merely to restart.

## 10. Quota exhaustion

If Copilot quota is exhausted:
```text
STOP CLEANLY
```

Report:
```text
completed real requests
remaining requests
coverage completed
coverage pending
last successful request id
resume command
```

State becomes:
```text
FULL_SYSTEM_AI_INTERPRETATION = INCOMPLETE_QUOTA
```

Do not silently switch accounts.
Any account switch requires owner action and a new preflight.

## 11. Account invariant

Expected:
```text
CarlosEGJDev
```

Do not silently use another account.

## 12. Coverage contract

Every project must eventually be one of:
```text
HUMAN_AND_MACHINE_DOCUMENTED
MACHINE_ONLY_DOCUMENTED
UNRESOLVED_NO_SOLUTION
CONTROLLED_ERROR
```

During interruption only:
```text
PENDING_INTERPRETATION
```

Final PASS requires:
```text
PENDING_INTERPRETATION = 0
silent omissions = 0
```

Expected corpus:
```text
solutions = 91
projects = 228
```

Expected structural coverage from STUB:
```text
184 HUMAN_AND_MACHINE_DOCUMENTED
9 MACHINE_ONLY_DOCUMENTED
35 UNRESOLVED_NO_SOLUTION
0 CONTROLLED_ERROR
```

## 13. Project real semantic state

Only after required real interpretation is complete, generate:
```text
human\
    index.html
    IST_Complete.pdf
    executive\
    system\
    solutions\
    projects\
    views\
    flows\
    data\
    diagrams\

ai\
internal\
```

Projection must have:
```text
provider calls = 0
scanner = 0
analyzer = 0
source reads = 0
```

## 14. Validate real product

Require:
```text
broken links = 0
missing assets = 0
invalid JSON = 0
dangling IDs = 0
duplicate IDs = 0
human provenance leaks = 0
invalid human states = 0
silent project omissions = 0
```

Human states only:
```text
Confirmado
Inferido
No resuelto
```

## 15. Manual quality review

Owner should inspect at least:
```text
system overview
executive overview
5 solutions
large UI project
small UI project
non-UI project
cross-project flow
data-heavy project
unresolved project
some reconstructed views
```

Check:
```text
behavior is explained
readable without source
no invented business meaning
uncertainties explicit
routes/relationships useful
```

## 16. Replay proof after completion

Re-run `interpret-system` against the same persisted real state.

Require:
```text
new provider calls = 0
all completed requests replayed
coverage unchanged
```

Regenerate product:
```text
provider calls = 0
```

## 17. Final evidence

Update/create:
```text
C:\LegacyMapperAcceptance\output\OWNER_ACCEPTANCE_RESULT.md
C:\LegacyMapperAcceptance\output\OWNER_ACCEPTANCE_EVIDENCE.json
```

Include:
```text
commit SHA
wheel SHA-256
baseline identity/hash
provider
authenticated account
model/default model behavior
planned/successful/replayed/failed requests
retries/quota interruptions
coverage states
human product
machine product
validation
second-run provider calls
projection provider calls
scanner/analyzer/source-read counters
manual owner review
blocking defects
final verdict
```

No secrets.

## 18. PASS gate

PASS only if:
```text
STANDALONE_INSTALL = PASS
FRESH_IST_ANALYSIS = PASS
FULL_SYSTEM_AI_INTERPRETATION = PASS
HUMAN_KNOWLEDGE_PRODUCT = PASS
MACHINE_KNOWLEDGE_PRODUCT = PASS
RESUME_WITHOUT_REPLAY = PASS
SECOND_REAL_RUN_PROVIDER_CALLS = 0
PROJECTION_PROVIDER_CALLS = 0
SILENT_OMISSIONS = 0
BLOCKING_ACCEPTANCE_DEFECTS = 0
MANUAL_OWNER_REVIEW = PASS
```

Then:
```text
OWNER_STANDALONE_ACCEPTANCE = PASS
```

If quota runs out first:
```text
OWNER_STANDALONE_ACCEPTANCE = INCOMPLETE_QUOTA_RESUMABLE
```

## 19. Authority

```text
repository edits = NO
commit = NO
push = NO
tag = NO
V6 start = NO

real provider calls = YES
full-system AI interpretation = YES
baseline reuse = YES
fresh IST re-analysis = NO
```

If a product defect is found:
```text
do not patch acceptance environment
record defect
stop as appropriate
return to repository for remediation
```

> Prove that LegacyMapper can interpret the complete system with real AI, persist every result, resume without replay, and generate useful human/machine knowledge outside the development environment.
