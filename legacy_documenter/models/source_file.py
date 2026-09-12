from dataclasses import dataclass, asdict


@dataclass
class SourceFile:
    """Provides the cohesive SourceFile responsibility for this module."""
    relative_path: str
    extension: str
    size: int
    folder: str
    name: str
    file_type: str

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
