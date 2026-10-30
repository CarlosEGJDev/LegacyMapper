# LegacyMapper Post-V5 — H4-R3 Final Verification and Closure
## Final Human Deliverables

### Purpose

H4 implementation is technically complete and validated on IST, but two closure gates remain:

```text
1. final full-suite rerun on the exact final tree
2. final human usability confirmation of the real HTML/PDF package
```

This round is **verification and closure only**.

Do NOT redesign H4.
Do NOT add new product features.
Do NOT start H5.

---

# 1. Read first

Read:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json

docs/POST_V5/H4_FINAL_HUMAN_DELIVERABLES_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md

C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\REVIEW_GUIDE.md
```

Inspect the actual H4 package:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\package\index.html
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\package\deliverables\SYSTEM_OVERVIEW.html
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\package\deliverables\USE_CASES.html
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\package\deliverables\EXTERNAL_INTEGRATIONS.html
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\package\functional\areas\slnPREPrevencion_2010.html

C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\pdf\LegacyMapper_System_Overview.pdf
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\pdf\LegacyMapper_Functional.pdf
```

---

# 2. Known current status

Preserve these facts unless current evidence contradicts them:

```text
H1 = CLOSED
H2 = CLOSED
H3 = CLOSED

H4 implementation = IMPLEMENTED_AND_VALIDATED
H4 human acceptance = PENDING
H5 = NOT_STARTED
```

Current technical evidence from H4-R1:

```text
3254 tests reported
0 failures
0 errors
132 skips

777 HTML
4 PDF
399 SVG
16549 links checked
0 broken links
0 missing fragments
0 missing visual references
provider = 0
scanner = 0
analyzer = 0
baseline delta = 0
```

However:

> The last full-suite run observed one live-inventory snapshot failure, then the snapshot was regenerated and only the directed inventory+H4 tests were rerun.

Therefore a **new complete suite run on the final tree is mandatory** before closure.

---

# 3. Roadmap hygiene correction

Fix stale text in:

```text
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

The section currently describing the main gap must agree with the already-updated backlog.

Required final meaning:

```text
HX-01 = resolved by H2 + H3 + H4, pending H5 human acceptance
HX-02 = resolved by H4
HX-03 = resolved by H3
```

Do not leave contradictory statements such as:

```text
HTML/PDF not productized
structured visuals not implemented
```

if later sections say they are implemented.

Do not change historical V5 facts.

---

# 4. Human package verification

Perform a final manual/visual verification of the actual H4 package.

## 4.1 HTML

Verify at minimum:

```text
index.html opens from local filesystem
no server required
no network dependency required
navigation works
relative links work
audience landing pages are understandable
10 deliverables are reachable
status legend is visible
unresolved content is prominent
main diagrams are readable
summary → detail navigation works
```

Inspect specifically:

```text
SYSTEM_OVERVIEW
USE_CASES
EXTERNAL_INTEGRATIONS
KNOWN_UNRESOLVED_AREAS
functional area slnPREPrevencion_2010
technical project WebPREPrevencion
```

Confirm semantic safety:

```text
USE_CASES does not invent business use cases
FUNCTIONAL_AREAS states area = solution, not business function
MODULE_MAP does not invent business modules
EXTERNAL_INTEGRATIONS does not promote unclassified dependencies
BUSINESS_FLOWS remains observable/evidence-backed where business semantics are unsupported
```

## 4.2 PDF

Open in a real PDF viewer if available.

Verify at minimum:

```text
cover readable
TOC/bookmarks or equivalent navigation usable
headings readable
tables not clipped
diagrams readable
no microscopic full-system graph
no corrupt pages
page numbers present
status labels remain visible
```

Inspect:

```text
LegacyMapper_System_Overview.pdf
LegacyMapper_Functional.pdf
```

If no real viewer is available, do not claim real-viewer verification; record the limitation honestly.

---

# 5. Human acceptance rule

Do NOT self-declare user acceptance.

Two possible outcomes:

### If the human reviewer has explicitly approved the HTML/PDF package

Then H4 may close:

```text
H4 = CLOSED
H4_HUMAN_REVIEW = APPROVED
NEXT = H5_REAL_IST_VALIDATION_AND_CLOSURE
```

### If explicit human approval is still absent

Then finish all technical closure work, but leave:

```text
H4 = READY_FOR_FINAL_HUMAN_CONFIRMATION
```

and do not mark H4 closed.

The final report must make the distinction explicit.

---

# 6. Full-suite final rerun

After all code/docs/state corrections are complete, run exactly:

```text
python -X utf8 -m unittest discover -s tests
```

This must be the **last test-changing step**.

Require:

```text
0 failures
0 errors
```

Record:

```text
total
failures
errors
skips
duration
exit code
```

If anything is modified after the run that could affect tests or snapshots, rerun the full suite again.

---

# 7. Final IST package verification

Do NOT reanalyze source.

Reuse the persisted IST baseline and existing H4 output.

Verify:

```text
baseline deterministic delta = 0
provider calls = 0
scanner invocations = 0
analyzer invocations = 0
broken links = 0
missing fragments = 0
missing visual references = 0
```

If the package must be regenerated because docs/templates changed, regenerate only from the persisted baseline.

Then verify byte determinism again.

---

# 8. State synchronization

Update:

```text
PROJECT_STATE.json
docs/POST_V5/H4_FINAL_HUMAN_DELIVERABLES_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

If technical closure is clean but human approval is not explicit:

```text
round_status = H4_READY_FOR_FINAL_HUMAN_REVIEW
h4_final_human_deliverables = IMPLEMENTED_AND_VALIDATED
h4_human_review = READY_FOR_FINAL_HUMAN_CONFIRMATION
next = H5_REAL_IST_VALIDATION_AND_CLOSURE
```

If explicit human approval is available:

```text
round_status = H4_CLOSED
h4_final_human_deliverables = CLOSED
h4_human_review = APPROVED
h4_human_acceptance = APPROVED_BY_HUMAN_REVIEW
next = H5_REAL_IST_VALIDATION_AND_CLOSURE
```

Do not change:

```text
current_version = POST_V5
v6_started = false
```

Do not start H5.

---

# 9. Result document update

Append a section to:

```text
docs/POST_V5/H4_FINAL_HUMAN_DELIVERABLES_RESULT.md
```

named:

```text
H4-R3 Final Verification and Closure
```

Include:

```text
roadmap hygiene corrections
HTML manual verification
PDF manual verification
semantic safety checks
final full-suite run
IST/baseline verification
determinism verification
human acceptance status
Git status
final recommendation
```

Final state must be exactly one of:

```text
H4_CLOSED
H4_READY_FOR_FINAL_HUMAN_REVIEW
H4_CLOSURE_CORRECTION_REQUIRED
H4_CLOSURE_BLOCKED
```

---

# 10. Git authority

For this H4-R3 verification round:

```text
edit production code = NO, unless a genuine closure defect is found
edit tests = NO, unless a genuine closure defect is found
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

If a real defect requires product/test changes, keep it narrowly scoped and rerun the full suite afterward.

Do not version anything unless the human explicitly authorizes it separately.

---

# 11. Non-goals

Do not implement:

```text
new H4 features
new diagram kinds
new semantic inference
H5 validation
new provider
Evidence changes
adapter changes
Plugin Runtime
V6
```

---

# 12. Success criterion

This round succeeds when:

```text
roadmap and state are internally consistent
the real HTML package is usable offline
the real PDF is readable
semantic safety remains intact
the final exact tree passes the full suite
IST baseline remains unchanged
provider/scanner/analyzer remain unused
human acceptance status is represented truthfully
```

If human approval is still pending, stop at:

```text
H4_READY_FOR_FINAL_HUMAN_REVIEW
```

If human approval is explicit and all gates pass, close H4 and leave:

```text
NEXT = H5_REAL_IST_VALIDATION_AND_CLOSURE
```
