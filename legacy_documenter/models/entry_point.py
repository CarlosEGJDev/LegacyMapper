from dataclasses import dataclass, field, asdict


@dataclass
class EntryPoint:
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
        return asdict(self)


@dataclass
class EventBinding:
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
        return asdict(self)
