from dataclasses import dataclass, asdict


@dataclass
class Dependency:
    """Provides the cohesive Dependency responsibility for this module."""
    source: str
    target: str
    dependency_type: str
    source_file: str
    evidence: str
    confidence: str = "confirmed"

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
