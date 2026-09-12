# LegacyMapper V4 — R11 Human-Readable Document Projection — Result

```text
STATUS=V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=1163_PASS
FINAL_TESTS=1213_PASS

PROJECTION_MODEL=DocumentProjection(target: ProjectionTarget, entries: tuple[CanonicalKnowledgeEntry, ...]) is a
purely in-memory, read-only view over already-approved canonical entries produced by ProjectionService.project().
It never stores a mutated copy of an entry, never invents an entry, and exposes is_empty/knowledge_ids as derived
read-only properties.

PROJECTION_RULE_MODEL=ProjectionRule(rule_id, target, category=None, source_type=None, nature=None, status=None,
temporal_state=None) declares an explicit AND of one or more structured conditions over already-approved
CanonicalKnowledgeEntry fields only: source_type, nature, status, temporal_state, and the explicit closed
metadata["projection_categories"] tag set. A rule with zero conditions is rejected at construction
(ProjectionPathError). matches(entry) never reads or evaluates entry.statement.

TARGET_MODEL=ProjectionTarget(document_path, family, title, purpose) is one closed, validated target document.
document_path is validated by validate_target_path against the fixed ALLOWED_FAMILY_PREFIXES closed set
(00-el-area/ through 09-capacitacion/); absolute paths, drive-qualified paths (e.g. C:), and '..' traversal
segments are rejected with fixed, non-echoing error codes. A target path is never derived from untrusted free
text; the whole closed set (41 documents) is declared once in rules.py, not one Python class per folder.

MANIFEST_MODEL=ProjectionManifest reports canonical_entry_count, projected_canonical_entry_count,
unmapped_canonical_entry_count, document_count, non_empty_document_count, empty_document_count,
projection_occurrence_count, knowledge_id_to_document_paths (knowledge_id -> sorted document path list), and
unmapped_knowledge_ids (sorted). to_dict() renders it as a plain, JSON-serializable, deterministically ordered
dict. It is projection metadata only, never canonical knowledge.

CANONICAL_SOURCE_POLICY=ONE_CANONICAL_KNOWLEDGE_SOURCE. ProjectionService.project reads
CanonicalKnowledgeCollection.list() only; it never calls add()/compose() and never constructs a
CanonicalKnowledgeEntry. No parallel human_truth/document_truth/functional_truth/technical_truth/markdown_truth
store exists anywhere in this package.

CANONICAL_INPUT_MUTATION=NONE. Verified by CanonicalBoundaryTests: collection.list() is unchanged before/after
projection, the collection's entry count never grows, CanonicalKnowledgeEntry stays a frozen dataclass (mutation
attempt raises dataclasses.FrozenInstanceError), and rendering never changes status/temporal_state.

DOCUMENT_STRUCTURE_POLICY=PROJECTION_ONLY. The 00-09 information architecture is one flat, closed tuple of
ProjectionTarget values (rules.ALL_TARGETS, 41 documents); it is a projection/navigation concern, never the
canonical domain model. DOCUMENT_STRUCTURE_IS_DOMAIN_MODEL=false. All 41 targets share exactly one Python type
(ProjectionTarget) — no per-folder or per-family subclass exists.

MAPPING_POLICY=EXPLICIT_STRUCTURED_RULES_ONLY. Every ProjectionRule condition reads only
source_type/nature/status/temporal_state/metadata["projection_categories"]. No rule ever parses, tokenizes, or
keyword-matches entry.statement text (proven by MappingTests.test_no_rule_inspects_statement_text: a
BUSINESS_RULE entry whose statement literally contains the words "security" and "normas" is still UNMAPPED
because no structured condition matches it).

FREE_TEXT_MAPPING=FORBIDDEN. No component in this package performs semantic inference over entry.statement to
decide a document mapping.

UNMAPPED_POLICY=PRESERVE_AND_REPORT. A canonical entry matched by zero rules becomes UNMAPPED: never an error,
never deleted, never auto-classified. Its knowledge_id is reported in
ProjectionManifest.unmapped_knowledge_ids and it remains retrievable from the (untouched) canonical collection.

MULTI_PROJECTION_POLICY=ALLOWED_WITH_SAME_CANONICAL_ID. One canonical entry matched by rules pointing at more
than one target document is rendered, verbatim, in every one of those documents. Every occurrence retains the
identical knowledge_id (example scenario 9: a security NORM entry tagged with both
"gobernanza_seguridad_y_datos" and "dev_security" projects into both 01-gobernanza/seguridad-y-datos.md and
03-desarrollo-de-software/security.md, while the canonical collection still holds exactly one entry for it).

TRACEABILITY_POLICY=Every rendered non-empty item is followed by an HTML comment traceability marker in the
fixed format: <!-- knowledge_id: KNO-... -->. Chosen because it is inert in rendered Markdown/HTML previews,
non-invasive to normal reading, and fully deterministic. The knowledge_id also appears as the item's plain
Markdown heading ("### KNO-...").

CANONICAL_ID_VISIBILITY=The knowledge_id is the only internal canonical identifier rendered into the human
document (as the item heading and the trailing traceability comment). proposal_id, approval_decision_id, and
evidence_refs are never rendered into the projected document.

HUMAN_READABILITY_POLICY=Every non-empty document includes a title, a short fixed projection-metadata block
(document_path/family/purpose/projection_kind/canonical_knowledge_source), and one section per canonical item
with its nature/source_type/status and, when present, a human-language temporal_state label. No AI-generated
explanatory prose is ever added anywhere in the renderer.

CANONICAL_STATEMENT_PRESERVATION=Every rendered statement is the exact CanonicalKnowledgeEntry.statement string,
rendered verbatim inside a Markdown blockquote — unparaphrased, unsummarized, and semantically unchanged.
Verified with a literal-text assertion (RenderingTests.test_statement_preserved_verbatim) and with
prompt-injection-/HTML-shaped statements rendered byte-for-byte unchanged (SecurityTests).

EMPTY_DOCUMENT_POLICY=GENERATE_EMPTY_DOCUMENT_WITH_EXPLICIT_NO_APPROVED_KNOWLEDGE_MARKER. A configured target
with zero matching entries is still rendered (never skipped), with the fixed marker text: "No approved canonical
knowledge is currently projected to this document." This marker is projection metadata, never invented domain
knowledge. 33 of the 41 example-fixture documents are empty and carry this marker.

ORDERING_POLICY=Entries within one document are sorted by (temporal_state rank [AS_IS, TO_BE, HISTORICAL, none],
knowledge nature value, knowledge_id) — a fixed, explicit, content-derived order defined once in
service._sort_key. Canonical entries are additionally pre-sorted by knowledge_id before rule matching. Never
insertion timing, filesystem enumeration order, Python object identity, current date/time, or locale-dependent
sorting.

FILE_IO_BOUNDARY=ProjectionService (service.py) and the Markdown renderer (markdown_renderer.py) perform zero
file I/O (verified by NoFileIOInCoreLayerTests scanning both modules for open()/Path()/write_text/read_text
tokens); both operate purely in memory. Writing the synthetic example Markdown tree to disk is isolated in
disk_io.write_markdown_tree, which performs no projection/mapping decisions of its own.

AI_CALLS=0
PROVIDER_CALLS=0

R12_BOUNDARY=PASS. R11 implements no Plugin payload, Plugin schema, Plugin consumer API, agent context package,
or machine-readable Plugin contract anywhere in legacy_documenter/knowledge/projection/ (verified by
R12BoundaryTests). R12 is expected to independently project the same R10 CanonicalKnowledgeCollection;
R12_SOURCE=CANONICAL_KNOWLEDGE_SOURCE, R12_SOURCE!=R11_MARKDOWN.

SECURITY=PASS. entry.statement/entry.metadata are treated as untrusted display data only; no eval/exec/dynamic
import/shell/template execution exists in the functional code (contract_report.py's policy *prose* names these
terms only to state they are forbidden — SecurityTests excludes that one documentation-generator file from the
raw-token scan and instead verifies functional behavior directly). Prompt-injection-shaped and HTML/Markdown-
shaped statements render as inert verbatim text. Exception messages use fixed, non-echoing codes only; a
path string embedding a fake secret never leaks through ProjectionPathError.

PATH_SAFETY=PASS. validate_target_path (models.py) is the single choke point for every path-accepting surface
in this package. Verified rejections: '../' traversal, absolute paths ('/etc/passwd'), drive-qualified paths
('C:/Windows/system.ini'), and any path outside the fixed ALLOWED_FAMILY_PREFIXES closed set.

CONTRACT_ARTIFACT=output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json
CONTRACT_SHA256=5802e0e78dabd8e44de030ee15c56db747444147a462d050ad2971ffc39206fd

EXAMPLE_ARTIFACT=output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json
EXAMPLE_SHA256=4923fa6f1e506fc657c520888c7ebe2ad52102673983424e7c7a26d9d13cbe86

EXAMPLE_DOCS_ROOT=output/v4_r11/example_docs
EXAMPLE_DOCS_FILE_COUNT=42

CONTRACT_DETERMINISM=PASS (rendered twice in-process and twice via independent `python -c` invocations; both
render_projection_contract_json() outputs and their SHA-256 were identical).
EXAMPLE_DETERMINISM=PASS (rendered twice in-process and twice via independent `python -c` invocations; both
render_projection_example_json() outputs and their SHA-256 were identical).
MARKDOWN_TREE_DETERMINISM=PASS (the 42-document tree was built twice in-process, written to two independent
temporary directories, and compared byte-for-byte identical for every relative path; also regenerated in a
separate `python -c` process and diffed byte-for-byte against the committed output/v4_r11/example_docs tree
with zero mismatches).

V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS
V4_R3_REGRESSION=PASS
V4_R4_REGRESSION=PASS
V4_R5_REGRESSION=PASS
V4_R6_REGRESSION=PASS
V4_R7_REGRESSION=PASS
V4_R8_REGRESSION=PASS
V4_R9_REGRESSION=PASS
V4_R10_REGRESSION=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

PRODUCTION_BEHAVIOR_CHANGED=NONE. This round adds a new, additive `legacy_documenter/knowledge/projection/`
package, two new deterministic output artifacts, one new synthetic example Markdown tree, and one new test
module. No existing module (including every R1-R10 knowledge module) was modified.

TECHNICAL_DEBT=(1) The 03-desarrollo-de-software category set (16 documents) and the file naming for the
05/06/07/08/09 "projection family" documents were a discretionary design decision (the prompt describes them in
prose without fixing filenames) — see DESIGN_DECISIONS below; a future round may replace/extend these with a
Technical-Lead-reviewed closed list without changing the projection engine itself. (2) 07-proyectos currently
projects into one single closed document (07-proyectos/proyectos.md) rather than one document per project;
per-project grouping was explicitly left for a future, additively-configured closed target once canonical
knowledge explicitly supports that grouping, per the prompt's caution against inferring projects from text
similarity.

DECISION=V4_R11_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R11
```

---

## 1. What was reused vs. newly built

**Reused directly, unmodified:**

* `legacy_documenter/knowledge/canonical/models.py` and `service.py` (R10) — read-only input:
  `CanonicalKnowledgeCollection.list()` is the only call this round makes into R10.
* `legacy_documenter/knowledge/domain/enums.py` (R1) — `SourceType`, `KnowledgeNature`,
  `KnowledgeStatus`, `TemporalState` are the closed vocabularies every `ProjectionRule`
  condition is built from.
* `legacy_documenter/documentation/contracts.py.stable_id` (V3) — reused indirectly through
  `canonical.models.new_knowledge_id` when building the synthetic example fixture entries; R11
  never re-implements id hashing.
* The established V3/R7-R10 **contract/example report pattern** (plain-dict builder + a
  `json.dumps(..., sort_keys=True, separators=(",", ":"))` renderer) was followed as-is for
  `contract_report.py`/`example_report.py`, for direct comparability with prior rounds.

**Inspected but not reused:** `legacy_documenter/documentation/renderer.py` (the V3 functional/
technical Markdown renderer). It is tightly coupled to the V3 `claims`/`missing_information`/
`coverage_metrics` document shape and to fixed Spanish section lists specific to a
levantamiento document — not to a canonical-entry-to-target-document projection. Reusing it
directly would have meant bending V3's claim-grouping model onto R10's very different
`CanonicalKnowledgeEntry` shape. Instead, R11's `markdown_renderer.py` follows the *same*
underlying idea (fixed deterministic section list, deterministic sort, plain string
concatenation, no templating engine) as a **new, purpose-built pure function**, so the
determinism/security properties are equivalent without forcing an unrelated schema.

**New in this round:** the whole `legacy_documenter/knowledge/projection/` package
(`models.py`, `rules.py`, `service.py`, `markdown_renderer.py`, `disk_io.py`,
`contract_report.py`, `example_report.py`, `__init__.py`) plus
`tests/test_v4_r11_human_readable_document_projection.py` and the two `output/v4_r11/*.json`
artifacts and `output/v4_r11/example_docs/` tree.

## 2. Mapping approach

Every `ProjectionRule` is an explicit AND of zero-or-more of: `source_type`, `nature`,
`status`, `temporal_state`, and an explicit `metadata["projection_categories"]` tag drawn from
a closed vocabulary (`rules.PROJECTION_CATEGORIES`). `projection_categories` is treated exactly
like `nature`/`source_type`: a structured, already-decided field supplied at
canonical-composition time (or, for this fixture, at synthetic-entry-construction time) — never
parsed out of the statement. Three globally unique natures (`GLOSSARY`, `CATALOG`, `TRAINING`)
and two historical natures (`RESOLUTION`, `LESSON`) map directly by nature alone, since exactly
one target document exists for each in the closed information architecture. Everything else
(governance categories, flow categories, the 03-desarrollo-de-software category set,
architecture-reference categories, onboarding categories) is resolved through the
`projection_categories` tag. A canonical entry with zero matching rules is `UNMAPPED`; a
canonical entry whose `projection_categories` includes tags mapped to more than one document is
legitimately rendered into all of them, always under the same `knowledge_id`.

## 3. Traceability format chosen

`<!-- knowledge_id: KNO-... -->`, an HTML comment appended immediately after each rendered
item. It renders invisibly in a Markdown/HTML preview, does not clutter the human-readable
prose, cannot be confused with normal document content, and is trivially greppable for tooling
that later needs to reconcile a document back to its canonical source. The `knowledge_id` is
also shown as the item's plain `###` heading, so a human reading the raw Markdown sees it
without needing to notice the HTML comment.

## 4. Information architecture handling

The fixed `00-el-area/` through `09-capacitacion/` tree is declared as one flat, closed tuple
of 41 `ProjectionTarget` values in `rules.py` — a single dataclass type, not a hierarchy of
per-folder classes. `00`, `01`, `02`, and `04` use the exact filenames the prompt specifies.
`03-desarrollo-de-software` and the `05`/`06`/`07`/`08`/`09` "projection families" required a
discretionary design decision, since the prompt describes their contents in prose without
fixing filenames — see **Design decisions** below.

`01-gobernanza/fuente-de-verdad.md` is rendered with the title "Fuente de verdad (proyección
humana)" and its contract entry (`governance_source_of_truth_note`) explicitly states that this
filename does not redefine the R10 "Canonical Knowledge Source" concept, which remains exactly
`CanonicalKnowledgeCollection`.

## 5. R12 / AI boundaries

No Plugin payload, schema, consumer API, or agent-context package is defined anywhere in this
package (`R12BoundaryTests` scans the package's source for such symbols). No provider SDK is
imported and no LLM/provider call occurs anywhere in this package (`AIBoundaryTests` scans for
provider import statements). When a canonical entry has no matching structured rule, the only
possible outcome is `UNMAPPED` — there is no fallback classification path, AI-based or
otherwise.

## 6. Design decisions flagged for Technical Lead review

1. **03-desarrollo-de-software category set**: modeled as 16 closed documents, one per
   category named in the prompt (`methodology.md`, `definition-of-done.md`,
   `deliverables.md`, `coding-standards.md`, `naming-standards.md`,
   `configuration-standards.md`, `source-control-standards.md`,
   `dev-environment-standards.md`, `design-principles.md`, `patterns.md`,
   `anti-patterns.md`, `devsecops.md`, `pipeline.md`, `quality.md`, `security.md`,
   `environments.md`). This is a discretionary but conservative choice: one file per
   named category, no sub-hierarchy, no per-category Python class.
2. **05/06/07/08/09 projection families**: each modeled as a single closed general document
   (`plantillas.md`, `catalogo.md`, `proyectos.md`, `historial.md`, `capacitacion.md`) since
   the prompt does not fix individual filenames for these the way it does for 00/01/02/04.
   Adding a more granular closed target later (e.g. one additional named project document)
   is a purely additive configuration change to `rules.py`, never a dynamically derived path.
3. **V3 Markdown renderer reuse**: inspected (`legacy_documenter/documentation/renderer.py`)
   and found not directly reusable (different, V3-specific claim/coverage schema); R11 built
   a new pure renderer following the same deterministic-string-building approach instead of
   adapting an incompatible schema.

## 7. Stop condition

Implementation, tests, deterministic artifact generation, and this result document are
complete. R11 is **not** approved. No git commit or push was performed. R12 was not started.
The next action is `HUMAN_REVIEW_V4_R11`.

## Closure — Human Approval Recorded

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

DESIGN_DECISION_03_DOCUMENTS=APPROVED
DESIGN_DECISION_05_09_GENERAL_DOCUMENTS=APPROVED
DESIGN_DECISION_RENDERER=APPROVED

ROUND_STATUS=APPROVED

DECISION=V4_R11_FORMALLY_APPROVED

NEXT=V4-R12
```
