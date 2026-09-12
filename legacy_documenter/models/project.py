from dataclasses import dataclass, field, asdict


@dataclass
class Project:
    """Provides the cohesive Project responsibility for this module."""
    name: str
    path: str
    assembly_name: str | None = None
    root_namespace: str | None = None
    target_framework: str | None = None
    output_type: str | None = None
    project_references: list[dict] = field(default_factory=list)
    assembly_references: list[dict] = field(default_factory=list)
    compile_items: list[str] = field(default_factory=list)
    content_items: list[str] = field(default_factory=list)
    configurations: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
