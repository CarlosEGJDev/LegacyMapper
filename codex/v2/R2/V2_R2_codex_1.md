TASK: Validate LegacyMapper V2-R2 on full real repository.
DO NOT modify code.
DO NOT start V2-R3.

INPUT:
- output/v2_r2_full/
- output/v2_r1_1_full/
- codex/V2/V2_R2_RESULTADO.md
- codex/V2/V2_R1_1_VALIDACION_REAL.md

PRIMARY:
- output/v2_r2_full/index/entry_points.json
- output/v2_r2_full/index/event_bindings.json
- output/v2_r2_full/index/functional_dependencies.json
- output/v2_r2_full/index/calls.json
- output/v2_r2_full/index/webforms.json
- output/v2_r2_full/index/errors.json

GOAL:
Determine whether WebForms functional entry points are accurate enough to authorize V2-R3.
Validate precision, coverage, handler resolution, call-graph linkage and regressions.

CHECK:

1. METRICS
Report:
- total entry_points
- confirmed/unresolved
- by type: web_event/web_lifecycle
- total event_bindings
- confirmed/unresolved
- bindings from VB Handles
- bindings from markup On<Event>
- lifecycle bindings
- unique WebForms with entry points
- unique controls
- unique handlers
- handlers with outgoing_calls
- WebForm -> Event edges
- Event -> Handler edges
- Handler -> Method edges
- duplicate logical edges
- errors

2. COVERAGE
Compare against:
- total WebForms
- WebForms with CodeBehind
- WebForms/classes containing detectable Handles
- markup containing On<Event>

Explain major coverage gaps only.
Do not treat absence of events as failure by itself.

3. CONFIRMED SAMPLE
Sample >=25 confirmed entry points, prioritizing:
- button Click
- Page/Control Load
- Init/PreRender
- markup On<Event>
- multiple Handles
- different projects/modules

For each verify:
WebForm
-> CodeBehind
-> class
-> event/control
-> handler method

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Report observed precision estimate.

4. CALL GRAPH CONNECTION
Sample >=15 confirmed handlers with outgoing_calls.

Verify:
EntryPoint
-> Handler
-> V2-R1.1 outgoing call(s)

Prioritize examples where possible:
WebForm -> Handler -> BL
WebForm -> Handler -> cross-project target

Do NOT recursively build full flows.

5. FALSE POSITIVES
Actively search for:
- arbitrary *_Click methods without binding
- JavaScript mistaken as event
- comments mistaken as bindings
- markup text mistaken as attributes
- lifecycle methods confirmed only by name
- duplicated event bindings
- handler resolved to wrong class/WebForm
- malformed On<Event> interpretation

Quantify findings.

6. FALSE NEGATIVES
Search representative cases for:
- Handles control.Event
- Handles Me.Load
- Handles MyBase.Load
- multiple Handles
- markup OnClick
- other markup On<Event>
- Overrides OnInit/OnLoad/OnPreRender

Report missed patterns/examples.

Do not require AddHandler support; it is an accepted R2 limitation.

7. UNRESOLVED
Group unresolved causes.
Determine whether they represent healthy conservatism or a material resolution defect.

8. REGRESSION
Verify V2-R1.1 remains healthy:
- calls totals/confidence broadly consistent with R1.1
- confirmed call resolution not materially reduced
- functional dependency dedup remains effective
- no new parser/runtime errors

9. SANITY
Identify anomalous:
- handlers linked to many unrelated WebForms
- events with excessive handler counts
- WebForms with implausibly high entry-point counts
- repeated identical bindings
- lifecycle explosion
- unexpected global hotspot

10. DECISION
Return exactly one:

A) V2-R2_APROBADA_PARA_R3
B) V2-R2_REQUIERE_CORRECCIONES
C) V2-R2_NO_CONFIABLE

If B/C:
REQUIRED_FIXES grouped:
CRITICAL
HIGH
MEDIUM
LOW

Only CRITICAL/HIGH should block R3 unless report demonstrates otherwise.

DO NOT implement fixes.

OUTPUT:
codex/V2/V2_R2_VALIDACION_REAL.md

FORMAT:
Machine-oriented compact only:

STATUS
METRICS
COVERAGE
CONFIRMED_SAMPLE
CALL_GRAPH_CONNECTION
FALSE_POSITIVES
FALSE_NEGATIVES
UNRESOLVED
REGRESSION
SANITY
REQUIRED_FIXES
DECISION

No ZIP.
No extra reports.
No code changes.
V2-R3 NOT STARTED.