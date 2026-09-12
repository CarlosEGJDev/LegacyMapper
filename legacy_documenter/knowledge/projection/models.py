"""In-memory projection-layer models for V4-R11 human-readable document projection.

`ProjectionTarget`/`ProjectionRule`/`DocumentProjection`/`ProjectionManifest`
are projection/navigation concepts only. None of them is a canonical-domain
concept: they never appear in `legacy_documenter/knowledge/canonical/`, never
mutate a `CanonicalKnowledgeEntry`, and never redefine
`KnowledgeStatus`/`SourceType`/`KnowledgeNature`/`TemporalState`.

This module performs no file, network, database, provider, or directory-scan
I/O, and never calls an LLM/provider.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.canonical.models import CanonicalKnowledgeEntry
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState

#: The closed set of top-level information-architecture family prefixes accepted for a
#: `ProjectionTarget.document_path`. Any path outside this closed set is rejected; a target
#: path is never derived from untrusted free text.
ALLOWED_FAMILY_PREFIXES: tuple[str, ...] = (
    "00-el-area/",
    "01-gobernanza/",
    "02-flujos/",
    "03-desarrollo-de-software/",
    "04-arquitecturas-de-referencia/",
    "05-plantillas/",
    "06-catalogo/",
    "07-proyectos/",
    "08-historial/",
    "09-capacitacion/",
)


class ProjectionPathError(ValueError):
    """Raised when a target document path violates the closed information-architecture policy.

    Deliberately uses fixed, non-echoing error codes: the rejected raw path text is never
    included in the exception message, so no untrusted content (nor any secret it might
    accidentally contain) can leak through an exception.
    """


def validate_target_path(path: str) -> str:
    """Validates `path` against the closed projection information-architecture policy.

    Rejects (with a fixed, non-echoing error code):
    * an empty/blank path;
    * an absolute path (leading `/` or `\\`);
    * a drive-qualified path (e.g. `C:`);
    * any path-traversal segment (`..`);
    * a path outside the fixed `ALLOWED_FAMILY_PREFIXES` closed set.

    Returns the same `path` unchanged when valid. This is the single choke point used by
    every path-accepting surface in this package (`ProjectionTarget` construction, and any
    future path-accepting API), so path safety is enforced identically everywhere.
    """
    if not isinstance(path, str) or not path.strip():
        raise ProjectionPathError("projection_target_path_required")
    normalized = path.replace("\\", "/")
    if normalized.startswith("/"):
        raise ProjectionPathError("projection_target_path_absolute_rejected")
    if len(normalized) >= 2 and normalized[1] == ":":
        raise ProjectionPathError("projection_target_path_drive_qualified_rejected")
    segments = normalized.split("/")
    if any(segment == ".." for segment in segments):
        raise ProjectionPathError("projection_target_path_traversal_rejected")
    if any(segment == "" for segment in segments):
        raise ProjectionPathError("projection_target_path_malformed")
    if not normalized.startswith(ALLOWED_FAMILY_PREFIXES):
        raise ProjectionPathError("projection_target_path_outside_closed_information_architecture")
    return normalized


@dataclass(frozen=True)
class ProjectionTarget:
    """Represents one closed, validated target document within the fixed information architecture.

    `document_path` is always validated through `validate_target_path` at construction time;
    it is never derived from untrusted free text (canonical `statement`, metadata values, or
    any other display data). `family` is the top-level folder (e.g. `01-gobernanza`), `title`
    is the deterministic human-readable document title, and `purpose` is one short closed
    label (e.g. `NORMA`, `FLUJO`, `LEVANTAMIENTO`) describing the document's role in the
    target information architecture — never a domain-model classification.
    """

    document_path: str
    family: str
    title: str
    purpose: str

    def __post_init__(self) -> None:
        validated = validate_target_path(self.document_path)
        object.__setattr__(self, "document_path", validated)
        if not self.family or not self.title or not self.purpose:
            raise ProjectionPathError("projection_target_incomplete")


@dataclass(frozen=True)
class ProjectionRule:
    """Declares one explicit, structured condition mapping canonical entries to a target document.

    Every condition field here reads only already-approved *structured* `CanonicalKnowledgeEntry`
    fields (`source_type`, `nature`, `status`, `temporal_state`, and an explicit
    `metadata["projection_categories"]` tag set). A rule never inspects `entry.statement` text.
    At least one condition field must be set (enforced in `__post_init__`); an unconditional
    rule that would match every entry is never valid.
    """

    rule_id: str
    target: ProjectionTarget
    category: str | None = None
    source_type: SourceType | None = None
    nature: KnowledgeNature | None = None
    status: KnowledgeStatus | None = None
    temporal_state: TemporalState | None = None

    def __post_init__(self) -> None:
        if not self.rule_id or not self.rule_id.strip():
            raise ProjectionPathError("projection_rule_id_required")
        if not isinstance(self.target, ProjectionTarget):
            raise ProjectionPathError("projection_rule_target_required")
        if all(condition is None for condition in (self.category, self.source_type, self.nature,
                                                     self.status, self.temporal_state)):
            raise ProjectionPathError("projection_rule_requires_at_least_one_structured_condition")

    def matches(self, entry: CanonicalKnowledgeEntry) -> bool:
        """Reports whether `entry` satisfies every structured condition declared by this rule.

        Reads only structured fields already present on the read-only `entry`; never
        evaluates, executes, or semantically interprets `entry.statement`.
        """
        if self.category is not None:
            categories = entry.metadata.get("projection_categories", ()) if isinstance(entry.metadata, dict) else ()
            if self.category not in tuple(categories):
                return False
        if self.source_type is not None and entry.source_type != self.source_type:
            return False
        if self.nature is not None and entry.nature != self.nature:
            return False
        if self.status is not None and entry.status != self.status:
            return False
        if self.temporal_state is not None and entry.temporal_state != self.temporal_state:
            return False
        return True


@dataclass(frozen=True)
class DocumentProjection:
    """Represents, purely in memory, what one target document should contain.

    `knowledge_ids` is a deterministically ordered tuple of the canonical `knowledge_id`
    values projected into this document (see `service.ORDERING_*` for the exact stable sort
    key). This is a projection-layer view only: it never stores a second copy of canonical
    knowledge content beyond what is needed to render it, and never mutates the entries it
    references.
    """

    target: ProjectionTarget
    entries: tuple[CanonicalKnowledgeEntry, ...] = ()

    @property
    def is_empty(self) -> bool:
        """Reports whether no canonical knowledge is currently projected to this document."""
        return len(self.entries) == 0

    @property
    def knowledge_ids(self) -> tuple[str, ...]:
        """Returns the ordered `knowledge_id` values projected into this document."""
        return tuple(entry.knowledge_id for entry in self.entries)


@dataclass(frozen=True)
class ProjectionManifest:
    """Deterministic, projection-only report describing the outcome of one projection run.

    This manifest is projection metadata; it is never itself canonical knowledge and is never
    consulted as an authority for `KnowledgeStatus`/`SourceType`/`KnowledgeNature`/
    `TemporalState`.
    """

    canonical_entry_count: int
    projected_canonical_entry_count: int
    unmapped_canonical_entry_count: int
    document_count: int
    non_empty_document_count: int
    empty_document_count: int
    projection_occurrence_count: int
    knowledge_id_to_document_paths: dict = field(default_factory=dict)
    unmapped_knowledge_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Renders this manifest as a plain, JSON-serializable dict with deterministic key order."""
        return {
            "canonical_entry_count": self.canonical_entry_count,
            "projected_canonical_entry_count": self.projected_canonical_entry_count,
            "unmapped_canonical_entry_count": self.unmapped_canonical_entry_count,
            "document_count": self.document_count,
            "non_empty_document_count": self.non_empty_document_count,
            "empty_document_count": self.empty_document_count,
            "projection_occurrence_count": self.projection_occurrence_count,
            "knowledge_id_to_document_paths": {
                knowledge_id: list(paths)
                for knowledge_id, paths in sorted(self.knowledge_id_to_document_paths.items())
            },
            "unmapped_knowledge_ids": list(self.unmapped_knowledge_ids),
        }
