# LegacyMapper V2-R2 — Web Functional Entry Points

TASK: Implement V2-R2.
BASELINE: V2-R1.1 approved for R2.
DO NOT implement V2-R3.
DO NOT add Oracle/SQL/stored-procedure analysis yet.

## GOAL

Build deterministic Web Forms functional entry-point mapping on top of the approved V2-R1.1 call graph.

Target chain:

WebForm
-> Control/Event
-> Handler
-> Method
-> existing V2-R1.1 Call Graph

R2 must identify where functional execution begins in ASP.NET Web Forms without inventing relationships.

## INPUTS

Reuse existing V1/V2 data/models:

- webforms
- symbols
- projects
- dependencies
- calls
- functional_dependencies
- Evidence/confidence model
- project/source ownership

Do not duplicate existing extraction/resolution logic.

## IMPLEMENT

### R2-01 WebForm -> CodeBehind -> Class

Reuse V1 mappings and produce stable links between:

WebForm
-> CodeBehind
-> VB Class

Preserve:
- source path
- class
- project
- evidence
- confidence

Do not guess unresolved ownership.

### R2-02 Event Handlers

Detect VB.NET handlers including:

`Handles control.Event`

Examples:

`Handles btnBuscar.Click`
`Handles Me.Load`
`Handles MyBase.Load`

Extract:

- control
- event
- handler method
- containing class
- source file
- line/evidence
- project

### R2-03 Handles multiple events

Support:

`Handles btnAceptar.Click, btnGuardar.Click`

Create independent event bindings sharing the same handler.

### R2-04 WebForms lifecycle

Recognize deterministic lifecycle entry points when explicitly wired/overridden, including relevant patterns such as:

- Page_Load
- Page_Init
- Page_PreRender
- OnInit
- OnLoad
- OnPreRender

Do not classify a method as lifecycle solely because its name resembles one unless ASP.NET/VB evidence supports it.

### R2-05 Markup event wiring

Detect explicit event attributes in ASPX/ASCX/Master markup when present, e.g.:

`OnClick="btnBuscar_Click"`
`OnSelectedIndexChanged="..."`
`OnTextChanged="..."`
`OnCommand="..."`

Generalize for `On<Event>` attributes.

Resolve:

WebForm control
-> event
-> handler

Preserve markup evidence.

### R2-06 Control identity

When possible associate event with:

- control ID
- control/tag type
- WebForm
- event name

Do not require full ASP.NET control type resolution.

### R2-07 EntryPoint model

Create/extend model equivalent to:

{
  "id": "...",
  "type": "web_event|web_lifecycle",
  "webform": "...",
  "control": "...",
  "event": "...",
  "handler": "...",
  "class": "...",
  "project": "...",
  "confidence": "confirmed|unresolved",
  "evidence": [...]
}

Use stable deterministic IDs.

Avoid `inferred` unless there is a clearly justified existing confidence rule.

### R2-08 Event bindings

Create structured event-binding representation:

WebForm
-> Event
-> Handler

A binding must not be `confirmed` unless handler/class association is deterministic.

### R2-09 Connect to Call Graph

For resolved handlers, link entry point to the corresponding V2-R1.1 method/call context.

Do NOT recursively construct complete business flows yet.

R2 only establishes:

EntryPoint
-> Handler Method
-> existing outgoing calls

Full flow traversal belongs to V2-R4.

### R2-10 Functional dependencies

Extend functional dependencies with appropriate normalized relations such as:

WebForm -> Event
Event -> Handler
Handler -> Method

Deduplicate logical edges using the V2-R1.1 mechanism.

Preserve evidence_count/evidence_samples where applicable.

## OUTPUT INDEXES

Add:

`output/index/entry_points.json`
`output/index/event_bindings.json`

Extend:

`output/index/functional_dependencies.json`

Do not remove or break V1/V2-R1.1 indexes.

## FALSE-POSITIVE RULES

Must NOT treat as event binding:

- JavaScript inside strings
- commented code
- markup text not representing attributes
- method names merely resembling handlers
- arbitrary `_Click` methods without binding evidence
- controls/events with ambiguous handler resolution

Ambiguous relation -> unresolved.

Never fabricate handler/class/project.

## TESTS

Preserve all existing tests.

Add tests for at least:

T01:
`Handles btnBuscar.Click`

T02:
`Handles Me.Load`

T03:
`Handles MyBase.Load`

T04:
multiple Handles events

T05:
markup `OnClick="btnBuscar_Click"`

T06:
generic markup `On<Event>`

T07:
WebForm -> CodeBehind -> Class -> Handler

T08:
handler with outgoing V2-R1.1 call

T09:
handler name exists but no event binding -> NOT entry point

T10:
ambiguous/missing handler -> unresolved

T11:
JavaScript/string false-positive exclusion

T12:
duplicate event binding deduplication

T13:
lifecycle valid mapping

T14:
lifecycle name without sufficient evidence -> NOT confirmed

## VALIDATION

Run:

`python -m unittest discover -s tests`

Run fixture/internal validation.

Do NOT automatically run the full 14k-file repository.

V1 and V2-R1.1 compatibility must remain intact.

## ACCEPTANCE

PASS only if:

- all previous tests pass;
- new R2 tests pass;
- WebForms event handlers are detected;
- markup events are detected;
- lifecycle entry points are conservatively detected;
- handlers resolve to actual methods when confirmed;
- entry points connect to existing call graph;
- ambiguity remains unresolved;
- no mass false-positive `_Click` inference;
- functional dependencies remain deduplicated;
- evidence/confidence preserved;
- errors in one file do not stop repository scan;
- no LLM dependency introduced.

## REPORT

Create only:

`codex/V2/V2_R2_RESULTADO.md`

Machine-oriented compact format:

STATUS
FILES_CHANGED
TESTS
OUTPUTS
EVENT_PATTERNS_SUPPORTED
RESOLUTION_RULES
CORRECTIONS_OR_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

No ZIP.
No extra reports.

## REAL VALIDATION COMMAND

Recommend:

`python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r2_full" --verbose`

Do not execute automatically unless required for targeted verification.

## STOP CONDITION

After implementation/tests:

STOP.

Expected NEXT:

`V2-R2 ready for full real validation.`
`V2-R3 NOT STARTED.`

Do not implement V2-R3.