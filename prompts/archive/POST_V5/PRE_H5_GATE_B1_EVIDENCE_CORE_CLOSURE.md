# LegacyMapper Post-V5 — Gate B.1
## Evidence-Core Closure: Asset Resolution, Navigation Completeness, Provenance Cleanup, Size Reduction, and Behavioral Parity

### Status

Pre-H5 Gate A = PASS.
Pre-H5 Gate A.1 = PASS.
Pre-H5 Gate B = PASS.
H5 = NOT_STARTED.
Gate C = NOT_STARTED.

Gate B achieved the architectural objective: UI/navigation/style facts are persisted and downstream rendering no longer rereads source.

This Gate B.1 is a **narrow closure round** to remove the remaining product-level residues discovered by the real IST Gate B validation before moving to Gate C.

Do not reopen Gate B architecture.
Do not start Gate C.
Do not start H5.
Do not start V6.

---

# 1. Objective

Close the remaining Gate B residues that still affect:

```text
evidence completeness
navigation completeness
portable provenance
behavioral reproducibility
storage efficiency
maintainability of the new Evidence path
```

Resolve exactly:

```text
B1-01  Resolve supported ~/ asset paths against application root
B1-02  Add menu/config → view navigation evidence where deterministically supported
B1-03  Reconcile usage-summary behavioral drift
B1-04  Remove physical-path leakage from portable provenance projection where safe
B1-05  Replace inherited constant source_snapshot_sha256 behavior with an honest deterministic contract
B1-06  Reduce UI Evidence storage overhead without losing semantics
B1-07  Remove the behavior.ui_evidence <-> behavior.styles dependency cycle
```

Do not touch cross-project BL resolution yet.

---

# 2. Preserve Gate B invariants

Do not regress:

```text
UI/navigation/style facts are authoritative in Evidence Core
behavior/source.py does not reread source
behavior/styles.py does not discover from disk
sidecar is derived and non-authoritative
source may be unavailable after analysis
downstream source_reads = 0
scanner = 0
analyzer = 0
provider = 0 for deterministic projections
stable IDs independent of physical root
old baseline fails explicitly for behavioral UI when UI Evidence is absent
```

---

# 3. B1-01 — Resolve ~/ assets

Gate B reported:

```text
ImageUrl="~/…"
→ 2,727 unresolved assets in IST
```

Implement deterministic WebForms application-root resolution where the project/application root is known from persisted project structure.

Rules:

```text
~/path
→ application root relative path
```

Only mark `CONFIRMED` when the resolved asset exists in the analyzed source snapshot.

If application root is ambiguous:

```text
UNRESOLVED
reason = AMBIGUOUS_APPLICATION_ROOT
```

If resolved logical path does not exist:

```text
UNRESOLVED
reason = ASSET_NOT_FOUND
```

Never guess across unrelated projects.

Persist:

```text
logical asset path
source_refs
resolution basis
status
sha256 when resolved
```

No source reads downstream.

---

# 4. B1-02 — Menu/config → view navigation

Gate B explicitly reports that menu/config → view relationships are not currently extracted.

Add deterministic extraction only for supported patterns that can be proven from source/config.

Examples may include:

```text
menu XML/config entries containing literal page/control paths
web.config/appSettings literal target mappings
static menu/user-control registries
literal navigation tables/config files
```

Do not create a general heuristic crawler.

Each edge must record:

```text
source
target
mechanism
status
source_refs
parameters if literal
```

Dynamic/config-computed targets remain `UNRESOLVED`.

Do not infer menu semantics from filenames alone.

---

# 5. B1-03 — Behavioral usage parity

Gate B observed a material change:

```text
before:
ACTIVE_OBSERVABLE 7
UNRESOLVED_USAGE 114

current:
ACTIVE_OBSERVABLE 7
POSSIBLY_ACTIVE 52
UNRESOLVED_USAGE 62
```

The current direct-source historical algorithm and persisted Evidence agree today, but the earlier H4 package cannot be reproduced.

This must be resolved before H5.

Required work:

```text
identify exact cause of the historical delta
determine whether:
  A. previous H4 package was stale/incorrect
  B. behavior algorithm changed after H4
  C. source snapshot changed
  D. historical fixture/projection differed
```

Use hashes, timestamps, source snapshot identifiers, code revisions, and persisted manifests where available.

Do not simply accept the new counts because they are internally consistent.

Final requirement:

```text
a documented, evidence-backed explanation exists
```

If the previous H4 package was wrong:

```text
mark it historical/superseded
```

If a regression exists:

```text
fix it
```

If irreducibly unknowable:

```text
record UNRESOLVED_HISTORICAL_PARITY
```

but explain why.

---

# 6. B1-04 — Physical vs logical provenance cleanup

Gate B added:

```text
logical_source_id
logical_snapshot_sha256
portable_evidence_sha256
physical_root = compatibility_metadata_not_identity
```

Review all new downstream/portable artifacts.

Required:

```text
portable package identity/hashes must not depend on physical root
HTML/PDF/SVG/template manifests must not expose machine-specific root unless explicitly in diagnostics
```

Historical fields such as:

```text
scan_summary.root
source_repository
```

may remain for compatibility if changing them is unsafe.

But no new logic may treat them as identity.

Add explicit tests proving:

```text
same source copied to two locations
→ same logical identity
→ same UI partitions
→ same portable evidence hash
```

---

# 7. B1-05 — source_snapshot_sha256

Gate B reports:

```text
SYSTEM_CONTEXT.json source_snapshot_sha256
= inherited literal constant
```

This is not acceptable as a final product contract if the field claims to represent the actual snapshot.

Choose one safe outcome:

```text
A. compute it deterministically from the logical source snapshot
B. deprecate/rename it if historical semantics are not really a snapshot hash
C. preserve historical field but add a correct new field and stop relying on the legacy one
```

Do not silently change a historical contract without compatibility handling.

Document the chosen semantics clearly.

Add tests for:

```text
same source different physical root → same logical snapshot hash
source content change → different logical snapshot hash
```

---

# 8. B1-06 — Evidence size reduction

Gate B added approximately:

```text
175 MB
```

of UI Evidence on IST.

That is functionally valid but should be optimized before H5 if possible without semantic loss.

Measure first.

Identify dominant contributors:

```text
duplicated attributes
repeated CSS rule payloads
repeated strings
embedded asset base64
repeated relationship metadata
```

Preferred strategies:

```text
deduplicate repeated CSS rule bodies
normalize repeated attribute maps
reference shared style/resource records by stable ID
avoid embedding binary/base64 unless actually required by downstream
```

Do not introduce compression formats that make Evidence opaque unless already supported.

Target:

```text
meaningful reduction
with byte-stable deterministic output
and no downstream semantic regression
```

Report before/after size.

Do not chase an arbitrary percentage if the remaining bytes are semantically justified.

---

# 9. B1-07 — Remove dependency cycle

The current inventory reports:

```text
legacy_documenter.behavior.ui_evidence
↔ legacy_documenter.behavior.styles
```

Remove this cycle.

Preferred direction:

```text
evidence/ui_* neutral models
      ↓
behavior/ui_evidence
      ↓
behavior/styles
```

or another acyclic direction consistent with architecture.

Do not solve it with runtime import hacks.

Preserve public behavior.

---

# 10. Tests

Create focused tests, for example:

```text
tests/test_post_v5_gate_b1_evidence_core_closure.py
```

Cover at least:

```text
~/ asset resolves against application root
missing ~/ asset remains unresolved
ambiguous app root remains unresolved
menu/config literal target becomes navigation edge
dynamic menu target remains unresolved
usage-summary parity explanation fixture
same source in two roots → same logical snapshot/provenance
source content change → logical snapshot hash changes
portable outputs do not depend on physical root
Evidence size optimization preserves semantics
UI evidence deterministic after deduplication
behavior.ui_evidence/styles dependency graph acyclic
source removed → downstream still succeeds
```

No real provider calls.

---

# 11. Test execution policy

During implementation:

```text
directed B.1 tests only
```

Then run relevant:

```text
Gate B
Gate A/A.1
H4 behavioral/template
Evidence invariants
adapter tests
```

Then exactly one final full suite on the final tree:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

---

# 12. IST validation

Do not repeatedly reanalyze IST.

If extractor changes require a refreshed UI Evidence baseline:

```text
perform exactly ONE deterministic IST analysis after directed tests are stable
```

Record:

```text
scanner count
analyzer count
duration
UI evidence counts
navigation counts
asset resolution before/after
Evidence size before/after
usage summary
logical snapshot hash
portable evidence hash
```

Then validate downstream from persisted output with source access blocked/instrumented:

```text
behavior
docs
visuals
deliver
interpret replay if applicable
```

Expected:

```text
source_reads = 0
scanner = 0
analyzer = 0
provider = 0
```

---

# 13. Required result report

Create:

```text
docs/POST_V5/PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE_RESULT.md
```

and preferably:

```text
docs/POST_V5/PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE_EVIDENCE.json
```

Report:

```text
asset resolution
menu/config navigation support
usage-summary parity diagnosis
provenance decision
snapshot-hash contract
Evidence-size before/after
dependency-cycle removal
tests
IST validation
remaining debt
```

---

# 14. State

Update:

```text
PROJECT_STATE.json
README.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

Expected state if successful:

```text
PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS
```

Keep:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
H5 = NOT_STARTED
Gate C = NOT_STARTED
```

---

# 15. Remaining work after B.1

After B.1 passes, proceed to Gate C:

```text
DT-04 cross-project BL resolution
DT-07 second human template validation
DT-08 selected remaining product debt
UX-03 decision
```

No new Gate B debt should remain except explicitly accepted low-risk historical compatibility.

---

# 16. Git authority

For Gate B.1:

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

# 17. Success criteria

Gate B.1 passes only if:

```text
supported ~/ assets resolve deterministically
menu/config literal navigation is persisted where supported
usage-summary drift is explained and resolved or explicitly historical-unresolved
portable identity does not depend on physical root
source snapshot hash has honest semantics
UI Evidence size is measured and reduced where safely possible
new UI Evidence dependency cycle is removed
source-offline downstream guarantee remains true
one final full suite passes
H5 remains NOT_STARTED
```

Final principle:

> **Gate B is not complete in product terms until its persisted Evidence is complete enough, portable enough, reproducible enough, and efficient enough to trust as the only downstream source of truth.**
