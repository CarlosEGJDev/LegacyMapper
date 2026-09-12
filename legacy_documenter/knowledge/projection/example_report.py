"""Deterministic synthetic example fixture for the V4-R11 human-readable document projection layer.

Every canonical entry below is synthetic, hand-authored, and constructed directly as a
`CanonicalKnowledgeEntry` value (never derived from any real repository content, and never
composed through the mutation-restricted R8/R9/R10 workflow — this fixture only needs
already-approved-shaped, read-only input data for the projection layer to consume). This is a
test/example projection only; it must never be presented as real approved organizational
documentation.
"""
import json

from legacy_documenter.knowledge.canonical.models import CanonicalKnowledgeEntry, new_knowledge_id
from legacy_documenter.knowledge.canonical.service import CanonicalKnowledgeCollection
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import EvidenceRef
from legacy_documenter.knowledge.projection.markdown_renderer import render_documents
from legacy_documenter.knowledge.projection.rules import ALL_TARGETS, DEFAULT_RULES
from legacy_documenter.knowledge.projection.service import ProjectionService

SCHEMA_VERSION = "V4-R11"

_AUTHORITATIVE_EVIDENCE = EvidenceRef(
    evidence_id="EVR-EXAMPLE-R11-AUTHORITATIVE", source_type=SourceType.CORPORATE_STANDARD, authoritative=True,
)


def _entry(
    proposal_id: str,
    statement: str,
    source_type: SourceType,
    nature: KnowledgeNature,
    status: KnowledgeStatus,
    temporal_state: TemporalState | None = None,
    categories: tuple[str, ...] = (),
    evidence_refs: tuple[EvidenceRef, ...] = (),
) -> CanonicalKnowledgeEntry:
    """Builds one synthetic, already-valid `CanonicalKnowledgeEntry` for the example fixture."""
    approval_decision_id = f"APR-EXAMPLE-{proposal_id}"
    evidence_ids = tuple(sorted({ref.evidence_id for ref in evidence_refs}))
    knowledge_id = new_knowledge_id(
        proposal_id, approval_decision_id, source_type, nature, status, temporal_state, evidence_ids, (),
    )
    metadata = {"projection_categories": tuple(sorted(categories))} if categories else {}
    entry = CanonicalKnowledgeEntry(
        knowledge_id=knowledge_id,
        statement=statement,
        source_type=source_type,
        nature=nature,
        status=status,
        proposal_id=proposal_id,
        approval_decision_id=approval_decision_id,
        temporal_state=temporal_state,
        evidence_refs=evidence_refs,
        related_statement_ids=(),
        metadata=metadata,
    )
    entry.validate()
    return entry


def build_example_entries() -> dict:
    """Builds the named synthetic canonical entries used by every required R11 example scenario."""
    return {
        "governance_norma": _entry(
            "PRP-EXAMPLE-R11-01",
            "Toda rama de release debe originarse desde main y fusionarse mediante pull request revisado.",
            SourceType.CORPORATE_STANDARD, KnowledgeNature.NORM, KnowledgeStatus.CONFIRMED,
            categories=("gobernanza_ramas_y_versionamiento",), evidence_refs=(_AUTHORITATIVE_EVIDENCE,),
        ),
        "flow": _entry(
            "PRP-EXAMPLE-R11-02",
            "El flujo de desarrollo en blanco inicia con el levantamiento de requerimientos del área solicitante.",
            SourceType.BUSINESS_CONTEXT, KnowledgeNature.FLOW, KnowledgeStatus.INTERPRETED,
            categories=("flujo_desarrollo_en_blanco",),
        ),
        "architecture_reference": _entry(
            "PRP-EXAMPLE-R11-03",
            "Un agente conserva responsabilidad única, juicio, misión, entradas, salidas, límites y aprobación humana.",
            SourceType.TECHNICAL_CONSTRAINT, KnowledgeNature.ARCHITECTURE, KnowledgeStatus.INTERPRETED,
            categories=("arquitectura_agentes",),
        ),
        "catalog_inventory": _entry(
            "PRP-EXAMPLE-R11-04",
            "El levantamiento actual identifica 12 procedimientos almacenados activos en el módulo de facturación.",
            SourceType.DETERMINISTIC_CODE_FACT, KnowledgeNature.CATALOG, KnowledgeStatus.INTERPRETED,
        ),
        "historical": _entry(
            "PRP-EXAMPLE-R11-05",
            "En 2021 se resolvió el conflicto de doble aprobación migrando a un único flujo de firma digital.",
            SourceType.APPROVED_DECISION, KnowledgeNature.RESOLUTION, KnowledgeStatus.INTERPRETED,
            temporal_state=TemporalState.HISTORICAL,
        ),
        "human_information_only": _entry(
            "PRP-EXAMPLE-R11-06",
            "Levantamiento: proceso de recopilar y documentar el estado actual de un sistema o requerimiento.",
            SourceType.BUSINESS_CONTEXT, KnowledgeNature.GLOSSARY, KnowledgeStatus.INTERPRETED,
        ),
        "as_is": _entry(
            "PRP-EXAMPLE-R11-07",
            "Actualmente el control de calidad se ejecuta de forma manual antes de cada despliegue.",
            SourceType.BUSINESS_CONTEXT, KnowledgeNature.PROCESS, KnowledgeStatus.INTERPRETED,
            temporal_state=TemporalState.AS_IS, categories=("dev_quality",),
        ),
        "to_be": _entry(
            "PRP-EXAMPLE-R11-08",
            "El objetivo es automatizar completamente el control de calidad dentro del pipeline de integración.",
            SourceType.BUSINESS_CONTEXT, KnowledgeNature.PROCESS, KnowledgeStatus.INTERPRETED,
            temporal_state=TemporalState.TO_BE, categories=("dev_quality",),
        ),
        "multi_projection": _entry(
            "PRP-EXAMPLE-R11-09",
            "Todo dato sensible debe cifrarse en tránsito y en reposo conforme al estándar corporativo de seguridad.",
            SourceType.CORPORATE_STANDARD, KnowledgeNature.NORM, KnowledgeStatus.CONFIRMED,
            categories=("gobernanza_seguridad_y_datos", "dev_security"), evidence_refs=(_AUTHORITATIVE_EVIDENCE,),
        ),
        "unmapped": _entry(
            "PRP-EXAMPLE-R11-10",
            "Regla de negocio interna sin categoría de proyección estructurada configurada todavía.",
            SourceType.BUSINESS_REQUIREMENT, KnowledgeNature.BUSINESS_RULE, KnowledgeStatus.INTERPRETED,
        ),
    }


def build_projection_example() -> dict:
    """Builds the full deterministic R11 example-fixture payload (summary dict, no Markdown tree)."""
    named_entries = build_example_entries()
    collection = CanonicalKnowledgeCollection()
    for entry in named_entries.values():
        collection.add(entry)

    result = ProjectionService().project(collection, DEFAULT_RULES, ALL_TARGETS)
    manifest = result.manifest

    empty_target = next(target for target in ALL_TARGETS if target.document_path == "05-plantillas/plantillas.md")
    empty_projection = result.documents[empty_target.document_path]

    multi_paths = manifest.knowledge_id_to_document_paths[named_entries["multi_projection"].knowledge_id]

    return {
        "kind": "HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE_FIXTURE",
        "schema_version": SCHEMA_VERSION,
        "example_docs_root": "output/v4_r11/example_docs",
        "scenarios": {
            "01_governance_norma": {
                "knowledge_id": named_entries["governance_norma"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["governance_norma"].knowledge_id],
            },
            "02_flow": {
                "knowledge_id": named_entries["flow"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["flow"].knowledge_id],
            },
            "03_architecture_reference": {
                "knowledge_id": named_entries["architecture_reference"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["architecture_reference"].knowledge_id],
            },
            "04_catalog_current_inventory": {
                "knowledge_id": named_entries["catalog_inventory"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["catalog_inventory"].knowledge_id],
                "CATALOG_NOT_AUTO_PROMOTED_TO_NORM": True,
            },
            "05_historical": {
                "knowledge_id": named_entries["historical"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["historical"].knowledge_id],
                "temporal_state": named_entries["historical"].temporal_state.value,
                "HISTORICAL_NOT_AUTO_MARKED_SUPERSEDED": named_entries["historical"].status != KnowledgeStatus.SUPERSEDED,
            },
            "06_human_information_only": {
                "knowledge_id": named_entries["human_information_only"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["human_information_only"].knowledge_id],
            },
            "07_as_is": {
                "knowledge_id": named_entries["as_is"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["as_is"].knowledge_id],
                "temporal_state": named_entries["as_is"].temporal_state.value,
            },
            "08_to_be": {
                "knowledge_id": named_entries["to_be"].knowledge_id,
                "document_paths": manifest.knowledge_id_to_document_paths[named_entries["to_be"].knowledge_id],
                "temporal_state": named_entries["to_be"].temporal_state.value,
            },
            "09_multi_projection": {
                "knowledge_id": named_entries["multi_projection"].knowledge_id,
                "document_paths": multi_paths,
                "projected_into_two_documents": len(multi_paths) == 2,
                "canonical_entry_count_for_this_knowledge_id": 1,
            },
            "10_unmapped": {
                "knowledge_id": named_entries["unmapped"].knowledge_id,
                "is_unmapped": named_entries["unmapped"].knowledge_id in manifest.unmapped_knowledge_ids,
            },
            "11_empty_document": {
                "document_path": empty_target.document_path,
                "is_empty": empty_projection.is_empty,
            },
        },
        "manifest": manifest.to_dict(),
    }


def build_projection_example_markdown_tree() -> dict:
    """Builds the full deterministic `{document_path: markdown_text}` tree for the example fixture."""
    named_entries = build_example_entries()
    collection = CanonicalKnowledgeCollection()
    for entry in named_entries.values():
        collection.add(entry)
    result = ProjectionService().project(collection, DEFAULT_RULES, ALL_TARGETS)
    return render_documents(result.documents)


def render_projection_example_json() -> str:
    """Renders the example fixture as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_projection_example(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
