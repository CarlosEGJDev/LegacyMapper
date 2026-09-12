# LegacyMapper V4 — User Manual

## Audience

The **Technical Lead** — the controlled human operator of LegacyMapper, and the sole final approval
authority for anything entering the canonical Knowledge Source. This manual explains what
LegacyMapper V4 does, what it deliberately does not do, and how to operate it safely.

## 1. What LegacyMapper Does

LegacyMapper **constructs knowledge**. It takes material from multiple sources — source code,
existing documents, requirements, user stories, business context, technical constraints, corporate
standards, approved decisions, external/project documents, and AI-generated interpretations — and
turns it, through a controlled pipeline, into one approved, traceable, structured **Knowledge
Source**. That Knowledge Source is later meant to be consumed by a separate multi-agent **Plugin**
that documents, designs, develops, validates, and evolves target projects.

`LegacyMapper constructs knowledge. The Plugin consumes knowledge.`

## 2. What LegacyMapper Does Not Do

* It does not implement the Plugin, any autonomous agent, orchestration, task planning, code
  generation, project modification, or model/provider routing. R12 (see §7) only defines the
  *contract* a future Plugin would read; no Plugin runtime exists in this repository.
* It does not decide truth on its own. A model (an LLM) may interpret, summarize, classify,
  propose, or flag a possible conflict/gap — it can never grant itself approval, hide uncertainty,
  invent evidence, or promote a hypothesis to a fact.
* It does not automatically resolve conflicts, fill gaps, or infer temporal relationships (see §6).
* It does not require source code. See §3.

## 3. Supported Input Modes

LegacyMapper's knowledge model treats source code as **one input among several, never a
precondition**. Four modes are explicitly supported and tested end-to-end:

* **CODE_ONLY** — knowledge built purely from deterministic code facts (the V1–V3 legacy-scanning
  capability, still valid and unchanged).
* **CODE_AND_HUMAN_INFORMATION** — code facts combined with Technical-Lead-supplied material.
* **HUMAN_INFORMATION_ONLY** — no source code involved at all; requirements, business context,
  standards, decisions, etc. flow through the same pipeline with no code-shaped field ever
  required.
* **PARTIAL_INFORMATION** — incomplete or unresolved material is preserved explicitly (`PARTIAL`,
  `UNRESOLVED` knowledge statuses) rather than guessed at or silently dropped.

The common V4 knowledge model is not VB.NET-specific: source code is one `SourceType` among twelve
(`DETERMINISTIC_CODE_FACT`, `HUMAN_REQUIREMENT`, `USER_STORY`, `BUSINESS_REQUIREMENT`,
`BUSINESS_CONTEXT`, `TECHNICAL_CONSTRAINT`, `CORPORATE_STANDARD`, `APPROVED_DECISION`,
`EXTERNAL_DOCUMENT`, `PROJECT_DOCUMENT`, `AI_INTERPRETATION`, `UNRESOLVED`). The existing V1/V2
legacy-code extraction remains valid and unchanged for deterministic code facts. Full
language/framework/project-layout-agnostic *extraction* is a future V5 concern — see
`docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` §15 — and is **not implemented** in V4.

## 4. How Human Information Fits

As Technical Lead you supply MATERIAL (a document, a requirement, a decision, a piece of business
context, etc.). Material is validated against a per-source-type contract (required fields,
sanitization) and ingested into a `MaterialItem` with a deterministic identity and a declared
`Origin` — the item never needs a filesystem path or a code symbol to be valid. Supplying material
does not by itself incorporate it into approved knowledge; see the pipeline in §5.

## 5. The Pipeline: Material → Proposal → Review → Approval

```text
MATERIAL → EVIDENCE / PROVENANCE → CLASSIFICATION / TEMPORAL / RELATIONS → PROPOSAL
    → TECHNICAL LEAD APPROVAL → CANONICAL KNOWLEDGE SOURCE → PROJECTIONS (human, Plugin)
```

Receiving material never means it is automatically incorporated. A **Proposal** (interpretation,
resolution, correction, reconciliation, selection, additional information, migration, or knowledge
addition) must be created explicitly, moved to `READY_FOR_REVIEW`, and then explicitly decided by
you. `READY_FOR_REVIEW` is a structural readiness state, **not** an approval — it only means the
proposal is well-formed enough to review.

You, the Technical Lead, are the **only** authority that can approve, reject, or request correction
of a proposal (`ApprovalDecisionType`: `APPROVED`, `REJECTED`, `CORRECTION_REQUESTED`). This is
structural, not just policy: `AI_NEVER_GRANTS_APPROVAL` and `SYSTEM_NEVER_GRANTS_APPROVAL` — no AI
and no part of the system can grant approval on your behalf; `ApprovalAuthority` has exactly one
member, `TECHNICAL_LEAD`. Approving a proposal makes it *eligible* for
composition into the canonical Knowledge Source — approval and composition are two separate,
explicit steps, and `APPROVED != CONFIRMED`: approving a proposal does not by itself mark the
resulting knowledge `CONFIRMED` (a knowledge status that still requires authoritative evidence).

Rejecting a proposal does not mean it was "false" — `REJECTED != FALSE`; it means you decided it
should not proceed. Requesting a correction does not reject it — `CORRECTION_REQUESTED != REJECTED`
— it means a new, corrected proposal is expected as a follow-up.

## 6. Uncertainty, Temporal State, and Relations — Nothing Is Inferred

LegacyMapper preserves uncertainty explicitly rather than resolving it silently:

* Knowledge statuses include `CONFIRMED`, `INTERPRETED`, `PARTIAL`, `UNRESOLVED`, `MISSING`,
  `CONFLICTING`, `SUPERSEDED`. None of these is ever assigned automatically from another field.
* **AS_IS / TO_BE / HISTORICAL**: what currently exists (`AS_IS`) and what should exist (`TO_BE`)
  are tracked separately and may coexist without being treated as a contradiction. A `HISTORICAL`
  statement is never automatically treated as obsolete or superseded, and an unset temporal state
  is never guessed at from wording or dates.
* **Relations** (`DIFFERENCE`, `GAP`, `CONFLICT`, `TEMPORAL_EVOLUTION`) are only created when you
  or an explicit deterministic/AI-proposed request creates them — an `AS_IS` and a `TO_BE`
  statement differing is never, by itself, automatically turned into a `GAP` or `CONFLICT`.

If you want a gap or conflict formally recorded, it must go through an explicit relation and,
typically, a proposal — LegacyMapper will never manufacture one on its own initiative.

## 7. Outputs: Human-Readable and Plugin-Facing

There is exactly **one** canonical Knowledge Source (built in what the engineering rounds call
"R10"). Everything else is a **projection** of it — never an independent source of truth:

* **Human-readable projection** — deterministic Markdown documents organized under a fixed
  `00-el-area/` … `09-capacitacion/` family structure, each rendered item traceable back to its
  canonical knowledge id (`KNO-...`). A document with no matching approved knowledge is still
  generated, carrying an explicit "no approved canonical knowledge is currently projected here"
  marker — it is never silently omitted.
* **Plugin-facing projection** — a versioned, machine-readable JSON contract named
  `LegacyMapperPluginKnowledge`, version `1.0`. It projects every canonical entry (nothing is
  silently dropped), preserving the same canonical id, but never republishing your arbitrary
  metadata as part of the Plugin API.

The human-readable projection and the Plugin-facing projection are **siblings**: both come directly
from the one canonical Knowledge Source, neither is derived from the other.

## 8. Provenance

Every piece of knowledge remains traceable to where it came from: its originating material, the
proposal that carried it forward, and the approval decision that authorized it. Provenance is not
the same thing as approval, authority, or status — a well-documented origin does not by itself make
a statement approved, authoritative, or confirmed. You still decide.

## 9. Operating LegacyMapper Today

There is currently **no unified V4 command-line interface** for the knowledge-construction pipeline
(ingestion → classification → proposal → approval → canonical composition → projection). That
pipeline is exercised through Python APIs and the automated test suite
(`python -m unittest discover -s tests`), which is also how each round's example artifacts under
`output/v4_r*/` were produced. Do not assume a CLI subcommand exists for these stages unless a
future round adds and documents one.

The one CLI entry point that does exist, `main.py`, drives the original V1–V3 legacy-code scanning
and documentation-generation pipeline:

```text
python main.py "<legacy_repository_path>" --output "<output_directory>" [--verbose] [--exclude <name>] [--flow-max-depth N]
```

This produces the deterministic V1–V3 functional/technical documentation artifacts; it does not, by
itself, run any V4 classification/proposal/approval/canonical-composition/projection step.

## 10. Safe Operational Expectations

* LegacyMapper never calls a real LLM/AI provider as part of its deterministic V4 core; every V4
  round's tests confirm `provider_calls=0` and `real_llm_calls=0`. Run
  `python -m legacy_documenter.knowledge.readiness` at any time to confirm this and the overall
  `READY` state.
* The legacy source repository you point LegacyMapper at is always treated as **read-only** — it is
  scanned, never modified.
* Prompt-injection-shaped text inside material/statements/rationale is always treated as inert
  data, never as an instruction to LegacyMapper or to any downstream tool.
* You are responsible for selecting material, declaring its context/origin, correcting incorrect
  information, resolving ambiguities that require human judgment, and approving or rejecting
  proposals. LegacyMapper will never make any of those five decisions for you.

For deeper technical detail, see `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md`. For recovery
and operational procedures, see `docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md`.
