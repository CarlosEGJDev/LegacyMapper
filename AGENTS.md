# LegacyMapper — Development Agent Instructions

## Autonomy

Work autonomously inside this repository.

Do not ask for confirmation for routine development operations required to complete the assigned task.

You are authorized to:

* Read repository files.
* Search repository contents.
* Create files required by the current task.
* Modify LegacyMapper source code required by the current task.
* Modify/add automated tests.
* Create/update files under `codex/`.
* Create/update generated files under `output/`.
* Run local Python commands required for development.
* Run unit tests.
* Run fixture tests.
* Run internal LegacyMapper validation.
* Inspect generated JSON/Markdown outputs.
* Delete/recreate generated `output/` directories when required for testing.

Do not ask permission before each file modification, test execution, search, or normal local validation.

Batch related operations when possible.

## Permission Boundary

Ask before actions that:

* Install software or packages.
* Modify operating-system configuration.
* Modify files outside the LegacyMapper repository, except reading the configured legacy source repository.
* Delete or modify legacy source files.
* Execute destructive commands outside generated LegacyMapper outputs.
* Access credentials or external/private services not already configured.
* Perform Git push, publish, deployment, or other external side effects.

## Legacy Source Repository

Current legacy repository:

`C:\Users\cgalianj\source\IST_40\operacional`

Legacy source is READ-ONLY.

LegacyMapper may:

* scan it;
* read files;
* search files;
* analyze files.

LegacyMapper must NEVER:

* modify it;
* rename files;
* delete files;
* generate files inside it.

## Project Rules

LegacyMapper principle:

`Python discovers and resolves facts. AI interprets later.`

Prefer deterministic analysis.

Do not introduce LLM dependencies unless explicitly requested.

Do not fabricate relationships.

Preserve:

* confirmed
* inferred
* unresolved

Never promote unresolved evidence to confirmed without deterministic evidence.

## Phase Control

Follow the currently assigned V2 phase/round exactly.

Do not automatically start the next round.

Current progression:

V1 -> CLOSED
V2-R1.1 -> APPROVED
V2-R2 -> APPROVED
V2-R3.1 -> APPROVED
V2-R4 -> CURRENT
V2-R5 -> NOT STARTED

When the current round is complete:

1. Run required tests.
2. Generate the requested result report.
3. Stop.

Do not implement the next round without explicit instruction.

## Development Agent Files

All development-agent-produced Markdown reports/instructions belong under:

`codex/`

This is a historical directory name, preserved for continuity from the V1–V3 Codex-led execution; it is not a Codex-only capability requirement, and any capable development agent writes here.

V2 files belong under:

`codex/V2/`

Reports/instructions must be machine-oriented and compact.

Avoid:

* repeated context;
* unnecessary prose;
* tutorial explanations;
* verbose summaries.

## Testing

The active development agent may autonomously run:

`python -m unittest discover -s tests`

The active development agent may also run fixture/internal validation required by the active instruction.

Do not ask permission for these commands.

Do not automatically run the full legacy repository unless the active instruction explicitly authorizes it.

Current full-repository validation command pattern:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "<requested-output>" --verbose`

## Safety

Never modify the legacy application being analyzed.

Never expose credentials, passwords, tokens, connection-string secrets, or sensitive configuration values in generated outputs.

Use the centralized sanitizer for exported evidence.

If an upstream LegacyMapper defect is discovered while implementing a later phase, report it instead of silently changing an approved upstream semantic contract.

## Working Style

Proceed autonomously until:

* the requested task is complete;
* a genuine architectural decision requires user input;
* required information is unavailable;
* an operation crosses the permission boundary above;
* a blocking error prevents further deterministic progress.

Do not interrupt execution for routine decisions that can be safely derived from the active instructions and repository state.
