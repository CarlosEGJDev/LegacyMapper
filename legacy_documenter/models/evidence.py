from dataclasses import dataclass, asdict


@dataclass
class Evidence:
    file: str
    line: int | None = None
    expression: str | None = None
    project: str | None = None
    class_name: str | None = None
    method: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
