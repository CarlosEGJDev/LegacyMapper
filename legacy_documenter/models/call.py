from dataclasses import dataclass, field, asdict

from legacy_documenter.models.evidence import Evidence


@dataclass
class TypeReference:
    """Provides the cohesive TypeReference responsibility for this module."""
    name: str
    alias: str | None = None
    kind: str = "import"
    evidence: Evidence | None = None

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        data = asdict(self)
        if self.evidence:
            data["evidence"] = self.evidence.to_dict()
        return data


@dataclass
class Instantiation:
    """Provides the cohesive Instantiation responsibility for this module."""
    type_name: str
    variable_name: str | None
    containing_class: str | None
    containing_method: str | None
    evidence: Evidence
    resolved_type: str | None = None
    confidence: str = "unresolved"

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        data = asdict(self)
        data["evidence"] = self.evidence.to_dict()
        return data


@dataclass
class Call:
    """Provides the cohesive Call responsibility for this module."""
    expression: str
    method_name: str
    receiver: str | None
    receiver_path: str | None
    arguments_count: int
    containing_class: str | None
    containing_method: str | None
    evidence: Evidence
    resolved_target: str | None = None
    resolved_project: str | None = None
    confidence: str = "unresolved"
    candidates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        data = asdict(self)
        data["evidence"] = self.evidence.to_dict()
        return data
