from dataclasses import dataclass, field, asdict


@dataclass
class Symbol:
    """Provides the cohesive Symbol responsibility for this module."""
    name: str
    kind: str
    file: str
    namespace: str | None = None
    declared_namespace: str | None = None
    root_namespace: str | None = None
    effective_namespace: str | None = None
    project_path: str | None = None
    namespace_confidence: str = "unresolved"
    accessibility: str | None = None
    modifiers: list[str] = field(default_factory=list)
    inherits: list[str] = field(default_factory=list)
    implements: list[str] = field(default_factory=list)
    members: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
