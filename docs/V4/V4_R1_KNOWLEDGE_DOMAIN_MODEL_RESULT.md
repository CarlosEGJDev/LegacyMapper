# V4-R1 Knowledge Domain Model — Result

## Entry Gate

Verified before implementation: `V3_BASELINE=VALID`, 662/662 tests passing, `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`. Entry gate: `PASS`.

## Required Reading

All eleven required documents were read, plus the four named existing implementation files (`models/evidence.py`, `documentation/contracts.py`, `documentation/evidence_catalog.py`, `documentation/human_review.py`) and their related tests.

## Design Decision — Module Placement and Relationship to V3

Created a new, small, cohesive package: `legacy_documenter/knowledge/domain/` (`__init__.py`, `enums.py`, `models.py`). This was chosen over `legacy_documenter/knowledge/models.py` because the enum vocabulary and the record types are each substantial and independently testable; splitting them keeps each file cohesive without unnecessary fragmentation.

Relationship to existing V3 models, per the required EXTEND/ADAPT/COMPOSE-before-duplicate rule:

* `legacy_documenter/models/evidence.py` (`Evidence`) is code-specific (`file`, `line`, `class_name`, `method`) — mutating it to become source-neutral would change its established V3 meaning. **Decision: COMPOSE**, a new `EvidenceRef` type was added instead; V3's `Evidence` is untouched.
* `legacy_documenter/documentation/contracts.py` (`SOURCE_TYPES`, `FACT_STATUSES`) encodes the V3-specific, narrower source/status vocabulary used by the closed V3 assessment pipeline. **Decision: COMPOSE**, a new, broader `SourceType`/`KnowledgeStatus` enum pair was added for V4; V3's sets are untouched and keep their V3 meaning.
* `legacy_documenter/documentation/contracts.py`'s `stable_id()` helper is a pure, source-agnostic deterministic hashing utility. **Decision: REUSE_AS_IS** — imported and reused by the new `new_statement_id`/`new_material_id`/`new_evidence_id` helpers instead of duplicating hashing logic.
* `legacy_documenter/documentation/evidence_catalog.py` and `documentation/human_review.py` remain untouched; they are V3-round-specific (fixed FMI/TMI vocabulary, request-local evidence keys) and out of scope for the R1 domain model itself, per the bootstrap inventory's `EXTEND`/`ADAPT` classification reserved for later rounds (R3, R4).

No V3 file was modified.

## Domain Model

**MaterialItem** (`legacy_documenter/knowledge/domain/models.py`) — represents pre-approval material from any V4 source type. `content` and `reference` are both optional individually; at least one must be present. No field requires a filesystem path or code metadata.

**EvidenceRef** — source-neutral evidence pointer with a free-form `locator` (not a code-specific `file`/`line` pair), an optional `Origin`, and an `authoritative` flag.

**KnowledgeStatement** — the core semantic unit: `statement_id`, `statement`, `source_type`, `nature`, `status`, `evidence_refs`, optional `provenance`, optional `temporal_state`, `related_statement_ids`, an `ApprovalInfo` holder, and `metadata`. Validation preserves the V3 rule that a `CONFIRMED` fact requires authoritative evidence, rejects duplicate evidence references, and enforces closed-enum membership everywhere a vocabulary applies.

Supporting types: `Origin` (source-neutral provenance anchor — `kind` plus optional `reference`/`contributor`/`captured_at`), `Provenance` (links a statement back to its materials/evidence and contributor), `ApprovalInfo` (Technical Lead approval data holder, no workflow logic).

## Source Types

Implemented as the `SourceType` closed enum with all twelve contract values: `DETERMINISTIC_CODE_FACT`, `HUMAN_REQUIREMENT`, `USER_STORY`, `BUSINESS_REQUIREMENT`, `BUSINESS_CONTEXT`, `TECHNICAL_CONSTRAINT`, `CORPORATE_STANDARD`, `APPROVED_DECISION`, `EXTERNAL_DOCUMENT`, `PROJECT_DOCUMENT`, `AI_INTERPRETATION`, `UNRESOLVED`.

## Knowledge Nature

Implemented as the `KnowledgeNature` closed enum with all seventeen contract values (`NORM`, `LEVANTAMIENTO`, `REQUIREMENT`, `NEED`, `BUSINESS_RULE`, `DECISION`, `ARCHITECTURE`, `PROCESS`, `FLOW`, `CATALOG`, `PROJECT`, `RESOLUTION`, `LESSON`, `TRAINING`, `GLOSSARY`, `CONSTRAINT`, `EXISTING_IMPLEMENTATION`). None of these values names a target document/section; the target-family test (Scenario 6) demonstrates the mapping is done through `metadata`, not through the enum itself.

## Knowledge Status

Implemented as the `KnowledgeStatus` closed enum: `CONFIRMED`, `INTERPRETED`, `PARTIAL`, `UNRESOLVED`, `MISSING`, `CONFLICTING`, `SUPERSEDED`. `CONFIRMED`, `INTERPRETED` and `UNRESOLVED` keep their V3 meaning; the four additional values only extend the vocabulary — no detection/promotion engine for `PARTIAL`, `MISSING`, `CONFLICTING` or `SUPERSEDED` was implemented, per the R1 scope limit.

## Temporal State

Implemented as the `TemporalState` closed enum: `AS_IS`, `TO_BE`, `HISTORICAL`, attached as an optional field on `KnowledgeStatement`. Two statements about the same subject may carry different temporal states and coexist without any automatic conflict being raised (Scenario 5); GAP detection itself is out of scope for this round.

## Provenance Support

Foundational only, per scope: `Origin` and `Provenance` let a statement declare where its material/evidence came from and who contributed it, without assuming a filesystem path, a URL, or that the origin is code. No resolution/lineage-building logic (V4-R3) was implemented.

## Code Optional

Confirmed `true`. No field on any of the four domain records requires a code file, code symbol, project file, repository scan, language, framework or technology. `SourceType.DETERMINISTIC_CODE_FACT` is one enum member among twelve, not a precondition for validity.

## Test Scenarios

All eight required scenarios were implemented in `tests/test_v4_r1_knowledge_domain_model.py` (14 test methods) and pass:

* **CODE_ONLY** — `PASS`
* **CODE_AND_HUMAN_INFORMATION** — `PASS` (independent `Provenance.origin.kind` per statement, verified distinct)
* **HUMAN_INFORMATION_ONLY** — `PASS` (no source-code path, language, project file, code symbol, or scan metadata anywhere in the record)
* **PARTIAL_INFORMATION** — `PASS` (`PARTIAL`/`UNRESOLVED` statements with no evidence refs validate without inventing content)
* **AS_IS_TO_BE_COEXISTENCE** — `PASS` (no automatic conflict raised)
* **TARGET_FAMILY_REPRESENTATION** — `PASS` (all ten target families represented via `nature` + `metadata`, no per-family class)
* **INVALID_CONTRACTS** — `PASS` (7 rejection cases: missing content/reference, empty id, invalid source type, unauthoritative-confirmed, duplicate evidence, empty origin kind, invalid approval status)
* **V3_REGRESSION** — `PASS` (full suite, see below)

## V3 Compatibility

`python -m unittest discover -s tests` → **676 tests, OK** (662 pre-existing + 14 new). No pre-existing test was modified. `python -m legacy_documenter.knowledge.readiness` re-run after the change: `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0` — identical to the pre-change baseline.

## Technical Debt

`TD-005` (type hints) was directly addressed: every new public class/function carries explicit type hints. `TD-002` (provider exception boundaries) was not touched — no provider code was called or modified in this round. `TD-003` (cross-round helpers) was not touched beyond reusing `stable_id()` as-is; no shared helper was modified.

## Production and Test Files Changed

Production: `legacy_documenter/knowledge/domain/__init__.py`, `legacy_documenter/knowledge/domain/enums.py`, `legacy_documenter/knowledge/domain/models.py` (all new files; no existing production file was modified).

Tests: `tests/test_v4_r1_knowledge_domain_model.py` (new file; no existing test file was modified).

## Result

```text
STATUS=V4_R1_KNOWLEDGE_DOMAIN_MODEL_COMPLETE
ENTRY_GATE=PASS
V3_BASELINE=VALID
BASELINE_TESTS=662_PASS
FINAL_TESTS=676_PASS
DOMAIN_MODEL=VALID
MATERIAL_ITEM=IMPLEMENTED
EVIDENCE_REF=IMPLEMENTED_OR_COMPATIBLY_EXTENDED
KNOWLEDGE_STATEMENT=IMPLEMENTED
SOURCE_TYPES=VALIDATED
KNOWLEDGE_NATURES=VALIDATED
KNOWLEDGE_STATUSES=VALIDATED
TEMPORAL_STATES=VALIDATED
PROVENANCE_SUPPORT=FOUNDATIONAL
CODE_OPTIONAL=true
CODE_ONLY_SCENARIO=PASS
CODE_AND_HUMAN_SCENARIO=PASS
HUMAN_INFORMATION_ONLY_SCENARIO=PASS
PARTIAL_INFORMATION_SCENARIO=PASS
TARGET_FAMILIES_COMPATIBILITY=PASS
V3_COMPATIBILITY=PASS
TECHNICAL_DEBT=TD-005_ADDRESSED;TD-002_UNTOUCHED;TD-003_UNTOUCHED
PRODUCTION_FILES_CHANGED=3_NEW_FILES;0_MODIFIED
TEST_FILES_CHANGED=1_NEW_FILE;0_MODIFIED
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
AI_KNOWLEDGE_GENERATED=false
DECISION=V4_R1_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R1
```

Stop. V4-R2 has not been started.
