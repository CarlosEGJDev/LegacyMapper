"""Pure in-memory V4-R11 projection service: canonical knowledge -> `DocumentProjection`s.

`ProjectionService.project` performs zero file, network, database, provider, or
directory-scan I/O. It reads a `CanonicalKnowledgeCollection` (never mutating it) plus an
explicit set of `ProjectionRule`s and `ProjectionTarget`s, and returns purely in-memory
`DocumentProjection` objects and one `ProjectionManifest`. No LLM/provider call occurs
anywhere in this module.
"""
from dataclasses import dataclass

from legacy_documenter.knowledge.canonical.models import CanonicalKnowledgeEntry
from legacy_documenter.knowledge.canonical.service import CanonicalKnowledgeCollection
from legacy_documenter.knowledge.projection.models import DocumentProjection, ProjectionManifest, ProjectionRule, ProjectionTarget

#: Deterministic ordering of `TemporalState` (and "no temporal state") used to sort items
#: within one target document. Never relies on enum declaration order or insertion order.
_TEMPORAL_ORDER = {"AS_IS": 0, "TO_BE": 1, "HISTORICAL": 2, None: 3}


def _sort_key(entry: CanonicalKnowledgeEntry) -> tuple:
    """Deterministic within-document sort key: temporal_state, then nature, then knowledge_id.

    Never depends on insertion timing, filesystem enumeration, Python object identity,
    current date/time, or locale-dependent sorting.
    """
    temporal_value = entry.temporal_state.value if entry.temporal_state is not None else None
    return (_TEMPORAL_ORDER.get(temporal_value, 99), entry.nature.value, entry.knowledge_id)


@dataclass
class ProjectionResult:
    """Groups the two deterministic outputs of one projection run."""

    documents: dict
    manifest: ProjectionManifest


class ProjectionService:
    """Stateless, pure in-memory service that projects canonical knowledge into documents.

    Never mutates `CanonicalKnowledgeCollection`, any `CanonicalKnowledgeEntry`, any R8
    `Proposal`, any R9 `ApprovalDecision`, or any R7 `KnowledgeRelation`. Never changes
    `KnowledgeStatus`/`SourceType`/`KnowledgeNature`/`TemporalState`. Never infers a document
    mapping from `entry.statement` free text: only explicit structured `ProjectionRule`
    conditions decide document membership.
    """

    def project(
        self,
        collection: CanonicalKnowledgeCollection,
        rules: tuple[ProjectionRule, ...],
        targets: tuple[ProjectionTarget, ...],
    ) -> ProjectionResult:
        """Projects every entry in `collection` through `rules` onto `targets`.

        A canonical entry matched by zero rules becomes `UNMAPPED` (never an error, never
        deleted, never auto-classified): its `knowledge_id` is preserved in the manifest. A
        canonical entry matched by rules pointing at more than one target legitimately
        appears in every one of those documents, always retaining the same `knowledge_id`;
        this never creates a second copy of canonical knowledge.
        """
        # Sort by knowledge_id up front: collection.list() order must never influence the
        # deterministic outcome (defense in depth beyond the final per-document sort below).
        entries = sorted(collection.list(), key=lambda entry: entry.knowledge_id)

        path_to_entries: dict[str, list[CanonicalKnowledgeEntry]] = {target.document_path: [] for target in targets}
        knowledge_id_to_paths: dict[str, list[str]] = {}
        unmapped_knowledge_ids: list[str] = []

        target_paths = {target.document_path for target in targets}
        for entry in entries:
            matched_paths = sorted({
                rule.target.document_path
                for rule in rules
                if rule.matches(entry) and rule.target.document_path in target_paths
            })
            if not matched_paths:
                unmapped_knowledge_ids.append(entry.knowledge_id)
                continue
            knowledge_id_to_paths[entry.knowledge_id] = matched_paths
            for path in matched_paths:
                path_to_entries[path].append(entry)

        documents: dict[str, DocumentProjection] = {}
        non_empty_document_count = 0
        projection_occurrence_count = 0
        for target in targets:
            ordered_entries = tuple(sorted(path_to_entries[target.document_path], key=_sort_key))
            documents[target.document_path] = DocumentProjection(target=target, entries=ordered_entries)
            if ordered_entries:
                non_empty_document_count += 1
            projection_occurrence_count += len(ordered_entries)

        manifest = ProjectionManifest(
            canonical_entry_count=len(entries),
            projected_canonical_entry_count=len(knowledge_id_to_paths),
            unmapped_canonical_entry_count=len(unmapped_knowledge_ids),
            document_count=len(targets),
            non_empty_document_count=non_empty_document_count,
            empty_document_count=len(targets) - non_empty_document_count,
            projection_occurrence_count=projection_occurrence_count,
            knowledge_id_to_document_paths=knowledge_id_to_paths,
            unmapped_knowledge_ids=tuple(sorted(unmapped_knowledge_ids)),
        )
        return ProjectionResult(documents=documents, manifest=manifest)
