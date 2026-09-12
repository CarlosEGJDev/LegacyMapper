STATUS
V3-R1_READY_FOR_REVIEW

FILES_CHANGED
legacy_documenter/documentation/contracts.py
legacy_documenter/documentation/__init__.py
tests/test_v3_r1.py

CONTRACT_VERSION
3.0.0

FUNCTIONAL_CONTRACT
FUNCTIONAL_ASSESSMENT supports metadata, modules, functionalities references, entry points, flows, data dependencies, unresolved items and review lifecycle.

TECHNICAL_CONTRACT
TECHNICAL_ASSESSMENT supports generic technical claims, project/component evidence and architecture pattern assessments without stack-specific fields.

CLAIM_MODEL
DocumentClaim supports status/confidence, one-to-many source/evidence references, entities and validation state. CONFIRMED requires authoritative evidence.

EVIDENCE_MODEL
Canonical source types retained: deterministic fact, approved documents/external information, AI interpretation and unresolved.

CONFIDENCE_MODEL
CONFIRMED, INTERPRETED, UNRESOLVED; no automatic promotion.

PATTERN_MODEL
ArchitecturePatternAssessment supports confirmed/interpreted/unresolved evidence, supporting and contradicting observations.

MISSING_INFORMATION_MODEL
MissingInformation supports lifecycle-ready gaps and categories without ingestion workflow.

DOCUMENT_LIFECYCLE
DRAFT/GENERATED/VALIDATED/NEEDS_CHANGES/APPROVED/REJECTED/SUPERSEDED validated.

APPROVAL_GATE
AI knowledge readiness gate returns true only when functional and technical assessments are APPROVED.

TRACEABILITY
Stable references and canonical SHA-256 IDs; no evidence-body duplication required.

MARKDOWN_CONTRACT
Deterministic heading-only templates for LEVANTAMIENTO_FUNCIONAL.md and LEVANTAMIENTO_TECNICO.md.

V4_COMPATIBILITY
Language/stack agnostic contracts; V2 entity references are generic strings.

TESTS
python -m unittest discover -s tests
55 passed

DETERMINISM
Canonical JSON serialization and SHA-256 stable IDs. No UUID/Python hash/timestamp identity.

SECURITY
No network, LLM, legacy scan or evidence ingestion implemented.

REGRESSION
V1/V2 code paths unchanged; suite passes.

KNOWN_LIMITATIONS
No AI generation, final documentation, approval UI, external-information ingestion or AI_KNOWLEDGE generation.

NEXT
V3-R2_NOT_STARTED
