from dataclasses import dataclass, asdict


@dataclass
class Evidence:
    """Provides the cohesive Evidence responsibility for this module."""
    file: str
    line: int | None = None
    expression: str | None = None
    project: str | None = None
    class_name: str | None = None
    method: str | None = None

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
