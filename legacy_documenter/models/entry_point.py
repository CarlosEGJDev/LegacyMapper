from dataclasses import dataclass, field, asdict


@dataclass
class EntryPoint:
    """Provides the cohesive EntryPoint responsibility for this module."""
    id: str
    type: str
    webform: str
    control: str | None
    event: str
    handler: str
    class_name: str | None
    project: str | None
    confidence: str
    evidence: list[dict] = field(default_factory=list)
    handler_method: str | None = None
    outgoing_calls: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)


@dataclass
class EventBinding:
    """Provides the cohesive EventBinding responsibility for this module."""
    id: str
    webform: str
    control: str | None
    control_type: str | None
    event: str
    handler: str
    class_name: str | None
    project: str | None
    confidence: str
    evidence: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
