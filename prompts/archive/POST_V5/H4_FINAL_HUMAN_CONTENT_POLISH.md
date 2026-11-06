# LegacyMapper Post-V5 — H4 Final Human Content Polish

## Objective

Apply one final **human-documentation content polish** before formally closing H4.

This is **not** a new architecture round.
This is **not** H4-R6.
Do not reopen Evidence Core, Gate A/B/C, or deterministic analysis.
Do not start H5.
Do not start V6.

The goal is to improve the **human experience** of the existing documentation so that it is:

```text
simple
concise
explanatory
focused on what was actually found
useful for nontechnical, functional, and technical readers
```

The documentation must explain the system, not expose the internal mechanics of LegacyMapper.

---

# 1. Current state

Treat the following as already approved/validated technically:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS
PRE_H5_GATE_C_FINAL_HARDENING = PASS
PRE_H5_BLOCKING_DEBT = 0
```

The real H4 manual validation also completed successfully:

```text
real IST deterministic analysis = SUCCESS
real Copilot interpretation = SUCCESS
human/default = SUCCESS
human/executive = SUCCESS
```

The human owner approves the **direction and technical correctness**, but requests one final content-quality correction before formal H4 closure.

H4 must remain:

```text
HUMAN_APPROVAL_PENDING_FINAL_CONTENT_POLISH
```

until the owner reviews the regenerated human documents.

H5 remains:

```text
NOT_STARTED
```

---

# 2. Critical product rule

Use this as the main rule for all human-facing output:

> **Human documentation must explain what the system does and how it does it. It must not be dominated by counts, analysis metrics, unresolved findings, internal Evidence diagnostics, or AI validation mechanics.**

Another rule:

> **Focus first on information LegacyMapper actually found, confirmed, or can safely infer. Unknown or unresolved information must remain preserved, but it belongs mainly in a dedicated uncertainty section instead of being repeated throughout the narrative.**

And:

> **Less information, but higher-value information.**

---

# 3. AI interpretation style

The AI interpretation must be:

```text
simple
concise
clear
explanatory
human-oriented
```

Do not make the AI sound like an analyzer report.

Bad style:

```text
The view has 17 calls, 8 unresolved references, 5 incoming invocations,
31 facts, 12 controls and 4 data interactions.
```

Preferred style:

```text
This view allows the user to search for a work center.
When it opens, it loads the available communes.
Other screens use it as a selection window.
```

For technical documentation:

```text
View: ucBusSuc
Load:
Page_Load
→ PrePrevencion.txcargacombocomunas
→ PrePrevencion.cargacombocomunas
→ PPRE_CONSULTAS.CARGACOMBOCOMUNAS

Search:
btnBuscar.Click
→ btnBuscar_Click
→ next destination indeterminate
```

The AI must talk about **behavior, purpose, relations, routes and data**, not about LegacyMapper's internal statistics.

---

# 4. Remove low-value numerical noise

Do not surface counts unless the number itself helps a human understand scope.

Allowed:

```text
Project WebCob
48 views
```

only if followed by the actual view list.

Allowed:

```text
Solution X contains 4 projects:
- ProjectA
- ProjectB
- ProjectC
- ProjectD
```

Not useful:

```text
26 incoming calls
53 facts
21 controls
11 rejected claims
7 unresolved calls
15 evidence references
```

Those may remain in internal JSON/evidence/debug artifacts, but not in the primary human narrative.

Rule:

> **Never replace useful names and relationships with counts.**

Bad:

```text
This view is opened by 26 other views.
```

Better:

```text
This view is opened by:
- ucPreAsigSucursal
- ucPreBiblioCentroTrabajo
- ucPreConsultaPago
- ...
```

If the list is very long:

```text
show the important/representative names in the main section
put the full list in an appendix or expandable HTML section
```

---

# 5. Human document information architecture

Human documentation should be centered on:

```text
Solution
→ Projects
→ Modules / functional areas when safely known
→ Views / screens
→ What each view does
→ What each action does
→ What other views it opens / what opens it
→ Technical execution route
→ Data / procedures / external systems
→ Uncertainties grouped separately
```

Recommended project structure:

```text
1. Project overview
2. Known purpose / inferred role
3. Modules or functional areas
4. Views
5. Main functional flows
6. Relations between views
7. Data and persistence
8. Technical routes
9. Known uncertainties
10. Technical appendix
```

---

# 6. View documentation

Each relevant view should prioritize:

```text
View name
Visible title
Simple explanation of what it does
Main actions
Relations to other views
Data it reads/writes if known
Technical route
```

Example:

```text
View: ucPreMantJerarquia2
Title: Mantención de Jerarquías

What it does
Allows consulting and maintaining hierarchical relationships.

Actions

Search
→ hypBuscar_Click
→ Lee_Datos()
→ next destination indeterminate

Assign
→ hypAsignar_Click
→ PreGesJerarquia.txcrear
→ sysPreGesJerarquia.crear
→ PPRE_GES_JERARQUIA.CREAR

Unassign
→ hypDesasociar_Click
→ PreGesJerarquia.txeliminar
→ sysPreGesJerarquia.eliminar
→ PPRE_GES_JERARQUIA.ELIMINAR
```

This is much more useful than showing call counts.

---

# 7. Technical documentation

Technical documentation must be genuinely technical, but still understandable.

Primary technical pattern:

```text
View
→ UI event
→ handler
→ business method
→ cross-project class/method
→ DAO/repository/data method
→ Stored Procedure / SQL
→ Database / external boundary
```

Use actual names.

Example:

```text
ucPreMantJerarquia2
→ hypAsignar.Click
→ hypAsignar_Click
→ PreGesJerarquia.txcrear
→ sysPreGesJerarquia.crear
→ PPRE_GES_JERARQUIA.CREAR
```

If one step is unknown:

```text
→ indeterminate
```

Do not write paragraphs repeatedly explaining why LegacyMapper could not resolve it.

---

# 8. Unknown / unresolved information

Preserve all uncertainty in the semantic model.

However, human-facing output must not repeatedly say:

```text
not resolved
unknown
not determined
not found
cannot be inferred
```

throughout every paragraph.

Instead, aggregate uncertainty.

Example:

```text
Known uncertainties — WebCob

- The purpose of 6 views could not be determined.
- 3 actions have an indeterminate downstream destination.
- 2 external assemblies are referenced but their implementation is unavailable.
```

For an individual view, only mention uncertainty when it materially changes understanding.

Example:

```text
Search
→ btnBuscar_Click
→ next data destination indeterminate
```

That is enough.

Do not turn absence of evidence into the main story.

---

# 9. Audience-specific output

The three human levels must become clearly different.

## Executive

Should answer:

```text
What is this system?
What projects/modules exist?
What business/functional areas are visible?
What main capabilities are known?
What important dependencies/data systems exist?
```

No methods, class names, hashes, call counts, Evidence IDs or validation diagnostics.

## Functional

Should answer:

```text
What does each module/project do?
What screens exist?
What does each screen allow the user to do?
How do screens relate to each other?
What major flows are visible?
What data is consulted or maintained?
```

Minimal technical names only when they help explain functionality.

## Technical

Should answer:

```text
What views exist?
What event/handler executes?
What methods/classes/projects are crossed?
What procedure/SQL is reached?
What external boundary remains?
What views open other views?
```

Use actual symbols and names, not internal metrics.

---

# 10. Evidence / AI internal data separation

Keep these artifacts internally:

```text
Evidence IDs
accepted/rejected claim counts
candidate counts
raw AI validation diagnostics
hashes
request IDs
provider metrics
analysis coverage metrics
call counts
fact counts
control counts
```

They may exist in:

```text
JSON
manifests
debug artifacts
AI internal outputs
appendices if explicitly technical
```

but they must not dominate the primary human documentation.

Human documentation is not an analyzer dashboard.

---

# 11. Human domain knowledge

Prepare the human-documentation layer to support **explicit human-confirmed domain knowledge**.

Examples:

```text
COB = Cobranza
WebCob = web project for the Cobranza domain
Mantencion = maintenance functions
Morosidad = debt / delinquency-related functions
```

Do not automatically infer these as facts from names alone.

The design must allow a human to provide these mappings later and have them appear in human documentation with an explicit trusted status.

Preferred existing authority:

```text
CANONICAL
```

if the current canonical/review mechanism fits.

Otherwise introduce only a minimal compatible concept such as:

```text
HUMAN_CONFIRMED_DOMAIN_KNOWLEDGE
```

Do not create a parallel truth system unnecessarily.

For this round:

```text
design/support the mechanism if required
do not invent domain mappings
do not populate COB/Mantencion/Morosidad unless explicitly provided by the owner
```

---

# 12. Modules and functional areas

Do not manufacture modules from naming similarity alone.

Module states remain:

```text
MODULE_STRUCTURE_CONFIRMED
MODULE_STRUCTURE_INFERRED
NO_SAFE_MODULE_STRUCTURE
```

However:

- human-confirmed domain knowledge may later enrich names and grouping;
- inferred module/group names must be visibly distinguished from confirmed ones;
- a project with no safe module structure should still present its views cleanly without repeating that limitation constantly.

Example:

```text
Project WebCob

Views
- ucCobMantencionClientes
- ucCobMorosidad
- ucCobConsultaDeuda
...
```

If later human knowledge confirms groups:

```text
Cobranza
  Mantención
  Morosidad
```

the document can organize accordingly.

---

# 13. Tables, diagrams and visual resources

Keep and improve the current strengths:

```text
tables
box flows
wireframes
view relationships
SVG diagrams
HTML navigation
PDF
```

The owner explicitly likes these.

Use visuals to reduce text.

Prefer:

```text
simple table
small diagram
short explanation
```

over long prose.

Example:

| Action | Route |
|---|---|
| Assign | `hypAsignar_Click → PreGesJerarquia.txcrear → sysPreGesJerarquia.crear → PPRE_GES_JERARQUIA.CREAR` |
| Unassign | `hypDesasociar_Click → PreGesJerarquia.txeliminar → sysPreGesJerarquia.eliminar → PPRE_GES_JERARQUIA.ELIMINAR` |

---

# 14. Do not rerun analysis

For this correction:

```text
DO NOT run scanner
DO NOT run analyzer
DO NOT regenerate Evidence
DO NOT rebuild the IST baseline
DO NOT modify deterministic Evidence semantics
```

Use the existing persisted analyzer-v4 baseline from the successful manual validation.

---

# 15. Do not call AI again unless absolutely necessary

The current H4 validation already has persisted AI responses using:

```text
provider_id = copilot-local
model_id = gpt-6-luna
```

Reuse:

```text
ai_raw_responses.json
explanations.json
AI_INTERPRETATION_MANIFEST.json
```

Prefer deterministic transformation / presentation-layer changes.

Do not call Copilot again simply to shorten wording.

If the current structured AI output does not contain enough semantic information to produce the new human narrative, stop and report exactly which missing semantic field requires a new AI interpretation before making provider calls.

No silent provider calls.

---

# 16. Focus files

Likely affected areas:

```text
legacy_documenter/behavior/explain.py
legacy_documenter/behavior/render.py
legacy_documenter/behavior/template.py
legacy_documenter/templates/human/default/
legacy_documenter/templates/human/executive/
documentation human projection/rendering code
```

Touch only what is required.

Do not refactor unrelated large modules.

---

# 17. Required regression examples

Regenerate the same five H4 representative views from persisted responses:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

The resulting human documentation must prove:

```text
less numerical noise
fewer repeated unresolved statements
more direct behavior explanation
actual view names
actual relation names
actual technical route names
uncertainty grouped
same Evidence truth
same AI provenance
no source read
no provider call
```

---

# 18. Human review package

Generate a new comparison package:

```text
<review_root>\before\
<review_root>\after\
```

or equivalent.

Include:

```text
default HTML
default PDF
executive HTML
executive PDF
five representative view sections
validation summary
short before/after content comparison
```

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_CONTENT_POLISH_RESULT.md
```

Report:

```text
what changed
what was removed from human narrative
what remained internal
how unresolved content is now grouped
how audience differences changed
whether AI was called
whether source was read
tests run
human review location
```

---

# 19. Tests

Create/update targeted tests covering:

```text
counts not shown as primary narrative
view names shown instead of only counts
relations name actual source/target views
technical routes use actual symbols
unresolved grouped
no repeated unresolved boilerplate
executive excludes technical internals
functional explains behavior simply
technical keeps useful routes
Evidence/AI diagnostics remain available internally
no provider call
no source read
templates preserve semantic truth
```

During development:

```text
targeted tests only
```

At the end, after stable:

```text
python -X utf8 -m unittest discover -s tests
```

Run the full suite exactly once.

Do not rerun IST analysis.

---

# 20. Success criteria

This round passes only if:

```text
1. A normal reader can understand what the project does without analyzer jargon.
2. A functional reader can understand screens and flows without source code.
3. A technical reader gets concrete execution routes with real names.
4. Counts are used only when they add real scope/context.
5. Names and relationships are preferred over counts.
6. Unknown information is preserved but grouped instead of repeated.
7. AI interpretation is concise and explanatory.
8. The document focuses on known/confirmed/inferred behavior.
9. Visuals remain strong and useful.
10. No new scanner/analyzer run occurs.
11. No provider call occurs unless explicitly justified and approved.
12. Existing Evidence truth and provenance remain unchanged.
```

---

# 21. State after this round

If technically successful:

```text
H4_FINAL_HUMAN_CONTENT_POLISH = READY_FOR_HUMAN_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not mark H4 CLOSED yet.

The owner will inspect the regenerated human documentation.

Only after explicit owner approval may a separate closure action set:

```text
H4 = CLOSED
```

---

# 22. Git authority

For this round:

```text
production edits = YES
tests = YES
docs/state draft updates = YES
commit = NO
push = NO
tag = NO
```

Do not perform Git commit/push/tag without explicit human authorization.

---

# Final principle

> **LegacyMapper's human documentation should explain the system, not explain LegacyMapper's uncertainty.**

And:

> **Known behavior first. Useful names and relationships first. Technical routes when needed. Uncertainty grouped. Internal metrics stay internal.**
