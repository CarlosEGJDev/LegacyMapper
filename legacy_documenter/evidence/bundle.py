"""Technology-neutral evidence aggregate; extensions remain opaque."""
from dataclasses import dataclass, field
from .entities import SourceArtifact, Solution, Component, ExternalDependency, DataObject, CallIdentity, Instantiation, UnresolvedBoundary, ScanSummary

@dataclass
class NormalizedEvidence:
    """The complete Normalized Evidence Core for one deterministic run."""

    source_artifacts: list[SourceArtifact] = field(default_factory=list)
    solutions: list[Solution] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)  # id added; original preserved in extensions
    components: list[Component] = field(default_factory=list)
    external_dependencies: list[ExternalDependency] = field(default_factory=list)
    data_objects: list[DataObject] = field(default_factory=list)
    call_identities: list[CallIdentity] = field(default_factory=list)
    instantiations: list[Instantiation] = field(default_factory=list)
    unresolved_boundaries: list[UnresolvedBoundary] = field(default_factory=list)
    scan_summary: ScanSummary | None = None
    #: UI / navigation / style Evidence (post-V5 Gate B): partition name -> records. Empty for adapters without a UI extractor.
    ui: dict[str, list[dict]] = field(default_factory=dict)
    #: Gate C: cross-project call resolutions (resolved / inferred / ambiguous / external), one record per call that crosses or fails to cross
    #: a project boundary. Empty list for adapters without a cross-project resolver.
    cross_project_calls: list[dict] | None = None
    ui_extractor: dict = field(default_factory=dict)
    passthrough: dict[str, object] = field(default_factory=dict)
    #: legacy repository.json, verbatim (LEGACY_ONLY field `duration_seconds`
    #: lives only here, never in scan_summary -- D-01).
    repository: dict = field(default_factory=dict)
