from dataclasses import dataclass, asdict


@dataclass
class SourceFile:
    relative_path: str
    extension: str
    size: int
    folder: str
    name: str
    file_type: str

    def to_dict(self) -> dict:
        return asdict(self)
