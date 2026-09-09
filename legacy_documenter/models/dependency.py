from dataclasses import dataclass, asdict


@dataclass
class Dependency:
    source: str
    target: str
    dependency_type: str
    source_file: str
    evidence: str
    confidence: str = "confirmed"

    def to_dict(self) -> dict:
        return asdict(self)
