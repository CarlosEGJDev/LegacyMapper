# LegacyMapper Post-V5 — H4-R4 Behavioral Documentation Prototype
## Macro-to-Micro Human Understanding Pilot

### Why this round exists

H4 technically produced valid HTML/PDF packaging, but human review revealed a product-level mismatch:

> The deliverables mostly reorganize existing technical documentation instead of explaining how the software actually works.

This is a justified exceptional H4 correction round.

It does **not** reopen H1-H3 architecture.
It does **not** start H5.
It does **not** generalize a new framework before validating the human-documentation concept on real IST.

Permanent principle for this round:

> **The AI explains behavior; it does not merely summarize files.**

Secondary principle:

> **Macro first, micro later.**

---

# 1. Objective

Build and validate a **behavioral human-documentation prototype** on a real IST slice.

Target:

```text
Solution
→ Project
→ Module (only if supported by evidence)
→ Views / screens
→ What each view does
→ How the user/system reaches it
→ What actions it supports
→ Which classes participate
→ What technical path each action follows
→ What data is read/written
→ What other views/popups/messages are invoked
→ What remains unresolved
```

The central unit of behavioral explanation is:

```text
VIEW / SCREEN
```

A module is used only if the project genuinely contains a module concept that can be supported by evidence.

Do not invent modules.

---

# 2. Real pilot target

Use:

```text
Solution:
slnPREPrevencion_2010

Project:
WebPREPrevencion
```

Select **3–5 representative views** covering different behavior where possible:

```text
one ordinary page
one page with data persistence
one page with significant business/service logic
one popup/modal/message-style view if present
one view with unresolved/complex flow if useful
```

Do not choose views only because they are easy.

The goal is to test whether LegacyMapper can explain a real project in a useful way.

---

# 3. First task: determine whether "module" exists

Before producing documentation, inspect the persisted deterministic knowledge and source structure already represented by LegacyMapper.

Determine whether `WebPREPrevencion` has a meaningful module concept.

Possible evidence:

```text
folders
namespaces
subprojects
consistent prefixes/suffixes
view groupings
business/service/data groupings
repeated structural boundaries
explicit project/module metadata
navigation groupings
master pages / menus
route/menu structure
```

Classify the result:

```text
MODULE_STRUCTURE_CONFIRMED
MODULE_STRUCTURE_INFERRED
NO_SAFE_MODULE_STRUCTURE
```

Rules:

```text
CONFIRMED
→ explicit structural evidence

INFERRED
→ repeated structural pattern, clearly labeled

NO_SAFE_MODULE_STRUCTURE
→ skip module level entirely
```

Do not create business modules just because a group of files looks related.

If no safe module exists, document:

```text
Solution → Project → Views
```

directly.

---

# 4. Behavioral interpretation concept

The AI interpretation layer must answer:

```text
What does this view appear to do?
How does a user/system arrive here?
What does it receive?
What does it display?
What actions can occur?
What does each important action trigger?
Which classes/methods participate?
Which data objects/procedures/services are reached?
What does this view open/invoke?
Who opens/invokes this view?
What messages/popups can appear?
What is confirmed?
What is inferred?
What remains unresolved?
```

The AI must convert technical evidence into a progressive human explanation.

It must **not**:

```text
list files without explanation
lead with artifact counts
invent business purpose
invent actors
invent use cases
invent module boundaries
invent external systems
upgrade inferred evidence to confirmed
```

---

# 5. Required documentation hierarchy

Prototype one document/package with this reading order:

```text
1. Solution overview
2. Project overview
3. Module structure, only if supported
4. View catalog
5. Detailed view explanations
6. Technical behavioral flows
7. Data/persistence paths
8. Cross-view invocation map
9. Unresolved areas
10. Technical appendix
```

The reader must be able to stop at any level.

A non-technical reader should understand sections 1–5.

A functional reader should understand through sections 5–8.

A technical reader can continue into full detail.

---

# 6. Solution-level explanation

For:

```text
slnPREPrevencion_2010
```

Explain in plain language:

```text
what projects it contains
how those projects relate structurally
what can be safely said about its purpose
what cannot be safely inferred
where WebPREPrevencion fits
```

Avoid opening with large counts.

Counts may appear in a compact facts box only when useful.

---

# 7. Project-level explanation

For:

```text
WebPREPrevencion
```

Produce:

```text
Project summary
Role inside the solution
Main structural areas
Views/screens found
Main dependencies
Observable data interaction patterns
Main unresolved boundaries
```

The first paragraph must explain the project in human terms, not as an inventory.

If purpose is not confirmed, use wording such as:

```text
"The observable evidence indicates..."
"The project appears to participate in..."
"The exact business purpose is unresolved."
```

---

# 8. View catalog

Create a readable view catalog.

For each view include at least:

```text
View name
View type
Module/group if safe
Simple purpose
How it is reached
Main actions
Reads data?
Writes data?
Opens another view/popup?
Invoked by other views?
Status of interpretation
```

The catalog is navigation, not the full explanation.

---

# 9. Detailed view document

For each selected pilot view produce the following structure.

## A. What this view does

One concise human explanation.

Example style:

```text
This screen allows the user to consult and modify ...
When opened it loads ...
The main actions available are ...
```

Only state what evidence supports.

## B. How the user/system reaches it

Show:

```text
origin view(s)
menu/navigation if known
popup/modal invocation if relevant
direct calls or redirects if detected
```

## C. Approximate visual reconstruction

If enough UI evidence exists, create a deterministic documentary wireframe.

Possible sources:

```text
.aspx markup
HTML controls
ASP.NET controls
labels
textboxes
dropdowns
buttons
grids
validators
panels
tabs
modal/popup controls
master/content regions
```

The wireframe must be labeled:

```text
DOCUMENTARY RECONSTRUCTION
NOT A SCREENSHOT
```

Do not invent controls not present in evidence.

If reconstruction is unsafe:

```text
WIRE_FRAME_UNAVAILABLE_FROM_CURRENT_EVIDENCE
```

## D. Main actions

For each important action:

```text
Action
Trigger/control
Handler/event
Simple explanation
Technical path
Data impact
Result/navigation
Status
```

## E. Technical behavioral path

Show the full evidence-backed route when available:

```text
View
→ event
→ code-behind/controller
→ business/service
→ helper/domain class
→ DAO/repository
→ stored procedure/SQL/service
→ database/external boundary
```

Not every project uses every layer.

Do not force a standard architecture onto the evidence.

## F. Data behavior

Explain:

```text
what data is received
what data is loaded
what data is transformed
what is persisted
what is returned
```

Use plain language first, technical names second.

## G. Related classes

Group related classes by observed role:

```text
UI/code-behind
controller
business
service
domain/model
helper
data access
other
```

Only use a role if supported.

If role is inferred, label it.

## H. Incoming invocations

Explain which pages/components invoke this view.

Especially important for:

```text
popups
modals
message windows
search dialogs
selection dialogs
```

## I. Outgoing invocations

Explain what this view opens/calls.

## J. Messages / popups

When evidence permits, document:

```text
message/popup
condition
source event
destination/behavior
```

Do not fabricate visible message text.

## K. Unresolved

Always include:

```text
What we know
What we infer
What remains unresolved
```

---

# 10. Cross-view understanding

Create a small project navigation/interaction explanation:

```text
View A
→ opens View B
→ invokes Popup C
→ returns to View A
```

and/or:

```text
View A
→ Business X
→ DAO Y
→ Procedure Z
```

The goal is to let a human understand how the project behaves without browsing code.

Do not generate a giant graph.

Prefer small focused diagrams.

---

# 11. AI interpretation contract

This round must explicitly define the contract between deterministic evidence and AI interpretation.

Required conceptual contract:

```text
Deterministic evidence
→ Behavioral context package
→ AI interpretation
→ Structured Human Explanation
→ deterministic validation
→ human-facing rendering
```

The AI output should be structured, not free-form-only.

Prototype a schema/model for at least:

```text
SolutionExplanation
ProjectExplanation
ModuleExplanation
ViewExplanation
ActionExplanation
BehaviorPath
DataInteractionExplanation
ViewInvocation
UIReconstruction
UnresolvedExplanation
```

Each important statement should support:

```text
status
source_refs
confidence/reason
```

Statuses remain:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

Do not auto-promote AI interpretation.

---

# 12. Deterministic validation of AI output

Python must validate AI-produced structured explanations.

Reject or downgrade unsupported claims.

At minimum validate:

```text
referenced project exists
referenced view exists
referenced event/method/class exists
referenced procedure/data object exists
source_refs resolve
CONFIRMED claims have deterministic support
INFERRED claims identify the inference basis
UNRESOLVED remains unresolved
AI_INTERPRETATION is visibly distinct
```

The AI may synthesize an explanation.

It may not invent relationships absent from evidence.

---

# 13. Prototype output

Create a prototype human artifact for the selected IST slice.

Primary:

```text
HTML
```

Secondary:

```text
PDF
```

Suggested title:

```text
Understanding WebPREPrevencion
```

Recommended structure:

```text
Cover
How to read this document
Solution
Project
Module structure / no-safe-module explanation
View catalog
3–5 detailed view chapters
Cross-view behavior
Data/persistence overview
Known unresolved areas
Technical appendix
```

The PDF should read like a system walkthrough, not an inventory report.

---

# 14. Human readability rules

Do not lead with counts.

Prefer:

```text
"This screen..."
"When the user..."
"After this action..."
"The request then passes to..."
"The data is finally..."
```

over:

```text
"27 events"
"14 procedures"
"42 methods"
```

Counts may appear later as supporting facts.

Use progressive disclosure:

```text
simple explanation
→ behavioral explanation
→ technical flow
→ raw technical references
```

---

# 15. Visual reconstruction rules

A reconstructed view is documentary, not a pixel-perfect reproduction.

Must show only controls supported by evidence.

Preserve:

```text
relative grouping where discoverable
labels
control types
important actions
tables/grids
tabs/panels
popup/modal identity
```

It is acceptable to omit styling.

Never claim:

```text
"This is exactly how the production UI looks"
```

Instead:

```text
"Approximate documentary reconstruction from persisted UI evidence"
```

---

# 16. Measure before implementing broadly

Before creating any generic production framework, inspect the real pilot.

Record:

```text
number of views in WebPREPrevencion
candidate modules/groups
how many views can be connected to code-behind/controller
how many reach business/service classes
how many reach DAO/repository
how many reach stored procedures/SQL
how many have incoming view invocations
how many have outgoing view invocations
how many can support documentary wireframes
how many remain structurally unresolved
```

These measurements are for design decisions.

They should not dominate the human document.

---

# 17. Scope

Allowed:

```text
analysis of existing persisted baseline
small exploratory/prototype code
structured behavioral model prototype
AI-context shaping
deterministic validators
prototype HTML/PDF
wireframe prototype
tests for prototype contracts
documentation/state updates
```

Do not broadly refactor H2/H3/H4 yet.

Do not generate documentation for all IST in this round.

---

# 18. Tests

Add focused tests for prototype behavior:

```text
module not invented
view exists
class/method refs resolve
behavior path refs resolve
confirmed claim requires support
inferred claim remains inferred
unresolved preserved
wireframe contains only evidenced controls
popup/view invocation traceability
same structured explanation → deterministic rendering
AI output validation rejects fabricated refs
```

Run directed tests.

If production code is changed, run full suite:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

---

# 19. Human review package

Create:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h4_behavioral_doc_prototype\
```

Include:

```text
HTML prototype
PDF prototype
structured explanation JSON
wireframe assets/models
REVIEW_GUIDE.md
```

Review questions:

```text
1. Can I understand what WebPREPrevencion does without opening code?
2. Is the hierarchy from solution → project → module/view natural?
3. If modules are shown, are they genuinely supported?
4. For each selected view, do I understand what it does?
5. Can I follow an important action from the screen to data/persistence?
6. Can I see who invokes a popup/view and what it invokes?
7. Does the wireframe help me recognize the screen structure?
8. Is the explanation simple first and technical later?
9. Are unsupported business meanings clearly avoided?
10. Is this substantially more useful than the current Markdown/PDF inventory?
```

---

# 20. Result document

Create:

```text
docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md
```

Include:

```text
empirical project/module findings
selected views
behavior reconstruction coverage
AI interpretation contract
structured model
validation rules
wireframe approach
prototype outputs
tests
human review package
limitations
recommendation for productization
```

Final state exactly one of:

```text
H4_BEHAVIORAL_PROTOTYPE_READY_FOR_HUMAN_REVIEW
H4_BEHAVIORAL_PROTOTYPE_NEEDS_CORRECTION
H4_BEHAVIORAL_PROTOTYPE_BLOCKED
H4_BEHAVIORAL_MODEL_NOT_SUPPORTED_BY_CURRENT_EVIDENCE
```

Do not mark H4 globally CLOSED from this round.

Human review decides whether this becomes the generalized H4 documentation model.

---

# 21. PROJECT_STATE / roadmap

Record clearly:

```text
H4 packaging implementation = technically validated
H4 human-documentation concept = reopened by human review
H4 behavioral prototype = in progress / result
H5 = NOT_STARTED
```

Do not claim Post-V5 closure.

Do not call this V6.

---

# 22. Git authority

For this prototype round:

```text
edit exploratory/production code = YES, narrowly
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

No versioning without explicit human authorization.

---

# 23. Success criterion

This round succeeds if the prototype demonstrates that LegacyMapper can explain a real IST project like this:

```text
Solution
→ Project
→ real Module if supported
→ View
→ what it does
→ how it is reached
→ what the user can do
→ what classes participate
→ what process each action follows
→ what data is touched
→ what other views/popups are involved
→ what remains unresolved
```

and a human reviewer can say:

> "Yes. This explains how the project works, instead of only describing what files exist."
