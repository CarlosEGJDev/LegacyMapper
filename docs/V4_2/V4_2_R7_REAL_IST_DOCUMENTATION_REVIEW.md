# LegacyMapper V4.2-R7 — Real IST/Operacional Documentation Review

This document lets the Technical Lead judge the real pilot's output without
requiring the full generated tree (`output/v4_2_r7_ist_operacional/`,
local-only, not committed). All examples below are filenames, symbol
names, and short evidence excerpts already present in LegacyMapper's own
generated output — no large source excerpt, credential, or business data
is reproduced.

## SELECTED_SOURCE

`C:\Users\cgalianj\source\IST_40\operacional`

Selected per `AGENTS.md`'s explicit "Legacy Source Repository" declaration
(the only current-configuration document naming a specific path); the
second historically-mentioned path
(`C:\inetpub\wwwroot\2010\IST\operacional`) also exists on this machine,
but `AGENTS.md` names exactly one path as authoritative, so there was no
actual ambiguity to resolve — see SOURCE_SELECTION in the round result
document for the full reasoning.

## PILOT_COMMAND

```
python main.py full "C:\Users\cgalianj\source\IST_40\operacional" --output "output/v4_2_r7_ist_operacional" --verbose
```

(`--allow-ai-interpretation` was never passed; `REAL_AI_RUNTIME_CALL_ALLOWED=false` throughout.)

## PILOT_EXIT_CODE

0

## PILOT_STATUS

SUCCESS — all ten deterministic stages (`SCAN` through `DOCUMENTATION`,
`FINAL_SUMMARY`) reported `SUCCESS`; `AI_INTERPRETATION`/
`PROPOSAL_GENERATION` correctly `NOT_RUN` (opt-in never passed).

## SOURCE_IMMUTABILITY

Verified by comparing `git status --short` (the repository is itself a
git working tree) and representative file hashes before and after the
run: byte-for-byte identical. `HEAD` unchanged
(`4ba871924cf1fd04b510be35d1d3c3f4d4d9d472`); file count (18,455) and
directory count (2,502) unchanged. No LegacyMapper write of any kind
reached the source tree.

## QUANTITATIVE_METRICS

From `output/v4_2_r7_ist_operacional/index/repository.json`,
`flow_summary.json`, and per-index element counts (`RUN_SUMMARY.json`'s
own `duration_seconds` field is not currently populated — see FINDINGS
F-05 — the duration below is a wall-clock measurement of the CLI
invocation itself):

| Metric | Value |
|---|---|
| Repository files scanned | 15,138 |
| VB source files | 4,328 |
| Solutions | 113 |
| Projects (`.vbproj`) | 259 |
| WebForm/control markup files (`.aspx` + `.ascx`) | 3,342 (177 `.aspx`, 3,165 `.ascx`) |
| Physical symbols | 6,513 |
| Extraction errors | 0 |
| Outgoing calls (entry-point level) | 67,220 |
| — resolved to a concrete target | 4,991 (7.4%) |
| Calls overall (`ai_context` call graph) | confirmed 12,775 / unresolved 217,581 (94.5% unresolved) |
| Web entry points | 12,662 (12,642 confirmed, 20 unresolved) |
| Event bindings | 12,662 |
| Data access operations | 20,082 |
| Stored procedure references | 5,389 |
| SQL operations (raw, non-procedure) | 3 |
| Data parameters | 74,633 |
| Functional dependencies | 335,698 |
| Functional flows | 12,642 (one per resolved entry point) |
| Functional paths | 170,020 |
| — paths reaching a stored procedure | 1,121 |
| — paths reaching a data operation | 4,612 |
| — paths reaching raw SQL | 1 |
| — unresolved boundaries | 162,914 (95.8% of paths) |
| Flows whose own `status` is `unresolved_boundary` despite a real `terminal_operations` value | 2,370 of 12,642 (18.7%) — see FINDINGS F-01 |
| Dependencies (project/DLL edges) | 26,960 |
| Generated documentation files | 10 (`documentation/*.md`) |
| Generated index files | 21 (`index/*.json`) |
| Generated `ai_context` files | 5 |
| Total generated output size | documentation/ ≈63MB; index/ ≈950MB; ai_context/ ≈267MB; context/ ≈876KB |

No metric above was UNAVAILABLE; all came directly from LegacyMapper's own
generated artifacts.

## DOCUMENT_EVALUATION

| Document | Classification | Why |
|---|---|---|
| `PROJECT_OVERVIEW.md` | USEFUL | Small (351 bytes), immediately orients a reader on repository scale by file type. Exposes the analyst's absolute local path (`C:\Users\cgalianj\...`) — see FINDINGS F-04. |
| `SOLUTION_STRUCTURE.md` | PARTIALLY_USEFUL | Readable size (425 lines / 22KB) and correctly maps every solution to its member projects, but 24 of 113 solution headers (21%) are exact-duplicate names with no disambiguation — a reader cannot tell two `## WebAmbiente` sections apart (see FINDINGS F-02). |
| `PROJECT_DEPENDENCIES.md` | PARTIALLY_USEFUL | Correct, deterministic project/DLL edge list (9,424 lines / 978KB) — useful as a `grep`-able reference, not something a human reads start to finish. |
| `WEBFORMS_MAP.md` | PARTIALLY_USEFUL | Correct per-WebForm metadata (13,944 lines / 1.37MB), but `register` entries render as raw Python `dict` repr (e.g. `{'TagPrefix': 'snt', 'Namespace': ...}`) instead of Markdown — a genuine presentation defect (FINDINGS F-03). |
| `CONFIGURATION_SUMMARY.md` | USEFUL | Clear, safe: reports only counts (`appSettings`, `connectionStrings`, `assemblies`) per `Web.config`, never actual values — exactly the sanitization this document should have. |
| `ANALYSIS_WARNINGS.md` | USEFUL | Minimal but accurate: "Errors captured: 0," consistent with `errors.json`. |
| `WEB_ENTRY_POINTS.md` | PARTIALLY_USEFUL | Correct, well-formatted per-WebForm tables (25,595 lines / 1.2MB across ~2,580 sections), but no index/navigation/filtering — impractical to browse linearly for a specific WebForm without external search tooling. |
| `FUNCTIONAL_FLOWS.md` | NOT_USEFUL | 396,178 lines, 44MB. Per-flow formatting is actually reasonable in isolation (see REPRESENTATIVE_SAMPLES), but at this scale no text editor or human review process can consume it directly — this is the single most severe usability problem found (FINDINGS F-01/F-06). |
| `DATABASE_ACCESS.md` | NOT_USEFUL | 32,560 lines, 5.2MB, one unbroken flat table with no grouping by project/package — the underlying data (stored procedure names, evidence) is correct and valuable, but the presentation makes it impractical to use directly. |
| `UNRESOLVED_FINDINGS.md` | NOT_USEFUL | 162,952 lines, 12.8MB. Dominated by low-value, boilerplate-shaped rows (`InitializeComponent()` appears repeatedly as an "unresolved flow boundary" — see FINDINGS F-06) that dilute the genuinely important unresolved gaps. |
| `RUN_SUMMARY.md` | USEFUL | Concise, accurate, exactly what it was designed to be (V4.2-R5): status, AI/proposal/approval state, output locations, next action. |

## QUALITY_QUESTIONS

- **Can the reader identify the system/project structure?** Partially. `PROJECT_OVERVIEW.md` gives scale; `SOLUTION_STRUCTURE.md` gives the solution→project map, but the duplicate-header issue (F-02) means the reader cannot always tell which physical copy of a solution (e.g. a `Backup/` folder duplicate) a given section describes.
- **Can the reader identify solutions/projects/modules?** Yes, by name, from `SOLUTION_STRUCTURE.md`/`PROJECT_DEPENDENCIES.md` — 113 solutions, 259 projects, all named.
- **Can the reader identify WebForms entry points?** Yes — `WEB_ENTRY_POINTS.md` lists every control/event/handler per WebForm with an explicit confidence value, though browsing it directly for one specific WebForm among ~2,580 is impractical without search tooling.
- **Can the reader follow representative UI → code → BL/service → database flows where evidence supports them?** Yes, for a meaningful minority, and the tool is more capable here than the headline `flow_summary.json` numbers suggest — see REPRESENTATIVE_SAMPLES and FINDINGS F-01. For the specific sample traced in depth (`webIndemnizacion\IndAcceso.aspx` → `BtnInicio_Click`), no — every outgoing call from that handler is unresolved, so that particular flow terminates without reaching BL/DB (see REPRESENTATIVE_SAMPLES sample 6).
- **Can the reader identify Oracle/database interactions?** Yes, clearly, when the interaction is a `stored_procedure`/`sql_operation` (e.g. `PPRE_CONSULTAS.CARGACOMBOCOMUNAS`, exact file/line evidence) — see REPRESENTATIVE_SAMPLES sample 4. Interactions LegacyMapper only classifies as `"transaction"` (a bare `BeginTrans`/`Commit`/`Rollback` sequence, `stored_procedure: null`) are correctly flagged as such rather than fabricating a procedure name, but tell the reader less on their own.
- **Are unresolved relationships clearly distinguished from resolved facts?** Yes, structurally — every call/flow/data-access record carries an explicit `confidence` field (`confirmed`/`unresolved`), and nothing sampled asserted a relationship beyond what its own evidence showed. See UNSUPPORTED_CLAIMS: no unsupported claim was found in the representative sample.
- **Are warnings understandable?** Yes but nearly empty of substance (`ANALYSIS_WARNINGS.md`: "Errors captured: 0"); the real warning signal for this run lives entirely in `UNRESOLVED_FINDINGS.md`'s scale (NOISE_OR_SCALE_ISSUES), which is not itself framed as a "warning."
- **Is deterministic evidence traceable?** Yes — every sampled claim carried an exact `file:line` and literal source expression.
- **Does any document imply unsupported semantics?** No instance found in the representative sample (see REPRESENTATIVE_SAMPLES/UNSUPPORTED_CLAIMS).
- **Is important information present only in JSON but missing from the human-readable documentation?** Yes, materially: the `terminal_operations`/edge-confidence detail that shows 2,370 flows actually reach a real DB terminal (F-01) is present in `index/functional_flows.json` but `FUNCTIONAL_FLOWS.md`'s own per-flow rendering still leads with the same misleading top-level `status: unresolved_boundary` (see REPRESENTATIVE_SAMPLES sample 5); a reader of the Markdown alone would not discover this without independently reading the JSON.
- **Is important information present only in JSON but missing from the human-readable documentation?** (repeated in the prompt; same answer as above — the JSON-only gap is F-01.)
- **Are documents too large/noisy to be useful?** Yes — `FUNCTIONAL_FLOWS.md` (44MB), `UNRESOLVED_FINDINGS.md` (12.8MB), `DATABASE_ACCESS.md` (5.2MB). See NOISE_OR_SCALE_ISSUES.
- **Are duplicate or low-value sections dominating the result?** Yes in two distinct ways: `SOLUTION_STRUCTURE.md`'s 24 duplicate solution headers (F-02), and `UNRESOLVED_FINDINGS.md`'s repeated `InitializeComponent()` boilerplate rows (F-06).
- **Does the documentation expose absolute local paths or other unnecessary environment-specific information?** Yes — `PROJECT_OVERVIEW.md` and `index/repository.json` both include the analyst's absolute local path (`C:\Users\cgalianj\source\IST_40\operacional`), revealing the local Windows username (F-04). No credential, connection-string value, or personal business data was found exposed anywhere sampled.

## REPRESENTATIVE_SAMPLES

Six samples, drawn only from LegacyMapper's own generated output (never
from prior knowledge of IST):

1. **WebForm** — `webIndemnizacion\IndAcceso.aspx` (VB code-behind
   `IndAcceso.aspx.vb`), five entry points discovered: `Page_Load`,
   `BtnInicio_Click` (8 outgoing calls), `btnGuardar_Click` (4),
   `btnCambiar_Click` (7), `btnCerrar_Click` (0). **Claim**: this WebForm
   has a login-shaped access page with a "start" button handler.
   **Evidence**: `entry_points.json` `EP-0421390846`/`EP-0436387830`/etc.,
   each with exact `file:line` evidence from `IndAcceso.aspx.vb`.
   **Verification**: SUPPORTED — every claimed control/event/handler
   triple is backed by a literal `Handles X.Click`/`Handles Me.Load`
   source line.
2. **Code-behind path** — `GCPAcceso.BtnInicio_Click`
   (`webIndemnizacion\IndAcceso.aspx.vb:24`), 8 outgoing calls, e.g.
   `InstUsua.txTraer(Me.txtUsuario.Text.ToUpper)`. **Claim**: this handler
   calls a method named `txTraer` on a receiver `InstUsua`. **Evidence**:
   `entry_points.json` `EP-0421390846.outgoing_calls[2]`, exact line 40.
   **Verification**: SUPPORTED as a *call site* claim (the call literally
   exists at that line) but the call itself is `resolved_target: null`,
   `confidence: "unresolved"` — LegacyMapper correctly does NOT claim which
   class/project `InstUsua` belongs to, so no unsupported claim is made
   about the target, only about the call's existence.
3. **BL/service path (positive example)** — `ucADHActualizaTasas.ascx`
   → `Page_Load` → `Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(2)`.
   **Claim**: this UI handler calls a method on a specific BL class in a
   specific project. **Evidence**: `entry_points.json` `EP-0618956849`,
   `resolved_target: "Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva"`,
   `confidence: "confirmed"`. **Verification**: SUPPORTED.
4. **Database/Oracle path** — the same handler's flow
   (`functional_flows.json`, entry point `EP-0618956849`) reaches
   `DAO-0508737736` (`project: "bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj"`,
   `class: "blADHds67"`, `method: "txtraerPereva"`, `provider: "OraConn"`,
   `operation_kind: "transaction"`, evidence: three exact `dbc.BeginTrans()`/
   `dbc.Commit()`/`dbc.Rollback()` lines). A separate, independently
   sampled stored-procedure example:
   `SP-0618773281` = `PPRE_CONSULTAS.CARGACOMBOCOMUNAS`, called from four
   different files/methods, each with an exact `dbc.ExecProc(...)` line
   and argument list. **Claim**: a real Oracle package/procedure is
   invoked from these exact locations. **Evidence**: literal
   `dbc.ExecProc("PPRE_CONSULTAS.CARGACOMBOCOMUNAS", ...)` source lines.
   **Verification**: SUPPORTED.
5. **Functional flow** — `FLOW-0136887931` (entry point `EP-0618956849`,
   same as sample 3/4). **Claim (as rendered in `FUNCTIONAL_FLOWS.md` and
   the flow's own top-level fields)**: `status: "unresolved_boundary"`,
   `confidence: "unresolved"`. **Evidence checked against**: the SAME
   flow's own `terminal_operations: ["DAO-0508737736"]` and a fully
   `confidence: "confirmed"` edge chain from the handler method through
   the BL call into the `DataAccessOperation` node.
   **Verification**: PARTIALLY_SUPPORTED — the underlying edges are each
   individually supported by real evidence, but the flow's own headline
   `status`/`confidence` fields materially understate what was actually
   resolved (this exact pattern reproduces at scale — see FINDINGS F-01;
   the synthetic fixture's `btnSave_Click` flow, section
   `docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md`, reproduces this
   precisely and deterministically).
6. **Unresolved relationship** — `webIndemnizacion\IndAcceso.aspx` →
   `BtnInicio_Click`'s flow (`FLOW-0995811533`): every one of its 8
   outgoing calls (`InstUsua.txTraer(...)`, six `SetFocus(...)` calls, one
   `Response.Redirect(...)`) renders as an `UnresolvedCall` node: the
   entire flow terminates unresolved, reaching no BL/DB evidence at all.
   **Verification**: SUPPORTED as an honest "nothing could be resolved
   here" — no fabricated relationship, no invented terminal operation.

## UNSUPPORTED_CLAIMS

None found in the six representative samples above, or in any other
document/JSON inspected during this review. Every claim traced carried
either an exact evidentiary source line (for a `confirmed` fact) or an
explicit `unresolved`/`null` marker (for a gap) — LegacyMapper's core
"never fabricate, always cite" invariant held throughout this pilot.

## MISSING_HUMAN_DOCUMENTATION

- The gap named in FINDINGS F-01 (a flow's headline status can
  understate what it actually resolved) is visible only by reading
  `index/functional_flows.json` directly (`terminal_operations` +
  per-edge `confidence`); `FUNCTIONAL_FLOWS.md`'s Markdown rendering does
  not surface this distinction anywhere.
- `flow_summary.json`'s `unresolved_boundaries: 162914` headline number
  (also shown verbatim atop `FUNCTIONAL_FLOWS.md`) has no accompanying
  note that a meaningful fraction of flows counted there still reached a
  real terminal database operation — a reader who only sees the Markdown
  summary table would reasonably conclude the tool's practical DB-tracing
  yield is far lower than it demonstrably is.

## NOISE_OR_SCALE_ISSUES

Three documents are effectively unusable as delivered due to raw scale:
`FUNCTIONAL_FLOWS.md` (396,178 lines / 44MB), `UNRESOLVED_FINDINGS.md`
(162,952 lines / 12.8MB), `DATABASE_ACCESS.md` (32,560 lines / 5.2MB).
`WEB_ENTRY_POINTS.md` (25,595 lines / 1.2MB) and `PROJECT_DEPENDENCIES.md`
(9,424 lines / 978KB) are large but at least structurally organized
(per-WebForm sections; one edge per line) and remain usable with external
search tooling (`grep`, an editor's find). `UNRESOLVED_FINDINGS.md`'s
noise is compounded by low-value repetition: the designer-generated
`InitializeComponent()` boilerplate call appears repeatedly in the
"Unresolved Flow Boundaries" table, diluting genuinely interesting
unresolved gaps (business method calls) with routine framework
boilerplate a reader has to scroll past.

## SECURITY_AND_CONFIDENTIALITY

- **No credential, connection-string value, or personal/business data**
  was found exposed in any generated document or index file sampled.
  `CONFIGURATION_SUMMARY.md` in particular is correctly designed to show
  only counts (`connectionStrings: 1`), never the value.
- **One environment-information leak found**: `PROJECT_OVERVIEW.md` and
  `index/repository.json` both embed the analyst's absolute local path
  (`C:\Users\cgalianj\source\IST_40\operacional`), which reveals the local
  Windows username. Not a secret/credential, but unnecessary
  environment-specific information a shared documentation package should
  not need to carry (F-04).
- This review document itself contains no large source excerpt, no full
  configuration file, and no raw generated JSON payload — only short,
  named evidence identifiers and short diagnostic excerpts, per section
  12's confidentiality requirement. The full generated output
  (`output/v4_2_r7_ist_operacional/`) remains local-only and is not
  committed.

## FINDINGS

| ID | Severity | Evidence | Affected artifact/stage | Expected behavior | Observed behavior | Recommended future action |
|---|---|---|---|---|---|---|
| F-01 | HIGH | `index/functional_flows.json`: 2,370 of 12,642 flows (18.7%) have a non-empty `terminal_operations` (a real, resolved DB/stored-procedure terminal) yet `status: "unresolved_boundary"`, `confidence: "unresolved"`. Reproduced minimally and deterministically by the synthetic fixture's `btnSave_Click` flow (`docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md`). | `FLOW_RESOLUTION` stage / `FunctionalFlowResolver` | A flow that reaches a real, confirmed database terminal should have its own top-level status/confidence reflect that success, not be indistinguishable from a flow that resolved nothing at all. | The flow's overall `status`/`confidence` is apparently downgraded to unresolved whenever ANY call anywhere in the traced method sequence is unresolved (e.g. an unrelated cleanup/logging call), even when the flow's actual DB-reaching path is fully confirmed. | Future round: review `FunctionalFlowResolver`'s status/confidence aggregation rule; consider whether "reached a confirmed terminal operation" should be reportable independently of "every call in the method resolved." |
| F-02 | MEDIUM | `documentation/SOLUTION_STRUCTURE.md`: 24 of 113 `## <SolutionName>` headers are exact-name duplicates (e.g. two consecutive `## WebAmbiente` sections) with no distinguishing path/context shown. | `DOCUMENTATION` stage / solution structure renderer | Two solutions that share a name (e.g. a live copy and a `Backup/` copy) should be visually distinguishable in the rendered document. | Identical headers repeated with no path/qualifier, making the sections indistinguishable to a reader. | Consider rendering each solution's own file path alongside/instead of its bare name when duplicates exist. |
| F-03 | MEDIUM | `documentation/WEBFORMS_MAP.md`: `register` entries render as Python `dict.__repr__` text, e.g. `` `{'TagPrefix': 'snt', 'Namespace': 'Sonda.Net.Control', 'Assembly': 'SondaNetWebUI', '_normalized': {...}}` ``. | `DOCUMENTATION` stage / WebForms map renderer | Structured `register` metadata should render as readable Markdown (e.g. a small sub-list or table), not a raw Python object repr. | Raw `dict` repr text is embedded directly in the Markdown. | Format `register` entries as Markdown fields/sub-bullets instead of `str(dict)`. |
| F-04 | LOW | `documentation/PROJECT_OVERVIEW.md` and `index/repository.json` both contain `"root": "C:\Users\cgalianj\source\IST_40\operacional"` verbatim. | `EXPORT`/`DOCUMENTATION` stages | Generated documentation intended to be shared/committed should not need to embed the analyst's absolute local filesystem path (and thus username). | The full absolute path, including the local username, is embedded verbatim. | Consider showing a relative/display-only repository label, or omitting the absolute prefix, in human-facing documentation. |
| F-05 | LOW | `output/v4_2_r7_ist_operacional/RUN_SUMMARY.json`: no wall-clock duration field is present in the top-level `RunResult` payload (only `index/repository.json`'s own `duration_seconds: 474.044`, which only covers the SCAN-through-EXTRACTION portion of the run, not the full ~9-minute pipeline). | `FINAL_SUMMARY` stage / `RunResult` | Section 6 of this round's own prompt asked to "capture ... duration if naturally available" for the whole pilot run. | No single field in `RUN_SUMMARY.json` reports the full run's wall-clock duration; it had to be measured externally (CLI start/end timestamps) for this review. | Consider whether `RunResult`/`RUN_SUMMARY.json` should carry a whole-run duration field in a future round. |
| F-06 | OBSERVATION | `documentation/UNRESOLVED_FINDINGS.md`'s "Unresolved Flow Boundaries" table: the designer-generated `InitializeComponent()` call recurs repeatedly as a distinct "unresolved boundary" row. | `DOCUMENTATION` stage / unresolved findings renderer | — | Routine framework-generated boilerplate is presented at the same level of significance as a genuine unresolved business-logic call. | Purely an observation for a future documentation-quality round; no code change proposed here. |
| F-07 | OBSERVATION | `WebEntryResolver` (see the synthetic fixture's `test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap`) never attaches `outgoing_calls` to an entry point bound via ASPX markup (`OnClick="..."`) — it looks the call graph up under the `.aspx` file path rather than the actual code-behind `.vb` file. Quantified impact on the real pilot: only 40 of 12,662 real entry points (0.3%) use markup-attribute binding (`webforms.json`'s `markup_events`); the vast majority use the code-behind `Handles` clause, which is unaffected. | `WEB_ENTRY_RESOLUTION` stage / `WebEntryResolver._add_binding_and_entry` | A markup-bound handler's `outgoing_calls` should reflect the same calls `calls.json` already correctly attributes to it. | `outgoing_calls` is always `[]` for a markup-bound handler, even when `calls.json` shows real, resolved calls for that exact method. | Real but narrow-impact gap (0.3% of real entry points); a future round could fix the file-path lookup key. Not the primary explanation for the pilot's overall unresolved rate — see F-01 for that. |

## OVERALL_DOCUMENTATION_ASSESSMENT

The deterministic pipeline is factually trustworthy: every claim sampled
across six representative examples was backed by exact, real evidence,
and no fabricated relationship was found anywhere. Scale, presentation
formatting, and one status-aggregation defect (F-01) are what currently
prevent the output from being genuinely useful to "a developer unfamiliar
with IST" as delivered: three of eleven human-facing documents are not
practically consumable at their current size, one presentation defect
(F-03) actively degrades readability, and the headline `unresolved_
boundaries` statistic materially understates the tool's actual DB-tracing
success rate (F-01) in a way that could mislead a reader into distrusting
output that is, in a meaningful fraction of cases, actually correct and
complete. None of this reflects a fabricated or incorrect fact — it is
entirely a completeness/presentation/aggregation problem, not a
correctness problem, in every case sampled.

## RECOMMENDATION

Proceed to closure with `DECISION=V4_2_R7_REQUIRES_CORRECTION` /
`NEXT=V4.2-R7.1` — see FINDINGS F-01, the HIGH-severity flow-status
aggregation defect, as the blocking rationale (see the round result
document for full decision reasoning). F-02/F-03/F-04/F-05 are
MEDIUM/LOW findings a corrective round could address alongside F-01;
F-06/F-07 are OBSERVATIONs for a future documentation-quality round, not
blocking.
